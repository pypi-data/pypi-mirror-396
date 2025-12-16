from enum import Enum

class DataSourceType(str, Enum):
    SQL = "sql"
    AZURE_DEVOPS = "azure_devops"
    SHAREPOINT = "sharepoint" 
    BLOB_STORAGE = "blob_storage"
    Dataverse = "Dataverse"