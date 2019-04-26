

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

# --- importing module ---

# this import will failed
import:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python -ic "import pycro" -OO)

import3:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python3 -ic "import pycro" -OO)

# --- for commiters ---

AUTO_COMMITS = makefile README.md _README.md misc .gitignore

.PHONY:
commit-all:
	git add $(AUTO_COMMITS)
	git commit -m "update everything!"

# --- building & publishing ---

.PHONY:
clean:
	rm -rd dist/
	rm -rd build/
	rm -rd pycro.egg-info/

.PHONY:
build: pycro.py
	python3 setup.py sdist bdist_wheel

.PHONY:
test-publish: build
	python3 -m twine upload \
		--repository-url https://test.pypi.org/legacy/ \
		dist/*

