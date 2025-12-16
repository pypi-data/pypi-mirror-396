from oop_di.service_builder import ServiceBuilder


class TestServiceBuilder:
    def test_it_should_use_factory_to_get_instance(self):
        service = ServiceBuilder(lambda: "ololo", is_singleton=True)
        assert service.get_instance() == "ololo"

    def test_it_should_cache_the_instance(self):
        service = ServiceBuilder(lambda: TestServiceBuilder(), is_singleton=True)
        assert service.get_instance() == service.get_instance()

    def test_it_should_not_cache_the_instance(self):
        service = ServiceBuilder(lambda: TestServiceBuilder(), is_singleton=False)
        assert service.get_instance() != service.get_instance()
