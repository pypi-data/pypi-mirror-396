from frictionless import Schema

# Load JSON schema
json_schema = {
    "type": "object",
    "properties": {"column1": {"type": "integer"}, "column2": {"type": "string"}},
}

# Convert JSON schema to frictionless schema
frictionless_schema = Schema.from_jsonschema(json_schema)
frictionless_schema.to_json("frictionless_schema.json")
frictionless_schema.to_excel_template("frictionless_schema.xlsx")

# Convert frictionless schema to Pandera schema
# pandera_schema = pa.from_frictionless_schema(frictionless_schema)

# Convert JSON schema to Pandera schema
# pandera_schema = pa.from_jsonschema(json_schema)
