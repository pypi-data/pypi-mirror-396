import os
from dotenv import load_dotenv
import logging
load_dotenv()

# Create and configure logger
logging.basicConfig(filename="datastore_library.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')


def DatastoreCredsLoader():
    try:
        creds = {
            "tenant_id": os.getenv("TENANT_ID"),
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "vault_url": os.getenv("VAULT_URL"),
            "azure_account_name": os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_NAME"),
            "azure_account_key": os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_KEY"),
            "azure_container_name": os.getenv("AZURE_STORAGE_DATASETS_CONTAINER_NAME"),
        }
        return creds
    except Exception as e:
        logging.error(f"Error loading datastore credentials: {e}")

 