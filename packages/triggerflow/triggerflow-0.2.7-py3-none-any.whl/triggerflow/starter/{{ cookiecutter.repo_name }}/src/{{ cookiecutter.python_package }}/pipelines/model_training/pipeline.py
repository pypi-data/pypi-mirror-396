"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 1.0.0
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import train_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=train_model,
                inputs=[
                    "processed_{{ cookiecutter.python_package }}_X_train",
                    "processed_{{ cookiecutter.python_package }}_y_train",
                    "params:{{ cookiecutter.python_package }}_model",
                ],
                outputs=["train_model", "training_history"],
                name="train_model_node",
            )
        ]
    )
