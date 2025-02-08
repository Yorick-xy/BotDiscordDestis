from dotenv import load_dotenv
from discord.ext import commands
from bot.commands import *
from bot.reminders import reminder
from bot.commands import get_cve
from bot.cve_view import fetch_vulnerabilities
import os
import discord

# Spécifier un chemin relatif vers .env dans un sous-répertoire
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GUILD_ID = os.getenv("GUILD_ID")  # Identifiant du serveur Discord

if TOKEN is None or CHANNEL_ID is None:
    print("Vérifie tes variables d'environnement !")
    exit(1)
else:
    print("Variables d'environnement valides.")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True # Permet au bot de lire le contenu des messages
intents.members = True # Permet au bot de voir les membres du serveur

bot = commands.Bot(command_prefix="!", intents=intents)

if CHANNEL_ID is not None:
    try:
        CHANNEL_ID = int(CHANNEL_ID)  # Convertit la chaîne en entier
        print(f"CHANNEL_ID est valide")
    except ValueError:
        print(f"Erreur de conversion pour CHANNEL_ID : {CHANNEL_ID}")
else:
    print("CHANNEL_ID est None")

if TOKEN is not None:
    print(f"TOKEN est valide")
else:
    print("TOKEN est invalide")

if GUILD_ID is not None:
    try:
        GUILD_ID = int(GUILD_ID)  # Convertit la chaîne en entier
        print(f"GUILD_ID est valide")
    except ValueError:
        print(f"Erreur de conversion pour GUILD_ID : {GUILD_ID}")

@bot.event
async def on_ready():
    """Le bot est prêt."""
    print(f"{bot.user} est connecté à Discord !")
    
    try:
        # Récupère le serveur et imprime les canaux disponibles
        guild = bot.get_guild(int(GUILD_ID))  # Assure-toi que GUILD_ID est aussi correctement défini
        if guild is None:
            print(f"Serveur introuvable avec l'ID {GUILD_ID}.")
        else:
            print(f"Serveur trouvé : {guild.name}")
            for channel in guild.text_channels:
                print(f"Canal disponible : {channel.name} (ID: {channel.id})")
            
            # Tente de récupérer le canal avec l'ID
            channel = await bot.fetch_channel(int(CHANNEL_ID))  # S'assurer que CHANNEL_ID est bien un int
            if channel is None:
                print("Canal introuvable ! Vérifie l'ID.")
            else:
                print(f"Canal trouvé : {channel.name}")
                await channel.send("Bot Destis est maintenant en ligne.")
    except Exception as e:
        print(f"Erreur lors de l'accès au canal : {e}")
    fetch_vulnerabilities.start(bot)  # Démarre la récupération des CVE en boucle

# Ajouter les commandes
bot.add_command(aide)
bot.add_command(ping)
bot.add_command(status)
bot.add_command(reminder)
bot.add_command(say)
bot.add_command(ajouter_role)
bot.add_command(time)
bot.add_command(blague)
bot.add_command(vuln)
bot.add_command(news)
bot.add_command(cve)
bot.add_command(search)
bot.add_command(get_cve)

# Démarrer le bot
if __name__ == "__main__":
    bot.run(TOKEN)