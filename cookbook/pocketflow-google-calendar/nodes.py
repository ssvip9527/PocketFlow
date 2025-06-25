from pocketflow import Node
from utils.google_calendar import create_event, list_events, list_calendar_lists
from datetime import datetime, timedelta

class CreateCalendarEventNode(Node):
    def prep(self, shared):
        """准备创建事件所需的数据。"""
        return {
            'summary': shared.get('event_summary'),
            'description': shared.get('event_description'),
            'start_time': shared.get('event_start_time'),
            'end_time': shared.get('event_end_time')
        }
    
    def exec(self, event_data):
        """创建一个新的日历事件。"""
        try:
            event = create_event(
                summary=event_data['summary'],
                description=event_data['description'],
                start_time=event_data['start_time'],
                end_time=event_data['end_time']
            )
            return {'success': True, 'event': event}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """存储事件创建结果。"""
        if exec_res['success']:
            shared['last_created_event'] = exec_res['event']
            return 'success'
        else:
            shared['error'] = exec_res['error']
            return 'error'

class ListCalendarEventsNode(Node):
    def prep(self, shared):
        """准备列出事件的参数。"""
        return {
            'days': shared.get('days_to_list', 7)
        }
    
    def exec(self, params):
        """列出日历事件。"""
        try:
            events = list_events(days=params['days'])
            return {'success': True, 'events': events}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """存储事件列表。"""
        if exec_res['success']:
            shared['calendar_events'] = exec_res['events']
            return 'success'
        else:
            shared['error'] = exec_res['error']
            return 'error'

class ListCalendarsNode(Node):
    def prep(self, shared):
        """列出日历不需要特殊准备。"""
        return {}

    def exec(self, params):
        """列出用户所有可用的日历。"""
        try:
            calendars = list_calendar_lists()
            return {'success': True, 'calendars': calendars}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post(self, shared, prep_res, exec_res):
        """将日历列表存储在共享存储中。"""
        if exec_res['success']:
            shared['available_calendars'] = exec_res['calendars']
            return 'success'
        else:
            shared['error'] = exec_res['error']
            return 'error' 