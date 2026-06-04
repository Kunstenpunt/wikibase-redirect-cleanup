import csv
from typing import Sequence


class Logger:
    def __init__(self, filename: str = "log.csv") -> None:
        self.filename = filename

    def write_row(self, row: Sequence[str]) -> None:
        with open(self.filename, mode="a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
