from dataclasses import dataclass
from pathlib import Path


VALID_PRICE_MODES = {
    "fixed",
    "time_of_use",
    "wholesale_hourly",
}

VALID_FORECAST_MODES = {
    "backtest",
    "future",
}


@dataclass(frozen=True)
class ProjectScenario:
    name: str

    consumption_data_path: str

    use_pvgis_solar_data: bool
    pvgis_solar_data_path: str

    price_mode: str
    tariff_profile_name: str
    financial_profile_name: str
    hourly_price_data_path: str | None
    allow_negative_hourly_prices: bool

    forecast_mode: str
    forecast_test_size_ratio: float
    random_seed: int

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Scenario name cannot be empty")

        if self.price_mode not in VALID_PRICE_MODES:
            raise ValueError(f"Invalid price mode: {self.price_mode}")

        if self.forecast_mode not in VALID_FORECAST_MODES:
            raise ValueError(f"Invalid forecast mode: {self.forecast_mode}")

        if not 0 < self.forecast_test_size_ratio < 1:
            raise ValueError("Forecast test size ratio must be between 0 and 1")

        if not self.financial_profile_name.strip():
            raise ValueError("Financial profile name cannot be empty")

        if self.random_seed < 0:
            raise ValueError("Random seed cannot be negative")

        if (
            self.price_mode == "wholesale_hourly"
            and self.hourly_price_data_path is None
        ):
            raise ValueError(
                "Wholesale hourly price mode requires an hourly price data path"
            )

        if (
            self.price_mode != "wholesale_hourly"
            and self.hourly_price_data_path is not None
        ):
            raise ValueError(
                "Hourly price data path must be None when "
                "wholesale hourly pricing is disabled"
            )

    @property
    def uses_hourly_prices(self) -> bool:
        return self.price_mode == "wholesale_hourly"

    def input_paths(self) -> list[str]:
        paths = [
            self.consumption_data_path,
        ]

        if self.use_pvgis_solar_data:
            paths.append(self.pvgis_solar_data_path)

        if self.hourly_price_data_path is not None:
            paths.append(self.hourly_price_data_path)

        return paths

    def validate_input_files_exist(self) -> None:
        missing_paths = [
            path for path in self.input_paths() if not Path(path).is_file()
        ]

        if missing_paths:
            missing_text = ", ".join(missing_paths)

            raise FileNotFoundError(
                f"Scenario input files do not exist: {missing_text}"
            )
