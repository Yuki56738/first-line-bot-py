import logging
import os
import traceback

from flask import Flask, request, abort
from linebot import *
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
# from linebot.async_api import *
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_TOKEN"))
handler = WebhookHandler(os.environ.get("WEBH"))


@app.route("/test")
def test():
    return "Hello World!"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(Event)
def handle_event(event: Event):
    print("event type: " + event.type)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    message_text = ''
    if event.message.type == "text":
        message_text = event.message.text

    if message_text.startswith('!r'):
        # reply_text = 'You said: ' + message_text
        reply_text = message_text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif message_text.startswith('!hello'):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Hello World!")
        )
    elif message_text.startswith('!info'):
        if event.source.type != "group":
            user_id = event.source.user_id
            user_prof = line_bot_api.get_profile(user_id=user_id)
            dispname = user_prof.display_name
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{dispname}\nuser id: {user_id}\n{user_prof.picture_url}")
            )
            return
        user_id = event.source.user_id
        group_id = event.source.group_id
        dispname = line_bot_api.get_group_member_profile(group_id=group_id, user_id=user_id).display_name
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{dispname}\nuser id: {user_id}")
        )
    elif message_text.startswith('!type'):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{event.message.type}")
        )
    elif message_text.startswith('!gid'):
        guild_id = event.source.group_id
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=guild_id)
        )
    elif message_text.startswith('!image'):
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url="https://1.risaton.net/image.jpg",
                preview_image_url="https://1.risaton.net/image.jpg"
            )
        )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=os.environ.get("PORT", 5100))
    # app.run()
    # app.run(host='0.0.0.0', port=5100, debug=False)
