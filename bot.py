import os
import base64
import discord
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
POE_CHANNEL_ID = 1551317813249970277
ai = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


# =========================
# DÉMARRAGE
# =========================

@bot.event
async def on_ready():
    print("--------------------------------")
    print(f"Assistant PoE2 connecté : {bot.user}")
    print("Commande !poe activée")
    print("--------------------------------")


# =========================
# ENVOYER UNE RÉPONSE
# =========================

async def envoyer_reponse(message, texte):
    if not texte:
        return

    # Discord limite la taille des messages
    for i in range(0, len(texte), 1900):
        await message.reply(texte[i:i + 1900])


# =========================
# RÉCEPTION DES MESSAGES
# =========================

@bot.event
async def on_message(message):

    # Empêche le bot de répondre à lui-même
    if message.author.bot:
        return
# Autorise !poe2 uniquement dans le salon choisi
if message.channel.id != POE_CHANNEL_ID:
    return
    # Le bot répond uniquement à !poe
    if not message.content.lower().startswith("!poe"):
        return

    print("--------------------------------")
    print(f"Commande !poe reçue de : {message.author}")
    print(f"Message : {message.content}")
    print("--------------------------------")

    # Retire !poe du début
    question = message.content[4:].strip()

    # =========================
    # RECHERCHE DES IMAGES
    # =========================

    images = []

    for attachment in message.attachments:

        content_type = attachment.content_type or ""

        if content_type.startswith("image/"):
            images.append(attachment)

    # Si !poe est envoyé tout seul
    if not question and not images:

        await message.reply(
            "❌ Écris ta question après `!poe`.\n"
            "Exemple : `!poe comment obtenir des charges de pouvoir ?`"
        )
        return

    # =========================
    # APPEL OPENAI
    # =========================

    async with message.channel.typing():

        try:

            contenu = []

            # TEXTE
            if question:

                contenu.append({
                    "type": "input_text",
                    "text": question
                })

            # IMAGE SANS QUESTION
            elif images:

                contenu.append({
                    "type": "input_text",
                    "text": (
                        "Analyse cette capture d'écran de Path of Exile 2 "
                        "et explique clairement ce que tu vois."
                    )
                })

            # =========================
            # AJOUT DES IMAGES
            # =========================

            for attachment in images:

                image_bytes = await attachment.read()

                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                mime_type = attachment.content_type or "image/png"

                contenu.append({
                    "type": "input_image",
                    "image_url":
                        f"data:{mime_type};base64,{image_base64}"
                })

            # =========================
            # OPENAI
            # =========================

            response = ai.responses.create(

                model="gpt-5.6-luna",

                instructions=(
                    "Tu es Assistant PoE2, un assistant Discord spécialisé "
                    "dans Path of Exile 2. "

                    "Réponds toujours en français. "

                    "Tu aides les joueurs sur les builds, objets, compétences, "
                    "gemmes, runes, passifs, arbre de talents, quêtes, boss, "
                    "maps, endgame, mana, esprit, résistances, craft et "
                    "mécaniques du jeu. "

                    "Donne des réponses claires, précises et faciles à comprendre. "

                    "Quand une capture d'écran est envoyée, analyse ce qui est "
                    "visible sur l'image. "

                    "Lis les statistiques, objets, compétences et messages "
                    "d'erreur visibles lorsque c'est possible. "

                    "Si tu n'es pas certain d'une information, dis-le clairement "
                    "au lieu d'inventer. "

                    "Ne confonds jamais Path of Exile 1 et Path of Exile 2. "

                    "Si une information dépend d'un patch ou d'une version "
                    "récente du jeu, précise qu'elle peut avoir changé."
                ),

                input=[
                    {
                        "role": "user",
                        "content": contenu
                    }
                ]
            )

            answer = response.output_text

            print("Réponse OpenAI reçue avec succès.")

            await envoyer_reponse(message, answer)

        except Exception as error:

            print("--------------------------------")
            print("ERREUR OPENAI :")
            print(error)
            print("--------------------------------")

            await message.reply(
                "❌ J'ai rencontré une erreur. "
                "Consulte les logs Railway pour voir le problème."
            )


# =========================
# LANCEMENT DU BOT
# =========================

bot.run(DISCORD_TOKEN)
