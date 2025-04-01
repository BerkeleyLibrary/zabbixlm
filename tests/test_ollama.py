import pytest
import random
from faker import Faker
from zabbixlm import Ollama

@pytest.fixture
def web_failure():
    return {
        "eventid": "2142364",
        "source": "0",
        "object": "0",
        "objectid": "85794",
        "clock": "1743533865",
        "value": "1",
        "acknowledged": "0",
        "ns": "203056602",
        "name": "GET http://nelson.lib.berkeley.edu:8080/ FAILED",
        "severity": "4",
        "r_eventid": "2142368",
        "c_eventid": "0",
        "correlationid": "0",
        "userid": "0",
        "cause_eventid": "0",
        "hosts": [
            {
                "hostid": "10778",
                "name": "nelson",
                "status": "0"
            }
        ],
        "opdata": "",
        "suppressed": "0",
        "urls": []
    }

@pytest.fixture
def simple_causes():
    return [
        {
            "eventid": "2142362",
            "clock": "1743533848",
            "name": "/var: Running out of free inodes (free < 10%)",
            "value": "1",
            "hosts": [
                {
                    "hostid": "10778",
                    "name": "nelson",
                    "status": "0"
                }
            ],
            "opdata": "Free inodes: 99.8962 %"
        },
        {
            "eventid": "2142341",
            "clock": "1743532828",
            "name": "/var: Running out of free inodes (free < 10%)",
            "value": "1",
            "hosts": [
                {
                    "hostid": "10778",
                    "name": "nelson",
                    "status": "0"
                }
            ],
            "opdata": "Free inodes: 99.8962 %"
        }
    ]

@pytest.fixture
def noisy_causes(simple_causes):
    fake = Faker()
    noise_count = 25
    noisy_causes = simple_causes + [
        {
            "eventid": 2142341 - i - 1,
            "clock": 1743532828 - i - 1,
            "name": fake.sentence(),
            "value": fake.ssn(),
            "hosts": [
                {
                    "hostid": str(10778 - i - 1),
                    "name": fake.name(),
                    "status": "0"
                }
            ],
            "opdata": fake.sentence()
        } for i in range(noise_count)
    ]

    # Randomize so the model can't rely on the top of the list
    # given it the right answer.
    random.shuffle(noisy_causes)

    return noisy_causes

def test_identifies_inode_exhaustion_in_simple_scenario(web_failure, simple_causes):
    llm = Ollama()
    diagnosis = llm.diagnose(web_failure, simple_causes)
    content = diagnosis.content.strip().lower()
    assert content.startswith('the most likely cause')
    assert 'inode' in content

def test_identifies_inode_exhaustion_when_there_is_random_noise(web_failure, noisy_causes):
    llm = Ollama()
    diagnosis = llm.diagnose(web_failure, noisy_causes)
    content = diagnosis.content.strip().lower()
    assert content.startswith('the most likely cause')
    assert 'inode' in content
