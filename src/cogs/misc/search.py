import json
import urllib.parse
from urllib.request import urlopen

import discord
from discord.ext import commands

from helpers import error_embed


class MiscSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter_cap = 25

    @commands.command()
    async def search(self, ctx, media="MISSING", *, query=""):
        media_types = ["image", "video", "audio"]
        if media.lower() not in media_types:
            await error_embed.send(ctx, "Invalid media type\nAvailable media types:\n image\n video\n audio\n\nExample: search image [query]")
            return
        
        try:
            url_query = urllib.parse.quote(query)
            api_url = f"https://images-api.nasa.gov/search?media_type={media}&q={url_query}"
            norm_url = f"https://images.nasa.gov/search-results?q={url_query}&page=1&media={media}&yearStart=1920&yearEnd=2024"
            response = urlopen(api_url)
            data = json.load(response)
            
            total_hits = data["collection"]["metadata"]["total_hits"]
            if total_hits == 0:
                await error_embed.send(ctx, "No posts found.")
                return
                
            embed = discord.Embed(
                title=f"{media.capitalize()} search for {query}",
                url=norm_url,
                color=discord.Color.dark_blue()
            )
            embed.set_thumbnail(url="https://www.nasa.gov/wp-content/themes/nasa/assets/images/nasa-logo@2x.png")
            
            for counter, item in enumerate(data["collection"]["items"], start=1):
                if counter > self.counter_cap:
                    break
                
                title = item["data"][0]["title"]
                desc = item["data"][0]["description"]
                nasa_id = item["data"][0]["nasa_id"]
                date_created = item["data"][0]["date_created"][:len(item["data"][0]["date_created"]) - 16]
                
                title = (title[:252] + "...") if len(title) > 256 else title
                
                embed.add_field(
                    name=f"[{counter}] {title} • {date_created}\nNASA ID: ``{nasa_id}``",
                    value=f"{desc[:50]}... ({-50 + len(desc)} omitted)\nhttps://images.nasa.gov/details-{urllib.parse.quote(nasa_id)}",
                    inline=False
                )
                
            embed.set_footer(text=f"Total hits: {total_hits} | Max results: {self.counter_cap}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await error_embed.send(ctx, e)

async def setup(bot):
    await bot.add_cog(MiscSearch(bot))
