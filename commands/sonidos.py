from typing import Any, Callable, Union

from discord import Embed, Member, User

from database import Database
from utils import get_sounds_list, get_sounds


async def on_sounds_requested(author: Union[User, Member], database: Database, callback: Callable[[Embed], Any]):
    blank_space = "\u2800"
    sounds_list = get_sounds_list()
    database.register_user_interaction(author.name, "sonidos")
    embed_msg = Embed(title="Lista de sonidos", description=f"Actualmente hay {len(get_sounds())} sonidos.",
                      color=0x01B05B)
    for sound_block in sounds_list:
        embed_msg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)
    await callback(embed_msg)
