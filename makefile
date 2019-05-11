
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

# *** generate README.md ***

README.md: README.m4.md todos.md
	m4 $< > $@


# *** copy to pylibs ***

copy-to-pylibs: pycro.py
	cp -f pycro.py ~/pylibs/

# *** generate todos.md ***

todos.md: pycro
	@echo making $@
	@echo 'in `pycro`:' > $@
	@echo '```' >> $@
	@grep "\s*#\s*TODO" -n pycro | \
			sed -E 's/([0-9]+):\s*(.*?)\s*$$/\1: \2/g' >> $@
	@echo '```' >> $@

# *** making virtual environment ***

venv:
	python3 -m virtualenv -p python3 venv

delete-venv:
	rm -rdf venv

# *** importing module ***

# this import will failed
import:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python -ic "import pycro" -OO)

import3:
	$(MAKE) package
	(cd $(PACKAGE_FOLDER) && python3 -ic "import pycro" -OO)



# *** for commiters ***

PACKAGES = pycro.py package

.PHONY:
commit-packages:
	git add $(PACKAGES)
	git commit -m "update packages"

READMES = README.*

.PHONY:
commit-readmes:
	git add $(READMES)
	git commit -m "update READMEs"

AUTO_COMMITS = makefile misc .gitignore todos.md

.PHONY:
commit-all:
	git add $(AUTO_COMMITS)
	git commit -m "update everything!"



# *** building & publishing ***

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

