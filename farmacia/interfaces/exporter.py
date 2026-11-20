from abc import ABC, abstractmethod
from typing import List, Any


class IReportExporter(ABC):
    @abstractmethod
    def exportar(self, matriz: List[List[Any]], nome_arquivo: str) -> str:
        pass

