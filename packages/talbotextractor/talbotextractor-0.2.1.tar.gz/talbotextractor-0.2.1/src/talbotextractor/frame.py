"""Class to work with a single frame from Talbot Illuminator exposures"""

# Standard library
import warnings
from typing import Optional, Tuple

# Third-party
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from astropy.io import fits
from corner import hist2d
from lamatrix import SIP, Spline
from scipy.ndimage import convolve
from sparse3d import Sparse3D

# First-party/Local
from talbotextractor.utils import (
    bin2d,
    fit_affine_3x3,
    image_to_cutouts,
    image_to_offsets,
    image_to_RS_matrix,
)
from .utils import primaryHDU

warnings.filterwarnings(
    "ignore", message="divide by zero encountered in divide"
)


class Frame(object):
    """Object to hold and work with a frame from the Talbot Illuminator"""

    def __init__(
        self,
        image: npt.NDArray,
        pixel_mask: Optional[npt.NDArray] = None,
        cutout_corner: Tuple = (0, 0),
        A: Optional[npt.NDArray] = None,
        sip: Optional[SIP] = None,
        poly_order=7,
        sip_order=3,
        kind: str = "spline",
        sigmas: Tuple = (0.6, 2),
    ):
        """Class for helping process Talbot frame

        Parameters:
        -----------
        image: npt.NDArray
            Data from the frame
        pixel_mask: npt.NDArray
            Boolean mask showing which pixels to include in the data analysis. Use this to mask out bad pixels on the detector.
            Pixels that should not be included should be marked as "False".
        cutout_corner: tuple
            The location in pixel space of the lower left corner in format (row, column)
        A: np.ndarray
            The affine transform matrix
        sip: lamatrix.SIP
            The SIP object for fitting the distortion matrix
        poly_order: int
            The polynomial order for any background components
        sip_order: int
            The polynomial order for the distortion model. This is only used if no SIP object is passed.
        kind: string
            Kind of modeling to do. Choose between "spline", "gaussian"
        sigmas: list
            Standard deviations for Gaussians, if using "gaussian" kind of modeling.
        """
        self.image = image
        self.cutout_corner = cutout_corner
        self.kind = kind
        self.sigmas = sigmas

        self.cutout_size = self.image.shape
        self.cutout_center = (
            self.cutout_corner[0] + self.cutout_size[0] // 2,
            self.cutout_corner[1] + self.cutout_size[1] // 2,
        )
        self.cutout_points = np.asarray(
            [
                [self.cutout_corner[0], self.cutout_corner[1], 1],
                [
                    self.cutout_corner[0] + self.cutout_size[0],
                    self.cutout_corner[1],
                    1,
                ],
                [
                    self.cutout_corner[0] + self.cutout_size[0],
                    self.cutout_corner[1] + self.cutout_size[1],
                    1,
                ],
                [
                    self.cutout_corner[0],
                    self.cutout_corner[1] + self.cutout_size[1],
                    1,
                ],
                [self.cutout_corner[0], self.cutout_corner[1], 1],
            ]
        )
        self.cutout_bounds = self.cutout_points - np.asarray(
            [*self.cutout_center, 0]
        )

        if pixel_mask is None:
            self.pixel_mask = np.ones(self.cutout_size, bool)
        else:
            self.pixel_mask = pixel_mask.copy()
        if A is None:
            self.A = np.eye(3)
        else:
            self.A = A
        if sip is None:
            self.sip = SIP(order=sip_order)
        else:
            self.sip = sip
        self.poly_order = poly_order

        # Fill in masked values, we can't mask in Fourier space
        self.image[~self.pixel_mask] = np.nanmedian(self.image)

        self.R, self.C = np.mgrid[: self.cutout_size[0], : self.cutout_size[1]]
        self.R += self.cutout_corner[0]
        self.C += self.cutout_corner[1]

        self.bkg = np.percentile(self.image, 20)
        self.spot_normalization = 1
        # self.rcent, self.ccent = 0, 0

    @property
    def Ainv(self):
        return np.linalg.inv(self.A)

    def shape(self):
        return self.image.shape

    def __repr__(self):
        return f"TalbotFrame {self.cutout_size}"

    def _get_offset_matrix(self, plot=False):
        if not hasattr(self, "Rot"):
            raise ValueError("Calculate rough position calibration first")
        return image_to_offsets(
            (self.image - self.bkg) / self.spot_normalization,
            self.Rot @ self.Scale,
            mask=self.pixel_mask,
            plot=plot,
        )

    def _rough_position_calibration(
        self,
        fourier_resolution: int = 6,
        spot_spacing_bounds: tuple = (6, 10),
        plot=False,
    ):
        """Roughly calibrate the positions of the data using the central region"""
        r = image_to_RS_matrix(
            (self.image - self.bkg) / self.spot_normalization,
            fourier_resolution=fourier_resolution,
            minimum_period=spot_spacing_bounds[0],
            maximum_period=spot_spacing_bounds[1],
            plot=plot,
        )
        if plot:
            self.Rot, self.Scale, fig1 = r
        else:
            self.Rot, self.Scale = r

        if plot:
            self.Offset, fig2 = self._get_offset_matrix(plot=True)
        else:
            self.Offset = self._get_offset_matrix(plot=False)

        self.A = self.Rot @ self.Scale @ self.Offset.T
        if plot:
            return fig1, fig2

    @property
    def spot_talbot_locations(self):
        rt, ct = (self.cutout_bounds @ self.Ainv)[:, :2].T
        r, c = np.mgrid[
            np.floor(np.min(rt)) - 1 : np.ceil(np.max(rt)) + 2,
            np.floor(np.min(ct)) - 1 : np.ceil(np.max(ct)) + 2,
        ]
        return r.ravel(), c.ravel()

    @property
    def spot_pixel_locations(self):
        """Get a grid of spot positions"""
        r, c = self.spot_talbot_locations
        rt, ct, _ = (
            np.asarray([r.ravel(), c.ravel(), r.ravel() ** 0]).T @ self.A
        ).T
        return rt + self.cutout_center[0], ct + self.cutout_center[1]

    @property
    def spot_pixel_location_distortion(self):
        rt, ct = self.spot_pixel_locations
        if self.sip is not None:
            if np.all(self.sip.posteriors.mean == 0):
                dx = np.zeros(self.nspots)
                dy = np.zeros(self.nspots)
            else:
                dx = self.sip.mu_x_to_Model().evaluate(
                    x=(ct - self.cutout_center[1]) / self.cutout_size[1],
                    y=(rt - self.cutout_center[0]) / self.cutout_size[0],
                )
                dy = self.sip.mu_y_to_Model().evaluate(
                    x=(ct - self.cutout_center[1]) / self.cutout_size[1],
                    y=(rt - self.cutout_center[0]) / self.cutout_size[0],
                )
        else:
            dx = np.zeros(self.nspots)
            dy = np.zeros(self.nspots)
        return dy, dx

    @property
    def nspots(self):
        return len(self.spot_pixel_locations[0])

    def get_stamps(self, image, subimage_size=6):
        rt, ct = self.spot_pixel_locations
        stamps = image_to_cutouts(
            image,
            rt - self.cutout_corner[0],
            ct - self.cutout_corner[1],
            subimage_size,
        )
        sR, sC = (
            np.mgrid[:subimage_size, :subimage_size] - subimage_size // 2 + 1
        )
        return sR[:, :, None] - (rt % 1), sC[:, :, None] - (ct % 1), stamps

    def get_gaussian_spot_design_matrices(self, subimage_size=19):
        rt, ct = self.spot_pixel_locations
        dy, dx = self.spot_pixel_location_distortion
        rt += dy
        ct += dx
        # nsources = len(rt)
        source_row_int, source_col_int = (
            np.floor(rt).astype(int),
            np.floor(ct).astype(int),
        )
        sR, sC = (
            np.mgrid[:subimage_size, :subimage_size] - subimage_size // 2 + 1
        )
        row3d = sR[:, :, None] + source_row_int
        col3d = sC[:, :, None] + source_col_int
        Ls = []
        for sigma in self.sigmas:
            dR1 = Sparse3D(
                data=-0.5 * (row3d - rt) ** 2 / sigma**2,
                row=row3d - self.cutout_corner[0],
                col=col3d - self.cutout_corner[1],
                imshape=self.cutout_size,
            )
            dC1 = Sparse3D(
                data=-0.5 * (col3d - ct) ** 2 / sigma**2,
                row=row3d - self.cutout_corner[0],
                col=col3d - self.cutout_corner[1],
                imshape=self.cutout_size,
            )
            Ls.append(np.exp(dR1 + dC1) * (1 / (2 * np.pi * sigma**2)))
        return Ls

    def get_spline_spot_design_matrices(self, subimage_size=19):
        rt, ct = self.spot_pixel_locations
        dy, dx = self.spot_pixel_location_distortion
        rt += dy
        ct += dx
        # nsources = len(rt)
        source_row_int, source_col_int = (
            np.floor(rt).astype(int),
            np.floor(ct).astype(int),
        )
        sR, sC = (
            np.mgrid[:subimage_size, :subimage_size] - subimage_size // 2 + 1
        )
        row3d = sR[:, :, None] + source_row_int
        col3d = sC[:, :, None] + source_col_int
        rad = np.hypot(row3d - rt, col3d - ct)
        # Fixed 0.5 pixel spacing...
        knots = np.arange(-0.5, 6, 0.25)
        X = Spline("rad", knots=knots)
        A = X.design_matrix(rad=rad) / 0.25
        normalization = 2 * np.pi * np.abs(knots[1:-2] + 0.125)
        A /= normalization[None, :]
        Ls = [
            Sparse3D(
                data=A[:, :, :, idx],
                row=row3d - self.cutout_corner[0],
                col=col3d - self.cutout_corner[1],
                imshape=self.cutout_size,
            )
            for idx in range(A.shape[3])
        ]
        return Ls

    def get_polynomial_design_matrix(self):
        def poly(R, C):
            return np.vstack(
                [
                    (R.ravel()) ** idx * (C.ravel()) ** jdx
                    for idx in range(self.poly_order + 1)
                    for jdx in range(self.poly_order + 1)
                ]
            ).T

        X = poly(
            (self.R - self.cutout_center[0]) / (self.cutout_size[0]),
            (self.C - self.cutout_center[1]) / self.cutout_size[1],
        )
        return X

    def get_spot_polynomial_design_matrix(self):
        rt, ct = self.spot_pixel_locations
        dy, dx = self.spot_pixel_location_distortion
        rt -= self.cutout_center[0] - dy
        ct -= self.cutout_center[1] - dx

        def poly(R, C):
            return np.vstack(
                [
                    (R) ** idx * (C) ** jdx
                    for idx in range(self.poly_order + 1)
                    for jdx in range(self.poly_order + 1)
                ]
            ).T

        X = poly(
            (rt) / (self.cutout_size[0]),
            (ct) / self.cutout_size[1],
        )
        return X

    def _fit_bkg_and_spots_spline(self, Ls=None):
        X = self.get_polynomial_design_matrix()
        if Ls is None:
            Ls = self.get_spline_spot_design_matrices()
        S = np.vstack(
            [
                X.T,
                *[L.dot(np.ones(L.shape[1])).ravel() for L in Ls],
            ]
        ).T
        k = self.pixel_mask.copy().ravel()
        Sk = S[k]
        sigma_w_inv = Sk.T.dot(Sk)
        w = np.linalg.solve(sigma_w_inv, Sk.T.dot(self.image.ravel()[k]))
        spline_weights = w[(self.poly_order + 1) ** 2 :]
        L = np.sum([L.multiply(w).tocsr() for L, w in zip(Ls, spline_weights)])
        A = np.vstack([X.T, L.dot(np.ones(L.shape[1])) * X.T]).T
        Ak = A[k]
        sigma_w_inv = Ak.T.dot(Ak)
        v = np.linalg.solve(sigma_w_inv, Ak.T.dot(self.image.ravel()[k]))

        bkg = A[:, : X.shape[1]].dot(v[: X.shape[1]]).reshape(self.cutout_size)
        spots = (
            A[:, X.shape[1] :].dot(v[X.shape[1] :]).reshape(self.cutout_size)
        )
        spot_normalization = X.dot(v[X.shape[1] :]).reshape(self.cutout_size)
        spot_normalization *= spline_weights.sum()

        # s = np.argsort((self.image - bkg - spots).ravel())
        # cut out top and bottom 0.5%
        # ns = int(np.ceil(len(s) * 0.005))
        # k[np.hstack([s[:ns], s[-ns:]])] = False
        # update pixel mask
        resids = (self.image - bkg) / spot_normalization - (
            spots / spot_normalization
        )
        self.pixel_mask &= resids < 0.5
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        self.pixel_mask &= np.abs(convolve(resids, laplacian)) < 1
        self.bkg_weights = v[: X.shape[1]]
        self.bkg = bkg
        self.spots = spots
        self.weights = spline_weights
        R, C = np.mgrid[-10:10:300j, -10:10:299j]
        rad = (R**2 + C**2) ** 0.5
        knots = np.arange(-0.5, 6, 0.25)
        X = Spline("rad", knots=knots)
        A = X.design_matrix(rad=rad) / 0.25
        normalization = 2 * np.pi * np.abs(knots[1:-2] + 0.125)
        A /= normalization[None, :]
        self.psf_norm = np.trapz(
            np.trapz(A.dot(self.weights), R[:, 0], axis=0), C[0]
        )
        self.spot_normalization = spot_normalization

    def _fit_bkg_and_spots_gaussian(self, Ls=None):
        X = self.get_polynomial_design_matrix()
        if Ls is None:
            Ls = self.get_gaussian_spot_design_matrices()
        S = np.vstack(
            [
                X.T,
                *[L.dot(np.ones(L.shape[1])).ravel() * X.T for L in Ls],
            ]
        ).T

        k = self.pixel_mask.copy().ravel()
        for count in range(3):
            Sk = S[k]
            sigma_w_inv = Sk.T.dot(Sk)
            w = np.linalg.solve(sigma_w_inv, Sk.T.dot(self.image.ravel()[k]))
            bkg = X.dot(w[: (self.poly_order + 1) ** 2]).reshape(
                self.cutout_size
            )
            spots = (
                S[:, (self.poly_order + 1) ** 2 :]
                .dot(np.hstack(w[(self.poly_order + 1) ** 2 :]))
                .reshape(self.cutout_size)
            )
            s = np.argsort((self.image - bkg - spots).ravel())
            # cut out top and bottom 0.5%
            ns = int(np.ceil(len(s) * 0.005))
            k[np.hstack([s[:ns], s[-ns:]])] = False
        pol = (self.poly_order + 1) ** 2
        spot_normalization = (
            X.dot(w[pol : 2 * pol]) + X.dot(w[2 * pol : 3 * pol])
        ).reshape(self.cutout_size)
        # update pixel mask
        resids = (self.image - bkg) / spot_normalization - (
            spots / spot_normalization
        )
        self.pixel_mask &= resids < 0.5
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        self.pixel_mask &= np.abs(convolve(resids, laplacian)) < 1
        self.bkg = bkg
        self.spots = spots
        self.weights = [w[idx * pol] for idx in np.arange(1, len(Ls) + 1)]
        self.psf_norm = 1
        self.spot_normalization = spot_normalization

    def fit_bkg_and_spots(self, Ls=None):
        if self.kind.lower() == "gaussian":
            self._fit_bkg_and_spots_gaussian(Ls=Ls)
        elif self.kind.lower() == "spline":
            self._fit_bkg_and_spots_spline(Ls=Ls)

    def _refine_position_calibration(self, plot=False):
        self.fit_bkg_and_spots()
        with np.errstate(divide="ignore", invalid="ignore"):
            sR, sC, stamps = self.get_stamps(
                ((self.image - self.bkg) / self.spot_normalization)
                / self.pixel_mask
            )
        rt, ct = self.spot_pixel_locations
        lR, lC = (
            (np.ones(sR.shape) * rt - self.cutout_center[0])
            / self.cutout_size[0],
            (np.ones(sC.shape) * ct - self.cutout_center[1])
            / self.cutout_size[1],
        )
        k = (
            (stamps > 0)
            & np.isfinite(lC)
            & np.isfinite(lR)
            & np.isfinite(sC)
            & np.isfinite(sR)
            & np.isfinite(stamps)
        )
        self.sip.fit(
            x=lC[k],
            y=lR[k],
            dx=sC[k],
            dy=sR[k],
            data=np.log(stamps[k]),
            errors=stamps[k] ** 0.5 / stamps[k],
        )
        if plot:
            fig = self.plot_registration(sR, sC, stamps)
            return fig

    def plot_registration(self, sR, sC, stamps):
        fig, ax = plt.subplots(2, 2, figsize=(8, 10))

        if not np.all(self.sip.posteriors.mean == 0):
            R, C = np.mgrid[
                self.cutout_corner[0] : self.cutout_corner[0]
                + self.cutout_size[0],
                self.cutout_corner[1] : self.cutout_corner[1]
                + self.cutout_size[1],
            ].astype(float)
            R -= self.cutout_center[0]
            C -= self.cutout_center[1]
            R /= self.cutout_size[0]
            C /= self.cutout_size[1]
            imshow = ax[0, 0].pcolormesh(
                C,
                R,
                self.sip.mu_x_to_Model().evaluate(
                    x=C.astype(float), y=R.astype(float)
                ),
                vmin=-1,
                vmax=1,
                rasterized=True,
            )
            imshow = ax[0, 1].pcolormesh(
                C,
                R,
                self.sip.mu_y_to_Model().evaluate(
                    x=C.astype(float), y=R.astype(float)
                ),
                vmin=-1,
                vmax=1,
                rasterized=True,
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
            cbar = plt.colorbar(imshow, ax=ax[0, 0], orientation="horizontal")
            cbar.set_label("$\delta$ Pixel")
            cbar = plt.colorbar(imshow, ax=ax[0, 1], orientation="horizontal")
            cbar.set_label("$\delta$ Pixel")

        dy, dx = self.spot_pixel_location_distortion
        k = (
            (stamps > 0)
            & np.isfinite(sC)
            & np.isfinite(sR)
            & np.isfinite(stamps)
        )
        imshow = bin2d(
            (sR)[k],
            (sC)[k],
            stamps[k],
            bin_width=0.05,
            vmin=0,
            vmax=0.2,
            ax=ax[1, 0],
        )
        ax[1, 0].set(
            xlabel="$\delta$ Column",
            ylabel="$\delta$ Row",
            aspect="equal",
            title="Affine Transform Only",
            xlim=(-2, 2),
            ylim=(-2, 2),
        )
        cbar = plt.colorbar(imshow, ax=ax[1, 0], orientation="horizontal")
        cbar.set_label("Image Brightness")
        if not np.all(dx == 0):
            imshow = bin2d(
                (sR - dy)[k],
                (sC - dx)[k],
                stamps[k],
                bin_width=0.05,
                vmin=0,
                vmax=0.2,
                ax=ax[1, 1],
            )
            ax[1, 1].set(
                xlabel="$\delta$ Column",
                aspect="equal",
                title="Affine Transform and Distortion",
                xlim=(-2, 2),
                ylim=(-2, 2),
            )
            cbar = plt.colorbar(imshow, ax=ax[1, 1], orientation="horizontal")
            cbar.set_label("Image Brightness")
            plt.subplots_adjust(wspace=0.1)
        return fig

    # def fit_centroid(self):
    #     sR, sC, stamps = self.get_stamps(
    #         ((self.image - self.bkg) / self.spot_normalization) / self.pixel_mask
    #     )
    #     dy, dx = self.spot_pixel_location_distortion
    #     sR -= dy[None, None, :]
    #     sC -= dx[None, None, :]

    #     k = (stamps > np.nanpercentile(stamps, 50)) & np.isfinite(stamps)
    #     self.rcent = np.average(sR[k], weights=stamps[k])
    #     self.ccent = np.average(sC[k], weights=stamps[k])
    #     return

    def plot_frame(self, ax=None, **kwargs):
        rt, ct = self.spot_pixel_locations
        if ax is None:
            _, ax = plt.subplots()
        im = ax.pcolormesh(
            self.C, self.R, self.image / self.pixel_mask, **kwargs
        )
        ax.scatter(*self.cutout_corner[::-1], s=100, marker="*", c="r")
        ax.scatter(*self.cutout_center[::-1], s=100, marker="*", c="r")
        ax.plot(*self.cutout_points[:, :2][:, ::-1].T, c="r")
        rt, ct = self.spot_pixel_locations
        ax.scatter(ct, rt, c="magenta", s=2)
        ax.set(
            xlim=(self.C.min() - 10, self.C.max() + 10),
            ylim=(self.R.min() - 10, self.R.max() + 10),
            aspect="equal",
            xlabel="Pixel Column",
            ylabel="Pixel Row",
        )
        plt.colorbar(im, ax=ax, label="Image Flux [e$^-$")
        return

    def _update_affine_matrix(self):
        r, c = self.spot_talbot_locations
        rt, ct = self.spot_pixel_locations
        dy, dx = self.spot_pixel_location_distortion
        rt -= self.cutout_center[0] - dy
        ct -= self.cutout_center[1] - dx
        self.A = fit_affine_3x3(np.asarray([r, c]).T, np.asarray([rt, ct]).T).T

    def plot_spot_model(self, ax=None):
        sR, sC, stamps = self.get_stamps(
            ((self.image - self.bkg) / self.spot_normalization)
            / self.pixel_mask
        )

        _, _, model_stamps = self.get_stamps(
            self.spots / self.spot_normalization
        )
        dy, dx = self.spot_pixel_location_distortion
        sR -= dy[None, None, :]
        sC -= dx[None, None, :]
        if ax is None:
            _, ax = plt.subplots()
        hist2d(
            np.hypot(sR, sC).ravel(),
            np.log10(stamps.ravel()),
            bins=100,
            range=(np.asarray([-1, 6]), np.asarray([-4.0, 0.0])),
            ax=ax,
        )
        ax.scatter(
            np.hypot(sR, sC).ravel(),
            np.log10(model_stamps.ravel()),
            s=0.01,
            c="r",
            label="PSF model",
        )
        ax.set(
            ylim=(-3, 0),
            xlabel="Radial Distance from Spot Center",
            ylabel="log$_{10}$ Normalized Spot Flux",
            title="Spot Profile Fit",
        )
        return

    @property
    def prf_hdulist(self):
        hdu0 = primaryHDU()
        if not hasattr(self, "weights"):
            raise ValueError("Must fit by running `fit_bkg_and_spots`")
        R, C = np.mgrid[-10:10:100j, -10:10:999j]
        rad = (R**2 + C**2) ** 0.5
        knots = np.arange(-0.5, 6, 0.25)
        X = Spline("rad", knots=knots)
        A = X.design_matrix(rad=rad) / 0.25
        normalization = 2 * np.pi * np.abs(knots[1:-2] + 0.125)
        A /= normalization[None, :]
        norm = np.trapz(np.trapz(A.dot(self.weights), R[:, 0], axis=0), C[0])
        # hdu = fits.ImageHDU(A.dot(self.weights), name="PRF")
        # hdu.header['norm'] = norm
        hdu2 = fits.TableHDU.from_columns(
            [fits.Column(name="weights", array=self.weights, format="D")]
        )
        hdu2.header["EXTNAME"] = "WEIGHTS"
        hdu2.header["norm"] = (norm, "PSF normalization")
        hdu2.header["bkg"] = (self.bkg.mean(), "Average background in frame")
        hdu2.header["corner0"] = self.cutout_corner[0]
        hdu2.header["corner1"] = self.cutout_corner[1]
        hdu2.header["size0"] = self.cutout_size[0]
        hdu2.header["size1"] = self.cutout_size[1]
        hdu2.header["rcent"] = self.A.T[0, 2]
        hdu2.header["ccent"] = self.A.T[1, 2]

        hdu2.header["hardsat"] = (self.image >= (2**16 - 1)).sum()
        hdu2.header["softsat"] = (self.image >= 0.9 * (2**16 - 1)).sum()
        return fits.HDUList([hdu0, hdu2])
