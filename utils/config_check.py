from settings import get_guild_settings

async def check_bot_config(ctx_or_interaction):
    guild = ctx_or_interaction.guild
    settings = get_guild_settings(guild.id)

    missing = []
    if not settings.get("mod_role_ids"):
        missing.append("mod roles (`/add_mod_role`)")
    if not settings.get("log_channel_id"):
        missing.append("log channel (`/set_log_channel`)")
    if not settings.get("ticket_category_id"):
        missing.append("ticket category (`/set_ticket_category`)")

    if missing:
        msg = (
            "⚠️ This server has not completed bot setup.\n"
            "Missing: " + ", ".join(missing) + "."
        )

        if hasattr(ctx_or_interaction, "response"):  # slash command
            await ctx_or_interaction.response.send_message(msg, ephemeral=True)
        else:  # message context
            await ctx_or_interaction.send(msg)

        return None  # ⛔ Block further logic

    return settings  # ✅ Config is valid, return settings
