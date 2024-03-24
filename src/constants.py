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


HELP_DESCRIPTION = """
**Client Tools**
`help`, this
`latency`, get ping in ms
`info`, get some client info

More soon:tm:
"""
