import logging
from typing import Callable, Any, Optional

import discord.ui
from discord import Embed, Interaction
from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from guild_queue import add_to_queue
from radio import get_radio_by_name, get_radios, get_number_of_radios, get_number_of_pages, get_radio_page
from utils import generate_sound_list_format
from voice import Sound, SoundType


class RadioView(discord.ui.View):

    def __init__(self, current_page: int, max_page: int):
        super().__init__(timeout=None)
        self.__current_page = current_page
        self.__max_page = max_page

    @discord.ui.button(label="Anterior", emoji="⬅️", style=discord.ButtonStyle.gray, disabled=True)
    async def previous_button(self, interaction: Interaction, button: discord.ui.Button):
        self.__current_page -= 1
        self.next_button.disabled = False
        if self.__current_page == 0:
            self.previous_button.disabled = True
        await self.__update_embed__(interaction)

    @discord.ui.button(label="Siguiente", emoji="➡️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: Interaction, button: discord.ui.Button):
        self.__current_page += 1
        self.previous_button.disabled = False
        if self.__current_page == self.__max_page:
            self.next_button.disabled = True
        await self.__update_embed__(interaction)

    async def __update_embed__(self, interaction):
        await interaction.response.edit_message(
            embed=get_formatted_embed(
                radio_pages=get_radio_page(self.__current_page),
                number_of_radios=get_number_of_radios(),
                current_page=self.__current_page
            ),
            view=self
        )


async def on_radio_play(radio_name: str, author_name: str, guild_id: int, database: Database,
                        voice_channel: VocalGuildChannel, text_channel: Messageable):
    database.register_user_interaction(author_name, "radio play")
    radio = get_radio_by_name(radio_name, database)
    sound = Sound(radio.get_radio_name(), SoundType.URL, radio.get_radio_url())
    await add_to_queue(guild_id, voice_channel, text_channel, sound)


async def on_radio_list(author_name: str, channel: Messageable, database: Database, on_message: Callable[[], Any]):
    database.register_user_interaction(author_name, "radio list")
    current_page = 0
    radio_formated = get_radio_page(current_page)
    embed_msg = get_formatted_embed(radio_formated, get_number_of_radios(), current_page)
    await on_message()
    await channel.send(embed=embed_msg, view=RadioView(current_page, get_number_of_pages()))


def get_formatted_embed(radio_pages: list[str], number_of_radios: int, current_page: int):
    blank_space = "\u2800"
    embed_msg = Embed(title="Lista de radios", description=f"Actualmente hay {number_of_radios} radios.", color=0x01B05B)
    max_page = get_number_of_pages() + 1
    for page in radio_pages:
        embed_msg.add_field(name=blank_space, value=page, inline=True)
    embed_msg.set_footer(text=f"Página {current_page + 1} de {max_page}")
    return embed_msg
