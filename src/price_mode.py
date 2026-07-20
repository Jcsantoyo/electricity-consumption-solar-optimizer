def build_electricity_price_mode_description(
    price_mode: str,
    hourly_price_data_path: str | None,
    tariff_profile_name: str,
) -> str:
    if price_mode == "wholesale_hourly":
        if hourly_price_data_path is None:
            raise ValueError(
                "Wholesale hourly price mode requires an hourly price data path"
            )

        return (
            "Hourly wholesale electricity prices "
            f"({hourly_price_data_path}); fixed power cost and surplus "
            "compensation from tariff profile "
            f"'{tariff_profile_name}'"
        )

    if price_mode == "fixed":
        return f"Fixed electricity price from tariff profile '{tariff_profile_name}'"

    if price_mode == "time_of_use":
        return (
            "Time-of-use electricity prices from tariff profile "
            f"'{tariff_profile_name}'"
        )

    raise ValueError(f"Invalid electricity price mode: {price_mode}")
