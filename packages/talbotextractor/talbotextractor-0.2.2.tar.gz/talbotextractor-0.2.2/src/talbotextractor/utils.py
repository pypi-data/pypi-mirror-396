"""Utility functions"""

# Third-party
import fitsio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.time import Time
from numpy.fft import fft2, fftshift

from . import __version__


def get_pixel_mask(fname):
    """Creates a boolean pixel mask for a given exposure.
    The pixel mask is True where pixels are "good" and False where pixels are "bad".
    """
    frame = fitsio.FITS(fname)[1][0, 0, :, :4096][0, 0].astype(float)
    grad = np.hypot(*np.gradient(frame))
    good_pix_grad = np.ones(frame.shape, bool)
    good_pix_grad = grad < np.percentile(grad, 99.99)
    for sigma in [10, 6, 5]:
        med = np.nanmedian(grad[good_pix_grad])
        std = np.std(grad[good_pix_grad] - med)
        good_pix_grad[(grad - med) / std > sigma] = False
    mask = np.ones_like(good_pix_grad)
    for axis in [0, 1]:
        for r in np.arange(-1, 2):
            if r == 0:
                continue
            mask &= np.roll(good_pix_grad, r, axis=axis)
    good_pix_grad &= mask
    del mask

    good_pix = np.ones(frame.shape, bool)
    for sigma in [10, 6, 5]:
        med = np.nanmedian(frame[good_pix & good_pix_grad])
        std = np.std(frame[good_pix & good_pix_grad] - med)
        good_pix[(frame - med) / std > sigma] = False

    mask = np.ones_like(good_pix)
    for axis in [0, 1]:
        for r in np.arange(-1, 2):
            if r == 0:
                continue
            mask &= np.roll(good_pix, r, axis=axis)
    good_pix &= mask
    del mask
    return good_pix & good_pix_grad


def fit_affine_3x3(src, dst):
    """
    Fit a 3x3 affine transform matrix A such that:
    [x', y', 1] ≈ A @ [x, y, 1]

    Parameters
    ----------
    src : ndarray of shape (N, 2)
        Source points
    dst : ndarray of shape (N, 2)
        Destination points

    Returns
    -------
    A : ndarray of shape (3, 3)
        Full affine transform matrix
    """
    N = src.shape[0]
    # Convert to homogeneous coordinates
    src_h = np.hstack([src, np.ones((N, 1))])  # shape (N, 3)
    dst_h = np.hstack([dst, np.ones((N, 1))])  # shape (N, 3)

    # Solve for A: minimize ||src_h @ A.T - dst_h||^2
    A, _, _, _ = np.linalg.lstsq(src_h, dst_h, rcond=None)  # shape (3, 3)

    return A.T


def bin2d(row, col, value, bin_width=1, ax=None, **kwargs):
    df = pd.DataFrame({"row": row, "col": col, "value": value})

    # Assign bin indices
    df["row_bin"] = df["row"] // bin_width
    df["col_bin"] = df["col"] // bin_width

    # Aggregate over bins
    binned = df.groupby(["row_bin", "col_bin"])["value"].mean().unstack()

    if ax is None:
        _, ax = plt.subplots()
    im = ax.pcolormesh(
        binned.columns.values * bin_width,
        binned.index.values * bin_width,
        binned.values,
        rasterized=True,
        **kwargs,
    )
    return im


def image_to_RS_matrix(
    im, fourier_resolution=6, minimum_period=6, maximum_period=10, plot=False
):
    padded = np.zeros(
        (fourier_resolution * im.shape[0], fourier_resolution * im.shape[1])
    )
    padded[: im.shape[0], : im.shape[1]] = im
    F = fftshift(fft2(padded))
    power_spectrum = np.abs(F)
    del padded
    fR, fC = (
        np.fft.fftshift(np.fft.fftfreq(power_spectrum.shape[0], d=1)),
        np.fft.fftshift(np.fft.fftfreq(power_spectrum.shape[1], d=1)),
    )

    # trim down to the shape that represents the minimum period
    shape = power_spectrum.shape
    edge = (np.asarray(power_spectrum.shape) * 1 / minimum_period).astype(int)
    power_spectrum = power_spectrum[
        -edge[0] + shape[0] // 2 : edge[0] + shape[0] // 2,
        -edge[1] + shape[1] // 2 : edge[1] + shape[1] // 2,
    ]
    fR = fR[-edge[0] + shape[0] // 2 : edge[0] + shape[0] // 2]
    fC = fC[-edge[1] + shape[1] // 2 : edge[1] + shape[1] // 2]
    shape = power_spectrum.shape
    # we will only use the region that is within the minimum and maximum period
    edge = (np.asarray(power_spectrum.shape) * 1 / maximum_period).astype(int)

    peaks = []

    f_row, f_col = np.unravel_index(
        np.argmax(
            power_spectrum[
                shape[0] // 2 - edge[0] : shape[0] // 2 + edge[0],
                0 : shape[1] // 2 - edge[1],
            ]
        ),
        (edge[0] * 2, shape[1] // 2 - edge[1]),
    )
    f_row += shape[0] // 2 - edge[0]
    f_col += 0
    peaks.append([fR[f_row], fC[f_col]])

    f_row, f_col = np.unravel_index(
        np.argmax(
            power_spectrum[
                shape[0] // 2 + edge[0] :,
                shape[1] // 2 - edge[1] : shape[1] // 2 + edge[1],
            ]
        ),
        (shape[0] // 2 - edge[0], edge[1] * 2),
    )
    f_row += shape[0] // 2 + edge[0]
    f_col += shape[1] // 2 - edge[1]
    peaks.append([fR[f_row], fC[f_col]])

    f_row, f_col = np.unravel_index(
        np.argmax(
            power_spectrum[
                shape[0] // 2 - edge[0] : shape[0] // 2 + edge[0],
                shape[1] // 2 + edge[1] :,
            ]
        ),
        (edge[0] * 2, shape[1] // 2 - edge[1]),
    )
    f_row += shape[0] // 2 - edge[0]
    f_col += shape[1] // 2 + edge[1]
    peaks.append([fR[f_row], fC[f_col]])

    f_row, f_col = np.unravel_index(
        np.argmax(
            power_spectrum[
                0 : shape[0] // 2 - edge[0],
                shape[1] // 2 - edge[1] : shape[1] // 2 + edge[1],
            ]
        ),
        (shape[0] // 2 - edge[0], edge[1] * 2),
    )
    f_row += 0
    f_col += shape[1] // 2 - edge[1]
    peaks.append([fR[f_row], fC[f_col]])

    peaks = np.asarray(peaks)

    spacing = 1 / np.linalg.norm(peaks, axis=1)
    spacing_c = np.mean([spacing[0], spacing[2]])
    spacing_r = np.mean([spacing[1], spacing[3]])

    angle = np.arctan2(peaks[:, 0], peaks[:, 1])
    # theta = np.deg2rad(np.mean([np.rad2deg(np.mean([angle[0], angle[2]])) % 90, np.rad2deg(np.mean([angle[1], angle[3]])) % 90]))
    theta = np.deg2rad((np.mean(np.rad2deg(angle) % 90)) - 90)

    Rot = np.eye(3)
    Rot[:2, :2] = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )

    # Scale matrix
    Scale = np.eye(3)
    Scale[:2, :2] = np.diag([spacing_r, spacing_c])

    if plot:
        fig, ax = plt.subplots()
        ax.pcolormesh(
            fC,
            fR,
            power_spectrum,
            vmin=0,
            vmax=np.percentile(power_spectrum, 99),
            cmap="Greys",
            shading="nearest",
            rasterized=True,
        )
        ax.set(xlabel="Frequency", ylabel="Frequency", aspect="equal")
        [
            ax.scatter(
                *p[::-1], s=100, edgecolor=f"C{idx}", facecolor="None", lw=3
            )
            for idx, p in enumerate(peaks)
        ]
        return Rot, Scale, fig
    return Rot, Scale


# def image_to_offsets(im, A, nterms=5, plot=False, mask=None):
#     if mask is None:
#         mask = np.ones(im.shape, bool)
#     Ainv = np.linalg.inv(A)
#     R, C = np.mgrid[: im.shape[0], : im.shape[1]]
#     R -= im.shape[0] // 2
#     C -= im.shape[1] // 2
#     r, c, _ = (np.asarray([R.ravel(), C.ravel(), R.ravel() ** 0]).T @ Ainv).T
#     r = r.reshape(R.shape)
#     c = c.reshape(C.shape)
#     k = mask.copy()
#     k &= (im > np.percentile(im[mask], 50)) & (im < np.percentile(im[mask], 99.9))

#     phi_c = (c[k] % 1) * 2 * np.pi
#     phi_r = (r[k] % 1) * 2 * np.pi
#     Xc = np.vstack(
#         [
#             np.ones((1, phi_c.shape[0])),
#             *[
#                 [np.cos(phi_c * idx), np.sin(phi_c * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     Xr = np.vstack(
#         [
#             np.ones((1, phi_r.shape[0])),
#             *[
#                 [np.cos(phi_r * idx), np.sin(phi_r * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     X = np.hstack([Xc * xr[:, None] for xr in Xr.T])
#     w = np.linalg.solve(X.T.dot(X), X.T.dot(im[k]))

#     r_m, c_m = np.mgrid[0:1:200j, 0:1:200j]
#     phi_c_m = (c_m.ravel() % 1) * 2 * np.pi
#     phi_r_m = (r_m.ravel() % 1) * 2 * np.pi
#     Xc = np.vstack(
#         [
#             np.ones((1, phi_c_m.shape[0])),
#             *[
#                 [np.cos(phi_c_m * idx), np.sin(phi_c_m * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     Xr = np.vstack(
#         [
#             np.ones((1, phi_r_m.shape[0])),
#             *[
#                 [np.cos(phi_r_m * idx), np.sin(phi_r_m * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     X = np.hstack([Xc * xr[:, None] for xr in Xr.T])
#     r_offset, c_offset = (
#         phi_r_m[np.argmax(X.dot(w))] / (2 * np.pi),
#         phi_c_m[np.argmax(X.dot(w))] / (2 * np.pi),
#     )
#     if plot:
#         fig, ax = plt.subplots(figsize=(5, 5))
#         ax.scatter(
#             phi_c_m / (2 * np.pi),
#             phi_r_m / (2 * np.pi),
#             c=X.dot(w),
#             vmin=np.nanpercentile(X.dot(w), 90),
#             vmax=np.nanpercentile(X.dot(w), 99.9),
#             s=1,
#         )
#         ax.scatter(c_offset, r_offset, c="r", marker="*", label="Best Fit Center")
#         ax.set(
#             xlabel="PSF Column Phase",
#             ylabel="PSF Row Phase",
#             title="Aligned PSFs",
#         )
#         ax.legend()
#     r_offset, c_offset = (np.asarray([r_offset, c_offset, 1]) @ A)[:2]
#     O = np.eye(3)  # noqa: E741
#     O[:2, 2] = [r_offset, c_offset]
#     if plot:
#         return O, fig
#     return O


# def image_to_offsets(im, A, nterms=10, plot=False, mask=None):
#     if mask is None:
#         mask = np.ones(im.shape, bool)
#     Ainv = np.linalg.inv(A)
#     R, C = np.mgrid[: im.shape[0], : im.shape[1]]
#     R -= im.shape[0] // 2
#     C -= im.shape[1] // 2
#     r, c, _ = (np.asarray([R.ravel(), C.ravel(), R.ravel() ** 0]).T @ Ainv).T
#     r = r.reshape(R.shape)
#     c = c.reshape(C.shape)
#     k = mask.copy()
#     k &= (im > np.percentile(im[mask], 50)) & (im < np.percentile(im[mask], 99.9))

#     phi_c = (c[k] % 1) * 2 * np.pi
#     phi_r = (r[k] % 1) * 2 * np.pi
#     Xc = np.vstack(
#         [
#             np.ones((1, phi_c.shape[0])),
#             *[
#                 [np.cos(phi_c * idx), np.sin(phi_c * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     Xr = np.vstack(
#         [
#             np.ones((1, phi_r.shape[0])),
#             *[
#                 [np.cos(phi_r * idx), np.sin(phi_r * idx)]
#                 for idx in np.arange(1, nterms + 1)
#             ],
#         ]
#     ).T
#     X = np.hstack([Xc * xr[:, None] for xr in Xr.T])
#     w = np.linalg.solve(X.T.dot(X), X.T.dot(im[k]))

#     roffset0 = np.nanmedian(phi_r[im[k] > np.nanpercentile(im, 99)] / (2 * np.pi))
#     coffset0 = np.nanmedian(phi_c[im[k] > np.nanpercentile(im, 99)] / (2 * np.pi))

#     r_offset, c_offset = (
#         np.average((r[k] - roffset0 + 0.5) % 1, weights=im[k]) + roffset0 - 0.5,
#         np.average((c[k] - coffset0 + 0.5) % 1, weights=im[k]) + coffset0 - 0.5,
#     )
#     if plot:
#         fig, ax = plt.subplots(figsize=(5, 5))
#         ax.scatter(
#             (c[k] - coffset0 + 0.5) % 1,
#             (r[k] - roffset0 + 0.5) % 1,
#             c=im[k],
#             vmin=np.nanpercentile(im[k], 50),
#             vmax=np.nanpercentile(im[k], 99.9),
#             s=1,
#         )
#         ax.scatter(
#             c_offset - coffset0 + 0.5,
#             r_offset - roffset0 + 0.5,
#             c="r",
#             marker="*",
#             label="Best Fit Center",
#         )
#         ax.set(
#             xlabel="PSF Column Phase",
#             ylabel="PSF Row Phase",
#             title="Aligned PSFs",
#             xlim=(0, 1),
#             ylim=(0, 1),
#         )
#         ax.legend()
#     r_offset, c_offset = (np.asarray([r_offset, c_offset, 1]) @ A)[:2]
#     O = np.eye(3)  # noqa: E741
#     O[:2, 2] = [r_offset, c_offset]
#     if plot:
#         return O, fig
#     return O


def image_to_offsets(im, A, plot=False, mask=None):
    if mask is None:
        mask = np.ones(im.shape, bool)
    Ainv = np.linalg.inv(A)
    R, C = np.mgrid[: im.shape[0], : im.shape[1]]
    R -= im.shape[0] // 2
    C -= im.shape[1] // 2
    r, c, _ = (np.asarray([R.ravel(), C.ravel(), R.ravel() ** 0]).T @ Ainv).T
    r = r.reshape(R.shape)
    c = c.reshape(C.shape)
    if mask is None:
        mask = np.ones(im.shape, bool)
    k = mask.copy()

    k &= (im > np.percentile(im[mask], 50)) & (
        im < np.percentile(im[mask], 99.9)
    )
    roffset0 = np.nanmedian(r[k][im[k] > np.nanpercentile(im, 99)] % 1)
    coffset0 = np.nanmedian(c[k][im[k] > np.nanpercentile(im, 99)] % 1)
    phi_r, phi_c = (r - roffset0 + 0.5) % 1, (c - coffset0 + 0.5) % 1
    rcent, ccent = (
        np.average(phi_r[k], weights=im[k]),
        np.average(phi_c[k], weights=im[k]),
    )

    if plot:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter(phi_c.ravel(), phi_r.ravel(), c=im.ravel(), s=1, alpha=0.1)
        ax.scatter(
            ccent,
            rcent,
            c="r",
            s=10,
            marker="*",
            label="Best Fit Center",
        )

        ax.legend()

    roffset = rcent + roffset0 - 0.5
    coffset = ccent + coffset0 - 0.5
    roffset, coffset = (np.asarray([roffset, coffset, 1]) @ A)[:2]

    O = np.eye(3)  # noqa: E741
    O[:2, 2] = [roffset, coffset]
    if plot:
        return O, fig
    return O


def image_to_cutouts(image, row, col, subimage_size):
    nrows, ncols = image.shape
    cutout_corner = (-subimage_size // 2 + 1, -subimage_size // 2 + 1)
    nsources = len(row)
    row_int = np.floor(row).astype(int)
    col_int = np.floor(col).astype(int)

    cutout_size = (subimage_size, subimage_size)
    stamps = np.zeros((subimage_size, subimage_size, nsources)) * np.nan
    for (
        idx,
        r1,
        c1,
    ) in zip(range(nsources), row_int, col_int):
        a1, a2, b1, b2 = (
            r1 + cutout_corner[0],
            r1 + cutout_corner[0] + cutout_size[0],
            c1 + cutout_corner[1],
            c1 + cutout_corner[1] + cutout_size[1],
        )
        if a2 < 0:
            continue
        if b2 < 0:
            continue
        if a1 > nrows:
            continue
        if b1 > ncols:
            continue
        a1m, a2m, b1m, b2m = (
            np.max([0, a1]),
            np.min([nrows, a2]),
            np.max([0, b1]),
            np.min([ncols, b2]),
        )
        stamps[
            a1m - a1 : a2m + cutout_size[0] - a2,
            b1m - b1 : b2m + cutout_size[1] - b2,
            idx,
        ] = image[a1m:a2m, b1m:b2m]
    return stamps


def primaryHDU():
    hdu0 = fits.PrimaryHDU()
    hdu0.header["AUTHOR"] = "Christina Hedges"
    hdu0.header["PIPELINE"] = "TalbotExtractor"
    hdu0.header["VERSION"] = __version__
    hdu0.header["DATE"] = Time.now().isot
    return hdu0
