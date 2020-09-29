import discord
import csv

import config


class WeenieHutGeneral(discord.Client):
    enabled = False
    setting_nicks = False

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))
        self.votes = lambda msg: sum(
            [
                reaction.count if str(reaction.emoji) == config.UP else -reaction.count
                for reaction in msg.reactions
            ]
        )
        channel = await self.fetch_channel(config.VOTE_CHANNEL)
        message = await channel.fetch_message(config.VOTE_MESSAGE)
        guild = await self.fetch_guild(config.GUILD)
        self.enabled = self.votes(message) >= config.VOTES_REQUIRED
        # if state isn't same as last time script was ran, run state change
        if guild.name != (config.PHRASE if self.enabled else config.GUILD_NAME):
            await self.change_state(self.enabled)

    async def on_message(self, message):
        if not self.enabled:
            return
        if message.content != config.PHRASE:
            print(
                f"Deleting fradulent message from {message.author}: {message.content}"
            )
            if config.DEBUG:
                return
            await message.delete()

    async def on_message_edit(self, before, after):
        if not self.enabled:
            return
        if after.content != config.PHRASE:
            print(
                f"Deleting fradulent edited message from {after.author}: {after.content}"
            )
            if config.DEBUG:
                return
            await after.delete()

    async def check_enabled(self, payload):
        if (
            payload.channel_id == config.VOTE_CHANNEL
            and payload.message_id == config.VOTE_MESSAGE
        ):
            channel = await self.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if str(payload.emoji) != config.UP and str(payload.emoji) != config.DOWN:
                await message.clear_reaction(payload.emoji)
                return True
            to_enable = self.votes(message) >= config.VOTES_REQUIRED
            if self.enabled != to_enable:
                await self.change_state(to_enable)
            return True
        return False

    async def change_state(self, enable):
        print("ENABLING" if enable else "DISABLING")
        self.enabled = enable
        with open(config.ICON_ON if enable else config.ICON_OFF, "rb") as file:
            icon = file.read()
        guild = await self.fetch_guild(config.GUILD)
        await guild.edit(icon=icon, name=config.PHRASE if enable else config.GUILD_NAME)

        if config.DEBUG:
            print("DEBUG: Skipping channels and nicks...")
            return

        self.setting_nicks = True
        if enable:
            nicks = {}
            async for member in guild.fetch_members():
                nicks[member.id] = member.display_name
                print(f"Setting {member.display_name} to {config.PHRASE}")
                try:
                    await member.edit(nick=config.PHRASE)
                except discord.errors.Forbidden:
                    print("forbidden")
            with open(config.NICKS_CSV, "w+") as file:
                writer = csv.DictWriter(
                    file, dialect=csv.excel_tab, fieldnames=["user", "nick"]
                )
                for user, nick in nicks.items():
                    writer.writerow({"user": user, "nick": nick})
        else:
            nicks = {}
            try:
                with open(config.NICKS_CSV, "r+") as file:
                    reader = csv.DictReader(
                        file, dialect=csv.excel_tab, fieldnames=["user", "nick"]
                    )
                    for row in reader:
                        nicks[row["user"]] = row["nick"]
                async for member in guild.fetch_members():
                    try:
                        print(
                            f"Setting {member.display_name} to {nicks.get(str(member.id))}"
                        )
                        await member.edit(nick=nicks.get(str(member.id)))
                    except discord.errors.Forbidden:
                        print("forbidden")
                        pass
            except FileNotFoundError:
                print("Nick CSV not found, skipping")
        self.setting_nicks = False

        for channel_id, name in config.CHANNELS.items():
            await (await self.fetch_channel(channel_id)).edit(
                name=config.PHRASE if enable else name
            )

    async def on_raw_reaction_add(self, payload):
        if await self.check_enabled(payload):
            return
        if not self.enabled:
            return
        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        print(
            f"Deleting fradulent reaction from {payload.member.name}: {payload.emoji}"
        )
        if config.DEBUG:
            return
        await message.clear_reactions()

    async def on_raw_reaction_remove(self, payload):
        await self.check_enabled(payload)

    async def on_member_update(self, before, after):
        if self.setting_nicks:
            return
        if not self.enabled:
            return
        if after.nick != config.PHRASE:
            print(f"Removing fradulent nickname from {before}: {after.nick}")
            if config.DEBUG:
                return
            try:
                await after.edit(nick=config.PHRASE)
            except discord.errors.Forbidden:
                print("Cannot change this user's nickname")


client = WeenieHutGeneral()
client.run(config.BOT_TOKEN)
