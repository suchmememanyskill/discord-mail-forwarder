import os

BOT_TOKEN = os.getenv("BOT_TOKEN", os.getenv("TOKEN"))

class RegisteredEmail:
    def __init__(self, email_host : str, email_user : str, email_pass : str, discord_channel_id : int, smtp_port : int = 587, imap_port : int = 993, allow_replies : int = 1):
        self.email_host = email_host
        self.email_user = email_user
        self.email_pass = email_pass
        self.discord_channel_id = discord_channel_id

        # Optional
        self.smtp_port = int(smtp_port) if smtp_port != None else 587
        self.imap_port = int(imap_port) if imap_port != None else 993
        self.allow_replies = (int(allow_replies) != 0) if allow_replies != None else True

REGISTERED_EMAILS : list[RegisteredEmail] = []

def probe_environment():
    global REGISTERED_EMAILS

    if ("EMAIL_HOST" in os.environ):
        REGISTERED_EMAILS.append(RegisteredEmail(os.environ["EMAIL_HOST"], 
                                                 os.environ["EMAIL_USER"], 
                                                 os.environ["EMAIL_PASS"], 
                                                 int(os.environ["DISCORD_CHANNEL_ID"]),
                                                 os.getenv("SMTP_PORT"),
                                                 os.getenv("IMAP_PORT"),
                                                 os.getenv("ALLOW_REPLIES")))
    
    idx = 1
    while os.getenv(f"EMAIL_HOST.{idx}") != None:
        REGISTERED_EMAILS.append(RegisteredEmail(os.environ[f"EMAIL_HOST.{idx}"], 
                                                 os.environ[f"EMAIL_USER.{idx}"], 
                                                 os.environ[f"EMAIL_PASS.{idx}"], 
                                                 int(os.environ[f"DISCORD_CHANNEL_ID.{idx}"]),
                                                 os.getenv(f"SMTP_PORT.{idx}"),
                                                 os.getenv(f"IMAP_PORT.{idx}"),
                                                 os.getenv(f"ALLOW_REPLIES.{idx}")))   
        idx += 1

probe_environment()