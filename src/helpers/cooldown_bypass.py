from constants import COOLDOWN_BYPASS

def bypass_cooldown(ctx, cmd):
    if ctx.author.id in COOLDOWN_BYPASS:
        cmd.reset_cooldown(ctx)