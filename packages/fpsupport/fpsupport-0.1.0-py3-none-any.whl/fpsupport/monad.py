"""An opinionated version of The Monad.

fpsupport/monad.py Copyright 2025 George Cummings

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License.

-----

Description:

Before defining a Monad, I will define "type." A "type" is any construct. For example a type could
be a scalar, a function, an object, or an object composed of scalars, functions, and other objects.

"A Monad is a monoid in the category of endofunctors, what's the problem?" - James Iry, in [A
Brief, Incomplete, and Mostly Wrong History of Programming
Languages](https://james-iry.blogspot.com/2009/05/brief-incomplete-and-mostly-wrong.html)

The definition above was Mr. Iry's inside joke, but it does have a hint of truth. Let's break it
down:

- An _endofunctor_ is a function that returns the same type as it takes in. For example, using
  python typing, the signature of an integer endofunctor would be "def my_function(x: int) -> int".
  A dict endofunctor would be "def my_function(x: dict) -> dict".

- A monoid is a collection of functions that will always return the same type.  Max Cerrina made an
  analogy on the post [Explain what a monoid is like I'm five"]
  (https://dev.to/nickytonline/explain-what-a-monoid-is-like-im-five-4gpf) in May, 2018. In short,
  he said that if you start with a pile of sticks and do things to those sticks, what do you have?
  You still have a pile of sticks. In his words, "They didn't turn into frogs."

A _monad_ is a monoid, but since it is in the class of endofunctors, its functions must accept and
return the same type. A monad has some mathematic rules. We will skip them here and just get on
with its practical application. A monad is an object that hides data and does hidden operations on
that hidden data while it processes outside ("bound") functions.

Practically, a monad is a collection of three functions:

- A _unit_ function that encapsulates a type, call it type "a" into itself, called "M a"
- Any number of "join" functions that take an outside function as one of their arguments, and
  expect type "M a" back
- An _identity_ function, which returns type "M a" with its current values.

Note that a monad does not have to be class or even a struct (in another language), just a
collection. However, through painful experience I find it better that a monad be a class, and it
accepts objects (or named tuples) as its wrapped type.
"""

# pylint: disable=unused-variable

from typing import Callable, Self, Any

from . import exception


class Monad:
    """The Monad Base Class.

    An interface to the base class. It contains the three mandatory functions,
    and it also creates aliases for the different names for those functions.

    Note that this monad has an inherent "Maybe" component: if a derived
    subclass's map() returns None, then bound execution is stopped.

    Attributes:
        There are no attributes. Any attribute will be defined by a derived
        class __init()__, and populated by the class unit() function.
    """

    def __init__(self, outer: Any = None) -> None:
        """Initializes the object with internal attributes.

        Monads are meant to be called from unit(). However, since we are using
        a Python class to represent the monad rather than a module full of
        functions, init will work just as well.

        Args:
            outer: the wrapped type

        Returns:
            This Monad

        """
        self.outer: Any = outer

    @staticmethod
    def unit(outer: Any = None) -> Self:  # type: ignore pylint: disable=undefined-variable
        """Wraps the arguments into this Monad. a -> M a.

        Also known as the type converter. Also known as pure() and return(),
        although using the latter as a function name in Python is a Bad
        Idea.™ It is one of the two "additional" functors as it is not an
        endofunctor.

        It may seem silly to return a new Monad (or subclass) rather than self,
        but one of the tenets of functional programming is immutable data.

        Args:
          outer: any object

        Returns:
          A Monad. Note that a subclassing does not work here as this is a
          static method.
        """
        return Monad(outer)

    @property
    def identity(self) -> Self:
        """Returns this Monad.

        identity() fulfills the left identity law of monads.

        Args:
            This Monad, or a sub-classed equivalent

        Returns:
            This Monad, or a sub-classed equivalent

        """
        return self

    def flat_map(self, f: Callable, *args, **kwargs) -> Self:
        """Execute _f_ with the wrapped type as the first argument.

        Unwraps the original type _outer_, sends it to self.map() for any pre-
        execution massaging, sends the result of self.map() to _f_ along with
        other arguments and returns the new Monad.

        This the second of the "additional" functions, as it is not an
        endofunctor.

        _f_ is not considered part of the monad, but makes use of the monad's
        composition properties. It _must_ return a Monad.

             ,--- unwrap   ,---- return
        M a -> (a -> M b) -> M b
                   `---- this represents the bound function

        Also known as chain, join, join_map, select, then_apply and the bind
        operator. The bind operator in Python is represented with ">>", the
        __rshift__ operator.

        Args:
            This Monad, or its sub-classed equivalent
            f: a function
            *args: additional positional arguments
            **kwargs: additional keyword arguments

        Returns:
            A Monad, or its sub-classed equivalent

        Raises:
            MonadException if the function fails to return the same type as
            the original wrapped value. Making the check is necessary in a
            duck-typed language.
        """
        result = f(self.map().outer, *args, **kwargs)
        if not isinstance(result, type(self)):
            me = str(type(self)).split("'")[1]
            raise exception.MonadException(
                f'bound function "{f.__name__}" did not return type {me}'
            )
        return result

    def map(self) -> Self:
        """A function that is run just prior to the flat_map's bound function.

        This function is not required for the definition of a monad. However,
        it allows for a defined set of repeatable operations.

        map() is meant to be overridden, so its base here is just a simple
        clone.

        Args:
            This Monad or its sub-classed equivalent

        Returns:
            A Monad or its sub-classed equivalent
        """
        return Monad.unit(self.outer)

    def final(self) -> Self:
        """Run the map by itself without calling any function.

        This is called optionally if the map needs to be run one last time. For
        example, if the map() function calls a Writer, it will write out any
        remaining buffer.

        Args:
            This Monad or its sub-classed equivalent

        Returns:
            A Monad or its sub-classed equivalent

        """
        return type(self).unit(self.map().outer)

    # Aliases
    chain = flat_map
    flatMap = flat_map
    fmap = flat_map
    join = flat_map
    join_map = flat_map
    joinMap = flat_map
    pure = unit
    select = flat_map
    then_apply = flat_map
    unwrap = identity
    __rshift__ = flat_map


# Convenience functions -----------------------------------------------------


def unwrap(m: Monad) -> Any:
    """Return the internally wrapped value of a Monad or subclass.

    It is not right to access an object's attributes directly, even if it is
    a simple "outer." One day the internal variables might change. It is better
    to use a public API. This is that API.

    Args:
        A Monad or sub-classed Monad

    Returns:
        The original wrapped value.
    """
    return m.outer
