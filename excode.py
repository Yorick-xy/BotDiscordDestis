import discord
from discord.ext import commands, tasks
import requests
import os
import random
from datetime import datetime
import asyncio

#TOKEN = os.getenv("DISCORD_TOKEN")  # Définir la variable d'environnement
TOKEN = 'MTMzMTczODM1NjA5ODI3MzQyMQ.GZ2qH6.Bp0qv9xi2DzgAbnpC5s0JlAxH1LXhsmoMy00ns'
CHANNEL_ID = 1331741159265140907  # Remplacez par l'ID de votre canal
API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
API_URL_CVE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
API_URL_NEWS = "https://hn.algolia.com/api/v1/search?query=cybersecurity"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Classe pour naviguer entre les CVE
class CVEView(discord.ui.View):
    def __init__(self, cve_data):
        super().__init__()
        self.cve_data = cve_data
        self.index = 0

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.primary, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="Suivant ➡️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        await self.update_message(interaction)

    async def update_message(self, interaction):
        cve = self.cve_data[self.index]
        embed = discord.Embed(title=cve["id"], description=cve["description"], color=discord.Color.red())
        embed.add_field(name="Score CVSS", value=cve["score"], inline=True)
        embed.add_field(name="🔗 Lien", value=f"[Voir plus](https://nvd.nist.gov/vuln/detail/{cve['id']})", inline=False)

        # Désactiver boutons si nécessaire
        self.children[0].disabled = self.index == 0
        self.children[1].disabled = self.index == len(self.cve_data) - 1

        await interaction.response.edit_message(embed=embed, view=self)

# Commande d'aide
@bot.command(name='aide')
async def aide(ctx):
    help_message = """
    Voici une liste des commandes disponibles :
    🏓 !ping - Teste la latence du bot
    📊 !status - Affiche le statut du bot
    ⏰ !reminder [temps en minutes] [message] - Définit un rappel
    🔥 !vuln - Affiche les dernières vulnérabilités
    🎭 !ajouter_role [membre] [role] - Ajoute un rôle à un membre
    🕒 !time - Affiche l'heure actuelle
    🔐 !news - Affiche les dernières actualités en cybersécurité
    🤡 !blague - Le bot vous raconte une blague !
    """
    await ctx.send(help_message)

# Commande Ping
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms
    await ctx.send(f'🏓 Pong ! Latence : {latency} ms')

# Commande Status
@bot.command()
async def status(ctx):
    await ctx.send("✅ Le bot fonctionne parfaitement !")

# Commande Reminder
@bot.command(name="reminder")
async def reminder(ctx, time: int, *, message: str):
    """Définit un rappel après un certain nombre de minutes."""
    if time <= 0:
        await ctx.send("⏳ Le temps doit être supérieur à 0 minute.")
        return

    await ctx.send(f"✅ Rappel défini dans {time} minute(s) : `{message}`")
    await asyncio.sleep(time * 60)  # Convertit les minutes en secondes
    await ctx.send(f"🔔 **Rappel pour {ctx.author.mention} :** {message}")

# Commande Say
@bot.command()
async def say(ctx, *, message: str):
    await ctx.message.delete()  # Supprime le message original
    await ctx.send(message)

# Commande Ajouter rôle
@bot.command()
async def ajouter_role(ctx, membre: discord.Member, role: discord.Role):
    await membre.add_roles(role)
    await ctx.send(f'✅ Le rôle {role.name} a été ajouté à {membre.mention}')

# Commande Heure actuelle
@bot.command()
async def time(ctx):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"🕒 Heure actuelle : {now}")

# Commande Blague
@bot.command()
async def blague(ctx):
    blagues = [
        "Quel est le comble pour un électricien ? De ne pas être au courant !",
        "Pourquoi les oiseaux ne jouent-ils pas au poker ? Parce qu'ils ont peur des chats !",
        "Chuck Norris peut faire un habit avec un moine.",
        "Les requins regardent Les Dents de Chuck Norris à leurs soirées films d'horreur.",
        "Chuck Norris peut faire de la bière en brassant de l'air.",
        "Chuck Norris mine de la crypto-monnaie avec la calculette de sa montre Casio",
        "Chuck Norris a déjà compté jusqu'à l'infini. Deux fois.",
        "Chuck Norris peut diviser par zéro.",
        "Un jour, Lara Croft à voulu battre Chuck Norris, maintenant on l'appelle Dora L'exploratrice",
        "Chuck Norris a déjà fini World of Warcraft.",
        "Chuck Norris ne se masturbe jamais. Chuck Norris est inébranlable.",
        "Un jour, les PowerRangers ont rencontré Chuck Norris. Maintenant on les appelle les Télétubbies.",
        "Chuck Norris n'a pas de père. On ne nique pas la mère de Chuck Norris.",
        "Un jour Chuck Norris a eu un zero en latin, depuis c'est une langue morte.",
        "Certains disent : La violence ne résout rien, Chuck Norris leur répond C'est que t'as pas tapé assez fort",
        "Chuck Norris a retrouvé Ornicar.",
        "Quand Chuck Norris s'est mis aux arts martiaux, les Japonais se sont reconvertis dans les jeux videos.",
        "Chuck Norris ne dépose pas d'argent à la banque. Chuck Norris n'épargne rien, ni personne.",
        "Chuck Norris a accroché Magneto des X-men sur son frigo.",
        "Si Chuck Norris te donne rendez-vous le 30 Fevrier, tu y vas.",
        "Aux Jeux Olympiques, Chuck Norris a été disqualifié de l'épreuve de natation. Il courait sur l'eau.",
        "Si les anglais roulent à gauche, c'est parce que Chuck Norris roule à droite.",
        "Pourquoi est-ce qu'il faut mettre tous les crocos en prison ? : Parce que les crocos dealent.",
        "Que se passe-t-il quand 2 poissons s'énervent ? : Le thon monte.",
        "Quel est le sport préféré des insectes ? : Le cricket.",
        "Qu'est-ce qu'une frite enceinte ? : Une patate sautée."
    ]
    await ctx.send(random.choice(blagues))

@bot.command()
async def vuln(ctx):
    response = requests.get(API_URL_CVE)
    if response.status_code == 200:
        data = response.json()["vulnerabilities"]
        cve_list = data[:3]  # Récupérer les 3 premières CVE

        for cve in cve_list:
            cve_id = cve["cve"]["id"]
            description = cve["cve"]["descriptions"][0]["value"]
            
            embed = discord.Embed(title=cve_id, url=f"https://nvd.nist.gov/vuln/detail/{cve_id}", description=description, color=discord.Color.red())
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Impossible de récupérer les vulnérabilités.")

# Commande News Cybersécurité
@bot.command()
async def news(ctx):
    response = requests.get(API_URL_NEWS)
    if response.status_code == 200:
        articles = response.json().get("hits", [])[:3]  # Récupérer les 3 premiers articles
        
        for article in articles:
            title = article["title"]
            url = article["url"]
            embed = discord.Embed(title=title, url=url, color=discord.Color.blue())
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Impossible de récupérer les actualités en cybersécurité.")

# ✅ Commande pour obtenir les dernières CVE
@bot.command()
async def cve(ctx):
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json().get("vulnerabilities", [])
        if not data:
            await ctx.send("⚠️ Aucune CVE trouvée.")
            return

        cve_list = [{"id": cve["cve"]["id"], "description": cve["cve"]["descriptions"][0]["value"], "score": cve.get("cve", {}).get("metrics", {}).get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseScore", "N/A")} for cve in data[:5]]

        embed = discord.Embed(title=cve_list[0]["id"], description=cve_list[0]["description"], color=discord.Color.red())
        embed.add_field(name="Score CVSS", value=cve_list[0]["score"], inline=True)
        embed.add_field(name="🔗 Lien", value=f"[Voir plus](https://nvd.nist.gov/vuln/detail/{cve_list[0]['id']})", inline=False)

        await ctx.send(embed=embed, view=CVEView(cve_list))
    else:
        await ctx.send("❌ Impossible de récupérer les CVE.")

# ✅ Recherche par mot-clé
@bot.command()
async def search(ctx, *, keyword: str):
    url = f"{API_URL}?keywordSearch={keyword}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("vulnerabilities", [])
        if not data:
            await ctx.send(f"⚠️ Aucune CVE trouvée pour '{keyword}'.")
            return

        cve_list = [{"id": cve["cve"]["id"], "description": cve["cve"]["descriptions"][0]["value"], "score": cve.get("cve", {}).get("metrics", {}).get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseScore", "N/A")} for cve in data[:3]]

        for cve in cve_list:
            embed = discord.Embed(title=cve["id"], description=cve["description"], color=discord.Color.blue())
            embed.add_field(name="Score CVSS", value=cve["score"], inline=True)
            embed.add_field(name="🔗 Lien", value=f"[Voir plus](https://nvd.nist.gov/vuln/detail/{cve['id']})", inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Erreur lors de la récupération des CVE.")

# ✅ Exécuter la récupération des CVE toutes les 6h
@tasks.loop(hours=6)
async def fetch_vulnerabilities():
    """Récupère les CVE et les envoie sur Discord."""
    print("🔍 Récupération des CVE...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        cves = data.get("vulnerabilities", [])

        if not cves:
            print("⚠️ Aucune CVE trouvée.")
            return

        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ Canal introuvable ! Vérifiez l'ID.")
            return

        for cve in cves[:5]:  # Limite à 5 CVE pour éviter le spam
            cve_id = cve["cve"]["id"]
            description = cve["cve"]["descriptions"][0]["value"]
            severity = cve.get("cve", {}).get("metrics", {}).get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseSeverity", "UNKNOWN").upper()
            
            embed = discord.Embed(title=cve_id, url=f"https://nvd.nist.gov/vuln/detail/{cve_id}", description=description, color=discord.Color.red())
            embed.add_field(name="🛑 Gravité", value=severity, inline=True)
            await channel.send(embed=embed)

        print("✅ CVE envoyées sur Discord.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des CVE : {e}")

# ✅ Démarrage du bot avec message de bienvenue
@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🤖 Le bot CVE est maintenant actif ! Tapez `!cve` pour voir les vulnérabilités récentes ou `!search <mot-clé>` pour rechercher une CVE.")

    fetch_vulnerabilities.start()

bot.run(TOKEN)