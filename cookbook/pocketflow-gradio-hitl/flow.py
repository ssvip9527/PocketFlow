from pocketflow import Flow

from nodes import (
    DecideAction,
    CheckWeather,
    BookHotel,
    FollowUp,
    ResultNotification,
)


def create_flow():
    """
    创建并连接节点以形成完整的代理流程。
    """
    decide_action = DecideAction()
    check_weather = CheckWeather()
    book_hotel = BookHotel()
    follow_up = FollowUp()
    result_notification = ResultNotification()

    decide_action - "check-weather" >> check_weather
    check_weather >> decide_action
    decide_action - "book-hotel" >> book_hotel
    book_hotel >> decide_action
    decide_action - "follow-up" >> follow_up
    decide_action - "result-notification" >> result_notification

    return Flow(start=decide_action)
