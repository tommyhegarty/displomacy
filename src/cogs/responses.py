import disnake

def respond(inter: disnake.ApplicationCommandInteraction, message: str):
    user=str(inter.author.id)
    channel=inter.channel_id

    print(f'Responding to {user} command in {channel} with message [{message}]')

def respond_privately(inter: disnake.ApplicationCommandInteraction, message: str):
    user=str(inter.author.id)
    channel=inter.channel_id