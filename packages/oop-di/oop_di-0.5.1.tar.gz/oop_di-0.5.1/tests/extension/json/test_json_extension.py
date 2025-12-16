from pathlib import Path

from oop_di.extension import JsonExtension
from tests.extension.json.services import Service1, Service2, Service3


class TestJsonExtension:
    def test_it_should_load_config(self):
        extension = JsonExtension(Path(__file__).parent / "config.json")

        params = extension.get_params()
        aliases = extension.get_aliases()
        services = extension.get_definitions()
        assert params == {"ololo": "trololo", "xxx": "yyy"}
        assert aliases == {"zzz": "xxx", "s2": Service2}
        service1 = services["s1"]
        service2 = services[Service2]
        service3 = services[Service3]

        assert service1.tags == ["a"]
        assert service2.tags == ["a", "b"]
        assert service3.tags == []

        assert service1.bindings == {"parameter1": "xxx"}
        assert service2.bindings == {}
        assert service3.bindings == {"parameter": Service1}
