"""
This is a boilerplate pipeline 'model_validation'
generated using Kedro 1.0.0
"""

import logging
import pandas as pd
from sklearn.metrics import roc_auc_score


def validated_model(model, X_test: pd.DataFrame, y_test: pd.DataFrame) -> pd.DataFrame:
    """Trains a dummy model on some data.

    Args:
        model:
        X_test:
        y_test:
    Returns:
        Model prediction.
    """
    # get logger for reporting
    logger = logging.getLogger(__name__)

    pred = model.predict(X_test)
    auc = roc_auc_score(y_test, pred)

    logger.info(f"Area under ROC curve: {auc:.4f}")

    return pred
