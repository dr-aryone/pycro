
README.md: makefile main.c main.pycro.c main.c.py
	@echo making '$@'
	echo "# hello world example" > $@
	echo '`main.c`:' >> $@
	echo '```' >> $@
	cat main.c >> $@
	echo '```' >> $@

main: main.pycro.c
	gcc $< -o $@

main.pycro.c: main.c.py ../compile.py
	../compile.py $< > $@

main.c.py: main.c ../generate.py
	../generate.py c $< > $@

../generate.py ../compile.py:
	cd ../.. && $(MAKE) copy-to-pylibs

