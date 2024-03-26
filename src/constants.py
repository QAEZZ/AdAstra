import discord

from logger import Logger

logger: Logger = Logger("Ad Astra")

INTENTS = discord.Intents.default()
INTENTS.message_content = True

EMBED_COLOR = discord.Color.from_rgb(67, 94, 121)
LOGO = "https://cdn.discordapp.com/attachments/1089094022351556729/1221316867944091759/Ad_Astra_Bot_New_Logo.png"
PREFIX = ";"

CLIENT_ID = 1221308395903123486
CLIENT_OWNER = 1123758641485459477
ACTIVITY = discord.Game("with rockets.")

COG_ACCESS = [CLIENT_OWNER]
COOLDOWN_BYPASS = [COG_ACCESS]


def TOKEN(token_name) -> str:
    """Returns contents of `client_secrets/{token_name}.key`"""
    with open(f"client_secrets/{token_name}.key", "r") as f:
        return f.read()


HELP_DESCRIPTION = f"""
**Client Tools**
 `help`    this
 `latency` get ping in ms
 `info`    get some client info

**Earth-related Commands**
 `aurora`  get aurora forecast
 `epic`    get EPIC images

**Sun-related Commands**
 `lasco`   get LASCO CX images
 `rtws`    get solar wind speed
 `suvi`    get Sol's EUV images
 
**DSO-related Commands**
 `lookup`  get an image of a DSO
 `messier` get info on a Messier DSO
 `platesolve` get a ps'd image

**Miscellaneous Commands**
 `apod`    get astronomy photo of the day
 `marsweather` get latest weater on Mars
 `post`    get a post from a subreddit
 `search`  NASA search engine
 
**NOTE:**
  Square brackets indicate optional arguments.
  Angled brackets indicate required arguments.

*Use `{PREFIX}help [command name]` to get more info on a command, such as arguments required.*
"""
