import json
import requests


# The json schemas paths can be relative to the __init__.py file location or an URL
# example for relative_path = os.path.join(os.path.dirname(__file__), "schemas/sip-schema-d1.json")
json_schemas_paths = {
    "v1": "https://gitlab.cern.ch/digitalmemory/sip-spec/-/raw/main/versions/sip-schema-v1.json"
}


def schemas():
    """
    Retrieves every JSON schema file defined in the "schemas_path",
    reading them from disk and returning an Object
    { 'schema_name' -> schema_dict }
    """
    json_schemas = {}
    # For every schema mentioned
    for schema_name in json_schemas_paths:
        # Read the file it points to
        if json_schemas_paths[schema_name].startswith("http"):
            # If the path is a URL, make a request to retrieve the JSON schema
            response = requests.get(json_schemas_paths[schema_name])
            if response.status_code == 200:
                json_schemas[schema_name] = response.json()
        else:
            # If the path is a local file, read the JSON schema from disk
            with open(json_schemas_paths[schema_name], "r") as file:
                json_schemas[schema_name] = json.load(file)

    return json_schemas
