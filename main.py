from bot import DJ
from discord.ext import commands

cogs = [
    'cogs.music',]

version_str = '0.9'
prefix = ';'
description = 'Meow Bop MeowMeowMeow Bop'
token = 'YOUR_TOKEN_HERE'
if __name__ == '__main__':
    bot = DJ(version_str, cogs, prefix, description)
    bot.run(token)