import pickle
from typing import List

from src.core.file import file_name
from src.models.profit import Profit


FILE_DATA = file_name()


class ProfitController:
    def create(self, profit: Profit) -> Profit:
        existing_profits = self.read()

        if any(p.name.lower() == profit.name.lower() for p in existing_profits):
            raise ValueError(f"Profit with name {profit.name} already exists.")

        with open(FILE_DATA, "ab") as file:
            pickle.dump(profit, file)
        return profit

    def read(id: str | None = None, name: str | None = None) -> List[Profit] | list[Profit]:
        with open(FILE_DATA, "rb") as file:
            profits = []
            while True:
                try:
                    profit = pickle.load(file)
                    if id and profit.id == id:
                        return [profit]
                    if name and name.lower() in profit.name.lower():
                        return [profit]
                    profits.append(profit)
                except EOFError:
                    break
        return profits

    def update(self, id: str, profit: Profit) -> Profit:
        data = self.read(id=id)

        if not data:
            raise ValueError(f"Profit with id {id} not found.")

        data.update(profit.model_dump())

        self.delete(id)

        with open(FILE_DATA, "ab") as file:
            pickle.dump(data, file)
        
        return profit

    def delete(self, id: str) -> None:
        profits = self.read()
        updated_profits = [p for p in profits if p.id != id]

        if not updated_profits:
            raise ValueError(f"Profit with id {id} not found.")

        with open(FILE_DATA, "wb") as file:
            for p in updated_profits:
                pickle.dump(p, file)
