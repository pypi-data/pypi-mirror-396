from pathlib import Path

from examples.s4_module import ProductService
from oop_di import ContainerDefinition, JsonExtension

container_definition = ContainerDefinition()
container_definition.add_extension(JsonExtension(Path(__file__).parent / "s4_config.json"))
container = container_definition.compile()


@container.inject()
def process_product_endpoint(something: str, *, product_service: ProductService) -> None:
    print(something)
    product_service.process_product()


process_product_endpoint("doing something before calling product service")
