#!/usr/bin/env python3
"""
Этап 2: Сбор данных (включая функциональность этапа 1)
Визуализатор графа зависимостей для Maven пакетов
"""

import argparse
import sys
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple


class DependencyVisualizer:
    def __init__(self):
        self.config = {}
        self.dependencies = []

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
        """Валидация параметров (Этап 1)"""
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
        """Вывод конфигурации в формате ключ-значение (Этап 1)"""
        print("\n=== КОНФИГУРАЦИЯ ПАРАМЕТРОВ (ЭТАП 1) ===")
        for key, value in config.items():
            print(f"{key:15}: {value}")
        print("===============================\n")

    def parse_package_name(self, package: str) -> Tuple[str, str]:
        """Разбор имени пакета на groupId и artifactId (Этап 2)"""
        try:
            if ':' not in package:
                raise ValueError("Имя пакета должно содержать ':'")

            group_id, artifact_id = package.split(':', 1)
            return group_id.strip(), artifact_id.strip()

        except ValueError as e:
            print(f"Ошибка разбора имени пакета: {e}")
            raise

    def construct_pom_url(self, group_id: str, artifact_id: str, version: str, repository: str) -> str:
        """Построение URL для POM файла (Этап 2)"""
        # Формируем путь в стиле Maven репозитория
        group_path = group_id.replace('.', '/')
        pom_filename = f"{artifact_id}-{version}.pom"

        # Строим полный URL
        if repository.endswith('/'):
            repository = repository[:-1]

        pom_url = f"{repository}/{group_path}/{artifact_id}/{version}/{pom_filename}"
        return pom_url

    def download_pom_file(self, pom_url: str) -> str:
        """Загрузка POM файла из репозитория (Этап 2)"""
        try:
            print(f"Загрузка POM файла: {pom_url}")

            # Создаем запрос с User-Agent
            req = urllib.request.Request(
                pom_url,
                headers={'User-Agent': 'Maven-Dependency-Visualizer/1.0'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8')
                    print("POM файл успешно загружен")
                    return content
                else:
                    raise Exception(f"HTTP ошибка: {response.status}")

        except urllib.error.HTTPError as e:
            raise Exception(f"Не удалось загрузить POM файл: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка URL: {e.reason}")
        except Exception as e:
            raise Exception(f"Ошибка при загрузке POM файла: {e}")

    def parse_dependencies_from_pom(self, pom_content: str) -> List[Dict[str, str]]:
        """Извлечение зависимостей из POM файла (Этап 2)"""
        try:
            dependencies = []

            # Парсим XML
            root = ET.fromstring(pom_content)

            # Определяем namespace
            ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}

            # Ищем секцию dependencies
            dependencies_elem = root.find('.//maven:dependencies', ns)
            if dependencies_elem is None:
                print("В POM файле не найдены зависимости")
                return dependencies

            # Извлекаем информацию о каждой зависимости
            for dep_elem in dependencies_elem.findall('maven:dependency', ns):
                group_id_elem = dep_elem.find('maven:groupId', ns)
                artifact_id_elem = dep_elem.find('maven:artifactId', ns)
                version_elem = dep_elem.find('maven:version', ns)
                scope_elem = dep_elem.find('maven:scope', ns)

                if group_id_elem is not None and artifact_id_elem is not None:
                    dependency = {
                        'groupId': group_id_elem.text,
                        'artifactId': artifact_id_elem.text,
                        'version': version_elem.text if version_elem is not None else 'N/A',
                        'scope': scope_elem.text if scope_elem is not None else 'compile'
                    }
                    dependencies.append(dependency)

            return dependencies

        except ET.ParseError as e:
            raise Exception(f"Ошибка парсинга POM XML: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при извлечении зависимостей: {e}")

    def display_dependencies(self, dependencies: List[Dict[str, str]], package_name: str):
        """Вывод списка зависимостей на экран (Этап 2)"""
        print(f"\n=== ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА: {package_name} (ЭТАП 2) ===")

        if not dependencies:
            print("Зависимости не найдены")
            return

        for i, dep in enumerate(dependencies, 1):
            print(f"{i:2}. {dep['groupId']}:{dep['artifactId']}:{dep['version']} [{dep['scope']}]")

        print(f"\nВсего найдено зависимостей: {len(dependencies)}")
        print("==============================================\n")

    def run_stage1(self, config: Dict[str, Any]):
        """Выполнение этапа 1"""
        print("=== ЭТАП 1: Минимальный прототип с конфигурацией ===")

        # Валидация параметров
        if not self.validate_arguments(config):
            print("Ошибка: неверные параметры конфигурации")
            sys.exit(1)

        # Вывод конфигурации
        self.display_config(config)
        print("Этап 1 успешно завершен! Конфигурация загружена.\n")

    def run_stage2(self, args: Dict[str, Any]):
        """Выполнение этапа 2"""
        print("=== ЭТАП 2: Сбор данных о зависимостях ===")

        # Разбор имени пакета
        group_id, artifact_id = self.parse_package_name(args['package'])
        package_name = f"{group_id}:{artifact_id}:{args['version']}"

        print(f"Анализируемый пакет: {package_name}")
        print(f"Репозиторий: {args['repository']}")

        # Построение URL POM файла
        pom_url = self.construct_pom_url(group_id, artifact_id, args['version'], args['repository'])
        print(f"POM URL: {pom_url}")

        # Загрузка POM файла
        pom_content = self.download_pom_file(pom_url)

        # Извлечение зависимостей
        dependencies = self.parse_dependencies_from_pom(pom_content)

        # Вывод зависимостей
        self.display_dependencies(dependencies, package_name)

        print("Этап 2 успешно завершен! Данные о зависимостях собраны.")

    def run(self):
        """Основной метод выполнения обоих этапов"""
        try:
            # Разбор аргументов
            config = self.parse_arguments()

            # Этап 1: Конфигурация
            self.run_stage1(config)

            # Этап 2: Сбор данных
            self.run_stage2(config)

            print("\n=== ВСЕ ЭТАПЫ УСПЕШНО ЗАВЕРШЕНЫ ===")

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