import discord
from discord.ext import commands

import pomice
from pomice import Track, Player

from collections import defaultdict

from core.player import CustomPlayer
from core.embeds import queue_embed, currently_playing_embed, play_embed, requested_embed, get_vote_embed, search_embed
from core.views import VoteView, SkipVoteView, ContinueQueueView


async def setup(bot):
    await bot.add_cog(Music(bot))

class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.pomice = pomice.NodePool()
        self.filter = None
        self.vote_threshold = 0.5
        self.votes = defaultdict(int)

    async def start_nodes(self):
        try:
            await self.pomice.create_node(bot=self.bot, host='127.0.0.1', port=2333,
                                         password='no password 4 u', identifier=str(self.bot.user.id))
            
            
        except pomice.exceptions.NodeConnectionFailure:
            self.bot.log("Failed to connect to the Pomice node.", "ERROR")
            raise pomice.exceptions.NodeConnectionFailure
        self.bot.log("Node is ready!", "SUCCESS")

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: CustomPlayer, track: Track, data: dict) -> None:
        if len(player.queue) == 0:
            await player.destroy()
        else:
            if player.queue.mode == "Anarchy":
                self.bot.log(f"Shuffling queue {' | '.join([x.title for x in player.queue])}", "INFO")
                player.queue.shuffle()
                self.bot.log(f"Shuffled queue {' | '.join([x.title for x in player.queue])}", "INFO")
                
            next_track = player.queue.get()
            if next_track is None:
                print('Hello, World!')
            
            message = None
            users = {}
            members = player.channel.members
            members = [user for user in members if not user.bot and not user.voice.self_deaf]
            if next_track.requester not in members:
                for i, song in enumerate(player.queue):
                    print(f'{i} parsing: {song.title}')
                    if song.requester in members:
                        next_track = song           
                        player.queue.remove(next_track)
                        break
                    
                    else:
                        
                        player.queue.remove(song)
                        
                        if song.requester in player.queue.songs:
                            if song in player.queue.songs[song.requester]:
                                player.queue.songs[song.requester].remove(song)
                        
                            
                        if message is None:
                            print('making message')
                            message = await next_track.ctx.send(f"Skipped **1** Song by {song.requester}")
                        else:
                            print('editing message')
                        
                        if song.requester in users:
                            users[song.requester] += 1
                        else:
                            users[song.requester] = 1
                        next_track = None
                
            if message is not None:
                msg_str = 'Skipped '
                for u in users:
                    # If last one 
                    if u == list(users.keys())[-1] and len(users) > 1:
                        msg_str += f'and {users[u]} songs by {u}'
                        break
                    
                    if users[u] > 1:
                        msg_str += f'**{users[u]}** songs by {u}, '
                    else:
                        msg_str += f'song by {u}, '
                        
                await message.edit(content=msg_str)


            if next_track is None and message is not None:
                print('nothing found')
                return await player.destroy()
            

            return await player.play(next_track)
            

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: Player, track: Track) -> None:
        self.bot.log(f"Track: {track.title} | Started playing", "INFO")
        embed = play_embed(self, track, player.queue.mode)
        if player.queue.songs.get(track.requester.id, None):
            if track in player.queue.songs[track.requester.id]:
                player.queue.songs[track.requester.id].remove(track)
            else: 
                print(f"{track} not in {player.queue.songs[track.requester.id]}")
        else:
            print(f"{track.requester} not in {player.queue.songs}")
            
        await track.ctx.send(embed=embed)
        self.bot.total_songs += 1
    ### JOIN / NOWPLAYING / PLAY

    @commands.hybrid_command(name='join', aliases=['connect', 'summon', 'here', 'summonme'], description="Connect me to a voice channel!")
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None) -> None:
        if not channel:
            channel = getattr(ctx.author.voice, 'channel', None)
            if not channel:
                return await ctx.send('You must be in a voice channel to use this command without specifying the channel argument.')

        await channel.connect(cls=CustomPlayer)
        await ctx.send(f"Joined the voice channel `{channel}`")

        player = ctx.voice_client
        if not player.queue.is_empty:
            view = ContinueQueueView(player, ctx)
            await ctx.send("There's an unfinished queue from a previous session. Do you want to continue it?", view=view)
            await view.wait()

            if view.value is None:
                # No response from user (timeout)
                await ctx.send("No response received, starting fresh.")
                player.queue.clear()
                
                
    @commands.hybrid_command(name='nowplaying', aliases=['np', 'current', 'playing', 'now', 'currentsong'], description="See what's currently playing")
    async def nowplaying(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. Join one, play something and try again")

        player = ctx.voice_client

        if not player.is_playing:
            return await ctx.send("I'm not playing anything right now. Try again later")

        embed = currently_playing_embed(self, player)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='play', aliases=['p', 'add', 'append', 'a', 'blast'], description="Enter a search or a link to play a song!")
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        
        # We need to do some additional logic to determine whether a user can use this 
        
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client
        if ctx.author not in player.channel.members:
            await ctx.send("You must be in the voice channel to use this command.", ephemeral=True, delete_after=5)
            return 
        
        results = await player.get_tracks(query=f'{search}')
        
        if not results:
            raise commands.CommandError('No results were found for that search term.')

        track = results[0]
        track.ctx = ctx
        track.requester = ctx.author
        
        # Add to the internal 'songs' list
        if ctx.author.id not in player.queue.songs:
            player.queue.songs[ctx.author.id] = []
        player.queue.songs[ctx.author.id].append(track)
            
        if player.queue.is_empty and not player.is_playing:
            embed = requested_embed(self, track, pos=0)
            await ctx.send(embed=embed)
            await player.play(track=track)
        else:

            position = player.queue.put(track)
            embed = requested_embed(self, track, pos=position)
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='search', aliases=['lookfor'])
    async def search(self, ctx: commands.Context, search_term: str) -> None:
        """Search for a Song"""
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. Use /join")
        player = ctx.voice_client
        results = await player.get_tracks(query=search_term)
        if len(results) > 25:
            results[:25]
        embed = search_embed(self, ctx.author, results, search_term)
        return await ctx.send(embed=embed)
        
## QUEUE, CLEAR, REMOVE, VOTE
    @commands.hybrid_command(name='queue', aliases=['q', 'list', 'l'], description="Views the Queue!")
    async def view_queue(self, ctx: commands.Context, page: int = 1) -> None:
        """Command for Seeing the Queue 

        Args:
            page (int, optional): Page Number. Defaults to 1.

        Returns:
            Embed: Embed of max size 25 of Songs listed.
        """
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel. Join one, play something and try again")

        player = ctx.voice_client
        # Embed now takes an index
        # Could do with a nice view 
        embed = queue_embed(self, player, page)
        await ctx.send(embed=embed)
    
    @commands.command(name="flood",hidden=True)
    @commands.is_owner()
    async def flood(self, ctx, r = 25, *, search="rick astley"):
        """Dirty Secret Command

        Args:
            r (int, optional): Amount to Spam. Defaults to 25.
            search (str, optional): Item To spam. Not Very consistent. Defaults to "rick astley".
        """
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if not ctx.voice_client:
            return
        # Adds 25 counts of rick astley to the queue 
        player = ctx.voice_client
        for i in range(r):
            results = await player.get_tracks(query=f'{search}')
            track = results[0]
            track.ctx = ctx
            track.requester = ctx.author
            if player.queue.is_empty and not player.is_playing:
                await player.play(track=track)
                
            else:
                player.queue.put(track)
            self.bot.log(f"{i} {search}s")

        
        
    ## CLEAR COMMAND ----------------------------------------------------
    
    @commands.command(name='clear', aliases=['c'], description='Clears the queue', hidden=True)
    @commands.is_owner()
    async def clear(self, ctx: commands.Context) -> None:
        """Clear Command

        Args:
            ctx (_type_): _description_

        Returns:
            _type_: _description_
        """
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel")

        # Owner only
        if ctx.author.id == 1166877695754375220:
            player = ctx.voice_client
            player.queue.clear()
            await ctx.send("Cleared the queue")
        else:
            await ctx.send("You don't have permission to use this command.")
    
    ## REMOVE COMMAND --------------------------------------------------------
    
    @commands.hybrid_command(name='remove', aliases=['delete', 'del', 'r'], description="Remove a song from the queue")
    async def remove(self, ctx: commands.Context, index: int) -> None:
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel.")
        
        player = ctx.voice_client
        queue = player.queue
        s = queue.get_user_song(ctx.author, index)
        if isinstance(s, str):
            return await ctx.send(s)
        
        else:
            song_to_remove = s
            if ctx.author == song_to_remove.requester or ctx.author.guild_permissions.manage_messages:
                queue._queue.remove(song_to_remove)
                if player.queue.songs.get(song_to_remove.requester.id, None):
                    player.queue.songs[song_to_remove.requester.id].remove(song_to_remove)
                
                embed = discord.Embed(title = f"Removed Song {index}", description=f"**Removed:** `{song_to_remove.title}`\nRequested by: `{song_to_remove.requester}` | Deleted by `{ctx.author}`", color=discord.Color.random())
                embed.set_footer(text=f'Made with :3 by Flo ❤️ | Queue Mode: {player.queue.get_mode()}', icon_url=self.bot.user.display_avatar.url)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("You don't have permission to remove this track.")

    ## SKIP COMMAND --------------------------------------------------------
    
    @commands.hybrid_command(name='skip', aliases=['s'], description="Skip the Current Song")
    async def skip(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel.")

        player = ctx.voice_client

        if len(ctx.author.voice.channel.members) == 1:
            await ctx.send('You are alone in the voice channel, skipping.')
            await player.stop()
        elif ctx.author == player.current.ctx.author:
            await ctx.send('This is your song, skipping.')
            await player.stop()
        elif ctx.author.guild_permissions.manage_messages:
            await ctx.send('Mod Perms: Skipping.')
            await player.stop()
        else:
            user_count = len(ctx.author.voice.channel.members)
            view = SkipVoteView(user_count=user_count, player=player)

            embed = discord.Embed(
                title="Vote to Skip",
                description="A vote has been started to skip the current song.",
                color=discord.Color.blue()
            )

            await ctx.send(embed=embed, view=view)

    ## LEAVE COMMAND --------------------------------------------------------
    
    @commands.hybrid_command(name='leave', aliases=['disconnect', 'dc', 'stop', 'quit','goaway','plsgo','pleaseleave'], description="Stop Playing")
    async def leave(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("I'm Sorry, Leaving is disabled pending security testing. Please wait for the queue to end, and I'll leave on my own." ,delete_after=5)
        else:
            player = ctx.voice_client
            await player.disconnect()
            await ctx.send('Goodbye :3')
    
    ## Voting and Queue Modes -----------------------------------------------------------
    
    @commands.hybrid_command(name='set_mode', aliases=['set', 'changemode', 'mode', 'votefair', 'democracy', 'vote'], description="Propose a vote to change the queue mode")
    async def set_mode(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("You need to be in a voice channel to start a vote.")

        user_count = len(ctx.author.voice.channel.members)
        if user_count <= 1:
            return await ctx.send("There must be more than one user in the voice channel to start a vote.")
        print('1')
        user_count = len(ctx.guild.voice_client.channel.members)
        view = VoteView(music_cog=self, user_count=user_count)
        print('2')
        embed = get_vote_embed(self, user_count, {})
        await ctx.send("Vote for the next queue mode!", embed=embed, view=view)

    @commands.hybrid_command(name='set_threshold', aliases=['change_vote', 'threshold'], description="Set the vote threshold for mode change")
    async def set_threshold(self, ctx, threshold: float):
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.send("You don't have permission to change the vote threshold.")
        if 0 < threshold <= 1:
            self.vote_threshold = threshold
            await ctx.send(f"Vote threshold set to {int(threshold * 100)}%")
        else:
            await ctx.send("Invalid threshold. Provide a number between 0 and 1.")


    ### FILTERS ###
    ## Timescale.nightcore = 200%
    ## Timescale.vaporwave = 50%
    # 
    # https://pomice.readthedocs.io/en/latest/api/filters.html
    # https://pomice.readthedocs.io/en/latest/hdi/filters.html
    # We reset on every filter to avoid filter gore.
    # Can change tho
    
  
