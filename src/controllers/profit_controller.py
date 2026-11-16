from typing import List

from src.models.profit import Profit


class ProfitController:
    def create(self, profit: Profit) -> Profit:
        return profit

    def read(id: str | None = None, name: str | None = None) -> List[Profit] | list[Profit]:
        pass

    def update(self, id: str, profit: Profit) -> Profit:
        return profit

    def delete(self, id: str) -> None:
        return None
