#generate openapi spec from RSL program
from structures.program import Program
from json import dumps

OPEN_API_VERSION = "3.0.3"

def example_for_type(t: str) -> str:
    if t == "string":
        return "example"
    elif t == "int":
        return 10
    elif t == "number":
        return 10.5
    elif t == "boolean":
        return True
    elif "[]" in t:
        ex = example_for_type(t.replace("[]", ""))
        return f"[{ex}, {ex}]"
    else:
        return "Integer ID referencing a "+t
    
def correct_type(t: str) -> str:
    if t == "string":
        return "string"
    elif t == "int":
        return "integer"
    elif t == "number":
        return "number"
    elif t == "boolean":
        return "boolean"
    elif t == "array":
        return "array"
    else:
        return "integer"


def generate_docs(p: Program) -> str:
    
    docs = {}
    docs["openapi"] = OPEN_API_VERSION
    docs["info"] = {
        "title": p.name,
        "version": "1.0.0",
        "description": "This is the OpenAPI spec for the RSL program " + p.name
    }

    docs["tags"] = []
    docs["paths"] = {}

    docs["components"] = {
            "schemas": {}
        }

    for obj in p.objects:
        docs["tags"].append({"name": obj.name, "description": f"Operations for {obj.name}"})
        docs["paths"][f"/{obj.name}/create"] = {
            "post": {
                "tags": [obj.name],
                "summary": f"Create a new {obj.name}",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{obj.name}_dehydrated"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": f"The {obj.name} was created successfully, and the new {obj.name}, along with derived fields, is returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{obj.name}"
                                }
                            }
                        }
                    }
                }
            }
        }

        docs["paths"][f"/{obj.name}/read/{{id}}"] = {
            "get": {
                "tags": [obj.name],
                "summary": f"Read a {obj.name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": f"The ID of the {obj.name} to read",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": f"The {obj.name} with the specified ID was found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{obj.name}"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": f"No {obj.name} with the specified ID was found"
                    }
                }
            }
        }

        docs["paths"][f"/{obj.name}/update/{{id}}"] = {
            "put": {
                "tags": [obj.name],
                "summary": f"Update a {obj.name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": f"The ID of the {obj.name} to update",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{obj.name}_update"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": f"The {obj.name} with the specified ID was updated successfully, and the updated {obj.name}, along with derived fields, is returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{obj.name}"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": f"No {obj.name} with the specified ID was found"
                    }
                }
            }
        }

        docs["paths"][f"/{obj.name}/delete/{{id}}"] = {
            "delete": {
                "tags": [obj.name],
                "summary": f"Delete a {obj.name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "description": f"The ID of the {obj.name} to delete",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": f"The {obj.name} with the specified ID was deleted successfully"
                    },
                    "404": {
                        "description": f"No {obj.name} with the specified ID was found"
                    }
                }
            }
        }

        docs["components"]["schemas"][obj.name] = {
            "type": "object",
            "properties": {
                "ID": {
                    "type": "integer",
                    "format": "int64",
                    "example": 10
                }
            }
        }

        docs["components"]["schemas"][obj.name +"_dehydrated"] = {
            "type": "object",
            "properties": {
                "ID": {
                    "type": "integer",
                    "format": "int64",
                    "example": 10
                }
            }
        }

        docs["components"]["schemas"][obj.name+"_update"] = {
            "type": "object",
            "properties": {
                "obj": {
                    "$ref": f"#/components/schemas/{obj.name}_dehydrated"
                }
            }
        }

        for field in obj.fields:
            docs["components"]["schemas"][obj.name]["properties"][field.name] = {
                "type":  correct_type(field.t),
                "example": example_for_type(field.t)
            }

            if not field.is_derived() and not field.is_list():
                docs["components"]["schemas"][obj.name+"_dehydrated"]["properties"][field.name] = {
                    "type":  correct_type(field.t),
                    "example": example_for_type(field.t)
                }

            if field.is_list():
                docs["components"]["schemas"][obj.name+"_update"]["properties"]["LA_"+field.name] = {
                    "type": "array",
                    "items": {
                        "type": correct_type(field.t),
                        "example": example_for_type(field.t)[1:-1]
                    }
                }
                

    return dumps(docs, indent=4)