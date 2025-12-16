from slack_sdk import WebClient

from ..utils import log_debug
from .notifier import BaseNotifier


class SlackNotifier(BaseNotifier):
    async def notify(self, device_id: str, event_type: str, value: int, **kwargs) -> None:
        slack_token   = kwargs.get('slack_token')
        slack_channel = kwargs.get('slack_channel')

        client = WebClient(token=slack_token)

        log_debug(f'Posting {event_type} event to Slack for device {device_id}: {value}')

        client.chat_postMessage(channel=slack_channel, text=f'Device {device_id} reported {event_type} with value {value}.')
