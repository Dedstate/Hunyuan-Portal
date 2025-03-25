import argparse
import sys

from gradio_client import Client
from cmd import Cmd


class HunyuanShell(Cmd):
    """Интерактивная оболочка для работы с Hunyuan T1"""
    intro = (
        "Добро пожаловать в CLI Hunyuan T1."
        "Введите 'help' для списка команд или 'exit' для выхода."
    )
    prompt = "hunyuan> "

    def __init__(self, client: Client, use_markdown: bool = False):
        super().__init__()
        self.client = client
        self.use_markdown = use_markdown
        self.console = None
        # Инициализация rich только если требуется
        if self.use_markdown:
            try:
                from rich.console import Console
                self.console = Console()
            except ImportError:
                print("Предупреждение: Для Markdown требуется пакет 'rich'. Установите его командой: pip install rich")

    def default(self, line: str) -> bool:
        """Обработка неизвестных команд как обычных сообщений"""
        return self._handle_message(line.strip())

    def do_exit(self) -> bool:
        """Выход из программы"""
        print("До свидания!")
        return True

    def help_exit(self) -> None:
        """Справка по команде exit"""
        print("Выход из программы. Все данные будут потеряны.")

    def _handle_message(self, message: str) -> bool:
        """Универсальная обработка сообщений"""
        # Добавляем сообщение о принятии запроса
        if self.console and self.use_markdown:
            from rich.panel import Panel
            self.console.print(Panel.fit(f"[bold yellow]Принят запрос:[/bold yellow] {message}"))
            self.console.print(Panel.fit("[bold blue]Обработка...[/bold blue]", style="blue"))
        else:
            print(f"Принят запрос: '{message}'")
            print("Обработка запроса к Hunyuan T1...")

        try:
            result = query_hunyuan(message, self.client)
            self._print_result(result)
            return True
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {str(e)}")
            return False

    def _print_result(self, result: str) -> None:
        """Вывод результата с поддержкой Markdown"""
        if self.console and self.use_markdown:
            from rich.markdown import Markdown
            self.console.print(Markdown(result))
        else:
            print(result)


def query_hunyuan(message: str, client: Client) -> str:
    """Отправка запроса к модели Hunyuan T1 и возврат ответа"""
    return client.predict(message=message, api_name="/chat")


def main():
    parser = argparse.ArgumentParser(
        description="Командная строка для работы с Hunyuan T1",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--message", "-m",
        type=str,
        help="Текстовое сообщение для отправки модели"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Запуск интерактивного режима"
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Включить вывод в формате Markdown (требует rich)"
    )
    parser.add_argument(
        "--url",
        default="tencent/Hunyuan-T1",
        help="URL или имя модели Hunyuan T1"
    )
    args = parser.parse_args()

    # Проверка подключения к модели
    try:
        print(f"Подключение к Hunyuan T1 ({args.url})...")
        client = Client(args.url)
        print("Успешное подключение!")
    except Exception as e:
        print(f"Ошибка подключения: {str(e)}")
        sys.exit(1)

    # Определение режима работы
    if args.interactive:
        HunyuanShell(client, args.markdown).cmdloop()
    elif args.message:
        result = query_hunyuan(args.message, client)
        print_result(result, args.markdown)
    else:
        parser.print_help()


def print_result(result: str, use_markdown: bool) -> None:
    """Универсальный вывод результата с Markdown"""
    if use_markdown:
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            Console().print(Markdown(result))
        except ImportError:
            print("Markdown недоступен. Установите 'rich' для этой функции.")
            print(result)
    else:
        print(result)


if __name__ == "__main__":
    main()
