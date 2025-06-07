import discord
from discord import app_commands, Interaction
from discord.ext import commands
from settings import get_guild_settings, set_guild_setting
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class ConfigHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_log_channel", description="Set the log channel for ticket logs")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="The channel where logs should be posted")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def set_log_channel(self, interaction: Interaction, channel: discord.TextChannel):
        set_guild_setting(interaction.guild.id, "log_channel_id", str(channel.id))
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="set_ticket_category", description="Set the ticket channel category")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(category="The category where tickets should be created")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def set_ticket_category(self, interaction: Interaction, category: discord.CategoryChannel):
        set_guild_setting(interaction.guild.id, "ticket_category_id", str(category.id))
        await interaction.response.send_message(f"✅ Ticket category set to `{category.name}`", ephemeral=True)

    @app_commands.command(name="add_mod_role", description="Add a role that can manage tickets")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="Role to be given mod access")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add_mod_role(self, interaction: Interaction, role: discord.Role):
        settings = get_guild_settings(interaction.guild.id)
        mod_roles = settings.get("mod_role_ids", [])
        if role.id in mod_roles:
            return await interaction.response.send_message("⚠️ That role is already a mod role.", ephemeral=True)

        mod_roles.append(role.id)
        set_guild_setting(interaction.guild.id, "mod_role_ids", mod_roles)
        await interaction.response.send_message(f"✅ Added `{role.name}` as a mod role.", ephemeral=True)

    @app_commands.command(name="list_help", description="List current help options")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def list_help(self, interaction: Interaction):
        settings = get_guild_settings(interaction.guild.id)
        options = settings["help_options"]

        if not options:
            await interaction.response.send_message("⚠️ No help options configured.", ephemeral=True)
        else:
            msg = "\n".join(f"{o['number']}. **{o['label']}** (`{o['keyword']}`)" for o in options)
            await interaction.response.send_message(f"📋 Current Help Options:\n{msg}", ephemeral=True)

    @app_commands.command(name="add_help", description="Add a new help option")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(number="Display number", keyword="Trigger word", label="Help label")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add_help(self, interaction: Interaction, number: str, keyword: str, label: str):
        settings = get_guild_settings(interaction.guild.id)
        options = settings["help_options"]

        if any(o["number"] == number or o["keyword"].lower() == keyword.lower() for o in options):
            return await interaction.response.send_message("❌ Number or keyword already exists.", ephemeral=True)

        options.append({"number": number, "keyword": keyword, "label": label})
        set_guild_setting(interaction.guild.id, "help_options", options)
        await interaction.response.send_message(f"✅ Added help option: {number}. {label} (`{keyword}`)", ephemeral=True)

    @app_commands.command(name="remove_help", description="Remove a help option by number or keyword")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(identifier="Enter number or keyword to remove")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def remove_help(self, interaction: Interaction, identifier: str):
        settings = get_guild_settings(interaction.guild.id)
        options = settings["help_options"]
        new_options = [o for o in options if o["number"] != identifier and o["keyword"].lower() != identifier.lower()]

        if len(new_options) == len(options):
            return await interaction.response.send_message("❌ No matching option found.", ephemeral=True)

        set_guild_setting(interaction.guild.id, "help_options", new_options)
        await interaction.response.send_message(f"🗑️ Removed help option matching `{identifier}`.", ephemeral=True)

    @app_commands.command(name="edit_help", description="Edit the label of a help option")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(identifier="Number or keyword", new_label="New label text")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def edit_help(self, interaction: Interaction, identifier: str, new_label: str):
        settings = get_guild_settings(interaction.guild.id)
        updated = False
        for o in settings["help_options"]:
            if o["number"] == identifier or o["keyword"].lower() == identifier.lower():
                o["label"] = new_label
                updated = True
                break

        if not updated:
            return await interaction.response.send_message("❌ No matching option found.", ephemeral=True)

        set_guild_setting(interaction.guild.id, "help_options", settings["help_options"])
        await interaction.response.send_message(f"✏️ Updated help label to: {new_label}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ConfigHelp(bot))
