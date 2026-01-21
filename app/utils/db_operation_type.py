from enum import Enum 

class DbRecordLevelOperationType(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    GET_ONE = "GET_ONE"
    GET_ALL = "GET_ALL"
