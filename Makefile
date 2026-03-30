.PHONY: help install install-dev test test-coverage lint format clean \
        build publish upload-test upload-prod examples redis-up redis-down \
        coverage-report benchmark docs init

PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
RUFF := ruff
MYPY := mypy
PKG_NAME := async-simple-cache

GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m

help:
	@echo "$(GREEN)AsyncSimpleCache - Доступные команды:$(NC)"
	@echo ""
	@echo "$(YELLOW)Установка и настройка:$(NC)"
	@echo "  make install          - Установка пакета"
	@echo "  make install-dev      - Установка с dev зависимостями"
	@echo "  make init             - Инициализация проекта (установка всех зависимостей)"
	@echo ""
	@echo "$(YELLOW)Тестирование:$(NC)"
	@echo "  make test             - Запуск всех тестов"
	@echo "  make test-coverage    - Запуск тестов с покрытием"
	@echo "  make test-parallel    - Запуск тестов параллельно"
	@echo "  make test-redis       - Запуск тестов с Redis"
	@echo ""
	@echo "$(YELLOW)Качество кода:$(NC)"
	@echo "  make lint             - Проверка линтерами (ruff, mypy)"
	@echo "  make format           - Форматирование кода (black)"
	@echo "  make check            - Проверка форматирования"
	@echo ""
	@echo "$(YELLOW)Сборка и публикация:$(NC)"
	@echo "  make clean            - Очистка временных файлов"
	@echo "  make build            - Сборка пакета (wheel + sdist)"
	@echo "  make publish-test     - Публикация на TestPyPI"
	@echo "  make publish          - Публикация на PyPI"
	@echo ""
	@echo "$(YELLOW)Docker/Redis:$(NC)"
	@echo "  make redis-up         - Запуск Redis в Docker"
	@echo "  make redis-down       - Остановка Redis"
	@echo "  make redis-shell      - Подключение к Redis CLI"
	@echo ""
	@echo "$(YELLOW)Другое:$(NC)"
	@echo "  make benchmark        - Запуск бенчмарков"
	@echo "  make docs             - Генерация документации"
	@echo "  make coverage-report  - Открыть отчет о покрытии"
	@echo "  make examples         - Запуск примеров"

install:
	@echo "$(GREEN)Установка пакета...$(NC)"
	$(PIP) install .

install-dev:
	@echo "$(GREEN)Установка с dev зависимостями...$(NC)"
	$(PIP) install -e .[dev]

init:
	@echo "$(GREEN)Инициализация проекта...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]
	@echo "$(GREEN)Готово!$(NC)"

test:
	@echo "$(GREEN)Запуск тестов...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto

test-coverage:
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto \
		--cov=async_simple_cache \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml
	@echo "$(GREEN)Отчет сохранен в htmlcov/index.html$(NC)"

test-parallel:
	@echo "$(GREEN)Запуск тестов параллельно...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto -n auto

test-redis:
	@echo "$(GREEN)Запуск тестов с Redis...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto -k "redis"

test-slow:
	@echo "$(GREEN)Запуск медленных тестов...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto --runslow

test-quick:
	@echo "$(GREEN)Запуск быстрых тестов...$(NC)"
	$(PYTEST) tests/ -v --asyncio-mode=auto -m "not slow"

lint:
	@echo "$(GREEN)Проверка линтерами...$(NC)"
	@echo "$(YELLOW)Running ruff...$(NC)"
	$(RUFF) check async_simple_cache/ tests/ examples/
	@echo "$(YELLOW)Running mypy...$(NC)"
	$(MYPY) async_simple_cache/ --ignore-missing-imports
	@echo "$(GREEN)Линтеры прошли успешно!$(NC)"

format:
	@echo "$(GREEN)Форматирование кода...$(NC)"
	$(BLACK) async_simple_cache/ tests/ examples/
	@echo "$(GREEN)Форматирование завершено!$(NC)"

check:
	@echo "$(GREEN)Проверка форматирования...$(NC)"
	$(BLACK) --check async_simple_cache/ tests/ examples/

clean:
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.so" -delete
	@echo "$(GREEN)Очистка завершена!$(NC)"

build: clean
	@echo "$(GREEN)Сборка пакета...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Пакет собран в dist/$(NC)"
	@ls -lh dist/

publish-test: build
	@echo "$(GREEN)Публикация на TestPyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)Готово! Установка: pip install --index-url https://test.pypi.org/simple/ $(PKG_NAME)$(NC)"

publish: build
	@echo "$(GREEN)Публикация на PyPI...$(NC)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)Готово!$(NC)"

redis-up:
	@echo "$(GREEN)Запуск Redis в Docker...$(NC)"
	docker run -d --name async-cache-redis -p 6379:6379 redis:7-alpine
	@echo "$(GREEN)Redis запущен на localhost:6379$(NC)"

redis-down:
	@echo "$(GREEN)Остановка и удаление Redis контейнера...$(NC)"
	docker stop async-cache-redis || true
	docker rm async-cache-redis || true
	@echo "$(GREEN)Redis остановлен$(NC)"

redis-shell:
	@echo "$(GREEN)Подключение к Redis CLI...$(NC)"
	docker exec -it async-cache-redis redis-cli

examples:
	@echo "$(GREEN)Запуск примеров...$(NC)"
	@echo "$(YELLOW)Basic usage example:$(NC)"
	$(PYTHON) examples/basic_usage.py
	@echo ""
	@echo "$(YELLOW)TTL example:$(NC)"
	$(PYTHON) examples/ttl_example.py

example-basic:
	$(PYTHON) examples/basic_usage.py

example-ttl:
	$(PYTHON) examples/ttl_example.py

benchmark:
	@echo "$(GREEN)Запуск бенчмарков...$(NC)"
	$(PYTHON) -m pytest tests/benchmarks/ -v --benchmark-only 2>/dev/null || \
	echo "Бенчмарки не настроены. Создайте tests/benchmarks/"

docs:
	@echo "$(GREEN)Генерация документации...$(NC)"
	@if [ -d "docs" ]; then \
		cd docs && make html; \
		echo "$(GREEN)Документация собрана в docs/_build/html/$(NC)"; \
	else \
		echo "$(YELLOW}Папка docs не найдена. Создайте документацию с помощью sphinx-quickstart$(NC)"; \
	fi

coverage-report:
	@if [ -f "htmlcov/index.html" ]; then \
		open htmlcov/index.html 2>/dev/null || \
		xdg-open htmlcov/index.html 2>/dev/null || \
		echo "Откройте htmlcov/index.html в браузере"; \
	else \
		echo "$(RED)Отчет не найден. Запустите 'make test-coverage' сначала$(NC)"; \
	fi

shell:
	@echo "$(GREEN)Запуск Python shell с загруженным пакетом...$(NC)"
	$(PYTHON) -c "import async_simple_cache; print('AsyncSimpleCache загружен!'); import IPython; IPython.embed()" 2>/dev/null || \
	$(PYTHON) -c "import async_simple_cache; print('AsyncSimpleCache загружен!'); import code; code.interact(local=locals())"

version:
	@echo "$(GREEN)Текущая версия:$(NC)"
	@$(PYTHON) -c "import async_simple_cache; print(async_simple_cache.__version__)"

pre-commit: format lint test
	@echo "$(GREEN)Все проверки пройдены! Можно коммитить.$(NC)"

ci: install-dev lint test-coverage
	@echo "$(GREEN)CI pipeline completed successfully!$(NC)"

dev: install-dev redis-up
	@echo "$(GREEN)Среда разработки готова!$(NC)"
	@echo "Redis запущен, зависимости установлены"
	@echo "Запустите 'make test' для проверки"

down: redis-down
	@echo "$(GREEN)Все сервисы остановлены$(NC)"