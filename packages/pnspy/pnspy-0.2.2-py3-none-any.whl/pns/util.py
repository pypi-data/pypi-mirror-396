"""Utility functions to generate and plot sample data."""

import numpy as np

from .base import rotation_matrix

__all__ = [
    "unit_sphere",
    "circular_data",
    "circle_3d",
]


def unit_sphere():
    """Helper function to plot a unit sphere.

    Returns
    -------
    x, y, z : array
        Coordinates for unit sphere.

    Examples
    --------
    >>> from pns.util import unit_sphere
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... ax = plt.figure().add_subplot(projection='3d')
    ... ax.plot_surface(*unit_sphere(), color='skyblue', alpha=0.6, edgecolor='gray')
    """
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def circular_data(v=(0, 0, 1)):
    """Circular data on a 3D unit sphere.

    Parameters
    ----------
    v : array of shape (3,), default=(0, 0, 1)
        Unit vector to center of circle.

    Returns
    -------
    ndarray of shape (100, 3)
        Data coordinates.

    Examples
    --------
    >>> from pns.util import unit_sphere, circular_data
    >>> v = [0, -1, 0]
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... ax = plt.figure().add_subplot(projection='3d', computed_zorder=False)
    ... ax.plot_surface(*unit_sphere(), color='skyblue', alpha=0.6, edgecolor='gray')
    ... ax.scatter(*circular_data(v).T)
    """
    t = np.linspace(0.1 * np.pi, 0.2 * np.pi, 10)
    p = np.linspace(-np.pi, np.pi / 2, 10)
    T, P = np.meshgrid(t, p)
    x = np.array([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), np.cos(T)]).T
    return x @ rotation_matrix(v)


def circle_3d(v, theta, n=100):
    """Helper function to plot a circle in 3D.

    Parameters
    ----------
    v : (3,) array
        Unit vector to center of circle in 3D.
    theta : scalar
        Geodesic distance.
    n : int, default=100
        Number of points.

    Examples
    --------
    >>> from pns.util import unit_sphere, circle_3d
    >>> circle = circle_3d([0, -1, 0], 0.5)
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... ax = plt.figure().add_subplot(projection='3d')
    ... ax.plot_surface(*unit_sphere(), color='skyblue', alpha=0.6, edgecolor='gray')
    ... ax.plot(*circle, color="tab:orange", zorder=10)
    """
    phi = np.linspace(0, 2 * np.pi, n)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.full_like(phi, np.cos(theta))
    circle = np.stack([x, y, z], axis=1)

    north_pole = np.array([0.0, 0.0, 1.0])
    u = v - north_pole
    u /= np.linalg.norm(u)
    H = np.eye(3) - 2 * np.outer(u, u)
    return H @ circle.T
