import numpy as np
from abc import ABC, abstractmethod

from .ft_types import ArrayLike, AnyList
from .link_functions import link_function
from . import link_functions
from typing import Optional


class CalibrationFunction(ABC):
    r"""
    Calibration function abstract base type. All calibration classes should inherit from this type.
    Calibration functions receive calibration parameters in the following order

    params :math:`= (p^+_0,\cdots, p^+_n, p^-_0,\cdots,p^-_n)`
    """

    def __init__(self, npar: int, link: type[link_function]=link_functions.mistag):
        self.npar: int = npar
        self.link: type[link_function] = link
        self.basis = None  # Function specific basis representation

    def __eq__(self, other):
        if self.basis is None or other.basis is None:
            raise RuntimeError("Cannot compare uninitialized calibration functions")

        equal = True
        equal &= self.npar == other.npar
        equal &= self.link == other.link
        equal &= len(self.basis) == len(other.basis)

        if equal:
            for b in range(len(self.basis)):
                equal &= np.array_equal(self.basis[b], other.basis[b])
        return equal

    @abstractmethod
    def print_basis(self) -> None:
        """ Pretty printer for the calibration basis """
        print("no basis")

    @abstractmethod
    def init_basis(self, eta: ArrayLike, weight: Optional[ArrayLike] = None) -> None:
        """ Initializer for the calibration function basis.
            Must be called before a calibration function is evaluated

            :param eta: Mistags
            :type eta: numpy.ndarray
            :param weight: Event weights
            :type weight: numpy.ndarray
        """
        pass

    @abstractmethod
    def eval(self, params: AnyList, eta: ArrayLike, dec: ArrayLike) -> ArrayLike:
        """ Evaluate the calibration function

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        print("no basis")

    @abstractmethod
    def eval_averaged(self, params: AnyList, eta: ArrayLike) -> ArrayLike:
        r""" Evaluate the calibration function and ignore differences of
            flavour specific calibrations

            :param params: Mean calibration function parameters :math:`[p_0,\cdots,p_n]`
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    def eval_uncertainty(self, params: AnyList, cov: ArrayLike, eta: ArrayLike, dec: ArrayLike) -> ArrayLike:
        """ Evaluate uncertainty of calibrated mistag

            :param params: Calibration function parameters
            :type params: list
            :param cov: Covariance matrix of the calibration function parameters
            :type: np.ndarray
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        gradient = self.gradient(params, eta, dec).T
        return np.sqrt([g @ cov @ g.T for g in gradient])

    def eval_averaged_uncertainty(self, params: AnyList, cov: ArrayLike, eta: ArrayLike) -> ArrayLike:
        r""" Evaluate uncertainty of calibrated mistag and ignore Delta paramaters

            :param params: Mean calibration function parameters :math:`[p_0,\cdots,p_n]`
            :type params: list
            :param cov: Covariance matrix of the calibration function parameters
            :type: np.ndarray
            :param eta: Mistags
            :type eta: numpy.ndarray
            :return: Uncertainties ofalibrated mistags
            :return type: numpy.ndarray
        """
        gradient = self.gradient_averaged(params, eta).T
        return np.sqrt([g @ cov @ g.T for g in gradient])

    @abstractmethod
    def eval_plotting(self, params: AnyList, eta: ArrayLike, dec: ArrayLike) -> ArrayLike:
        """ Compute the combined lineshape of the flavour specific calibration components (for plotting).

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def derivative(self, partial, params: AnyList, eta: ArrayLike, dec: ArrayLike) -> ArrayLike:
        """ Evaluate the partial derivative w.r.t. one of the calibration parameters.

            :param partial: :math:`n`-th calibration parameter
            :type partial: int
            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibration function partial derivative
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def derivative_averaged(self, partial: int, params: AnyList, eta: ArrayLike) -> ArrayLike:
        """ Evaluate the partial derivative w.r.t. one of the average calibration parameters.

            :param partial: :math:`n`-th calibration parameter
            :type partial: int
            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibration function partial derivative
            :return type: numpy.ndarray
        """
        pass

    def gradient(self, params: AnyList, eta: ArrayLike, dec: ArrayLike) -> ArrayLike:
        """ Evaluate the calibration function gradient w.r.t. to the set of calibration parameters

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: List of all calibration function partial derivatives
            :return type: numpy.ndarray
        """
        return np.array([self.derivative(i, params, eta, dec) for i in range(self.npar * 2)])

    def gradient_averaged(self, params: AnyList, eta: ArrayLike) -> ArrayLike:
        """ Evaluate the calibration function gradient w.r.t. to the set of averaged calibration parameters

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: List of all calibration function partial derivatives
            :return type: numpy.ndarray
        """
        return np.array([self.derivative_averaged(i, params, eta) for i in range(self.npar)])

    def __str__(self) -> str:
        return f"<CalibrationFunction, type={self.__class__.__name__}, link={self.link.__name__}, npar={self.npar}>"

    def __repr__(self) -> str:
        return self.__str__()
