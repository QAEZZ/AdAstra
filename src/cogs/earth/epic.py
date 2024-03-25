import glob
import json
import os
import shutil
from datetime import date
from pathlib import Path

import discord
import requests
from discord.ext import commands
from Paginator import Simple as Paginator

from constants import EMBED_COLOR, TOKEN
from helpers import error_embed, uid

todays_date = date.today()
current_year, current_month, current_day = (
    todays_date.year,
    todays_date.month,
    todays_date.day,
)


class EarthEpic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def epic(self, ctx, collection="MISSING", year="MISSING", month="MISSING", day="MISSING"):
        try:
            try:
                collection = collection.lower()
                if collection not in ["natural", "enhanced"]:
                    await error_embed.send(
                        ctx, "Invalid collection, use 'natural' or 'enhanced'."
                    )
                    return
            except ValueError:
                await error_embed.send(
                    ctx, "Invalid collection, use 'natural' or 'enhanced'."
                )
                return

            if not all([year, month, day]):
                await error_embed.send(ctx, "Invalid date, use format YYYY MM DD.")
                return

            try:
                year, month, day = int(year), int(month), int(day)
            except ValueError:
                await error_embed.send(
                    ctx, "Invalid date format, use format YYYY MM DD."
                )
                return

            if year > current_year or month > 12 or day > 31:
                await error_embed.send(ctx, "Invalid date values.")
                return

            url = f"https://epic.gsfc.nasa.gov/api/{collection}/date/{year}-{month:02d}-{day:02d}?api_key={TOKEN('nasa')}"

            resp = requests.get(url)
            if not resp.ok:
                await error_embed.send(ctx, "Couldn't reach out to GSFC.")
                return
            
            data = json.loads(resp.text)

            loading_em = discord.Embed(title="Loading...", color=EMBED_COLOR)
            loading_msg = await ctx.send(embed=loading_em)
            
            epic_data_directory = os.path.abspath("./temp/epic_data")

            Path(epic_data_directory).mkdir(parents=True, exist_ok=True)

            _uid = uid.gen(5)
            for idx, item in enumerate(data, start=1):
                image = item["image"]
                caption = item["caption"]
                date = item["date"]
                image_url = f"https://epic.gsfc.nasa.gov/archive/{collection}/{year}/{month:02d}/{day:02d}/jpg/{image}.jpg"

                data_to_dump = {"CAPTION": caption, "DATE": date, "imageUrl": image_url}
                with open(f"{epic_data_directory}/e{idx}-{_uid}.json", "w") as f:
                    json.dump(data_to_dump, f, indent=4)

            await loading_msg.delete()

            pages = []
            for i in range(15, 0, -1):
                response_path = f"{epic_data_directory}/e{i}-{_uid}.json"
                if os.path.exists(response_path):
                    response_data = json.load(open(response_path))
                    date = response_data["DATE"]
                    caption = response_data["CAPTION"]
                    image_url = response_data["imageUrl"]
                    embed = discord.Embed(
                        title=date, description=caption, color=discord.Color.dark_blue()
                    )
                    embed.set_image(url=image_url)
                    embed.set_footer(text=f"Requested by {ctx.author}")
                    pages.append(embed)

            if not pages:
                await ctx.send("No files found.")
                return

            paginator = Paginator()
            await paginator.start(ctx, pages=pages)
            
            ## Clean-up        
            for file in glob.glob(f"{os.path.abspath('./temp/epic_data')}/e*-{_uid}.json"):
                os.remove(file)

        except Exception as e:
            await error_embed.send(ctx=ctx, e=e, print_error=True, print_traceback=True)


async def setup(bot):
    await bot.add_cog(EarthEpic(bot))
