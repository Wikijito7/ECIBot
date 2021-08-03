import random
import time
import requests
import datetime
import os
from io import BytesIO

import discord
from discord.ext import tasks
from discord.ext import commands

from utils import *
from voice import *


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)


# TODO: Configurar el bot al iniciarse.

@bot.event
async def on_ready():
    print('{0.user} is alive!'.format(bot))
    await bot.change_presence(activity=discord.Game("~bip-bop"))
    

@commands.has_permissions(administrator=True)
@bot.command(pass_context=True)
async def play(ctx, audio_name):
    ch = None
    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0:
            ch = channel
            break

    if ch != None:
        audio = get_audio(audio_name)

        if audio != None:
            voice_client = await channel.connect()
            voice_client.play(source=audio)

            while voice_client.is_playing():
                time.sleep(.1)

            await voice_client.disconnect()
        else: 
            await ctx.send(f"´{audio_name}´ no existe.. :frowning:")
            
    else:
        await ctx.send("No estás en ningún canal conectado.. :confused:")
    
    # TODO: Quitar todos los roles a un usuario
    # TODO: Dar rol configurado
    # TODO: Mover usuario al canal configurado

if __name__ == "__main__":
    bot.run(get_bot_key(), bot=True)
