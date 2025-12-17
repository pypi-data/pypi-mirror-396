"""
This is a boilerplate pipeline 'model_validation'
generated using Kedro 1.0.0
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import validated_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=validated_model,
                inputs=[
                    "train_model",
                    "processed_{{ cookiecutter.python_package }}_X_test",
                    "processed_{{ cookiecutter.python_package }}_y_test",
                ],
                outputs="model_pred",
                name="validated_model_node",
            )
        ]
    )
