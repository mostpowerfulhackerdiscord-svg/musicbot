import discord
from discord.ui import View, Button, Select
from discord import FFmpegPCMAudio
import os
import asyncio
from Handlers.debugger import log_event
from dotenv import load_dotenv
import sys

load_dotenv()
ADMIN_ID = int(os.getenv("USER_ID1", 0))
audio_folder = os.path.join("Modules", "sounds")
pfp_path = os.path.join("music.png")
ffmpeg_exe = os.path.join("ffmpeg", "ffmpeg-8.0.1-essentials_build", "bin", "ffmpeg.exe")

class BotHandler:
    selected_audio = None
    selected_channel = None
    audio_list = []
    voice_list = []
    loop_audio = False

    @staticmethod
    def register(bot_instance):
        @bot_instance.tree.command(name="gui", description="Open the audio GUI")
        async def gui(interaction: discord.Interaction):
            log_event(f"{interaction.user} ran /gui")
            BotHandler.update_audio_list()
            BotHandler.update_voice_list(interaction.guild)
            view = TOSView(bot_instance, interaction.guild)
            file = discord.File(pfp_path, filename=os.path.basename(pfp_path))
            embed = BotHandler.create_tos_embed()
            await interaction.response.send_message(embed=embed, view=view, file=file)

        async def check_admin(interaction: discord.Interaction):
            return interaction.user.id == ADMIN_ID

        @bot_instance.tree.command(name="shutdown", description="Shutdown the bot")
        async def shutdown(interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                await interaction.response.send_message("You cannot use this command.", ephemeral=True)
                return
            log_event(f"{interaction.user} ran /shutdown")
            await interaction.response.send_message("Shutting down...")
            await bot_instance.close()

        @bot_instance.tree.command(name="restart", description="Restart the bot")
        async def restart(interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                await interaction.response.send_message("You cannot use this command.", ephemeral=True)
                return
            log_event(f"{interaction.user} ran /restart")
            await interaction.response.send_message("Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)

        @bot_instance.tree.command(name="forceshutdown", description="Force shutdown")
        async def forceshutdown(interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                await interaction.response.send_message("You cannot use this command.", ephemeral=True)
                return
            log_event(f"{interaction.user} ran /forceshutdown")
            await interaction.response.send_message("Force shutdown...")
            await bot_instance.close()

        @bot_instance.tree.command(name="forcerestart", description="Force restart")
        async def forcerestart(interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                await interaction.response.send_message("You cannot use this command.", ephemeral=True)
                return
            log_event(f"{interaction.user} ran /forcerestart")
            await interaction.response.send_message("Force restart...")
            os.execv(sys.executable, ['python'] + sys.argv)

        @bot_instance.tree.command(name="refresh", description="Refresh audio list from folder")
        async def refresh(interaction: discord.Interaction):
            BotHandler.update_audio_list()
            log_event(f"{interaction.user} ran /refresh, updated audio list: {BotHandler.audio_list}")
            await interaction.response.send_message(f"Audio list refreshed. {len(BotHandler.audio_list)} tracks found.", ephemeral=True)

    @staticmethod
    def update_audio_list():
        BotHandler.audio_list = [f for f in os.listdir(audio_folder) if f.endswith(".mp3")]
        log_event(f"Audio list updated: {BotHandler.audio_list}")

    @staticmethod
    def update_voice_list(guild):
        BotHandler.voice_list = [vc for vc in guild.voice_channels]
        log_event(f"Voice channels updated: {[vc.name for vc in BotHandler.voice_list]}")

    @staticmethod
    def create_tos_embed():
        embed = discord.Embed(title="Use At Your Own Risk", description="Accept The TOS", color=0x808080)
        embed.set_thumbnail(url=f"attachment://{os.path.basename(pfp_path)}")
        embed.set_footer(text="Made by p̷̧̅ara̶͍̎n̶̰̓oį̵̿ḏ̵̓ | BETA")
        return embed

    @staticmethod
    def create_main_embed():
        embed = discord.Embed(title="Audio Player", description="Select an audio and voice channel", color=0x808080)
        embed.set_thumbnail(url=f"attachment://{os.path.basename(pfp_path)}")
        footer_text = "Made by p̷̧̅ara̶͍̎n̶̰̓oį̵̿ḏ̵̓ | BETA"
        if BotHandler.selected_audio:
            embed.add_field(name="Selected Audio", value=BotHandler.selected_audio, inline=False)
        if BotHandler.selected_channel:
            embed.add_field(name="Selected Voice Channel", value=BotHandler.selected_channel.name, inline=False)
        embed.set_footer(text=footer_text)
        return embed

class TOSView(View):
    def __init__(self, bot, guild):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild = guild
        self.add_item(TOSAcceptButton(bot, guild))
        self.add_item(TOSDisagreeButton())

class TOSAcceptButton(Button):
    def __init__(self, bot, guild):
        super().__init__(label="Accept", style=discord.ButtonStyle.success)
        self.bot = bot
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        log_event(f"{interaction.user} clicked Accept")
        BotHandler.update_audio_list()
        BotHandler.update_voice_list(self.guild)
        gui_view = GUIView(self.guild, self.bot)
        embed = BotHandler.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=gui_view)

class TOSDisagreeButton(Button):
    def __init__(self):
        super().__init__(label="Disagree", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        log_event(f"{interaction.user} clicked Disagree")
        await interaction.response.send_message("You disagreed. You cannot use this bot.", ephemeral=True)

class GUIView(View):
    def __init__(self, guild, bot):
        super().__init__(timeout=None)
        self.guild = guild
        self.bot = bot
        self.add_item(AudioSelect())
        self.add_item(ChannelSelect())
        self.add_item(PlayButton())
        self.add_item(StopButton())
        self.add_item(LoopButton())

class AudioSelect(Select):
    def __init__(self):
        options = [discord.SelectOption(label=a) for a in BotHandler.audio_list]
        super().__init__(placeholder="Select Audio", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        BotHandler.selected_audio = self.values[0]
        log_event(f"{interaction.user} selected audio: {self.values[0]}")
        embed = BotHandler.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class ChannelSelect(Select):
    def __init__(self):
        options = [discord.SelectOption(label=vc.name, value=str(vc.id)) for vc in BotHandler.voice_list]
        super().__init__(placeholder="Select Voice Channel", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        vc_id = int(self.values[0])
        BotHandler.selected_channel = discord.utils.get(self.view.guild.voice_channels, id=vc_id)
        log_event(f"{interaction.user} selected voice channel: {BotHandler.selected_channel.name}")
        embed = BotHandler.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class PlayButton(Button):
    def __init__(self):
        super().__init__(label="Play", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not BotHandler.selected_audio or not BotHandler.selected_channel:
            log_event(f"{interaction.user} tried to play but no audio/VC selected")
            await interaction.followup.send("Select both audio and channel first", ephemeral=True)
            return
        vc = BotHandler.selected_channel
        if not vc.guild.voice_client:
            vc_client = await vc.connect()
        else:
            vc_client = vc.guild.voice_client
        vc_client.stop()
        audio_path = os.path.join(audio_folder, BotHandler.selected_audio)
        source = FFmpegPCMAudio(audio_path, executable=ffmpeg_exe)
        vc_client.play(source)
        log_event(f"{interaction.user} played {BotHandler.selected_audio} in {vc.name}")
        await interaction.followup.send(f"Playing {BotHandler.selected_audio} in {vc.name}", ephemeral=True)

class StopButton(Button):
    def __init__(self):
        super().__init__(label="Stop", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc_client = interaction.guild.voice_client
        if vc_client and vc_client.is_playing():
            vc_client.stop()
            log_event(f"{interaction.user} stopped playback")
            await interaction.followup.send("Playback stopped", ephemeral=True)
        else:
            await interaction.followup.send("No audio is playing", ephemeral=True)

class LoopButton(Button):
    def __init__(self):
        super().__init__(label="Loop", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        BotHandler.loop_audio = not BotHandler.loop_audio
        state = "enabled" if BotHandler.loop_audio else "disabled"
        log_event(f"{interaction.user} set loop: {state}")
        await interaction.response.send_message(f"Loop {state}", ephemeral=True)
