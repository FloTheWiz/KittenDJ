from datetime import datetime 
import time
import pomice 

from discord.ext import commands
import discord 
from typing import Optional, List


class DJ(commands.Bot):
    def __init__(self, version_str: str, cogs: List[str],  prefix: str = ";", description: str = "Kittens that keep you jamming!") -> None:
        # Allowed Mentions 
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        
        # Intents, for more info: https://discordpy.readthedocs.io/en/latest/intents.html
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        
        # Initialize Bot
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            description=description,
            allowed_mentions=allowed_mentions)
        self.boot_start = time.time()
        self._cogs = cogs 
        self._uptime = datetime.now()
        self._version = version_str
    
    
    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
        
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        raise error
    
    async def on_ready(self) -> None:
        print(
            f"Username: {self.user} | {discord.__version__=}\nGuilds: {len(self.guilds)} | Users: {len(self.users)}|Prefix: {self.command_prefix}"
        )
        print(
            f"Invite Link: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=52288&scope=bot%20applications.commands"
        )
        print(f"Ready: {self.user} (ID: {self.user.id})")
    
    async def startup(self) -> None:
        await self.wait_until_ready()
        await self.cogs["Music"].start_nodes()
        print("Music Nodes Started")
        await self.tree.sync()
        print("Ready and Tree Synced")
        done = time.time()
        print(f"Booted in: {done - self.boot_start:.2f} seconds")
        
    
    async def setup_hook(self) -> None:
        """Initialize cogs"""

        for cog in self._cogs:
            try:
                print('Loading: %s' % cog)
                await self.load_extension(cog)
            except Exception as e:
                print('Failed to load: %s - %s' % cog % e)
            finally:
                print('Loaded: %s' % cog)                
        self.loop.create_task(self.startup())
        