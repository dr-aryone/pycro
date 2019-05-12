<!-- @ divert 0 -->

<!-- @ def run_command(command, syntax=''): -->
__`$ ${command}`__:
```${syntax}
<!-- @ run command -->
```
<!-- @ end def -->

<!-- @ def include_file(filename, syntax=''): -->
```${syntax}
<!-- @ place filename -->
```
<!-- @ end def -->

<!-- @ divert -->

imagine we have this `main.c` file:

<!-- # include_file("main.c", syntax='c') -->

we open this file and pass it to generate\_code function:

<!-- # include_file("generate.py", syntax="python") -->

another file will be created named `main.c.py`:

<!-- # include_file("main.c.py", syntax="python") -->

now we can compile and execute `main.c.py`:

<!-- # include_file("compile.py", syntax="python") -->

the generated result saved as `_main.c`:

<!-- # include_file("_main.c", syntax="c") -->

it's time to compile `_main.c` and see the result:

```
$ gcc main.c -o main
```

here is the result:

<!-- @ run "./main" -->


