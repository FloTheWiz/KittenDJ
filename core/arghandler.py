import argparse 

from typing import Union

"""
Argparse Stuff
Add to as you wish.
"""
def make_parser():
    parser = argparse.ArgumentParser('main')
    parser.add_argument('--token', type=str, help='The bot token')
    parser.add_argument('--prefix', type=str, help='The bot prefix')
    parser.add_argument('--cogs', type=str, help='The bot cogs')
    parser.add_argument('--description', type=str, help='The bot description')
    return parser

def parse_logic(parser: argparse.ArgumentParser, config: dict) -> Union[dict, bool]:
    """Parses Logic for Command Handling.
    This is a baseline, and other arguments can easily be added to the object gained from the make_parser() above.
    

    Args:
        parser (argparse.ArgumentParser): Parser object, hopefully with some commands.
        config (dict): Dict from main.py

    Returns:
        Union[dict, bool]: If all goes according to plan, returns config. If not, returns False
    """
    args = parser.parse_args()
    if args.token:
        config['token'] = args.token
    elif config.get('token') is None:
        print('No Token Provided in Config, and None Provided with --token. Forced to Terminate')
        return 0
    if args.prefix:
        config['prefix'] = args.prefix
    if args.cogs:
        config['cogs'] = args.cogs
    if args.description:
        config['description'] = args.description
    return config
