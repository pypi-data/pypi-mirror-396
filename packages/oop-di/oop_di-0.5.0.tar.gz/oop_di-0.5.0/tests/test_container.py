from oop_di import Container


class TestContainer:
    def setup_method(self):
        self.sut = Container({"x": "y"})

    def test_it_should_get_param(self):
        assert self.sut.get("x") == "y"

    def test_it_should_get_service(self):
        self.sut.add_service(Container, lambda: "lol")
        self.sut.add_service("test", lambda: "lol2")
        assert self.sut.get(Container) == "lol"
        assert self.sut.get("test") == "lol2"

    def test_it_should_resolve_alias(self):
        self.sut.add_service(Container, lambda: "lol")
        self.sut.add_alias("test", Container)
        assert self.sut.get("test") == "lol"

    def test_it_should_get_by_tags(self):
        self.sut.add_service("a", lambda: "lolA", tags=["tag1", "tag2"])
        self.sut.add_service("b", lambda: "lolB", tags=["tag1"])
        self.sut.add_service("c", lambda: "lolC", tags=["tag2"])
        assert self.sut.get_tagged("tag1") == ["lolA", "lolB"]
        assert self.sut.get_tagged("tag2") == ["lolA", "lolC"]

    def test_it_should_get_dict_by_tags(self):
        self.sut.add_service("a", lambda: "lolA", tags=["tag1", "tag2"])
        self.sut.add_service("b", lambda: "lolB", tags=["tag1"])
        self.sut.add_service("c", lambda: "lolC", tags=["tag2"])
        assert self.sut.get_tagged("#tag1") == {"a": "lolA", "b": "lolB"}
        assert self.sut.get_tagged("#tag2") == {"a": "lolA", "c": "lolC"}

    def test_it_should_inject_kwargs(self):
        self.sut.add_service(Container, lambda: "lol")

        @self.sut.inject(t="x")
        def a(s, *, y: Container, t: int, define_it):
            return [s, y, t, define_it]

        assert a("test", define_it="defined") == ["test", "lol", "y", "defined"]
