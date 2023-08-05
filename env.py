import os

BOT_TOKEN = os.getenv("BOT_TOKEN", os.getenv("TOKEN"))


class RegisteredEmail:
    def __init__(self, email_host: str, email_user: str, email_pass: str, discord_channel_id: int | str | None = 0, discord_channel_webhook: str | None = None, smtp_port: int | str | None = 587,
                 imap_port: int | str | None = 993, allow_replies: int | str | None = 1, allowed_replier: int | str | None = None):
        self.email_host = email_host
        self.email_user = email_user
        self.email_pass = email_pass

        # Optional
        self.discord_channel_webhook = discord_channel_webhook
        self.discord_channel_id = int(discord_channel_id) if discord_channel_id else None
        self.smtp_port = int(smtp_port or 587)
        self.imap_port = int(imap_port or 993)
        self.allow_replies = bool(allow_replies) if allow_replies is not None else True
        self.allowed_replier = int(allowed_replier) if allowed_replier else None


REGISTERED_EMAILS: list[RegisteredEmail] = []


def probe_environment():
    global REGISTERED_EMAILS

    if "EMAIL_HOST" in os.environ:
        REGISTERED_EMAILS.append(RegisteredEmail(os.environ["EMAIL_HOST"],
                                                 os.environ["EMAIL_USER"],
                                                 os.environ["EMAIL_PASS"],
                                                 os.getenv("DISCORD_CHANNEL_ID"),
                                                 os.getenv("DISCORD_CHANNEL_WEBHOOK"),
                                                 os.getenv("SMTP_PORT"),
                                                 os.getenv("IMAP_PORT"),
                                                 os.getenv("ALLOW_REPLIES"),
                                                 os.getenv("ALLOWED_REPLIER")))

    idx = 1
    while os.getenv(f"EMAIL_HOST.{idx}") is not None:
        REGISTERED_EMAILS.append(RegisteredEmail(os.environ[f"EMAIL_HOST.{idx}"],
                                                 os.environ[f"EMAIL_USER.{idx}"],
                                                 os.environ[f"EMAIL_PASS.{idx}"],
                                                 os.getenv(f"DISCORD_CHANNEL_ID.{idx}"),
                                                 os.getenv(f"DISCORD_CHANNEL_WEBHOOK.{idx}"),
                                                 os.getenv(f"SMTP_PORT.{idx}"),
                                                 os.getenv(f"IMAP_PORT.{idx}"),
                                                 os.getenv(f"ALLOW_REPLIES.{idx}"),
                                                 os.getenv("ALLOWED_REPLIER")))
        idx += 1


probe_environment()
