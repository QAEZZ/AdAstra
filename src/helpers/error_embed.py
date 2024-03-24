from discord import Embed, Color
from constants import LOGO, logger
import traceback

async def send(ctx, e, print_error: bool = False, print_traceback: bool = False):
    if print_error: logger.error(e)
    elif print_traceback: traceback.print_exc()
        
    embed: Embed = Embed(
        description=f"```{e}```", color=Color.from_rgb(255,100,100)
    )
    embed.set_thumbnail(url=LOGO)
    await ctx.reply(embed=embed)