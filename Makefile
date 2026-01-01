.PHONY: run
run:
	uv run streamlit run streamlit_app.py

.PHONY: ci
ci:
	uv run pytest


.PHONY: open-coverage
open-coverage: ## Open coverage HTML report in browser
	@open htmlcov/index.html