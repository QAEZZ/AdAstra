import json

import discord
from discord.ext import commands

from helpers import error_embed


class DsoMessier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["messier"])
    async def m(self, ctx, number="help"):
        try:
            with open("data/messier.json", "r") as f:
                data = json.load(f)

            if (
                number == "help"
                or number.isspace()
                or not number.isnumeric()
                or int(number) > 110
                or int(number) <= 0
            ):
                await error_embed.send(ctx, "Usage:\n    messier <number 1-110>")
            else:
                m_info = data[f"M{number}"]
                title = f"{m_info['NGC']} (M{number})"
                desc = [
                    f"{m_info['TYPE'].capitalize()} located in/near {m_info['CONS']}.\n",
                    f"**Angular Size:** {m_info['SIZE']} arc-minutes",
                    f"**Distance:** {m_info['DIST (ly)']}ly away from the Earth",
                    f"**Best Visibility:** {m_info['VIEWING SEASON']}",
                    f"**Difficulty:** {m_info['VIEWING DIFFICULTY'].lower()} (medium-range telescopes)\n"
                    f"**Right Ascension:** {m_info['RA']}",
                    f"**Declination:** {m_info['DEC']}",
                    f"**Apparent Magnitude:** {m_info['MAG']}"
                ]

                embed = discord.Embed(
                    title=title, description='\n'.join(desc), color=discord.Color.dark_blue()
                )
                embed.set_image(url=f"{m_info['PHOTO']}")
                await ctx.send(embed=embed)

        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(DsoMessier(bot))
