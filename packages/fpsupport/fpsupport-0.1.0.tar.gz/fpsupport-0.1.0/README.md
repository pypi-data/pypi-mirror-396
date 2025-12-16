---
date: 2025-11-06
tags: [functional programming, python, library]
author: George Cummings
---

# Functional Programming Support

This project has three goals:

- Provide functional programming helpers up and beyond official Python functional programming
  tools
- Assist in teaching junior Python programmers functional programming
- Provide a pathway for Python programmers to more easily learn compiled, typed languages.

Do not get me wrong: I enjoy programming in Python. Its readability, libraries, and quick
development cycle is second to none. It is not tied to any programming style, be it _imperative_,
_procedural_, _object-oriented_, or functional. I am not blind, however, to programming missteps
and debugging chaos. These obstacles can be prevented by type checking and using easy-to-test,
"pure" functions.

There are, of course, many many quality Python projects creating functional tools. I encourage
developers to explore them as well and see if they suit their needs.

## Licence

The code and documentation is licensed under the Apache 2.0 licence. See [LICENCE](LICENSE).

## Installation

```sh
pip install fpsupport
```

## TL;DR

This is an example of using monads to hide IO functions.

```python
from fpsupport.jinja import load_template, render
from fpsupport.monad import Monad
from fpsupport.struct import IOType

def render_from_file(io: Monad, template_filepath: str, data: dict) -> str | None:
    """Generate a message from a jinja2 template.
    
    Any I/O Exceptions will have stopped processing and returned the error message.
    """
    result = unwrap(io.join(load_template, template_filepath).join(render, data))
    return result.contents if result.ok else result.error_msg

print(render_from_file(
    Monad(IOType()),
    "greeting.txt.j2",
    {"holiday": "Birthday", "to": "Mum", "from": "Gus"}
))
```

To see how _render_from_file_ is unit tested and how IO is dealt with without mocking, read the
[example](examples/jinja2_templating.py).

## Training Materials

Functional programming (FP) holds the promise of correct, easy to follow, and easily maintained
software. Object-oriented programming (OOP) also holds that promise. Acceptance-driven,
behaviour-driven and test- driven development along with integration testing hold programmers to a
higher quality.

All of these concepts can be difficult to comprehend without experience. My notes and other
materials are posted here as well along with their references. My intention is to provide exercises
as well.

Training materials will be published as I become more proficient at both functional programming in
Python and in documentation. In the meantime, I recommend you watch Boot Dev's [Functional
Programming Full Course](https://youtu.be/5QZYGU0C2OA?si=X6n3TtgSBZZUsiC7).

## Development and Use of this Library

The library is published in PyPi. I am using Agile principles, even as a one-man project. This
means that the software will be minimal to begin with, but guaranteed to work. As the project
continues, so grows its worth. The speed of development depends on my professional and family
work-load.

## Statement on the Use of AI

See my [Personal Policy on the Use of Artificial Intelligence](content/ai_policy.md).

## Project layout

```text
mkdocs.yml    # The configuration file.
docs/
    index.md  # The documentation homepage.
    ...       # Other markdown pages, images and other files.
examples/     # How to use the library
fpsupport/    # The library. As it expands, so will the folders
test/         # Unit testing. Functional and integration testing are not applicable.
```

## Examples

### Monads

This library includes monadic patterns such as State, Maybe and Writer monads.
In the case of the monad that I call _Pipeline_, it incorporates all three to
be used as a logged chain-of-responsibility[^1] pattern.

Of interest to a TDD[^2] enthusiast is the use of the monad for IO, used to hide
not only system calls but any other side effect or non-deterministic[^3] value
that plays havoc with the proof of a function. It is used in dependency
injection[^4], so there would be no need to use monkeypatching in unit tests.

#### Why start with Monads?

Oh my stars, you say. Monads ... are you kidding me?

When it comes to functional programming, Monads are considered advanced by most of the online
courses I remember. There are many, many tutorials on Monads on YouTube. Their quality varies. Some
lectures on them are pure Category Theory, which can be depressing to the programmer in a rush.
Others are pedantic, pushing ideology over need. Most ignore Python.

Monads are hard to explain but are so very, very useful. I am starting with Monads because I have
already used them to great visible effect on a critical, team-based project at work. I write
_visible_ because Python decorators -- effectively the definition of a higher-order function -- are
so ubiquitous as to be unnoticed.

#### Are monads Pythonic?

See [The Zen of Python](https://peps.python.org/pep-0020/).

This will be debated in the training materials once written. The answer is, quite frankly, up to
the writer. They certainly seem to add complication at first glance, violating _simple is better
than complex_. However, it enforces _explicit is better than implicit_ and, properly used, is the
epitome of _readability counts_.

## Development

```bash
make setup
```

Now you can program away without messing up my standards. For suggested VS Code plugins, see
[preferences](setup/preferences/examples/README.md).

[^1]: Refactoring.Guru. [Chain of
    Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility), retrieved
    Nov 26, 2025.

[^2]: Test-driven development, used to encourage technical correctness. It works alongside BDD
      (Behaviour-Driven Development for system behaviour), and ATDD (Acceptance Test-Driven
      Development as an Agile collaboration with stakeholders).

[^3]: For example, a random number generator.

[^4]: That is to say, converting a system call made from inside a function to an argument of that
      function.
