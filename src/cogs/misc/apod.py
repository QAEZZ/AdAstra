import discord
from discord.ext import commands
import json
import requests
from helpers import error_embed
from constants import TOKEN, EMBED_COLOR


class MiscApod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def apod(self, ctx):
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={TOKEN('nasa')}"
            resp = requests.get(url)
            data = json.loads(resp.text)
            
            title = data["title"]
            desc = data["explanation"]
            date = data["date"]
            hd_img = data["hdurl"]
            
            embed: discord.Embed = discord.Embed(
                title=f"{title} **•** *{date}*",
                description=desc,
                color=EMBED_COLOR
            )
            embed.set_image(url=hd_img)
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await error_embed.send(ctx, e, False)


async def setup(bot):
    await bot.add_cog(MiscApod(bot))
