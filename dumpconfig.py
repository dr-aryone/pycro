#!/usr/bin/python3

import sys
import configparser

def main():
    if len(sys.argv) != 2:
        print('usage: {} CONFIG'.format(sys.argv[0]))
        sys.exit(0)

    parser = configparser.ConfigParser(
            defaults = None,

            dict_type = dict,
            allow_no_value = False,

            delimiters = ('=', ),

            comment_prefixes = ('#', ),
            inline_comment_prefixes = None,

            strict = True,

            empty_lines_in_values = False,

            default_section = "DEFAULT",

            interpolation = None,

            converters = {},
            )

    with open(sys.argv[1]) as infile:
        parser.read_file(infile)

    for section_name in parser:
        print( '[{}]'.format(section_name) )

        section = parser[section_name]

        for name in section:

            print( '    {}: {!r}'.format(name, section[name]))

if __name__ == '__main__':
    main()

