VENV := venv

.EXPORT_ALL_VARIABLES:
VENV_BINARY := $(VENV)/bin
PY_PATH := python3.12
PYTHONPATH := ./
GOSZAKUP_TOKEN :=

$(VENV_BINARY)/activate: requirements.txt .EXPORT_ALL_VARIABLES


venv: $(VENV_BINARY)/activate


parse-applications:
	@$(VENV_BINARY)/python ./parser/src/parse_applications.py


parse-lots:
	@$(VENV_BINARY)/python ./parser/src/parse_lots.py


parse-ads:
	@$(VENV_BINARY)/python ./parser/src/parse_advertisements.py
