# restricting_tg_bot
Telegram bot with integration of Google Sheets, collection of information about users,
the ability to limit messages from selected users and delete messages.

The bot consists of several parts.

tg bot
Structure: channel with an attached discussion group, the bot has been added to the group as an administrator.
Allow group work for the bot: to do this, set Bot Settings → Group Privacy → Disable via the botfather.
Use the /help command to find out the existing bot commands.

tg API
To use TG API, you need to create an application through the site:
https://my.telegram.org/
Insert api_id and api_hash of this application into the configuration file
The user must be added to the group. It is desirable that the user does not have two-factor authentication.
During the first launch, you must enter the phone number, the confirmation code from the account and the code
from the message in the command line, if there is two-factor authentication.

Google Sheets
User table, you need to write the table ID in the configuration file and put the file with the keys
from the Google service account: app/data/credentials.json



Before running the file app/src/main.py, install the libraries from the file requirements.txt

