import os

BOT_TOKEN = os.getenv("BOT_TOKEN", os.getenv("TOKEN"))


class RegisteredEmail:
    def __init__(self, imap_host: str, smtp_host : str, email_user: str, email_pass: str, discord_channel_id: int | str | None = 0, discord_channel_webhook: str | None = None, smtp_port: int | str | None = 587,
                 imap_port: int | str | None = 993, allow_replies: int | str | None = 1, allowed_replier: int | str | None = None):
        self.imap_host = imap_host
        self.smtp_host = smtp_host
        self.email_user = email_user
        self.email_pass = email_pass

        if (self.imap_host is None or self.smtp_host is None or self.email_user is None or self.email_pass is None):
            raise Exception("Missing credentials...")

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
    default_imap_host = os.getenv("IMAP_HOST", os.getenv("EMAIL_HOST"))
    default_smtp_host = os.getenv("SMTP_HOST", os.getenv("EMAIL_HOST"))
    default_email_user = os.getenv("EMAIL_USER")
    default_email_pass = os.getenv("EMAIL_PASS")
    default_discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    default_discord_channel_webhook = os.getenv("DISCORD_CHANNEL_WEBHOOK")
    default_smtp_port = os.getenv("SMTP_PORT")
    default_imap_port = os.getenv("IMAP_PORT")
    default_allow_replies = os.getenv("ALLOW_REPLIES")
    default_discord_role_id = os.getenv("DISCORD_ROLE_ID", os.getenv("ALLOWED_REPLIER"))

    idx = 1
    while (os.getenv(f"EMAIL_HOST.{idx}") or os.getenv(f"IMAP_HOST.{idx}") or os.getenv(f"SMTP_HOST.{idx}") or os.getenv(f"EMAIL_USER.{idx}") or os.getenv(f"EMAIL_PASS.{idx}")) is not None:
        REGISTERED_EMAILS.append(RegisteredEmail(os.getenv(f"IMAP_HOST.{idx}", os.getenv(f"EMAIL_HOST.{idx}", default_imap_host)),
                                                 os.getenv(f"SMTP_HOST.{idx}", os.getenv(f"EMAIL_HOST.{idx}", default_smtp_host)),
                                                 os.getenv(f"EMAIL_USER.{idx}", default_email_user),
                                                 os.getenv(f"EMAIL_PASS.{idx}", default_email_pass),
                                                 os.getenv(f"DISCORD_CHANNEL_ID.{idx}", default_discord_channel_id),
                                                 os.getenv(f"DISCORD_CHANNEL_WEBHOOK.{idx}", default_discord_channel_webhook),
                                                 os.getenv(f"SMTP_PORT.{idx}", default_smtp_port),
                                                 os.getenv(f"IMAP_PORT.{idx}", default_imap_port),
                                                 os.getenv(f"ALLOW_REPLIES.{idx}", default_allow_replies),
                                                 os.getenv(f"DISCORD_ROLE_ID.{idx}", os.getenv(f"ALLOWED_REPLIER.{idx}", default_discord_role_id))))
        idx += 1

    if len(REGISTERED_EMAILS) <= 0 and default_imap_host is not None:
        REGISTERED_EMAILS.append(RegisteredEmail(default_imap_host, default_smtp_host, default_email_user, default_email_pass, default_discord_channel_id, default_discord_channel_webhook, default_smtp_port, default_imap_port, default_allow_replies, default_discord_role_id))

probe_environment()
