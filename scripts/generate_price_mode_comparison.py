import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import config
from price_comparison import compare_all_price_modes
from price_loader import load_hourly_prices
from visualization import plot_price_mode_comparison

# Example fixed household electricity price.
# Replace this later with the real price from your contract.
DEFAULT_FIXED_PRICE_EUR_PER_KWH = 0.20


def load_energy_data(file_path: str) -> pd.DataFrame:
    energy_df = pd.read_csv(file_path, parse_dates=["datetime"])

    required_columns = {"datetime", "grid_import_kwh"}
    missing_columns = required_columns - set(energy_df.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required energy columns: {missing_text}")

    return energy_df[["datetime", "grid_import_kwh"]].copy()


def build_price_mode_comparison_markdown(
    comparison_df: pd.DataFrame,
    fixed_price_eur_per_kwh: float,
    energy_data_path: str,
    hourly_price_data_path: str,
) -> str:
    cheapest_row = comparison_df.loc[comparison_df["variable_grid_cost_eur"].idxmin()]

    lines = [
        "# Electricity Price Mode Comparison",
        "",
        (
            "This report compares different electricity price "
            "models using the same hourly grid-import profile."
        ),
        "",
        "## Input data",
        "",
        f"- Energy data: `{energy_data_path}`",
        f"- Hourly electricity prices: `{hourly_price_data_path}`",
        (f"- Fixed electricity price: `{fixed_price_eur_per_kwh:.4f} EUR/kWh`"),
        "",
        "## Results",
        "",
        (
            "| Price mode | Variable grid cost | Difference vs fixed "
            "| Difference vs 2.0TD |"
        ),
        "|---|---:|---:|---:|",
    ]

    for row in comparison_df.itertuples(index=False):
        lines.append(
            f"| {row.price_mode} "
            f"| {row.variable_grid_cost_eur:.2f} EUR "
            f"| {row.difference_vs_flat_eur:.2f} EUR "
            f"| {row.difference_vs_2_0td_eur:.2f} EUR |"
        )

    lines.extend(
        [
            "",
            "## Cheapest price mode",
            "",
            (
                "The lowest variable grid-import cost is obtained "
                f"with `{cheapest_row['price_mode']}`:"
            ),
            "",
            f"**{cheapest_row['variable_grid_cost_eur']:.2f} EUR**",
            "",
            "## Interpretation",
            "",
            "Only the variable cost of imported electricity is compared here.",
            (
                "Fixed power charges, taxes, meter rental and surplus "
                "compensation are not included in this comparison."
            ),
            (
                "OMIE values represent wholesale market prices and are not "
                "equivalent to a complete household retail electricity tariff."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def generate_price_mode_comparison(
    energy_data_path: str | None = None,
    fixed_price_eur_per_kwh: float = DEFAULT_FIXED_PRICE_EUR_PER_KWH,
    output_csv_path: str | None = None,
    output_markdown_path: str | None = None,
    output_plot_path: str | None = None,
) -> pd.DataFrame:
    if config.HOURLY_PRICE_DATA_PATH is None:
        raise ValueError(
            "Electricity price mode comparison requires an hourly price dataset"
        )

    paths = config.OUTPUT_PATHS
    paths.create_directories()

    resolved_energy_data_path = energy_data_path or paths.best_scenario_timeseries
    resolved_output_csv_path = output_csv_path or paths.price_mode_comparison_csv
    resolved_output_markdown_path = (
        output_markdown_path or paths.price_mode_comparison_markdown
    )
    resolved_output_plot_path = output_plot_path or paths.price_mode_comparison_plot

    energy_df = load_energy_data(resolved_energy_data_path)

    price_df = load_hourly_prices(
        file_path=config.HOURLY_PRICE_DATA_PATH,
        allow_negative_prices=config.ALLOW_NEGATIVE_HOURLY_PRICES,
    )

    active_tariff = config.get_active_tariff_profile()

    comparison_df = compare_all_price_modes(
        energy_df=energy_df,
        price_df=price_df,
        fixed_price_eur_per_kwh=fixed_price_eur_per_kwh,
        peak_price_eur_per_kwh=active_tariff["peak_price_eur_per_kwh"],
        flat_price_eur_per_kwh=active_tariff["flat_price_eur_per_kwh"],
        off_peak_price_eur_per_kwh=active_tariff["off_peak_price_eur_per_kwh"],
        allow_negative_hourly_prices=config.ALLOW_NEGATIVE_HOURLY_PRICES,
    )

    output_csv = Path(resolved_output_csv_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(output_csv, index=False)

    markdown_text = build_price_mode_comparison_markdown(
        comparison_df=comparison_df,
        fixed_price_eur_per_kwh=fixed_price_eur_per_kwh,
        energy_data_path=resolved_energy_data_path,
        hourly_price_data_path=config.HOURLY_PRICE_DATA_PATH,
    )

    output_markdown = Path(resolved_output_markdown_path)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown_text, encoding="utf-8")

    plot_price_mode_comparison(
        comparison_df=comparison_df,
        output_path=resolved_output_plot_path,
    )

    return comparison_df


def main() -> None:
    if config.HOURLY_PRICE_DATA_PATH is None:
        print(
            "\nElectricity price mode comparison skipped: "
            "the active scenario has no hourly price dataset."
        )
        return

    comparison_df = generate_price_mode_comparison()
    paths = config.OUTPUT_PATHS

    print("\nElectricity price mode comparison")
    print(comparison_df.to_string(index=False))
    print(f"\nCSV saved to: {paths.price_mode_comparison_csv}")
    print(f"Markdown report saved to: {paths.price_mode_comparison_markdown}")
    print(f"Comparison plot saved to: {paths.price_mode_comparison_plot}")


if __name__ == "__main__":
    main()
