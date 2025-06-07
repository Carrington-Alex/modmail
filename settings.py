# settings.py
import sqlite3
import json

DB_PATH = "settings.db"

# === INITIALIZE DB ===
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id TEXT PRIMARY KEY,
                prefix TEXT DEFAULT '.',
                mod_role_ids TEXT,
                log_channel_id TEXT,
                ticket_category_id TEXT,
                help_intro TEXT,
                help_options TEXT
            )
        ''')
        conn.commit()

# === LOAD SETTINGS ===
def get_guild_settings(guild_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (str(guild_id),))
        row = c.fetchone()

        if row is None:
            default = {
                "prefix": ".",
                "mod_role_ids": [],
                "log_channel_id": None,
                "ticket_category_id": None,
                "help_intro": "What do you need help with?",
                "help_options": [
                    {"number": "1", "keyword": "verify", "label": "Verification Help"},
                    {"number": "2", "keyword": "dm ad", "label": "DM Advertisement Report"},
                    {"number": "3", "keyword": "report", "label": "User Report"},
                    {"number": "4", "keyword": "appeal", "label": "Mute/Ban Appeal"},
                    {"number": "5", "keyword": "other", "label": "Other Issue"},
                ]
            }

            for key, value in default.items():
                set_guild_setting(guild_id, key, value)

            return default

        keys = [desc[0] for desc in c.description]
        result = dict(zip(keys, row))
        if result["mod_role_ids"]:
            result["mod_role_ids"] = json.loads(result["mod_role_ids"])
        if result["help_options"]:
            result["help_options"] = json.loads(result["help_options"])
        return result

# === SAVE SETTINGS ===
def set_guild_setting(guild_id, key, value):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM guild_settings WHERE guild_id = ?", (str(guild_id),))
        exists = c.fetchone() is not None

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        if exists:
            c.execute(f"UPDATE guild_settings SET {key} = ? WHERE guild_id = ?", (value, str(guild_id)))
        else:
            default_values = {
                "prefix": ".",
                "mod_role_ids": json.dumps([]),
                "log_channel_id": None,
                "ticket_category_id": None,
                "help_intro": "What do you need help with?",
                "help_options": json.dumps([])
            }
            default_values[key] = value
            columns = ", ".join(["guild_id"] + list(default_values.keys()))
            placeholders = ", ".join(["?"] * (len(default_values) + 1))
            values = [str(guild_id)] + list(default_values.values())
            c.execute(f"INSERT INTO guild_settings ({columns}) VALUES ({placeholders})", values)

        conn.commit()

# === DYNAMIC TYPE MAP ===
def build_type_map(help_options):
    result = {}
    for opt in help_options:
        label = opt["label"]
        result[opt["number"]] = label
        result[opt["keyword"].lower()] = label
    return result
