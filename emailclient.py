import asyncio
import base64
import email
import email.message
import email.utils
import io
import re

import env
import imaplib
import smtplib

from discord import File
from email import policy
from bs4 import BeautifulSoup


class ProcessedEmail:
    attachment: list
    sender: str
    receiver: str
    date: str
    subject: str
    references: str
    message_id: str

    def __init__(self, email: email.message.Message, received_by: str):
        self.attachments = []
        self.body = ''
        self._process(email)
        self.received_by = received_by

    def _process(self, email: email.message.Message):
        self.sender = email["From"]
        self.receiver = email["To"]
        self.date = email["Date"]
        self.subject = email["Subject"]
        self.references = email["References"] or ""
        self.message_id = email["Message-Id"]

        # https://stackoverflow.com/questions/64377425/how-can-i-read-the-mail-body-of-a-mail-with-python
        if email.is_multipart():
            for part in email.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                # skip any text/plain (txt) attachments
                if ctype == 'text/plain':
                    self.body = part.get_payload(decode=True)  # decode
                elif cdispo is not None and cdispo.startswith('attachment') and ctype in ['image/jpeg', 'image/png']:
                    img_bytes = base64.b64decode(part.get_payload())
                    buffer = io.BytesIO(img_bytes)
                    self.attachments.append(File(fp=buffer, filename=part.get_filename()))

            if self.body == '':
                for part in email.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    # skip any text/html (html) attachments
                    if ctype == 'text/html' and 'attachment' not in cdispo:
                        self.body = part.get_payload(decode=True)  # decode
                        break

            if self.body == '':
                self.body = "(No Content)"

        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            self.body = email.get_payload(decode=True)

        if isinstance(self.body, bytes):
            self.body = self.body.decode('utf-8')

        if self.body:
            soup = BeautifulSoup(self.body, features="html.parser")
            # Remove HTML tags from body
            self.body = soup.get_text(separator='\n').replace("\r\n", "\n").strip()
            # Remove extra newlines
            self.body = re.sub(r'\n\s*\n', r'\n\n', self.body, flags=re.M)
            # Try to remove replies, should work for gmail at least, this is just an unwinnable battle
            self.body = re.sub(r'>?On.* wrote:\n+>[\s\S]*', '', self.body)


async def get_new_emails() -> list[tuple[env.RegisteredEmail, ProcessedEmail]]:
    emails = []

    for x in env.REGISTERED_EMAILS:
        fetched_emails = await asyncio.to_thread(_fetch_emails_sync, x)
        for y in fetched_emails:
            emails.append((x, y))

    return emails


def _fetch_emails_sync(creds: env.RegisteredEmail) -> list[ProcessedEmail]:
    mail = imaplib.IMAP4_SSL(creds.email_host, creds.imap_port)
    rc, resp = mail.login(creds.email_user, creds.email_pass)

    mail.select('Inbox')
    status, data = mail.search(None, '(UNSEEN)')

    emails = []

    for num in data[0].split():
        # get a single message and parse it by policy.SMTP (RFC compliant)
        status, email_data = mail.fetch(num, '(RFC822)')
        content: tuple | bytes | None = email_data[0]
        if isinstance(content, tuple):
            email_msg = content[1]
        elif isinstance(content, bytes):
            email_msg = content
        else:
            continue
        email_msg = email.message_from_bytes(email_msg, policy=policy.SMTP)
        emails.append(ProcessedEmail(email_msg, creds.email_user))

    mail.close()
    mail.logout()

    return emails


async def reply_to_email(reply_to: ProcessedEmail, subject: str, body: str):
    # Find associated email
    creds = None
    for x in env.REGISTERED_EMAILS:
        if x.email_user == reply_to.received_by:
            creds = x
            break

    if creds is None:
        raise Exception("Receiver's credentials are not present")

    await asyncio.to_thread(_send_reply_sync, creds, reply_to, subject, body)


def _send_reply_sync(creds: env.RegisteredEmail, reply_to: ProcessedEmail, subject: str, body: str):
    body = body + f"\n\n\nOn {reply_to.date}, {reply_to.sender} wrote:\n{reply_to.body}"

    message = email.message.EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = creds.email_user
    message["X-Sender"] = creds.email_user
    # TODO: Check properly who we should send this to using Return-to and Reply to headers
    message["To"] = reply_to.sender
    message["In-Reply-To"] = reply_to.message_id
    message["References"] = reply_to.references + " " + reply_to.message_id
    message["Date"] = email.utils.formatdate(localtime=True)

    mail = smtplib.SMTP(creds.email_host, creds.smtp_port)
    mail.starttls()
    mail.login(creds.email_user, creds.email_pass, initial_response_ok=True)
    mail.send_message(message, creds.email_user, reply_to.sender)
    mail.quit()
