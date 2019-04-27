
PACKAGE_FOLDER = package
PYCRO_PACKAGE_NAME = pycro
PYCRO_FOLDER = $(PACKAGE_FOLDER)/$(PYCRO_PACKAGE_NAME)

package: pycro __init__.py __main__.py
	mkdir -p $(PYCRO_FOLDER)
	cp pycro $(PYCRO_FOLDER)/_pycro.py
	cp __init__.py $(PYCRO_FOLDER)/__init__.py
	cp __main__.py $(PYCRO_FOLDER)/__main__.py

pycro.py: pycro
	cp -f pycro pycro.py

# --- generate README.md ---


# --- making virtual environment ---
venv:
	python3 -m virtualenv -p python3 venv

delete-venv:
	rm -rdf venv

# --- importing module ---

# this import will failed
import:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python -ic "import pycro" -OO)

import3:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python3 -ic "import pycro" -OO)

# --- for commiters ---

.PHONY:
commit-packages:
	git add pycro.py package
	git commit -m "update pycro.py"

.PHONY:
commit-readme:
	git add _README.md README.md
	git commit -m "update readme's"

AUTO_COMMITS = makefile misc .gitignore

.PHONY:
commit-all:
	git add $(AUTO_COMMITS)
	git commit -m "update everything!"

# --- building & publishing ---

.PHONY:
clean:
	rm -rdf dist/
	rm -rdf build/
	rm -rdf pycro.egg-info/
	rm -rdf __pycache__/

.PHONY:
build: pycro.py
	python3 setup.py sdist bdist_wheel

.PHONY:
test-publish: build
	python3 -m twine upload \
		--repository-url https://test.pypi.org/legacy/ \
		dist/*

