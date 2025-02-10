from typing import Any, Callable, Union

from discord import Embed, Member, User

from database import Database
from utils import get_sound_list_filtered


async def on_search_executed(arg: str, author: Union[User, Member], database: Database, on_succ: Callable[[Embed], Any], on_error: Callable[[str], Any]):
    blank_space = "\u2800"
    sounds_list = get_sound_list_filtered(arg)
    database.register_user_interaction(author.name, "buscar")
    if len(sounds_list[0]) > 0:
        embed_msg = Embed(title="Lista de sonidos", description=f"Sonidos que contienen `{arg}` en su nombre",
                          color=0x01B05B)
        for sound_block in sounds_list:
            if len(sound_block) > 0:
                embed_msg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

        await on_succ(embed_msg)

    else:
        await on_error(f":robot: No he encontrado ningún sonido que contenga `{arg}`.")
