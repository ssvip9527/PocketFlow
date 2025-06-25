import random
from datetime import date, datetime


def call_check_weather_api(city: str, date: date | None):
    if date is None:
        date = datetime.now().date()

    current_date = datetime.now().date()

    # 计算日期差
    date_diff = (date - current_date).days

    # 检查日期是否在允许的范围内
    if abs(date_diff) > 7:
        return f"Failed to check weather: Date {date} is more than 7 days away from current date."

    return f"The weather in {city} on {date} is {random.choice(['sunny', 'cloudy', 'rainy', 'snowy'])}, and the temperature is {random.randint(10, 30)}°C."


def call_book_hotel_api(hotel: str, checkin_date: date, checkout_date: date):
    current_date = datetime.now().date()

    # 检查入住日期是否在当前日期之后
    if checkin_date <= current_date:
        return (
            f"Failed to book hotel {hotel}: Check-in date must be after current date."
        )

    # 检查入住日期是否在退房日期之前
    if checkin_date >= checkout_date:
        return f"Failed to book hotel {hotel}, because the checkin date is after the checkout date."

    # 检查日期差是否超过 7 天
    date_diff = (checkout_date - checkin_date).days
    if date_diff > 7:
        return f"Failed to book hotel {hotel}: Stay duration cannot exceed 7 days."

    return f"Booked hotel {hotel} from {checkin_date.strftime('%Y-%m-%d')} to {checkout_date.strftime('%Y-%m-%d')} successfully."
