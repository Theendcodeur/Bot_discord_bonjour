import asyncio
import json
import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio


token = input("Token de votre bot: ")
guild_id = input("ID de votre serveur: ")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="$", intents=intents)

with open('data.json', 'r') as file:
    json_data = json.load(file)

intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True
coming_peaple_voc = 0
current_channel_id = None

@bot.event
async def on_ready():
    print(f"{bot.user.name} s'est bien connecté")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

@bot.event
async def on_voice_state_update(member, before, after):
    global coming_peaple_voc
    global current_channel_id
    global json_data
    # Vérifiez si le membre est un bot
    if member.bot:
        return
    if before.channel is None and after.channel is not None and after.channel.id == json_data["bonjour_channel_id"] and len(member.guild.get_channel(json_data["bonjour_channel_id"]).members) > 1:
        print(f'{member.name} a rejoint le canal {after.channel.name}')
        # Vérifiez si le bot est déjà connecté à un canal vocal dans ce serveur
        if bot.voice_clients and member.guild in [vc.guild for vc in bot.voice_clients]:
            for vc in bot.voice_clients:
                if vc.guild == member.guild:
                    print(f'Le bot était déjà dans le channel {after.channel.name}')

        # Le bot n'est pas connecté à un canal vocal dans ce serveur, alors connectez-le
        else:
            coming_peaple_voc += 1
            try:
                vc = await after.channel.connect()
                print(f'Le bot a été connecté au canal {after.channel.name}')

            except discord.errors.ClientException:
                print("Le bot est déjà connecté à un autre canal vocal.")

            while coming_peaple_voc > 0:
                await asyncio.sleep(1.5)
                if vc.is_connected():
                    vc.play(FFmpegPCMAudio("son.mp3"))
                    while vc.is_playing():
                        await asyncio.sleep(1.5)
                coming_peaple_voc -= 1
            await vc.disconnect()


def is_owner():
    def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
    return app_commands.check(predicate)


@bot.tree.command(guild=discord.Object(id=guild_id), name="salonbonjour", description="atest command")
@is_owner()
async def salonbonjour_slash(interaction: discord.Interaction, channel_id: str):
    global json_data
    try:
        channel = discord.utils.get(interaction.user.guild.channels, id=int(channel_id))
    except ValueError:
        await interaction.response.send_message("ID de channel invalide. Assurez-vous que c'est un nombre.", ephemeral=True)
        return

    if channel is not None:
        if isinstance(channel, discord.VoiceChannel) and int(channel_id) != json_data["bonjour_channel_id"]:
            await interaction.response.send_message(f"Le channel vocal Bonjour à bien été déplacé sur le channel {channel}.", ephemeral=True)
            json_data["bonjour_channel_id"] = int(channel_id)
            with open('data.json', 'w') as file:
                json.dump(json_data, file)
        elif int(channel_id) == json_data["bonjour_channel_id"]:
            await interaction.response.send_message(f"Le channel vocal Bonjour est déjà sur le channel {channel}.", ephemeral=True)
        else:
            await interaction.response.send_message("Ce channel n'est pas un channel vocal.", ephemeral=True)
    else:
        await interaction.response.send_message("ID de channel invalide.", ephemeral=True)

bot.run(token)