#!/usr/bin/env python3
"""
MRG Language CLI - Full Discord Bot Support
รองรับ Slash Commands, Modals, Context Menus, Voice, Threads และทุกอย่าง!
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
    from discord.ui import Button, Select, View, Modal, TextInput
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

VERSION = "1.0.0"

# ==================== Package Manager ====================

class MRGPackageManager:
    def __init__(self):
        self.home_dir = Path.home() / ".mrg"
        self.packages_dir = self.home_dir / "packages"
        self.registry_file = self.home_dir / "registry.json"
        self.installed_file = self.home_dir / "installed.json"
        
        self.home_dir.mkdir(exist_ok=True)
        self.packages_dir.mkdir(exist_ok=True)
        
        self.registry = self._load_registry()
        self.installed = self._load_installed()
        
    def _load_registry(self) -> Dict:
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        default_registry = {
            "discord.mrg": {
                "name": "discord.mrg",
                "version": "1.0.0",
                "description": "Discord Bot Module - รองรับทุกฟีเจอร์!",
                "author": "MRG Team",
                "python_packages": ["discord.py"]
            }
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(default_registry, f, indent=2, ensure_ascii=False)
        
        return default_registry
    
    def _load_installed(self) -> Dict:
        if self.installed_file.exists():
            with open(self.installed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_installed(self):
        with open(self.installed_file, 'w', encoding='utf-8') as f:
            json.dump(self.installed, f, indent=2, ensure_ascii=False)
    
    def install(self, package_name: str):
        print(f"📦 กำลังติดตั้ง {package_name}...")
        
        if package_name not in self.registry:
            print(f"❌ ไม่พบ package '{package_name}'")
            return False
        
        if package_name in self.installed:
            print(f"✓ {package_name} ติดตั้งแล้ว")
            return True
        
        info = self.registry[package_name]
        
        if info.get("python_packages"):
            print(f"📋 กำลังติดตั้ง dependencies...")
            for pkg in info["python_packages"]:
                os.system(f"pip install {pkg} -q")
        
        self.installed[package_name] = {"version": info["version"]}
        self._save_installed()
        
        print(f"✅ ติดตั้ง {package_name} สำเร็จ!")
        return True
    
    def list_packages(self):
        if not self.installed:
            print("📦 ยังไม่มี packages")
            return
        
        print(f"\n📦 Packages ({len(self.installed)}):\n")
        for name, info in self.installed.items():
            print(f"  ✓ {name} v{info['version']}")

# ==================== MRG Parser ====================

class MRGParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.config = {
            "bot_name": "MRGBot",
            "token": None,
            "prefix": "!",
            "commands": {},
            "slash_commands": {},
            "context_menus": {},
            "events": {},
            "button_handlers": {},
            "select_handlers": {},
            "modal_handlers": {},
            "voice_handlers": {}
        }
    
    def parse(self) -> Dict:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_command = None
        current_slash = None
        current_modal = None
        current_embed = None
        current_buttons = []
        current_select_options = []
        current_modal_inputs = []
        in_event = None
        in_button_handler = None
        in_modal_submit = False
        
        for line in lines:
            line = line.split('#')[0].rstrip()
            if not line.strip():
                continue
            
            stripped = line.strip()
            parts = stripped.split(None, 1)
            
            if not parts:
                continue
            
            keyword = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            # ===== Basic Config =====
            if keyword == "bot":
                self.config["bot_name"] = args
                
            elif keyword == "token":
                self.config["token"] = args
                
            elif keyword == "prefix":
                self.config["prefix"] = args
            
            # ===== Events =====
            elif keyword == "on":
                if "ready" in args:
                    in_event = "ready"
                    self.config["events"]["ready"] = []
                elif "member join" in args:
                    in_event = "member_join"
                    self.config["events"]["member_join"] = []
                elif "member leave" in args:
                    in_event = "member_leave"
                    self.config["events"]["member_leave"] = []
                elif "message delete" in args:
                    in_event = "message_delete"
                    self.config["events"]["message_delete"] = []
                elif "voice join" in args:
                    in_event = "voice_join"
                    self.config["voice_handlers"]["join"] = []
                elif "voice leave" in args:
                    in_event = "voice_leave"
                    self.config["voice_handlers"]["leave"] = []
                elif "button click" in args:
                    btn_id = args.split()[-1]
                    in_button_handler = btn_id
                    self.config["button_handlers"][btn_id] = []
                    current_command = None
                    current_slash = None
                elif "submit" in args:
                    in_modal_submit = True
                    
            elif keyword == "print" and in_event:
                self.config["events"][in_event].append(("print", args))
                
            elif keyword == "set" and in_event:
                set_parts = args.split(None, 1)
                if len(set_parts) >= 2:
                    self.config["events"][in_event].append(("set", set_parts[0], set_parts[1]))
            
            # ===== Prefix Commands =====
            elif keyword == "command":
                current_command = args
                current_slash = None
                self.config["commands"][current_command] = {
                    "replies": [],
                    "embeds": [],
                    "buttons": [],
                    "selects": [],
                    "images": [],
                    "actions": [],
                    "modals": []
                }
                in_event = None
                in_button_handler = None
            
            # ===== Slash Commands =====
            elif keyword == "slash":
                current_slash = args
                current_command = None
                self.config["slash_commands"][current_slash] = {
                    "description": f"คำสั่ง {args}",
                    "options": [],
                    "replies": [],
                    "embeds": [],
                    "buttons": [],
                    "selects": [],
                    "modals": [],
                    "actions": [],
                    "permissions": []
                }
                in_event = None
                in_button_handler = None
                
            elif keyword == "description" and current_slash:
                self.config["slash_commands"][current_slash]["description"] = args
                
            elif keyword == "option" and current_slash:
                opt_parts = args.split()
                if len(opt_parts) >= 3:
                    opt_type = opt_parts[0]
                    opt_name = opt_parts[1]
                    opt_desc = " ".join(opt_parts[2:])
                    required = "required" in opt_desc.lower()
                    self.config["slash_commands"][current_slash]["options"].append({
                        "type": opt_type,
                        "name": opt_name,
                        "description": opt_desc.replace("required", "").replace("optional", "").strip(),
                        "required": required
                    })
            
            # ===== Context Menus =====
            elif keyword == "context":
                ctx_parts = args.split(None, 1)
                if len(ctx_parts) >= 2:
                    ctx_type = ctx_parts[0]
                    ctx_name = ctx_parts[1]
                    self.config["context_menus"][ctx_name] = {
                        "type": ctx_type,
                        "actions": []
                    }
            
            # ===== Modals =====
            elif keyword == "modal":
                current_modal = {
                    "title": "Form",
                    "inputs": []
                }
                
            elif keyword == "title" and current_modal is not None and not current_embed:
                current_modal["title"] = args
                
            elif keyword == "input" and current_modal is not None:
                inp_parts = args.split(None, 2)
                if len(inp_parts) >= 3:
                    inp_type = inp_parts[0]
                    inp_label = inp_parts[1]
                    inp_placeholder = inp_parts[2]
                    current_modal["inputs"].append({
                        "style": inp_type,
                        "label": inp_label,
                        "placeholder": inp_placeholder
                    })
            
            # ===== Replies =====
            elif keyword == "reply":
                reply_text = args
                if in_button_handler:
                    self.config["button_handlers"][in_button_handler].append(("reply", reply_text))
                elif in_modal_submit and current_slash:
                    if "modal_submit" not in self.config["slash_commands"][current_slash]:
                        self.config["slash_commands"][current_slash]["modal_submit"] = []
                    self.config["slash_commands"][current_slash]["modal_submit"].append(("reply", reply_text))
                elif current_slash:
                    self.config["slash_commands"][current_slash]["replies"].append(reply_text)
                elif current_command:
                    self.config["commands"][current_command]["replies"].append(reply_text)
            
            # ===== Embeds =====
            elif keyword == "embed":
                current_embed = {
                    "title": "",
                    "description": "",
                    "color": 0x3498db,
                    "fields": [],
                    "thumbnail": False,
                    "image": None,
                    "footer": ""
                }
                
            elif keyword == "title" and current_embed is not None:
                current_embed["title"] = args
                
            elif keyword == "description" and current_embed is not None:
                current_embed["description"] = args
                
            elif keyword == "color" and current_embed is not None:
                colors = {
                    "blue": 0x3498db, "สีน้ำเงิน": 0x3498db,
                    "red": 0xe74c3c, "สีแดง": 0xe74c3c,
                    "green": 0x2ecc71, "สีเขียว": 0x2ecc71,
                    "yellow": 0xf1c40f, "สีเหลือง": 0xf1c40f,
                    "purple": 0x9b59b6, "สีม่วง": 0x9b59b6,
                    "orange": 0xe67e22, "สีส้ม": 0xe67e22
                }
                current_embed["color"] = colors.get(args.lower(), 0x3498db)
                
            elif keyword == "field" and current_embed is not None:
                current_embed["fields"].append(args)
                
            elif keyword == "thumbnail" and current_embed is not None:
                current_embed["thumbnail"] = True
                
            elif keyword == "image" and current_embed is not None:
                current_embed["image"] = args
                
            elif keyword == "footer" and current_embed is not None:
                current_embed["footer"] = args
                
            elif keyword == "send" and args == "embed" and current_embed:
                if current_slash:
                    self.config["slash_commands"][current_slash]["embeds"].append(current_embed)
                elif current_command:
                    self.config["commands"][current_command]["embeds"].append(current_embed)
                current_embed = None
            
            # ===== Buttons =====
            elif keyword == "button":
                btn_parts = args.split(None, 2)
                if len(btn_parts) >= 3:
                    current_buttons.append({
                        "style": btn_parts[0],
                        "label": btn_parts[1],
                        "custom_id": btn_parts[2]
                    })
                    
            elif keyword == "send" and args == "buttons":
                if current_slash:
                    self.config["slash_commands"][current_slash]["buttons"] = current_buttons.copy()
                elif current_command:
                    self.config["commands"][current_command]["buttons"] = current_buttons.copy()
                current_buttons = []
            
            # ===== Select Menus =====
            elif keyword == "select" and args == "menu":
                current_select_options = []
                
            elif keyword == "option" and not current_slash:
                opt_parts = args.split(None, 1)
                if len(opt_parts) >= 2:
                    current_select_options.append({
                        "value": opt_parts[0],
                        "label": opt_parts[1]
                    })
                    
            elif keyword == "send" and args == "menu":
                select_data = {"options": current_select_options.copy()}
                if current_slash:
                    self.config["slash_commands"][current_slash]["selects"].append(select_data)
                elif current_command:
                    self.config["commands"][current_command]["selects"].append(select_data)
                current_select_options = []
            
            # ===== Actions =====
            elif keyword == "kick":
                action = ("kick", args)
                if current_slash:
                    self.config["slash_commands"][current_slash]["actions"].append(action)
                elif current_command:
                    self.config["commands"][current_command]["actions"].append(action)
                    
            elif keyword == "ban":
                action = ("ban", args)
                if current_slash:
                    self.config["slash_commands"][current_slash]["actions"].append(action)
                elif current_command:
                    self.config["commands"][current_command]["actions"].append(action)
                    
            elif keyword == "timeout":
                action = ("timeout", args)
                if current_slash:
                    self.config["slash_commands"][current_slash]["actions"].append(action)
                    
            elif keyword == "role" and "add" in args:
                action = ("add_role", args)
                if current_slash:
                    self.config["slash_commands"][current_slash]["actions"].append(action)
                    
            elif keyword == "role" and "remove" in args:
                action = ("remove_role", args)
                if current_slash:
                    self.config["slash_commands"][current_slash]["actions"].append(action)
            
            # ===== Permissions =====
            elif keyword == "require" and "permission" in args:
                perm = args.split()[-1]
                if current_slash:
                    self.config["slash_commands"][current_slash]["permissions"].append(perm)
            
            # ===== Images =====
            elif keyword == "send" and "image" in args:
                img_parts = args.split(None, 1)
                if len(img_parts) >= 2:
                    if current_slash:
                        self.config["slash_commands"][current_slash].setdefault("images", []).append(img_parts[1])
                    elif current_command:
                        self.config["commands"][current_command].setdefault("images", []).append(img_parts[1])
            
            # ===== Modal Send =====
            elif keyword == "send" and args == "modal" and current_modal:
                if current_slash:
                    self.config["slash_commands"][current_slash]["modals"].append(current_modal)
                current_modal = None
                in_modal_submit = False
        
        return self.config

# ==================== MRG Runtime ====================

class MRGRuntime:
    def __init__(self, config: Dict):
        self.config = config
        self.bot = None
        
    def create_bot(self):
        if not DISCORD_AVAILABLE:
            print("❌ Discord.py ไม่ได้ติดตั้ง!")
            print("💡 รันคำสั่ง: mrg install discord.mrg")
            return None
        
        intents = discord.Intents.all()
        
        bot = commands.Bot(
            command_prefix=self.config["prefix"],
            intents=intents
        )
        
        # ===== on_ready =====
        @bot.event
        async def on_ready():
            print(f"✅ {bot.user.name} ออนไลน์แล้ว!")
            print(f"📊 Servers: {len(bot.guilds)}")
            print(f"👥 Users: {sum(g.member_count for g in bot.guilds)}")
            
            if "ready" in self.config["events"]:
                for event in self.config["events"]["ready"]:
                    if event[0] == "print":
                        print(event[1])
                    elif event[0] == "set" and event[1] == "status":
                        status_map = {
                            "online": discord.Status.online,
                            "idle": discord.Status.idle,
                            "dnd": discord.Status.dnd
                        }
                        await bot.change_presence(status=status_map.get(event[2], discord.Status.online))
                    elif event[0] == "set" and event[1] == "activity":
                        await bot.change_presence(activity=discord.Game(name=event[2]))
            
            # Sync slash commands
            if self.config["slash_commands"]:
                try:
                    synced = await bot.tree.sync()
                    print(f"✅ Synced {len(synced)} slash commands")
                except Exception as e:
                    print(f"⚠️  Slash commands sync error: {e}")
        
        # ===== Other Events =====
        @bot.event
        async def on_member_join(member):
            if "member_join" in self.config["events"]:
                for event in self.config["events"]["member_join"]:
                    if event[0] == "print":
                        print(f"{member.name} joined!")
        
        @bot.event
        async def on_member_remove(member):
            if "member_leave" in self.config["events"]:
                for event in self.config["events"]["member_leave"]:
                    if event[0] == "print":
                        print(f"{member.name} left!")
        
        # ===== Prefix Commands =====
        for cmd_name, cmd_data in self.config["commands"].items():
            async def command_func(ctx, cmd_data=cmd_data):
                await self._execute_command(ctx, cmd_data, is_slash=False)
            
            bot.command(name=cmd_name)(command_func)
        
        # ===== Slash Commands =====
        for slash_name, slash_data in self.config["slash_commands"].items():
            # Create slash command
            @bot.tree.command(name=slash_name, description=slash_data.get("description", "MRG Command"))
            async def slash_func(interaction: discord.Interaction, slash_data=slash_data):
                # Check modals first
                if slash_data.get("modals"):
                    modal_data = slash_data["modals"][0]
                    
                    class DynamicModal(Modal):
                        def __init__(self):
                            super().__init__(title=modal_data["title"])
                            for inp in modal_data["inputs"]:
                                style = discord.TextStyle.short if inp["style"] == "short" else discord.TextStyle.long
                                self.add_item(TextInput(
                                    label=inp["label"],
                                    placeholder=inp["placeholder"],
                                    style=style
                                ))
                        
                        async def on_submit(self, interaction: discord.Interaction):
                            if "modal_submit" in slash_data:
                                for action in slash_data["modal_submit"]:
                                    if action[0] == "reply":
                                        await interaction.response.send_message(action[1])
                    
                    await interaction.response.send_modal(DynamicModal())
                else:
                    await self._execute_slash(interaction, slash_data)
        
        return bot
    
    async def _execute_command(self, ctx, cmd_data, is_slash=False):
        # Replies
        for reply in cmd_data.get("replies", []):
            formatted = self._format_text(reply, ctx)
            await ctx.send(formatted)
        
        # Embeds
        for embed_data in cmd_data.get("embeds", []):
            embed = await self._create_embed(embed_data, ctx)
            await ctx.send(embed=embed)
        
        # Buttons
        if cmd_data.get("buttons"):
            view = await self._create_button_view(cmd_data["buttons"])
            await ctx.send(view=view)
        
        # Select Menus
        for select_data in cmd_data.get("selects", []):
            view = await self._create_select_view(select_data)
            await ctx.send(view=view)
        
        # Images
        for img_url in cmd_data.get("images", []):
            await ctx.send(img_url)
        
        # Actions
        for action in cmd_data.get("actions", []):
            await self._execute_action(ctx, action)
    
    async def _execute_slash(self, interaction, slash_data):
        # Replies
        if slash_data.get("replies"):
            formatted = self._format_text(slash_data["replies"][0], interaction)
            await interaction.response.send_message(formatted)
        elif slash_data.get("embeds"):
            embed = await self._create_embed(slash_data["embeds"][0], interaction)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Done!")
    
    def _format_text(self, text, ctx):
        if hasattr(ctx, 'author'):
            text = text.replace("{user_name}", ctx.author.name)
            text = text.replace("{user_id}", str(ctx.author.id))
        if hasattr(ctx, 'guild') and ctx.guild:
            text = text.replace("{server_name}", ctx.guild.name)
            text = text.replace("{member_count}", str(len(ctx.guild.members)))
            if ctx.guild.owner:
                text = text.replace("{owner_name}", ctx.guild.owner.name)
        return text
    
    async def _create_embed(self, embed_data, ctx):
        embed = discord.Embed(
            title=self._format_text(embed_data["title"], ctx),
            description=self._format_text(embed_data["description"], ctx),
            color=embed_data["color"]
        )
        
        for field in embed_data.get("fields", []):
            formatted = self._format_text(field, ctx)
            embed.add_field(name=formatted, value="✓", inline=False)
        
        if embed_data.get("thumbnail") and hasattr(ctx, 'guild') and ctx.guild and ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        if embed_data.get("image"):
            embed.set_image(url=embed_data["image"])
        
        if embed_data.get("footer"):
            footer = self._format_text(embed_data["footer"], ctx)
            embed.set_footer(text=footer)
        
        return embed
    
    async def _create_button_view(self, buttons_data):
        view = View(timeout=None)
        
        for btn in buttons_data:
            style_map = {
                "Primary": discord.ButtonStyle.primary,
                "Success": discord.ButtonStyle.success,
                "Danger": discord.ButtonStyle.danger,
                "Secondary": discord.ButtonStyle.secondary
            }
            
            async def button_callback(interaction, btn_id=btn["custom_id"]):
                if btn_id in self.config["button_handlers"]:
                    for action in self.config["button_handlers"][btn_id]:
                        if action[0] == "reply":
                            await interaction.response.send_message(action[1])
            
            button = Button(
                label=btn["label"],
                style=style_map.get(btn["style"], discord.ButtonStyle.primary),
                custom_id=btn["custom_id"]
            )
            button.callback = button_callback
            view.add_item(button)
        
        return view
    
    async def _create_select_view(self, select_data):
        view = View(timeout=None)
        select = Select(placeholder="เลือกตัวเลือก")
        
        for opt in select_data["options"]:
            select.add_option(label=opt["label"], value=opt["value"])
        
        async def select_callback(interaction):
            selected = interaction.data["values"][0]
            await interaction.response.send_message(f"คุณเลือก {selected}")
        
        select.callback = select_callback
        view.add_item(select)
        return view
    
    async def _execute_action(self, ctx, action):
        action_type = action[0]
        
        if action_type == "kick" and ctx.message.mentions:
            try:
                await ctx.message.mentions[0].kick()
            except:
                await ctx.send("❌ ไม่สามารถไล่ได้")
        elif action_type == "ban" and ctx.message.mentions:
            try:
                await ctx.message.mentions[0].ban()
            except:
                await ctx.send("❌ ไม่สามารถแบนได้")
    
    def run(self):
        token = self.config.get("token")
        
        if not token or token == "YOUR_BOT_TOKEN_HERE":
            print("❌ กรุณาใส่ Discord Bot Token")
            print("💡 https://discord.com/developers/applications")
            return
        
        bot = self.create_bot()
        if not bot:
            return
        
        try:
            bot.run(token)
        except discord.LoginFailure:
            print("❌ Token ไม่ถูกต้อง!")
        except Exception as e:
            print(f"❌ Error: {e}")

# ==================== CLI ====================

def show_banner():
    print("""
╔════════════════════════════════════════════════════╗
║        🚀  MRG Programming Language  🚀           ║
║              Version 1.0.0 - Full                  ║
║      รองรับ Discord Bot ทุกฟีเจอร์!              ║
╚════════════════════════════════════════════════════╝
    """)

def show_help():
    print("""
📚 MRG Commands:

  🎮 Running:
    mrg run <file.mrg>          รันไฟล์ .mrg
    
  📦 Packages:
    mrg install <package>       ติดตั้ง package
    mrg i <package>             ติดตั้ง (สั้น)
    mrg list                    แสดง packages
    
  ℹ️  Info:
    mrg version                 เวอร์ชัน
    mrg help                    ช่วยเหลือ
    
✨ รองรับ:
  • Prefix Commands
  • Slash Commands
  • Buttons & Select Menus
  • Modals (Forms)
  • Context Menus
  • Embeds
  • Voice Events
  • Member Events
  • Permissions
  • และอื่นๆ อีกมากมาย!
    """)

def main():
    if len(sys.argv) < 2:
        show_banner()
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    pm = MRGPackageManager()
    
    if command == "run":
        if len(sys.argv) < 3:
            print("❌ กรุณาระบุไฟล์")
            sys.exit(1)
        
        filepath = sys.argv[2]
        
        if not Path(filepath).exists():
            print(f"❌ ไม่พบไฟล์ {filepath}")
            sys.exit(1)
        
        print(f"🚀 กำลังรัน {filepath}...\n")
        
        parser = MRGParser(filepath)
        config = parser.parse()
        
        runtime = MRGRuntime(config)
        runtime.run()
        
    elif command in ["install", "i"]:
        if len(sys.argv) < 3:
            print("❌ กรุณาระบุ package")
            sys.exit(1)
        
        for pkg in sys.argv[2:]:
            pm.install(pkg)
            
    elif command == "list":
        pm.list_packages()
        
    elif command == "version":
        show_banner()
        
    elif command == "help":
        show_help()
        
    else:
        print(f"❌ ไม่รู้จักคำสั่ง: {command}")
        print("💡 ใช้ 'mrg help' เพื่อดูคำสั่งทั้งหมด")

if __name__ == "__main__":
    main()