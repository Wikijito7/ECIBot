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
bot.remove_command("help")


@bot.event
async def on_ready():
    print('{0.user} is alive!'.format(bot))
    await bot.change_presence(activity=discord.Game("~bip-bop"))
    bot_vitals.start()
    

@bot.event
async def on_guild_join(guild):
    for text_channel in guild.text_channels:
        if text_channel.permissions_for(guild.me).send_messages:
            await text_channel.send("~ Oh.. :robot: hello, _I'm here_.")
            break


@bot.listen()
async def on_command_error(ctx, exception):
    if isinstance(exception, commands.CommandNotFound):
        await ctx.send("Oh.. No encuentro ese comando en mis registros. Prueba a escribir ´!help´")

    if isinstance(exception, commands.MissingRequiredArgument):
        await ctx.send("Argumentos no validos. Revisa cómo la has liado, humano.")

    if isinstance(exception, commands.CheckFailure):
        await ctx.send("Lo siento, no hablo con mortales sin permisos.")


@bot.event
async def on_message(message):
    # 378213328570417154
    if message.author.id == 378213328570417154:
        emoji = "🍆"
        await message.add_reaction(emoji)
    await bot.process_commands(message)


@bot.command(pass_context=True)
async def help(ctx):
    embedMsg = discord.Embed(title="Comando ayuda", description="En este comando se recoge todos los comandos registrados", color=0x01B05B)
    embedMsg.add_field(name="!sonidos", value="Muestra el listado de sonidos actualmente disponibles.", inline=False)
    embedMsg.add_field(name="!play <nombre sonido>", value="Reproduce el sonido con el nombre indicado.", inline=False)
    embedMsg.add_field(name="!stop", value="Para el sonido actual que se está reproduciendo.", inline=False)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True)
async def sonidos(ctx):
    sounds = get_sounds()
    sounds.sort()
    desc = ""

    for sound in sounds:
        desc = desc + sound.replace(".mp3", "") + " \n"

    embedMsg = discord.Embed(title="Lista de sonidos", description=desc, color=0x01B05B)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True)
async def play(ctx, audio_name):
    ch = None
    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0 and ctx.author in channel.members:
            ch = channel
            break

    if ch != None:
        audio = get_audio(audio_name)

        if audio != None:
            voice_client = await channel.connect()
            voice_client.play(source=audio)

            await ctx.send(f":notes: Reproduciendo `{audio_name}` en `{channel.name}`.")

        else: 
            await ctx.send(f"`{audio_name}` no existe.. :frowning:")
            
    else:
        await ctx.send("No estás en ningún canal conectado.. :confused:")
    

async def jail(ctx):
    # TODO: Quitar todos los roles a un usuario
    # TODO: Dar rol configurado
    # TODO: Mover usuario al canal configurado
    pass


@bot.command(pass_context=True)
async def stop(ctx):
    for voice_client in bot.voice_clients:
        if voice_client.guild == ctx.guild and voice_client.is_playing():
            voice_client.stop()
            await ctx.send(":stop_button: Sonido parado.")
            break


@tasks.loop(seconds=2)
async def bot_vitals():
    for voice_client in bot.voice_clients:
        if not voice_client.is_playing():
            await voice_client.disconnect()

if __name__ == "__main__":
    bot.run(get_bot_key(), bot=True)
