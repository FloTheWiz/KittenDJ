from discord.ext import commands
from pomice import Player

class FilterCog(commands.Cog):
    def __init__(self, bot):
        from core.filters import FilterManager
        self.bot = bot
        self.filter_manager = FilterManager()

    async def apply_filter(self, ctx, filter_obj):
        player: Player = ctx.voice_client

        if not player or not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel.")
        elif not player.current or player.current.requester.id != ctx.author.id:
            return await ctx.send("You can only apply filters to songs you've queued.")

        await self.filter_manager.apply_filter(player, filter_obj)
        await ctx.send(f"Applied {filter_obj.__class__.__name__} filter.")

    @commands.Cog.listener()
    async def on_track_end(self, player, track, reason):
        await self.filter_manager.reset_filters(player)

    @commands.command(name="reset_filters")
    async def reset_filters(self, ctx):
        """Resets all filters to their default state."""
        player: Player = ctx.voice_client
        if not player or not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel.")
        await self.filter_manager.reset_filters(player)
        await ctx.send("All filters have been reset.")

    @commands.command(name="channelmix")
    async def channelmix(self, ctx, left_to_left: float = 1.0, right_to_right: float = 1.0, left_to_right: float = 0.0, right_to_left: float = 0.0):
        """Applies the ChannelMix filter."""
        filter_obj = self.filter_manager.create_channelmix(
            tag="channelmix", left_to_left=left_to_left, right_to_right=right_to_right, left_to_right=left_to_right, right_to_left=right_to_left
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="distortion")
    async def distortion(self, ctx, sin_offset: float = 0, sin_scale: float = 1, cos_offset: float = 0, cos_scale: float = 1, tan_offset: float = 0, tan_scale: float = 1, offset: float = 0, scale: float = 1):
        """Applies the Distortion filter."""
        filter_obj = self.filter_manager.create_distortion(
            tag="distortion", sin_offset=sin_offset, sin_scale=sin_scale, cos_offset=cos_offset, cos_scale=cos_scale, tan_offset=tan_offset, tan_scale=tan_scale, offset=offset, scale=scale
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="equalizer")
    async def equalizer(self, ctx, levels: str):
        """Applies the Equalizer filter. Levels should be provided as a list of tuples like (band, gain)."""
        levels_list = eval(levels)  # Convert string to list
        filter_obj = self.filter_manager.create_equalizer(
            tag="equalizer", levels=levels_list
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="karaoke")
    async def karaoke(self, ctx, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220.0, filter_width: float = 100.0):
        """Applies the Karaoke filter."""
        filter_obj = self.filter_manager.create_karaoke(
            tag="karaoke", level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="lowpass")
    async def lowpass(self, ctx, smoothing: float = 20):
        """Applies the LowPass filter."""
        filter_obj = self.filter_manager.create_lowpass(
            tag="lowpass", smoothing=smoothing
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="rotation")
    async def rotation(self, ctx, rotation_hertz: float = 5.0):
        """Applies the Rotation filter."""
        filter_obj = self.filter_manager.create_rotation(
            tag="rotation", rotation_hertz=rotation_hertz
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="timescale")
    async def timescale(self, ctx, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0):
        """Applies the Timescale filter."""
        filter_obj = self.filter_manager.create_timescale(
            tag="timescale", speed=speed, pitch=pitch, rate=rate
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="tremolo")
    async def tremolo(self, ctx, frequency: float = 2.0, depth: float = 0.5):
        """Applies the Tremolo filter."""
        filter_obj = self.filter_manager.create_tremolo(
            tag="tremolo", frequency=frequency, depth=depth
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="vibrato")
    async def vibrato(self, ctx, frequency: float = 2.0, depth: float = 0.5):
        """Applies the Vibrato filter."""
        filter_obj = self.filter_manager.create_vibrato(
            tag="vibrato", frequency=frequency, depth=depth
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="nightcore")
    async def nightcore(self, ctx):
        """Applies the Nightcore preset of the Timescale filter."""
        filter_obj = self.filter_manager.create_timescale(
            tag="nightcore", speed=1.2, pitch=1.0, rate=1.0
        )
        await self.apply_filter(ctx, filter_obj)

    @commands.command(name="vaporwave")
    async def vaporwave(self, ctx):
        """Applies the Vaporwave preset of the Timescale filter."""
        filter_obj = self.filter_manager.create_timescale(
            tag="vaporwave", speed=0.85, pitch=1.0, rate=1.0
        )
        await self.apply_filter(ctx, filter_obj)

async def setup(bot):
    await bot.add_cog(FilterCog(bot))
