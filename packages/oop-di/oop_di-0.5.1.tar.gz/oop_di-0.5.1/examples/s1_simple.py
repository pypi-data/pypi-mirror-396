from abc import ABC, abstractmethod

from oop_di import ContainerDefinition


# ### Domain code
class MailerInterface(ABC):
    @abstractmethod
    def send_mail(self) -> None:
        ...


class Mailer(MailerInterface):
    def __init__(self, from_email: str) -> None:
        self.from_email = from_email

    def send_mail(self) -> None:
        print(f"Sending from {self.from_email}...")
        print("Sent")


class ProductService:
    def __init__(self, mailer: MailerInterface) -> None:
        self.mailer = mailer

    def process_product(self) -> None:
        print("processing product")
        self.mailer.send_mail()


# ### Container definition
container_definition = ContainerDefinition()
container_definition.add_param("from_email", "test@example.com")
container_definition.add_service(ProductService)
container_definition.add_named_service(MailerInterface, Mailer)

container = container_definition.compile()


# ### Application code


@container.inject()
def process_product_endpoint_or_something(something: str, *, product_service: ProductService) -> None:
    print(something)
    product_service.process_product()


process_product_endpoint_or_something("doing something before calling product service")
