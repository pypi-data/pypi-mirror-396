"""Classes for working at the exposure level"""

# Standard library
import io
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

# Third-party
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from astropy.io import fits
from lamatrix import Spline
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from scipy import sparse
from tqdm import tqdm

from .frame import Frame
from .utils import get_pixel_mask, image_to_offsets, primaryHDU


@dataclass
class Exposure(object):
    """Class for working with Talbot exposures

    Parameters:
    -----------
    filename: str
        Filename for the exposure from the Talbot Illuminator
    pixel_mask: npt.NDArray
        Boolean mask showing which pixels to include in the data analysis. Use this to mask out bad pixels on the detector.
        Pixels that should not be included should be marked as "False".
    cutout_corner: tuple
        The location in pixel space of the lower left corner in format (row, column)
    cutout_size: tuple
        The shape of the image cutout to process (row, column)
    keyframe: int
        Which frame to use to calibrate the spot grid positions. Choose an unsaturated, fairly bright frame.
    poly_order: int
        The polynomial order for any background components
    sip_order: int
        The polynomial order for the distortion model. This is only used if no SIP object is passed.
    kind: string
        Kind of modeling to do. Choose between "spline", "gaussian"
    sigmas: list
        Standard deviations for Gaussians, if using "gaussian" kind of modeling.
    """

    filename: str
    pixel_mask: Optional[npt.NDArray] = None
    cutout_corner: Tuple = (1024, 1024)
    cutout_size: Tuple = (1024, 1024)
    keyframe = 5
    poly_order = 7
    sip_order = 3
    kind: str = "spline"
    sigmas: Tuple = (0.6, 2)

    def __post_init__(self):
        if not isinstance(self.filename, str):
            raise ValueError("Must pass a filename.")

        with fits.open(self.filename) as hdulist:
            self.data = hdulist[1].data[0][
                :,
                self.cutout_corner[0] : self.cutout_corner[0]
                + self.cutout_size[0],
                self.cutout_corner[1] : self.cutout_corner[1]
                + self.cutout_size[1],
            ]
            self.nframes = len(self.data)

        if self.pixel_mask is None:
            self.pixel_mask = get_pixel_mask(self.filename)[
                self.cutout_corner[0] : self.cutout_corner[0]
                + self.cutout_size[0],
                self.cutout_corner[1] : self.cutout_corner[1]
                + self.cutout_size[1],
            ]
        if not self.pixel_mask.shape == self.data.shape[1:]:
            raise ValueError(
                "Must pass a `pixel_mask` with the correct shape."
            )
        self._calibrated = "Uncalibrated"
        self.figs = []
        self.saturated_mask = (self.data > 0.95 * 2**16).any(axis=0)

    def __repr__(self):
        return f"TalbotExposure [{self.filename}] [{self._calibrated}]"

    def calibrate(self):
        """Uses"""
        image = self.data[self.keyframe].astype(float) - self.data[0].astype(
            float
        )
        self.keyframe = Frame(
            image=image,
            pixel_mask=self.pixel_mask,
            cutout_corner=self.cutout_corner,
            poly_order=self.poly_order,
            sip_order=self.sip_order,
            kind=self.kind,
            sigmas=self.sigmas,
        )

        fig1, fig2 = self.keyframe._rough_position_calibration(
            spot_spacing_bounds=(6, 20), plot=True
        )
        fig3 = self.keyframe._refine_position_calibration(plot=True)
        self.keyframe._update_affine_matrix()
        self.keyframe._refine_position_calibration(plot=False)
        self.Ls = self.keyframe.get_spline_spot_design_matrices()
        self.keyframe.fit_bkg_and_spots(Ls=self.Ls)
        fig4, ax = plt.subplots()
        self.keyframe.plot_spot_model(ax=ax)
        self.figs = []
        for fig in (fig1, fig2, fig3, fig4):
            if fig is None:
                continue
            if fig.canvas is None or not hasattr(fig.canvas, "print_pdf"):
                FigureCanvas(fig)  # attach a non-GUI canvas
            self.figs.append(fig)
            plt.close(fig)
        self._calibrated = "Calibrated"

    def make_report(self, outfile: str = "talbot_report.pdf", dpi=150):
        with PdfPages(outfile) as pdf:
            info = pdf.infodict()
            info["Title"] = "Talbot Illuminator Calibration Report"
            info["Author"] = "TalbotExtractor"
            info["CreationDate"] = datetime.now()
            info["Filename"] = self.filename.split("/")[-1]
            info["cutout_corner"] = self.cutout_corner
            info["cutout_size"] = self.cutout_size

            # --- Title page ---
            title_text = (
                f"{info['Title']}\n\n"
                f"Author: {info['Author']}\n"
                f"Date: {info['CreationDate']:%Y-%m-%d %H:%M}\n"
                f"Filename: {info['Filename']}"
                f"Cutout Corner: {info['cutout_corner']}"
                f"Cutout Size: {info['cutout_size']}"
            )
            fig_cover, ax = plt.subplots(figsize=(8.5, 11))  # letter-size page
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                title_text,
                ha="center",
                va="center",
                fontsize=14,
                wrap=True,
            )
            pdf.savefig(fig_cover)
            plt.close(fig_cover)

            for fig in getattr(self, "figs", []):
                if fig is None:
                    continue

                # Render figure as PNG into memory
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
                buf.seek(0)

                # Open the PNG as an image
                img = Image.open(buf)

                # Make a new figure sized to the image
                fig_img, ax = plt.subplots(
                    figsize=(img.width / 100, img.height / 100), dpi=dpi
                )
                ax.axis("off")
                ax.imshow(img)

                pdf.savefig(fig_img, bbox_inches="tight")
                plt.close(fig_img)

                buf.close()

    def fit_frame_prf(self, frame_index, update_positions=False):
        image = self.data[frame_index].astype(float) - self.data[0].astype(
            float
        )
        O = image_to_offsets(image, self.keyframe.Rot @ self.keyframe.Scale)
        r_offset, c_offset = O[:2, 2] - self.keyframe.Offset[:2, 2]
        O2 = np.eye(3)
        O2[:2, 2] = r_offset, c_offset

        frame = Frame(
            image=image,
            pixel_mask=self.pixel_mask,
            cutout_corner=self.cutout_corner,
            poly_order=self.poly_order,
            sip_order=self.sip_order,
            kind=self.kind,
            sigmas=self.sigmas,
            A=self.keyframe.A @ O2.T,
            sip=self.keyframe.sip,
        )
        if update_positions:
            frame.fit_bkg_and_spots()
        else:
            frame.fit_bkg_and_spots(Ls=self.Ls)
        return frame

    def get_prf_hdulist(self, update_position=False):
        hdus = [
            self.fit_frame_prf(
                idx, update_position=update_position
            ).prf_hdulist[1]
            for idx in tqdm(np.arange(1, self.nframes), position=0, leave=True)
        ]
        hdulist = fits.HDUList([primaryHDU(), *hdus])
        self._plot_prf_hdulist(hdulist)
        return hdulist

    def _plot_prf_hdulist(self, hdulist):
        knots = np.arange(-0.5, 6, 0.25)
        rad = np.linspace(0, 3, 1000)
        X = Spline("rad", knots=knots)
        A = X.design_matrix(rad=rad) / 0.25
        normalization = 2 * np.pi * np.abs(knots[1:-2] + 0.125)
        A /= normalization[None, :]
        fig, ax = plt.subplots(dpi=150)
        ims = [
            ax.scatter(
                rad,
                A.dot(hdulist[idx].data["weights"])
                / hdulist[idx].header["norm"],
                c=np.ones(A.shape[0]) * idx,
                vmin=0,
                vmax=55,
                s=0.1,
            )
            for idx in np.arange(1, len(hdulist))
        ]
        ax.set(
            xlabel="Radial Distance from Source", ylabel="Normalized Profile"
        )
        cbar = plt.colorbar(ims[0], ax=ax)
        cbar.set_label("Frame Number")
        if fig.canvas is None or not hasattr(fig.canvas, "print_pdf"):
            FigureCanvas(fig)  # attach a non-GUI canvas
        self.figs.append(fig)
        plt.close(fig)

        norm = np.asarray(
            [hdulist[idx].header["norm"] for idx in np.arange(1, len(hdulist))]
        )
        lin = np.cumsum(
            np.mean(np.diff(norm[20:30])) * np.ones(len(hdulist) - 1)
        )

        fig, ax = plt.subplots()
        ax.plot(np.arange(1, len(hdulist)), norm, c="k", label="Measured")
        ax.plot(
            np.arange(1, len(hdulist)),
            lin,
            c="grey",
            ls="--",
            label="Linear Trend",
        )
        ax.plot()
        ax.set(xlabel="Frame Number", ylabel="Point Normalization [DN]")
        ax.legend()
        if fig.canvas is None or not hasattr(fig.canvas, "print_pdf"):
            FigureCanvas(fig)  # attach a non-GUI canvas
        self.figs.append(fig)
        plt.close(fig)

        rcent = np.asarray(
            [
                hdulist[idx].header["RCENT"]
                for idx in np.arange(1, len(hdulist))
            ]
        )
        ccent = np.asarray(
            [
                hdulist[idx].header["CCENT"]
                for idx in np.arange(1, len(hdulist))
            ]
        )
        rcent -= np.mean(rcent)
        ccent -= np.mean(ccent)

        fig, ax = plt.subplots()
        ax.plot(
            np.arange(1, len(hdulist)),
            rcent,
            c="r",
            ls="--",
            label="Row centroid",
        )
        ax.plot(
            np.arange(1, len(hdulist)),
            ccent,
            c="b",
            ls="--",
            label="Column centroid",
        )
        ax.plot()
        ax.set(xlabel="Frame Number", ylabel="Centroid [pixel]")
        ax.legend()
        if fig.canvas is None or not hasattr(fig.canvas, "print_pdf"):
            FigureCanvas(fig)  # attach a non-GUI canvas
        self.figs.append(fig)
        plt.close(fig)

    def fit_frame(self, frame_index, update_positions=False):
        """Fit an individual frame"""
        if self._calibrated != "Calibrated":
            raise ValueError(
                "Must calibrate the data first before fitting the frames."
            )
        if frame_index == 0:
            raise ValueError(
                "Can not fit the first frame, this is used for subtraction."
            )

        df = pd.DataFrame(
            np.asarray(
                [
                    *self.keyframe.spot_talbot_locations,
                    *(
                        np.asarray(self.keyframe.spot_pixel_locations)
                        + np.asarray(
                            self.keyframe.spot_pixel_location_distortion
                        )
                    ),
                ]
            ).T,
            columns=["spot_row", "spot_column", "pix_row", "pix_column"],
        ).set_index(["spot_row", "spot_column", "pix_row", "pix_column"])
        frame = self.fit_frame_prf(
            frame_index, update_positions=update_positions
        )

        k = frame.pixel_mask.ravel()
        if update_positions:
            Ls = frame.get_spline_spot_design_matrices()
        else:
            Ls = self.Ls
        Lc = np.sum([L.tocsr().multiply(w) for L, w in zip(Ls, frame.weights)])
        Lc.eliminate_zeros()
        prior_mu = np.zeros(Lc.shape[1])
        prior_sigma = np.ones(Lc.shape[1]) * 1e6

        best_fit_weights = sparse.linalg.spsolve(
            Lc[k].T.dot(Lc[k]) + sparse.diags(1 / prior_sigma**2),
            sparse.csc_matrix(
                Lc[k].T.dot((frame.image - frame.bkg).ravel()[k])
            ).T
            + sparse.csr_matrix(prior_mu / prior_sigma**2).T,
        )  # / frame.psf_norm
        # rt, ct = frame.spot_pixel_locations
        # dy, dx = frame.spot_pixel_location_distortion
        # rt -= frame.cutout_center[0] - dy
        # ct -= frame.cutout_center[1] - dx
        tot = np.asarray(
            Lc.multiply(frame.pixel_mask.ravel()[:, None].astype(float)).sum(
                axis=0
            )
        )[0]
        j = tot > 0.7 * tot.max()
        j &= best_fit_weights > 0
        j &= best_fit_weights > (np.median(best_fit_weights[j]) * 0.2)

        df["flux"] = best_fit_weights * frame.psf_norm
        df["quality"] = j.astype(float)
        X = frame.get_spot_polynomial_design_matrix()
        df["bkg"] = X.dot(frame.bkg_weights)
        w = np.linalg.solve(X[j].T.dot(X[j]), X[j].T.dot(df.flux.values[j]))
        correction = X.dot(w) / np.mean(X[j].dot(w))
        df["correction"] = correction
        spot_model = Lc.dot(best_fit_weights).reshape(self.cutout_size)
        bkg_model = (
            frame.get_polynomial_design_matrix()
            .dot(frame.bkg_weights)
            .reshape(self.cutout_size)
        )
        return frame, df, spot_model, bkg_model

    def get_all_hdulists(self, update_positions=False):
        """
        Call this function to get the output of the extractor as fits files.

        Use `update_positions` to set whether each frame updates the positions of the spots.
        This is slower, but if you think the spots move appreciably in each frame you should set this to True.

        Returns
        -------
        prf_hdu: astropy.io.fits.HDUList
            HDUList of the PRF model information, can be used to recreate the PRF model.
        spot_hdu: astropy.io.fits.HDUList
            HDUList of the spot brightness information
        model_hdu: astropy.io.fits.HDUList
            HDUList of the spot model in the cutout region
        bkg_model_hdu: astropy.io.fits.HDUList
            HDUList of the background model in the cutout region
        data_hdu: astropy.io.fits.HDUList
            HDUList of the data in the cutout region
        """
        prf_hdus = []
        spot_hdus = []
        model_hdus = []
        bkg_model_hdus = []
        data_hdus = []
        for idx in tqdm(np.arange(1, self.nframes), position=0, leave=True):
            frame, df, spot_model, bkg_model = self.fit_frame(
                idx, update_positions=update_positions
            )
            prf_hdus.append(frame.prf_hdulist[1])
            spot_hdus.append(
                fits.TableHDU.from_columns(
                    [
                        fits.Column(name=c[0], format="D", array=c[1])
                        for c in df.dropna().reset_index().T.iterrows()
                    ],
                    name=f"FRAME_{idx:02}",
                )
            )
            model_hdus.append(
                fits.CompImageHDU(
                    spot_model,
                    name=f"FRAME_{idx:02}",
                )
            )
            bkg_model_hdus.append(
                fits.CompImageHDU(
                    bkg_model,
                    name=f"FRAME_{idx:02}",
                )
            )
            data_hdus.append(
                fits.CompImageHDU(
                    frame.image,
                    name=f"FRAME_{idx:02}",
                )
            )

        hdu0 = primaryHDU()
        prf_hdulist = fits.HDUList([hdu0, *prf_hdus])
        spot_hdulist = fits.HDUList([hdu0, *spot_hdus])
        model_hdulist = fits.HDUList([hdu0, *model_hdus])
        bkg_model_hdulist = fits.HDUList([hdu0, *bkg_model_hdus])
        data_hdulist = fits.HDUList([hdu0, *data_hdus])
        self._plot_prf_hdulist(prf_hdulist)
        return (
            prf_hdulist,
            spot_hdulist,
            model_hdulist,
            bkg_model_hdulist,
            data_hdulist,
        )
