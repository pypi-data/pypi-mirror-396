import numpy as np
import awkward as ak
from sklearn.metrics import roc_curve
from scipy import interpolate
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import shap


def set_global_plotting_settings():
    plt.style.use(hep.style.ROOT)

    # there is a super strange hack here:
    # you need to create a plot, and then only the second (and following) ones have the correct text sizes
    # if there is any better solution for this, let me know!
    fig = plt.figure()
    matplotlib.rcParams.update({"font.size": 26})
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    plt.close()


# a collection of plotting functions


# helper function to have a central definition of the total L1 rate
def totalMinBiasRate():
    LHCfreq = 11245.6
    nCollBunch = 2544

    return LHCfreq * nCollBunch / 1e3  # in kHz


# helper function to get best triggers for a signal
def getBestTriggers(bits, n_best):
    count_fires = ak.to_pandas(ak.sum(bits, axis=0))
    best_columns = count_fires.T[0].sort_values(ascending=False)[:n_best].index.values

    return best_columns


# a helper wrapper around the sklearn roc_curve method to handle multiple inputs at the same time
# expected return is fpr, tpr and thr
# where in the case of kfolding, the tpr will be a list with [mean, std]
def roc_curve_handlekfold(y_true, y_pred, weights):
    if isinstance(y_true, list) and isinstance(y_pred, list):
        # first calculating ROC curve for all examples
        fprs = []
        tprs = []
        thrs = []
        for y_true_one, y_pred_one, weights_one in zip(y_true, y_pred, weights):
            fpr_this, tpr_this, thr_this = roc_curve(
                y_true_one,
                y_pred_one,
                drop_intermediate=False,
                sample_weight=weights_one,
            )

            fprs.append(fpr_this)
            tprs.append(tpr_this)
            thrs.append(thr_this)

        # ensuring that we have the same thresholds everywhere
        new_tprs = []
        for fpr, tpr in zip(fprs, tprs):
            func = interpolate.interp1d(
                fpr, tpr, kind="linear", bounds_error=False, fill_value=0
            )
            new_tprs.append(func(fprs[0]))  # just using the first as our baseline

        new_tprs = np.asarray(new_tprs)

        # now we know that these are in agreement, we can get mean and std
        tpr_mean = np.mean(new_tprs, axis=0)
        tpr_std = np.std(new_tprs, axis=0)

        return fprs[0], [tpr_mean, tpr_std], thrs[0]

    else:
        return roc_curve(y_true, y_pred, drop_intermediate=False, sample_weight=weights)


# function to calculate the pure rate
def roc_curve_pure(
    y_true, y_pred, other, FPRpure=True, TPRpure=True, verbosity=0, weights=None
):
    assert len(y_true) == len(y_pred) == len(other)
    if (not FPRpure) and (not TPRpure):
        raise Exception(
            "pureROC: make at least one of FPR or TPR pure, or don't use this."
        )

    # all following stuff needs to also work if we are kfolding!
    if (
        isinstance(y_true, list)
        and isinstance(y_pred, list)
        and isinstance(other, list)
    ):
        y_pred_copy = []

        for y_true_one, y_pred_one, other_one in zip(y_true, y_pred, other):
            y_pred_copy_one = y_pred_one.copy()

            # first, we assume everything that is already triggered by "other" is not triggered here -> setting to -1
            if FPRpure:
                mask = other_one & (y_true_one == 0)
                y_pred_copy_one[mask] = 0
            if TPRpure:
                mask = other_one & (y_true_one == 1)
                y_pred_copy_one[mask] = 0

            y_pred_copy.append(y_pred_copy_one)

    else:
        # we'll construct a new prediction that gives the "pure FPR" and "pure TPR", whatever that is :D
        y_pred_copy = y_pred.copy()

        # first, we assume everything that is already triggered by "other" is not triggered here -> setting to -1
        if FPRpure:
            mask = other & (y_true == 0)
            y_pred_copy[mask] = 0
        if TPRpure:
            mask = other & (y_true == 1)
            y_pred_copy[mask] = 0

    fpr_pure, tpr_pure, thr_pure = roc_curve_handlekfold(
        y_true, y_pred_copy, weights=weights
    )

    return fpr_pure, tpr_pure, thr_pure


# Flexible function to plot ROC curves
# Minimal input are y_values for model prediction and the corresponding truth values
# FPR and TPR modes allow two main options: pure and rate / total (only for FPR / tpr)
# for this to work, a pureReference must be passed!
def plotROC(
    y_true,
    y_pred,
    weights=None,
    FPRmode="normal",
    TPRmode="normal",
    pureReference=None,
    drawBandIfKfold=True,
    ax=None,
    verbosity=0,
    **kwargs,
):
    if not ax:
        f, ax = plt.subplots()

    if "total" in TPRmode and not "pure" in TPRmode:
        if verbosity > 0:
            print(
                "You want to plot a total efficiency. This always need to be handled 'pure' for the NN relative to the trigger to combine with, so the option pure is implicitely added. You can suppress this warning by adding 'pure' to your TPRmode manually."
            )
        TPRmode += " pure"

    # assure that a pureReference is given if a mode requires pure
    if ("pure" in FPRmode) or ("pure" in TPRmode):
        if weights == None and isinstance(
            y_true, list
        ):  # Necessary to handle kfold. Need a None for each fold
            weights_None = [None for _ in y_true]
            fpr, tpr, thr = roc_curve_pure(
                y_true,
                y_pred,
                pureReference,
                FPRpure=("pure" in FPRmode),
                TPRpure=("pure" in TPRmode),
                weights=weights_None,
            )
        # if pureReference == None: raise Exception("If FPR mode or TPR mode contains pure, please pass a pureReference!")
        else:
            fpr, tpr, thr = roc_curve_pure(
                y_true,
                y_pred,
                pureReference,
                FPRpure=("pure" in FPRmode),
                TPRpure=("pure" in TPRmode),
                weights=weights,
            )
    else:
        if weights == None and isinstance(
            y_true, list
        ):  # Necessary to handle kfold. Need a None for each fold
            weights_None = [None for _ in y_true]
            fpr, tpr, thr = roc_curve_handlekfold(y_true, y_pred, weights=weights_None)
        else:
            fpr, tpr, thr = roc_curve_handlekfold(y_true, y_pred, weights=weights)

    # if we want to consider rate, scale the y axis
    if "rate" in FPRmode:
        fpr *= totalMinBiasRate()

    # handle potential total rate
    if "total" in TPRmode:
        if isinstance(y_true, list) and isinstance(pureReference, list):
            efficiencies = []
            for y_true_one, pureReference_one in zip(y_true, pureReference):
                efficiencies.append(
                    np.count_nonzero(pureReference_one[y_true_one == 1])
                    / len(pureReference_one[y_true_one == 1])
                )
            efficiency = np.mean(np.asarray(efficiencies))

            tpr[0] += efficiency

        else:
            efficiency = np.count_nonzero(pureReference[y_true == 1]) / len(
                pureReference[y_true == 1]
            )
            tpr += efficiency

        if verbosity > 0:
            print(
                "Added a cutbased efficiency of " + str(efficiency) + " to the curve."
            )

    # now do the plotting
    if isinstance(tpr, list):  # kfold
        same_color = ax.plot(fpr, tpr[0], **kwargs)[0].get_color()
        if drawBandIfKfold:
            ax.fill_between(
                fpr, tpr[0] + tpr[1], tpr[0] - tpr[1], alpha=0.5, color=same_color
            )
    else:
        ax.plot(fpr, tpr, **kwargs)

    # and styling
    ylabel = "Signal efficiency"
    if "rate" in FPRmode:
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 1)
        xlabel = "L1 rate [kHz]"
    else:
        ax.set_xscale("log")
        ax.set_yscale("log")
        plt.plot([0, 1], [0, 1], "k--")
        xlabel = "Background efficiency"

    ax.set_ylabel

    if "pure" in FPRmode:
        xlabel += " (pure)"
    if "pure" in TPRmode:
        ylabel += " (pure)"

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.grid(True)


def plotTrigger(
    bits,
    y_test,
    weights=None,
    mode="point",
    FPRmode="normal",
    TPRmode="normal",
    pureReference=None,
    ax=None,
    verbosity=0,
    **kwargs,
):
    # first, split datasets into parts
    y_test = np.asarray(y_test).astype(bool)
    bits_sig = bits[y_test]
    bits_bkg = bits[np.logical_not(y_test)]
    if np.all(weights) != None:
        weights_sig = weights[y_test]
        weights_bkg = weights[np.logical_not(y_test)]
    assert len(bits) == len(bits_sig) + len(bits_bkg)

    # calculating fpr and tpr
    if np.all(weights) == None:
        fpr = ak.sum(bits_bkg) / len(bits_bkg)
        tpr = ak.sum(bits_sig) / len(bits_sig)
    else:
        fpr = ak.sum(np.array(weights_bkg)[bits_bkg]) / np.sum(weights_bkg)
        tpr = ak.sum(np.array(weights_sig)[bits_sig]) / np.sum(weights_sig)

    plotROCpoint(
        fpr,
        tpr,
        mode=mode,
        FPRmode=FPRmode,
        TPRmode=TPRmode,
        pureReference=pureReference,
        ax=ax,
        verbosity=verbosity,
        **kwargs,
    )


# stolen from https://stackoverflow.com/questions/29321835/is-it-possible-to-get-color-gradients-under-curve-in-matplotlib
# with some changes. Will be used in the function below
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon


def gradient_fill(x, y, fill_color=None, ax=None, **kwargs):
    """
    Plot a line with a linear alpha gradient filled beneath it.

    Parameters
    ----------
    x, y : array-like
        The data values of the line.
    fill_color : a matplotlib color specifier (string, tuple) or None
        The color for the fill. If None, the color of the line will be used.
    ax : a matplotlib Axes instance
        The axes to plot on. If None, the current pyplot axes will be used.
    Additional arguments are passed on to matplotlib's ``plot`` function.

    Returns
    -------
    line : a Line2D instance
        The line plotted.
    im : an AxesImage instance
        The transparent gradient clipped to just the area beneath the curve.
    """
    if ax is None:
        ax = plt.gca()

    (line,) = ax.plot(x, y, **kwargs)
    if fill_color is None:
        fill_color = line.get_color()

    zorder = line.get_zorder()
    alpha = line.get_alpha()
    alpha = 1.0 if alpha is None else alpha

    z = np.empty((100, 1, 4), dtype=float)
    rgb = mcolors.colorConverter.to_rgb(fill_color)
    z[:, :, :3] = rgb
    z[:, :, -1] = np.linspace(0, alpha, 100)[:, None]

    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    ymin -= 0.2
    im = ax.imshow(
        z, aspect="auto", extent=[xmin, xmax, ymin, ymax], origin="lower", zorder=zorder
    )

    xy = np.column_stack([x, y])
    xy = np.vstack([[xmin, ymin], xy, [xmax, ymin], [xmin, ymin]])
    clip_path = Polygon(xy, facecolor="none", edgecolor="none", closed=True)
    ax.add_patch(clip_path)
    im.set_clip_path(clip_path)

    return line, im


# Method to plot the result of a single trigger
def plotROCpoint(
    fpr,
    tpr,
    mode="point",
    FPRmode="normal",
    TPRmode="normal",
    pureReference=None,
    ax=None,
    verbosity=0,
    **kwargs,
):
    if not ax:
        f, ax = plt.subplots()

    if "rate" in FPRmode:
        fpr *= totalMinBiasRate()

    if ("pure" in FPRmode) or ("pure" in TPRmode):
        raise Exception("Pure rate/efficiency not yet implemented for trigger plotting")

    # plotting...
    if mode == "line":
        gradient_fill(np.asarray([0, 9999999]), np.asarray([tpr, tpr]), ax=ax, **kwargs)
    else:
        ax.plot(fpr, tpr, "o", **kwargs)

    # and styling
    xlabel = ""
    ylabel = "Signal efficiency"
    if "rate" in FPRmode:
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 1)
        xlabel = "L1 rate [kHz]"
    else:
        ax.set_xscale("log")
        ax.set_yscale("log")
        plt.plot([0, 1], [0, 1], "k--")
        xlabel = "Background efficiency"

    ax.set_ylabel

    if "pure" in FPRmode:
        xlabel += " (pure)"
    if "pure" in TPRmode:
        ylabel += " (pure)"

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.grid(True)


# histogram plotting function, for example to compare situation before/after trigger
def plotHist(
    data,
    bins=10,
    weights=None,
    interval=None,
    logy=False,
    logx=False,
    density=False,
    ax=None,
    divide_by_bin_width=False,
    verbosity=0,
    **kwargs,
):
    if not ax:
        fig, ax = plt.subplots()

    # convert awkward array to numpy array, if needed
    try:
        data_np = ak.flatten(data).to_numpy()
    except:
        data_np = data

    # creating histogram from data
    hist_data, hist_edges = np.histogram(
        data_np, bins=bins, range=interval, density=density, weights=weights
    )

    if divide_by_bin_width:
        bin_widths = np.diff(hist_edges)
        assert hist_data.shape == bin_widths.shape
        hist_data = hist_data / bin_widths

    # plotting the histogram
    hep.histplot(hist_data, hist_edges, ax=ax, **kwargs)
    if logy:
        ax.set_yscale("log")
    if logx:
        ax.set_xscale("log")

    ax.set_ylabel("events")
    if density:
        ax.set_ylabel("events / total events")


def plotEfficiency(
    efficiency, bins, error, logy=False, logx=False, ax=None, verbosity=0, **kwargs
):
    if not ax:
        fig, ax = plt.subplots()

    # plotting the histogram
    hep.histplot(efficiency, bins, yerr=error, ax=ax, **kwargs)
    if logy:
        ax.set_yscale("log")
    if logx:
        ax.set_xscale("log")

    ax.set_ylabel("efficiency")


def plotRateVsLumi(triggerResults, runInfo, interval=100, verbosity=0, **kwargs):
    raise Exception("Rate vs. lumi is not implemented yet!")


def plotStability(
    triggerResults, runInfo=None, interval=100, ax=None, verbosity=0, **kwargs
):
    # a function to plot the stability of some trigger

    if not runInfo:
        # just do a stability plot with a fixed interval
        # if a runInfo object is passed, call plotRateVsLumi instead

        # we'll average the dataframe entries. first, convert to numpy
        np_triggerResults = triggerResults.to_numpy()

        # for the following to work, we need to assure that the length is dividable by the desired interval
        nLastElements = len(triggerResults) % interval
        nBlocks = int(len(np_triggerResults) / interval)

        if verbosity > 1:
            print(
                "Found "
                + str(nBlocks)
                + " blocks with "
                + str(nLastElements)
                + " leftover events"
            )

        # split events to handle leftovers later
        # (some code improvement might be possible here)
        np_lastElements = np_triggerResults[len(np_triggerResults) - nLastElements :]
        np_triggerResults = np_triggerResults[: len(np_triggerResults) - nLastElements]

        # block the results
        np_triggerResults_blocked = np_triggerResults.reshape(nBlocks, interval)

        # calculate passed events along axis
        np_passedEvents = np.sum(np_triggerResults_blocked.astype("int"), axis=1)
        if nLastElements > 0:
            np_passedEventsLeftovers = np.sum(np_lastElements)

        # calculate efficiency & get bin edges
        np_efficiency = np_passedEvents / interval
        binEdges = np.arange(0, (len(np_efficiency) + 1) * interval, interval)

        # handle if there are leftovers
        if nLastElements > 0:
            np_efficiency = np.append(
                np_efficiency, np_passedEventsLeftovers / nLastElements
            )
            binEdges = np.append(binEdges, len(triggerResults))

        if not ax:
            fig, ax = plt.subplots(figsize=(20, 8))

        # plotting
        hep.histplot(
            np_efficiency, binEdges, label=triggerResults.name, ax=ax, **kwargs
        )

        # styling
        ax.set_ylabel("efficiency")
        ax.set_xlabel("event")
        ax.set_xlim(0, len(triggerResults))
        ax.ticklabel_format(style="plain")

        return np_efficiency
    else:
        return plotRateVsLumi(triggerResults, runInfo, interval=interval, **kwargs)


# plotting function for a generic training history
def plotTrainingHistory(history, metrics=["loss", "accuracy"], f=None, axs=None):
    # creating the plot
    if not f and not axs:
        f, axs = plt.subplots(
            len(metrics), 1, figsize=(12, 4 * len(metrics)), sharex=True
        )
    if len(metrics) == 1:
        axs = [axs]
    plt.subplots_adjust(wspace=0, hspace=0)

    # labeling
    hep.cms.label("private work", data=False, ax=axs[0])

    for i in range(len(metrics)):
        metric = metrics[i]
        ax = axs[i]
        ax.set_ylabel(metric)

        if isinstance(history, list):  # handle kfold
            for foldi in range(len(history)):
                ax.plot(history[foldi].history[metric], color="C{}".format(foldi))
                ax.plot(
                    history[foldi].history["val_" + metric],
                    color="C{}".format(foldi),
                    linestyle="--",
                )

            (la2,) = ax.plot([0, 0], [0, 0], color="Grey")
            (lb2,) = ax.plot([0, 0], [0, 0], color="Grey", linestyle="--")
            ax.legend([la2, lb2], ["training", "validation"])
        else:
            ax.plot(history.history[metric], label="training")
            ax.plot(history.history["val_" + metric], label="validation")
            ax.legend()

    axs[-1].set_xlabel("Epoch")

    return f, axs


# plotting function for shapley feature importance
# make sure that len(x) > 1100 if you use the default n_* values!
def plot_feature_importance(
    model, x, n_fit=1000, n_explain=100, feature_names=None, show=False
):
    explainer = shap.DeepExplainer(model, x[0:n_fit])

    # explain the first 100 predictions
    # explaining each prediction requires 2 * background dataset size runs
    shap_values = explainer.shap_values(x[n_fit : n_fit + n_explain])
    shap.summary_plot(
        shap_values, feature_names=feature_names, max_display=x.shape[1], show=show
    )

def get_dummy():
    return plt.subplots()
