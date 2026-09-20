import os
import discord
from openai import OpenAI

# Les deux clés sont récupérées depuis Windows
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

ai = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print("--------------------------------")
    print(f"Assistant PoE2 connecté : {bot.user}")
    print("--------------------------------")


@bot.event
async def on_message(message):
    # Empêche le bot de répondre à lui-même
    if message.author.bot:
        return

    # Le message doit commencer par !poe
    if not message.content.lower().startswith("!poe"):
        return

    question = message.content[4:].strip()

    if not question:
        await message.reply(
            "Écris ta question après `!poe`.\n"
            "Exemple : `!poe comment obtenir plus de mana ?`"
        )
        return

    async with message.channel.typing():
        try:
            response = ai.responses.create(
                model="gpt-5.6-luna",
                instructions=(
                    "Tu es Assistant PoE2, un assistant spécialisé dans "
                    "Path of Exile 2. Réponds en français. Donne des réponses "
                    "claires, précises et faciles à comprendre. "
                    "Ne prétends pas connaître une information si tu n'es "
                    "pas certain qu'elle est correcte pour la version actuelle."
                ),
                input=question
            )

            answer = response.output_text

            # Discord limite les messages à 2000 caractères
            for i in range(0, len(answer), 1900):
                await message.reply(answer[i:i + 1900])

        except Exception as error:
            print("ERREUR :", error)
            await message.reply(
                "❌ J'ai rencontré une erreur. Regarde la fenêtre CMD."
            )


bot.run(DISCORD_TOKEN)