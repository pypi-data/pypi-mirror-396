import pytest

from oop_di import ContainerDefinition, Extension
from oop_di.exception import CircularImportError, DefinitionNotFoundError


class SimpleTestService:
    ...


class DimpleTestService(SimpleTestService):
    ...


class DependentService:
    def __init__(self, simple: SimpleTestService):
        self.simple = simple


class CircularImportProblem1:
    def __init__(self, mention_it_self: "CircularImportProblem1"):
        self.mention_it_self = mention_it_self


def simple_factory(simple: SimpleTestService):
    return isinstance(simple, SimpleTestService)


class TagsInjected:
    def __init__(self, services: list[object]):
        self.count = len(services)


class InjectTagsInjected:
    def __init__(self, ti: TagsInjected):
        self.ti = ti


def simple_factory_for_tagged(tagged):
    return len(tagged)


class TestContainerDefinition:
    def setup_method(self):
        self.sut = ContainerDefinition()

    def test_it_should_compile_simple_service(self):
        self.sut.add_service(SimpleTestService)
        container = self.sut.compile()
        service = container.get(SimpleTestService)
        assert isinstance(service, SimpleTestService)

    def test_it_should_compile_named_service(self):
        self.sut.add_named_service("xxx", SimpleTestService)
        container = self.sut.compile()
        service = container.get("xxx")
        assert isinstance(service, SimpleTestService)

    def test_it_should_compile_dependent_service(self):
        self.sut.add_service(SimpleTestService)
        self.sut.add_service(DependentService)
        container = self.sut.compile()
        service = container.get(DependentService)
        assert isinstance(service, DependentService)

    def test_it_should_detect_circular_import_problem(self):
        self.sut.add_named_service("CircularImportProblem1", CircularImportProblem1)
        with pytest.raises(CircularImportError):
            self.sut.compile()

    def test_it_should_notify_if_dependency_not_registered(self):
        self.sut.add_service(DependentService)
        with pytest.raises(DefinitionNotFoundError):
            self.sut.compile()

    def test_it_should_compile_factory(self):
        self.sut.add_service(SimpleTestService)
        self.sut.add_factory("test", simple_factory)
        container = self.sut.compile()
        assert container.get("test")

    def test_it_should_compile_param(self):
        self.sut.add_param("test", "y")
        container = self.sut.compile()
        assert container.get("test") == "y"

    def test_it_should_inject_by_name_if_by_type_fails(self):
        self.sut.add_service(DependentService)
        self.sut.add_named_service("simple", SimpleTestService)
        container = self.sut.compile()
        assert isinstance(container.get(DependentService), DependentService)

    def test_it_should_inject_binding_by_name(self):
        self.sut.add_service(DependentService, simple="dimple")
        self.sut.add_service(SimpleTestService)
        self.sut.add_named_service("dimple", DimpleTestService)
        container = self.sut.compile()
        assert isinstance(container.get(DependentService).simple, DimpleTestService)

    def test_it_should_compile_aliases(self):
        self.sut.add_service(DependentService, simple="dimple")
        self.sut.add_service(SimpleTestService)
        self.sut.add_service(DimpleTestService)
        self.sut.add_alias("dimple", DimpleTestService)
        container = self.sut.compile()
        assert isinstance(container.get(DependentService).simple, DimpleTestService)

    def test_it_should_pass_singleton_flag(self):
        self.sut.add_service(SimpleTestService)
        self.sut.add_named_service("x", SimpleTestService, is_singleton=False)
        container = self.sut.compile()
        assert container.get(SimpleTestService) == container.get(SimpleTestService)
        assert container.get("x") != container.get("x")
        assert isinstance(container.get("x"), SimpleTestService)

    def test_it_should_inject_tagged_services(self):
        self.sut.add_factory("threetags", simple_factory_for_tagged, tagged="#tag1")
        self.sut.add_named_service("x", SimpleTestService, tags=["tag1", "tag2"])
        self.sut.add_named_service("y", SimpleTestService, tags=["tag1"])
        self.sut.add_named_service("z", SimpleTestService, tags=["tag1", "tag2"])
        self.sut.add_factory("twotags", simple_factory_for_tagged, tagged="#tag2")
        container = self.sut.compile()
        assert container.get("threetags") == 3
        assert container.get("twotags") == 2

    def test_it_should_build_tagged_as_deps(self):
        self.sut.add_service(InjectTagsInjected)
        self.sut.add_service(TagsInjected, services="#tag1")

        self.sut.add_service(SimpleTestService, tags=["tag1"])

        container = self.sut.compile()
        ti: InjectTagsInjected = container.get(InjectTagsInjected)
        assert ti.ti.count == 1

    def test_it_should_combine_extensions(self):
        class Ext1(Extension):
            def define(self):
                self.add_service(SimpleTestService, tags=["tag1"])

        class Ext2(Extension):
            def define(self):
                self.add_service(DependentService, tags=["tag1"])

        self.sut.add_factory("twotags", simple_factory_for_tagged, tagged="#tag1")
        self.sut.add_extension(Ext1())
        self.sut.add_extension(Ext2())

        container = self.sut.compile()
        assert isinstance(container.get(DependentService), DependentService)
        assert container.get("twotags") == 2
