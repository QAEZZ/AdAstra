import contextlib
import glob
import json
import os
import random
import shutil
import string
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import discord
import requests
from discord.ext import commands
from Paginator import Simple as Paginator
from PIL import Image

from constants import EMBED_COLOR, TOKEN, logger
from helpers import error_embed, images_to_gif, uid


class SunSuvi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def suvi(self, ctx, option="animation", composite="195"):
        try:
            if option.lower() not in ["animation", "latest"]:
                await error_embed.send(ctx, "Options are 'animation' and 'latest'.")
                return
            
            composite_types = ["094", "131", "171", "195", "284", "304", "map"]
            if composite.lower() not in composite_types:
                await error_embed.send(ctx, f"The only composite types allowed are:\n - " + "\n - ".join(composite_types) + f"\n\nYou entered, '{composite.lower()}'.")
                return

            match option:
                case "latest":
                    await self._send_latest(ctx, composite.lower())
                case _:
                    await self._send_animation(ctx, composite.lower())

        except Exception as e:
            await error_embed.send(ctx, e, False, True)

    async def _send_latest(self, ctx, composite) -> None:
        why_does_discord_cache_this_image_anyways_here_is_a_uid_to_bypass_the_cache = (
            uid.gen()
        )
        embed: discord.Embed = discord.Embed(
            title=f"Latest EUV Image of the Sun.", color=EMBED_COLOR
        )
        embed.set_image(
            url=f"https://services.swpc.noaa.gov/images/animations/suvi/primary/{composite}/latest.png?{why_does_discord_cache_this_image_anyways_here_is_a_uid_to_bypass_the_cache}={why_does_discord_cache_this_image_anyways_here_is_a_uid_to_bypass_the_cache}"
        )
        await ctx.reply(embed=embed)

    async def _send_animation(self, ctx, composite) -> None:
        embed = discord.Embed(title="Checking cache for GIF.", color=EMBED_COLOR)
        msg = await ctx.reply(embed=embed)

        Path(os.path.abspath("./cache")).mkdir(exist_ok=True)

        cached_gif_dir = os.path.abspath("./cache")
        cached_gif_pattern = f"swpc_suvi_{composite}_animation.gif"
        cached_gifs = glob.glob(os.path.join(cached_gif_dir, cached_gif_pattern))

        if cached_gifs:

            # Sort the cached GIFs by creation time
            cached_gifs.sort(key=os.path.getctime)
            cached_gif_path = cached_gifs[-1]

            # Check if the latest cached GIF is within the 2-hour window
            creation_time = os.path.getctime(cached_gif_path)
            current_time = time.time()

            logger.debug(f"ctime: {creation_time}, curtime: {current_time}")
            logger.debug(f"ctime - curtime: {creation_time - current_time}")
            logger.debug(f"eq: {current_time - creation_time} < {2 * 60 * 60}")

            if current_time - creation_time < 2 * 60 * 60:
                embed.title = "Cached GIF created <2 hours ago."
                embed.description = "```\nUploading...\n```"
                await msg.edit(embed=embed)

                file = discord.File(
                    cached_gif_path, filename=f"suvi_{composite}_animation.gif"
                )
                embed.title = f"Animation of the Sun's EUV (Comp. {composite})."
                embed.url = f"https://services.swpc.noaa.gov/images/animations/suvi/primary/{composite}/latest.png"
                embed.description = None
                embed.set_image(url=f"attachment://suvi_{composite}_animation.gif")
                embed.set_footer(
                    text=f"This GIF is cached. It was created at {datetime.fromtimestamp(creation_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC. GIFs refresh every 2 hours."
                )
                await ctx.reply(file=file, embed=embed)
                await msg.delete()
                return

        resp = requests.get(
            f"https://services.swpc.noaa.gov/products/animations/suvi-primary-{composite}.json"
        )
        if not resp.ok:
            await error_embed.send(
                ctx, "There was an error fetching data from the SWPC."
            )
            return

        data = json.loads(resp.text)

        _uid = uid.gen(5)
        images_path = os.path.abspath(f"./temp/suvi/{composite}")

        Path(images_path).mkdir(parents=True, exist_ok=True)

        embed.title = "Past 2 hours, creating new GIF."
        await msg.edit(embed=embed)
        await images_to_gif.download_images(
            data,
            images_path,
            _uid,
            f"https://services.swpc.noaa.gov",
            "jpg",
            1,
            send_progress=True,
            embed=embed,
            msg=msg,
            send_dropped_frames_error=True,
            ctx=ctx,
        )

        file_name = f"swpc_suvi_{composite}_animation_{_uid}.gif"

        await images_to_gif.compile_images_to_gif(
            images_path,
            _uid,
            file_name,
            "jpg",
            send_progress=True,
            embed=embed,
            msg=msg,
        )

        embed = discord.Embed(title=f"Animation of the Sun's EUV (Comp. {composite}).", color=EMBED_COLOR)
        embed.url = f"https://services.swpc.noaa.gov/images/animations/suvi/primary/{composite}/latest.png"

        embed.set_image(url=f"attachment://{file_name}")
        await ctx.reply(file=discord.File(file_name), embed=embed)
        await msg.delete()

        ## Clean-up and caching
        shutil.move(
            os.path.abspath(f"./{file_name}"), os.path.abspath(f"./cache/swpc_suvi_{composite}_animation.gif")
        )

        for image in glob.glob(f"{os.path.abspath(f'./temp/suvi/')}/*-{_uid}.jpg"):
            os.remove(image)


async def setup(bot):
    await bot.add_cog(SunSuvi(bot))
