VENV: = venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

.PHONY: install run debug lint clean fclean re help

install: $(VENV)/bin/activate
