# nadap

**N**amespace **A**ware **D**ata V**a**lidator and **P**re-processor

## Introduction

This Python module provides data validation against a data schema.
The data schema describes the structure, the data types and
all value limitations which a given data must match.

In addition data values at defined points within the data schema
can be referenced among each other. They can be tested on uniqueness
or if at some point in the data a value (consumer) is the same
value that is located at another point in data (producer).

Furthermore, input data can be enriched with default values or values
can be converted (i.e. into another data type).

## Documentation

A documentation about the concept, features, data types, API details
and examples can be found at
[Read the Docs](https://nadap.readthedocs.io/).

## License

This project is licensed under GPLv3.
See LICENSE file within this project.

## Contributing

The source code development is hosted at
[GitLab.com](https://gitlab.com/ko.no/nadap).
