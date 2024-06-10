import os
import json
import codecs
import firebase_admin
from loguru import logger
from firebase_admin import credentials, storage


# Load Firebase admin credentials and initialize app
def load_credentials() -> None:
    credentials = {
        "type": "service_account",
        "project_id": os.environ["project_id"],
        "private_key_id": os.environ["private_key_id"],
        "private_key": codecs.decode(os.environ["private_key"], "unicode_escape"),
        "client_email": os.environ["client_email"],
        "client_id": os.environ["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ["client_x509_cert_url"],
        "universe_domain": "googleapis.com"
    }
    with open("secret.json", "w") as file:
        json.dump(credentials, file, indent=4)
        
load_credentials()        
cred = credentials.Certificate("secret.json")
firebase_admin.initialize_app(cred)
        

def download_firebase_folder(bucket: str, firebase_folder: str, local_folder: str) -> None:
    """
    Downloads all files from a specified folder in Firebase Cloud Storage to a local folder.

    Args:
        bucket (str): The name of the Firebase storage bucket.
        firebase_folder (str): The folder path in Firebase Cloud Storage.
        local_folder (str): The path to the local folder where files will be downloaded.

    Returns:
        None
    """
    firebase_bucket = storage.bucket(bucket)
    blobs = firebase_bucket.list_blobs(prefix=firebase_folder)
    for blob in blobs:
        try:
            local_file_path = os.path.join(local_folder, os.path.basename(blob.name))
            blob.download_to_filename(local_file_path)
            logger.info(f"Downloaded file: {blob.name}")
            
        except Exception as e:
            logger.error(f"Error while downloading file: {blob.name}")
            pass

def download_firebase_file(
    bucket: str, firebase_filename: str, local_filename: str
) -> None:
    """
    Downloads a file from the local filesystem to Firebase Cloud Storage.

    Args:
        bucket (str): The name of the Firebase storage bucket.
        firebase_filename (str): The desired name of the file in Firebase Cloud Storage.
        local_filename (str): The path to the local file to be downloaded.

    Returns:
        None
    """
    firebase_bucket = storage.bucket(bucket)
    blob = firebase_bucket.blob(firebase_filename)
    blob.download_to_filename(local_filename)
    logger.info(f"Downloaded file {local_filename}")


def upload_firebase_file(
    bucket: str, firebase_filename: str, local_filename: str
) -> None:
    """
    Uploads a file from the local filesystem to Firebase Cloud Storage.

    Args:
        bucket (str): The name of the Firebase storage bucket.
        firebase_filename (str): The desired name of the file in Firebase Cloud Storage.
        local_filename (str): The path to the local file to be uploaded.

    Returns:
        None
    """
    firebase_bucket = storage.bucket(bucket)
    blob = firebase_bucket.blob(firebase_filename)
    blob.upload_from_filename(local_filename)
    logger.info(f"Uploaded file {local_filename}")

    
