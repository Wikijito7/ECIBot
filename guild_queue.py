import logging as log
from typing import Optional

from discord import VoiceClient
from discord.abc import Messageable
from discord.channel import VocalGuildChannel
from discord.ext import tasks

from utils import remove_files
from voice import Sound, stop_and_disconnect, SoundType, play_sound


class GuildQueue:
    def __init__(self, guild_id: int, vocal_channel: VocalGuildChannel, messageable: Messageable, sound_queue: list[Sound]):
        self.__guild_id = guild_id
        self.__vocal_channel = vocal_channel
        self.__messageable = messageable
        self.__sound_queue = sound_queue
        self.__voice_client = None
        self.__finished = False
        self.__pending_files_for_deletion = []

    def get_guild_id(self) -> int:
        return self.__guild_id

    def get_vocal_channel(self) -> VocalGuildChannel:
        return self.__vocal_channel

    def get_messageable(self) -> Messageable:
        return self.__messageable

    def get_sound_queue(self) -> list[Sound]:
        return self.__sound_queue

    def add_sound_to_queue(self, sound: Sound):
        self.__sound_queue.append(sound)

    def clear_queue(self):
        self.__sound_queue.clear()

    def get_voice_client(self) -> Optional[VoiceClient]:
        return self.__voice_client

    async def get_or_connect_to_voice_client(self) -> Optional[VoiceClient]:
        if self.__voice_client is None:
            self.__voice_client = await self.__vocal_channel.connect()
        return self.__voice_client

    def has_finished(self) -> bool:
        return self.__finished

    def set_finished(self, ready_for_removal: bool):
        self.__finished = ready_for_removal

    def add_pending_file_for_deletion(self, path: str):
        self.__pending_files_for_deletion.append(path)

    def get_pending_files_for_deletion(self) -> list[str]:
        return self.__pending_files_for_deletion


guild_queues: list[GuildQueue] = []


def get_guild_queue(guild_id: int) -> Optional[GuildQueue]:
    return next((gq for gq in guild_queues if gq.get_guild_id() == guild_id), None)


def add_new_guild_queue(guild_id: int, vocal_channel: VocalGuildChannel, messageable: Messageable) -> Optional[GuildQueue]:
    guild_queue = GuildQueue(guild_id, vocal_channel, messageable, [])
    if guild_queue is not None:
        guild_queues.append(guild_queue)
    return guild_queue


async def cleanup_guild_queues():
    not_finished_guild_queues = []
    for guild_queue in guild_queues:
        if not guild_queue.has_finished():
            not_finished_guild_queues.append(guild_queue)
        else:
            await stop_and_disconnect(guild_queue.get_voice_client())
            remove_files(guild_queue.get_pending_files_for_deletion())

    guild_queues.clear()
    guild_queues.extend(not_finished_guild_queues)
    if len(guild_queues) == 0:
        queue_vitals.stop()


async def add_to_queue(guild_id: int, vocal_channel: VocalGuildChannel, messageable: Messageable, sound: Sound):
    try:
        guild_queue = get_guild_queue(guild_id)
        should_start_vitals = False

        if guild_queue is None:
            guild_queue = add_new_guild_queue(guild_id, vocal_channel, messageable)
            should_start_vitals = True
        else:
            await messageable.send(f":notes: Añadido a la cola `{sound.get_name()}`.")

        if guild_queue is not None:
            guild_queue.add_sound_to_queue(sound)
            if should_start_vitals and not queue_vitals.is_running():
                queue_vitals.start()  # TODO doesn't work when method is run from another thread

    except Exception as e:
        log.error("add_to_queue >> Exception thrown when adding sound to queue.", exc_info=e)


async def play_sounds_in_all_queues():
    for guild_queue in guild_queues:
        try:
            voice_client = await guild_queue.get_or_connect_to_voice_client()
            if isinstance(voice_client, VoiceClient) and not voice_client.is_playing():
                sound_queue = guild_queue.get_sound_queue()
                if len(sound_queue) == 0:
                    guild_queue.set_finished(True)

                else:
                    sound = sound_queue[0]

                    if sound.get_sound_type() is SoundType.TTS:
                        await guild_queue.get_messageable().send(f":microphone: Reproduciendo un mensaje tts en `{voice_client.channel.name}`.")
                        guild_queue.add_pending_file_for_deletion(sound.get_source())
                    elif sound.get_sound_type() is not SoundType.FILE_SILENT:
                        await guild_queue.get_messageable().send(f":notes: Reproduciendo `{sound.get_name()}` en `{voice_client.channel.name}`.")

                    await play_sound(voice_client, sound)
                    sound_queue.pop(0)

        except Exception as e:
            log.error("play_sounds_in_all_queues >> Caught exception playing sound. Removing sound queue for this guild...", exc_info=e)
            sound_queue = guild_queue.get_sound_queue()
            if len(sound_queue) > 0:
                removed_sound = guild_queue.get_sound_queue().pop(0)
                if removed_sound.get_sound_type() is SoundType.TTS:
                    guild_queue.add_pending_file_for_deletion(removed_sound.get_source())
            if len(sound_queue) == 0:
                guild_queue.set_finished(True)


@tasks.loop(seconds=1, reconnect=True)
async def queue_vitals():
    await play_sounds_in_all_queues()
    await cleanup_guild_queues()
