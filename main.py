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
from text import TextChannel


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)
bot.remove_command("help")

sound_queue = []


@bot.event
async def on_ready():
    print('{0.user} is alive!'.format(bot))
    await bot.change_presence(activity=discord.Game("~bip-bop"))
    sdos = bot.get_guild(689108711452442667)
    if sdos is not None:
        await sdos.me.edit(nick="Fran López")
    kiwi.start()
    

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
async def on_error(event, *args, **kwargs):
    print(args)

@bot.event
async def on_message(message):
    # 378213328570417154
    if message.author.id == 378213328570417154:
        emoji = "🍆"
        await message.add_reaction(emoji)

    if message.author.id == 651163679814844467:
        emoji = "😢"
        await message.add_reaction(emoji)

    await bot.process_commands(message)
    
    if "francia" in message.content.lower():
        emojies = ["🇫🇷", "🥖", "🥐", "🍷"]
        for emoji in emojies:
            await message.add_reaction(emoji)



@bot.command(pass_context=True)
async def help(ctx):
    embedMsg = discord.Embed(title="Comando ayuda", description="En este comando se recoge todos los comandos registrados", color=0x01B05B)
    embedMsg.add_field(name="!sonidos", value="Muestra el listado de sonidos actualmente disponibles.", inline=False)
    embedMsg.add_field(name="!play <nombre sonido>", value="Reproduce el sonido con el nombre indicado. También funciona con !p", inline=False)
    embedMsg.add_field(name="!stop", value="Para el sonido actual que se está reproduciendo. También funciona con !s", inline=False)
    embedMsg.add_field(name="!queue", value="Muestra la cola actual. También funciona con !q y !cola", inline=False)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True)
async def sonidos(ctx):
    sounds = get_sounds()
    list_size = len(sounds)
    blank_space = "\u2800"
    half_list = (list_size // 2) + 1
    sounds = [sound.replace(".mp3", "") + blank_space * 2 for sound in sounds]
    sounds.sort()

    embedMsg = discord.Embed(title="Lista de sonidos", color=0x01B05B)
    embedMsg.add_field(name=blank_space, value="\n".join(sounds[0:half_list]), inline=True)
    embedMsg.add_field(name=blank_space, value="\n".join(sounds[half_list:list_size]), inline=True)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True, aliases=["p"])
async def play(ctx, audio_name):
    ch = None
    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0 and ctx.author in channel.members:
            ch = channel
            break

    if ch != None:
        channel_text.set_text_channel(ctx.channel)
        audio = get_audio(audio_name)
        if audio != None:
            if voice_channel.get_voice_channel() == None:
                client = await ch.connect()
                voice_channel.set_voice_channel(client)
                sound_queue.append(audio_name)
                bot_vitals.start()

            else:
                if audio_name not in sound_queue:
                    await ctx.send(f":notes: Añadido a la cola `{audio_name}`.")
                    sound_queue.append(audio_name)
                
                else:
                    await ctx.send(f":robot: `{audio_name}` ya está en la cola.. (!queue).")

        else: 
            await ctx.send(f"`{audio_name}` no existe.. :frowning:")
            
    else:
        await ctx.send("No estás en ningún canal conectado.. :confused:")
    

@bot.command(pass_context=True, aliases=["q", "cola"])
async def queue(ctx):
    embedMsg = discord.Embed(title="Cola de sonidos", description=f"Actualmente hay {len(sound_queue)} sonidos en la cola.", color=0x01B05B)

    if len(sound_queue) > 0:
        embedMsg.add_field(name="Sonidos en cola", value=", ".join(sound_queue), inline=False)

    await ctx.send(embed=embedMsg)


async def jail(ctx):
    # TODO: Quitar todos los roles a un usuario
    # TODO: Dar rol configurado
    # TODO: Mover usuario al canal configurado
    pass


@bot.command(pass_context=True, aliases=["s"])
async def stop(ctx):
    for voice_client in bot.voice_clients:
        if voice_client.guild == ctx.guild and voice_client.is_playing():
            voice_client.stop()
            await ctx.send(":stop_button: Sonido parado.")
            break


@tasks.loop(seconds=1, reconnect=True)
async def bot_vitals():
    for voice_client in bot.voice_clients:
        if not voice_client.is_playing():
            if len(sound_queue) == 0:
                await voice_client.disconnect()
                voice_channel.set_voice_channel(None)
                bot_vitals.stop()

            else:
                await play_sound(voice_client, channel_text.get_text_channel(), sound_queue[0])
                sound_queue.pop(0)


@tasks.loop(minutes=1)
async def kiwi():
    first_random = random.randrange(1, 10000)
    second_random = random.randrange(1, 10000)
    eci_channel = bot.get_channel(689385180921724954)

    if eci_channel is not None and len(eci_channel.members) > 0:
        play_sound = True
        for voice_client in bot.voice_clients:
            if eci_channel.guild == voice_client.guild and voice_client.is_playing() and bot.get_user(826784718589526057) in eci_channel.members:
                play_sound = False
                break

        if play_sound:
            if (first_random == second_random):
                voice_client = await eci_channel.connect()
                await play_sound_no_message(voice_client, "a")
                bot_vitals.start()

        
            elif (abs(first_random - second_random) <= 100):
                voice_client = await eci_channel.connect()
                await play_sound_no_message(voice_client, "kiwi")
                bot_vitals.start()

            

if __name__ == "__main__":
    channel_text = TextChannel()
    voice_channel = VoiceChannel()
    bot.run(get_bot_key(), bot=True)
