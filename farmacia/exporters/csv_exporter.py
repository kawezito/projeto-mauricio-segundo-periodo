import csv
from pathlib import Path
from typing import List, Any, Optional
from interfaces.exporter import IReportExporter

DEFAULT_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


class CsvReportExporter(IReportExporter):
    def __init__(self, reports_dir: Optional[Path | str] = None, delimiter: str = ";"):
        self.reports_dir = Path(reports_dir) if reports_dir else DEFAULT_REPORTS_DIR
        self.delimiter = delimiter
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def exportar(self, matriz: List[List[Any]], nome_arquivo: str) -> str:
        caminho = self.reports_dir / nome_arquivo
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            for linha in matriz:
                escritor.writerow(linha)

        return str(caminho.resolve())

