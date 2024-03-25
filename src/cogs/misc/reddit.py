import random

import asyncpraw
import discord
from discord.ext import commands

from constants import EMBED_COLOR, TOKEN
from helpers import error_embed


class MiscReddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = None
    
    async def _setup_reddit(self) -> asyncpraw.Reddit:
        self.reddit = asyncpraw.Reddit(client_id=TOKEN("reddit/id"),
                                        client_secret=TOKEN("reddit/secret"),
                                        username=TOKEN("reddit/username"),
                                        password="",
                                        user_agent="redditisgreedy")
        return self.reddit

    @commands.command()
    async def post(self, ctx, subreddit = "astrophotography", post_type = "image"):
        try:   
            await self._setup_reddit()
            valid_subreddits = ["spaceporn", "astrophotography", "space"]
            if subreddit not in valid_subreddits:
                await ctx.send("Invalid subreddit. Please choose from 'astrophotography', 'spaceporn', or 'space'.")
                return

            valid_post_types = ["image", "text"]
            if post_type not in valid_post_types:
                await ctx.send("Invalid post type. Please choose from 'image' or 'text'.")
                return

            embed = discord.Embed(title=f"Loading an r/{subreddit} post from hot.",
                                color=EMBED_COLOR)
            message = await ctx.send(embed=embed)

            async with self.reddit:
                subreddit = await self.reddit.subreddit(subreddit)
                all_subs = []
                async for submission in subreddit.hot(limit=50):
                    await submission.load()
                    if (post_type == "image" and not submission.is_self) or (post_type == "text" and submission.is_self):
                        all_subs.append(submission)

                if not all_subs:
                    await message.edit(content="No posts found matching the criteria.")
                    return

                random_sub = random.choice(all_subs)
                name = random_sub.title
                url = random_sub.url
                em = discord.Embed(title=f"{name} - r/{subreddit.display_name}",
                                url=f"https://reddit.com{random_sub.permalink}",
                                color=EMBED_COLOR)
                if post_type == "image":
                    em.set_image(url=url)
                await message.edit(embed=em)
        
        except Exception as e:
            await error_embed.send(ctx, e, False, True)

async def setup(bot):
    await bot.add_cog(MiscReddit(bot))
