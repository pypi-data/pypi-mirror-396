from abc import abstractmethod
import numpy as np
import iminuit
import pandas as pd
from packaging import version
from copy import deepcopy
from typing import Optional, Union

from lhcb_ftcalib.resolution_model import ResolutionModel

from .printing import raise_error, warning, info, printbold
from .PolynomialCalibration import PolynomialCalibration
from .TaggingData import TaggingData
from . import constants
from .CalParameters import CalParameters
from .ft_types import AnyList, ArrayLike, CalibrationMode
from .CalibrationFunction import CalibrationFunction
from .link_functions import link_function, mistag
from .warnings import ftcalib_warning


class TaggerBase:
    r""" Purely virtual Tagger base class """

    def __init__(self,
                 name: str,
                 eta_data: ArrayLike,
                 dec_data: ArrayLike,
                 B_ID: ArrayLike,
                 mode: Union[CalibrationMode, str],
                 tau_ps: Optional[ArrayLike]    = None,
                 tauerr_ps: Optional[ArrayLike] = None,
                 weight: Optional[ArrayLike]    = None,
                 selection: Optional[ArrayLike] = None,
                 resolution_model        = None,
                 analytic_gradient: bool = False):
        # Consistency checks
        raise_error(len(eta_data) == len(dec_data) == len(B_ID), "Tagging data must have matching dimensions")

        if selection is None:
            selection = pd.Series(np.full(len(dec_data), True))

        # Variables needed for minimization
        self.name: str = name  #: Name of tagger
        self.mode: CalibrationMode = CalibrationMode(mode)  #: Calibration mode (one of "Bd", "Bu", "Bs")
        self.minimizer = None  #: iminuit minimizer
        self.func: CalibrationFunction = PolynomialCalibration(npar=2, link=mistag)  #: Calibration function
        self.stats     = TaggingData(eta_data  = eta_data,
                                     dec_data  = dec_data,
                                     ID        = B_ID,
                                     tau       = tau_ps,
                                     tauerr    = tauerr_ps,
                                     weights   = weight,
                                     selection = selection)  #: Tagger statistics
        self.func.init_basis(self.stats._tagdata.eta, weight=self.stats._tagdata.weight)
        self._analytic_gradient: bool = analytic_gradient
        self.resolution_model: Optional[ResolutionModel] = resolution_model  #: Decay time resolution model
        self._calibrated: bool = False
        self._weighted: bool = weight is not None

        if self.mode == CalibrationMode.Bd:
            self.DeltaM     = constants.DeltaM_d  #: B oscillation frequency :math:`\Delta m`
            self.DeltaGamma = constants.DeltaGamma_d  #: Decay width difference of B mass eigenstates :math:`\Delta\Gamma`
            self.Aprod      = 0  #: Production asymmetry (WIP)
        elif self.mode == CalibrationMode.Bs:
            self.DeltaM     = constants.DeltaM_s
            self.DeltaGamma = constants.DeltaGamma_s
            self.Aprod      = 0
        else:
            self.DeltaM     = None
            self.DeltaGamma = None
            self.Aprod      = 0

        if self.mode.oscillation:
            raise_error(tau_ps is not None, f"Decay time needed for mode {self.mode}")

            if self.resolution_model is not None:
                self.resolution_model.DM = self.DeltaM
                self.resolution_model.DG = self.DeltaGamma
                self.resolution_model.a  = 0

        # Flip production flavour is oscillation is likely
        self.stats._init_timeinfo(self.mode, self.DeltaM, self.DeltaGamma, self.resolution_model)
        self._has_b_id = True

        # Plan B settings if minimization does not converge
        self._has_plan_b = False
        self._link_alternative = None
        self._increase_func_order = False

    def destroy(self) -> None:
        """ Frees most of the allocated memory.
            Tagger is ill-defined afterwards.
        """
        del self.stats

    def is_calibrated(self) -> bool:
        """ Returns true if calibration was performed

            :return type: bool
        """
        return self._calibrated

    @abstractmethod
    def get_dataframe(self, calibrated: bool=True) -> pd.DataFrame:
        raise RuntimeError("This method needs to be provided in a derived class")

    def __eq__(self, other) -> bool:
        # Needed for cached_property
        # Tagger names have to be unique
        return f"{self.name}{self._calibrated}{self.stats.Nt}" == f"{other.name}{other._calibrated}{other.stats.Nt}"

    def __hash__(self):
        # Needed for cached_property
        return hash(f"{self.name}{self._calibrated}{self.stats.Nt}")

    def __str__(self) -> str:
        return f"Tagger({self.name})"

    def __repr__(self) -> str:
        return self.__str__()


class Tagger(TaggerBase):
    r""" LHCb Tagger object

    :param name: Custom name of the tagger
    :type name: str
    :param eta_data: Uncalibrated mistag data
    :type eta_data: list
    :param dec_data: Uncalibrated tagging decisions
    :type dec_data: list
    :param B_ID: B meson ids
    :type B_ID: list
    :param mode: Which mode to use for calibration (Bd, Bu, Bs, TRUEID)
    :type mode: CalibrationMode | str
    :param tau_ps: Decay time in picoseconds
    :type tau_ps: list
    :param tauerr_ps: Decay time uncertainty in picoseconds
    :type tauerr_ps: list
    :param weight: Per-Event weight
    :type weight: list
    :param selection: List of booleans, True = selected
    :type selection: list
    :param resolution_model: Decay time resolution model (default=Gaussian resolution)
    :type resolution_model: ResolutionModel
    :param analytic_gradient: Whether to use the analytical gradient implementation
    :type analytic_gradient: bool

    :raises ValueError: if input data lists are not of the same length
    :raises ValueError: if decay time data is not given and calibration mode is Bd or Bs
    """

    def __init__(self,
                 name: str,
                 eta_data: ArrayLike,
                 dec_data: ArrayLike,
                 B_ID: ArrayLike,
                 mode: Union[CalibrationMode, str],
                 tau_ps: Optional[ArrayLike]    = None,
                 tauerr_ps: Optional[ArrayLike] = None,
                 weight: Optional[ArrayLike]    = None,
                 selection: Optional[ArrayLike] = None,
                 resolution_model           = None,
                 analytic_gradient: bool    = False):
        super().__init__(name              = name,
                         eta_data          = eta_data,
                         dec_data          = dec_data,
                         B_ID              = B_ID,
                         mode              = mode,
                         tau_ps            = tau_ps,
                         tauerr_ps         = tauerr_ps,
                         weight            = weight,
                         selection         = selection,
                         resolution_model  = resolution_model,
                         analytic_gradient = analytic_gradient)
        self.__init_minimizer()
        self.__check_logic(B_ID, tau_ps)

    def __init_minimizer(self) -> None:
        """ Initializes the flavour tagging likelihood and the minimizer """
        self.stats.params = CalParameters(self.func.npar)
        self.minimizer = iminuit.Minuit(self.__nll_oscil if self.mode.oscillation else self.__nll,
                                        tuple(np.zeros(2 * self.func.npar)),
                                        name      = self.stats.params.names_flavour,
                                        grad      = self.__nll_oscil_grad if self._analytic_gradient else None)
        self.minimizer.errordef = iminuit.Minuit.LIKELIHOOD
        self.minimizer.print_level = 2
        self.minimizer.strategy = 0

    def __check_logic(self, ID: ArrayLike, tau_ps: Optional[ArrayLike]) -> None:
        # Check branch name
        if isinstance(ID, pd.Series):
            if "true" in str(ID.name).lower() and self.mode.oscillation:
                ftcalib_warning(f"LogicWarning:{self.name}", f"Possible 'TRUEID' found in ID branch name '{ID.name}'. Be advised that mode='{self.mode}' accounts for oscillation of the decay flavour specific to the B meson type, but TRUEID is already the true production flavour and no further correction must be applied. This will break the calibration. Use mode='TRUEID' instead to disable the correction.")

        if tau_ps is not None and len(tau_ps) > 1000 and self.mode.oscillation:
            tau_expected = constants.Lifetime_Bd if self.mode == CalibrationMode.Bd else constants.Lifetime_Bs
            tau_ratio = np.mean(tau_ps) / tau_expected
            if tau_ratio < 1/constants.LifetimeToleranceFactor or tau_ratio > constants.LifetimeToleranceFactor:
                ftcalib_warning(f"UnitWarning:{self.name}", f"Tagger {self.name}: average decay time seems inconsistent with calibration mode '{self.mode}'. Off by more than a factor {constants.LifetimeToleranceFactor}. Average tau = {np.mean(tau_ps):.6f} ps, while expected lifetime is {constants.Lifetime_Bd if self.mode == CalibrationMode.Bd else constants.Lifetime_Bs} ps. This will likely break the calibration. Please check your input data and unit settings.")
            
    def set_calibration(self, func: CalibrationFunction) -> None:
        """ Override default calibration function

            :param func: Calibration function
            :type func: CalibrationFunction
        """
        self.func = deepcopy(func)
        self.func.init_basis(self.stats._tagdata.eta, weight=self.stats._tagdata.weight)
        self.__init_minimizer()

    def retry_on_error(self, use_link_alternative: Optional[link_function] = None, increase_func_order: bool = False):
        """ Modify calibration function in case initial
            minimization fails. Only one retry will be attempted.

            :param use_link_alternative: Alternative link function type
            :type use_link_alternative: link_function
            :param increase_func_order: If true, calibration order is increased
            :type increase_func_order: bool
        """
        self._has_plan_b = True
        self._link_alternative = use_link_alternative
        self._increase_func_order = increase_func_order

    def calibrate(self):
        """ Runs configured flavour tagging calibration and adds calibrated mistag information to TaggingData """
        if self._calibrated:
            warning(f"Tagger {self.name} has already been calibrated. Skipping.")
            ftcalib_warning(f"CalibrationWarning [{self.name}]", f"Tagger {self.name} has already been calibrated. Skipped.")
            return
        iminuit_version = iminuit.__version__
        printbold(20 * "-" + f" {self.name} calibration " + 20 * "-")
        info("iminuit version", iminuit_version)
        assert version.parse(iminuit_version) >= version.parse("2.3.0"), "iminuit >= 2.3.0 required"

        info("Starting minimization for", self.name)
        info(f"Selection keeps {self.stats.Ns}({self.stats.Nws} weighted) out of {self.stats.N}({self.stats.Nw}) events ({100*np.round(self.stats.Ns/self.stats.N, 4)}%)")

        def call_minimizer():
            self.minimizer.migrad()
            self.minimizer.hesse()

            if self.minimizer.valid:
                info("Minimum found")
                if self.minimizer.accurate:
                    info("Covariance matrix accurate")
                else:
                    warning("Covariance matrix -NOT- accurate")
                    ftcalib_warning(f"MinimizationWarning [{self.name}]", f"Tagger {self.name}: Covariance matrix not accurate after minimization.")
            else:
                if self._has_plan_b:
                    self._has_plan_b = False
                    newlink = self.func.link if self._link_alternative is None else self._link_alternative
                    neworder: int = self.func.npar + 1 if self._increase_func_order else self.func.npar
                    self.set_calibration(type(self.func)(neworder, newlink))
                    warning("Trying alternative calibration function type", str(self.func))
                    self.minimizer.migrad()
                    self.minimizer.hesse()
                    call_minimizer()
                else:
                    raise_error(False, "Minimization did not converge")

        call_minimizer()

        covariance = self.__covariance_correction()

        params = [self.minimizer.values[v] for v in self.minimizer.parameters]
        self.stats._compute_calibrated_statistics(self.func, params, covariance, self.minimizer.accurate, self.name)

        self._calibrated = True
        print()

    def __covariance_correction(self) -> np.ndarray:
        # Correct covariance if likelihood is weighted
        if constants.CovarianceCorrectionMethod == "None" or not self._weighted:
            return np.array(self.minimizer.covariance)

        info("Scaling Hesse Matrix")
        params = [self.minimizer.values[n] for n in self.minimizer.parameters]
        cov = -np.linalg.inv(self.__hessian(params, squaredWeight=False))
        if constants.CovarianceCorrectionMethod == "SquaredHesse":
            sqhessian = -1 * self.__hessian(params, squaredWeight=True)
            return cov @ sqhessian @ cov
        if constants.CovarianceCorrectionMethod == "SumW2":
            sumW  = np.sum(self.stats._tagdata.weight)
            sumW2 = np.sum(self.stats._tagdata.weight**2)
            return cov * (sumW2 / sumW)
        raise RuntimeError("Unknown covariance correction method")

    def get_dataframe(self, calibrated: bool = True) -> pd.DataFrame:
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :param calibrated: Return dataframe of calibrated mistags and tag decisions
            :type calibrated: bool
            :raises: AssertionError if tagger has not been calibrated and calibrated=True
            :return: dataframe with mistag and tagging decision
            :return type: pandas.DataFrame
        """
        if calibrated:
            assert self._calibrated
            return pd.DataFrame({
                self.name + "_CDEC"  : np.array(self.stats._full_data.cdec.copy(), dtype=np.int32),
                self.name + "_OMEGA" : np.array(self.stats._full_data.omega.copy()),
                self.name + "_OMEGA_ERR" : np.array(self.stats._full_data.omega_err.copy())
            })
        else:
            if constants.propagate_errors and self.stats._can_propagate_error:
                return pd.DataFrame({
                    self.name + "_DEC"     : np.array(self.stats._full_data.dec.copy(), dtype=np.int32),
                    self.name + "_ETA"     : np.array(self.stats._full_data.eta.copy()),
                    self.name + "_ETA_ERR" : np.array(self.stats._full_data.eta_err.copy())
                })
            else:
                return pd.DataFrame({
                    self.name + "_DEC" : np.array(self.stats._full_data.dec.copy(), dtype=np.int32),
                    self.name + "_ETA" : np.array(self.stats._full_data.eta.copy())
                })

    def __nll(self, params: AnyList) -> np.ndarray:
        """ Likelihood for B+ modes without oscillation """
        data = self.stats._tagdata  # This is not a copy
        omega = self.func.eval(params, data.eta, data.prod_flav)

        log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(np.maximum(1 - omega[data.correct_tags], 1e-5)))  # Correct tags
        log_likelihood += np.sum(data.weight[data.wrong_tags]   * np.log(np.maximum(    omega[data.wrong_tags],   1e-5)))  # Incorrect tags

        return -log_likelihood

    def __nll_oscil(self, params: AnyList) -> np.ndarray:
        """ Likelihood for Bd and Bs modes with oscillation """
        data = self.stats._tagdata  # This is not a copy
        omega_given = self.func.eval(params, data.eta,      data.prod_flav)  # Omega based on predicted production flavour
        omega_oscil = self.func.eval(params, data.eta, -1 * data.prod_flav)  # Omega for opposite prod flavour

        correct_terms  = (1.0 - data.osc_dilution[data.correct_tags]) * (1.0 - omega_given[data.correct_tags])  # No mixing (tag == prod flav == decay flav)
        correct_terms +=        data.osc_dilution[data.correct_tags]  * omega_oscil[data.correct_tags]          # mixing    (tag == prod flav != decay flav)

        wrong_terms    = (1.0 - data.osc_dilution[data.wrong_tags]) * omega_given[data.wrong_tags]          # No mixing (tag != prod flav == decay flav)
        wrong_terms   +=        data.osc_dilution[data.wrong_tags]  * (1.0 - omega_oscil[data.wrong_tags])  # mixing    (tag != prod flav != decay flav)

        # log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(np.maximum(correct_terms, 1e-5)))
        # log_likelihood += np.sum(data.weight[data.wrong_tags] * np.log(np.maximum(wrong_terms, 1e-5)))

        log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(correct_terms))
        log_likelihood += np.sum(data.weight[data.wrong_tags] * np.log(wrong_terms))

        return -log_likelihood

    def __nll_oscil_grad(self, params: AnyList) -> np.ndarray:
        """ Likelihood gradient """
        data = self.stats._tagdata  # This is not a copy

        omega_given = self.func.eval(params, data.eta,      data.prod_flav)
        omega_oscil = self.func.eval(params, data.eta, -1 * data.prod_flav)
        correct_tags = data.correct_tags
        wrong_tags   = data.wrong_tags

        osc_dilution_correct = data.osc_dilution[correct_tags]
        osc_dilution_wrong   = data.osc_dilution[wrong_tags]

        denom_correct  = (1.0 - osc_dilution_correct) * (1.0 - omega_given[correct_tags])
        denom_correct +=        osc_dilution_correct  *        omega_oscil[correct_tags]
        denom_wrong    = (1.0 - osc_dilution_wrong)   *        omega_given[wrong_tags]
        denom_wrong   +=        osc_dilution_wrong    * (1.0 - omega_oscil[wrong_tags])

        grad = np.zeros(self.func.npar * 2)

        for i in range(self.func.npar * 2):
            correct_terms  =      osc_dilution_correct  * self.func.derivative(i, params, data.eta[correct_tags], -1 * data.decay_flav[correct_tags])
            correct_terms -= (1 - osc_dilution_correct) * self.func.derivative(i, params, data.eta[correct_tags],      data.decay_flav[correct_tags])

            wrong_terms  = (1 - osc_dilution_wrong) * self.func.derivative(i, params, data.eta[wrong_tags],      data.decay_flav[wrong_tags])
            wrong_terms -=      osc_dilution_wrong  * self.func.derivative(i, params, data.eta[wrong_tags], -1 * data.decay_flav[wrong_tags])

            grad[i]  = np.sum(data.weight[correct_tags] * correct_terms / denom_correct)
            grad[i] += np.sum(data.weight[wrong_tags] * wrong_terms / denom_wrong)

        return -grad

    def __hessian(self, params: AnyList, squaredWeight: bool) -> np.ndarray:
        """ Likelihood hessian """
        data = self.stats._tagdata
        dilution = data.osc_dilution
        dim      = self.func.npar * 2

        # Compute likelihood terms
        omega_given = self.func.eval(params, data.eta,      data.prod_flav)
        omega_oscil = self.func.eval(params, data.eta, -1 * data.prod_flav)

        Pi = (1.0 - omega_given) * (1.0 - dilution) + omega_oscil * dilution

        hesse = np.zeros((dim, dim))

        domega_given = self.func.gradient(params, data.eta,      data.prod_flav)
        domega_oscil = self.func.gradient(params, data.eta, -1 * data.prod_flav)

        for i in range(dim):
            dPi = -domega_given[i] * (1.0 - dilution) + domega_oscil[i] * dilution

            for j in range(dim):
                dPij = -domega_given[j] * (1.0 - dilution) + domega_oscil[j] * dilution

                vals = np.zeros(len(data.eta))
                vals[data.correct_tags] = -dPi[data.correct_tags] * dPij[data.correct_tags] / Pi[data.correct_tags]**2
                vals[data.wrong_tags]   = -dPi[data.wrong_tags] * dPij[data.wrong_tags] / (1.0 - Pi[data.wrong_tags])**2

                if squaredWeight:
                    hesse[i][j] = np.sum(data.weight**2 * vals)
                else:
                    hesse[i][j] = np.sum(data.weight * vals)
        return hesse
