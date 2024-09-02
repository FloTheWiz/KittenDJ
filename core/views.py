from discord.ui import Button, View 
import discord

from .embeds import get_vote_embed, vote_result_embed, MODE_DESCRIPTIONS

class SilenceButton(Button):
    def __init__(self):
        """Unused for Now"""
        
        super().__init__(label="Silence", style=discord.ButtonStyle.green, emoji="🔇")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(suppress=True)

class MessageButton(Button):
    def __init__(self):
        """Carried Over from a Grandma Implementation. needs Work"""
    
        super().__init__(label="Message", style=discord.ButtonStyle.green, emoji="✉️")
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.user.send(interaction.message.content)
        except discord.errors.Forbidden:
            await interaction.response.send_message("I can't DM you.", ephemeral=True)




class VoteButton(Button):
    def __init__(self, label, mode, music_cog, user_count, vote_view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.mode = mode
        self.music_cog = music_cog
        self.user_count = user_count
        self.vote_view = vote_view

    async def callback(self, interaction: discord.Interaction):
        # Track which users have voted
        if interaction.user.id not in self.vote_view.voted_users:
            self.vote_view.voted_users[interaction.user.id] = self.mode
            self.music_cog.votes[self.mode] += 1
        else:
            await interaction.response.send_message("You have already voted!", ephemeral=True)
            return
        
        total_votes = sum(self.music_cog.votes.values())

        # Check if the vote passes the threshold
        if total_votes / self.user_count >= self.music_cog.vote_threshold:
            interaction.guild.voice_client.queue.set_mode(self.mode.capitalize())
            self.music_cog.votes.clear()
            embed = vote_result_embed(self.music_cog.bot, self.mode)
            await interaction.response.edit_message(content=f"Queue mode changed to {self.mode.capitalize()}!", embed=embed, view=None)
        else:
            # Update button label to reflect vote count
            self.label = f"{self.mode} ({self.music_cog.votes[self.mode]})"
            embed = get_vote_embed(self.music_cog, self.user_count, self.vote_view.voted_users)
            await interaction.response.edit_message(embed=embed, view=self.view)

class VoteView(View):
    def __init__(self, music_cog, user_count):
        super().__init__()
        self.music_cog = music_cog
        self.user_count = user_count
        
        self.user_count -= 1 ## For The Bot!
        self.voted_users = {}  # Track who has voted and for which mode

        modes = MODE_DESCRIPTIONS.keys()

        for mode in modes:
            music_cog.bot.log(f"Adding vote button for {mode}")
            self.add_item(VoteButton(label=f"{mode} (0)", mode=mode, music_cog=self.music_cog, user_count=self.user_count, vote_view=self))

    def get_vote_embed(self):
        return get_vote_embed(self.music_cog.bot, self.music_cog, self.user_count, self.voted_users)

    def get_vote_result_embed(self, mode):
        return vote_result_embed(self.music_cog.bot, mode)
