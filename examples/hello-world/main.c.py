__outfile__.write('\n');
__outfile__.write('#include <stdio.h>\n');
__outfile__.write('\n');
names = ['Oliver', 'Jack', 'Harry', 'James', 'John']
__outfile__.write('\n');
__outfile__.write('int main()\n');
__outfile__.write('{\n');
for name in names:
	__outfile__.write('\tprintf("Hello ');__outfile__.write(str(name));__outfile__.write('!\\n");\n');
__outfile__.write('\treturn 0;\n');
__outfile__.write('}\n');
__outfile__.write('\n');
