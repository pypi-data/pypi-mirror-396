Intro
===

Dependency Injection is the key pattern used to implement Inversion of Control and Dependency Inversion principles 
(check D in SOLID).

It makes it simple to standardize the way objects are initialized in the application.

This package provides you with the set of components to automate dependency injection through the application.

Installation
===

Add `oop-di` as a dependency in `pyproject.toml` of your project. Or, do

`pip install oop-di`

Usage
===

To make it work do the following steps:

- provide definitions for all the services
- compile the container
- use container to inject services

```python
# Init the `ContainerDefinition` component
container_definition = ContainerDefinition()
# fill the service definitions
container_definition.add_service(SomeService)
# compile the container
container = container_definition.compile()

# get an instance of the service from the container ...
service = container.get(SomeService)

# ... or inject it. Kwonly arguments will be injected
@container.inject()
def something(*, service: SomeService):
    ...

something()

# partial injection is also possible
def something_else(*, wont_inject: UnknownService, service: SomeService):
    ...

something_else(wont_inject=UnknownService())
```

Extensions
===

EnvExtension
---

You can add all environment variables to your container by adding `EnvExtension` to the container definition:

```python
container_definition = ContainerDefinition()
container_definition.add_extension(EnvExtension())
```

JsonExtension
---

You can add define parameters/aliases/services in a JSON file.
Check `examples/s4_json.py` for more details.

```python
container_definition = ContainerDefinition()
container_definition.add_extension(JsonExtension(Path(__file__).parent / "config.json"))
```

Config example:

```json
{
  "parameters": {
    "test1_email": "test@example.com",
    "test2_email": "test2@example.com",
    "test3_email": "test3@example.com"
  },
  "services": {
    "examples.s4_module": [
      {"class": "ProductService"},
      {"class": "Mailer", "name": "m1","tags": ["admin_mailers"], "parameters": {"from_email": "test1_email"}},
      {"class": "Mailer", "name": "m2","tags": ["admin_mailers"], "parameters": {"from_email": "test2_email"}},
      {"class": "Mailer", "name": "m3","tags": ["admin_mailers"], "parameters": {"from_email": "test3_email"}},
      {"class": "MultiMailer", "name": "@examples.s4_module.MailerInterface","parameters": {"mailers": "#admin_mailers"}}
    ]
  }
}
```


Why not `python-dependency-injector`?
===

`python-dependency-injector` is the most popular Python DI library with a large community, excellent docs, and tons
of features that are not available in `oop-di`. Probably, `python-dependency-injector` is the best choice for you.
I've built this small library to handle the DI of my small experiments/pet projects.

What I don't like in `python-dependency-injector` and tried to mitigate in this library:

- it requires a name for every service. `oop-di` can use class itself as the name of the service;
- it makes you pollute your function's params with ` = Provide[Container.service]` defaults to inject something. 
`oop-di` just auto-wires the services by checking the parameter's types;
- `oop-di` has the tagging feature that can gather services into an array without an explicit definition of that array.


Check `examples/` folder for more info:

- `s1_simple.py` - shows the basics: how to define services and how to inject the services somewhere.
- `s2_extensions.py` - how to split the definitions between modules.
- `s3_tags.py`, `s3_tags2_dict.py` - how to use tags to group services (list or dict grouping is possible).
- `s4_json.py` - JsonExtension usage example.