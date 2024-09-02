import discord  
from pomice import Player, Track
from .utils import get_length, bar

# Mode descriptions for the vote embed
MODE_DESCRIPTIONS = {
    "Normal": "Plays songs in the order they were added.",
    "Anarchy": "Randomizes the queue, so songs play in no particular order.",
    "Round Robin": "Each user gets their next song played in sequence, no matter when they added it.",
    "Fair": "Balances song plays among users, ensuring everyone gets their turn."
}

def queue_embed(self, player: Player) -> discord.Embed:
    if player.queue.get_mode() == "Anarchy":
        description = "\n".join(
            f"### **{i+1}?.** [{track.title}](<{track.uri}>)\n **Length:** `[{get_length(track.length)}]`- **From:** `{track.requester}`"
            for i, track in enumerate(player.queue)
        )
    else:
        description = "\n".join(
            f"### **{i+1}.** [{track.title}](<{track.uri}>)\n **Length:** `[{get_length(track.length)}]`- **From:** `{track.requester}`"
            for i, track in enumerate(player.queue)
        )
    
    total_time = sum(track.length for track in player.queue)
    embed = discord.Embed(
        title=f"Queue - {len(player.queue)} tracks ({get_length(total_time)})",
        description=description,
        color=discord.Color.random()
    )
    
    if len(player.queue) == 0:
        embed.description += "Use ;play or /play to add songs!"
    
    if player.is_playing:
        embed.set_author(
            name=f"Now Playing: {player.current.title} - {get_length(player.adjusted_position)}",
            url=player.current.uri, 
            icon_url=player.current.thumbnail
        )
    
    embed.set_footer(text=f'Made with :3 by Flo ❤️ | Queue Mode: {player.queue.get_mode()}', icon_url=self.bot.user.display_avatar.url)
    return embed


def currently_playing_embed(self, player: Player) -> discord.Embed:
    # possible check for if player is somehow not playing
    track = player.current
    embed = discord.Embed(
        title=track.title, 
        url=track.uri, 
        color=discord.Color.random(),
        description=f"`{get_length(player.adjusted_position)} |{bar(player.adjusted_position, player.adjusted_length)}| {get_length(player.adjusted_length)}`\n**Requested by {track.ctx.author }**"
    )
    embed.set_author(name="ıllı.ılıllıl.ılı - Now Playing - ılı.lıllılı.ıllı", icon_url=track.thumbnail)
    embed.set_image(url=track.thumbnail)
    embed.set_footer(text=f'Made with :3 by Flo ❤️ | Queue Mode: {player.queue.get_mode()}', icon_url=self.bot.user.display_avatar.url)
    return embed


def play_embed(self, track: Track, mode: str) -> discord.Embed:
    # This is the only one that doesn't take the player, so we manually put in the mode when the command is summonned
    embed = discord.Embed(
        title=track.title, 
        url=track.uri, 
        color=discord.Color.random(),
        description=f"**Requested by {track.ctx.author }** - `{get_length(track.length)}`"
    )
    embed.set_author(name="Now Playing", icon_url=track.thumbnail)
    embed.set_image(url=track.thumbnail)
    embed.set_footer(text=f'Made with :3 by Flo ❤️ | Queue Mode: {mode}', icon_url=self.bot.user.display_avatar.url)
    return embed


def requested_embed(self, track: Track, pos: int = 0) -> discord.Embed:
    embed = discord.Embed(
        title=track.title,
        url=track.uri,
        color=discord.Color.random(),
        description=f"**Requested by {track.ctx.author }** | `{get_length(track.length)}`"
    )
    
    author_str = "Requested."
    if pos == 0: 
        author_str += ' | [Playing Now!]'
    else:
        author_str += f" | [Position: {pos}]"
        
    embed.set_author(name=author_str, icon_url=track.thumbnail)
    embed.set_footer(text='Made with :3 by Flo ❤️', icon_url=self.bot.user.display_avatar.url)
    return embed


def get_vote_embed(bot: discord.Client, music_cog, user_count, voted_users) -> discord.Embed:
    description = "\n".join([
        f"**{music_cog.votes[mode]}** votes for **{mode.capitalize()}** - {MODE_DESCRIPTIONS[mode]}"
        for mode in music_cog.votes
    ])
    
    voters = "\n".join([
        f"<@{user}> voted for **{mode.capitalize()}**"
        for user, mode in voted_users.items()
    ])
    
    embed = discord.Embed(
        title="Voting In Progress",
        description=f"Current votes:\n{description}",
        color=discord.Color.random()
    )
    
    if voters:
        embed.add_field(name="Voters", value=voters, inline=False)
    
    embed.set_footer(text=f"Threshold: {music_cog.vote_threshold * 100:.1f}% of {user_count} users",icon_url=bot.user.display_avatar.url)
    return embed


def vote_result_embed(bot: discord.Client, mode: str) -> discord.Embed:
    print(mode)
    embed = discord.Embed(
        title="Vote Complete!",
        description=f"The queue mode has been changed to **{mode}**.\n{MODE_DESCRIPTIONS[mode]}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Thanks for voting!", icon_url=bot.user.display_avatar.url)
    return embed
