"""
This is a boilerplate pipeline 'compile'
generated using Kedro 1.0.0
"""

import logging
import pandas as pd
from triggerflow.core import TriggerModel
from sklearn.metrics import roc_auc_score


def compile_model(
    model, X_test: pd.DataFrame, y_test: pd.DataFrame, config: dict
) -> pd.DataFrame:
    """Compiles the model and runs some further checks.

    Args:
        model:
        X_test:
        y_test:
        config:
    Returns:
        Model prediction.
    """
    # get logger for reporting
    logger = logging.getLogger(__name__)

    triggerflow = TriggerModel(
        name=config["name"],
        ml_backend=config["ml_backend"],
        compiler=config["compiler"],
        model=model,
        # compiler_config or None
        compiler_config=None,
    )
    triggerflow()

    output_software = triggerflow.software_predict(X_test)
    output_firmware = triggerflow.firmware_predict(X_test)
    output_qonnx = triggerflow.qonnx_predict(X_test)

    auc_software = roc_auc_score(y_test, output_software)
    auc_firmware = roc_auc_score(y_test, output_firmware)
    auc_qonnx = roc_auc_score(y_test, output_qonnx)

    logger.info(f"Area under ROC curve Software: {auc_software:.4f}")
    logger.info(f"Area under ROC curve Firmware: {auc_firmware:.4f}")
    logger.info(f"Area under ROC curve QONNX: {auc_qonnx:.4f}")

    return triggerflow, [auc_software, auc_firmware, auc_qonnx]
