"""Detect the principal subsphere by optimization."""

import warnings

import numpy as np
from scipy.optimize import least_squares

from .base import exp_map, log_map, rotation_matrix

__all__ = [
    "pss",
]


def pss(x, tol=1e-3, maxiter=None, lm_kwargs=None):
    r"""Find the principal subsphere (PSS) from data on a hypersphere.

    Parameters
    ----------
    x : (N, d+1) real array
        Extrinsic coordinates of data on a ``d``-dimensional hypersphere,
        embedded in a ``d+1``-dimensional space.
    tol : float, default=1e-3
        Convergence tolerance in radian.
    maxiter : int, optional
        Maximum number of iterations for the optimization.
        If None, the number of iterations is not checked.
    lm_kwargs : dict, optional
        Additional keyword arguments to be passed for Levenberg-Marquardt optimization.
        Follows the signature of :func:`scipy.optimize.least_squares`.

    Returns
    -------
    v : (d+1,) real array
        Estimated principal axis of the subsphere in extrinsic coordinates.
    r : scalar in [0, pi]
        Geodesic distance from the pole by *v* to the estimated principal subsphere.

    Notes
    -----
    This function determines the best fitting subsphere
    :math:`\hat{A}_{d-k} = A_{d-k}(\hat{v}_k, \hat{r}_k) \subset S^{d-k+1}` for
    :math:`k = 1, 2, \ldots, d`.

    The Fréchet mean :math:`\hat{A}_0` of the lowest level best fitting subsphere
    :math:`\hat{A}_1` is also determined by this function.

    Examples
    --------
    >>> from pns.pss import pss
    >>> from pns.util import unit_sphere, circular_data, circle_3d
    >>> x = circular_data()
    >>> v, r = pss(x.reshape(-1, x.shape[-1]))
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... ax = plt.figure().add_subplot(projection='3d', computed_zorder=False)
    ... ax.plot_surface(*unit_sphere(), color='skyblue', alpha=0.6, edgecolor='gray')
    ... ax.scatter(*x.T, marker="x")
    ... ax.plot(*circle_3d(v, r), color="tab:orange", zorder=10)
    """
    if lm_kwargs is None:
        lm_kwargs = {}
    else:
        lm_kwargs = lm_kwargs.copy()
        lm_kwargs.pop("method", None)
        lm_kwargs.pop("args", None)

    _, D = x.shape
    if D <= 1:
        raise ValueError("Data must be on at least 1-sphere.")
    elif D == 2:
        r = np.int_(0)
        v = np.mean(x, axis=0)
        norm = np.linalg.norm(v)
        if norm != 0:
            v /= norm
        else:
            v = np.array([1, 0])
    else:
        pole = np.array([0] * (D - 1) + [1])
        R = np.eye(D)
        _x = x
        v, r = _pss(_x, lm_kwargs=lm_kwargs)

        iter_count = 0
        while np.arccos(np.dot(pole, v)) > tol:
            if iter_count == maxiter:
                warnings.warn(
                    f"Maximum number of iterations ({maxiter}) reached. "
                    "Optimization may not have converged.",
                    UserWarning,
                    stacklevel=2,
                )
                break

            # Rotate so that v becomes the pole
            _x, _R = rotation_matrix(_x, v)
            v, r = _pss(_x, lm_kwargs=lm_kwargs)
            R = R @ _R.T
            iter_count += 1

        v = R @ v  # re-rotate back
    return v.astype(x.dtype), r.astype(x.dtype)


def _pss(pts, lm_kwargs):
    # Projection
    x_dag = log_map(pts)
    v_dag_init = np.mean(x_dag, axis=0)
    r_init = np.mean(np.linalg.norm(x_dag - v_dag_init, axis=1))
    init = np.concatenate([v_dag_init, [r_init]])
    # Optimization
    opt = least_squares(_res, init, _jac, method="lm", args=(x_dag,), **lm_kwargs).x
    v_dag_opt, r_opt = opt[:-1], opt[-1]
    v_opt = exp_map(v_dag_opt.reshape(1, -1)).reshape(-1)
    r_opt = np.mod(r_opt, np.pi)
    return v_opt, r_opt


def _res(params, x_dag):
    v_dag, r = params[:-1].reshape(1, -1), params[-1]
    diff = x_dag - v_dag
    dist = np.linalg.norm(diff, axis=1)
    return dist - r


def _jac(params, x_dag):
    n = len(x_dag)
    m = len(params)
    v_dag = params[:-1].reshape(1, -1)
    diff = x_dag - v_dag
    dist = np.linalg.norm(diff, axis=1)
    mask = dist > 1e-12
    out = np.empty((n, m), dtype=float)
    out[mask, :-1] = -diff[mask] / dist[mask][:, None]
    out[~mask, :-1] = 0.0
    out[:, -1] = -1.0
    return out
