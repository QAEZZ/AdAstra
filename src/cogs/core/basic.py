import json

import discord
from discord.ext import commands

from constants import EMBED_COLOR, HELP_DESCRIPTION, LOGO, PREFIX
from helpers import error_embed


class CoreHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command_name = None):
        try:
            embed: discord.Embed = discord.Embed(
                title="Ad Astra — To the Stars",
                color=EMBED_COLOR,
                description=HELP_DESCRIPTION,
            )
            embed.set_thumbnail(url=LOGO)

            if command_name:
                with open("data/help.json", "r") as file:
                    help_data = json.load(file)

                    command_info = help_data.get(command_name.lower())
                    if command_info:
                        embed.title = f"Help for command {command_name}"
                        embed.description = command_info["description"]
                        embed.add_field(
                            name="Usage", value=f"```{PREFIX}{command_info['usage']}```"
                        )
                        
                        if "footer" in command_info:
                            embed.set_footer(text=command_info["footer"])

                        if "image" in command_info:
                            embed.set_image(url=command_info["image"])


            await ctx.reply(embed=embed)

        except Exception as e:
            await error_embed.send(ctx, e)

    @commands.command()
    async def info(self, ctx):
        embed: discord.Embed = discord.Embed(color=EMBED_COLOR)
        embed.add_field(name="Wrapper", value="```discord.py```")
        embed.add_field(name="Creator", value="```qaezz```")

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(CoreHelp(bot))