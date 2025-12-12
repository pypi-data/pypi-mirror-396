import numpy as np
from .FemtoDAQController import FemtoDAQController
from .Loaders.BaseLoader import EventInfo
from typing import Optional, Dict


def quickPlotEvent(
    digitizer: FemtoDAQController,
    event: EventInfo,
    fig_title: Optional[str] = None,
    channel_titles: Dict[int, str] = {},
):
    """generates a matplotlib figure for the event passed in

    .. warning:: requires Matplotlib.

        Matplotlib is not installed by default with skutils.
        Two installation methods are `pip install skutils[dev]` or `pip install matplotlib`

    .. warning:: Queries digitizer for plotting context

        This quickPlotting method

    :param digitizer: The target digitizer. This will be used to grab information for plot context
    :param event: The desired event to plot
    :param fig_title: Title for the figure if desired.
    :param channel_titles: Names for each channel if desired. Keys are channels, values are titles

    :raise ImportError: If matplotlib is not installed
    :raise RuntimeError: If the event passed in does not contain any waveform data
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise RuntimeError("matplotlib must be installed separately to use quickPlotEvent!")

    if not event.has_waves:
        raise RuntimeError("This event contains no waveforms")

    waves = event.wavedata()

    num_samples = waves.shape[0]
    num_channels = waves.shape[1]

    x_position = digitizer.getTriggerXPosition()
    trigger_window_span = (x_position, x_position + digitizer.getTriggerActiveWindow())
    pulse_height_window_span = (x_position, x_position + digitizer.getPulseHeightWindow())

    fig, axes = plt.subplots(num_channels, 1)
    if fig_title:
        fig.suptitle(fig_title)
    fig.tight_layout()
    plt.subplots_adjust(hspace=1.3, bottom=0.25, top=0.82)

    xticks_samples = np.linspace(0, num_samples, 9)

    def samples_to_us(s: int):
        return s * digitizer.clk_period_ns / 1000

    def us_to_samples(t: int):
        return t / digitizer.clk_period_ns * 1000

    ylim_buffer = 0.05 * (waves.max() - waves.min())
    ylim_min = waves.min() - ylim_buffer
    ylim_max = waves.max() + ylim_buffer

    for i in range(num_channels):
        channel = event.channels[i]
        ax = axes[i]
        ax_title = channel_titles.get(channel, f"Channel {channel}")
        ax.set_ylabel(ax_title)

        # Plot waveform
        wave = waves[:, i]
        ax.plot(wave, color="tab:blue")

        # highlight trigger and pulse height windows
        ax.axvspan(*trigger_window_span, color="tab:red", alpha=0.25, hatch="\\", label="Trigger Window")
        ax.axvspan(*pulse_height_window_span, color="tab:green", alpha=0.25, hatch="/", label="Pulse Height Window")

        # configure axis label and tick labels
        ax.set_xticks(xticks_samples, labels=[f"{int(s)}" for s in xticks_samples], rotation=45)
        ax.set_xlabel("samples", labelpad=0.5)
        ax.set_ylim(ylim_min, ylim_max)
        second_ax = ax.secondary_xaxis("top", functions=(samples_to_us, us_to_samples))
        second_ax.set_xlabel("microseconds", labelpad=0.5)
        second_ax.tick_params(rotation=45)

        # mark the min and maximum points
        wavemin_coords = (int(wave.argmin()), int(wave.min()))
        wavemax_coords = (int(wave.argmax()), int(wave.max()))
        ax.scatter(*wavemin_coords, s=11, color="black", marker="x", label="min val")
        ax.scatter(*wavemax_coords, s=11, color="black", marker="+", label="max val")
        ax.annotate(
            f"max={wavemax_coords[1]}",
            xy=wavemax_coords,
            xytext=(20, -10),
            textcoords="offset pixels",
            ha="left",
            va="center",
            arrowprops=dict(facecolor="black", arrowstyle="->"),
        )
        ax.annotate(
            f"min={wavemin_coords[1]}",
            xy=wavemin_coords,
            xytext=(-20, 10),
            textcoords="offset pixels",
            ha="right",
            va="center",
            arrowprops=dict(facecolor="black", arrowstyle="->"),
        )

        # Add pulse summary text on the right
        cd = event.channel_data[i]
        pulse_summary_data = (
            "Pulse Summary:\n"
            f"channel                   = {cd.channel}\n"
            f"pulse height (filtered)   = {cd.pulse_height}\n"
            f"trigger fired             = {'true' if cd.triggered else 'false'}\n"
            f"trigger height (filtered) = {cd.trigger_height}\n"
            f"trigger multiplicity      = {cd.trigger_multiplicity}\n"
            # f"waveform min coordinates  = {wavemin_coords}\n"
            # f"waveform max coordinates  = {wavemax_coords}\n"
        )

        # BEGIN DEBUGGING
        # ph_locations = np.where(wave.flatten() == cd.pulse_height)
        # ax.scatter(ph_locations, wave.flat[ph_locations], s=14, marker='X', color='m', label='points equal to pulse height')
        # END DEBUGGING

        # place markers at minimum and maximum points
        ax.annotate(
            pulse_summary_data,
            (1.05, 0),
            xycoords="axes fraction",
            font="monospace",
            fontsize=10,
        )

        is_first_channel = i == 0
        if is_first_channel:
            pass
        # Last channel conditions
        is_last_channel = i + 1 == num_channels
        if is_last_channel:
            # Add in legend for all plots at the bottom right
            ax.legend(loc="upper right", bbox_to_anchor=(1.4, 0), ncol=1, fancybox=True)
            # make the top axis in us
            # ax.tick_params(top=False, labeltop=False, bottom=True, labelbottom=True)
            # ax.xaxis.set_label_position('bottom')

    return fig
