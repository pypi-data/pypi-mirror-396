""" Main
"""

import logging
import json

from eea.jupyter.controllers.plotly import PlotlyController


plotlyCtrl = PlotlyController()


def upload_plotly(**kwargs):
    """
    Uploads a Plotly figure to a specified API endpoint.

    This function validates the input, initializes the Plotly controller,
    and uploads the Plotly figure to the API. If any step fails, it logs
    an error message.
    """
    err = plotlyCtrl.init(**kwargs)
    if err:
        return logging.error(err)

    fig = kwargs.get("fig", None)

    if not fig:
        return logging.error(
            "Figure must be a Plotly Figure object or a dictionary")

    visualization = fig if isinstance(fig, dict) else json.loads(fig.to_json())

    try:
        err = plotlyCtrl.upload_plotly(visualization=visualization, **kwargs)
        if err:
            return logging.error(err)
    except Exception:
        return logging.exception(
            "Error handling visualization at %s", kwargs.get("url", ""))

    return None


def get_theme(**kwargs):
    """
    Get the theme from the Plotly controller.
    """
    err = plotlyCtrl.init(**kwargs)
    if err:
        return logging.error(err)

    [theme, err] = plotlyCtrl.get_theme(kwargs.get("theme", None))
    if err:
        return logging.error(err)
    return theme


def get_template(**kwargs):
    """
    Get the theme from the Plotly controller.
    """
    err = plotlyCtrl.init(**kwargs)
    if err:
        return logging.error(err)

    [template, err] = plotlyCtrl.get_template(kwargs.get("template", None))
    if err:
        return logging.error(err)
    return template
