
from bot import DJ
from core.arghandler import make_parser, parse_logic

cogs = [
    'cogs.music',
    'cogs.admin',
    'cogs.filters' # Filters is broken for now
]

TOKEN = 'Get your own Token'
version_str = '1.1.0'
prefix = ';'
description = 'Meow Bop MeowMeowMeow Bop'

##
BOT_CONFIG = {
    'token':TOKEN,
    'id': '1',
    'prefix':';',
    'cogs':cogs,
    'version':version_str,
    'description': description,
    'text_channel':'419065933844316162', # Music
    'voice_channel':'419066880901251072', # Music VC
    'activity':'use /play or ;play to play music!'
}

if __name__ == '__main__':
    parser = make_parser()
    config = parse_logic(parser, BOT_CONFIG)
    if config == 0:
        exit(0)
    bot = DJ(config)
    bot.run(config['token'])
