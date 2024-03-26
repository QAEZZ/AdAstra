import json
from typing import Union

import discord
from discord.ext import commands
from pyongc import ongc

from constants import EMBED_COLOR, HELP_DESCRIPTION, LOGO, PREFIX
from helpers import dso, error_embed


class DsoLookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RA_ERROR_MESSAGE = "Could not verify the format of RA.\n\nExamples of acceptable formats:\n- 12.662\n- 3:47:24\n- H:M:S"
        self.DEC_ERROR_MESSAGE = "Could not verify the format of Dec.\n\nExamples of acceptable formats:\n- -11.623\n- +24:7:0\n- D:M:S"

    @commands.command()
    async def lookup(self, ctx, type = "MISSING", fov = None, name_or_ra = None, dec = None) -> None:
        try:
            if type.lower() not in ["name", "coords"]:
                await error_embed.send(ctx, "You can only look up `name` or `coords` (ra and dec)")
                return
            elif fov is None:
                await error_embed.send(ctx, "You haven't provided an FOV!")
                return
            elif name_or_ra is None:
                await error_embed.send(ctx, "You haven't provided a name!" if type.lower() == "name" else "You must provide RA DEC coordinates!")
                return
            
            match type.lower():
                case "name":
                    res = dso.object_name_to_coordinates(name_or_ra)
                    if not res[0]:
                        if res[1] == 1.0:
                            await error_embed.send(ctx, self.RA_ERROR_MESSAGE)
                            return
                        elif res[2] == 1.0:
                            await error_embed.send(ctx, self.DEC_ERROR_MESSAGE)
                            return
                        else:
                            await error_embed.send(ctx, res[-1])
                            return
                        
                    await self._get_dso(ctx, fov, res[1][1], res[2][1], name_or_ra)
                case _:
                    await self._get_dso(ctx, fov, name_or_ra, dec)

        except Exception as e:
            await error_embed.send(ctx, e, False, True)
            
    
    async def _get_dso(self, ctx, fov, ra: Union[float, str], dec: Union[float, str], name = None, object_rotation = 0) -> None:
        if type(ra).__name__ == "str" and ":" in ra:
            ra = dso.ra_time_to_hours(ra)
            if not ra[0]:
                await error_embed.send(ctx, self.RA_ERROR_MESSAGE)
                return
            ra = ra[1]
        if type(dec).__name__ == "str" and ":" in dec:
            dec = dso.declination_to_degrees(dec)
            if not dec[0]:
                await error_embed.send(ctx, self.DEC_ERROR_MESSAGE)
                return
            dec = dec[1]

        try: ra = float(ra)
        except TypeError:
            await error_embed.send(ctx, self.RA_ERROR_MESSAGE)
            return
        
        try: dec = float(dec)
        except TypeError: 
            await error_embed.send(ctx, self.DEC_ERROR_MESSAGE)
            return
        
        ra = f"{ra:.7f}"
        dec = f"{dec:.7f}"
        
        # TODO: Get the object name at the coords.
        
        embed: discord.Embed = discord.Embed(
            title=f"{ra} {dec}",
            color=EMBED_COLOR
        )
        
        if name is not None:
            object = ongc.get(name)
            object_name = object.name
            object_constellation = object.constellation
            object_surface_brightness = object.surface_brightness
            messier_name, ngc_names, ic_names, common_names, other_names = object.identifiers
            object_redshift = object.redshift 
            object_type = object.type
            object_notes = object.notes
            object_rotation = object.dimensions[2] or 0
            
                        
            embed.title = f"{object_name} **•** {object_type}"
            embed.description = " ".join(object_notes)
            
            embed.add_field(name="RA Hours", value=ra)
            embed.add_field(name="Dec Degrees", value=dec)
            embed.add_field(name="FOV Degrees", value=fov)
            embed.add_field(name="Constellation", value=object_constellation)
            
            if object_surface_brightness is not None:
                embed.add_field(name="Surface Brightness", value=f"{object_surface_brightness} mag/arcsec²")
            if object_redshift is not None:
                embed.add_field(name="Redshift", value=f"{object_redshift:f}")
            
            names_with_categories = []
            if messier_name:
                names_with_categories.append(f"{messier_name}")

            if ngc_names:
                ngc_names_str = "\n".join([f"{name}" for name in ngc_names])
                names_with_categories.append(ngc_names_str)

            if ic_names:
                ic_names_str = "\n".join([f"{name}" for name in ic_names])
                names_with_categories.append(ic_names_str)

            if common_names:
                common_names_str = "\n".join([f"{name}" for name in common_names])
                names_with_categories.append(common_names_str)

            if other_names:
                other_names_str = "\n".join([f"{name}" for name in other_names])
                names_with_categories.append(other_names_str)

            embed.description = f"{embed.description}\n**Names:**\n" + "\n".join(names_with_categories)
            
            
            
        img = dso.get_object_image_from_coords(fov, ra, dec, object_rotation)
        
        embed.set_image(url=img)
        embed.set_footer(text="Image may be wrong.")
        
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(DsoLookup(bot))