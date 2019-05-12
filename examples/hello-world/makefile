
README.md: main.c generate.py main.c.py compile.py _main.c main
	../../pycro README.pycro.md -o README.md

main: _main.c
	gcc $< -o $@

_main.c: compile.py main.c.py
	./compile.py

main.c.py: generate.py main.c
	./generate.py

.PHONY: generate.py compile.py
generate.py compile.py:
	cd ../.. && $(MAKE) copy-to-pylibs

.PHONY:
clean:
	rm -f main.c.py
	rm -f _main.c
	rm -f main

