from enum import Enum


class RevisionColumns(Enum):
    object_path = "Imx Object Path"
    object_puic = "Puic of object for revision"
    issue_comment = "What is the issue"
    issue_cause = "What is the cause of the issue"
    attribute_or_element = "The attribute or element path"
    operation = "Type of revision operation"
    value_old = "Old value that is being checked if it is still like this"
    value_new = "Revision Value"
    processing_status = "Boolean If revision need to be processed"
    revision_reasoning = "Revision reasoning, why this value, or why not to revision?"


class RevisionOperationValues(Enum):
    CreateAttribute = "Create a new attribute"
    UpdateAttribute = "Update an existing attribute"
    DeleteAttribute = "Remove an attribute"
    DeleteObject = "Delete the entire object"
    AddElementUnder = "Add an element under a parent"
    DeleteElement = "Remove an element from structure"
