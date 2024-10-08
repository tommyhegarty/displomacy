import disnake, asyncio

async def respond(inter: disnake.ApplicationCommandInteraction, message: str):
    user=str(inter.author.id)
    channel=inter.channel_id

    print(f'Responding to {user} command in {channel} with message [{message}]')
    await inter.send(content=message)

def respond_privately(inter: disnake.ApplicationCommandInteraction, message: str):
    user=str(inter.author.id)
    channel=inter.channel_id