## Telegram bot for live customer support

### How this bot works:
This is a telegram webhook bot that I made using python and flask. It's primary purpose is to act as a line of communication between a customer support group and the customers. Any user can privately message the bot, and it will forward those messages into a designated telegram group chat that you set. Members of that group chat can then reply to those messages anonymously and the bot will forward the messages back to the user who first sent that message. (Members of that group can also type their message followed by #C followed by a user's chat ID to send a message to a particular user. eg. How may I help you? #C535478901)  

### What is a webhook?
A webhook can be thought of as a type of API that is driven by events rather than requests. Instead of one application making a request to another to receive a response, a webhook is a service that allows one program to send data to another as soon as a particular event takes place.

### How to set up bot locally:

You will need to do 3 things, set up your webhook, get BOT_ID and GROUP_ID.

#### How to set up webhook:
1. Key in this url into any web browser: `https://api.telegram.org/bot<token\>/setwebhook?url=\<yoururl\>`
2. `<token\>` is your telegram bot token
3. To get `<token\>`, on telegram, use the __/newbot__ command to create a new bot. The BotFather will ask you for a name and username, then generate an authentication token for your new bot.
4. The token is a string along the lines of `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw` that is required to authorize the bot and send requests to the Bot API. Keep your token secure and store it safely, it can be used by anyone to control your bot.
3.  To get <yoururl\>, cd to the root directory of this folder and run:
```bash
./ngrok http 5000
```
4. The __Forwarding__ `https` url is <yoururl\>
5. Run the program in the terminal using:
```bash
python app.py
```


#### How to get bot id:
1. Add the new bot to the group
2. Send a message to the bot privately
3. Reply to the message by the bot in the group
4. See reply_to_message.from.id in the response json object

#### How to get group id:
1. Check the url in telegram web


