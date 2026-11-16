import pickle

from src.core.file import file_name
from src.models.profit import Profit
from src.utils.profits import calculate_profits


class ProfitController:
    def create(self, profit: Profit) -> Profit:
        existing_profits = self.read()

        if any(p.name.lower() == profit.name.lower() for p in existing_profits):
            raise ValueError(f"Já existe um profit com o nome '{profit.name}'.")

        after_fees, calculated_profit = calculate_profits(
            profit.price_sale, profit.price_cost, profit.fees
        )
        profit = profit.model_copy(
            update={"after_fees": after_fees, "profit": calculated_profit}
        )

        with open(file_name(), "ab") as file:
            pickle.dump(profit, file)
        return profit

    def read(
        self, id: str | None = None, name: str | None = None
    ) -> list[Profit]:
        profits: list[Profit] = []
        try:
            file = open(file_name(), "rb")
        except FileNotFoundError:
            return profits

        with file:
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
        profits = self.read()
        existing = next((item for item in profits if item.id == id), None)

        if existing is None:
            raise ValueError(f"Não foi encontrado um profit com o ID {id}.")

        if any(
            item.id != id and item.name.lower() == profit.name.lower()
            for item in profits
        ):
            raise ValueError(f"Já existe um profit com o nome '{profit.name}'.")

        after_fees, calculated_profit = calculate_profits(
            profit.price_sale, profit.price_cost, profit.fees
        )
        updated_profit = profit.model_copy(
            update={
                "id": id,
                "after_fees": after_fees,
                "profit": calculated_profit,
            }
        )
        updated_profits = [
            updated_profit if item.id == id else item for item in profits
        ]

        with open(file_name(), "wb") as file:
            for item in updated_profits:
                pickle.dump(item, file)

        return updated_profit

    def delete(self, id: str) -> None:
        profits = self.read()
        updated_profits = [p for p in profits if p.id != id]

        if len(updated_profits) == len(profits):
            raise ValueError(f"Não foi encontrado um profit com o ID {id}.")

        with open(file_name(), "wb") as file:
            for p in updated_profits:
                pickle.dump(p, file)
