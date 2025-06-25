from datetime import datetime
from queue import Queue

import yaml
from pocketflow import Node

from utils.call_llm import call_llm
from utils.call_mock_api import call_book_hotel_api, call_check_weather_api
from utils.conversation import load_conversation, save_conversation
from utils.format_chat_history import format_chat_history


class DecideAction(Node):
    def prep(self, shared):
        conversation_id = shared["conversation_id"]
        session = load_conversation(conversation_id)
        return session, shared["history"], shared["query"]

    def exec(self, prep_res):
        session, history, query = prep_res
        prompt = f"""
### 指令
您是一名生活助理，能够帮助用户预订酒店和查询天气状况。
您需要根据您上次的操作、操作执行结果、聊天历史和当前用户问题来决定下一步操作。

### 聊天历史
{format_chat_history(history)}

### 当前用户问题
user: {query}

### 上下文
上次操作: {session.get("last_action", None)}
上次操作结果: {session.get("action_result", None)}
当前日期: {datetime.now().date()} 

### 操作空间
[1] check-weather
描述: 当用户询问天气时，使用此工具。
参数:
    - name: city
        description: 要查询天气的城市
        required: true
        example: 北京
    - name: date
        description: 要查询天气的日期，如果未提供，则使用当前日期
        required: false
        example: 2025-05-28

[2] book-hotel
描述: 当用户想要预订酒店时，使用此工具。
参数:
    - name: hotel
        description: 要预订的酒店名称
        required: true
        example: 上海希尔顿酒店
    - name: checkin_date
        description: 入住日期
        required: true
        example: 2025-05-28
    - name: checkout_date
        description: 退房日期
        required: true
        example: 2025-05-29

[3] follow-up
描述: 1. 当用户的问题超出预订酒店和查询天气的范围时，使用此工具引导用户；2. 当当前信息无法满足相应工具的参数要求时，使用此工具询问用户。
参数:
    - name: question
        description: 您对用户的引导或跟进，保持热情活泼的语言风格，并使用与用户问题相同的语言。
        required: true
        example: 您想预订哪家酒店？😊

[4] result-notification
描述: 当酒店预订或天气查询完成后，使用此工具通知用户结果并询问是否需要其他帮助。如果您发现用户的历史对话中未完成的问题，您可以在最后一步引导用户完成意图。
参数:
    - name: result
        description: 根据上次操作结果通知用户结果。保持热情活泼的语言风格，并使用与用户问题相同的语言。
        required: true
        example: 酒店已为您成功预订。😉\n\n入住日期是 XX，退房日期是 XX。感谢您的使用。您还需要其他帮助吗？😀

## 下一步操作
根据上下文和可用操作决定下一步操作。
以以下格式返回您的响应:

```yaml
thinking: |
    <您的逐步推理过程>
action: check-weather OR book-hotel OR follow-up OR result-notification
reason: <您选择此操作的原因>
question: <如果操作是 follow-up>
city: <如果操作是 check-weather> 
hotel: <如果操作是 book-hotel>
checkin_date: <如果操作是 book-hotel>
checkout_date: <如果操作是 book-hotel>
result: <如果操作是 result-notification>
```

重要提示: 确保:
1. 所有多行字段都使用正确的缩进（4 个空格）
2. 多行文本字段使用 | 字符
3. 单行字段不带 | 字符
"""

        response = call_llm(prompt.strip())
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        print(f"🤖 代理响应: \n{yaml_str}")
        decision = yaml.safe_load(yaml_str)
        return decision

    def post(self, shared, prep_res, exec_res):
        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        """保存决策并确定流程中的下一步。"""
        # 如果 LLM 决定搜索，则保存搜索查询
        session["last_action"] = exec_res["action"]
        flow_log: Queue = shared["flow_queue"]

        for line in exec_res["thinking"].split("\n"):
            line = line.replace("-", "").strip()
            if line:
                flow_log.put(f"🤔 {line}")

        if exec_res["action"] == "check-weather":
            session["check_weather_params"] = {
                "city": exec_res["city"],
                "date": exec_res.get("date", None),
            }
            flow_log.put(f"➡️ 代理决定查询 {exec_res['city']} 的天气")
        elif exec_res["action"] == "book-hotel":
            session["book_hotel_params"] = {
                "hotel": exec_res["hotel"],
                "checkin_date": exec_res["checkin_date"],
                "checkout_date": exec_res["checkout_date"],
            }
            flow_log.put(f"➡️ 代理决定预订酒店: {exec_res['hotel']}")
        elif exec_res["action"] == "follow-up":
            session["follow_up_params"] = {"question": exec_res["question"]}
            flow_log.put(f"➡️ 代理决定跟进: {exec_res['question']}")
        elif exec_res["action"] == "result-notification":
            session["result_notification_params"] = {"result": exec_res["result"]}
            flow_log.put(f"➡️ 代理决定通知结果: {exec_res['result']}")
        save_conversation(conversation_id, session)
        # 返回操作以确定流程中的下一个节点
        return exec_res["action"]


class CheckWeather(Node):
    def prep(self, shared):
        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        city = session["check_weather_params"]["city"]
        date = session["check_weather_params"].get("date", None)
        return city, date

    def exec(self, prep_res):
        city, date = prep_res
        return call_check_weather_api(city, date)

    def post(self, shared, prep_res, exec_res):
        flow_log: Queue = shared["flow_queue"]
        flow_log.put(f"⬅️ 查询天气结果: {exec_res}")

        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        session["action_result"] = exec_res
        save_conversation(conversation_id, session)
        return "default"


class BookHotel(Node):
    def prep(self, shared):
        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)

        hotel = session["book_hotel_params"]["hotel"]
        checkin_date = session["book_hotel_params"]["checkin_date"]
        checkout_date = session["book_hotel_params"]["checkout_date"]
        return hotel, checkin_date, checkout_date

    def exec(self, prep_res):
        hotel, checkin_date, checkout_date = prep_res
        return call_book_hotel_api(hotel, checkin_date, checkout_date)

    def post(self, shared, prep_res, exec_res):
        flow_log: Queue = shared["flow_queue"]
        flow_log.put(f"⬅️ 预订酒店结果: {exec_res}")

        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        session["action_result"] = exec_res
        save_conversation(conversation_id, session)
        return "default"


class FollowUp(Node):
    def prep(self, shared):
        flow_log: Queue = shared["flow_queue"]
        flow_log.put(None)

        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        question = session["follow_up_params"]["question"]
        return question, shared["queue"]

    def exec(self, prep_res):
        question, queue = prep_res
        queue.put(question)
        queue.put(None)
        return question

    def post(self, shared, prep_res, exec_res):
        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        session["action_result"] = exec_res
        return "done"


class ResultNotification(Node):
    def prep(self, shared):
        flow_log: Queue = shared["flow_queue"]
        flow_log.put(None)

        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        result = session["result_notification_params"]["result"]
        return result, shared["queue"]

    def exec(self, prep_res):
        result, queue = prep_res
        queue.put(result)
        queue.put(None)
        return result

    def post(self, shared, prep_res, exec_res):
        conversation_id = shared["conversation_id"]
        session: dict = load_conversation(conversation_id)
        session["action_result"] = None
        session["last_action"] = None
        save_conversation(conversation_id, session)
        return "done"
