import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot.commands import *
from bot.reminders import reminder
from bot.commands import get_cve
from bot.cve_view import fetch_vulnerabilities

# Charger les variables d'environnement depuis .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Le bot est prêt."""
    print(f"{bot.user} est connecté à Discord !")
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