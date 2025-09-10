.PHONY: test test-cov test-watch install dev clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python3 -m pytest test_api.py -v

# Run tests with coverage
test-cov:
	python3 -m pytest test_api.py -v --cov=app --cov-report=html --cov-report=term

# Run tests in watch mode (requires pytest-watch)
test-watch:
	python3 -m pytest-watch test_api.py -v

# Run the development server
dev:
	python3 app.py

# Clean up generated files
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.pyc
	rm -rf .DS_Store

# Run all tests and generate coverage report
coverage: test-cov

# Run linting (requires flake8)
lint:
	flake8 app.py test_api.py

# Format code (requires black)
format:
	black app.py test_api.py
