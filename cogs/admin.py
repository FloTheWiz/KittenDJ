import discord
from discord.ext import commands
import io
import contextlib
import traceback

from core.embeds import about_me_embed
async def setup(bot):
    await bot.add_cog(Admin(bot))
    
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last = None
    def last_or_cog(self, cog: str) -> str:
        if cog.lower() == "last" or cog.lower() == "l":
            if self.last is None:
                return None
            else:
                cog = self.last 
        else:
            self.last = cog.lower()
        return cog.lower()
    
    @commands.command(name='eval')
    @commands.is_owner()
    async def eval_code(self, ctx, *, code: str):
        # Clean up the code block if it's wrapped in triple backticks
        error = False 
        if code.startswith('```') and code.endswith('```'):
            code = code[3:-3].strip()

        # Prepare the environment
        local_variables = {
            'discord': discord,
            'commands': commands,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            
        }
        if ctx.voice_client:
            local_variables['player'] = ctx.voice_client
        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                # Use exec to handle multi-line code
                exec(code, globals(), local_variables)
                # If the last line of the code is an expression, evaluate it
                if code.splitlines()[-1].strip().startswith("return"):
                    result = eval(code.splitlines()[-1][7:], globals(), local_variables)
                else:
                    result = None
        except Exception as e:
            error = True
            result = f'Error: {e}\n{traceback.format_exc()}'
        
        output = stdout.getvalue()
        if result is None:
            result = output or "No output."
        else:
            result = f"{output}{result}"
        if error:
            return await ctx.send(f"```py\n{result}\n```",delete_after=10)
        await ctx.send(f"```py\n{result}\n```")
    
    @commands.command(name = "load", aliases=["lcog"])
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        cog = self.last_or_cog(cog)
        if cog is None:
            await ctx.send("No last cog found!")
            return 
        try:
            await self.bot.load_extension("cogs."+cog)
        except Exception as e:
            await ctx.send(f'**`[{cog.upper()}] -> ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**` [{cog.upper()}] -> SUCCESS`**')

    @commands.command(name= "unload", aliases=["ucog", "ulcog"])
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        cog = self.last_or_cog(cog)
        if cog is None:
            await ctx.send("No last cog found!")
            return 
        try:
            await self.bot.unload_extension("cogs."+cog)
        except Exception as e:
            await ctx.send(f'**` [{cog.upper()}] -> ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`[{cog.upper()}] -> SUCCESS`**\N{PISTOL}')

    @commands.command(name='reload', aliases=["rlcog","rcog"])
    @commands.is_owner()
    async def rel(self, ctx, *, cog: str):
        
        cog = self.last_or_cog(cog)
        if cog is None:
            await ctx.send("No last cog found!")
            return 
        try:
            await self.bot.unload_extension("cogs."+cog)
            await self.bot.load_extension("cogs."+cog)
        except Exception as e:
            await ctx.send(f'**`[{cog.upper()}] -> ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`[{cog.upper()}] -> SUCCESS`**\N{PISTOL}')
            
    @commands.command(name='shinobu', hidden=True)
    async def p(self, ctx):
        await ctx.send("**I love you** <@!{}> {}".format(ctx.author.id, ":3"))
        
    
    @commands.command(name='about', aliases=['info'])
    async def info(self, ctx):
        embed = about_me_embed(self)
        await ctx.send(embed=embed)
