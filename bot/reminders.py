import asyncio
from discord.ext import commands

@commands.command(name="reminder")
async def reminder(ctx, time: int, *, message: str):
    """Définit un rappel après un certain nombre de minutes."""
    if time <= 0:
        await ctx.send("⏳ Le temps doit être supérieur à 0 minute.")
        return

    await ctx.send(f"✅ Rappel défini dans {time} minute(s) : `{message}`")
    await asyncio.sleep(time * 60)  # Convertit les minutes en secondes
    await ctx.send(f"🔔 **Rappel pour {ctx.author.mention} :** {message}")