"""Implements extractor class"""

# Standard library
from functools import lru_cache
from typing import Optional

# Third-party
import fitsio
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from astropy.io import fits
from astropy.time import Time
from lamatrix.models.sip import SIP
from scipy import sparse
from sparse3d import Sparse3D
from tqdm import tqdm

from . import __version__
from .utils import (
    bin2d,
    fit_affine_3x3,
    image_to_cutouts,
    image_to_offsets,
    image_to_RS_matrix,
)


class TalbotExtractor(object):
    """Class for helping to process Talbot data"""

    def __init__(
        self,
        fname: str,
        ref_frame: int = 20,
        bkg_polyorder: int = 3,
        pixel_mask: Optional[npt.NDArray] = None,
        fourier_resolution: int = 6,
        spot_spacing_bounds: tuple = (6, 10),
    ):
        """Class for helping process Talbot data

        This class assumes that the spots from the Talbot experiment are well described by a pair of Gaussians with specified widths.

        Parameters:
        -----------
        fname: str
            File name of Talbot file.
        ref_frame: int
            Frame number for the frame that should be used for image registration.
            Pick a frame that is neither saturated nor too faint.
        bkg_polyorder: int
            What order of polynomial to use to fit any background in the image
        pixel_mask: npt.NDArray
            Boolean mask showing which pixels to include in the data analysis. Use this to mask out bad pixels on the detector.
            Pixels that should not be included should be marked as "False".
        fourier_resolution: int
            The resolution at which to calculate the fourier transform. Higher resolutions are more accurate, but slower.
        spot_spacing_bounds: tuple
            The minimum and maximum spot spacing to test, in units of pixels.
            If spots are approximately 8 pixels apart, set bounds (6, 10) to test
            all spot spacings between 6 pixels and 10 pixels.
        """
        self.fname = fname
        self.bkg_polyorder = bkg_polyorder
        self.nexposures = fitsio.FITS(fname)[1].get_dims()[1]
        self.shape = tuple(fitsio.FITS(fname)[1].get_dims()[2:])
        if self.shape == (4096, 4224):
            self.center = (2048, 2048)
        self.center = (self.shape[0] // 2, self.shape[1] // 2)
        if pixel_mask is None:
            self.pixel_mask = np.ones(self.shape, bool)
        else:
            if pixel_mask.shape == (4096, 4096):
                self.pixel_mask = np.zeros(self.shape, bool)
                self.pixel_mask[:4096, :4096] = pixel_mask.copy()
            elif pixel_mask.shape == self.shape:
                self.pixel_mask = pixel_mask.copy()
            else:
                raise ValueError("Can not parse input `pixel_mask'")

        self.ref_frame = ref_frame
        self.fourier_resolution = fourier_resolution
        self.spot_spacing_bounds = spot_spacing_bounds
        self.sip = None
        self._rough_position_calibration()
        self._refine_position_calibration()

    def __repr__(self):
        return "TalbotExtractor"

    def _get_cutout_corners(self, cutout_size):
        """Get the corners of the cutout inside the original image."""
        a1, a2 = (
            np.max([self.center[0] - cutout_size[0] // 2, 0]),
            np.min([self.center[0] + cutout_size[0] // 2, self.shape[1]]),
        )
        b1, b2 = (
            np.max([self.center[1] - cutout_size[1] // 2, 0]),
            np.min([self.center[1] + cutout_size[1] // 2, self.shape[1]]),
        )
        return a1, a2, b1, b2

    def _get_cutout_center(self, cutout_size):
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        return (a2 - a1) // 2, (b2 - b1) // 2

    def _get_cutout_shape(self, cutout_size):
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        return (a2 - a1, b2 - b1)

    def _get_image_center(self):
        return (self.shape[0] // 2, self.shape[1] // 2)

    @lru_cache(maxsize=4)
    def _load_frame(self, idx=0, cutout_size=(512, 512)):
        """Load an frame from the center of the Talbot dataset. Will only load the frame index and cutout size specified."""
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        return fitsio.FITS(self.fname)[1][0, idx : idx + 1, a1:a2, b1:b2][
            0, 0
        ].astype(float)

    def _load_mask(self, cutout_size=(512, 512)):
        """Load an frame from the center of the Talbot dataset. Will only load the frame index and cutout size specified."""
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        return self.pixel_mask[a1:a2, b1:b2].copy()

    def _rough_position_calibration(
        self,
        cutout_size: tuple = (512, 512),
    ):
        """Roughly calibrate the positions of the data using the central region

        Parameters:
        -----------
        cutout_size: tuple
            The size of the region of the detector to use.
        """
        frame = self._load_frame(
            self.ref_frame, cutout_size=cutout_size
        ) - self._load_frame(0, cutout_size=cutout_size)
        frame_mask = self._load_mask(cutout_size=cutout_size)
        frame[~frame_mask] = np.nanmedian(frame[frame_mask])
        R, C = np.mgrid[: cutout_size[0], : cutout_size[1]]
        R -= cutout_size[0] // 2
        C -= cutout_size[1] // 2
        self.Rot, self.Scale = image_to_RS_matrix(
            frame,
            fourier_resolution=self.fourier_resolution,
            minimum_period=self.spot_spacing_bounds[0],
            maximum_period=self.spot_spacing_bounds[0],
        )
        self.Offset = image_to_offsets(
            frame, self.Rot @ self.Scale, mask=frame_mask
        )
        self.A = self.Rot @ self.Scale @ self.Offset.T
        self.Ainv = np.linalg.inv(self.A)

    def _refine_position_calibration(self):
        for count in [0, 1, 2]:
            # In the first round we calculate the distortion in a small region and update the affine transform matrix
            # In the second round we recalculate the disortion in a larger region
            if count == 0:
                cutout_size = (512, 512)
                order = 3
            if count == 1:
                cutout_size = (512, 512)
                order = 3
            if count == 2:
                cutout_size = (1024, 1024)
                order = 4
            # if count == 3:
            #     cutout_size = (2048, 2048)
            #     order = 4
            bkg, _, _, _, _, _ = self._fit_poly_model(
                frame=self.ref_frame, cutout_size=cutout_size
            )
            im = self._load_frame(
                self.ref_frame, cutout_size=cutout_size
            ) - self._load_frame(0, cutout_size=cutout_size)
            im_mask = self._load_mask(cutout_size=cutout_size)
            im_mask &= (im - bkg) > 0

            a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
            cutout_center = self._get_cutout_center(cutout_size=cutout_size)
            cutout_shape = self._get_cutout_shape(cutout_size=cutout_size)

            R, C = np.mgrid[a1:a2, b1:b2]
            R -= cutout_center[0]
            C -= cutout_center[1]

            coords1, coords2 = self.get_spot_grid(
                cutout_size=cutout_size, include_distortion=False
            )
            r, c = coords1
            rt, ct = coords2
            cdx, rdx = (
                np.round(ct + cutout_center[1]).astype(int),
                np.round(rt + cutout_center[0]).astype(int),
            )
            rdx_l, cdx_l = np.asarray(
                [
                    [[rdx + idx], [cdx + jdx]]
                    for idx, jdx in np.mgrid[-1:2, -1:2][
                        :, np.ones((3, 3), bool)
                    ].T
                ]
            )[:, :, 0, :].transpose([1, 0, 2])
            rdx_l, cdx_l = np.hstack(rdx_l), np.hstack(cdx_l)
            rt_l, ct_l = np.hstack([rt] * 9), np.hstack([ct] * 9)
            mask = (
                (cdx_l >= 0)
                & (rdx_l >= 0)
                & (rdx_l < cutout_shape[1])
                & (cdx_l < cutout_shape[0])
            )
            mask[mask] &= im_mask[rdx_l[mask], cdx_l[mask]]
            mask[mask] &= (
                im[rdx_l[mask], cdx_l[mask]] > np.percentile(im[im_mask], 0.1)
            ) & (
                im[rdx_l[mask], cdx_l[mask]]
                < np.percentile(im[im_mask], 99.99)
            )
            self.sip = SIP(order=order)
            self.sip.fit(
                x=C[rdx_l[mask], cdx_l[mask]].astype(float),
                y=R[rdx_l[mask], cdx_l[mask]].astype(float),
                dx=cdx_l[mask] - ct_l[mask] - cutout_center[1],
                dy=rdx_l[mask] - rt_l[mask] - cutout_center[0],
                data=np.log(
                    im[rdx_l[mask], cdx_l[mask]]
                    - bkg[rdx_l[mask], cdx_l[mask]]
                ),
                errors=im[rdx_l[mask], cdx_l[mask]] ** 0.5
                / im[rdx_l[mask], cdx_l[mask]],
            )

            if count != 2:
                # If not the last round, update the internal affine transform matrix
                coords1, coords2 = self.get_spot_grid(
                    cutout_size=cutout_size, include_distortion=True
                )
                r, c = coords1
                rt, ct = coords2
                self.A = fit_affine_3x3(
                    np.asarray([r, c]).T, np.asarray([rt, ct]).T
                ).T
                self.Ainv = np.linalg.inv(self.A)

    def get_spot_grid(self, cutout_size=(512, 512), include_distortion=True):
        """Get a grid of spot positions"""
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        ac, bc = self._get_cutout_center(cutout_size=cutout_size)
        a1, a2, b1, b2 = a1 - ac, a2 - ac, b1 - bc, b2 - bc
        corners = np.asarray(
            [
                (a1, b1, 1),
                (a1, b2, 1),
                (a2, b1, 1),
                (a2, b2, 1),
            ]
        )
        rt, ct = (corners @ self.Ainv)[:, :2].T
        r, c = np.mgrid[
            np.floor(np.min(rt)) - 1 : np.ceil(np.max(rt)) + 2,
            np.floor(np.min(ct)) - 1 : np.ceil(np.max(ct)) + 2,
        ]
        rt, ct, _ = (
            np.asarray([r.ravel(), c.ravel(), r.ravel() ** 0]).T @ self.A
        ).T
        if include_distortion:
            if self.sip is not None:
                c_corr = self.sip.mu_x_to_Polynomial().evaluate(
                    x=ct.astype(float), y=rt.astype(float)
                )
                r_corr = self.sip.mu_y_to_Polynomial().evaluate(
                    x=ct.astype(float), y=rt.astype(float)
                )
                ct += c_corr
                rt += r_corr
        return np.asarray([r.ravel(), c.ravel()]), np.asarray([rt, ct])

    def _build_spot_design_matrix(
        self, cutout_size=(512, 512), sigma1=0.6, sigma2=2, subimage_size=7
    ):
        """Creates two design matrices. Each contain a Gaussian at every spot location, with the widths defined by sigma1 and sigma2."""
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        _, coords2 = self.get_spot_grid(cutout_size=cutout_size)
        cutout_center = self._get_cutout_center(cutout_size=cutout_size)
        rt, ct = coords2
        nsources = len(rt)
        source_row_int, source_row_phase = (
            np.floor(rt + cutout_center[0] // 2).astype(int),
            (rt + cutout_center[0] // 2) % 1,
        )
        source_col_int, source_col_phase = (
            np.floor(ct + cutout_center[1] // 2).astype(int),
            (ct + cutout_center[1] // 2) % 1,
        )
        sR, sC = np.mgrid[:subimage_size, :subimage_size] - subimage_size // 2
        row3d = sR[:, :, None] + source_row_int
        col3d = sC[:, :, None] + source_col_int
        x3d = sR[:, :, None] * np.ones(nsources)
        y3d = sC[:, :, None] * np.ones(nsources)

        dX1 = Sparse3D(
            -0.5 * (x3d - source_row_phase) ** 2 / sigma1**2,
            row3d,
            col3d,
            imshape=(a2 - a1, b2 - b1),
        )
        dY1 = Sparse3D(
            -0.5 * (y3d - source_col_phase) ** 2 / sigma1**2,
            row3d,
            col3d,
            imshape=(a2 - a1, b2 - b1),
        )
        L1 = np.exp(dX1 + dY1) * (1 / (2 * np.pi * sigma1**2))

        dX1 = Sparse3D(
            -0.5 * (x3d - source_row_phase) ** 2 / sigma2**2,
            row3d,
            col3d,
            imshape=(a2 - a1, b2 - b1),
        )
        dY1 = Sparse3D(
            -0.5 * (y3d - source_col_phase) ** 2 / sigma2**2,
            row3d,
            col3d,
            imshape=(a2 - a1, b2 - b1),
        )
        L2 = np.exp(dX1 + dY1) * (1 / (2 * np.pi * sigma2**2))
        return L1, L2

    def _fit_poly_model(
        self,
        frame,
        sigma1=0.6,
        sigma2=2,
        cutout_size=(512, 512),
        subimage_size=7,
        plot=False,
    ):
        """This function fits a model to the data which consists of a background and a set of spots.
        All the spots share flux set by a 2D polynomial."""
        im = self._load_frame(
            frame, cutout_size=cutout_size
        ) - self._load_frame(0, cutout_size=cutout_size)
        im_mask = self._load_mask(cutout_size=cutout_size)
        a1, a2, b1, b2 = self._get_cutout_corners(cutout_size=cutout_size)
        ac, bc = self._get_cutout_center(cutout_size=cutout_size)
        cutout_shape = self._get_cutout_shape(cutout_size=cutout_size)
        R, C = np.mgrid[a1:a2, b1:b2]
        R -= ac
        C -= bc

        X = np.vstack(
            [
                (R.ravel()) ** idx * (C.ravel()) ** jdx
                for idx in range(self.bkg_polyorder + 1)
                for jdx in range(self.bkg_polyorder + 1)
            ]
        ).T
        L1, L2 = self._build_spot_design_matrix(
            cutout_size=cutout_size,
            sigma1=sigma1,
            sigma2=sigma2,
            subimage_size=subimage_size,
        )
        Lc1 = L1.tocsr()
        Lc2 = L2.tocsr()
        k = im_mask.ravel()
        S = np.vstack(
            [
                X.T,
                Lc1.dot(np.ones(Lc1.shape[1])).ravel() * X.T,
                Lc2.dot(np.ones(Lc2.shape[1])).ravel() * X.T,
            ]
        ).T
        w = np.linalg.solve(S[k].T.dot(S[k]), S[k].T.dot(im.ravel()[k]))
        bkg_w = w[: X.shape[1]]
        bkg = X.dot(bkg_w).reshape(cutout_shape)
        model = S[:, X.shape[1] :].dot(w[X.shape[1] :]).reshape(cutout_shape)
        amp = np.asarray(
            [
                np.asarray(np.array_split(w, 3))[1, 0],
                np.asarray(np.array_split(w, 3))[2, 0],
            ]
        )
        L = (L1 * amp[0]) + (L2 * amp[1])
        chi = np.sum(((im - model - bkg) ** 2 / (im))[im_mask]) / im_mask.sum()
        if plot:
            _, coords2 = self.get_spot_grid(
                cutout_size=cutout_size, include_distortion=True
            )
            rt, ct = coords2

            source_row_phase = (rt + cutout_size[0] // 2) % 1
            # source_col_phase = (ct + cutout_size[1] // 2) % 1
            x3d, y3d = (
                np.mgrid[:subimage_size, :subimage_size] - subimage_size // 2
            )
            x3d = x3d[:, :, None] * np.ones(rt.shape[0])
            y3d = y3d[:, :, None] * np.ones(ct.shape[0])
            fig, ax = plt.subplots()
            stamps = image_to_cutouts(
                im - bkg,
                rt + cutout_shape[0] // 2,
                ct + cutout_shape[1] // 2,
                subimage_size,
            )
            ax.scatter(
                (x3d - source_row_phase[None, None, :]).ravel(),
                np.log10(stamps.ravel()),
                s=0.001,
                c="grey",
            )
            stamps = image_to_cutouts(
                model,
                rt + cutout_shape[0] // 2,
                ct + cutout_shape[1] // 2,
                subimage_size,
            )
            ax.scatter(
                (x3d - source_row_phase[None, None, :]).ravel(),
                np.log10(stamps.ravel()),
                s=0.001,
                c="red",
            )

        return bkg, bkg_w, model, amp, L, chi

    def plot_registration(self, cutout_size=(512, 512)):
        """Plot a diagnostic of the registration of the spot grid."""
        im = self._load_frame(
            self.ref_frame, cutout_size=cutout_size
        ) - self._load_frame(0, cutout_size=cutout_size)
        im_mask = self._load_mask(cutout_size=cutout_size)

        shape = self._get_cutout_shape((1024, 1024))
        R, C = np.mgrid[: shape[0], : shape[1]].astype(float)
        R -= shape[0] // 2
        C -= shape[1] // 2
        fig, ax = plt.subplots(2, 2, figsize=(8, 10))
        if self.sip is not None:
            imshow = ax[0, 0].pcolormesh(
                C,
                R,
                self.sip.mu_x_to_Polynomial().evaluate(
                    x=C.astype(float), y=R.astype(float)
                ),
                vmin=-0.2,
                vmax=0.2,
            )
            imshow = ax[0, 1].pcolormesh(
                C,
                R,
                self.sip.mu_y_to_Polynomial().evaluate(
                    x=C.astype(float), y=R.astype(float)
                ),
                vmin=-0.2,
                vmax=0.2,
            )
            ax[0, 0].set(
                aspect="equal",
                xlabel="Column Pixel",
                ylabel="Row Pixel",
                title="Column Position Distortion",
            )
            ax[0, 1].set(
                aspect="equal",
                xlabel="Column Pixel",
                title="Row Position Distortion",
            )
            plt.subplots_adjust(wspace=0.1)
            cbar = plt.colorbar(imshow, ax=ax[0, 0], orientation="horizontal")
            cbar.set_label("$\delta$ Pixel")
            cbar = plt.colorbar(imshow, ax=ax[0, 1], orientation="horizontal")
            cbar.set_label("$\delta$ Pixel")

        _, coords2 = self.get_spot_grid(
            cutout_size=cutout_size, include_distortion=False
        )
        # r, c = coords1
        rt, ct = coords2
        cdx, rdx = (
            np.round(ct + shape[1] // 2).astype(int),
            np.round(rt + shape[0] // 2).astype(int),
        )
        rdx_l, cdx_l = np.asarray(
            [
                [[rdx + idx], [cdx + jdx]]
                for idx, jdx in np.mgrid[-1:2, -1:2][
                    :, np.ones((3, 3), bool)
                ].T
            ]
        )[:, :, 0, :].transpose([1, 0, 2])
        rdx_l, cdx_l = np.hstack(rdx_l), np.hstack(cdx_l)
        rt_l, ct_l = np.hstack([rt] * 9), np.hstack([ct] * 9)
        l = (
            (cdx_l >= 0)
            & (rdx_l >= 0)
            & (rdx_l < shape[0])
            & (cdx_l < shape[1])
        )
        l[l] &= im_mask[rdx_l[l], cdx_l[l]]
        l[l] &= (im[rdx_l[l], cdx_l[l]] > np.percentile(im[im_mask], 0.1)) & (
            im[rdx_l[l], cdx_l[l]] < np.percentile(im[im_mask], 99.99)
        )
        imshow = bin2d(
            row=rdx_l[l] - rt_l[l] - shape[0] // 2,
            col=cdx_l[l] - ct_l[l] - shape[1] // 2,
            value=im[rdx_l[l], cdx_l[l]],
            bin_width=0.025,
            ax=ax[1, 0],
            vmin=np.percentile(im, 50),
            vmax=np.percentile(im, 99),
        )
        ax[1, 0].set(
            xlabel="$\delta$ Column",
            ylabel="$\delta$ Row",
            aspect="equal",
            title="Affine Transform",
            xlim=(-2, 2),
            ylim=(-2, 2),
        )
        cbar = plt.colorbar(imshow, ax=ax[1, 0], orientation="horizontal")
        cbar.set_label("Image Brightness")
        if self.sip is not None:
            c_corr = self.sip.mu_x_to_Polynomial().evaluate(
                x=ct_l.astype(float), y=rt_l.astype(float)
            )
            r_corr = self.sip.mu_y_to_Polynomial().evaluate(
                x=ct_l.astype(float), y=rt_l.astype(float)
            )
            imshow = bin2d(
                row=rdx_l[l] - rt_l[l] - r_corr[l] - self.shape[0] // 2,
                col=cdx_l[l] - ct_l[l] - c_corr[l] - self.shape[1] // 2,
                value=im[rdx_l[l], cdx_l[l]],
                bin_width=0.025,
                ax=ax[1, 1],
                vmin=np.percentile(im, 50),
                vmax=np.percentile(im, 99),
            )
            ax[1, 1].set(
                xlabel="$\delta$ Column",
                ylabel="$\delta$ Row",
                aspect="equal",
                title="Affine Transform and Distortion",
                xlim=(-2, 2),
                ylim=(-2, 2),
            )
            cbar = plt.colorbar(imshow, ax=ax[1, 1], orientation="horizontal")
            cbar.set_label("Image Brightness")
        return fig

    def extract_spots(self, cutout_size=(512, 512), subimage_size=7):
        """Extracts the spot flux and positions for the file as a function of frame number.

        Returns:
        -------
        hdulist: astropy.io.fits.HDUList
            An HDUList object with the extracted data for the spots across each frame of the data.
        """
        coords1, coords2 = self.get_spot_grid(cutout_size=cutout_size)
        r, c = coords1
        rt, ct = coords2
        nsources = len(rt)
        im_mask = self._load_mask(cutout_size=cutout_size)

        Xs = np.vstack(
            [
                rt**idx * ct**jdx
                for idx in range(self.bkg_polyorder + 1)
                for jdx in range(self.bkg_polyorder + 1)
            ]
        ).T
        prior_mu = np.zeros(nsources)
        prior_sigma = np.ones(nsources) * 1e6
        k = im_mask.ravel()

        fits_df = pd.DataFrame(
            np.asarray([r, c, rt, ct]).T,
            columns=["spot_row", "spot_column", "pix_row", "pix_column"],
        ).set_index(["spot_row", "spot_column", "pix_row", "pix_column"])

        hdu0 = fits.PrimaryHDU()
        hdu0.header["AUTHOR"] = "Christina Hedges"
        hdu0.header["PIPELINE"] = "TalbotExtractor"
        hdu0.header["VERSION"] = __version__
        hdu0.header["DATE"] = Time.now().isot
        hdu0.header["FNAME"] = self.fname

        hdulist = fits.HDUList([hdu0])
        for tdx in tqdm(np.arange(1, self.nexposures), position=0, leave=True):
            im = self._load_frame(
                tdx, cutout_size=cutout_size
            ) - self._load_frame(0, cutout_size=cutout_size)
            bkg, bkg_w, model, amp, L, chi = self._fit_poly_model(
                frame=1, cutout_size=cutout_size
            )
            Lc = L.tocsr()
            fits_df["bkg"] = Xs.dot(bkg_w)

            best_fit_weights = sparse.linalg.spsolve(
                Lc[k].T.dot(Lc[k]) + sparse.diags(1 / prior_sigma**2),
                sparse.csc_matrix(Lc[k].T.dot((im - bkg).ravel()[k])).T
                + sparse.csr_matrix(prior_mu / prior_sigma**2).T,
            )
            sigma_w = sparse.linalg.inv(
                Lc.T.dot(Lc) + sparse.diags(1 / prior_sigma**2)
            )
            best_fit_weights_err = sigma_w.diagonal() ** 0.5
            with np.errstate(divide="ignore"):
                best_fit_weights[
                    np.abs(best_fit_weights_err / best_fit_weights) > 0.2
                ] = np.nan
                best_fit_weights_err[
                    np.abs(best_fit_weights_err / best_fit_weights) > 0.2
                ] = np.nan
            tot = np.asarray(Lc[k].sum(axis=0))[0]
            best_fit_weights[tot < np.median(tot) * 0.95] = np.nan
            best_fit_weights_err[tot < np.median(tot) * 0.95] = np.nan
            fits_df["flux"] = best_fit_weights * amp.sum()
            fits_df["flux_err"] = best_fit_weights_err * amp.sum()

            im_stack = image_to_cutouts(
                im,
                rt + self.shape[0] // 2,
                ct + self.shape[1] // 2,
                subimage_size,
            )
            model_stack = image_to_cutouts(
                L.dot(best_fit_weights) + bkg,
                rt + self.shape[0] // 2,
                ct + self.shape[1] // 2,
                subimage_size,
            )
            with np.errstate(invalid="ignore"):
                chi = np.nansum(
                    ((im_stack - model_stack) ** 2 / im_stack**0.5),
                    axis=(0, 1),
                ) / (subimage_size**2)
            chi[
                ~np.isfinite(best_fit_weights)
                | ~np.isfinite(best_fit_weights_err)
            ] = np.nan
            fits_df["chi"] = chi
            hdulist.append(
                fits.TableHDU.from_columns(
                    [
                        fits.Column(name=c[0], format="D", array=c[1])
                        for c in fits_df.dropna().reset_index().T.iterrows()
                    ],
                    name=f"FRAME_{tdx:02}",
                )
            )
        return hdulist
