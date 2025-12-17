import argparse
import json
import subprocess
import sys

def do_it(flat  :str,
          indent:int|None):
    
    return json.dumps(json.loads(flat), indent=indent) if flat.strip() else flat

def main(indent:int|None=2):

    class A:
        ARGS        = 'args'
        COMMAND     = 'command'
        INTERACTIVE = 'interactive'
    ap = argparse.ArgumentParser(description='JSON beautifier for literals and command outputs')
    group = ap.add_mutually_exclusive_group()
    group.add_argument(f'--{A.COMMAND}','-c', 
                    help='interpret argument(s) as a command\nOtherwise, expect single argument as JSON literal',
                    action='store_true')
    group.add_argument(f'--{A.INTERACTIVE}','-i',
                    help='interactive input - useful if you want to pass the JSON literal without escaping any characters (quotes, etc)',
                    action='store_true')
    ap.add_argument(f'{A.ARGS}', 
                    help='arguments - JSON literal or command token(s)',
                    nargs='*')
    # parse args
    get = ap.parse_args().__getattribute__
    args:list[str] = get(A.ARGS)
    is_command:bool = get(A.COMMAND)
    interactive:bool = get(A.INTERACTIVE)
    # do it
    if not is_command:
        if not interactive:
            if len(args) != 1:
                raise Exception('Expected single argument as JSON literal')
            flat=args[0]
        else:
            flat=input('Enter JSON literal: ')
    else:
        flat= subprocess.run(args,
                             shell=True,
                             capture_output=True).stdout.decode()
    print(do_it(flat  =flat,
                indent=indent))

if __name__ == '__main__': main()
