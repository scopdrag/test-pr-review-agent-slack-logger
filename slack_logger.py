import json
import logging
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from logging.handlers import HTTPHandler


class SlackHandler(HTTPHandler):
    def __init__(self, url, username=None, icon_url=None, icon_emoji=None, channel=None, mention=None):
        o = urlparse(url)
        is_secure = o.scheme == 'https'
        HTTPHandler.__init__(self, o.netloc, o.path, method="POST", secure=is_secure)
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji
        self.channel = channel
        self.mention = mention and mention.lstrip('@')

    def mapLogRecord(self, record):
        text = self.format(record)

        if isinstance(self.formatter, SlackFormatter):
            payload = {
                'attachments': [
                    text,
                ],
            }
            if self.mention:
                payload['text'] = '<@{0}>'.format(self.mention)
        else:
            if self.mention:
                text = '<@{0}> {1}'.format(self.mention, text)
            payload = {
                'text': text,
            }

        if self.username:
            payload['username'] = self.username
        if self.icon_url:
            payload['icon_url'] = self.icon_url
        if self.icon_emoji:
            payload['icon_emoji'] = self.icon_emoji
        if self.channel:
            payload['channel'] = self.channel

        ret = {
            'payload': json.dumps(payload),
        }
        return ret


class SlackFormatter(logging.Formatter):
    def format(self, record):
        ret = {}
        if record.levelname == 'INFO':
            ret['color'] = 'good'
        elif record.levelname == 'WARNING':
            ret['color'] = 'warning'
        elif record.levelname == 'ERROR':
            ret['color'] = '#E91E63'
        elif record.levelname == 'CRITICAL':
            ret['color'] = 'danger'

        ret['author_name'] = record.levelname
        ret['title'] = record.name
        ret['ts'] = record.created
        ret['text'] = super(SlackFormatter, self).format(record)
        return ret


class SlackLogFilter(logging.Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:

        `logger.info("...", extra={'notify_slack': True})`
    """

    def filter(self, record):
        return getattr(record, 'notify_slack', False)
