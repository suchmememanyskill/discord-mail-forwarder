import discord
from discord.ext import commands

import asyncio
import emailclient
import env
import logging
import traceback
import sys
import aiohttp

intents = discord.Intents.none()
intents.guilds = True
logger = logging.getLogger('discord.bot')

bot = discord.Client(intents=intents)
is_bot = False


class ReplyEmail(discord.ui.Modal):
    def __init__(self, email: emailclient.ProcessedEmail):
        self.subject.default = "Re: " + email.subject
        super().__init__(title="Reply to Email")
        self.email = email

    subject = discord.ui.TextInput(
        label='Subject',
        placeholder='Subject of reply',
    )

    body = discord.ui.TextInput(
        label='Body',
        style=discord.TextStyle.long,
        placeholder='Type your reply here',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await emailclient.reply_to_email(self.email, self.subject.value, self.body.value)
        logger.info(f"Replied to email: {self.subject.value}")

        embed = discord.Embed(title=self.subject.value, description=self.body.value, colour=discord.Colour.blue())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send("Reply Sent!", embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class ReplyButton(discord.ui.View):
    def __init__(self, email: emailclient.ProcessedEmail, allowed_replier: discord.Role | None):
        super().__init__(timeout=None)
        self.email = email
        self.allowed_replier = allowed_replier

    @discord.ui.button(label='Reply', style=discord.ButtonStyle.gray, emoji="✉️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReplyEmail(self.email)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.allowed_replier and self.allowed_replier not in interaction.user.roles:
            await interaction.response.send_message("You are not allowed to reply to this email.", ephemeral=True)
            return False
        
        return True


async def loop():
    while True:

        try:
            emails = await emailclient.get_new_emails()

            for x in emails:
                creds = x[0]
                email = x[1]

                logger.info(f"Received email ({creds.email_user}): {email.subject}")

                embed = discord.Embed(title=f"{email.subject}", description=email.body[0:4000], colour=discord.Colour.green())
                embed.set_author(name=f"From: {email.sender}")

                if creds.discord_channel_webhook is not None:
                    async with aiohttp.ClientSession() as session:
                        webhook = discord.Webhook.from_url(creds.discord_channel_webhook, session=session)
                        await webhook.send(f"New email received ({creds.email_user})", embed=embed, files=email.attachments)

                if is_bot and creds.discord_channel_id:
                    channel = bot.get_channel(creds.discord_channel_id)
                    allowed_replier = None
                    view = None

                    if channel is None:
                        channel = await bot.fetch_channel(creds.discord_channel_id)

                    if creds.allowed_replier:
                        allowed_replier = channel.guild.get_role(creds.allowed_replier)
                        if allowed_replier is None:
                            await channel.guild.fetch_roles()
                            allowed_replier = channel.guild.get_role(creds.allowed_replier)
                            if allowed_replier is None:
                                logger.warning(f"Role {creds.allowed_replier} was not found in the server")

                    if creds.allow_replies:
                        view = ReplyButton(email, allowed_replier)

                    await channel.send(f"New email received ({creds.email_user})", embed=embed, view=view, files=email.attachments)

        except Exception:
            logger.error(None, exc_info=True)

        await asyncio.sleep(60)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info('------')
    asyncio.create_task(loop())


if env.BOT_TOKEN is None or env.BOT_TOKEN == "":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.warning("Bot token is nothing. Can only execute webhooks")
    asyncio.run(loop())
else:
    is_bot = True
    bot.run(env.BOT_TOKEN)
