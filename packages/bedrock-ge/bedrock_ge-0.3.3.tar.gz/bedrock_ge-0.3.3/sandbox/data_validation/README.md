# Data Schemas and Validation

- [pandera](https://pandera.readthedocs.io/en/stable/index.html)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [frictionless-py](https://framework.frictionlessdata.io/) implementing the [Data Package Standard](https://datapackage.org/overview/introduction/)
- [OpenAPI Specification](https://swagger.io/specification/) (Can be generated from SQLModel + FastAPI or pandera + FastAPI, right?)
- [JSON Schema](https://json-schema.org/) (Can be generated from SQLModel)
- [bSDD](https://github.com/buildingSMART/bSDD/tree/master)

One issue with the very common JSON schema, is that it's not easily possible to describe relationships between different objects. It is possible to reference another object within another object, but not to reference a specific property from another object, which is what is done in relational databases.

GI Data is actually relatively simple, and therefore it might be OK to describe GI data with JSON schema, and just use $ref to entire objects, instead of to specific fields of objects.

Moreover, GeoPackage and Speckle don't allow for relationships, because of which `project_uid`, `location_uid` and `sample_uid` columns are given the same names in both the parent and child tables.

- AGS 3 data schema: JSON schema scraped from the AGS 3.1 documentation .pdf
- AGS 4 data schema: JSON schema read from the data dictionaries (see [ags-validator](https://github.com/groundup-dev/ags-validator))
- User defined GI data schemas: JSON → Table Schema using `frictionless`
- Bedrock schema: define SQLModel → write a simple function to export to Table Schema, and generation of JSON schemas and OpenAPI documentation is easy because of the connection to FastAPI.

## Data Package Standard

[Data Package Standard Introduction | datapackage.org](https://datapackage.org/overview/introduction/)

The data package standard is a specification designed to simplify the sharing, validation, and use of data. It defines a consistent structure for organizing datasets, typically using metadata files (like datapackage.json) to describe the contents, formats, and sources of the data.

The data package standard makes datasets FAIR:

>**FAIR Data Exchange**  
>The Data Package standard facilitates findability, accessibility, interoperability, and reusability of data making it perfect for FAIR Data Exchange.

It's possible to describe relational database (RDB) schema with the Data Package Standard, which is what Bedrock uses the Data Package Standard for.

This can by done in 2 ways:

1. A single Data Package JSON with a Data Resource for each RDB table. The [`path` or `data`](https://datapackage.org/standard/data-resource/#path-or-data) properties of the Data Resource are then left empty, and the `schema` property then contains a Table Schema:
2. A Table Schema for each RDB table in a separate JSON. These JSON's then refer to each other to establish the relationships between the tables in the RDB.

Option 2. is probably better, because a data resource is supposed to contain data.

The Data Package, Data Resource, Table Schema hierarchy:

[Data Package](https://datapackage.org/standard/data-package/)  
└─[Data Resource](https://datapackage.org/standard/data-resource/)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─[Table Schema](https://datapackage.org/standard/table-schema)

An example Data Package JSON with data originating from a relational database:
[Schleswig-Holstein outdoor swimming waters | opendata.schleswig-holstein.de/data/frictionless/badegewaesser.json](https://opendata.schleswig-holstein.de/data/frictionless/badegewaesser.json)

### Why I like the Data Package Standard

- Open
- Active community and backed by the [Open Knowledge Foundation](https://okfn.org/en/)
- JSON → much more readable than XML-based standards
- Ecosystem of [Open Source Software compatible with the Data Package Standard](https://datapackage.org/overview/software/)
  - [Open Data Editor](https://opendataeditor.okfn.org/): The Open Data Editor (ODE) is an open source tool for non-technical data practitioners to explore and detect errors in tables.
  - Python package: [`frictionless-py](https://framework.frictionlessdata.io/)
