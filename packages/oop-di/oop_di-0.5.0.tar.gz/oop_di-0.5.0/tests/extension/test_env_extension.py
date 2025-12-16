import os
from unittest import mock

from oop_di.extension import EnvExtension


def mockenv(**envvars):
    return mock.patch.dict(os.environ, envvars)


class TestEnvExtension:
    @mockenv(OLOLO="TROLOLO", XXX="yyy")
    def test_it_should_add_env_as_params(self):
        sut = EnvExtension()
        params = sut.get_params()
        assert params["ololo"] == "TROLOLO"
        assert params["xxx"] == "yyy"

    @mockenv(OLOLO="TROLOLO", xxx="yyy")
    def test_it_should_add_env_as_params_without_changing_case(self):
        sut = EnvExtension(keys_to_lower=False)
        params = sut.get_params()
        assert params["OLOLO"] == "TROLOLO"
        assert params["xxx"] == "yyy"
