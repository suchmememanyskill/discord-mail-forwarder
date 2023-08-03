# discord-mail-forwarder

discord-mail-forwarder is a dockerised mail forwarder to discord. It will read out the inbox of an email account, and dump those messages in a channel as an embed. You can also reply to these emails within discord. Multiple emails can be monitored at once. Inspired by [discord-mail-webhook](https://github.com/AshCorr/discord-mail-webhook)

![preview1](img/message.jpg)

![preview2](img/modal.jpg)

## Configuration

This bot supports watching multiple emails. Configuration wise, this is defined by placing a number incrementally behind the name of an environment variable. For an example, see the docker-compose example

Environment Variable|Default Value|Description
----|----|----
BOT_TOKEN|None|Sets the discord bot token.
EMAIL_HOST.{idx}|None|Sets the email host. Host for SMTP and IMAP is assumed to be the same.
EMAIL_USER.{idx}|None|Sets the email to login with.
EMAIL_PASS.{idx}|None|Sets the password to login with.
DISCORD_CHANNEL_ID.{idx}|None|Sets the discord channel to send messages in.
SMTP_PORT.{idx}|589|Sets the port of the SMTP server. Uses StartTLS
IMAP_PORT.{idx}|993|Sets the port of the IMAP server.
ALLOW_REPLIES.{idx}|1|Set to 1 to allow replying from within discord. Set to 0 to disable.

### Example docker-compose.yml

```yml
version: '3'

services:
  email-listener:
    image: TODO
    restart: unless-stopped
    container_name: email-listener
    environment:
      - BOT_TOKEN=my_very_secure_bot_token
      # Email Account 1
      - EMAIL_HOST.1=mail.server.com
      - EMAIL_USER.1=mudkip@server.com
      - EMAIL_PASS.1=my_very_secure_password
      - DISCORD_CHANNEL_ID.1=1001843557109346365
      # Email Account 2
      - EMAIL_HOST.2=mail.server.com
      - EMAIL_USER.2=treeco@server.com
      - EMAIL_PASS.2=my_very_secure_password_2
      - DISCORD_CHANNEL_ID.2=1001843557109346365
      - ALLOW_REPLIES.2=0
