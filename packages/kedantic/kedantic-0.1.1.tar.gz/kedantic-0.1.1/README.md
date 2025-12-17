# Kedantic

## Overview

Kedantic allows you to specify Pydantic models as parameter inputs
to your kedro nodes.
This has the following benefits

1. Offload parameter validation to Pydantic
2. Make unit testing of nodes simpler, due to point 1.
3. Better type hinting than generic dictionaries when working in an IDE with a lsp

## Installation

To install, simply run

```bash
pip install kedantic
```

## Use

To utilize, simply annotate your node's function parameters with pydantic models and kedantic
will take care of the rest. Kedantic will only automatically validate inputs that
are parameters into a node, i.e. the inputs name must start with "params:" on the
pipeline definition.
