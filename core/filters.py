import pomice
"""
Largely Untested 
"""

class FilterManager:
    def __init__(self):
        self.active_filters = {}

    async def apply_filter(self, player, filter_obj: pomice.filters.Filter):
        """Applies a single filter to the player."""
        self.active_filters[filter_obj.tag] = filter_obj
        await self.update_filters(player)

    async def remove_filter(self, player, tag: str):
        """Removes a filter by its tag."""
        if tag in self.active_filters:
            del self.active_filters[tag]
            await self.update_filters(player)

    async def reset_filters(self, player):
        """Resets all filters, removing them from the player."""
        self.active_filters.clear()
        await player.reset_filters(fast_apply=True)

    async def update_filters(self, player):
        """Applies all active filters to the player."""
        if self.active_filters:
            combined_filter = pomice.filters.Filter(
                tag="combined", payload=self.combine_payloads()
            )
            await player.set_filter(combined_filter, fast_apply=True)
        else:
            await player.reset_filters(fast_apply=True)

    def combine_payloads(self):
        """Combines the payloads of all active filters."""
        combined_payload = {}
        for filter_obj in self.active_filters.values():
            if filter_obj.payload:
                combined_payload.update(filter_obj.payload)
        return combined_payload

    # Filter creation methods with default values

    def create_channelmix(self, tag: str = 'channelmix', left_to_left=1.0, right_to_right=1.0, left_to_right=0.0, right_to_left=0.0):
        return pomice.filters.ChannelMix(
            tag=tag,
            left_to_left=left_to_left,
            right_to_right=right_to_right,
            left_to_right=left_to_right,
            right_to_left=right_to_left
        )

    def create_distortion(self, tag: str ='distortion', sin_offset=0.0, sin_scale=1.0, cos_offset=0.0, cos_scale=1.0, tan_offset=0.0, tan_scale=1.0, offset=0.0, scale=1.0):
        return pomice.filters.Distortion(
            tag=tag,
            sin_offset=sin_offset,
            sin_scale=sin_scale,
            cos_offset=cos_offset,
            cos_scale=cos_scale,
            tan_offset=tan_offset,
            tan_scale=tan_scale,
            offset=offset,
            scale=scale
        )

    def create_equalizer(self, tag: str = 'equalizer', levels=None):
        if levels is None:
            levels = [(0, 0.0)] * 15  # Flat EQ
        return pomice.filters.Equalizer(
            tag=tag,
            levels=levels
        )

    def create_karaoke(self, tag: str = 'karaoke', level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0):
        return pomice.filters.Karaoke(
            tag=tag,
            level=level,
            mono_level=mono_level,
            filter_band=filter_band,
            filter_width=filter_width
        )

    def create_lowpass(self, tag: str = 'lowpass', smoothing=20.0):
        return pomice.filters.LowPass(
            tag=tag,
            smoothing=smoothing
        )

    def create_rotation(self, tag: str = 'rotation', rotation_hertz=5.0):
        return pomice.filters.Rotation(
            tag=tag,
            rotation_hertz=rotation_hertz
        )

    def create_timescale(self, tag: str = 'timescale', speed=1.0, pitch=1.0, rate=1.0):
        return pomice.filters.Timescale(
            tag=tag,
            speed=speed,
            pitch=pitch,
            rate=rate
        )

    def create_tremolo(self, tag: str = 'tremolo', frequency=2.0, depth=0.5):
        return pomice.filters.Tremolo(
            tag=tag,
            frequency=frequency,
            depth=depth
        )

    def create_vibrato(self, tag: str = 'vibrato', frequency=2.0, depth=0.5):
        return pomice.filters.Vibrato(
            tag=tag,
            frequency=frequency,
            depth=depth
        )
