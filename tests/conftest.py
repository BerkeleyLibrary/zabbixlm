"""Shared pytest fixtures."""

import logging
import pytest
from zabbixlm import ZabbixClient

logging.basicConfig(filename='logs/tests.log', encoding='utf-8', level=logging.DEBUG)

@pytest.fixture
def zabbix_client():
    return ZabbixClient()

"""
The inode_ fixtures capture a simple concocted scenario created on the 'nelson' development server.
A web server was setup and monitored, then /var was filled up, causing the web server to crash.
Zabbix noticed the two problems in sequence: first /var filling up, then the web server failing.
This scenario is meant to capture a very simple X -> Y causal chain with essentially no confounding
data for the LLM to ignore.
"""

@pytest.fixture
def inode_problem_failed_webcheck(zabbix_client):
    return zabbix_client.get_event('2142364')

@pytest.fixture
def inode_problem_var_is_full(zabbix_client):
    return zabbix_client.get_event('2142362')

@pytest.fixture
def inode_related_problems(zabbix_client, inode_problem_failed_webcheck):
    return zabbix_client.get_related_problems(inode_problem_failed_webcheck)
