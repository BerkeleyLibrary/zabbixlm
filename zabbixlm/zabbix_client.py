from zabbixlm import LastPass
from datetime import datetime, timedelta
from os import getenv
from zabbix_utils import ZabbixAPI

class ZabbixClient:
    @classmethod
    def connect_api(cls, zabbix_url=None, zabbix_token_name=None):
        if zabbix_url is None:
            zabbix_url = getenv('ZLM_ZABBIX_URL')

        if zabbix_token_name is None:
            zabbix_token_name = 'zabbix_llama_testing_token'

        zabbix_token = LastPass.get_password(zabbix_token_name)
        api = ZabbixAPI(url=zabbix_url, validate_certs=False)
        api.login(token=zabbix_token)
        return api

    def __init__(self, client: ZabbixAPI = None):
        if client is None:
            client = self.connect_api()
        self._client = client

    def get_event(self, eventid):
        try:
            return self._client.event.get(
                eventids=[eventid],
                selectHosts=['hostid', 'name', 'status'],
            )[0]
        except KeyError:
            return None

    def get_related_problems(self, event, limit=50, window_s=300):
        """Returns problems that occurred within 'window' of the given event"""
        problems = self._client.event.get(
            problem_time_from=int((datetime.fromtimestamp(int(event['clock'])) - timedelta(seconds=window_s)).timestamp()),
            problem_time_till=event['clock'],
            hostids=[h['hostid'] for h in event['hosts']],
            selectHosts=['hostid', 'name', 'status'],
            output=['clock', 'eventid', 'name', 'opdata', 'value'],
            limit=(limit + 1), # b/c the problem itself is in the list
            sortfield='clock',
            sortorder='DESC',
        )

        # Filter out duplicates
        return [p for p in problems if p['name'] != event['name']]
