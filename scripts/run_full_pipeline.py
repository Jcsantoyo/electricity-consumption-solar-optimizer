import subprocess
import sys


def run_command(command: list[str]) -> None:
    print("\nRunning command:")
    print(" ".join(command))

    result = subprocess.run(
        command,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: "
            f"{' '.join(command)}"
        )


def main() -> None:
    python_executable = sys.executable

    commands = [
        [
            python_executable,
            "scripts/generate_config_summary.py"
        ],
        [
            python_executable,
            "src/main.py"
        ],
        [
            python_executable,
            "scripts/run_forecasting.py"
        ],
        [
            python_executable,
            "scripts/run_forecast_optimization.py"
        ],
        [
            python_executable,
            "scripts/compare_optimization_results.py"
        ],
        [
            python_executable,
            "scripts/compare_optimization_results.py"
        ],
        [
            python_executable,
            "scripts/generate_final_results_summary.py"
        ]
    ]

    print("\nElectricity Consumption Solar Optimizer")
    print("Running full project pipeline...")

    for command in commands:
        run_command(command)

    print("\nFull pipeline completed successfully.")


if __name__ == "__main__":
    main()