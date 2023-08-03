import env, emailclient, asyncio, traceback

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description="Bot to forward emails", intents=intents)

class ReplyEmail(discord.ui.Modal):
    def __init__(self, email : emailclient.ProcessedEmail):
        self.subject.default = "Re: " + email.subject
        super().__init__(title=f"Reply to Email")
        self.email = email;

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
        await interaction.followup.send(f"{interaction.user.display_name} successfully sent a reply")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

class ReplyButton(discord.ui.View):
    def __init__(self, email : emailclient.ProcessedEmail):
        super().__init__(timeout=999999999999)
        self.email = email

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Reply', style=discord.ButtonStyle.gray, emoji="✉️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReplyEmail(self.email)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.stop()

async def loop():
    while True:
        
        try:
            emails = await emailclient.get_new_emails()
            
            for x in emails:
                channel = await bot.fetch_channel(x[0].discord_channel_id)
                email = x[1]

                embed = discord.Embed(title=email.subject, description=email.body)
                embed.set_author(name=email.sender)

                await channel.send(embed=embed, view=ReplyButton(email))

        except Exception as e:
            print(f"Exception: {str(e)}")
        
        await asyncio.sleep(60)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    asyncio.create_task(loop())

bot.run(env.BOT_TOKEN)