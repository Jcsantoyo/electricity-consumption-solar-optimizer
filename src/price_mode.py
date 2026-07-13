def build_electricity_price_mode_description(
    use_hourly_price_data: bool,
    hourly_price_data_path: str,
    tariff_profile_name: str,
) -> str:
    if use_hourly_price_data:
        return (
            f"Hourly electricity prices ({hourly_price_data_path}); "
            "fixed power cost and surplus compensation from tariff profile "
            f"'{tariff_profile_name}'"
        )

    return (
        "Time-of-use electricity prices from tariff profile "
        f"'{tariff_profile_name}'"
    )