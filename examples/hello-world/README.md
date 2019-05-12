
imagine we have this `main.c` file:

```c

#include <stdio.h>

//# names = ['Oliver', 'Jack', 'Harry', 'James', 'John']

int main()
{
	//@ for name in names:
	printf("Hello ${name}!\n");
	//@ end for
	return 0;
}

```

we open this file and pass it to generate\_code function:

```python
#!/usr/bin/python3

import pycro

env = pycro.CompilerEnvironment(language = 'c')

with open('main.c') as infile:
    with open('main.c.py', 'w') as outfile:
        pycro.generate_code(infile, outfile, env)

```

another file will be created named `main.c.py`:

```python
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
```

now we can compile and execute `main.c.py` using the following code:

```python
#!/usr/bin/python3

import pycro

env = pycro.ExecutorEnvironment()

with open('main.c.py') as infile:
    with open('_main.c', 'w') as outfile:

        code_object = pycro.compile_generated_code(infile.read(), infile.name)

        pycro.execute_code_object(code_object, outfile, env)

```

the generated result saved as `_main.c`:

```c

#include <stdio.h>


int main()
{
	printf("Hello Oliver!\n");
	printf("Hello Jack!\n");
	printf("Hello Harry!\n");
	printf("Hello James!\n");
	printf("Hello John!\n");
	return 0;
}

```

it's time to compile `_main.c`:

```
$ gcc _main.c -o main
```

and run `./main`:

`$ ./main`:

```
Hello Oliver!
Hello Jack!
Hello Harry!
Hello James!
Hello John!
```

