import re
import requests
import os
from flask import Flask, request

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') # Telegram bot token
SENDMESSAGE_URL = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_TOKEN) # Telegram send message url
SENDPHOTO_URL =  "https://api.telegram.org/bot{}/sendPhoto".format(TELEGRAM_TOKEN) # Telegram send photo url
SENDDOCUMENT_URL =  "https://api.telegram.org/bot{}/sendDocument".format(TELEGRAM_TOKEN) # Telegram send document url
BOT_ID = int(os.environ.get('BOT_ID')) # Bot id
GROUP_ID = int(os.environ.get('GROUP_ID')) # Telegram bot group chat id 
COMPANYNAME = "Customer Support"

app = Flask(__name__)

def send_message(msg_text, chat_id):
    payload = {
        'text': msg_text,
        'chat_id': chat_id
    }
    resp = requests.get(SENDMESSAGE_URL, params=payload)
    return resp

def send_photo(chat_id, file_id, caption):
    payload = {
        'chat_id': chat_id,
        'photo': file_id,
        'caption': caption
    }
    resp = requests.get(SENDPHOTO_URL, params=payload)
    return resp

def send_document(chat_id, file_id, caption):
    payload = {
        'chat_id': chat_id,
        'document': file_id,
        'caption': caption
    }
    resp = requests.get(SENDDOCUMENT_URL, params=payload)
    return resp

def get_text_message(resp): 
    if 'text' in resp:
        inc_text = resp['text']  # Get text message
        return inc_text
    else:
        inc_text = "No text"
        return inc_text

def get_chat_id(resp): 
    if 'chat' in resp:
        if 'id' in resp['chat']:
            chat_id = resp['chat']['id']  # Get chat id
            return chat_id
    chat_id = "No chat id"
    return chat_id

def get_first_name(resp): 
    if 'from' in resp:
        if 'first_name' in resp['from']:
            first_name = resp['from']['first_name'] # Get sender first name
            return first_name
    else:
        first_name = "Unknown first name"
        return first_name

def get_caption(resp):
    caption = resp['caption']
    print(caption)
    return caption

def get_file_id_photo(resp):
    file_id = resp['photo'][-1]['file_id']
    return file_id

def get_file_id_document(resp):
    file_id = resp['document']['file_id']
    return file_id

def new_chat_member(resp):
    first_name = resp['first_name']
    inc_text = "Welcome {fname} to the group!".format(fname=first_name)
    return inc_text

def left_chat_member(resp):
    first_name = resp['first_name']
    inc_text = "{fname} has left the group. Sorry to see you go!".format(fname=first_name)
    return inc_text

def get_user_id(resp_message, msg_type):
    if msg_type == 'text':
        user_id = resp_message['reply_to_message']['text'].split(
                                    "Chat ID: ")[-1]  # Get the chat id to send message to
    elif msg_type == 'photo/document':
        user_id = resp_message['reply_to_message']['caption'].split(
                                    "Chat ID: ")[-1]  # Get the chat id to send message to
    else:
        return
    return user_id


@app.route("/", methods=["POST", "GET"])
def telegram_app_POST():
    if (request.method == "POST"):
        resp = request.get_json()
        print(resp)

        if 'message' in resp:  # Check if resp contains 'message'
            resp_message = resp['message']
            if 'new_chat_member' in  resp_message:  # User joined the group
                inc_text = new_chat_member(resp_message['new_chat_member'])
                response = send_message(inc_text, GROUP_ID)
                if response.status_code == 200:
                    print('New chat member message sent.')
                elif response.status_code == 404:
                    print('Not Found.')
                else:
                    print('Unknown error.')
            elif 'left_chat_member' in  resp_message: # User left the group
                inc_text = left_chat_member(resp_message['left_chat_member'])
                response = send_message(inc_text, GROUP_ID)
                if response.status_code == 200:
                    print('Left chat member message sent.')
                elif response.status_code == 404:
                    print('Not Found.')
                else:
                    print('Unknown error.')
            elif 'photo' in resp_message: # Photo received
                if 'caption' in resp_message: # Check if there is a caption
                    caption = get_caption(resp_message)
                else:
                    caption = ''
                chat_id = get_chat_id(resp_message)
                first_name = get_first_name(resp_message)
                file_id = get_file_id_photo(resp_message)

                if (chat_id == GROUP_ID): # Sender is a member of customer support group
                    if 'reply_to_message' in resp_message: # Message is sent by reply method
                        if 'photo' in resp_message['reply_to_message'] or 'document' in resp_message['reply_to_message']: # Replying to a photo/document with a photo
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['caption']): # Check if the message is a reply message to the bot's message
                                user_id = get_user_id(resp_message, 'photo/document') # Get the chat id to send message to
                                caption = caption + \
                                    "\n\nFrom: {fname}".format(fname=COMPANYNAME) # Create a caption from the customer support group
                                response = send_photo(user_id, file_id, caption)
                                if response.status_code == 200:
                                    print("Photo sent to user!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Please reply to a message sent to the bot by a user.')
                        
                        else: # Replying to a text message with a photo
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['text']): # Check if the message is a reply message to the bot's message
                                user_id = get_user_id(resp_message, 'text') # Get the chat id to send message to
                                caption = caption + \
                                    "\n\nFrom: {fname}".format(fname=COMPANYNAME) # Create a caption from the customer support group
                                response = send_photo(user_id, file_id, caption)
                                if response.status_code == 200:
                                    print("Photo sent to user!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Please reply to a message sent to the bot by a user.')
                    elif (re.search("#C[0-9]+", caption)): # Message sent via #C method
                        start = caption.find('#C') + 2
                        end = caption.find('#C') + 11
                        user_id = caption[start:end]  # Extract 9 characters starting from #C
                        caption_text = caption.replace(
                            "#C" + user_id, "")  # Get the caption message
                        outgoing_text = caption_text + \
                            "\n\nFrom: {fname}".format(fname=COMPANYNAME)
                        response = send_photo(user_id, file_id, outgoing_text)
                        if response.status_code == 200:
                            print("Photo sent to user by #C method!")
                        elif response.status_code == 404:
                            print('Not Found.')
                        else:
                            print('Unknown error.')
                    else:
                        print('Photo sent within the group, but not to any user.')           
                else: # Sender is not a member of the group
                    caption = caption + \
                        "\n\nFrom: {fname} \nChat ID: {chat_id}".format(
                                fname=first_name, chat_id=chat_id)
                    response = send_photo(GROUP_ID, file_id, caption)
                    if response.status_code == 200:
                        print("Photo received from user!")
                    elif response.status_code == 404:
                        print('Not Found.')
                    else:
                        print('Unknown error.')
            elif 'document' in resp_message: # Document received
                if 'caption' in resp_message: # Check if there is a caption
                    caption = get_caption(resp_message)
                else:
                    caption = ''
                chat_id = get_chat_id(resp_message)
                first_name = get_first_name(resp_message)
                file_id = get_file_id_document(resp_message)

                if (chat_id == GROUP_ID): # Sender is a member of customer support group
                    if 'reply_to_message' in resp_message: # Message is sent by reply method
                        if 'photo' in resp_message['reply_to_message'] or 'document' in resp_message['reply_to_message']: # Replying to a photo/document with a document
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['caption']): # Check if the message is a reply message to the bot's message
                                user_id = get_user_id(resp_message, 'photo/document') # Get the chat id to send message to
                                caption = caption + \
                                            "\n\nFrom: {fname}".format(fname=COMPANYNAME) # Create a caption from the customer support
                                response = send_document(user_id, file_id, caption)
                                if response.status_code == 200:
                                    print("Document sent to user!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Please reply to a message sent to the bot by a user.')

                        else: # Replying to a text message with a document
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['text']): # Check if the message is a reply message to the bot's message
                                user_id = get_user_id(resp_message, 'text') # Get the chat id to send message to
                                caption = caption + \
                                    "\n\nFrom: {fname}".format(fname=COMPANYNAME) # Create a caption from the customer support
                                response = send_document(user_id, file_id, caption)
                                if response.status_code == 200:
                                    print("Document sent to user!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Please reply to a message sent to the bot by a user.')
                    elif (re.search("#C[0-9]+", caption)): # Message sent via #C method
                        start = caption.find('#C') + 2
                        end = caption.find('#C') + 11
                        user_id = caption[start:end]  # Extract 9 characters starting from #C
                        caption_text = caption.replace(
                            "#C" + user_id, "")  # Get the caption message
                        outgoing_text = caption_text + \
                            "\n\nFrom: {fname}".format(fname=COMPANYNAME)
                        response = send_document(user_id, file_id, outgoing_text)
                        if response.status_code == 200:
                            print("Document sent to user by #C method!")
                        elif response.status_code == 404:
                            print('Not Found.')
                        else:
                            print('Unknown error.')
                    else:
                        print('Document sent within the group, but not to any user.')    
                else: # Sender is not a member of the group
                    caption = caption + \
                        "\n\nFrom: {fname} \nChat ID: {chat_id}".format(
                                fname=first_name, chat_id=chat_id)
                    response = send_document(GROUP_ID, file_id, caption)
                    if response.status_code == 200:
                        print("Document received from user!")
                    elif response.status_code == 404:
                        print('Not Found.')
                    else:
                        print('Unknown error.')
            elif 'text' in resp_message: # Text message received
                inc_text = get_text_message(resp_message)
                chat_id = get_chat_id(resp_message)
                first_name = get_first_name(resp_message)

                if (chat_id == GROUP_ID): # Sender is a member of customer support group, Group id is chat id
                    if (re.search("#C[0-9]+", inc_text)):  
                        start = inc_text.find('#C') + 2
                        end = inc_text.find('#C') + 11
                        user_id = inc_text[start:end]  # Extract 9 characters starting from #C
                        text_message = inc_text.replace(
                            "#C" + user_id, "")  # Get the text message
                        outgoing_text = text_message + \
                            "\n\nFrom: {fname}".format(fname=COMPANYNAME)
                        response = send_message(outgoing_text, user_id)
                        if response.status_code == 200:
                            print("Message sent by #C method to user!")
                        elif response.status_code == 404:
                            print('Not Found.')
                        else:
                            print('Unknown error.')

                    elif 'reply_to_message' in resp_message:   
                        if 'photo' in resp_message['reply_to_message'] or 'document' in resp_message['reply_to_message']: # Replying to a photo/document with a text
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['caption']): # Check if the message is a reply message
                                user_id = get_user_id(resp_message, 'photo/document') # Get the chat id to send message to
                                outgoing_text = inc_text + \
                                        "\n\nFrom: {fname}".format(fname=COMPANYNAME) # Create a caption from the customer support
                                response = send_message(outgoing_text, user_id)
                                if response.status_code == 200:
                                    print("Message sent by reply method to a user's photo!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Text message sent within the group, replied to a photo, but not to any user.')
                        
                        else: # Replying to a text message with a text
                            if (resp_message['reply_to_message']['from']['id'] == BOT_ID and "Chat ID:" in resp_message['reply_to_message']['text']): # Check if the message is a reply message
                                user_id = get_user_id(resp_message, 'text') # Get the chat id to send message to
                                outgoing_text = inc_text + \
                                    "\n\nFrom: {fname}".format(fname=COMPANYNAME)
                                response = send_message(outgoing_text, user_id)
                                if response.status_code == 200:
                                    print("Message sent by reply method to user!")
                                elif response.status_code == 404:
                                    print('Not Found.')
                                else:
                                    print('Unknown error.')
                            else:
                                print('Text message sent within the group, replied to another text message, but not to any user.')
                        
                    else:
                        print("Text message sent within the group, but not to any user.")
                        
                else: # Sender is not a member of customer support group
                    outgoing_text = inc_text + \
                        "\n\nFrom: {fname} \nChat ID: {chat_id}".format(
                                fname=first_name, chat_id=chat_id)
                    response = send_message(outgoing_text, GROUP_ID) # Forward messages to group
                    if response.status_code == 200:
                        print("Message received from user!")
                    elif response.status_code == 404:
                        print('Not Found.')
                    else:
                        print('Unknown error.')
            else: # Unknown message received/error handling
                chat_id = get_chat_id(resp_message)
                if (chat_id == GROUP_ID):
                    if resp_message['reply_to_message']['from']['id'] == BOT_ID: # Check if the message is a reply message
                        warning = 'Your message has not been sent to the user because it is currently not supported by the bot. This bot only takes in text, photos, documents and emojis.'
                        response = send_message(warning, chat_id) # Write warning message to group chat
                    else:
                        print('An unexpected event has been triggered within this group.')
                else:
                    warning = 'Your message has not been received as this bot only takes in text, photos, documents and emojis. All other types of messages will be supported in the future.'
                    response = send_message(warning, chat_id) # Write warning message to group chat
                    if response.status_code == 200:
                        print("Warning sent to user.")
                    elif response.status_code == 404:
                        print('Not Found.')
                    else:
                        print('Unknown error.')
        else:
            print("Response does not contain message.")
    return "done"  # status 200 OK by default


