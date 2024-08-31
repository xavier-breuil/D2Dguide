### Configure paths. ###
PROJECT_PATH := $(CURDIR)
APP_PATH := $(CURDIR)/D2D_guide_backend
ENV_PATH := $(CURDIR)/virtual_env
PYTHON := $(ENV_PATH)/bin/python

### Shell configure. ###
# Enable colors for ouput. Use echo with -e.
RED=\033[0;31m
ORANGE=\033[0;33m
NC=\033[0m

### Configure virtual environment. ###
# Shortcut to set env command before each python cmd.
VENV = source $(ENV_PATH)/bin/activate

# Config is based on two environment files, initalized here.
virtualenv: $(ENV_PATH)/bin/activate

$(ENV_PATH)/bin/activate:
	virtualenv -p /opt/homebrew/bin/python3 $(ENV_PATH) #--distribute $(ENV_PATH)

### Project installation. ###
# Install python requirements.
pip: virtualenv
	$(VENV) && cd $(APP_PATH) && pip install -r $(APP_PATH)/requirements.txt;

#.comp_env:
#	cp .comp_env_template .comp_env

#install: pip

### Migrations. ###
migrate: virtualenv
	$(VENV) && $(PYTHON) $(APP_PATH)/manage.py migrate
