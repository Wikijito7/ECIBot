from typing import Callable, Any, Union, Optional

from discord import Member, Guild, Message, ChannelType, Thread
from discord.abc import Messageable
from discord.channel import VocalGuildChannel, TextChannel

from ai import AiClient
from bd import Database
from commands.say import on_tts
from voice import audio_play_prechecks

MAX_RESPONSE_CHARACTERS = 2000 - 6
DEFAULT_THREAD_NAME = "ECIBot - Ask"


async def on_ask(author: Member, guild: Guild, database: Database, channel: Union[TextChannel, Thread],
                 text: str, ai_client: AiClient, message: Optional[Message],
                 tts_listener: Callable[[int, VocalGuildChannel, Messageable, str], Any]):
    database.register_user_interaction(author.name, "ask")

    response = ai_client.generate_response(text)
    if response is not None:
        thread = await get_thread_or_create(channel, text, message)
        await thread.send(":e_mail: Respuesta:")
        for x in range(0, (len(response) // MAX_RESPONSE_CHARACTERS) + 1):
            text_start = MAX_RESPONSE_CHARACTERS * x
            text_end = MAX_RESPONSE_CHARACTERS * (x + 1)
            await thread.send(f"```{response[text_start:text_end]}```")
        tts_message = f"{text} {response}"

        if not await audio_play_prechecks(guild, author, lambda error: thread.send(error)):
            return

        await on_tts(
            text=tts_message,
            author=author,
            guild=guild,
            voice_channel=author.voice.channel,
            channel=thread,
            database=database,
            tts_listener=tts_listener,
            on_generate=lambda message: thread.send(message)
        )


async def get_thread_or_create(channel: Union[TextChannel, Thread], text: str, message: Optional[Message]) -> Thread:
    if isinstance(channel, Thread):
        return channel

    else:
        return await channel.create_thread(
            name=text[:100] if len(text) > 0 else DEFAULT_THREAD_NAME,
            message=message,
            type=ChannelType.public_thread,
            auto_archive_duration=60
        )
