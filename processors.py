from discord import Message


async def process_reactions(message: Message):
    if message.author.id == 378213328570417154:
        emoji = "🍆"
        await message.add_reaction(emoji)

    if message.author.id == 651163679814844467:
        emoji = "😢"
        await message.add_reaction(emoji)

    if message.author.id == 899918332965298176:
        emoji = "😭"
        await message.add_reaction(emoji)

    if "francia" in message.content.lower():
        emojis = ["🇫🇷", "🥖", "🥐", "🍷"]
        for emoji in emojis:
            await message.add_reaction(emoji)

    if "españa" in message.content.lower():
        emojis = ["🆙", "🇪🇸", "❤️‍🔥", "💃", "🥘", "🏖️", "🛌", "🇪🇦"]
        for emoji in emojis:
            await message.add_reaction(emoji)

    if "mexico" in message.content.lower():
        emojis = ["🇲🇽", "🌯", "🌮", "🫔"]
        for emoji in emojis:
            await message.add_reaction(emoji)


async def process_link(message: Message, author_id: int):
    if message.content.startswith("!") or message.author.id == author_id:
        return

    if "https://x.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://x")
        return

    if "https://www.x.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://www.x")
        return

    if "https://twitter.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://twitter")

    if "https://www.twitter.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://www.twitter")

    if "https://instagram.com" in message.content.lower():
        await send_fixed_up_instagram(message, "https://instagram")

    if "https://www.instagram.com" in message.content.lower():
        await send_fixed_up_instagram(message, "https://www.instagram")

    if "https://www.reddit.com" in message.content.lower():
        await send_fixed_up_reddit(message, "https://www.reddit")

    if "https://reddit.com" in message.content.lower():
        await send_fixed_up_reddit(message, "https://reddit")

    if "https://www.tiktok.com" in message.content.lower():
        await send_fixed_up_tiktok(message, "https://www.tiktok")

    if "https://tiktok.com" in message.content.lower():
        await send_fixed_up_tiktok(message, "https://tiktok")

    if "https://vm.tiktok.com" in message.content.lower():
        await send_fixed_up_tiktok(message, "https://vm.tiktok")


async def send_fixed_up_twitter(message: Message, content: str):
    fixed_tweet = message.content.replace(content, "https://fixupx").split("?")[0]
    await __send_fixed_up_message__(fixed_tweet, message)


async def send_fixed_up_instagram(message: Message, content: str):
    fixed_insta = message.content.replace(content, "https://ddinstagram").split("?")[0]
    await __send_fixed_up_message__(fixed_insta, message)


async def send_fixed_up_reddit(message: Message, content: str):
    fixed_post = message.content.replace(content, "https://rxddit").split("?")[0]
    await __send_fixed_up_message__(fixed_post, message)


async def send_fixed_up_tiktok(message: Message, content: str):
    fixed_post = message.content.replace(content, "https://tnktok").split("?")[0]
    await __send_fixed_up_message__(fixed_post, message)


async def __send_fixed_up_message__(fixed_post: str, message: Message):
    await message.channel.send(f"Post enviado por {message.author.mention} con el enlace arreglado:\n{fixed_post}")
    await message.delete()

