import asyncio
import json
import os
import time
import requests

import discord
from discord.ext import commands

from constants import EMBED_COLOR, TOKEN
from helpers import error_embed


class DsoPlatesolving(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ps"])
    async def platesolve(
        self,
        ctx,
        to_plate_solve: str = "MISSING",
        image_url_or_scale_units: str = "MISSING",
        scale_units_or_center_ra="MISSING",
        center_ra_or_center_dec="MISSING",
        center_dec_or_radius="MISSING",
        radius="MISSING",
    ) -> None:
        try:
            is_uploaded_image: bool = False
            to_plate_solve = to_plate_solve.lower()

            if to_plate_solve not in ["image", "url"]:
                await error_embed.send(ctx, "You can only platesolve `image` or `url`.")
                return
            elif to_plate_solve == "url":
                if image_url_or_scale_units == "MISSING":
                    await error_embed.send(ctx, "You must provide an image url!")
                    return
                image_url = image_url_or_scale_units
                scale_units = scale_units_or_center_ra.lower()
                center_ra = center_ra_or_center_dec
                center_dec = center_dec_or_radius
                radius = radius
            elif to_plate_solve == "image":
                if not ctx.message.attachments:
                    await error_embed.send(ctx, "You must attach an image!")
                    return

                is_uploaded_image = True
                image_url = ctx.message.attachments[0].url
                scale_units = image_url_or_scale_units.lower()
                center_ra = scale_units_or_center_ra
                center_dec = center_ra_or_center_dec
                radius = center_dec_or_radius
            else:
                await error_embed.send(ctx, "Some odd error occured!")
                return

            if scale_units not in ["degwidth", "arcminwidth", "arcsecperpix"]:
                await error_embed.send(
                    ctx,
                    "Only three types of scale units supported:\n- degwidth\n- arcminwidth\n- arcsecperpix",
                )
                return

            try:
                center_ra = float(center_ra)
            except ValueError:
                await error_embed.send(
                    ctx,
                    f"Center RA must be an integer or decimal!\n\nProblem is pointed at:\nplatesolve {'(url)' if not is_uploaded_image else ''} {scale_units} ->{center_ra}<- {center_dec} {radius}\n\n(assuming args are in order)",
                )
                return
            try:
                center_dec = float(center_dec)
            except ValueError:
                await error_embed.send(
                    ctx,
                    f"Center Dec must be an integer or decimal!\n\nProblem is pointed at:\nplatesolve {'(url)' if not is_uploaded_image else ''} {scale_units} {center_ra} ->{center_dec}<- {radius}\n\n(assuming args are in order)",
                )
                return
            try:
                radius = float(radius)
            except ValueError:
                await error_embed.send(
                    ctx,
                    f"Radius must be an integer or decimal!\n\nProblem is pointed at:\nplatesolve {'(url)' if not is_uploaded_image else ''} {scale_units} {center_ra} {center_dec} ->{radius}<-\n\n(assuming args are in order)",
                )
                return
            msg = await ctx.reply("**Uploading...**")

            resp = requests.post(
                "http://nova.astrometry.net/api/login",
                data={"request-json": json.dumps({"apikey": TOKEN("astrometry")})},
            )
            data = json.loads(resp.text)

            if data["status"] != "success":
                await error_embed.send(
                    ctx, "There was an error connecting to the astometry API."
                )
                await msg.delete()
                return

            session = data["session"]

            del resp
            # {"session": "dlldhwp42hcrdp57d1wbv6umqx01ys6b", "url": "http://apod.nasa.gov/apod/image/1206/ldn673s_block1123.jpg", "scale_units": "degwidth", "center_ra": 290, "center_dec": 11, "radius": 2.0 }

            payload = {
                "session": session,
                "url": image_url,
                "scale_units": scale_units,
                "center_ra": center_ra,
                "center_dec": center_dec,
                "radius": radius,
            }
            

            resp = requests.post(
                "http://nova.astrometry.net/api/url_upload",
                data={"request-json": json.dumps(payload)},
            )

            del data
            data = json.loads(resp.text)
            if data["status"] != "success":
                await error_embed.send(
                    ctx,
                    f"There was an error connecting to the astometry API.\n\n{data['errormessage']}",
                )
                await msg.delete()
                return
            
            subid = data["subid"]

            embed: discord.Embed = discord.Embed(
                title="Submitted",
                description=f"Please wait for it to process...\n\n**Subid:** {subid}",
                color=EMBED_COLOR
            )
            embed.set_footer(text="Checking...")
            await msg.edit(content="", embed=embed)
            
            del data
            timeout = False
            checks = 0
            while not timeout:
                resp = requests.get(f"http://nova.astrometry.net/api/submissions/{subid}")
                data = json.loads(resp.text)
                processing_end_datetime = data["processing_finished"]
                if processing_end_datetime != "None" and data["jobs"][0] is not None:
                    break
                elif checks > 10:
                    print("timeout reached")
                    timeout = True
                    break
                
                embed.set_footer(text=f"Still processing. Checks done: {checks}/10")
                await msg.edit(embed=embed)
                checks += 1;
                await asyncio.sleep(2)
            
            if timeout:
                embed.title="Uh oh!"
                embed.description = f"More than 10 checks were done and the image is still not finished processing.\nYou can check the status of your image manually here:\nhttps://nova.astrometry.net/status/{subid}."
                await ctx.reply(embed=embed)
                await msg.delete()
                return
            
            platesolved_job_id = data["jobs"][0]
            extraction_image = f"https://nova.astrometry.net/extraction_image_display/{platesolved_job_id}"
            
            del embed

            embed: discord.Embed = discord.Embed(
                title = "Finished Platesolving.",
                description=f"For annotated and red/green images, view the status here:\nhttps://nova.astrometry.net/status/{subid}\n\nHere is the extraction image:",
                color=EMBED_COLOR
            )
            embed.set_image(url=extraction_image)
            
            await ctx.reply(embed=embed)
            await msg.delete()

        except Exception as e:
            await error_embed.send(ctx, e)


async def setup(bot):
    await bot.add_cog(DsoPlatesolving(bot))
