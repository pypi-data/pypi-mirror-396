## ScurryKit

ScurryKit is a batteries-included framework built on top of [ScurryPy](https://github.com/scurry-works/scurrypy), providing decorators, routing, structured patterns, and higher-level convenience features.

All addons in `scurry-kit/addons` are self-contained and can be reused independently in your own projects.

## Features
---
* Declarative style using decorators
* Built-in command and event routing
* Configurable caching by object type
* Unix-shell-style wildcards for component routing
* Fully compatible with raw ScurryPy (no lock-in)

## Installation

```bash
pip install scurry-kit
```

## Examples

These examples are ideal starting points:

* [Event](examples/basic_event.py)
* [Prefix](examples/basic_prefix.py)
* [Slash Command](examples/basic_command.py)

The `examples/` directory includes more advanced examples, roughly in order of increasing complexity:

* [Buttons](examples/button.py)
* [V2 Components](examples/v2_components.py)
* [Select Components](examples/select_components.py)
* [Modal](examples/modal.py)
* [Building Embeds](examples/building_embeds.py)
* [Stateful Bot](examples/stateful_bot.py)
* [Ephemeral Interaction](examples/ephemeral.py)
* [Context Menu](examples/context_menu.py)
* [Autocomplete Interaction](examples/autocomplete.py)
* [Deferred Interaction](examples/deferred.py)
* [Error Handling](examples/error_handling.py)
* [Configuring Caches](examples/configuring_cache.py)
* [Pagination](examples/pagination.py)
