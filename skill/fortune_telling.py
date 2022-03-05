import random

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import get_slot_value, is_intent_name, is_request_type
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

import requests
import config
from pprint import pprint
import json
from datetime import datetime as dt

url = "https://api.notion.com/v1/databases/%s/query" %config.NOTION_DATABASE_ID
headers = {
  'Authorization': 'Bearer ' + config.NOTION_ACCESS_TOKEN,
  'Notion-Version': '2021-08-16',
  'Content-Type': 'application/json',
}
r = requests.post(url, headers=headers)

sb = SkillBuilder()
today_task = {}                   # タスクが入る，辞書型で管理

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
	# type: (HandlerInput) -> Response
	inf = notion()
	today_now = str(dt.now())       # datetime型ではスライス使えない
	today_now = today_now[:10]      # 年月日だけ欲しいからスライス
	today_now = dt.strptime(today_now, "%Y-%m-%d")
	speech_text = today_task.get(today_now)
	handler_input.response_builder.speak(speech_text).set_card(SimpleCard("Fortune Telling", speech_text)).set_should_end_session(False)
	return handler_input.response_builder.response


def notion():                     # Notionから情報を持ってくる
  for i in range(len(r.json()["results"])):
    name = r.json()['results'][i]['properties']['名前']['title'][0]['plain_text']
		quantity = r.json()['results'][i]['properties']['日付']['date']['start']
		quantity = quantity[:10]      # 年月日だけ欲しいからスライス
		tdate = dt.strptime(quantity, "%Y-%m-%d")
		# tdate = datetime.strptime(quantity, "%Y-%m-%d")
		today_task[tdate] = name
  return today_task


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "こんにちは。と言ってみてください。"

    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("Fortune Telling", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "さようなら"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Fortune Telling", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # type: (HandlerInput) -> Response

    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    print(exception)

    speech = "すみません、わかりませんでした。もう一度言ってください。"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


handler = sb.lambda_handler()
