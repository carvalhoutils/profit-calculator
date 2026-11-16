from decimal import Decimal, InvalidOperation
import pickle

from src.controllers.profit_controller import ProfitController
from src.models.fee import Fee
from src.models.profit import Profit


class ProfitCalculator:
    def __init__(self, controller: ProfitController | None = None) -> None:
        self.controller = controller or ProfitController()

    @staticmethod
    def _read_decimal(prompt: str) -> Decimal:
        while True:
            value = input(prompt).strip().replace(",", ".")
            try:
                amount = Decimal(value)
            except InvalidOperation:
                print("Informe um valor decimal válido.")
                continue
            if not amount.is_finite():
                print("Informe um valor decimal finito.")
                continue
            return amount

    @staticmethod
    def _read_yes_no(prompt: str) -> bool:
        while True:
            answer = input(prompt).strip().lower()
            if answer in {"s", "sim"}:
                return True
            if answer in {"n", "nao", "não"}:
                return False
            print("Responda com 's' ou 'n'.")

    def _read_fees(self) -> list[Fee]:
        fees: list[Fee] = []
        while self._read_yes_no("Deseja adicionar uma taxa? (s/n): "):
            name = input("Nome da taxa: ").strip()
            while not name:
                print("O nome da taxa não pode ficar vazio.")
                name = input("Nome da taxa: ").strip()
            amount = self._read_decimal("Valor da taxa: ")
            fees.append(Fee(name=name, amount=amount))
        return fees

    @staticmethod
    def _display_profits(profits: list[Profit]) -> None:
        if not profits:
            print("Nenhum profit encontrado.")
            return

        for index, profit in enumerate(profits, start=1):
            print(
                f"{index}. {profit.name} | ID: {profit.id} | "
                f"Custo: {profit.price_cost} | Venda: {profit.price_sale} | "
                f"Após taxas: {profit.after_fees} | Lucro: {profit.profit}"
            )
            for fee in profit.fees:
                print(f"   Taxa: {fee.name} | Valor: {fee.amount} | ID: {fee.id}")

    @staticmethod
    def _show_controller_error(error: Exception) -> None:
        print(f"Não foi possível concluir a operação: {error}")

    def create(self) -> None:
        name = input("Nome: ").strip()
        while not name:
            print("O nome não pode ficar vazio.")
            name = input("Nome: ").strip()

        profit = Profit(
            name=name,
            price_cost=self._read_decimal("Preço de custo: "),
            price_sale=self._read_decimal("Preço de venda: "),
            after_fees=Decimal("0"),
            profit=Decimal("0"),
            fees=self._read_fees(),
        )
        try:
            created = self.controller.create(profit)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        print(f"Profit '{created.name}' criado. Lucro: {created.profit}")

    def _select_profit(self, profits: list[Profit]) -> Profit | None:
        self._display_profits(profits)
        if not profits:
            return None

        while True:
            selection = input(
                "Selecione o número do profit (ou 0 para cancelar): "
            ).strip()
            if selection == "0":
                return None
            try:
                index = int(selection) - 1
            except ValueError:
                print("Seleção inválida.")
                continue
            if 0 <= index < len(profits):
                return profits[index]
            print("Seleção fora da lista.")

    def update(self) -> None:
        try:
            profits = self.controller.read()
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return

        selected = self._select_profit(profits)
        if selected is None:
            return

        print(
            "\n1. Alterar nome\n"
            "2. Alterar preço de custo\n"
            "3. Alterar preço de venda\n"
            "4. Adicionar taxa\n"
            "5. Remover taxa"
        )
        choice = input("Campo/ação: ").strip()
        changes: dict[str, object] = {}

        if choice == "1":
            name = input("Novo nome: ").strip()
            if not name:
                print("O nome não pode ficar vazio.")
                return
            changes["name"] = name
        elif choice == "2":
            changes["price_cost"] = self._read_decimal("Novo preço de custo: ")
        elif choice == "3":
            changes["price_sale"] = self._read_decimal("Novo preço de venda: ")
        elif choice == "4":
            name = input("Nome da taxa: ").strip()
            if not name:
                print("O nome da taxa não pode ficar vazio.")
                return
            changes["fees"] = [
                *selected.fees,
                Fee(name=name, amount=self._read_decimal("Valor da taxa: ")),
            ]
        elif choice == "5":
            if not selected.fees:
                print("Este profit não possui taxas.")
                return
            for index, fee in enumerate(selected.fees, start=1):
                print(f"{index}. {fee.name} | Valor: {fee.amount}")
            try:
                fee_index = int(input("Número da taxa a remover: ").strip()) - 1
            except ValueError:
                print("Seleção inválida.")
                return
            if not 0 <= fee_index < len(selected.fees):
                print("Seleção fora da lista.")
                return
            changes["fees"] = [
                fee for index, fee in enumerate(selected.fees) if index != fee_index
            ]
        else:
            print("Opção inválida.")
            return

        updated_profit = selected.model_copy(update=changes)
        try:
            updated = self.controller.update(selected.id, updated_profit)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        print(f"Profit atualizado. Lucro: {updated.profit}")

    def delete(self) -> None:
        try:
            profits = self.controller.read()
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._display_profits(profits)
        if not profits:
            return

        profit_id = input("ID do profit a excluir: ").strip()
        try:
            self.controller.delete(profit_id)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        print("Profit excluído.")

    def read(self) -> None:
        name = input("Nome para buscar (vazio para listar todos): ").strip()
        try:
            profits = self.controller.read(name=name or None)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._display_profits(profits)

    def run(self) -> None:
        try:
            while True:
                print(
                    "\n=== Calculadora de lucro ===\n"
                    "1. Criar\n"
                    "2. Atualizar\n"
                    "3. Excluir por ID\n"
                    "4. Consultar por nome / listar todos\n"
                    "0. Sair"
                )
                option = input("Opção: ").strip()
                if option == "1":
                    self.create()
                elif option == "2":
                    self.update()
                elif option == "3":
                    self.delete()
                elif option == "4":
                    self.read()
                elif option == "0":
                    print("Até logo!")
                    return
                else:
                    print("Opção inválida.")
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")


def main() -> None:
    ProfitCalculator().run()
