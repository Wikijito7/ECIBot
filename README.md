# ECIBot
A custom Discord bot made in Python.

## Index
* [Pre-requisites](https://github.com/Wikijito7/ECIBot#pre-requisites)
* [How to run it](https://github.com/Wikijito7/ECIBot#how-to-run-it)
* [How it works](https://github.com/Wikijito7/ECIBot#how-it-works)
* [TODO](https://github.com/Wikijito7/ECIBot#todo)

## Pre-requisites
* Python 3.7+.
* Knowledge using a terminal.
* A little bit of time.
* Optional: Coffee to drink while executing the app.

## How to run it
* First of all, let's make sure we've got java install. To do so, run `python -V`. If we have at least Python 3.7, we can continue. If not, install a more recent Python version and come back. 
**NOTE**: Older Python3 versions may work as well but it hasn't been tested, so procede at your own risk.
* Download the code:
    * Clone the project and compile the code. To do so, download it from the green button at the top or execute `git clone https://github.com/Wikijito7/ECIBot.git`. Once downloaded, we can modify some parameters of the [config](https://github.com/Wikijito7/ECIBot/blob/main/data/keys.json) file in order to add our Discord key. Adittionaly, add an OpenAI key to enable some extra functionallity. After that, install the [requirements](https://github.com/Wikijito7/ECIBot/blob/main/requirements.txt)), to do so, open a terminal and execute `pip install -r requirements.txt`.
* We're almost done! Now execute the main script, to do so open a terminal and execute `python main.py`.
* We've finished! Now you can start using the bot.

## How it works

ECIBot is a Discord bot made in Python. It's main purpose is to be a custom bot for the ECI Discord server. It's main features are:

* Play music from different services thanks to yt-dlp.
* Play customs sounds uploaded by the server members.
* Play custom messages via tts.
* Generate custom images using Dall-e mini API.
* Generate custom text using OpenAI API.

### Commands
* `!help`: Shows the help message.
* `!sonidos`: Shows the list of custom sounds and the quantity available.
* `!play <name or url>`: Plays the sound with that name or the specified url. This url can be direct or from services supported by yt-dlp, such as YouTube or Twitter. Alternative command: !p.
* `!stop`: Stops the current sound playing. If there isn't more on the queue, the bot will disconnect from the voice channel. Alternative command: !s. 
* `!queue`: Shows current queue. Alternative command: !q y !cola.
* `!tts <prompt>`: Generates a tts sound with the given message. Alternative command: !t, !say y !decir.
* `!ask <prompt>`: Sends the prompt to OpenAI's API and generate a tts sound with the answer given. Alternative command: !a, !preguntar y !pr.
* `!poll <prompt>`: Creates a yes or no poll message with the given prompt. Alternative command: !e y !encuesta.
* `!yt <search query>`: Searches YouTube and plays the first result. Alternative command: !youtube.
* `!ytmusic <search query>`: Searches YouTube Music and plays the first result. You can use hashtags to specify the type of content. Alternative command: !ytm and !youtubemusic.
* `!search <prompt>`: Search custom sounds that contains given prompt. Alternative command: !b y !buscar.
* `!dalle <prompt>`: Generates 9 images in a 3 by 3 array by sending the given prompt to Dall-e mini API. It may take up to a minute to get the images from the API. Alternative command: !d.
* `!confetti <number>`: Plays the specified number of random Confetti songs. Alternative command: !co.

## TODO:
* [ ] Add more commands.
* [ ] Add tts messages to queue.
* [ ] Create log system.
* [ ] Add more logs.
* [ ] Add language support.
* [ ] Create lang file.
* [ ] Create constants file for the bot.

## Known bugs
* Have you found one? Create a ticket [here](https://github.com/Wikijito7/ECIBot/issues).
