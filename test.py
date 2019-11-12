import argparse


def exit():
    pass


parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

parser_sub = subparser.add_parser("+exit", help="BOTを終了します")
parser_sub.set_defaults(handler=exit)

args = parser.parse_args(["+exit", ])

print(args)
