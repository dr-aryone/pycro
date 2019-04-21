
PACKAGE_FOLDER = package/pycro

package: pycro __init__.py __main__.py
	mkdir -p $(PACKAGE_FOLDER)
	cp pycro $(PACKAGE_FOLDER)/_pycro.py
	cp __init__.py $(PACKAGE_FOLDER)/__init__.py
	cp __main__.py $(PACKAGE_FOLDER)/__main__.py

