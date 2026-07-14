import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pytest

from forecasting import (
    add_time_features,
    add_lag_features,
    prepare_forecasting_dataset,
    split_train_test_by_time,
    get_feature_importance,
    build_forecasted_consumption_dataframe
)


def test_add_time_features_creates_expected_columns() -> None:
    df = pd.DataFrame(
        {"datetime": [pd.Timestamp("2025-01-04 21:00:00")], "consumption_kwh": [0.50]}
    )

    result = add_time_features(df)

    assert result.loc[0, "hour"] == 21
    assert result.loc[0, "day"] == 4
    assert result.loc[0, "month"] == 1
    assert result.loc[0, "weekday"] == 5
    assert result.loc[0, "is_weekend"] == 1


def test_add_lag_features_creates_lag_columns() -> None:
    df = pd.DataFrame({"consumption_kwh": [0.10, 0.20, 0.30, 0.40]})

    result = add_lag_features(df, target_column="consumption_kwh", lags=[1])

    assert list(result["consumption_kwh_lag_1"]) == [0.10, 0.20, 0.30]
    assert list(result["consumption_kwh"]) == [0.20, 0.30, 0.40]


def test_add_lag_features_drops_missing_values() -> None:
    df = pd.DataFrame({"consumption_kwh": [0.10, 0.20, 0.30]})

    result = add_lag_features(df, target_column="consumption_kwh", lags=[2])

    assert len(result) == 1
    assert result.loc[0, "consumption_kwh"] == 0.30
    assert result.loc[0, "consumption_kwh_lag_2"] == 0.10


def test_prepare_forecasting_dataset_returns_features_target_and_datetimes() -> None:
    date_range = pd.date_range(
        start="2025-01-01",
        periods=30,
        freq="h",
    )

    df = pd.DataFrame(
        {
            "datetime": date_range,
            "consumption_kwh": [0.5] * 30,
        }
    )

    X, y, datetimes = prepare_forecasting_dataset(df)

    assert len(X) == 6
    assert len(y) == 6
    assert len(datetimes) == 6

    assert X.columns.tolist() == [
        "hour",
        "day",
        "month",
        "weekday",
        "is_weekend",
        "consumption_kwh_lag_1",
        "consumption_kwh_lag_24",
    ]

    assert datetimes.iloc[0] == pd.Timestamp(
        "2025-01-02 00:00:00"
    )


def test_split_train_test_by_time_preserves_order() -> None:
    X = pd.DataFrame(
        {
            "feature": list(range(10)),
        }
    )

    y = pd.Series(list(range(10)))

    datetimes = pd.Series(
        pd.date_range(
            start="2025-01-01",
            periods=10,
            freq="h",
        )
    )

    (
        X_train,
        X_test,
        y_train,
        y_test,
        datetime_train,
        datetime_test,
    ) = split_train_test_by_time(
        X,
        y,
        datetimes,
        test_size_ratio=0.2,
    )

    assert X_train["feature"].tolist() == list(
        range(8)
    )
    assert X_test["feature"].tolist() == [
        8,
        9,
    ]

    assert y_train.tolist() == list(range(8))
    assert y_test.tolist() == [8, 9]

    assert datetime_train.iloc[-1] == pd.Timestamp(
        "2025-01-01 07:00:00"
    )
    assert datetime_test.iloc[0] == pd.Timestamp(
        "2025-01-01 08:00:00"
    )


def test_get_feature_importance_returns_sorted_dataframe() -> None:
    X_train = pd.DataFrame(
        {"feature_a": [1, 2, 3, 4, 5, 6], "feature_b": [6, 5, 4, 3, 2, 1]}
    )

    y_train = pd.Series([1, 2, 3, 4, 5, 6])

    model = RandomForestRegressor(n_estimators=20, random_state=42)

    model.fit(X_train, y_train)

    importance_df = get_feature_importance(model, list(X_train.columns))

    assert list(importance_df.columns) == ["feature", "importance"]
    assert len(importance_df) == 2
    assert importance_df["importance"].iloc[0] >= importance_df["importance"].iloc[1]


def test_build_forecasted_consumption_dataframe_in_future_mode() -> None:
    original_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01 00:00:00",
                    "2024-01-01 01:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
                1.2,
            ],
        }
    )

    forecast_results_df = pd.DataFrame(
        {
            "predicted_consumption_kwh": [
                0.9,
                1.1,
                1.3,
            ],
        }
    )

    forecast_df = build_forecasted_consumption_dataframe(
        original_df=original_df,
        forecast_results_df=forecast_results_df,
        forecast_mode="future",
    )

    assert forecast_df["datetime"].tolist() == list(
        pd.to_datetime(
            [
                "2024-01-01 02:00:00",
                "2024-01-01 03:00:00",
                "2024-01-01 04:00:00",
            ]
        )
    )

    assert forecast_df["consumption_kwh"].tolist() == [
        0.9,
        1.1,
        1.3,
    ]

def test_build_forecasted_consumption_dataframe_in_backtest_mode() -> None:
    original_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01 00:00:00",
                    "2024-01-01 01:00:00",
                ]
            ),
            "consumption_kwh": [
                1.0,
                1.2,
            ],
        }
    )

    forecast_results_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01 00:00:00",
                    "2024-01-01 01:00:00",
                ]
            ),
            "predicted_consumption_kwh": [
                0.9,
                1.1,
            ],
        }
    )

    forecast_df = build_forecasted_consumption_dataframe(
        original_df=original_df,
        forecast_results_df=forecast_results_df,
        forecast_mode="backtest",
    )

    assert forecast_df["datetime"].tolist() == list(
        forecast_results_df["datetime"]
    )

    assert forecast_df["consumption_kwh"].tolist() == [
        0.9,
        1.1,
    ]

def test_build_forecasted_consumption_dataframe_rejects_invalid_mode() -> None:
    original_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2024-01-01 00:00:00"]
            ),
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    forecast_results_df = pd.DataFrame(
        {
            "predicted_consumption_kwh": [
                0.9,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="Invalid forecast mode",
    ):
        build_forecasted_consumption_dataframe(
            original_df=original_df,
            forecast_results_df=forecast_results_df,
            forecast_mode="unknown",
        )

def test_backtest_mode_requires_datetime_column() -> None:
    original_df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2024-01-01 00:00:00"]
            ),
            "consumption_kwh": [
                1.0,
            ],
        }
    )

    forecast_results_df = pd.DataFrame(
        {
            "predicted_consumption_kwh": [
                0.9,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="must contain datetime",
    ):
        build_forecasted_consumption_dataframe(
            original_df=original_df,
            forecast_results_df=forecast_results_df,
            forecast_mode="backtest",
        )