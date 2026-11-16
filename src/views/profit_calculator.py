from decimal import Decimal, InvalidOperation
import json
import os
import pickle
import sys

from src.controllers.profit_controller import ProfitController
from src.models.fee import Fee
from src.models.profit import Profit


class ProfitCalculator:
    _COLORS = {
        "blue": "94",
        "cyan": "96",
        "green": "92",
        "magenta": "95",
        "red": "91",
        "white": "97",
        "yellow": "93",
    }

    def __init__(self, controller: ProfitController | None = None) -> None:
        self.controller = controller or ProfitController()

    @classmethod
    def _format(cls, text: str, color: str | None = None) -> str:
        if color is None or not sys.stdout.isatty() or "NO_COLOR" in os.environ:
            return text
        return f"\033[{cls._COLORS[color]}m{text}\033[0m"

    @classmethod
    def _say(cls, text: str, color: str | None = None) -> None:
        print(cls._format(text, color))

    @classmethod
    def _ask(cls, prompt: str) -> str:
        return input(cls._format(f"👉 {prompt}", "cyan"))

    @staticmethod
    def _read_decimal(prompt: str) -> Decimal:
        while True:
            value = ProfitCalculator._ask(prompt).strip().replace(",", ".")
            try:
                amount = Decimal(value)
            except InvalidOperation:
                ProfitCalculator._say("⚠️  Informe um valor decimal válido.", "yellow")
                continue
            if not amount.is_finite():
                ProfitCalculator._say("⚠️  Informe um valor decimal finito.", "yellow")
                continue
            return amount

    @staticmethod
    def _read_yes_no(prompt: str) -> bool:
        while True:
            answer = ProfitCalculator._ask(prompt).strip().lower()
            if answer in {"s", "sim"}:
                return True
            if answer in {"n", "nao", "não"}:
                return False
            ProfitCalculator._say("⚠️  Responda com 's' ou 'n'.", "yellow")

    def _read_fees(self) -> list[Fee]:
        fees: list[Fee] = []
        while self._read_yes_no("Deseja adicionar uma taxa? (s/n): "):
            name = self._ask("Nome da taxa: ").strip()
            while not name:
                self._say("⚠️  O nome da taxa não pode ficar vazio.", "yellow")
                name = self._ask("Nome da taxa: ").strip()
            amount = self._read_decimal("Valor da taxa: ")
            fees.append(Fee(name=name, amount=amount))
        return fees

    @staticmethod
    def _display_profits(profits: list[Profit]) -> None:
        data = [profit.model_dump(mode="json") for profit in profits]
        print(ProfitCalculator._format_json(data))

    @classmethod
    def _format_json(cls, value: object, level: int = 0) -> str:
        indentation = " " * (level * 2)

        if isinstance(value, list):
            if not value:
                return cls._format("[]", "blue")
            items = ",\n".join(
                f"{' ' * ((level + 1) * 2)}{cls._format_json(item, level + 1)}"
                for item in value
            )
            return (
                f"{cls._format('[', 'blue')}\n{items}\n"
                f"{indentation}{cls._format(']', 'blue')}"
            )

        if isinstance(value, dict):
            if not value:
                return cls._format("{}", "magenta")
            items = ",\n".join(
                f"{' ' * ((level + 1) * 2)}"
                f"{cls._format(json.dumps(key, ensure_ascii=False), 'white')}: "
                f"{cls._format_json(item, level + 1)}"
                for key, item in value.items()
            )
            return (
                f"{cls._format('{', 'magenta')}\n{items}\n"
                f"{indentation}{cls._format('}', 'magenta')}"
            )

        return cls._format(json.dumps(value, ensure_ascii=False), "green")

    def _show_controller_error(self, error: Exception) -> None:
        if isinstance(error, ValueError):
            message = "⚠️  Operação inválida. Verifique os dados e tente novamente."
        elif isinstance(error, PermissionError):
            message = "🔒 Sem permissão para acessar o arquivo de dados."
        elif isinstance(error, OSError):
            message = "💾 Não foi possível acessar o arquivo de dados."
        elif isinstance(error, pickle.PickleError):
            message = "📂 Não foi possível ler ou salvar os dados armazenados."
        else:
            message = "❌ Ocorreu um erro inesperado durante a operação."
        self._say(message, "red")

    def create(self) -> None:
        self._say("\n✨ Criar profit", "green")
        name = self._ask("Nome: ").strip()
        while not name:
            self._say("⚠️  O nome não pode ficar vazio.", "yellow")
            name = self._ask("Nome: ").strip()

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
        self._say(
            f"✅ Profit '{created.name}' criado.\n💰 Lucro: {created.profit}",
            "green",
        )

    def _select_profit(self, profits: list[Profit]) -> Profit | None:
        self._display_profits(profits)
        if not profits:
            return None

        while True:
            selection = self._ask(
                "Selecione o número do profit (ou 0 para cancelar): "
            ).strip()
            if selection == "0":
                return None
            try:
                index = int(selection) - 1
            except ValueError:
                self._say("⚠️  Seleção inválida.", "yellow")
                continue
            if 0 <= index < len(profits):
                return profits[index]
            self._say("⚠️  Seleção fora da lista.", "yellow")

    def update(self) -> None:
        try:
            profits = self.controller.read()
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return

        selected = self._select_profit(profits)
        if selected is None:
            return

        self._say(
            "\n🛠️  Atualizar profit\n"
            "1. ✏️  Alterar nome\n"
            "2. 💸 Alterar preço de custo\n"
            "3. 💰 Alterar preço de venda\n"
            "4. ➕ Adicionar taxa\n"
            "5. ➖ Remover taxa",
            "blue",
        )
        choice = self._ask("Campo/ação: ").strip()
        changes: dict[str, object] = {}

        if choice == "1":
            name = self._ask("Novo nome: ").strip()
            if not name:
                self._say("⚠️  O nome não pode ficar vazio.", "yellow")
                return
            changes["name"] = name
        elif choice == "2":
            changes["price_cost"] = self._read_decimal("Novo preço de custo: ")
        elif choice == "3":
            changes["price_sale"] = self._read_decimal("Novo preço de venda: ")
        elif choice == "4":
            name = self._ask("Nome da taxa: ").strip()
            if not name:
                self._say("⚠️  O nome da taxa não pode ficar vazio.", "yellow")
                return
            changes["fees"] = [
                *selected.fees,
                Fee(name=name, amount=self._read_decimal("Valor da taxa: ")),
            ]
        elif choice == "5":
            if not selected.fees:
                self._say("ℹ️  Este profit não possui taxas.", "yellow")
                return
            for index, fee in enumerate(selected.fees, start=1):
                self._say(f"{index}. {fee.name} | Valor: {fee.amount}", "cyan")
            try:
                fee_index = int(self._ask("Número da taxa a remover: ").strip()) - 1
            except ValueError:
                self._say("⚠️  Seleção inválida.", "yellow")
                return
            if not 0 <= fee_index < len(selected.fees):
                self._say("⚠️  Seleção fora da lista.", "yellow")
                return
            changes["fees"] = [
                fee for index, fee in enumerate(selected.fees) if index != fee_index
            ]
        else:
            self._say("⚠️  Opção inválida.", "yellow")
            return

        updated_profit = selected.model_copy(update=changes)
        try:
            updated = self.controller.update(selected.id, updated_profit)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._say(
            f"✅ Profit atualizado.\n💰 Lucro: {updated.profit}",
            "green",
        )

    def delete(self) -> None:
        try:
            profits = self.controller.read()
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._display_profits(profits)
        if not profits:
            return

        profit_id = self._ask("ID do profit a excluir: ").strip()
        try:
            self.controller.delete(profit_id)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._say("🗑️  Profit excluído.", "green")

    def read(self) -> None:
        self._say("\n🔎 Consultar profits", "blue")
        name = self._ask("Nome para buscar (vazio para listar todos): ").strip()
        try:
            profits = self.controller.read(name=name or None)
        except (ValueError, OSError, pickle.PickleError) as error:
            self._show_controller_error(error)
            return
        self._display_profits(profits)

    def run(self) -> None:
        try:
            while True:
                self._say(
                    "\n"
                    "╭────────────────────────────────────╮\n"
                    "│       🧮 CALCULADORA DE LUCRO       │\n"
                    "├────────────────────────────────────┤\n"
                    "│ 1. ✨ Criar                         │\n"
                    "│ 2. 🛠️  Atualizar                     │\n"
                    "│ 3. 🗑️  Excluir por ID                │\n"
                    "│ 4. 🔎 Consultar por nome / listar   │\n"
                    "│ 0. 👋 Sair                          │\n"
                    "╰────────────────────────────────────╯",
                    "blue",
                )
                option = self._ask("Opção: ").strip()
                if option == "1":
                    self.create()
                elif option == "2":
                    self.update()
                elif option == "3":
                    self.delete()
                elif option == "4":
                    self.read()
                elif option == "0":
                    self._say("👋 Até logo!", "green")
                    return
                else:
                    self._say("⚠️  Opção inválida. Escolha uma opção do menu.", "yellow")
        except (EOFError, KeyboardInterrupt):
            self._say("\n👋 Até logo!", "green")


def main() -> None:
    ProfitCalculator().run()
