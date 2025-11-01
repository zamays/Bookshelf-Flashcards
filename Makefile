.PHONY: help setup install run run-example list clean gui

help: ## Show this help message
	@echo "Bookshelf-Flashcards - Make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Run the setup script (installs dependencies and creates .env)
	./setup.sh

install: ## Install dependencies only
	pip3 install -r requirements.txt

run: ## Launch the application (GUI by default)
	python3 main.py

run-example: ## Add example books and list them
	python3 bookshelf.py --quiet add-file example_books.txt
	python3 bookshelf.py --quiet list

list: ## List all books in the bookshelf
	python3 bookshelf.py --quiet list

gui: ## Launch the GUI application
	python3 bookshelf_gui.py

clean: ## Remove database and cache files
	rm -f bookshelf.db
	rm -rf __pycache__
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
