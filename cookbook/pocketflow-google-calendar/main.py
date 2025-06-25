from pocketflow import Flow
from nodes import CreateCalendarEventNode, ListCalendarEventsNode, ListCalendarsNode
from datetime import datetime, timedelta

def create_calendar_flow():
    """创建一个管理日历事件的流程。"""
    # 创建节点
    create_event_node = CreateCalendarEventNode()
    list_events_node = ListCalendarEventsNode()
    
    # 连接节点
    create_event_node - "success" >> list_events_node
    create_event_node - "error" >> None
    
    # 创建流程
    return Flow(start=create_event_node)

def list_calendars_flow():
    """创建一个列出所有用户日历的流程。"""
    list_calendars_node = ListCalendarsNode()
    return Flow(start=list_calendars_node)

def main():
    # 示例：列出所有日历
    print("=== 列出您的日历 ===")
    flow = list_calendars_flow()
    shared = {}
    flow.run(shared)
    
    if 'available_calendars' in shared:
        for cal in shared['available_calendars']:
            print(f"- {cal.get('summary')}")

    # 示例：创建一个简单事件
    print("\n=== 创建一个示例事件 ===")
    flow = create_calendar_flow()

    shared = {
        'event_summary': '示例会议',
        'event_description': '由 PocketFlow 创建的示例会议',
        'event_start_time': datetime.now() + timedelta(days=1),
        'event_end_time': datetime.now() + timedelta(days=1, hours=1),
        'days_to_list': 7
    }

    flow.run(shared)
    
    if 'last_created_event' in shared:
        print("事件创建成功！")
        print(f"事件 ID: {shared['last_created_event']['id']}")

if __name__ == "__main__":
    main()