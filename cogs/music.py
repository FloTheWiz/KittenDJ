import discord 
from discord.ext import commands 
from discord.ui import View, Button
import pomice 

from pomice import Track, Playlist, Queue, Player 

class SilenceButton(Button):
    def __init__(self, track: Track):
        super().__init__(label="Silence", style=discord.ButtonStyle.green, emoji="🔇")
        self.track = track
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(suppress=True)

class MessageButton(Button):
    def __init__(self):
        super().__init__(label="Message", style=discord.ButtonStyle.green, emoji="✉️")
    
    async def callback(self, interaction: discord.Interaction):
        # Try to DM the user who presses the button with the interaction.response text 
        try:
            await interaction.user.send(interaction.message.content)
        except discord.errors.Forbidden:
            await interaction.response.send_message("I can't DM you.", ephemeral=True)

class CustomPlayer(Player):
    def __init__(self, *args, **kwargs):
        self.queue = Queue()
        super().__init__(*args, **kwargs)
    
    
def get_length(milliseconds: int) -> str:
    total_seconds = milliseconds / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def bar(position, length):
    bar_char = '—'
    location_char = '⏵'
    bar_length = 15
    
    index = int((position / length) * bar_length)
    length_list = [bar_char] * bar_length
    length_list[index] = location_char
    return ''.join(length_list)
    
    



def queue_embed(self, player: Player) -> discord.Embed:
    total_time = sum(track.length for track in player.queue)
    embed = discord.Embed(
        title=f"Queue - {len(player.queue)} tracks ({get_length(total_time)})",
        description = "\n".join(f"### **{i+1}.** [{track.title}](<{track.uri}>)\n **Length:** `[{get_length(track.length)}]`- **From:** `{track.requester}`" for i, track in enumerate(player.queue)),
        color = discord.Color.random()
    )
    if len(player.queue) == 0:
        embed.description += 'Use play to add songs!'
        
    if player.is_playing:
        embed.set_author(name=f"Now Playing: {player.current.title} - {get_length(player.adjusted_position)}", url=player.current.uri, icon_url=player.current.thumbnail)
    embed.set_footer(text='Made with :3 by Flo ❤️',icon_url=self.bot.user.display_avatar.url)
    return embed


def currently_playing_embed(self, player: Player = None) -> discord.Embed:
    track = player.current
    embed = discord.Embed(
        title=track.title, 
        url=track.uri, 
        color=discord.Color.random(),
        description=f"`{get_length(player.adjusted_position)} |{bar(player.adjusted_position, player.adjusted_length)}| {get_length(player.adjusted_length)}`\n**Requested by {track.ctx.author }**")
    embed.set_author(name="ıllı.ılıllıl.ılı - Now Playing - ılı.lıllılı.ıllı",icon_url=track.thumbnail)
    embed.set_image(url=track.thumbnail)
    embed.set_footer(text='Made with :3 by Flo ❤️',icon_url=self.bot.user.display_avatar.url)
    return embed

def play_embed(self, track: Track) -> discord.Embed:
    # Often, the discord embed won't have a song length for player.adjusted_length or player.adjusted_position
    # So we'll use this, using the track length
    # This could likely be 1 function, but it's easier to read this way
    
    embed = discord.Embed(
        title=track.title, 
        url=track.uri, 
        color=discord.Color.random(),
        description=f"**Requested by {track.ctx.author }** - `{get_length(track.length)}`")
    embed.set_author(name="Now Playing",url=track.thumbnail)
    embed.set_image(url=track.thumbnail)
    embed.set_footer(text='Made with :3 by Flo ❤️',icon_url=self.bot.user.display_avatar.url)
    return embed

def requested_embed(self, track: Track, pos: int = 0) -> discord.Embed:
    embed = discord.Embed(
        title=track.title,
        url=track.uri,
        color=discord.Color.random(),
        description=f"**Requested by {track.ctx.author }** | `{get_length(track.length)}`")
    author_str = "Requested."
    if pos == 0: 
        author_str += ' | [Playing Now!]'
    else:
        author_str += f" | [Position: {pos}]"
        
        
    embed.set_author(name=author_str,url=track.thumbnail)
    embed.set_footer(text='Made with :3 by Flo️ ❤️',icon_url=self.bot.user.display_avatar.url)
    
    
    return embed
    
async def setup(bot):
    await bot.add_cog(Music(bot))


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.pomice = pomice.NodePool()
        self.filter = None
    async def start_nodes(self):
        try:
            await self.pomice.create_node(bot=self.bot, host='127.0.0.1', port=2333,
                                     password='correct_horse_battery_staple', identifier='MAIN')
        except pomice.exceptions.NodeConnectionFailure:
            raise pomice.exceptions.NodeConnectionFailure
        print("Node is ready!")
    
    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track: Track, data: dict) -> None:
        if len(player.queue) == 0:
            # Timeout 
            await player.destroy()
        else:
            next_track = player.queue[0]
            await player.play(next_track) # Pop it from queue
            player.queue.remove(next_track)
        
    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: Player, track: Track) -> None:
        print(f"Started playing: {track.title}")
        play = play_embed(self, track)
        # Test 
        await track.ctx.send(embed=play)
        recommendation_list = await player.get_recommendations(track=track)
        if recommendation_list is not None:
            print('| '.join([x.title for x in recommendation_list]))
        
    
    @commands.hybrid_command(name='remove',aliases=['delete','del','r'],description="Remove the Song at the current position")
    async def remove(self, ctx: commands.Context, index: int) -> None:
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel.")

        player = ctx.voice_client
        if index > len(player.queue):
            return await ctx.send("There are only {} tracks in the queue.".format(len(player.queue)))
        elif index < 1:
            if index == '-1':
                pass 
            return
        
        if ctx.author == player.queue[index-1].requester or ctx.author.guild_permissions.manage_messages:
            song = player.queue[index-1]
            player.queue.remove(song)
            await ctx.send("Track {} - {} removed.".format(index, song))
        else:
            return await ctx.send("You don't have permission to remove this track.")
    
    @commands.hybrid_command(name='skip',aliases=['s'],description="Skip the Current Song")
    async def skip(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel.")

        player = ctx.voice_client
        if len(ctx.author.voice.channel.members) == 1:
            print('1')
            await player.stop()
        if ctx.author == player.current.ctx.author:
            return await player.stop()
            print('2')
        if ctx.author.guild_permissions.manage_messages:
            print('3')
            return await player.stop()
    
    @commands.hybrid_command(name='nightcore',aliases=['nc','gottagofast','speedy'],description='Nightcore Time!')
    async def nightcore_filter(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel")
           
        player = ctx.voice_client 
        if self.filter != "nightcore":
            self.filter = 'nightcore'
            await player.add_filter(pomice.filters.Timescale.nightcore(),fast_apply=True)
            await ctx.send("Nightcore Mode Activated!")
            return 
        else:
            self.filter = None 
            await player.reset_filters(fast_apply=True)
            await ctx.send("Nightcore Mode Disabled")
    
    @commands.hybrid_command(name='vaporwave',aliases=['vw','vaportime'],description='Vaporwave Time!')
    async def vaporwave_filter(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel")
           
        player = ctx.voice_client 
        if self.filter != "vaporwave":
            self.filter = 'vaporwave'
            await player.add_filter(pomice.filters.Timescale.vaporwave(),fast_apply=True)
            await ctx.send("Vaporwave Mode Activated!")
            return 
        else:
            self.filter = None 
            await player.reset_filters(fast_apply=True)
            await ctx.send("Vaporwave Mode Disabled")
    
    
        
        
    @commands.hybrid_command(name='karaoke',aliases=['k','singalong','karoake','kar'])
    async def karaoke_filter(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel")
        
        player = ctx.voice_client
        if self.filter != "karaoke":
            self.filter = 'karaoke'
            await player.add_filter(pomice.filters.Karaoke(tag='karoake'),fast_apply=True)
            await ctx.send("Karaoke Mode Activated!")
            return
        else:
            self.filter = None
            await player.reset_filters(fast_apply=True)
            await ctx.send("Karaoke Mode Disabled")
        

    @commands.hybrid_command(name='leave',
                      aliases=[
                          'disconnect',
                          'dc',
                          'stop',
                          'quit',
                          ],
                          description="Stop Playing")
    async def leave(self, ctx: commands.Context) -> None:
        # User should either be the only user, there should be NO users, OR the user should be a mod with manage_messages
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. How do you expect us to leave?", ephemeral=True)
        members = ctx.voice_client.channel.members
        
        if len(members) > 1:
            if ctx.author not in members and not ctx.author.guild_permissions.manage_messages:
                return await ctx.send("You don't have permission to use this command.", ephemeral=True)
        else:
            if ctx.author not in members:
                return await ctx.send("You can't leave if you're the only user in the voice channel.", ephemeral=True)
        if ctx.author.voice.channel == ctx.voice_client.channel:
            await ctx.voice_client.disconnect()
            await ctx.send("Bye!")
        

    @commands.hybrid_command(name='join',
                      aliases=[
                          'connect',
                          'summon',
                          'here',
                          'summonme',
                          ],
                          description="Connect me to a voice channel!")
    async def join(self, ctx: commands.Context, *, channel: discord.TextChannel = None) -> None:
        if not channel:
            channel = getattr(ctx.author.voice, 'channel', None)
            if not channel:
                await ctx.send('You must be in a voice channel to use this command without specifying the channel argument.', ephemeral=True)
        await ctx.author.voice.channel.connect(cls=CustomPlayer)
        await ctx.send(f"Joined the voice channel `{channel}`")


    @commands.hybrid_command(name='nowplaying',
                      aliases=[
                          'np',
                          'current',
                          'playing',
                          'now'
                          'currentsong'
                          ],
                          description="See what's currently playing")
    async def nowplaying(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. Join one, play something and try again", ephemeral=True)

        player = ctx.voice_client

        if not player.is_playing:
            return await ctx.send("I'm not playing anything right now. Try again later", ephemeral=True)
        embed = currently_playing_embed(self, player)

        await ctx.send(embed=embed)



    @commands.hybrid_command(name='play',
                      aliases=[
                          'p',
                          'add',
                          'append',
                          'a',
                          'blast',
                      ],
                      description="Enter a search or a link to play a song!")
    async def play(self, ctx, *, search: str) -> None:
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client

        results = await player.get_tracks(query=f'{search}')
        if not results:
            raise commands.CommandError('No results were found for that search term.')
        track = results[0]
        track.ctx = ctx
        track.requester = ctx.author
        
        if player.queue.is_empty and not player.is_playing:
            
            embed = requested_embed(self, track, pos=0)
            await ctx.send(embed=embed)
            await player.play(track=track)
        else:
            position = len(player.queue) + 1
            embed = requested_embed(self, track, pos=position)
            await ctx.send(embed=embed)
            player.queue.put(track)
            
    @commands.hybrid_command(name='queue',
                      aliases=[
                          'q',
                          'list',
                          'l'
                      ])
    async def view_queue(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. Join one, play something and try again", ephemeral=True)
        
        player = ctx.voice_client
        embed = queue_embed(self, player)
        await ctx.send(embed=embed)
                      
    
   