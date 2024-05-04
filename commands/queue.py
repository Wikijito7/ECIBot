from typing import Callable, Any

from discord import Guild, Embed

from database import Database
from guild_queue import get_guild_queue


async def on_queue(guild: Guild, author_name: str, database: Database, on_succ: Callable[[Embed], Any], on_error: Callable[[str], Any]):
    if guild is not None:
        guild_queue = get_guild_queue(guild.id)
        sound_queue = guild_queue.get_sound_queue() if guild_queue is not None else []

        embed_msg = Embed(
            title="Cola de sonidos",
            description=f"Actualmente hay {len(sound_queue)} sonidos en la cola de {guild.name}.",
            color=0x01B05B
        )
        database.register_user_interaction(author_name, "queue")

        if len(sound_queue) > 0:
            sounds = map(lambda sound: sound.get_name(), sound_queue)
            sounds_to_be_sent = []
            for sound in sounds:
                sounds_joined = ", ".join(sounds_to_be_sent)
                if len(sounds_joined) + len(sound) > 1000:
                    generate_embed_field(embed_msg, sounds_joined)
                    sounds_to_be_sent.clear()
                    sounds_to_be_sent.append(sound)
                else:
                    sounds_to_be_sent.append(sound)
            sounds_joined = ", ".join(sounds_to_be_sent)
            generate_embed_field(embed_msg, sounds_joined)

        await on_succ(embed_msg)
    else:
        await on_error("No estás conectado a un servidor :angry:")


def generate_embed_field(embed_msg: Embed, sounds_joined: str):
    embed_title = "Sonidos en cola" if len(embed_msg.fields) == 0 else "\u2800"
    embed_msg.add_field(name=embed_title, value=sounds_joined, inline=False)
