import discord
import requests
import os
from discord.ext import tasks
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

API_URL_CVE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

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

        self.children[0].disabled = self.index == 0
        self.children[1].disabled = self.index == len(self.cve_data) - 1

        await interaction.response.edit_message(embed=embed, view=self)

async def send_cve_to_discord(bot):
    """Récupère les CVE et les envoie sur Discord."""
    print("🔍 Récupération des CVE...")
    try:
        response = requests.get(API_URL_CVE, timeout=10)
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

@tasks.loop(hours=6)
async def fetch_vulnerabilities(bot):
    """Exécute la récupération des CVE toutes les 6h."""
    await send_cve_to_discord(bot)