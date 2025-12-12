from abc import ABC, abstractmethod
import numpy as np
from scipy.special import erf, erfinv
from .ft_types import ArrayLike


class link_function(ABC):
    """ Link function base type (purely virtual) """

    @staticmethod
    @abstractmethod
    def L(x: ArrayLike) -> ArrayLike:
        """ Link function """
        return np.empty(0)

    @staticmethod
    @abstractmethod
    def DL(x: ArrayLike) -> ArrayLike:
        """ Link function derivative """
        return np.empty(0)

    @staticmethod
    @abstractmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        """ Link function inverse """
        return np.empty(0)

    @staticmethod
    @abstractmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        """ Derivative of link function inverse """
        return np.empty(0)

    # https://docs.python.org/3/library/abc.html
    @classmethod
    def __subclasshook__(cls, C):
        if cls is link_function:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class mistag(link_function):
    """ Identity link """
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta)=\eta` """
        return np.array(x)  # Creating copy is deliberate

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=1` """
        return np.ones(len(x))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\eta` """
        return np.array(x)

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=1` """
        return np.ones(len(x))


class logit(link_function):
    r""" logit link """
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta)=(1 + e^\eta)^{-1}` """
        return 1.0 / (1.0 + np.exp(x))

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{1}{2}(1 + \cosh(\eta))^{-1}` """
        return -0.5  / (1.0 + np.cosh(x))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\log\left(\frac{1-\eta}{\eta}\right)` """
        return np.log((1 - x) / x)

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=\frac{1}{\eta(\eta-1)}` """
        return (x * (x - 1))**-1


class rlogit(link_function):
    r""" rlogit link """
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta)=\frac{1}{2}(1 + e^\eta)^{-1}` """
        return 0.5 / (1.0 + np.exp(x))

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{1}{4}(1 + \cosh(\eta))^{-1}` """
        return -0.25 / (1.0 + np.cosh(x))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\log\left(\frac{1-2\eta}{2\eta}\right)` """
        return np.log((1 - 2 * x) / (2 * x))

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=\frac{1}{\eta(2\eta-1)}` """
        return (x * (2 * x - 1))**-1


class probit(link_function):
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta) =\frac{1}{2}\left(1-\mathrm{erf}\left(\frac{\eta}{\sqrt{2}}\right)\right)` """
        return 0.5 * (1.0 - erf(x / np.sqrt(2)))

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{e^{-\frac{1}{2}\eta^2}}{\sqrt{2\pi}}` """
        return -np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\sqrt{2}\mathrm{inferf}(1-2\eta)` """
        return np.sqrt(2) * erfinv(1 - 2 * x)

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=-\sqrt{2\pi}\exp(\mathrm{inverf}(1-2\eta)^2)` """
        return -np.sqrt(2 * np.pi) * np.exp(erfinv(1 - 2 * x)**2)


class rprobit(link_function):
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta) =\frac{1}{4}\left(1-\mathrm{erf}\left(\frac{\eta}{\sqrt{2}}\right)\right)` """
        return 0.25 * (1.0 - erf(x / np.sqrt(2)))

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{e^{-\frac{1}{2}\eta^2}}{2\sqrt{2\pi}}` """
        return -np.exp(-0.5 * x**2) / (2 * np.sqrt(2 * np.pi))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\sqrt{2}\mathrm{inverf}(1-4\eta)` """
        return np.sqrt(2) * erfinv(1 - 4 * x)

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=-2\sqrt{2\pi}\exp(\mathrm{inverf}(1-4\eta)^2)` """
        return -2 * np.sqrt(2 * np.pi) * np.exp(erfinv(1 - 4 * x)**2)


class cauchit(link_function):
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta) = \frac{1}{2} - \frac{1}{\pi}\arctan(\eta)` """
        return 0.5 - np.arctan(x) / np.pi

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{1}{\pi(1+\eta^2)}` """
        return -1.0 / (np.pi * (1 + x**2))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\begin{cases}\infty&\eta<0\\-\infty&\eta>1\\-\tan\left(\frac{1}{2}\pi(2\eta-1)\right)&\text{else}\end{cases}` """
        il = -np.tan(0.5 * np.pi * (2 * x - 1))
        il[x < 0] = np.inf
        il[x > 1] = -np.inf
        return il

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=-\pi\csc^2(\pi \eta)` """
        return -np.pi * np.sin(np.pi * x)**(-2)


class rcauchit(link_function):
    @staticmethod
    def L(x: ArrayLike) -> ArrayLike:
        r""" :math:`g(\eta) = \frac{1}{4} - \frac{1}{2\pi}\arctan(\eta)` """
        return 0.25 - np.arctan(x) / (2 * np.pi)

    @staticmethod
    def DL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g(\eta)}{\mathrm{d}\eta}=-\frac{1}{2\pi(1+\eta^2)}` """
        return -0.5 / (np.pi * (1 + x**2))

    @staticmethod
    def InvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`g^{-1}(\eta)=\begin{cases}\infty & \eta<0 \\ -\infty & \eta > 0.5 \\ -\tan\left(\frac{1}{2}\pi(4\eta-1)\right) &\text{else}\end{cases}` """
        il = -np.tan(0.5 * np.pi * (4 * x - 1))
        il[x < 0] = np.inf
        il[x > 0.5] = -np.inf
        return il

    @staticmethod
    def DInvL(x: ArrayLike) -> ArrayLike:
        r""" :math:`\frac{\mathrm{d}g^{-1}(\eta)}{\mathrm{d}\eta}=-2\pi\csc^2(2\pi \eta)` """
        return -2 * np.pi * np.sin(2 * np.pi * x)**(-2)
