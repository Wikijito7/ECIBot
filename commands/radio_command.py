from typing import Callable, Any

import discord.ui
from discord import Embed, Interaction
from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from guild_queue import add_to_queue
from radio import get_radio_by_name, get_number_of_radios, get_number_of_pages, get_radio_page
from voice import Sound, SoundType


class RadioView(discord.ui.View):

    def __init__(self, current_page: int, max_page: int):
        super().__init__(timeout=None)
        self.__current_page = current_page
        self.__max_page = max_page

    @discord.ui.button(label="Anterior", emoji="⬅️", style=discord.ButtonStyle.gray, disabled=True)
    async def previous_button(self, interaction: Interaction, button: discord.ui.Button):
        if self.__current_page <= 0:
            return
        self.__current_page -= 1
        self.next_button.disabled = False
        if self.__current_page <= 0:
            self.previous_button.disabled = True
        await self.__update_embed__(interaction)

    @discord.ui.button(label="Siguiente", emoji="➡️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: Interaction, button: discord.ui.Button):
        if self.__current_page >= self.__max_page - 1:
            return
        self.__current_page += 1
        self.previous_button.disabled = False
        if self.__current_page == self.__max_page - 1:
            self.next_button.disabled = True
        await self.__update_embed__(interaction)

    async def __update_embed__(self, interaction):
        await interaction.response.edit_message(
            embed=__get_formatted_embed__(
                radio_pages=get_radio_page(self.__current_page),
                number_of_radios=get_number_of_radios(),
                current_page=self.__current_page + 1
            ),
            view=self
        )


async def on_radio_play(radio_name: str, author_name: str, guild_id: int, database: Database,
                        voice_channel: VocalGuildChannel, text_channel: Messageable, on_message: Callable[[str], Any]):
    database.register_user_interaction(author_name, "radio play")
    radio = get_radio_by_name(radio_name, database)
    if radio is not None:
        await on_message(f":radio: Sintonizando la radio `{radio_name}`.")
        sound = Sound(radio.get_radio_name(), SoundType.URL, radio.get_radio_url())
        await add_to_queue(guild_id, voice_channel, text_channel, sound)
    else:
        await on_message(f":confused: No hay ninguna estación de radio llamada `{radio_name}`")


async def on_radio_list(author_name: str, database: Database, on_message: Callable[[Embed, RadioView], Any]):
    database.register_user_interaction(author_name, "radio list")
    current_page = 0
    radio_formated = get_radio_page(current_page)
    embed_msg = __get_formatted_embed__(radio_formated, get_number_of_radios(), current_page + 1)
    await on_message(embed_msg, RadioView(current_page, get_number_of_pages()))


async def on_radio_add(radio_name: str, radio_url: str, author_name: str, database: Database, on_message: Callable[[str], Any]):
    radio = get_radio_by_name(radio_name, database)
    if radio is None:
        database.register_user_interaction(author_name, "radio add")

    else:
        on_message("La radio ya existe.")


def __get_formatted_embed__(radio_pages: list[str], number_of_radios: int, current_page: int):
    blank_space = "\u2800"
    embed_msg = Embed(title="Lista de radios", description=f"Actualmente hay {number_of_radios} radios.", color=0x01B05B)
    max_page = get_number_of_pages()
    for page in radio_pages:
        embed_msg.add_field(name=blank_space, value=page, inline=True)
    embed_msg.set_footer(text=f"Página {current_page} de {max_page}")
    return embed_msg
