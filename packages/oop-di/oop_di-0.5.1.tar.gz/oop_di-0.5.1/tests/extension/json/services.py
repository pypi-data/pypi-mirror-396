class Service1:
    ...


class Service2:
    ...


class Service3:
    ...


class AgrService:
    def __init__(self, services: list[object]):
        self.count = len(services)