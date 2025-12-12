import json
import pandas as pd
import numpy as np
from typing import List, Union, Optional

from .ft_types import ArrayLike, CalibrationMode
from .Tagger import TaggerBase
from .TaggerCollection import TaggerCollection
from .CalibrationFunction import CalibrationFunction
from .PolynomialCalibration import PolynomialCalibration
from .NSplineCalibration import NSplineCalibration
from .BSplineCalibration import BSplineCalibration
from .printing import (info, print_tagger_correlation,
                       print_tagger_performances, print_tagger_statistics, warning,
                       raise_error, printbold, raise_warning)
from .plotting import draw_inputcalibration_curve
from . import link_functions as links
from .CalParameters import CalParameters
from . import constants


class TargetTagger(TaggerBase):
    """ A variation of the tagger object which loads a calibration
        from file and applies it to some data. Like the "Tagger",
        it contains two sets of TaggingData (BasicTaggingData) for
        before and after the calibration.

        Note: Specifying the B id, calibration mode,
        decay time and its uncertainty as well as the resolution model is
        optional and only needed in order to estimate the raw mistag if this performance
        number is needed and if it makes sense to compute it from the B ids in the tuple.

        :param name: Name of this target tagger. Ideally, try to use the same as for the calibrated tagger
        :type name: str
        :param eta: Targeted mistag data
        :type eta: list
        :param dec: Targeted tagging decisions
        :type dec: list
        :param ID: B meson IDs (Not needed)
        :type ID: list
        :param mode: Calibration mode (Not needed)
        :type mode: str | CalibrationMode
        :param tau: Decay times in ps (Not needed)
        :type tau: list
        :param tauerr: Decay time uncertainties in ps (Not needed)
        :type tauerr: list
        :param weight: Weight variable (needed for tagging statistics information)
        :type weight: list
    """

    class __LoadedMinimizer:
        def __init__(self):
            self.values: Optional[np.ndarray] = None
            self.errors: Optional[np.ndarray] = None
            self.covariance: Optional[np.ndarray] = None
            self.accurate: bool = True  # At this point we trust the calibration file

    def __init__(self,
                 name: str,
                 eta_data: ArrayLike,
                 dec_data: ArrayLike,
                 B_ID: Optional[ArrayLike]      = None,
                 mode: Optional[Union[CalibrationMode, str]] = None,
                 tau_ps: Optional[ArrayLike]    = None,
                 tauerr_ps: Optional[ArrayLike] = None,
                 weight: Optional[ArrayLike]    = None,
                 resolution_model             = None):
        if tau_ps is not None and B_ID is None:
            warning("Need B ID to interpret decay time info. Ignoring tau branch.")
        raise_error(not (mode is None and any([a is not None for a in [tau_ps, tauerr_ps, resolution_model]])),
                    "If decay time related info is provided for a target tagger, the mode must be set to Bd or Bs.")

        super().__init__(name              = name,
                         eta_data          = eta_data,
                         dec_data          = dec_data,
                         B_ID              = B_ID if B_ID is not None else np.ones(len(eta_data)),
                         mode              = CalibrationMode.Bu if mode is None else mode,
                         tau_ps            = tau_ps if B_ID is not None else None,
                         tauerr_ps         = tauerr_ps if B_ID is not None else None,
                         weight            = weight,
                         selection         = np.ones(len(eta_data), dtype=bool),  # All events are selected when taggers are applied
                         resolution_model  = resolution_model,
                         analytic_gradient = False)
        raise_error(not (self.mode.oscillation and tau_ps is None), f"If a calibration mode \"{mode}\" is specified for a TargetTagger, the decay time needs to be provided")

        self.info        = None
        self.func: CalibrationFunction = PolynomialCalibration(2, links.mistag)  # TaggerBase sets func by default
        self._calibrated = False
        self._has_b_id   = B_ID is not None
        self.minimizer   = self.__LoadedMinimizer()

    def apply(self, ignore_delta: bool = True):
        """ Apply the previously loaded calibration to this tagger

            :param ignore_delta: If false, delta calibration parameters will be used when calibration is applied
            :type ignore_delta: bool
        """
        assert self._calibrated

        if not constants.ignore_mistag_asymmetry_for_apply:
            raise_warning(not self._has_b_id, "No B ID has been provided! Cannot apply mistag asymmetries!")

        self.stats._compute_calibrated_statistics(self.func, self.minimizer.values, self.minimizer.covariance, self.minimizer.accurate, self.name)

    def load(self, filename_or_dict: Union[str, dict], tagger_name: str, style: str = "flavour") -> None:
        """ Load a calibration entry from a calibration file

            :param filename_or_dict: Filename of the calibration file or ftcalib calibration dictionary
            :type filename_or_dict: str or dict
            :param tagger_name: Entry name of the calibration data you would like to load
            :type tagger_name: str
            :param style: Which parameter style to use
            :type style: str ("delta", "flavour")
        """
        assert isinstance(filename_or_dict, (dict, str)), "Invalid type for calibration info"
        if isinstance(filename_or_dict, dict):
            calib = filename_or_dict
        elif isinstance(filename_or_dict, str):
            with open(filename_or_dict, "r") as F:
                calib = json.loads(F.read())

        # Reconstruct calibration function
        assert tagger_name in calib, "Tagger " + tagger_name + " not contained in calibration info"
        self.info = calib[tagger_name]

        assert style in ["flavour", "delta"], "Calibrations in " + style + "style not supported. Please use 'flavour' or 'delta' style."

        if "PolynomialCalibration" in self.info:
            fun_info = self.info["PolynomialCalibration"]
            self.func = PolynomialCalibration(int(fun_info["degree"]), _get_link_by_name(fun_info["link"]))
            basis = self.info["PolynomialCalibration"]["basis"]
            basis = [np.array(vec) for vec in basis]
            self.func.set_basis(basis)
        elif "NSplineCalibration" in self.info:
            fun_info = self.info["NSplineCalibration"]
            self.func = NSplineCalibration(int(fun_info["degree"]) - 2, _get_link_by_name(fun_info["link"]))
            basis = self.info["NSplineCalibration"]["basis"]
            basis = [np.array(vec) for vec in basis]
            self.func.set_basis(basis=fun_info["basis"], nodes=fun_info["nodes"])
        elif "BSplineCalibration" in self.info:
            fun_info = self.info["BSplineCalibration"]
            self.func = BSplineCalibration(int(fun_info["degree"]), _get_link_by_name(fun_info["link"]))
            self.func.set_basis(fun_info["nodes"])
        else:
            raise RuntimeError("Unknown calibration function")

        self.stats.params = CalParameters(npar=self.func.npar)
        params = np.array(self.info["calibration"][style + "_style"]["params"])

        noms_loaded   = [float(v) for v in params[:, 1]]
        cov_loaded = self.info["calibration"][style + "_style"]["cov"]
        cov_loaded = np.array([float(e) for row in cov_loaded for e in row]).reshape((2 * self.func.npar, 2 * self.func.npar))

        if style == "delta":
            self.stats.params.set_calibration_delta(noms_loaded, cov_loaded)
        elif style == "flavour":
            self.stats.params.set_calibration_flavour(noms_loaded, cov_loaded)

        self.minimizer.values = self.stats.params.params_flavour
        self.minimizer.errors = self.stats.params.errors_flavour
        self.minimizer.covariance = self.stats.params.covariance_flavour

        self.DeltaM     = self.info["osc"]["DeltaM"]
        self.DeltaGamma = self.info["osc"]["DeltaGamma"]
        self.Aprod      = self.info["osc"]["Aprod"]

        self._calibrated = True

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
            return pd.DataFrame({
                self.name + "_DEC" : np.array(self.stats._full_data.dec.copy(), dtype=np.int32),
                self.name + "_ETA" : np.array(self.stats._full_data.eta.copy())
            })


def _get_link_by_name(link: str) -> type[links.link_function]:
    return {
        "mistag"   : links.mistag,
        "logit"    : links.logit,
        "rlogit"   : links.rlogit,
        "probit"   : links.probit,
        "rprobit"  : links.rprobit,
        "cauchit"  : links.cauchit,
        "rcauchit" : links.rcauchit,
    }[link.lower()]


class TargetTaggerCollection(TaggerCollection):
    r""" class TaggerCollection List type for grouping target taggers. Supports iteration.

        :param \*taggers: Tagger instance
        :type \*taggers: Tagger
    """

    def __init__(self, *taggers: List[TargetTagger]):
        super().__init__(*taggers)

    def __str__(self) -> str:
        return "TargetTaggerCollection [" + ','.join([t.name for t in self._taggers]) + "]"

    def _validate(self) -> None:
        assert all([isinstance(tagger, TargetTagger) for tagger in self._taggers]), "TargetTaggerCollection can only store TargetTagger instances"
        assert len(set([tagger.name for tagger in self._taggers])) == len(self._taggers), "Tagger names are not unique"

    def add_taggers(self, *tagger: List[TargetTagger]) -> None:
        """ Adds tagger(s) to the TagCollection instance by reference """
        self._taggers += [*tagger]
        self._validate()

    def create_tagger(self, *args, **kwargs):
        """ Adds a Target instance to the TargetTaggerCollection instance
            by passing the arguments to the TargetTagger() constructor.
        """
        self._taggers.append(TargetTagger(*args, **kwargs))
        self._validate()

    def load_calibrations(self, filename_or_dict: Union[str, dict], tagger_mapping: Optional[dict] = None, style: str = "flavour") -> None:
        """ Load calibrations from a file

            :param filename_or_dict: Filename of the calibration file or ftcalib calibratiopn dictionary
            :type filename_or_dict: str or dict
            :param tagger_mapping: Optional dictionary of a mapping of tagger names in this list vs corresponding entry names in the calibration file. By default, the same naming is assumed (!)
            :type tagger_mapping: dict
            :param style: Which parameter style to use
            :type style: str ("delta", "flavour")
        """
        if tagger_mapping is None:
            tagger_mapping = { t.name : t.name for t in self._taggers }
        else:
            assert len(tagger_mapping) == len(self)

        for tagger in self._taggers:
            info(f"Loading {tagger_mapping[tagger.name]} calibrations for {tagger.name}")
            tagger.load(filename_or_dict, tagger_mapping[tagger.name], style)

    def apply(self, quiet: bool = False, ignore_delta: bool = True) -> None:
        """ Applies the previously loaded calibrations to a taggers

            :param quiet: Whether to print performance summary tables
            :type quiet: bool
        """

        if not quiet:
            print_tagger_correlation(self, "fire")
            print_tagger_correlation(self, "dec")
            print_tagger_correlation(self, "dec_weight")
            print_tagger_statistics(self, calibrated=False, selected=False)
            print_tagger_performances(self, calibrated=False, selected=False)

        for tagger in self._taggers:
            info(f"Applying calibration for {tagger.name}")
            tagger.apply(ignore_delta)

        if not quiet:
            print_tagger_statistics(self, calibrated=True, selected=False)
            print_tagger_performances(self, calibrated=True, selected=False)

    def plot_inputcalibration_curves(self, **kwargs) -> None:
        r""" Plots input calibration curves of a set of taggers, like the EPM
            does when a calibration is applied.  Plots the loaded calbration curve
            (uncertainties are loaded but ignored while applying the calibration)
            and the targeted mistag data.

            :param \**kwargs: Arguments to pass to draw_inputcalibration_curve
        """
        for tagger in self._taggers:
            print("Info: pdf file", draw_inputcalibration_curve(tagger, **kwargs), "has been created")

    def combine_taggers(self, name: str, calibrated: bool, next_selection: Optional[ArrayLike] = None, tagger_subset: Optional[List[str]] = None, append: bool = False) -> TargetTagger:
        """ Computes the combination of multiple target taggers
            and returns it in the form of a new TargetTagger object

            :param name: Name of the tagger combination
            :type name: str
            :param calibrated: Whether to use calibrated tagger data for combination (recommended)
            :type calibrated: bool
            :param next_selection: Event selection to use for calibrating combination (default: No selection)
            :type next_selection: list
            :param tagger_subset: List of tagger names to combine (optional)
            :type tagger_subset: list of (str or int)
            :return: Tagger combination
            :rtype: Tagger
        """

        (incombination,
         omega_combined,
         d_combined,
         gradients_combined,
         covariances) = self._prepare_combination(name,
                                                   calibrated     = calibrated,
                                                   next_selection = next_selection,
                                                   tagger_subset  = tagger_subset,
                                                   append         = append)

        combination = TargetTagger(name     = name,
                                   eta_data = omega_combined,
                                   dec_data = d_combined,
                                   weight = incombination[0].stats._full_data.weight)
        if calibrated and constants.propagate_errors:
            combination.stats._compute_combination_statistics(omega_combined, gradients_combined, covariances, name)
        printbold(f"New tagger combination {combination.name} has been created")
        return combination
