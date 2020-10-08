# -*- coding:utf-8; -*-
import json
import typing

from redis import Redis

from .base import BaseStorage


class RedisStorage(BaseStorage):
    """
    Storage based on Redis
    """

    def close(self):
        self._redis.close()

    def __init__(self,
                 host: typing.Optional[typing.AnyStr] = 'localhost',
                 port: typing.Optional[int] = 6379,
                 db: typing.Optional[int] = 1,
                 password: typing.Optional[typing.AnyStr] = None,
                 url: typing.Optional[typing.AnyStr] = None,
                 **kwargs):
        if url:
            self._redis = Redis.from_url(url)
        else:
            self._redis = Redis(host=host, port=port, db=db, password=password, **kwargs)

    def _get_record(self, *,
                    chat: typing.Union[str, int, None] = None,
                    user: typing.Union[str, int, None] = None) -> typing.Dict:
        """
        Get record from storage
        :param chat:
        :param user:
        :return:
        """
        chat, user = self.check_address(chat=chat, user=user)
        addr = f"fsm:{chat}:{user}"

        data = self._redis.get(addr)
        if data is None:
            return {'state': None, 'data': {}}
        return json.loads(data)

    def _set_record(self, *, chat: typing.Union[str, int, None] = None, user: typing.Union[str, int, None] = None,
                    state=None, data=None) -> typing.Dict:
        """
        Write record to storage
        :param bucket:
        :param chat:
        :param user:
        :param state:
        :param data:
        :return:
        """
        if data is None:
            data = {}

        chat, user = self.check_address(chat=chat, user=user)
        addr = f"fsm:{chat}:{user}"

        record = {'state': state, 'data': data}
        self._redis.set(addr, json.dumps(record))

    def get_state(self, chat: typing.Union[int, str, None] = None, user: typing.Union[int, str, None] = None,
                  default: typing.Optional[str] = None) -> typing.Union[str]:
        record = self._get_record(chat=chat, user=user)
        return record['state'] or default

    def get_data(self,
                 chat: typing.Union[int, str, None] = None,
                 user: typing.Union[int, str, None] = None,
                 default: typing.Optional[str] = None) -> typing.Dict:
        """
        Get data for user in chat
        :param chat: Chat id
        :param user: User id
        :param default: Returns if no data.
        :return: User data
        """
        record = self._get_record(chat=chat, user=user)['data']
        return record

    def set_state(self, chat: typing.Union[int, str, None] = None, user: typing.Union[int, str, None] = None,
                  state: typing.Optional[typing.AnyStr] = None):
        record = self._get_record(chat=chat, user=user)
        self._set_record(chat=chat, user=user, state=state, data=record['data'])

    def set_data(self, chat: typing.Union[int, str, None] = None, user: typing.Union[int, str, None] = None,
                 data: typing.Dict = None):
        record = self._get_record(chat=chat, user=user)
        self._set_record(chat=chat, user=user, state=record['state'], data=data)

    def update_data(self, chat: typing.Union[int, str, None] = None, user: typing.Union[int, str, None] = None,
                    data: typing.Dict = None, **kwargs):
        if data is None:
            data = {}
        record = self._get_record(chat=chat, user=user)
        record_data = record.get('data', {})
        record_data.update(data, **kwargs)
        self._set_record(chat=chat, user=user, state=record['state'], data=record_data)
