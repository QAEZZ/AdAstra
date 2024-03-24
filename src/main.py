#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from constants import INTENTS, COG_ACCESS, logger, EMBED_COLOR, TOKEN, PREFIX
from helpers import error_embed


class Client(commands.Bot):
    """Class to make a client, gonna be a lot of
    these little docstrings because of pylint.

    Args:
        commands.bot: Represents a Discord bot. Subclass of :class:`discord.Client`.
    """

    def __init__(self) -> None:
        super().__init__(
            intents=INTENTS,
            help_command=None,
            command_prefix=commands.when_mentioned_or(PREFIX),
        )

    async def setup_hook(self) -> None:
        logger.info("Finding cogs to load...")
        children = [os.path.join("cogs", child) for child in os.listdir("cogs")]
        cog_folders = filter(os.path.isdir, children)
        for folder in cog_folders:
            for filename in os.listdir(folder):
                if filename.endswith(".py"):
                    try:
                        directory = folder.replace("cogs/", "")
                        await self.load_extension(f"cogs.{directory}.{filename[:-3]}")
                        logger.success(f"Loaded cogs.{directory}.{filename}")
                    except Exception as e:
                        logger.error(str(e))

    async def on_ready(self) -> None:
        """Runs once the client is connected to the Discord Gateway."""
        logger.info(f"Logged in as {self.user.name}")
        logger.info(f"API version: {discord.__version__}\n")

    async def on_command_error(self, ctx: Context, error) -> None:

        embed = discord.Embed(title="Error!", color=EMBED_COLOR)

        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed.description = f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}."

        elif isinstance(error, commands.NotOwner):
            embed.description = "You are not the owner of the bot!"
            if ctx.guild:
                logger.important(
                    f"{ctx.author} (ID: {ctx.author.id}) tried to execute an owner only command in the guild {ctx.guild.name} (ID: {ctx.guild.id}), but the user is not an owner of the bot."
                )
            else:
                logger.important(
                    f"{ctx.author} (ID: {ctx.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )

        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=EMBED_COLOR,
            )

        elif isinstance(error, commands.BotMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            embed.description = f"I am missing the permission(s) `{missing_permissions}` to fully perform this command!"

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"```\n{str(error).capitalize()}\n```"

        await ctx.reply(embed=embed)


client = Client()

def _cog_access(ctx):
    if ctx.author.id in COG_ACCESS:
        return True
    return False

@client.command()
@commands.check(_cog_access)
async def load(ctx, cog: str):
    cog_helper = cogs.CogHelper(client, ctx)
    await cog_helper.load(cog)


@client.command()
@commands.check(_cog_access)
async def unload(ctx, cog: str):
    cog_helper = cogs.CogHelper(client, ctx)
    await cog_helper.unload(cog)


@client.command()
@commands.check(_cog_access)
async def reload(ctx, cog: str):
    cog_helper = cogs.CogHelper(client, ctx)
    await cog_helper.reload(cog)


@client.command()
@commands.is_owner()
async def shutdown(self, ctx: Context) -> None:
    embed = discord.Embed(
        description="Shutting down. Bye! :wave:", color=EMBED_COLOR
    )
    await ctx.reply(embed=embed)
    await self.bot.close()

if __name__ == "__main__":
    client.run(TOKEN("discord"))
