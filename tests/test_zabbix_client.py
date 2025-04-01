import pytest
from pprint import pp

def test_gets_a_problem(inode_problem_failed_webcheck):
    assert inode_problem_failed_webcheck['name'] == 'GET http://nelson.lib.berkeley.edu:8080/ FAILED'
    assert inode_problem_failed_webcheck['eventid'] == '2142364'
    assert inode_problem_failed_webcheck['clock'] == '1743533865'
    assert len(inode_problem_failed_webcheck['hosts']) == 1
    assert inode_problem_failed_webcheck['hosts'][0]['hostid'] == '10778'
    assert inode_problem_failed_webcheck['hosts'][0]['name'] == 'nelson'

def test_gets_related_problems(inode_related_problems, inode_problem_var_is_full):
    assert len(inode_related_problems) == 2
    assert next((p for p in inode_related_problems if p['eventid'] == inode_problem_var_is_full['eventid']), False)
