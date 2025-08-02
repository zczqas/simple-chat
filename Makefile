.PHONY: install test run clean lint format help docker-build docker-up docker-down docker-logs env

# Variables
PYTHON = python3
POETRY = poetry

help:
	@echo "Available commands:"
	@echo "  make install        - Install project dependencies"
	@echo "  make test           - Run tests"
	@echo "  make run            - Run the FastAPI application"
	@echo "  make clean          - Remove Python cache files"
	@echo "  make lint           - Run linting checks"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-up      - Start Docker Compose services"
	@echo "  make docker-down    - Stop Docker Compose services"
	@echo "  make docker-logs    - Show logs from Docker Compose"
	@echo "  make make-migrate   - Generate new migration (use m='description')"
	@echo "  make migrate        - Apply pending migrations"
	@echo "  make env            - Generate a sample .env file"

install:
	$(POETRY) install

test:
	$(POETRY) run pytest -v

run:
	$(POETRY) run uvicorn src.sc_chat.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

lint:
	$(POETRY) run flake8 src tests
	$(POETRY) run mypy src tests

format:
	$(POETRY) run black src tests
	$(POETRY) run isort src tests

# Dependencies installation for development
dev-setup: install
	$(POETRY) add --group dev black flake8 mypy isort pytest pytest-cov

docker-build:
	docker compose build

docker-up:
	docker compose up

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# Database migration commands
revision:
	docker compose exec web alembic revision --autogenerate -m "$(m)"

migrate:
	docker compose exec web alembic upgrade head