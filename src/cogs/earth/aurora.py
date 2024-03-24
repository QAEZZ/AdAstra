import discord
from discord.ext import commands
from pathlib import Path
import string
import random
import glob
import json
import contextlib
import shutil
import requests
import os
import time
from datetime import datetime, timezone
from Paginator import Simple as Paginator
from constants import TOKEN, EMBED_COLOR
from helpers import error_embed
from PIL import Image
from io import BytesIO


class EarthAurora(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def aurora(self, ctx, option="future", direction="north"):
        try:
            if option.lower() not in ["future", "current"]:
                await error_embed.send(ctx, "Options are 'future' and 'current'.")
                return

            if direction.lower() not in ["north", "south"]:
                await error_embed.send(
                    ctx, "Auroras only happen north and south! Not E & W..."
                )
                return

            match option:
                case "current":
                    await self._send_current(ctx, direction)
                case _:
                    await self._send_future(ctx, direction)

        except Exception as e:
            await error_embed.send(ctx, e, False, True)

    async def _send_current(self, ctx, direction) -> None:
        embed: discord.Embed = discord.Embed(
            title="Aurora Forecast for the Next Hour.", color=EMBED_COLOR
        )
        embed.set_image(
            url=f"https://services.swpc.noaa.gov/images/animations/ovation/{direction.lower()}/latest.jpg"
        )
        await ctx.reply(embed=embed)

    async def _send_future(self, ctx, direction) -> None:
        embed = discord.Embed(
            title="Checking cache for GIF.", color=EMBED_COLOR
        )
        msg = await ctx.reply(embed=embed)
        
        Path(os.path.abspath("./cache")).mkdir(exist_ok=True)

        cached_gif_dir = os.path.abspath("./cache")
        cached_gif_pattern = f"swpc_aurora_{direction.lower()}_future_forecast_*.gif"
        cached_gifs = glob.glob(os.path.join(cached_gif_dir, cached_gif_pattern))

        if cached_gifs:
            embed.title = "Found cached GIF."
            await msg.edit(embed=embed)
            
            # Sort the cached GIFs by creation time
            cached_gifs.sort(key=os.path.getctime)
            cached_gif_path = cached_gifs[-1] 

            # Check if the latest cached GIF is within the 12-hour window
            creation_time = os.path.getctime(cached_gif_path)
            current_time = time.time()
            if current_time - creation_time < 12 * 60 * 60:
                embed.title="Cached GIF created <12 hours ago."
                embed.description = "```\nUploading...\n```"
                await msg.edit(embed=embed)
                
                file=discord.File(cached_gif_path, filename="aurora_future_forecast.gif")
                embed.title="Aurora Future Forecast"
                embed.description = None
                embed.set_image(url="attachment://aurora_future_forecast.gif")
                embed.set_footer(
                )
                embed.set_footer(text=f"This GIF is cached. It was created at {datetime.fromtimestamp(creation_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC. GIFs refresh every 12 hours.")
                await ctx.reply(file=file, embed=embed)
                await msg.delete()
                return

        resp = requests.get(
            f"https://services.swpc.noaa.gov/products/animations/ovation_{direction.lower()}_24h.json"
        )
        if not resp.ok:
            await error_embed.send(
                ctx, "There was an error fetching data from the SWPC."
            )
            return

        data = json.loads(resp.text)

        uid = "".join(random.choice(string.ascii_letters) for x in range(5))
        images_path = os.path.abspath(f"./temp/aurora")

        Path(images_path).mkdir(parents=True, exist_ok=True)

        embed.title = "Past 12 hours, creating new GIF."
        await msg.edit(embed=embed)

        data_len = len(data)
        count = 0
        for image in data:
            if count == 0 or count % 5 == 0:
                if count == 0 or count % 40 == 0:
                    embed.description = (
                        f"```\nFetching images ({round(count/data_len*100)}%)...\n```"
                    )
                    await msg.edit(embed=embed)

                resp = requests.get(
                    f"https://services.swpc.noaa.gov{image['url']}", stream=True
                )  # already provides a slash
                if resp.status_code == 200:
                    with open(f"{images_path}/{count}-{uid}.jpg", "wb") as f:
                        shutil.copyfileobj(resp.raw, f)
                del resp
            count += 1

        file_name = f"swpc_aurora_{direction.lower()}_future_forecast_{uid}.gif"
        with contextlib.ExitStack() as stack:
            embed.description = "```\nFetching all local images...\n```"
            await msg.edit(embed=embed)

            images = (
                stack.enter_context(Image.open(f))
                for f in sorted(glob.glob(f"{images_path}/*-{uid}.jpg"))
            )

            image = next(images)

            embed.description = "```\nCombining into one GIF...\n```"
            await msg.edit(embed=embed)
            # Add creation time as metadata to the GIF, not sure if this actually works.
            creation_time = datetime.now(timezone.utc)
            creation_time_str = creation_time.strftime("%Y-%m-%d %H:%M:%S")
            creation_time_bytes = creation_time_str.encode("utf-8")
            image.info["CreationTime"] = creation_time_bytes
            image.save(
                fp=file_name,
                # fp=f"swpc_aurora_{direction.lower()}_future_forcast-{uid}.gif",
                format="GIF",
                append_images=images,
                save_all=True,
                duration=200,
                loop=0,
            )

        embed = discord.Embed(title="Aurora Future Forecast", color=EMBED_COLOR)

        embed.set_image(url=f"attachment://{file_name}")
        await ctx.reply(file=discord.File(file_name), embed=embed)
        await msg.delete()

        ## Clean-up and caching
        shutil.move(
            os.path.abspath(f"./{file_name}"), os.path.abspath(f"./cache/{file_name}")
        )
        
        for image in glob.glob(f"{os.path.abspath('./temp/aurora')}/*-{uid}.jpg"):
            os.remove(image)

    # async def _send_future(self, ctx, direction) -> None:
    #     resp = requests.get(f"https://services.swpc.noaa.gov/products/animations/ovation_{direction.lower()}_24h.json");
    #     if not resp.ok:
    #         await error_embed.send(ctx, "There was an error fetching data from the SWPC.")
    #         return

    #     data = json.loads(resp.text)

    #     uid = ''.join(random.choice(string.ascii_letters) for x in range (5))
    #     images_path = os.path.abspath(f"./temp/aurora")

    #     Path(images_path).mkdir(parents=True, exist_ok=True)

    #     embed: discord.Embed = discord.Embed(
    #         title="Loading",
    #         color=EMBED_COLOR
    #     )
    #     msg = await ctx.reply(embed=embed)

    #     data_len = len(data)
    #     count = 0
    #     for image in data:
    #         if count == 0 or count % 5 == 0:
    #             if count == 0 or count % 40 == 0:
    #                 embed.description = f"```\nFetching image ({round(count/data_len*100)}%)...\n```"
    #                 await msg.edit(embed=embed)

    #             resp = requests.get(f"https://services.swpc.noaa.gov{image['url']}", stream=True) # already provides a slash
    #             if resp.status_code == 200:
    #                 with open (f"{images_path}/{count}-{uid}.jpg", "wb") as f:
    #                     shutil.copyfileobj(resp.raw, f)
    #             del resp
    #         count += 1;

    #     with contextlib.ExitStack() as stack:
    #         embed.description = "```\nFetching all local images...\n```"
    #         await msg.edit(embed=embed)

    #         images = (stack.enter_context(Image.open(f)) for f in sorted(glob.glob(f"{images_path}/*-{uid}.jpg")))

    #         image = next(images)

    #         embed.description = "```\nCombining into one GIF...\n```"
    #         await msg.edit(embed=embed)
    #         # output_path = os.path.abspath(f"./{images_path}/swpc_aurora_{direction.lower()}_future_forcast-{uid}.gif")
    #         image.save(fp=f"swpc_aurora_{direction.lower()}_future_forcast-{uid}.gif", format="GIF", append_images=images, save_all=True, duration=200, loop=0)

    #     embed: discord.Embed = discord.Embed(
    #         title="Aurora Future Forecast",
    #         color=EMBED_COLOR
    #     )

    #     file_name = f"swpc_aurora_{direction.lower()}_future_forcast-{uid}.gif"
    #     embed.set_image(url=f"attachment://{file_name}")
    #     await ctx.reply(file=discord.File(file_name), embed=embed)
    #     await msg.delete()


async def setup(bot):
    await bot.add_cog(EarthAurora(bot))
