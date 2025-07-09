# restricting_tg_bot

Telegram bot with Google Sheets integration that collects user information,  
allows restricting messages from selected users, and deleting messages.

---

## Bot Structure

### Telegram Bot

- Setup: A channel with an attached discussion group, where the bot is added as an administrator.
- To enable the bot to work properly in the group, disable group privacy:  
  Go to BotFather → Bot Settings → Group Privacy → Disable.
- Use the `/help` command to see available bot commands.

### Telegram API

- To use the Telegram API, create an application at:  
  [https://my.telegram.org/](https://my.telegram.org/)
- Insert the `api_id` and `api_hash` from your application into the configuration file.
- The user must be added to the group.
- It is recommended that the user does not have two-factor authentication enabled.
- On the first run, you will need to enter your phone number, confirmation code from the account, and (if applicable) the code from the message, in the command line.

### Google Sheets

- User data is stored in a spreadsheet.
- Write the spreadsheet ID in the configuration file.
- Place the Google service account credentials file at:  
  `app/data/credentials.json`.

---

## Installation

Before running the file `app/src/main.py`, install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
