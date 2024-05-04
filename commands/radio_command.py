from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from guild_queue import add_to_queue
from radio import get_radio_by_name
from voice import Sound, SoundType


async def on_radio_play(radio_name: str, author_name: str, guild_id: int, database: Database,
                        voice_channel: VocalGuildChannel, text_channel: Messageable):
    database.register_user_interaction(author_name, "radio play")
    radio = get_radio_by_name(radio_name, database)
    sound = Sound(radio.get_radio_name(), SoundType.URL, radio.get_radio_url())
    await add_to_queue(guild_id, voice_channel, text_channel, sound)
