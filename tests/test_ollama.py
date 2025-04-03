import json
import os
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

def generate_noisy_causes(real_causes, noise_count=25):
    fake = Faker()
    noisy_causes = real_causes + [
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

def write_example(name, llm, scenario, diagnosis):
    try:
        os.mkdir(f'examples/{name}')
    except FileExistsError:
        pass

    with open(f'examples/{name}/scenario.json', 'w') as fh:
        json.dump(scenario, fh)

    with open(f'examples/{name}/response.md', 'w') as fh:
        fh.write(f'---\nmodel: {llm.model}\n---\n\n')
        fh.write(diagnosis.content)

def test_identifies_inode_exhaustion_in_simple_scenario(web_failure, simple_causes):
    llm = Ollama()
    diagnosis = llm.diagnose(web_failure, simple_causes)
    content = diagnosis.content.strip().lower()
    assert content.startswith('the most likely cause')
    assert 'inode' in content

@pytest.mark.parametrize('noise_count', [(25), (50)])
def test_identifies_inode_exhaustion_with_random_events(web_failure, simple_causes, noise_count):
    noisy_causes = generate_noisy_causes(simple_causes, noise_count)

    llm = Ollama()
    diagnosis = llm.diagnose(web_failure, noisy_causes)
    content = diagnosis.content.strip().lower()

    write_example(
        name=f'noisy-{noise_count}',
        llm=llm,
        scenario={ 'problem': web_failure, 'possible_causes': noisy_causes },
        diagnosis=diagnosis,
    )

    assert content.startswith('the most likely cause')
    assert 'inode' in content
