"""
This is a boilerplate pipeline 'model_training'
generated using Kedro 1.0.0
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import load_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=load_data,
                inputs=["{{ cookiecutter.python_package }}_data", "{{ cookiecutter.python_package }}_meta_data"],
                outputs=["{{ cookiecutter.python_package }}_data_loaded", "{{ cookiecutter.python_package }}_meta_data_loaded"],
                name="load_data",
            )
        ]
    )
