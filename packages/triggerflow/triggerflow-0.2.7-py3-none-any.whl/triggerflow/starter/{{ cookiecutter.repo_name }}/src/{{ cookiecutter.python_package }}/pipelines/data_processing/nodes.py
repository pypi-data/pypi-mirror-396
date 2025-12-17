"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 1.0.0
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def data_processing(
    data: pd.DataFrame, random_state: int, test_size: float
) -> pd.DataFrame:
    """Preprocesses some data.

    Args:
        data: Raw data.
        random_state:
    Returns:
        X_train:
        X_test:
        y_train:
        y_test:
        event_ids:
        scaler:
    """
    y = data["y"].to_frame()
    event_ids = data["event"].to_frame()
    X = data.drop(columns=["y", "event"])

    # Normalize features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)

    # Split into training and test sets
    X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
        X_scaled, y, event_ids, test_size=test_size, random_state=random_state
    )

    return X_train, X_test, y_train, y_test, scaler, ids_train, ids_test
