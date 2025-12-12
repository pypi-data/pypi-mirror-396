import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use("agg")
from scipy.stats import beta
from scipy.special import erf
from typing import List, Tuple, Optional 

from .Tagger import Tagger
from .ft_types import ArrayLike, PathStr, StrOptionOrSettingsList, ScaleType
from .resolution_model import mixing_asymmetry



# Set LHCb style
ftcalib_plotstyle = {
    # Axis
    "axes.labelsize"              : 32,
    "axes.linewidth"              : 2,
    "axes.facecolor"              : "white",
    "axes.formatter.min_exponent" : 3,
    "axes.titlesize"              : 28,
    "axes.unicode_minus"          : False,
    "xaxis.labellocation"         : "right",
    "yaxis.labellocation"         : "top",
    "text.usetex"                 : False,
    # Errorbars
    "errorbar.capsize" : 2.5,
    # Figure
    "figure.dpi"        : 300,
    "figure.facecolor"  : "white",
    "figure.autolayout" : True,
    "figure.figsize"    : (12, 9),
    "font.family"       : "serif",
    "font.serif"        : ["Times New Roman", "Noto Serif"],
    "font.size"         : 13,  # 14
    "font.weight"       : 400,
    # Legend
    "legend.frameon"        : False,
    "legend.fancybox"       : True,
    "legend.facecolor"      : "inherit",
    "legend.numpoints"      : 1,
    "legend.labelspacing"   : 0.2,
    "legend.fontsize"       : 28,
    "legend.title_fontsize" : 28,
    "legend.handletextpad"  : 0.75,
    "legend.borderaxespad"  : 1.0,
    # Lines
    "lines.linewidth"       : 1.3,
    "lines.markeredgewidth" : 1.3,
    "lines.markersize"      : 10,
    # Format
    "savefig.bbox"       : "tight",
    "savefig.pad_inches" : 0.3,
    "savefig.format"     : "pdf",
    "patch.linewidth"    : 2,
    # Y Ticks
    "ytick.minor.visible" : True,
    "ytick.right"         : True,
    "ytick.major.size"    : 14,
    "ytick.minor.size"    : 7,
    "ytick.major.width"   : 2,
    "ytick.minor.width"   : 2,
    "ytick.major.pad"     : 10,
    "ytick.minor.pad"     : 10,
    "ytick.labelsize"     : 30,
    "ytick.direction"     : "in",
    # X Ticks
    "xtick.minor.visible" : True,
    "xtick.top"           : True,
    "xtick.major.size"    : 14,
    "xtick.minor.size"    : 7,
    "xtick.major.width"   : 2,
    "xtick.minor.width"   : 2,
    "xtick.major.pad"     : 10,
    "xtick.minor.pad"     : 10,
    "xtick.labelsize"     : 30,
    "xtick.direction"     : "in",
}


def beta_central_interval_efficiency(k: int, N: int) -> List[float]:
    # Returns the efficiency and its 1 sigma confidence interval of k events out of N passing a selection
    e = k / N
    nsigma = 1

    conf = erf(nsigma / np.sqrt(2))
    aa = k + 1
    bb = N - k + 1

    upper = beta.ppf((1 + conf) / 2, aa, bb)
    lower = beta.ppf((1 - conf) / 2, aa, bb)

    return [k / N, e - lower, upper - e]


def eta_omega_binning(tagger: Tagger, nbins: Optional[int], bins: Optional[ArrayLike]=None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ Determines the binning scheme used for plotting histograms and computes
        the binned true efficiencies of the tagger mistag in bins of eta.

        :param tagger: tagger object
        :type tagger: Tagger
        :param nbins: (optional) Number of true mistag bins
        :type nbins: (optional) int
        :param bins: (optional) list of mistag bin boundaries
        :type bins: (optional) np.ndarray

        :return: binning, efficiency estimators, lower confidence level bounds, upper confidence level bounds
    """

    # Divide eta range into bins of nbins equal sizes
    data       = tagger.stats._tagdata
    eta        = data.eta
    if bins is None:
        splitting  = np.array_split(sorted(eta), nbins)
        binning = np.array([[s[0], s[-1]] for s in splitting])
    else:
        assert bins is not None, "Either nbins or bins must be specified"
        assert len(bins) > 1, "List of bin boundaries must contain at least two bounds"
        assert sorted(bins) == bins, "Mistag bin boundaries must be sorted"
        binning = np.array([[i, j] for i, j in zip(bins[:-1], bins[1:])])

    if tagger.mode != "Bu":
        if tagger.stats._has_tauerr:
            Amix = mixing_asymmetry(tau=data.tau, DM=tagger.DeltaM, DG=tagger.DeltaGamma, tauerr=data.tau_err)
        else:
            Amix = mixing_asymmetry(tau=data.tau, DM=tagger.DeltaM, DG=tagger.DeltaGamma)
        pollution = 0.5 * (1 - np.abs(Amix))
    else:
        pollution = np.zeros(len(eta))

    def true_mistag_bin(eta_lo, eta_hi):
        # Returns true mis-classifiaction percentage in given bin bounds in the form:
        # Weighted mean of eta in bin (x axis) and true mistag estimate with simple binomial error (y axis)
        binmask = (eta >= eta_lo) & (eta < eta_hi)  # Selects bin

        binweights = data.weight[binmask]
        sumW = np.sum(binweights)

        oscDsq = np.sum(binweights * (1 - 2 * pollution[binmask])**2) / sumW

        asym  = np.sum(data.weight[data.correct_tags & binmask] * (1 - 2 * pollution[data.correct_tags & binmask]))
        asym -= np.sum(data.weight[data.wrong_tags & binmask]   * (1 - 2 * pollution[data.wrong_tags & binmask]))
        asym /= (sumW * oscDsq)

        effnum = (sumW**2 / np.sum(binweights**2)) * oscDsq

        Nw = 0.5 * (1 - asym) * effnum
        Nr = 0.5 * (1 + asym) * effnum
        return np.array([np.sum(eta[binmask] * binweights) / sumW] + beta_central_interval_efficiency(Nw, Nw + Nr))

    omega_true = np.array([true_mistag_bin(lo, hi) for lo, hi in binning])
    return binning, omega_true[:, 0], omega_true[:, 1], omega_true[:, 2], omega_true[:, 3]


def calibration_lineshape(tagger: Tagger, eta_plot: ArrayLike) -> np.ndarray:
    """ Returns the lineshape of the calibration curve
        corresponding to the input eta range.

        :param tagger: Tagger object
        :type tagger: Tagger
        :param eta_plot: List of increasing eta values for plotting
        :type eta_plot: list

        :return: calibration curve points
        :return type: list
    """
    return tagger.func.eval_plotting(tagger.stats.params.params_flavour, eta_plot, tagger.stats._tagdata.decay_flav)


def confidence_bands_lineshape(tagger: Tagger, eta_plot: ArrayLike, dec_plot: ArrayLike) -> np.ndarray:
    """ Returns the lineshape of the calibration curve
        corresponding to the input eta range.

        :param tagger: Tagger object
        :type tagger: Tagger
        :param eta_plot: List of increasing eta values for plotting
        :type eta_plot: list

        :return: 1-sigma confidence band line shape
        :return type: list
    """
    assert len(eta_plot) == len(dec_plot)
    J = tagger.func.gradient(tagger.stats.params.params_flavour, eta_plot, dec_plot).T
    assert tagger.minimizer.covariance is not None, f"Tagger {tagger} needs to be calibrated before its calibration curve can be plotted"
    cov = tagger.minimizer.covariance.tolist()

    band = np.array([np.sqrt(j @ cov @ j.T) for j in J])

    return band


def print_fit_setup(ax, position: List[float], tagger: Tagger, uformat: str="{:L}") -> Tuple[float, float, str]:
    """ Print calibration parameters in flavour style to the canvas

    :param ax: matplotlib axis
    :type ax: matplotlib.pyplot.axis
    :param position: x and y coordinate of starting corner
    :type position: list
    :param tagger: Tagger object
    :type tagger: Tagger
    :param uformat: uncertainties.ufloat formatting string. Alternative suggestion: "{:1uS}"
    :type uformat: str
    """
    param = tagger.stats.params.names_latex_delta

    noms = tagger.stats.params.params_delta
    errs = tagger.stats.params.errors_delta

    param = [fr"${p} = {np.round(n, 4)} \pm {np.round(s, 4)}$" for n, s, p in zip(noms, errs, param)]

    text = "\n".join(param) + "\n"
    text += tagger.func.link.__name__ + " link"
    ax.text(x=position[0], y=position[1], s=text, transform = ax.transAxes)
    return position[0], position[1], text


def get_eta_plotrange(eta_range: StrOptionOrSettingsList, binning: np.ndarray) -> List[float]:
    """ Determines a good x-axis range for the mistag

        :param eta_range: How to construct the mistag range
        :type eta_range: ("minimal", "full", or (float, float))
        :param binning: List of bin boundaries computed by get_omega_plotrange
        :type binning: list of list
    """
    if isinstance(eta_range, (tuple, list)):
        # User chose range
        assert len(eta_range) == 2, "Invalid mistag range"
        return list(eta_range)

    if eta_range == "minimal":
        eta_range = [binning[0][0], binning[-1][1]]
        eta_interv = eta_range[1] - eta_range[0]
        # Add padding
        eta_range[0] -= eta_interv * 0.02
        eta_range[1] += eta_interv * 0.02
    elif eta_range == "full":
        eta_range = [0, 0.5]
    elif isinstance(eta_range, str):
        raise RuntimeError("Unknown mistag range option", eta_range)

    if eta_range[0] < 0:
        eta_range[0] = 0

    return eta_range


def get_omega_plotrange(omega_range: StrOptionOrSettingsList, omega_true: ArrayLike, lower: ArrayLike, upper: ArrayLike, curve: ArrayLike) -> List[float]:
    """ Determines a good y-axis range for the calibrated mistag

        :param omega_range: How to construct the mistag range
        :type omega_range: "minimal", or (float, float)
        :param omega_true: List of true mistags to plot
        :type omega_true: np.ndarray
        :param lower: List of lower errors of the true mistag
        :type lower: np.ndarray
        :param upper: List of upper errors of the true mistag
        :type upper: np.ndarray
        :param curve: The sampled calibration curve
        :type curve: np.ndarray
    """

    if isinstance(omega_range, (tuple, list)):
        # User chose range
        assert len(omega_range) == 2, "Invalid calibrated mistag range"
        return list(omega_range)

    if omega_range == "minimal":
        # This imitates the EPM where the curve also determines the omega range
        omega_range = [min(np.nanmin(curve), np.nanmin(omega_true - lower)),
                       max(np.nanmax(curve), np.nanmax(omega_true + upper))]
        # Add padding
        omega_interv = omega_range[1] - omega_range[0]
        omega_range[0] -= omega_interv * 0.02
        omega_range[1] += omega_interv * 0.02

        return omega_range

    raise RuntimeError("Unknown calibrated mistag range option", omega_range)


def draw_calibration_curve(tagger: Tagger,
                           nbins: Optional[int]                     = 10,
                           eta_range: StrOptionOrSettingsList       = "minimal",
                           omega_range: StrOptionOrSettingsList     = "minimal",
                           print_params: bool                       = True,
                           params_position: StrOptionOrSettingsList = "auto",
                           title: Optional[str]                     = None,
                           samples: int                             = 100,
                           nsigma: int                              = 2,
                           sigma_color                              = [0.1, 0.7, 0.1],
                           nsigmaoutline: bool                      = False,
                           # etabins: int                             = 100,
                           savepath: PathStr                        = ".",
                           format: str                              = "pdf",
                           x_scale: ScaleType                       = 'linear',
                           y_scale: ScaleType                       = 'linear',
                           bins: Optional[ArrayLike]                  = None) -> str:
    """ Plots the calibration curve of a tagger including the confidence bands,
        true mistag and binned measured mistag distribution

        :param tagger: Tagger object
        :type tagger: Tagger
        :param nbins: Number of true mistag bins to plot
        :type nbins: int
        :param eta_range: measured mistag plot range
        :type eta_range: "minimal" or list
        :param omega_range: true mistag range
        :type omega_range: "minimal" or list
        :param print_params: Whether to plot the calibration parameters
        :type print_params: bool
        :param params_position: Text box position
        :type params_position: "auto" or [x, y] pair list
        :param title: Title to use instead of tagger name (default)
        :type title: str
        :param sample: How many curve points to plot (Plotting precision)
        :type sample: int
        :param nsigma: how many sigma intervals to plot
        :type nsigma: int
        :param sigma_color: R,G,B list
        :type sigma_color: list
        :param nsigmaoutline: whether to outline the last sigma interval
        :type nsigmaoutline: bool
        :param savepath: Path to the plot folder
        :type savepath: str
        :param format: Output file format (pdf, png, json)
        :type format: str
        :param x_scale: x-axis scale. Built-in matplotlib scale, or a tuple of the scale function and its inverse
        :type x_scale: str or tuple(Callable, Callable)
        :param y_scale: y-axis scale. Built-in matplotlib scale, or a tuple of the scale function and its inverse
        :type y_scale:  str or tuple(Callable, Callable)
        :param bins: Bin edges to use for the eta binning. If None, equal binning is used with <nbins> bins
        :type bins: list or None
    """
    with mpl.rc_context(ftcalib_plotstyle):
        if title is None:
            title = tagger.name + " Calibration"

        # Matplotlib
        _, ax_calib = plt.subplots()
        if title is not None:
            ax_calib.set_title(title)

        if format.startswith("."):
            format = format[1:]

        plot_json_data = {}

        # Get binning scheme, eta x values and true mistag rates including stat. uncertainty
        if bins is None:
            (binning, eta_points, omega_true, omega_true_lower, omega_true_upper) = eta_omega_binning(tagger, nbins)
        else:
            print(f"in draw{bins}")
            (binning, eta_points, omega_true, omega_true_lower, omega_true_upper) = eta_omega_binning(tagger, nbins=None, bins=bins)

        eta_range = get_eta_plotrange(eta_range, binning)

        eta_plot = np.linspace(eta_range[0], eta_range[1], samples)  # "Continuous" eta for plotting

        # Plot calibration curve and mean mistag
        curve = calibration_lineshape(tagger, eta_plot)
        ax_calib.plot(eta_plot, curve, color='k', label="Calibration")

        omega_range = get_omega_plotrange(omega_range, omega_true, omega_true_lower, omega_true_upper, curve)

        # Draw confidence bands
        bandsplus = confidence_bands_lineshape(tagger, eta_plot,  np.ones(samples))
        bandsminus = confidence_bands_lineshape(tagger, eta_plot, -np.ones(samples))
        bands = (bandsplus + bandsminus) / 2

        for ns in reversed(range(nsigma)):
            ax_calib.fill_between(eta_plot, curve - (ns + 1) * bands, curve + (ns + 1) * bands, facecolor=(sigma_color + [1 - ns / nsigma]))

        if nsigmaoutline:
            # Draw an outline
            ax_calib.plot(eta_plot, curve + nsigma * bands, color='k')
            ax_calib.plot(eta_plot, curve - nsigma * bands, color='k')

        # Plot true omega
        ax_calib.errorbar(x          = eta_points,
                          y          = omega_true,
                          xerr       = [eta_points - binning[:, 0], binning[:, 1] - eta_points],
                          yerr       = [omega_true_lower, omega_true_upper],
                          color      = 'k',
                          fmt        = '.',
                          label      = r"$\omega^{\mathrm{true}}$")
        ax_calib.set_xlabel(r'Predicted mistag $\eta$')
        ax_calib.set_ylabel(r'Measured mistag $\omega$')
        ax_calib.set_xlim(*eta_range)
        ax_calib.set_ylim(*omega_range)

        # Set scales
        if isinstance(x_scale, str) and x_scale != "function":
            ax_calib.set_xscale(x_scale)
        elif isinstance(x_scale, tuple):
            ax_calib.set_xscale('function', functions=x_scale)

        if isinstance(y_scale, str) and y_scale != "function":
            ax_calib.set_yscale(y_scale)
        elif isinstance(y_scale, tuple):
            ax_calib.set_yscale('function', functions=y_scale)

        aspect = (eta_range[1] - eta_range[0]) / (omega_range[1] - omega_range[0])

        ax_calib.set_aspect(aspect)

        if print_params:
            if params_position == "auto":
                textx, texty, text_text = print_fit_setup(ax_calib, [0.65, 0.25], tagger)
            else:
                assert isinstance(params_position, list)
                textx, texty, text_text = print_fit_setup(ax_calib, params_position, tagger)
        else:
            textx = texty = text_text = None

        ax_calib.plot([0, 0.5], [0, 0.5], color='b', linestyle='-', linewidth=0.5, label="Identity")
        ax_calib.legend(loc="upper left")

        if format == "json":
            plot_json_data["curve_eta"]      = list(eta_plot)
            plot_json_data["curve_omega"]    = list(curve)
            plot_json_data["curve_err"]      = list(bands)
            plot_json_data["eta"]            = list(eta_points)
            plot_json_data["omega"]          = list(omega_true)
            plot_json_data["eta_err_left"]   = list(eta_points - binning[:, 0])
            plot_json_data["eta_err_right"]  = list(binning[:, 1] - eta_points)
            plot_json_data["omega_err_high"] = list(omega_true_upper)
            plot_json_data["omega_err_low"]  = list(omega_true_lower)
            plot_json_data["title"]          = title
            plot_json_data["text"]           = [textx, texty, text_text]
            plot_json_data["eta_range"]      = list(eta_range)
            plot_json_data["omega_range"]    = list(omega_range)
            json.dump(plot_json_data, open(os.path.join(savepath, f"{tagger.name}_Calibration.{format}"), "w+"))
        else:
            plt.savefig(os.path.join(savepath, f"{tagger.name}_Calibration.{format}"))
            plt.close()

        return f"{tagger.name}_Calibration.{format}"


def draw_inputcalibration_curve(tagger, nbins=10, eta_range="minimal", omega_range=[0, 0.5], print_params=True, params_position="auto", title=None, samples=100, nsigma=2, sigma_color=[0.7, 0.7, 0.7], nsigmaoutline=False, etabins=100, savepath="."):
    """ Plots the input calibration curve of a loaded tagger including the confidence bands,
        true mistag and binned measured mistag distribution

        :param tagger: TargetTagger object
        :type tagger: TargetTagger
        :param nbins: Number of true mistag bins to plot
        :type nbins: int
        :param eta_range: measured mistag plot range
        :type eta_range: "minimal" or list
        :param omega_range: true mistag range
        :type omega_range: list
        :param print_params: Whether to plot the calibration parameters
        :type print_params: bool
        :param params_position: Text box position
        :type params_position: "auto" or [x, y] pair list
        :param title: Title to use instead of tagger name (default)
        :type title: str
        :param sample: How many curve points to plot (Plotting precision)
        :type sample: int
        :param nsigma: how many sigma intervals to plot
        :type nsigma: int
        :param sigma_color: R,G,B list
        :type sigma_color: list
        :param nsigmaoutline: whether to outline the last sigma interval
        :type nsigmaoutline: bool
        :param etabins: Number of bins for the eta histogram
        :type etabins: int
        :param savepath: Path to the plot folder
        :type savepath: str
    """
    with mpl.rc_context(ftcalib_plotstyle):
        if title is None:
            title = tagger.name + " Input Calibration"

        # Matplotlib
        _, ax_calib = plt.subplots()
        ax_calib.set_title(title)

        if eta_range == "minimal":
            eta = tagger.stats._tagdata.eta
            eta_range = [np.nanmin(eta), 0.5]
            eta_range[0] -= (eta_range[1] - eta_range[0]) * 0.02

        eta_plot = np.linspace(eta_range[0], eta_range[1], samples)  # "Continuous" eta for plotting

        # Plot calibration curve and mean mistag
        curve = calibration_lineshape(tagger, eta_plot)
        ax_calib.plot(eta_plot, curve, color='k', label="Input Calibration", linewidth=0.5)

        # Draw confidence bands
        bandsplus = confidence_bands_lineshape(tagger, eta_plot,  np.ones(samples))
        bandsminus = confidence_bands_lineshape(tagger, eta_plot, -np.ones(samples))
        bands = (bandsplus + bandsminus) / 2

        for ns in reversed(range(nsigma)):
            ax_calib.fill_between(eta_plot, curve - (ns + 1) * bands, curve + (ns + 1) * bands, facecolor=(sigma_color + [1 - ns / nsigma]))

        if nsigmaoutline:
            # Draw an outline
            plt.plot(eta_plot, curve + nsigma * bands, color='k', linewidth=0.05)
            plt.plot(eta_plot, curve - nsigma * bands, color='k', linewidth=0.05)

        ax_calib.set_xlabel(r'Predicted mistag $\eta$')
        ax_calib.set_ylabel(r'Measured mistag $\omega$')
        ax_calib.set_xlim(*eta_range)
        ax_calib.set_ylim(*omega_range)

        if print_params:
            if params_position == "auto":
                print_fit_setup(ax_calib, [0.00, 0.60], tagger)
            else:
                print_fit_setup(ax_calib, params_position, tagger)

        ax_calib.plot([0, 0.5], [0, 0.5], color='b', linestyle=(0, (5, 10)), linewidth=0.5, label="Identity")
        ax_calib.legend(loc="upper left")

        ax_etahist = ax_calib.twinx()
        etacolor = [0, 0, 0]
        ax_etahist.hist(tagger.stats._tagdata.eta, range=eta_range, bins=etabins, density=True, histtype="step", color=etacolor, label=r"$\eta$")
        ax_etahist.set_ylabel(r"$\eta\;/\;" + "{:.2}".format((eta_range[1] - eta_range[0]) / etabins) + "$")
        ax_etahist.tick_params(axis='y', labelcolor='k')
        ax_etahist.set_ylim(0, ax_etahist.get_ylim()[1] * 2)
        ax_etahist.legend(loc="center right")

        plt.savefig(os.path.join(savepath, f"{tagger.name}_InputCalibration.pdf"))
        plt.clf()
        plt.close()
        return f"{tagger.name}_InputCalibration.pdf"
