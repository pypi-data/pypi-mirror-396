# trigger_mlflow.py
import datetime
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient

from .core import TriggerModel

logger = logging.getLogger(__name__)


def setup_mlflow(
        mlflow_uri: str = None,
        web_eos_url: str = None,
        web_eos_path: str = None,
        model_name: str = None,
        experiment_name: str = None,
        run_name: str = None,
        experiment_id: str = None,
        run_id: str = None,
        creat_web_eos_dir: bool = False,
        save_env_file: bool = False,
        auto_configure: bool = False
    ):

    # Set the MLflow tracking URI
    if mlflow_uri is None:
        mlflow_uri = os.getenv('MLFLOW_URI', 'https://ngt.cern.ch/models')
    mlflow.set_tracking_uri(mlflow_uri)
    os.environ["MLFLOW_URI"] = mlflow_uri
    logger.info(f"Using MLflow tracking URI: {mlflow_uri}")

    # Set the model name
    if model_name is None:
        if os.getenv('MLFLOW_MODEL_NAME'):
            model_name = os.getenv('MLFLOW_MODEL_NAME')
        else:
            model_name = os.getenv('CI_COMMIT_BRANCH', 'Test-Model')
    os.environ["MLFLOW_MODEL_NAME"] = model_name
    logger.info(f"Using model name: {model_name}")


    # Set the experiment name
    if experiment_name is None:
        if os.getenv('MLFLOW_EXPERIMENT_NAME'):
            experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME')
        else:
            experiment_name = os.getenv('CI_COMMIT_BRANCH', 'Test-Training-Torso')
    os.environ["MLFLOW_EXPERIMENT_NAME"] = experiment_name
    logger.info(f"Using experiment name: {experiment_name}")


    # Set the run name
    if run_name is None:
        if os.getenv('CI') == 'true':
            if os.getenv('CI_PARENT_PIPELINE_ID'):
                run_name = f"{os.getenv('CI_PARENT_PIPELINE_ID')}-{os.getenv('CI_PIPELINE_ID')}"
            else:
                run_name = f"{os.getenv('CI_PIPELINE_ID')}"
        else:
            run_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.environ["MLFLOW_RUN_NAME"] = run_name
    logger.info(f"Using run name: {run_name}")


    # Create a new experiment or get the existing one
    if experiment_id is None:
        if os.getenv("MLFLOW_EXPERIMENT_ID"):
            experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID")
        else:
            try:
                experiment_id = mlflow.create_experiment(experiment_name)
            except mlflow.exceptions.MlflowException:
                experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id

    check_experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    if str(check_experiment_id) != str(experiment_id):
        raise ValueError(f"Provided experiment_id {experiment_id} does not match the ID of experiment_name {experiment_name} ({check_experiment_id})")

    # if mlflow.get_experiment_by_name(experiment_name).experiment_id is None:
    #     experiment_id = mlflow.create_experiment(experiment_name)
    # else:
    #     experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id

    mlflow.set_experiment(experiment_id=experiment_id)
    os.environ["MLFLOW_EXPERIMENT_ID"] = experiment_id
    logger.info(f"Using experiment ID: {experiment_id}")


    # Start a new MLflow run
    if run_id is None:
        if os.getenv("MLFLOW_RUN_ID"):
            run_id = os.getenv("MLFLOW_RUN_ID")
        else:
            with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
                run_id = run.info.run_id

    check_run_info = mlflow.get_run(run_id)
    if str(check_run_info.info.experiment_id) != str(experiment_id):
        raise ValueError(f"Provided run_id {run_id} does not belong to experiment_id {experiment_id} (found {check_run_info.info.experiment_id})")

    os.environ["MLFLOW_RUN_ID"] = run_id
    logger.info(f"Started run with ID: {run_id}")


    if creat_web_eos_dir:
        # Set the web_eos_url
        if web_eos_url is None:
            web_eos_url = os.getenv('WEB_EOS_URL', 'https://ngt-modeltraining.web.cern.ch/')
        os.environ["WEB_EOS_URL"] = web_eos_url
        logger.info(f"Using WEB_EOS_URL: {web_eos_url}")

        # Set the web_eos_path
        if web_eos_path is None:
            web_eos_path = os.getenv('WEB_EOS_PATH', '/eos/user/m/mlflowngt/backend/www')
        os.environ["WEB_EOS_PATH"] = web_eos_path
        logger.info(f"Using WEB_EOS_PATH: {web_eos_path}")

        # Create WebEOS experiment dir
        web_eos_experiment_dir = os.path.join(web_eos_path, experiment_name, run_name)
        web_eos_experiment_url = os.path.join(web_eos_url, experiment_name, run_name)
        os.makedirs(web_eos_experiment_dir, exist_ok=True)
        logger.info(f"Created WebEOS experiment directory: {web_eos_experiment_dir}")
        logger.info(f"Using WebEOS experiment URL: {web_eos_experiment_url}")

    else:
        web_eos_url=None
        web_eos_path=None
        web_eos_experiment_dir=None
        web_eos_experiment_url=None


    # Save environment variables to a file for later steps in CI/CD pipelines
    if save_env_file and os.getenv("CI") == "true":
        logger.info(f"Saving MLflow environment variables to {os.getenv('CI_ENV_FILE', 'mlflow.env')}")
        with open(os.getenv('CI_ENV_FILE', 'mlflow.env'), 'a') as f:
            f.write(f"MLFLOW_URI={mlflow_uri}\n")
            f.write(f"MLFLOW_MODEL_NAME={model_name}\n")
            f.write(f"MLFLOW_EXPERIMENT_NAME={experiment_name}\n")
            f.write(f"MLFLOW_RUN_NAME={run_name}\n")
            f.write(f"MLFLOW_EXPERIMENT_ID={experiment_id}\n")
            f.write(f"MLFLOW_RUN_ID={run_id}\n")

            if creat_web_eos_dir:
                f.write(f"WEB_EOS_URL={web_eos_url}\n")
                f.write(f"WEB_EOS_PATH={web_eos_path}\n")
                f.write(f"WEB_EOS_EXPERIMENT_DIR={web_eos_experiment_dir}\n")
                f.write(f"WEB_EOS_EXPERIMENT_URL={web_eos_experiment_url}\n")

            if auto_configure:
                logger.info("Auto_configure is set to true. Exporting AUTO_CONFIGURE=true")
                f.write("AUTO_CONFIGURE=true\n")

    return {
        "experiment_name": experiment_name,
        "run_name": run_name,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "mlflow_uri": mlflow_uri,
        "model_name": model_name,
        "web_eos_url": web_eos_url,
        "web_eos_path": web_eos_path,
        "web_eos_experiment_dir": web_eos_experiment_dir,
        "web_eos_experiment_url": web_eos_experiment_url,
    }

if os.getenv("AUTO_CONFIGURE") == "true":
    logger.info("AUTO_CONFIGURE is true and running in CI environment. Setting up mlflow...")
    setup_mlflow()
else:
    logger.info("AUTO_CONFIGURE is not set. Skipping mlflow run setup")

class MLflowWrapper(mlflow.pyfunc.PythonModel):
    """PyFunc wrapper for TriggerModel; backend can be set at runtime."""
    def load_context(self, context):
        archive_path = Path(context.artifacts["triggerflow"])
        self.model = TriggerModel.load(archive_path)
        self.backend = "software"

    def predict(self, context, model_input):
        if self.backend == "software":
            return self.model.software_predict(model_input)
        elif self.backend == "qonnx":
            if self.model.model_qonnx is None:
                raise RuntimeError("QONNX model not available.")
            return self.model.qonnx_predict(model_input)
        elif self.backend == "firmware":
            if self.model.firmware_model is None:
                raise RuntimeError("Firmware model not available.")
            return self.model.firmware_predict(model_input)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def get_model_info(self):
        if hasattr(self.model, "get_model_info"):
            return self.model.get_model_info()
        return {"error": "Model info not available"}


def _get_pip_requirements(triggerflow: TriggerModel) -> list:
    requirements = ["numpy"]
    if triggerflow.ml_backend == "keras":
        requirements.extend(["tensorflow", "keras"])
    elif triggerflow.ml_backend == "xgboost":
        requirements.append("xgboost")
    if triggerflow.compiler == "hls4ml":
        requirements.append("hls4ml")
    elif triggerflow.compiler == "conifer":
        requirements.append("conifer")
    if hasattr(triggerflow, "model_qonnx") and triggerflow.model_qonnx is not None:
        requirements.append("qonnx")
    return requirements


def log_model(triggerflow: TriggerModel, registered_model_name: str, artifact_path: str = "TriggerModel"):
    """Log a TriggerModel as a PyFunc model and register it in the Model Registry."""
    if not registered_model_name:
        if not os.getenv("MLFLOW_MODEL_NAME"):
            raise ValueError("registered_model_name must be provided and non-empty")
        else:
            registered_model_name = os.getenv("MLFLOW_MODEL_NAME")

    if mlflow.active_run() is None:
        raise RuntimeError("No active MLflow run. Start a run before logging.")

    run = mlflow.active_run()
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / "triggermodel.tar.xz"
        triggerflow.save(archive_path)

        mlflow.pyfunc.log_model(
            artifact_path=artifact_path,
            python_model=MLflowWrapper(),
            artifacts={"triggerflow": str(archive_path)},
            pip_requirements=_get_pip_requirements(triggerflow)
        )

        # register model (always required)
        client = MlflowClient()
        model_uri = f"runs:/{run.info.run_id}/{artifact_path}"
        try:
            client.get_registered_model(registered_model_name)
        except mlflow.exceptions.RestException:
            client.create_registered_model(registered_model_name)
        client.create_model_version(
            name=registered_model_name,
            source=model_uri,
            run_id=run.info.run_id
        )

def load_model(model_uri: str) -> mlflow.pyfunc.PyFuncModel:
    return mlflow.pyfunc.load_model(model_uri)


def load_full_model(model_uri: str) -> TriggerModel:
    local_path = mlflow.artifacts.download_artifacts(model_uri)
    archive_path = Path(local_path) / "triggerflow" / "triggermodel.tar.xz"
    return TriggerModel.load(archive_path)


def get_model_info(model_uri: str) -> dict[str, Any]:
    model = mlflow.pyfunc.load_model(model_uri)
    if hasattr(model._model_impl, "get_model_info"):
        return model._model_impl.get_model_info()
    return {"error": "Model info not available"}
