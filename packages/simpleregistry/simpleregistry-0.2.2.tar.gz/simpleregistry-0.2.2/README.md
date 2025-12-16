simpleregistry
==============

Simple registries in Python.

Right now supports only object registries, but class registries are coming in the future releases:

```python
import dataclasses

import simpleregistry


book_registry = simpleregistry.Registry('books')


@book_registry
@dataclasses.dataclass
class Book:
    isbn: int
    title: str
    author: str
    
    def __hash__(self) -> int:
        return hash(self.isbn)


lord_of_the_rings = Book(123, 'The Lord of the Rings', 'J. R. R. Tolkien')

assert lord_of_the_rings in book_registry
assert len(book_registry) == 1
assert book_registry.all() == {lord_of_the_rings}
assert book_registry.get(isbn=123) == lord_of_the_rings
assert book_registry.filter(author='J. R. R. Tolkien') == {lord_of_the_rings}
assert book_registry.exclude(author='J. R. R. Tolkien') == set()
```

Works with custom types, standard-library dataclasses and Pydantic. See tests for examples.

This project is currently in Alpha status. You are welcome to use it. Code should be stable, but the API may change.


Registries and Type Constraints
-------------------------------

By default, registries allow for limited polymorphism. This means that if you register one type with a registry, 
any instances of its subclasses will also be registered:

```python
import simpleregistry


publication_registry = simpleregistry.Registry('publications')


@publication_registry
class Book:
    pass


class Magazine(Book):
    pass


book = Book()
magazine = Magazine()

assert book in publication_registry
assert magazine in publication_registry
```

If this is not desired, you can use the `allow_subclasses` argument to the `Registry` constructor:

```python
import simpleregistry


publication_registry = simpleregistry.Registry('publications', allow_subclasses=False)


@publication_registry
class Book:
    pass


class Magazine(Book):
    pass


book = Book()
magazine = Magazine()

assert book in publication_registry
assert magazine not in publication_registry
```

If you want to be able to register multiple related or unrelated types, 
you can use the `allow_polymorphism` argument to the `Registry` constructor:

```python
import simpleregistry


publication_registry = simpleregistry.Registry('publications', allow_polymorphism=True)


@publication_registry
class Book:
    pass


@publication_registry
class Magazine:
    pass


book = Book()
magazine = Magazine()

assert book in publication_registry
assert magazine in publication_registry
```

If you want to further relax the type constraints, you can use the `check_type` argument. This will allow you to force
any types of objects into the registry:

```python
import simpleregistry


publication_registry = simpleregistry.Registry('publications', check_type=False)


@publication_registry
class Book:
    pass


class Magazine:
    pass


# Book will be registered automatically
book = Book()
assert book in publication_registry

# Magazine will not be registered automatically
magazine = Magazine()
assert magazine not in publication_registry

# You can, however, register it manually
publication_registry.register(magazine)
assert magazine in publication_registry
```


Integrations
------------

### Pydantic

Pydantic models are supported out of the box, provided you make them hashable.
One way of doing that is by using the `frozen` option:

```python
import pydantic
import simpleregistry


publication_registry = simpleregistry.Registry('publications', check_type=False)


@publication_registry
class Book(pydantic.BaseModel):
    isbn: int
    title: str

    class Config:
        frozen = True


book = Book(isbn=123, title='The Lord of the Rings')
assert book in publication_registry
```

Another option is to write a custom hash function, which can for example return the int value of the primary key:

```python
import pydantic
import simpleregistry


publication_registry = simpleregistry.Registry('publications', check_type=False)


@publication_registry
class Book(pydantic.BaseModel):
    isbn: int
    title: str

    def __hash__(self) -> int:
        return self.isbn
        
        
book = Book(isbn=123, title='The Lord of the Rings')
assert book in publication_registry
``` 
