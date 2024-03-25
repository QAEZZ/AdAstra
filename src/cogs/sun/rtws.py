import json

import discord
import requests
from discord.ext import commands

from constants import EMBED_COLOR
from helpers import error_embed


class SunRtws(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rtws(self, ctx):
        try:
            resp = requests.get("https://services.swpc.noaa.gov/products/solar-wind/plasma-5-minute.json")
            if not resp.ok:
                await error_embed.send(ctx, "There was an error reaching out to SWPC.")
                return
            
            data = json.loads(resp.text)
            
            embed: discord.Embed = discord.Embed(
                title="Solar Wind Speed",
                description=f"**{data[-1][2]}** km/sec",
                color=EMBED_COLOR
            )
            embed.set_footer(text="Updated every 5 minutes.")
            await ctx.reply(embed=embed)

        except Exception as e:
            await error_embed.send(ctx, e, False, True)


async def setup(bot):
    await bot.add_cog(SunRtws(bot))
