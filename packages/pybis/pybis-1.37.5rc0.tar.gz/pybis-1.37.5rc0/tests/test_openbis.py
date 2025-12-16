#   Copyright ETH 2018 - 2024 Zürich, Scientific IT Services
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import json
import random
import re

import pytest
import time
from pybis import DataSet
from pybis import Openbis


def test_token(openbis_instance):
    assert openbis_instance.token is not None
    assert openbis_instance.is_token_valid(openbis_instance.token) is True
    assert openbis_instance.is_session_active() is True


### Temporarily disabled
# def test_http_only(openbis_instance):
#     with pytest.raises(Exception):
#         new_instance = Openbis("http://localhost")
#         assert new_instance is None
#
#     new_instance = Openbis(
#         url="http://localhost",
#         allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks=True,
#     )
#     assert new_instance is not None


def test_cached_token(other_openbis_instance):
    assert other_openbis_instance.is_token_valid() is True

    other_openbis_instance.logout()
    assert other_openbis_instance.is_token_valid() is False


def test_create_permId(openbis_instance):
    permId = openbis_instance.create_permId()
    assert permId is not None
    m = re.search("([0-9]){17}-([0-9]*)", permId)
    ts = m.group(0)
    assert ts is not None
    count = m.group(1)
    assert count is not None

def test_openbis():
    def get_instance():
        base_url = "http://localhost:8888/openbis-test"
        # base_url = "https://localhost:8443/openbis"
        # base_url = "https://openbis-sis-ci-sprint.ethz.ch/"
        # base_url = "https://local.openbis.ch/openbis"
        openbis_instance = Openbis(
            url=base_url,
            verify_certificates=False,
            allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks=True
        )
        token = openbis_instance.login('admin', 'changeit')
        print(token)
        return openbis_instance

    o = get_instance()



    print("DONE")