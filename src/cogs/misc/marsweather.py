import asyncio
import os
import time

import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from constants import EMBED_COLOR
from helpers import error_embed


class MiscMarsWeather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["mw"])
    async def marsweather(self, ctx, temp_unit = "f"):
        try:
            temp_unit = temp_unit.lower()
            if temp_unit not in ["f", "fahrenheit", "freedom", "c", "celcius", "eurotard"]:
                await error_embed.send(ctx, "Only F and C are valid temperature units.")
                return
            
            embed: discord.Embed = discord.Embed(
                title="Loading...",
                color=EMBED_COLOR
            )
            msg = await ctx.reply(embed=embed)
            
            url = "https://mars.nasa.gov/layout/embed/image/mslweather/"
            
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=980,650")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            await asyncio.sleep(2)
            
            driver.execute_script("var slashes = document.getElementsByClassName('slash'); for (var i = slashes.length - 1; i >= 0; i--) { slashes[0].parentNode.removeChild(slashes[0]); }")
            
            if "c" in temp_unit or temp_unit == "eurotard":
                unit_button = driver.find_element(By.CSS_SELECTOR, "html body.pageContent div#containerMain div#MSL-Weather-Report.section.embed div#Weather-Content.vCentered div#Weather-Data.vAlignTop.textWhite div.textLarger.vCentered div.temperatures.main.vCenteredInner.textLarge div.highs span.degree span.lbl_celsius.fadeWhite")
                unit_button.click()
                driver.execute_script("var fahrenheit = document.getElementsByClassName('lbl_fahrenheit'); for (var i = fahrenheit.length - 1; i >= 0; i--) { fahrenheit[0].parentNode.removeChild(fahrenheit[0]); }")
            else:
                driver.execute_script("var celciuses = document.getElementsByClassName('lbl_celsius'); for (var i = celciuses.length - 1; i >= 0; i--) { celciuses[0].parentNode.removeChild(celciuses[0]); }")
            
            image_path = os.path.abspath("./mars_weather.png")
            content = driver.find_element(By.ID, "containerMain")
            content.screenshot(image_path)
            
            
            await msg.delete()
            del embed
            
            file=discord.File(image_path, "latest_mars_weather.png")
            embed: discord.Embed = discord.Embed(
                title="Latest Mars Weather",
                color=EMBED_COLOR
            )
            embed.set_image(url="attachment://latest_mars_weather.png")
            await ctx.reply(file=file, embed=embed)
            
            os.remove(image_path)

        except Exception as e:
            await error_embed.send(ctx, e)


async def setup(bot):
    await bot.add_cog(MiscMarsWeather(bot))
