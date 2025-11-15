
"""
Этап 1: Минимальный прототип с конфигурацией
Визуализатор графа зависимостей для Maven пакетов
"""

import argparse
import sys
from typing import Dict, Any


class DependencyVisualizer:
    def __init__(self):
        self.config = {}

    def parse_arguments(self) -> Dict[str, Any]:
        """Разбор аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей для Maven пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # Обязательные параметры
        parser.add_argument(
            '--package',
            required=True,
            help='Имя анализируемого пакета (например: "org.springframework:spring-core")'
        )

        parser.add_argument(
            '--repository',
            required=True,
            help='URL репозитория или путь к тестовому репозиторию'
        )

        parser.add_argument(
            '--version',
            required=True,
            help='Версия пакета для анализа'
        )

        # Опциональные параметры
        parser.add_argument(
            '--test-mode',
            action='store_true',
            default=False,
            help='Режим работы с тестовым репозиторием'
        )

        parser.add_argument(
            '--output',
            default='dependency_graph.png',
            help='Имя генерируемого файла с изображением графа'
        )

        parser.add_argument(
            '--ascii-tree',
            action='store_true',
            default=False,
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )

        parser.add_argument(
            '--max-depth',
            type=int,
            default=10,
            help='Максимальная глубина анализа зависимостей'
        )

        parser.add_argument(
            '--filter',
            default='',
            help='Подстрока для фильтрации пакетов'
        )

        return vars(parser.parse_args())

    def validate_arguments(self, args: Dict[str, Any]) -> bool:
        """Валидация параметров"""
        try:
            # Проверка имени пакета
            if ':' not in args['package']:
                raise ValueError("Имя пакета должно содержать ':' (group:artifact)")

            # Проверка версии
            if not args['version'] or args['version'].isspace():
                raise ValueError("Версия пакета не может быть пустой")

            # Проверка максимальной глубины
            if args['max_depth'] <= 0:
                raise ValueError("Максимальная глубина должна быть положительным числом")

            # Проверка репозитория
            if not args['repository']:
                raise ValueError("Репозиторий не может быть пустым")

            return True

        except ValueError as e:
            print(f"Ошибка валидации параметров: {e}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка при валидации: {e}")
            return False

    def display_config(self, config: Dict[str, Any]):
        """Вывод конфигурации в формате ключ-значение"""
        print("\n=== КОНФИГУРАЦИЯ ПАРАМЕТРОВ ===")
        for key, value in config.items():
            print(f"{key:15}: {value}")
        print("===============================\n")

    def run(self):
        """Основной метод выполнения этапа 1"""
        try:
            print("=== ЭТАП 1: Минимальный прототип с конфигурацией ===")

            # Разбор аргументов
            config = self.parse_arguments()

            # Валидация параметров
            if not self.validate_arguments(config):
                print("Ошибка: неверные параметры конфигурации")
                sys.exit(1)

            # Вывод конфигурации
            self.display_config(config)

            print("Этап 1 успешно завершен! Конфигурация загружена.")

        except argparse.ArgumentError as e:
            print(f"Ошибка разбора аргументов: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            sys.exit(1)


if __name__ == "__main__":
    visualizer = DependencyVisualizer()
    visualizer.run()