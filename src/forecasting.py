import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

def add_time_feature(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["hour"] = df["datetime"].dt.hour
    df["day"] = df["datetime"].dt.day
    df["month"] = df["datetime"].dt.month
    df["weekday"] = df["datetime"].dt.weekday
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)

    return df


def add_lag_features(
        df: pd.DataFrame,
        target_column: str = "consumption_kwh",
        lags: list[int] | None = None
) -> pd.DataFrame:
    
    df = df.copy()

    if lags is None:
        lags = [1, 24]
    
    for lag in lags:
        df[f"{target_column}_lag_{lag}"] = df[target_column].shift(lag)

    df = df.dropna().reset_index(drop=True)

    return df


def prepare_forecasting_dataset(
        df: pd.DataFrame,
        target_column: str = "consumption_kwh"
) -> tuple[pd.DataFrame, pd.Series]:
    
    df = add_time_feature(df)

    df = add_lag_features(
        df, 
        target_column=target_column,
        lags=[1,24]
    )

    feature_columns = [
        "hour",
        "day",
        "month",
        "weekday",
        "is_weekend",
        f"{target_column}_lag_1",
        f"{target_column}_lag_24"
    ]

    X = df[feature_columns]
    y = df[target_column]

    return X, y


def split_train_test_by_time(
        X: pd.DataFrame,
        y: pd.Series,
        test_size_ratio: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    split_index = int(len(X) * (1-test_size_ratio))

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test

def train_random_forest_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    random_state: int = 42
) -> RandomForestRegressor:
    
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state
    )

    model.fit(X_train, y_train)

    return model

def evaluate_forecast(
        y_true: pd.Series,
        y_pred
) -> dict[str, float]:
    
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = mse ** 0.5

    return {
        "mae": mae,
        "rmse": rmse
    }

def run_consumption_forecast(
        df: pd.DataFrame,
        target_column: str = "consumption_kwh",
        test_size_ratio: float = 0.2
) -> dict:
    
    X, y = prepare_forecasting_dataset(
        df,
        target_column=target_column
    )

    X_train, X_test, y_train, y_test = split_train_test_by_time(
        X,
        y,
        test_size_ratio=test_size_ratio
    )

    model = train_random_forest_model(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = evaluate_forecast(
        y_test,
        y_pred
    )

    feature_importance_df = get_feature_importance(model, list(X_train.columns))

    results_df = X_test.copy()
    results_df["actual_consumption_kwh"] = y_test.values
    results_df["predicted_consumption_kwh"] = y_pred
    
    return {
        "model": model,
        "metrics": metrics,
        "results_df": results_df, 
        "feature_importance_df": feature_importance_df
    }

def get_feature_importance(
        model: RandomForestRegressor,
        feature_names: list[str]
) -> pd.DataFrame:
    
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False
    ).reset_index(drop=True)

    return importance_df