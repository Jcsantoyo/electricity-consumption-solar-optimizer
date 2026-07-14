import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:

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
    lags: list[int] | None = None,
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
    target_column: str = "consumption_kwh",
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    prepared_df = add_time_features(df)

    prepared_df = add_lag_features(
        prepared_df,
        target_column=target_column,
        lags=[1, 24],
    )

    feature_columns = [
        "hour",
        "day",
        "month",
        "weekday",
        "is_weekend",
        f"{target_column}_lag_1",
        f"{target_column}_lag_24",
    ]

    X = prepared_df[feature_columns]
    y = prepared_df[target_column]
    datetimes = prepared_df["datetime"]

    return X, y, datetimes


def split_train_test_by_time(
    X: pd.DataFrame,
    y: pd.Series,
    datetimes: pd.Series,
    test_size_ratio: float = 0.2,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
    pd.Series,
]:
    if not 0 < test_size_ratio < 1:
        raise ValueError(
            "Test size ratio must be between 0 and 1"
        )

    if not (
        len(X)
        == len(y)
        == len(datetimes)
    ):
        raise ValueError(
            "Features, target and datetimes must have "
            "the same number of rows"
        )

    split_index = int(
        len(X) * (1 - test_size_ratio)
    )

    if split_index <= 0 or split_index >= len(X):
        raise ValueError(
            "Train/test split produces an empty partition"
        )

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    datetime_train = datetimes.iloc[:split_index]
    datetime_test = datetimes.iloc[split_index:]

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        datetime_train,
        datetime_test,
    )


def train_random_forest_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 200,
    random_state: int = 42,
) -> RandomForestRegressor:

    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)

    model.fit(X_train, y_train)

    return model


def train_linear_regression_model(
    X_train: pd.DataFrame, y_train: pd.Series
) -> LinearRegression:

    model = LinearRegression()

    model.fit(X_train, y_train)

    return model


def evaluate_forecast(y_true: pd.Series, y_pred) -> dict[str, float]:

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = mse**0.5

    return {"mae": mae, "rmse": rmse}


def run_consumption_forecast(
    df: pd.DataFrame,
    target_column: str = "consumption_kwh",
    test_size_ratio: float = 0.2,
    random_state: int = 42
) -> dict:

    X, y, datetimes = prepare_forecasting_dataset(df, target_column=target_column)

    X_train, X_test, y_train, y_test, _, datetime_test = split_train_test_by_time(
        X, y, datetimes, test_size_ratio=test_size_ratio
    )

    model = train_random_forest_model(X_train, y_train, random_state=random_state)

    y_pred = model.predict(X_test)

    metrics = evaluate_forecast(y_test, y_pred)

    feature_importance_df = get_feature_importance(model, list(X_train.columns))

    results_df = X_test.copy()
    results_df.insert(
        0,
        "datetime",
        datetime_test.values,
    )
    results_df["actual_consumption_kwh"] = (
        y_test.values
    )
    results_df["predicted_consumption_kwh"] = (
        y_pred
    )

    return {
        "model": model,
        "metrics": metrics,
        "results_df": results_df,
        "feature_importance_df": feature_importance_df,
    }


def get_feature_importance(
    model: RandomForestRegressor, feature_names: list[str]
) -> pd.DataFrame:

    importance_df = pd.DataFrame(
        {"feature": feature_names, "importance": model.feature_importances_}
    )

    importance_df = importance_df.sort_values(
        "importance", ascending=False
    ).reset_index(drop=True)

    return importance_df


def compare_forecasting_models(
    df: pd.DataFrame,
    target_column: str = "consumption_kwh",
    test_size_ratio: float = 0.2,
    random_state: int = 42
) -> pd.DataFrame:

    X, y, datetimes = prepare_forecasting_dataset(df, target_column=target_column)

    X_train, X_test, y_train, y_test, _, _ = split_train_test_by_time(
        X, y, datetimes, test_size_ratio=test_size_ratio
    )

    models = {
        "Linear_Regression": train_linear_regression_model(X_train, y_train),
        "Random Forest": train_random_forest_model(X_train, y_train, random_state=random_state),
    }

    rows = []

    for model_name, model in models.items():
        y_pred = model.predict(X_test)

        metrics = evaluate_forecast(y_test, y_pred)

        rows.append(
            {"model": model_name, "mae": metrics["mae"], "rmse": metrics["rmse"]}
        )

    comparison_df = pd.DataFrame(rows)

    comparison_df = comparison_df.sort_values("mae", ascending=True).reset_index(
        drop=True
    )

    return comparison_df


def build_forecasted_consumption_dataframe(
    original_df: pd.DataFrame,
    forecast_results_df: pd.DataFrame,
    forecast_mode: str = "backtest",
) -> pd.DataFrame:
    if "predicted_consumption_kwh" not in forecast_results_df.columns:
        raise ValueError(
            "Forecast results are missing "
            "predicted_consumption_kwh"
        )

    if forecast_mode == "backtest":
        if "datetime" not in forecast_results_df.columns:
            raise ValueError(
                "Backtest forecast results must contain datetime"
            )

        forecast_datetimes = pd.to_datetime(
            forecast_results_df["datetime"],
            errors="coerce",
        )

        if forecast_datetimes.isna().any():
            raise ValueError(
                "Backtest forecast results contain "
                "invalid datetime values"
            )

    elif forecast_mode == "future":
        last_datetime = pd.to_datetime(
            original_df["datetime"]
        ).max()

        forecast_datetimes = pd.date_range(
            start=(
                last_datetime
                + pd.Timedelta(hours=1)
            ),
            periods=len(forecast_results_df),
            freq="h",
        )

    else:
        raise ValueError(
            f"Invalid forecast mode: {forecast_mode}"
        )

    return pd.DataFrame(
        {
            "datetime": forecast_datetimes,
            "consumption_kwh": (
                forecast_results_df[
                    "predicted_consumption_kwh"
                ].values
            ),
        }
    )
