@bot.event
async def on_message(message):

    # Empêche le bot de répondre à lui-même
    if message.author.bot:
        return

    # Le bot répond uniquement aux messages commençant par !poe
    if not message.content.lower().startswith("!poe"):
        return

    # Enlève !poe du début du message
    question = message.content[4:].strip()

    # Recherche les captures/images
    images = []

    for attachment in message.attachments:
        content_type = attachment.content_type or ""

        if content_type.startswith("image/"):
            images.append(attachment)

    # Exemple : !poe + une capture fonctionne aussi
    if not question and not images:
        await message.reply(
            "❌ Écris ta question après `!poe`.\n"
            "Exemple : `!poe comment obtenir des charges de pouvoir ?`"
        )
        return

    async with message.channel.typing():

        try:

            contenu = []

            if question:
                contenu.append({
                    "type": "input_text",
                    "text": question
                })

            elif images:
                contenu.append({
                    "type": "input_text",
                    "text": (
                        "Analyse cette capture d'écran de Path of Exile 2 "
                        "et explique clairement ce que tu vois."
                    )
                })

            for attachment in images:

                image_bytes = await attachment.read()

                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                mime_type = attachment.content_type or "image/png"

                contenu.append({
                    "type": "input_image",
                    "image_url": f"data:{mime_type};base64,{image_base64}"
                })

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
                    "Donne des réponses claires et faciles à comprendre. "
                    "Quand une capture d'écran est envoyée, analyse ce qui est "
                    "visible sur l'image. "
                    "Si tu n'es pas certain d'une information, dis-le clairement "
                    "au lieu d'inventer. "
                    "Fais attention à ne pas confondre Path of Exile 1 "
                    "et Path of Exile 2."
                ),

                input=[
                    {
                        "role": "user",
                        "content": contenu
                    }
                ]
            )

            answer = response.output_text

            await envoyer_reponse(message, answer)

        except Exception as error:

            print("--------------------------------")
            print("ERREUR :")
            print(error)
            print("--------------------------------")

            await message.reply(
                "❌ J'ai rencontré une erreur."
            )