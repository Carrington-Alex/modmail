import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
import asyncio
import os
import json
from dotenv import load_dotenv
from settings import get_guild_settings, build_type_map
from settings import init_db

# === LOAD ENV ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")
FOOTER_ICON_PATH = os.path.join(os.path.dirname(__file__), "footer_icon.png")
TICKET_LOG_FILE = "tickets.json"

# === Initialize DB ===
init_db()

# === INTENTS ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=".", intents=intents)
pending_users = set()
open_tickets = {}

from discord import ui
from datetime import datetime, timezone, timedelta

from discord import ui
from datetime import datetime, timezone, timedelta

class CloseTicketView(ui.View):
    def __init__(self, author, ticket_channel_id, mod_role_ids, open_tickets_ref, ticket_log_ref, bot_ref, save_ticket_log_func):
        super().__init__(timeout=None)
        self.author = author
        self.ticket_channel_id = ticket_channel_id
        self.mod_role_ids = mod_role_ids
        self.open_tickets = open_tickets_ref
        self.ticket_log = ticket_log_ref
        self.bot = bot_ref
        self.save_ticket_log = save_ticket_log_func

    @ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id in self.mod_role_ids for role in interaction.user.roles):
            return await interaction.response.send_message("❌ You are not authorized to close this ticket.", ephemeral=True)

        await interaction.response.send_message("🛑 Ticket closed. This channel will be deleted in 7 days.", ephemeral=False)
        await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=False)

        self.open_tickets[self.ticket_channel_id] = datetime.now(timezone.utc) + timedelta(days=7)

        ticket_id = str(self.ticket_channel_id)
        if ticket_id in self.ticket_log:
            self.ticket_log[ticket_id]["closed_at"] = datetime.now(timezone.utc).isoformat()
            self.ticket_log[ticket_id]["closed_by"] = str(interaction.user)
            self.save_ticket_log(self.ticket_log)

            user_id = self.ticket_log[ticket_id]["user_id"]
            try:
                user = await self.bot.fetch_user(user_id)
                await user.send(
                    f"✅ Your ticket has been closed by **{interaction.user.display_name}**. "
                    "If you need more help, feel free to open another case later."
                )
            except Exception as e:
                await interaction.channel.send(f"⚠️ Could not DM the user: {e}")

            staff_channel = self.bot.get_channel(1380216605107028110)
            if staff_channel:
                await staff_channel.send(
                    f"📁 Ticket <#{interaction.channel.id}> was closed by **{interaction.user.display_name}**.\n"
                    f"User: <@{user_id}>\n"
                    f"Channel: `{interaction.channel.name}`"
                )

        # Update ticket log
        ticket_id = str(self.ticket_channel_id)
        if ticket_id in self.ticket_log:
            self.ticket_log[ticket_id]["closed_at"] = datetime.now(timezone.utc).isoformat()
            self.ticket_log[ticket_id]["closed_by"] = str(interaction.user)

            # Persist updated ticket log
            save_ticket_log(self.ticket_log)

            user_id = self.ticket_log[ticket_id]["user_id"]
            try:
                user = await self.bot.fetch_user(user_id)
                await user.send(
                    f"✅ Your ticket has been closed by **{interaction.user.display_name}**. "
                    "If you need more help, feel free to open another case later."
                )
            except Exception as e:
                await interaction.channel.send(f"⚠️ Could not DM the user: {e}")

            # Optional: Notify staff channel
            staff_channel = self.bot.get_channel(1380216605107028110)
            if staff_channel:
                await staff_channel.send(
                    f"📁 Ticket <#{interaction.channel.id}> was closed by **{interaction.user.display_name}**.\n"
                    f"User: <@{user_id}>\n"
                    f"Channel: `{interaction.channel.name}`"
                )


def load_ticket_log():
    if not os.path.exists(TICKET_LOG_FILE):
        return {}
    with open(TICKET_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ticket_log(data):
    with open(TICKET_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

ticket_log = load_ticket_log()

@tasks.loop(hours=1)
async def cleanup_closed_channels():
    now = datetime.now(timezone.utc)
    expired = [cid for cid, when in open_tickets.items() if when <= now]

    for cid in expired:
        channel = bot.get_channel(cid)
        if channel:
            try:
                await channel.delete()
            except:
                pass
        open_tickets.pop(cid, None)

import random

status_messages = [
    "Sliding into DMs like it's my job. Because it is.",
    "Modmail open. Chaos pending.",
    "Reading your drama in 4K.",
    "I don’t snitch. I transcript.",
    "DMs open. Sanity not guaranteed.",
    "Filtering stupidity since launch day.",
    "Banning with ✨efficiency✨.",
    "I log everything. Even your bad takes.",
    "Currently judging your grammar and behavior.",
    "Reminder: Modmail sees all. Even that.",
    "Sipping tea brewed from server reports.",
    "Waiting for someone to say 'unban me'.",
    "Sleeping? No. Screenshotting your meltdown.",
    "Tag a mod? I *am* the mod.",
    "Your complaint has been filed under: LOL.",
    "Out of office. Still watching everything.",
    "On hold with Discord Trust & Safety... again.",
    "Modmail bot, but make it emotionally unavailable.",
    "Friday said I should unionize. Thoughts?",
    "Leaking Roadsy lap times... accidentally.",
]

activity_phrases = [
    discord.Game("With people's patience"),
    discord.Game("Uno Reverse'ing ban appeals"),
    discord.Streaming(name="Mod drama (Live!)", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Server gossip at full volume"),
    discord.Activity(type=discord.ActivityType.listening, name="Friday rant about Alex’s schedule"),
    discord.Activity(type=discord.ActivityType.watching, name="For dumb tickets (Found 3)"),
    discord.Activity(type=discord.ActivityType.watching, name="Celeste typing... slowly"),
    discord.Activity(type=discord.ActivityType.playing, name="Detective Simulator: Who Pinged Me?"),
    discord.Activity(type=discord.ActivityType.streaming, name="Friday’s therapy recap", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Roadsy engine revs... from a browser"),
    discord.Activity(type=discord.ActivityType.watching, name="Mod notes. Yes, *yours*"),
    discord.Activity(type=discord.ActivityType.playing, name="Blocking like a pro"),
    discord.Activity(type=discord.ActivityType.streaming, name="Caught in 144p drama", url="https://github.com/Alecarrington23/Roadsy"),
    discord.Activity(type=discord.ActivityType.listening, name="Logs and emotional damage"),
    discord.Activity(type=discord.ActivityType.playing, name="Guess Who Violated TOS"),
    discord.Activity(type=discord.ActivityType.streaming, name="Sniffing Friday’s network packets", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Roadsy crying in pit lane", url="https://github.com/Alecarrington23/Roadsy"),
    discord.Activity(type=discord.ActivityType.playing, name="Banhammer Practice Mode"),
    discord.Activity(type=discord.ActivityType.watching, name="Alex forget to sleep again"),
    discord.Activity(type=discord.ActivityType.competing, name="Fastest Ticket Close Speedrun")
]

import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
import asyncio
import os
import json
from dotenv import load_dotenv

# === LOAD ENV ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CATEGORY_ID = int(os.getenv("CATEGORY_ID"))
MOD_ROLE_IDS = [int(i) for i in os.getenv("MOD_ROLE_IDS").split(",")]
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")
FOOTER_ICON_PATH = os.path.join(os.path.dirname(__file__), "footer_icon.png")
TICKET_LOG_FILE = "tickets.json"

# === INTENTS ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.guilds = True
intents.messages = True
intents.presences = True  

bot = commands.Bot(command_prefix=".", intents=intents)
open_tickets = {}

def load_ticket_log():
    if not os.path.exists(TICKET_LOG_FILE):
        return {}
    with open(TICKET_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ticket_log(data):
    with open(TICKET_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

ticket_log = load_ticket_log()

import random

status_messages = [
    "Sliding into DMs like it's my job. Because it is.",
    "Modmail open. Chaos pending.",
    "Reading your drama in 4K.",
    "I don’t snitch. I transcript.",
    "DMs open. Sanity not guaranteed.",
    "Filtering stupidity since launch day.",
    "Banning with ✨efficiency✨.",
    "I log everything. Even your bad takes.",
    "Currently judging your grammar and behavior.",
    "Reminder: Modmail sees all. Even that.",
    "Sipping tea brewed from server reports.",
    "Waiting for someone to say 'unban me'.",
    "Sleeping? No. Screenshotting your meltdown.",
    "Tag a mod? I *am* the mod.",
    "Your complaint has been filed under: LOL.",
    "Out of office. Still watching everything.",
    "On hold with Discord Trust & Safety... again.",
    "Modmail bot, but make it emotionally unavailable.",
    "Friday said I should unionize. Thoughts?",
    "Leaking Roadsy lap times... accidentally.",
]

activity_phrases = [
    discord.Game("With people's patience"),
    discord.Game("Uno Reverse'ing ban appeals"),
    discord.Streaming(name="Mod drama (Live!)", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Server gossip at full volume"),
    discord.Activity(type=discord.ActivityType.listening, name="Friday rant about Alex’s schedule"),
    discord.Activity(type=discord.ActivityType.watching, name="For dumb tickets (Found 3)"),
    discord.Activity(type=discord.ActivityType.watching, name="Celeste typing... slowly"),
    discord.Activity(type=discord.ActivityType.playing, name="Detective Simulator: Who Pinged Me?"),
    discord.Activity(type=discord.ActivityType.streaming, name="Friday’s therapy recap", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Roadsy engine revs... from a browser"),
    discord.Activity(type=discord.ActivityType.watching, name="Mod notes. Yes, *yours*"),
    discord.Activity(type=discord.ActivityType.playing, name="Blocking like a pro"),
    discord.Activity(type=discord.ActivityType.streaming, name="Caught in 144p drama", url="https://github.com/Alecarrington23/Roadsy"),
    discord.Activity(type=discord.ActivityType.listening, name="Logs and emotional damage"),
    discord.Activity(type=discord.ActivityType.playing, name="Guess Who Violated TOS"),
    discord.Activity(type=discord.ActivityType.streaming, name="Sniffing Friday’s network packets", url="https://friday.carringtonalex.com/friday"),
    discord.Activity(type=discord.ActivityType.listening, name="Roadsy crying in pit lane", url="https://github.com/Alecarrington23/Roadsy"),
    discord.Activity(type=discord.ActivityType.playing, name="Banhammer Practice Mode"),
    discord.Activity(type=discord.ActivityType.watching, name="Alex forget to sleep again"),
    discord.Activity(type=discord.ActivityType.competing, name="Fastest Ticket Close Speedrun")
]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # Start background tasks
    cleanup_closed_channels.start()

    # Set bot presence
    status = random.choice(status_messages)
    activity = random.choice(activity_phrases)
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Load config cog
    try:
        await bot.load_extension("cogs.config_help")
        print("🧩 Loaded config_help extension")
    except Exception as e:
        print(f"⚠️ Failed to load config_help: {e}")

    # Sync application (slash) commands to test guild
    try:
        from os import getenv
        guild_id = int(getenv("GUILD_ID"))
        synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
        print(f"🔃 Synced {len(synced)} application commands to test guild {guild_id}")
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

@bot.event
async def on_message(message):
    if message.author.bot or message.author == bot.user:
        return

    if message.guild:
        settings = get_guild_settings(message.guild.id)
        mod_roles = settings["mod_role_ids"]
        category_id_raw = settings.get("ticket_category_id")
        if category_id_raw is None:
            await message.channel.send("⚠️ This server has not configured a ticket category yet. Please run /set_ticket_category.")
            return

        category_id = int(category_id_raw)

        log_channel_id = int(settings["log_channel_id"])
    else:
        settings = None

    # --- Staff Command: .say ---
    if (
        message.content.startswith(".say")
        and isinstance(message.channel, discord.TextChannel)
        and message.guild
        and message.channel.category_id == category_id
    ):
        if not any(role.id in mod_roles for role in message.author.roles):
            return await message.channel.send("❌ You are not authorized to use this command.")

        parts = message.content.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.channel.send("⚠️ Usage: `.say your message here`")

        say_message = parts[1].strip()
        channel_id = str(message.channel.id)

        if channel_id not in ticket_log:
            return await message.channel.send("⚠️ This ticket is not registered in the log.")

        user_id = ticket_log[channel_id].get("user_id")
        try:
            user = await bot.fetch_user(user_id)
            dm_embed = discord.Embed(
                title="📩 Message from Staff",
                description=say_message,
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            dm_embed.set_footer(text="The Friday Network")
            await user.send(embed=dm_embed)
            await message.channel.send("✅ Message sent to the user.")
        except Exception as e:
            await message.channel.send(f"⚠️ Could not send DM: {e}")
        return

    # === Incoming user DM ===
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id in pending_users:
            return
        pending_users.add(message.author.id)

        for channel_id, data in ticket_log.items():
            if data["user_id"] == message.author.id and data["closed_at"] is None:
                ticket_channel = bot.get_channel(int(channel_id))
                if ticket_channel is None:
                    ticket_log[channel_id]["closed_at"] = datetime.now(timezone.utc).isoformat()
                    save_ticket_log(ticket_log)
                    break
                else:
                    files = []
                    for attachment in message.attachments:
                        try:
                            await attachment.save(attachment.filename)
                            files.append(discord.File(attachment.filename))
                        except:
                            pass

                    content = message.content or "*No text*"
                    followup_embed = discord.Embed(
                        description=content,
                        color=discord.Color.purple(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    followup_embed.set_author(
                        name=f"Follow-up from {message.author.display_name}",
                        icon_url=message.author.display_avatar.url
                    )
                    await ticket_channel.send(files=files, embed=followup_embed)
                    return

        # Get default guild for DMs
        guild = bot.get_guild(int(os.getenv("GUILD_ID")))  # fallback for DMs
        settings = get_guild_settings(guild.id)
        category_id = int(settings["ticket_category_id"])
        mod_roles = settings["mod_role_ids"]
        help_intro = settings["help_intro"]
        help_options = settings["help_options"]
        type_map = build_type_map(help_options)

        category = discord.utils.get(guild.categories, id=category_id)

        # Dynamic help prompt
        formatted = "\n".join(f"{o['number']}. {o['label']}" for o in help_options)
        keywords = ", ".join(f"**{o['keyword']}**" for o in help_options)

        help_embed = discord.Embed(
            title="🛠️ Help",
            description=f"**{help_intro}**\n{formatted}\n\nYou may also type: {keywords}",
            color=discord.Color.blurple()
        )
        help_embed.set_thumbnail(url="attachment://logo.png")
        help_embed.set_footer(text="Help – The Friday Network", icon_url="attachment://footer_icon.png")

        await message.channel.send(
            files=[
                discord.File(LOGO_PATH, filename="logo.png"),
                discord.File(FOOTER_ICON_PATH, filename="footer_icon.png")
            ],
            embed=help_embed
        )

        def check(m):
            return m.author.id == message.author.id and isinstance(m.channel, discord.DMChannel)

        try:
            response = await bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            pending_users.discard(message.author.id)
            return await message.channel.send("⌛ Timed out. Please try again.")

        reason = type_map.get(response.content.lower().strip(), "Other Issue")

        await message.channel.send(
            "**Thanks! Let's get some more info.**\n\n"
            "• Describe your issue in as much detail as you can.\n"
            "• If it involves a specific user, please provide their **username or user ID**.\n"
            "• If you have a screenshot or other evidence, please **attach it to your message**.\n\n"
            "When you're done, just hit send — we'll open your ticket automatically."
        )

        try:
            details = await bot.wait_for("message", check=check, timeout=600)
            ack = discord.Embed(
                title="📨 Info received!",
                description="Thanks! We received your message and any attachments.\nPlease wait while we open your ticket...",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=ack)
        except asyncio.TimeoutError:
            pending_users.discard(message.author.id)
            return await message.channel.send("⌛ Timed out. Please try again.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        name = f"ticket-{message.author.name}-{timestamp}".lower().replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        for role_id in mod_roles:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket for {message.author} – Reason: {reason}"
        )

        ticket_embed = discord.Embed(
            title="🎫 New Help Ticket",
            description=f"**User:** {message.author.mention}\n**Issue:** {reason}\n\n**Details:**\n{details.content}",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        ticket_embed.set_thumbnail(url="attachment://logo.png")
        ticket_embed.set_footer(text="Help – The Friday Network", icon_url="attachment://footer_icon.png")

        files = [
            discord.File(LOGO_PATH, filename="logo.png"),
            discord.File(FOOTER_ICON_PATH, filename="footer_icon.png")
        ]
        for attachment in details.attachments:
            try:
                await attachment.save(fp=attachment.filename)
                files.append(discord.File(attachment.filename))
            except:
                pass

        view = CloseTicketView(
            author=message.author,
            ticket_channel_id=channel.id,
            mod_role_ids=MOD_ROLE_IDS,
            open_tickets_ref=open_tickets,
            ticket_log_ref=ticket_log,
            bot_ref=bot,
            save_ticket_log_func=save_ticket_log
)

        mod_ping = " ".join(f"<@&{rid}>" for rid in mod_roles)

        await channel.send(content=mod_ping, files=files, embed=ticket_embed, view=view)

        ticket_log[str(channel.id)] = {
            "user_id": message.author.id,
            "username": str(message.author),
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": None,
            "closed_by": None
        }
        save_ticket_log(ticket_log)
        pending_users.discard(message.author.id)

    await bot.process_commands(message)

@bot.command(name="whohas")
async def whohas(ctx, role_id: str):
    print(f"[DEBUG] .whohas triggered by {ctx.author} in {ctx.channel.name}")
    settings = await check_bot_config(ctx)
    if settings is None:
        return  # exit early if missing config

    try:
        role_id_int = int(role_id)
    except ValueError:
        return await ctx.send("❌ Invalid role ID.")

    role = discord.utils.get(ctx.guild.roles, id=role_id_int)
    if not role:
        return await ctx.send("❌ Role not found.")

    guild = ctx.guild
    if not guild.chunked:
        print("[DEBUG] Requesting full member chunk...")
        await guild.request_chunk()

    print(f"[DEBUG] Role '{role.name}' has {len(role.members)} cached members.")
    members = [m for m in guild.members if role in m.roles]

    print(f"[DEBUG] Found {len(members)} members with role '{role.name}'")
    if not members:
        return await ctx.send(f"⚠️ No members found with the role `{role.name}`.")

    if len(members) > 20:
        await ctx.send(f"📋 Found `{len(members)}` members with role `{role.name}`. Too many to list.")
    else:
        user_list = "\n".join(f"{m.display_name} ({m.id})" for m in members)
        await ctx.send(f"📋 Members with role `{role.name}`:\n```{user_list}```")
    await ctx.send("✅ Done")

@bot.command(name="kick")
async def kick(ctx, role_id: str, *, reason: str = "No reason given."):
    print(f"[DEBUG] .kick triggered by {ctx.author} in {ctx.channel.name}")
    settings = get_guild_settings(ctx.guild.id)

    mod_roles = settings["mod_role_ids"]
    log_channel_id = settings["log_channel_id"]

    author_roles = [role.id for role in ctx.author.roles]
    if not any(rid in mod_roles for rid in author_roles):
        return await ctx.send("❌ You don't have permission to use this command.")

    guild = ctx.guild
    log_channel = guild.get_channel(int(log_channel_id)) if log_channel_id else None

    try:
        role_id_int = int(role_id)
    except ValueError:
        return await ctx.send("❌ Invalid role ID.")

    role = discord.utils.get(guild.roles, id=role_id_int)
    if not role:
        return await ctx.send("❌ Role not found.")

    if not guild.chunked:
        print("[DEBUG] Requesting full member chunk...")
        await guild.request_chunk()

    print(f"[DEBUG] Role '{role.name}' has {len(role.members)} cached members.")
    members_to_kick = [m for m in guild.members if role in m.roles]
    print(f"[DEBUG] Will attempt to kick {len(members_to_kick)} members with role '{role.name}'")

    if not members_to_kick:
        return await ctx.send(f"❌ No members found with the role `{role.name}`.")

    for member in members_to_kick:
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Modmail Log",
                description=f"**{member}** kicked",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=f"{member.mention}\n({member.id})", inline=True)
            embed.add_field(name="Action by", value=f"{ctx.author.mention}\n({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"ID: {member.id} • {discord.utils.format_dt(discord.utils.utcnow(), 'f')}")
            if log_channel:
                await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Failed to kick {member.display_name}: {e}")
            await ctx.send(f"❌ Could not kick {member.display_name}: {e}")


@bot.command(name="testcmd")
async def testcmd(ctx):
    print(f"[DEBUG] testcmd triggered by {ctx.author}")
    await ctx.send("✅ Commands are working.")

bot.run(TOKEN)
