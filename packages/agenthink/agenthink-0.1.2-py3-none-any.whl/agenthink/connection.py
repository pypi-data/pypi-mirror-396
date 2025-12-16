# ...existing code...
import json
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from fastapi import APIRouter
import mysql.connector
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from mysql.connector import pooling
import json
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobPrefix
import pyodbc
import agenthink.utils as utils
import os
import json
import dotenv
import logging
import re
dotenv.load_dotenv()

# Create and configure logger
logging.basicConfig(
    filename="datastore_library.log",
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DBConnector:
    _class_cache = {}   # session_id -> instance

    def __init__(self, session_id: str, user_id: str, workflow_id: str):
        logger.debug("Initializing DBConnector(session_id=%s, user_id=%s, workflow_id=%s)",
                     session_id, user_id, workflow_id)

        self.session_id = session_id
        self._initialized = False
        self._workflow_id = None
        self._user_id = None
        self.connection_object_dict = {}

        self.__account_name = os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_NAME")
        self.__account_key = os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_KEY")
        self.__container_name = os.getenv("AZURE_STORAGE_DATASETS_CONTAINER_NAME")

        connection_str = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.__account_name};"
            f"AccountKey={self.__account_key};"
            f"EndpointSuffix=core.windows.net"
        )

        try:
            blob_service = BlobServiceClient.from_connection_string(connection_str)
            container_client = blob_service.get_container_client(self.__container_name)
            logger.debug("Obtained container client for container: %s", self.__container_name)
        except Exception as e:
            logger.exception("Failed to initialize BlobServiceClient or container client: %s", e)
            container_client = None

        try:
            # Fallback: if 'data' not present, log and set json_data to empty list
            if 'data' in globals():
                json_data = json.loads(data.decode("utf-8"))
            else:
                logger.warning("'data' not present in globals(), expecting blob read but none found. Using empty dataset list.")
                json_data = []
            self.no_of_datastores = len(json_data)
            secret_names = [entry["key"] for entry in json_data]
            logger.info("Found %d datastores in dataset definition.", self.no_of_datastores)
        except Exception as e:
            logger.exception("Failed to parse datastores JSON: %s", e)
            json_data = []
            self.no_of_datastores = 0
            secret_names = []

        self.__client_id = os.getenv("CLIENT_ID")
        self.__tenant_id = os.getenv("TENANT_ID")
        self.__client_secret = os.getenv("CLIENT_SECRET")
        self.__vault_url = os.getenv("VAULT_URL")

        for dict_creds in json_data:
            try:
                cleaned_key = self.sanitize_secret_name(dict_creds["key"])
                datastore_type = dict_creds.get("datastore_type")
                name = dict_creds.get("name")
                logger.debug("Processing datastore: name=%s, key=%s, type=%s",
                             name, dict_creds.get("key"), datastore_type)
            except Exception as e:
                logger.exception("Malformed datastore entry: %s", e)
                continue

            try:
                credential = ClientSecretCredential(
                    tenant_id=self.__tenant_id,
                    client_id=self.__client_id,
                    client_secret=self.__client_secret
                )

                client = SecretClient(vault_url=self.__vault_url, credential=credential)
                secret_value = client.get_secret(cleaned_key)
                secret = json.loads(secret_value.value)
            except Exception as e:
                logger.exception("Failed to fetch or parse secret for key '%s': %s", cleaned_key, e)
                continue

            # MySQL connection
            if datastore_type == "mysql":
                try:
                    connection_object = self.__connect_mysql(secret)
                    if connection_object:
                        db_name = secret.get("database_name", "unknown")
                        self.connection_object_dict[f"{db_name}"] = connection_object
                        logger.info("Added MySQL connection for database '%s' to connection_object_dict", db_name)
                except Exception as e:
                    logger.exception("Unable to create connection object for MySQL secret: %s", e)

            # MS SQL connection
            elif datastore_type == "mssql":
                try:
                    connection_object = self.__connect_mssql(secret)
                    if connection_object:
                        db_name = secret.get("database_name", "unknown")
                        self.connection_object_dict[f"{db_name}"] = connection_object
                        logger.info("Added MSSQL connection for database '%s' to connection_object_dict", db_name)
                except Exception as e:
                    logger.exception("Unable to create connection object for MSSQL secret: %s", e)
            else:
                logger.warning("Unsupported datastore_type '%s' for key '%s'", datastore_type, cleaned_key)

    # ---- class method to create instance ----
    @classmethod
    def get(cls, session_id: str, user_id: str, workflow_id: str):
        if session_id not in cls._class_cache:
            logger.debug("Creating new DBConnector instance for session_id=%s", session_id)
            cls._class_cache[session_id] = DBConnector(session_id, user_id, workflow_id)
        else:
            logger.debug("Returning cached DBConnector instance for session_id=%s", session_id)
        return cls._class_cache[session_id]

    # ---- public method ----
    def execute(self, query: str, workflow_id: str, user_id: str):
        logger.debug("execute called: session=%s, workflow=%s, user=%s, query=%s",
                     self.session_id, workflow_id, user_id, query)
        if not self._initialized:
            self._workflow_id = workflow_id
            self._user_id = user_id
            self._initialized = True
            logger.debug("DBConnector initialized for workflow_id=%s user_id=%s", workflow_id, user_id)

        return {
            "session": self.session_id,
            "workflow": self._workflow_id,
            "user": self._user_id,
            "query": query
        }

    def __connect_mysql(self, secret):
        config = {
            "host": secret.get("cluster_ip"),
            "port": secret.get("port"),
            "user": secret.get("username"),
            "password": secret.get("password"),
            "database": secret.get("database_name")
        }

        # Log connection info without the password
        logger.debug("Trying MySQL connection: host=%s port=%s user=%s database=%s",
                     config["host"], config["port"], config["user"], config["database"])

        try:
            conn = mysql.connector.connect(**config)
            logger.info("MySQL connection successfully established to database '%s' on host '%s'",
                        config["database"], config["host"])
            return conn
        except Exception as e:
            logger.exception("MySQL connection failed: %s", e)
            return None

    def __connect_mssql(self, secret):
        # Use single quotes inside f-strings to avoid syntax errors
        connection_string = (
            f"mssql+pyodbc://{secret.get('username')}:{secret.get('password')}@{secret.get('cluster_ip')}:{secret.get('port')}/{secret.get('database_name')}"
            "?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=no"
        )
        logger.debug("Trying MSSQL connection for host=%s port=%s user=%s db=%s",
                     secret.get("cluster_ip"), secret.get("port"), secret.get("username"), secret.get("database_name"))
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            # Fetch a row only if we can; wrap safely:
            try:
                row = cursor.fetchone()
                if row:
                    logger.info("Connected to MSSQL. Sample row/first column: %s", row[0])
                else:
                    logger.info("Connected to MSSQL. No rows returned by initial fetch.")
            except Exception:
                logger.debug("No initial row fetch possible or returned no results.")
            return conn
        except Exception as e:
            logger.exception("MS SQL Connection failed: %s", e)
            return None

    def sanitize_secret_name(self, secret_name: str) -> str:
        """
        Convert secret name to a valid Azure Key Vault format:
        - Replaces spaces and underscores with hyphens
        - Removes any characters not allowed in Key Vault secret names
        """
        logger.debug("Sanitizing secret name: %s", secret_name)
        # Replace spaces and underscores with hyphens
        sanitized = re.sub(r"[ _]+", "-", secret_name)

        # Remove any characters that are not letters, numbers, or hyphens
        sanitized = re.sub(r"[^a-zA-Z0-9\-]", "", sanitized)

        logger.debug("Sanitized secret name: %s -> %s", secret_name, sanitized)
        return sanitized
# ...existing code...