# DoD Specification Tool

This tool aims at facilitating the prototyping of Data Oriented APIs.
The system is described in a .yaml file,


## Dependencies
- graphviz (https://www.graphviz.org/)
- pyyaml (https://pyyaml.org/)

## Usage
```python3 tool.py example.yaml```

## Syntax

Knowledge about the system is specified in a yaml file.

Define a label for your system
```
Label: "DoD Design - DataFlow"

```

Define a list of inputs, 
```
Inputs:
  - "MousePosition"
```

Define a list of used components,
it lets us make some error checking (typos)
```
Components:
  - "Layout"
  - "Transform"
  - "Text"
```

Define a collection of systems:
 - System input may be *Input* or *Component*
```
Systems:
  -
    name: "System0"
    in:
      - "Layout"
      - "Transform"
    out:
      - "Transform"

  -
    name: "System1"
    depend_on: # optional
      - "System0" # let's us build the computational graph based on dependencies
    in:
      - "Transform"
    out:
      - "Transform"
```

