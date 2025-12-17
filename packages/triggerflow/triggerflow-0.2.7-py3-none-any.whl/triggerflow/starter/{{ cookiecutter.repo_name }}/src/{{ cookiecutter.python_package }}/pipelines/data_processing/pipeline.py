"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 1.0.0
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import data_processing


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=data_processing,
                inputs=["{{ cookiecutter.python_package }}_data_loaded", "params:random_state", "params:test_size"],
                outputs=[
                    "processed_{{ cookiecutter.python_package }}_X_train",
                    "processed_{{ cookiecutter.python_package }}_X_test",
                    "processed_{{ cookiecutter.python_package }}_y_train",
                    "processed_{{ cookiecutter.python_package }}_y_test",
                    "scaler",
                    "event_ids_train",
                    "event_ids_test",
                ],
                name="data_processing_{{ cookiecutter.python_package }}_node",
            )
        ]
    )
