"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 1.0.0
"""

import pandas as pd
from {{ cookiecutter.python_package }}.utils.plotting import plotTrainingHistory, get_dummy
from {{ cookiecutter.python_package }}.models.{{ cookiecutter.python_package }}_model import {{ cookiecutter.python_package }}


def train_model(
    X_train: pd.DataFrame, y_train: pd.DataFrame, params: dict
) -> pd.DataFrame:
    """Trains a dummy model on some data.

    Args:
        X_train:
        y_train:
        params:
    Returns:
        Trained model.
    """
    params["hps"]["nInputs"] = X_train.shape[-1]
    model = {{ cookiecutter.python_package }}(name=params["hps"]["name"], hps=params["hps"])
    model.train(X_train, y_train)

    f, _ = get_dummy()
    # NOTE: one can also plot the history
    # f, _ = plotTrainingHistory(model.history)

    return model, f
