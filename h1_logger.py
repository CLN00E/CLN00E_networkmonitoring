import csv
from pathlib import Path


def hl_save_measurement(result):
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(exist_ok=True)

    file_path = data_dir / "measurements.csv"
    file_exists = file_path.exists() and file_path.stat().st_size > 0

    with file_path.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")

        if not file_exists:
            writer.writerow([
                "Szolgáltatás",
                "Állapot",
                "Válaszidő (ms)",
                "Időpont"
            ])

        writer.writerow([
            result["name"],
            "ONLINE" if result["online"] else "OFFLINE",
            result["response_time"] if result["response_time"] is not None else "",
            result["timestamp"]
        ])
