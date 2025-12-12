import numpy as np
import pandas as pd
import threading
from typing import List, Optional, Union
from scipy.linalg import block_diag
from numba import jit

from .ft_types import ArrayLike
from .link_functions import link_function
from .CalibrationFunction import CalibrationFunction
from .plotting import draw_calibration_curve
from .combination import _combine_taggers, _correlation
from .printing import (print_tagger_correlation, print_tagger_performances, print_tagger_statistics,
                       blue_header, section_header, printbold, raise_warning,
                       raise_error, print_calibration_parameters, info)
from .Tagger import Tagger
from . import constants


class TaggerCollection:
    r""" class TaggerCollection
        Lists type for grouping taggers.

        :param \*taggers: Tagger instance
        :type \*taggers: Tagger
    """

    def __init__(self, *taggers: Tagger):
        self._taggers: List[Tagger] = [*taggers]
        self._index = -1
        if self._taggers:
            self._validate()

    def __str__(self) -> str:
        return "TaggerCollection [" + ','.join([t.name for t in self._taggers]) + "]"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self._taggers)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == len(self._taggers) - 1:
            self._index = -1
            raise StopIteration
        self._index += 1
        return self._taggers[self._index]

    def __getitem__(self, t: Union[int, slice, str]) -> Union[Tagger, List[Tagger]]:
        if isinstance(t, (int, slice)):
            return self._taggers[t]
        else:
            for j, tagger in enumerate(self._taggers):
                if tagger.name == t:
                    return self._taggers[j]
        raise IndexError

    def _validate(self) -> None:
        # Taggers cannot come from different datasets and their names must be unique
        assert all([isinstance(tagger, Tagger) for tagger in self._taggers]), "TaggerCollection can only store Tagger instances"
        assert len(set([tagger.name for tagger in self._taggers])) == len(self._taggers), "Tagger names are not unique"
        assert len(set([tagger.stats.N for tagger in self._taggers])) == 1, "Data of Taggers have inconsistent lenghts"

    def set_calibration(self, func: CalibrationFunction) -> None:
        """ Sets a calibration function for all taggers

            :param func: Calibration function
            :type func: CalibrationFunction
        """
        for tagger in self._taggers:
            tagger.set_calibration(func)

    def add_taggers(self, *tagger: Tagger) -> None:
        """ Adds tagger(s) to the TagCollection instance by reference """
        self._taggers += [*tagger]
        self._validate()

    def create_tagger(self, *args, **kwargs) -> None:
        """ Adds a tagger to the TaggerCollection instance
            by passing the arguments to the Tagger() constructor.
        """
        self._taggers.append(Tagger(*args, **kwargs))
        self._validate()

    def calibrate(self, corr: bool=True, stats: bool=True, perf: bool=True, params: bool=True, basis: bool=True, quiet: bool=False, parallel: bool=False) -> None:
        """ Loops over taggers, calibrates taggers and prints tagging information
            both before and after the calibrations and prints a summary of warning at the end.

            :param corr: If false, correlation coefficients are not printed
            :type corr: bool
            :param stats: If false, tagged event statistics are not printed
            :type stats: bool
            :param perf: If false, tagging performances are not printed
            :type perf: bool
            :param params: If false, tagging result is not printed
            :type params: bool
            :param basis: If false, does not print basis representation
            :type basis: bool
            :param quiet: If True all outputs except warnings are silenced
            :type quiet: bool
            :param parallel: If true calibrations of individual taggers will be split up into parallel threads
            :type parallel: bool
        """
        # Sanity checks
        raise_error(len(set([t.name for t in self._taggers])) == len(self._taggers), "Tagger names not unique")

        if quiet:
            corr = False
            stats = False
            perf = False
            params = False
            basis = False

        if corr:
            print_tagger_correlation(self, "fire")
            print_tagger_correlation(self, "dec")
            print_tagger_correlation(self, "dec_weight")
            print_tagger_correlation(self, "both_fire")  # expensive
        if stats:
            print_tagger_statistics(self, calibrated=False)
        if perf:
            print_tagger_performances(self, calibrated=False)

        for tagger in self._taggers:
            if basis:
                printbold(f"Basis representation for {tagger.name}")
                tagger.func.print_basis()

        if not quiet:
            blue_header("Running calibrations")

        if parallel:
            info("Starting calibrations in parallel threads")
            threads = []

            def cal_wrapper(func):
                func()

            for tagger in self._taggers:
                threads.append(threading.Thread(target=cal_wrapper, args=(tagger.calibrate, )))

            for thread in threads:
                thread.start()

            info("Waiting for calibrations to finish...")
            for thread in threads:
                thread.join()

        else:
            for tagger in self._taggers:
                tagger.calibrate()

        if params:
            print_calibration_parameters(self)
        if stats:
            print_tagger_statistics(self, calibrated=True)
        if perf:
            print_tagger_performances(self, calibrated=True)

    def get_dataframe(self, calibrated: bool=True) -> pd.DataFrame:
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :param calibrated: If true, calibrated decisions and mistags are written
            :type calibrated: bool

            :return: Calibrated data
            :return type: pandas.DataFrame
        """
        df = pd.DataFrame()
        if calibrated:
            for tagger in self._taggers:
                assert tagger.is_calibrated()
                df[tagger.name + "_CDEC"]  = np.array(tagger.stats._full_data.cdec.copy(), dtype=np.int32)
                df[tagger.name + "_OMEGA"] = np.array(tagger.stats._full_data.omega.copy())
                df[tagger.name + "_OMEGA_ERR"] = np.array(tagger.stats._full_data.omega_err.copy())
        else:  # Only makes sense if user writes an uncalibrated combination to file
            for tagger in self._taggers:
                df[tagger.name + "_DEC"] = np.array(tagger.stats._full_data.dec.copy(), dtype=np.int32)
                df[tagger.name + "_ETA"] = np.array(tagger.stats._full_data.eta.copy())
                if constants.propagate_errors and tagger.stats._can_propagate_error:
                    df[tagger.name + "_ETA_ERR"] = np.array(tagger.stats._full_data.eta_err.copy())
        return df

    def plot_calibration_curves(self, **kwargs):
        r""" Plots calibration curves of a set of taggers

            :param \**kwargs: Arguments to pass to draw_calibration_curve
        """
        section_header("Plotting")
        for tagger in self._taggers:
            info("pdf file", draw_calibration_curve(tagger, **kwargs), "has been created")

    def _prepare_combination(self, name: str, calibrated: bool, next_selection: Optional[ArrayLike]=None, tagger_subset: Optional[List[str]]=None, append: bool=False):
        # Internal function that prepares data and chooses taggers for tagger combination
        # If configured, calibration uncertainties are  propagated
        if tagger_subset is None:
            incombination = self._taggers
        else:
            assert isinstance(tagger_subset, list), "A list needs to be provided for argument tagger_subset"
            incombination = []
            for sel in tagger_subset:
                incombination.append(self.__getitem__(sel))

        if len(incombination) == 0:
            raise RuntimeWarning("No taggers to combine")
            return None

        taggernames = [t.name for t in incombination]
        section_header("TAGGER COMBINATION")
        printbold("Combining taggers " + " ".join(taggernames) + f" into {name}")
        printbold("Checking compatibility")

        # Sanity checks
        for tagger in incombination:
            raise_error(tagger.stats._full_data.decay_flav.equals(incombination[0].stats._full_data.decay_flav), "Taggers must refer to the same pp collision, otherwise combination is nonsense")
        raise_warning(name not in taggernames, "Name of combination is already in use")
        if calibrated:
            indeed_calibrated = [t.is_calibrated() for t in incombination]  # Do not forbid combination of calibrated and uncalibrated taggers
            raise_warning(all(indeed_calibrated), "None, or not all provided taggers have been calibrated")

        printbold("Running combination...")
        # Collect data
        gradients_combined = None
        covariances = None

        @jit(forceobj=True)
        def compute_gradient(npars, vec_gradients, ntaggers: int, nevents: int):
            gradients = np.empty((int(nevents), int(ntaggers), int(np.sum(npars))))
            for i in range(nevents):
                for j in range(ntaggers):
                    start = 0
                    for m in range(j):
                        start += npars[m]
                    for k in range(npars[j]):
                        gradients[i][j][int(start + k)] = vec_gradients[j][k][i]
            return gradients

        npars = None
        gradients = None
        if calibrated and constants.propagate_errors:
            decs   = np.array([ np.array(tagger.stats._full_data.cdec  if cal else tagger.stats._full_data.dec) for tagger, cal in zip(incombination, indeed_calibrated) ]).T
            omegas = np.array([ np.array(tagger.stats._full_data.omega if cal else tagger.stats._full_data.eta) for tagger, cal in zip(incombination, indeed_calibrated) ]).T
            etas = np.array([ np.array(tagger.stats._full_data.eta) for tagger, cal in zip(incombination, indeed_calibrated) ]).T
            npars = np.array([tagger.func.npar for tagger in incombination])
            if constants.ignore_mistag_asymmetry_for_apply:
                vec_gradients = np.array([tagger.func.gradient_averaged(tagger.stats.params.params_average, etas[:, i]) for i, tagger in enumerate(incombination)], dtype=object)
                covariances = block_diag(*[t.stats.params.covariance_average for t in incombination])
            else:
                npars *= 2
                vec_gradients = np.array([tagger.func.gradient(tagger.stats.params.params_flavour, etas[:, i], decs[:, i]) for i, tagger in enumerate(incombination)], dtype=object)
                covariances = block_diag(*[t.stats.params.covariance_flavour for t in incombination])
            gradients = np.empty((len(decs), len(incombination), np.sum(npars)))
            gradients = compute_gradient(npars, vec_gradients, ntaggers=len(incombination), nevents=len(decs))
        elif calibrated:
            decs   = np.array([ np.array(tagger.stats._full_data.cdec) for tagger in incombination ]).T
            omegas = np.array([ np.array(tagger.stats._full_data.omega) for tagger in incombination ]).T
        else:
            decs   = np.array([ np.array(tagger.stats._full_data.dec) for tagger in incombination ]).T
            omegas = np.array([ np.array(tagger.stats._full_data.eta) for tagger in incombination ]).T

        d_combined, omega_combined, gradients_combined = _combine_taggers(decs, omegas, gradients=gradients, npars=npars)

        return incombination, omega_combined, d_combined, gradients_combined, covariances

    def combine_taggers(self, name: str, calibrated: bool, next_selection: Optional[ArrayLike]=None, tagger_subset: Optional[List[str]]=None, append: bool=False) -> Tagger:
        """ Computes the combination of multiple taggers
            and returns it in the form of a new Tagger object

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

        # Find decay time info
        tau = None
        tauerr = None

        for tagger in incombination:
            if tagger.stats._has_tau:
                tau = tagger.stats._full_data.tau
            if tagger.stats._has_tauerr:
                tauerr = tagger.stats._full_data.tau_err

        # Construct Tagger object
        combination = Tagger(name      = name,
                             eta_data  = omega_combined,
                             dec_data  = d_combined,
                             B_ID      = incombination[0].stats._full_data.decay_flav,
                             mode      = incombination[0].mode,
                             tau_ps    = tau,
                             tauerr_ps = tauerr,
                             weight    = incombination[0].stats._full_data.weight,
                             selection = next_selection)
        if calibrated and constants.propagate_errors:
            combination.stats._compute_combination_statistics(omega_combined, gradients_combined, covariances, combination.name)
        printbold(f"New tagger combination {combination.name} has been created")
        return combination

    def correlation(self, corrtype: str="dec_weight", calibrated: bool=False) -> pd.DataFrame:
        r""" Compute different kinds of tagger correlations. The data points are weighted by their per-event weight.
            The weighted correlation coefficient between two observables X and Y with weights W is defined as

            :math:`\displaystyle\mathrm{corr}(X, Y, W) = \frac{\mathrm{cov}(X, Y, W)}{\mathrm{cov}(X, X, W) \mathrm{cov}(Y, Y, W)}`

            whereby

            :math:`\mathrm{cov}(X, Y, W) = \displaystyle\sum_i w_i (x_i-\overline{X}) (y_i - \overline{Y}) / \sum_iw_i`

            and

            :math:`\overline{X} = \sum_i w_ix_i / \sum_i w_i`

            One can choose between 4 different correlation types:

            * corrtype="fire" : Correlation of tagger decisions irrespective of decision sign
                :math:`x_i=|d_{x,i}|, y_i=|d_{y,i}|` and :math:`W` is the event weight

            * corrtype="dec" : Correlation of tagger decisions taking sign of decision into account
                :math:`x_i=d_{x,i}, y_i=d_{y,i}` and :math:`W` is the event weight

            * corrtype="dec_weight" : Correlation of tagger decisions taking sign of decision into account and weighted by tagging dilution
                :math:`x_i=d_{x,i}(1-2\eta_{x,i}), y_i=d_{y,i}(1-2\eta_{y,i}),` and :math:`W` is the event weight

            * corrtype="both_fire" : Correlation of tagger decisions if both have fired taking sign of decision into account
                :math:`x_i=d_{x,i}, y_i=d_{y,i}` and :math:`W` is the event weight

            :param corr: Type of correlation
            :type corr: string
            :param calibrated: Whether to use calibrated statistics. (Only relevant for correlation types with mistag, not part of automatic print-out)
            :type calibrated: bool
            :return: Correlation matrix
            :rtype: pandas.DataFrame
        """

        return _correlation(self._taggers, corrtype=corrtype, calibrated=calibrated)

    def destroy(self) -> None:
        """ Frees most of the allocated memory.
            Collection is ill-defined afterwards.
        """
        for tagger in self._taggers:
            tagger.destroy()

    def retry_on_error(self, use_link_alternative: Optional[link_function]=None, increase_func_order: bool=False) -> None:
        """ Modify calibration function for each tagger in case initial
            minimization fails. Only one retry will be attempted.

            :param use_link_alternative: Alternative link function type
            :type use_link_alternative: link_function
            :param increase_func_order: If true, calibration order is increased
            :type increase_func_order: bool
        """
        for tagger in self._taggers:
            tagger.retry_on_error(use_link_alternative, increase_func_order)
