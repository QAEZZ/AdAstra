import json

import discord
import requests
from discord.ext import commands

from constants import EMBED_COLOR, TOKEN
from helpers import error_embed


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
            media_url = data["url"]
            
            
            embed: discord.Embed = discord.Embed(
                title=f"{title} **•** *{date}*",
                description=desc,
                color=EMBED_COLOR
            )
            
            if "youtube" in media_url:
                embed.url = media_url
                embed.set_image(url=f"https://img.youtube.com/vi/{media_url.split('/')[-1].replace('?rel=0', '')}/sd1.jpg")
            else:
                embed.set_image(url=media_url)
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await error_embed.send(ctx, e, False)


async def setup(bot):
    await bot.add_cog(MiscApod(bot))
