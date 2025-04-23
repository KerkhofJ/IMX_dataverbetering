from enum import Enum

class RevisionColumns(Enum):
    ObjectPath = "Imx Object Path"
    ObjectPuic = "Puic of object for revision"
    IssueComment = "What is the issue"
    IssueCause = "What is the cause of the issue"
    AtributeOrElement = "The attribute or element path"
    Operation = "Type of revision operation"
    ValueOld = "Old value that is being checked if it is still like this"
    ValueNew = "Revision Value"
    ProcessingStatus = "Boolean If revision need to be processed"
    RevisionReasoning = "Revision reasoning, why this value, or why not to revision?"

class RevisionOperationValues(Enum):
    CreateAttribute = "Create a new attribute"
    UpdateAttribute = "Update an existing attribute"
    DeleteAttribute = "Remove an attribute"
    DeleteObject = "Delete the entire object"
    AddElementUnder = "Add an element under a parent"
    DeleteElement = "Remove an element from structure"
