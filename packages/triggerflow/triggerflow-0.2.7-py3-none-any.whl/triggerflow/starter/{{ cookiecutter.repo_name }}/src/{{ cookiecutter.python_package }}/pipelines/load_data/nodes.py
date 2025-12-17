"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 1.0.0
"""

import logging
import pandas as pd
from glob import glob


def load_data({{ cookiecutter.python_package }}_data: pd.DataFrame, meta_data: dict) -> list[dict, pd.DataFrame]:
    return {{ cookiecutter.python_package }}_data, meta_data
