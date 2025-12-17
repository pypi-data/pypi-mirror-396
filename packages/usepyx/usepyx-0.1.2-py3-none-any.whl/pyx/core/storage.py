"""
PyX Cloud Storage
Unified cloud storage abstraction with Zen Mode access.
"""
import os
import secrets
import mimetypes
from typing import Optional, List, BinaryIO, Union
from datetime import datetime, timedelta
from pathlib import Path


class StorageBackend:
    """Base class for storage backends"""
    
    def upload(self, file, path: str) -> str:
        raise NotImplementedError
    
    def download(self, path: str) -> bytes:
        raise NotImplementedError
    
    def delete(self, path: str) -> bool:
        raise NotImplementedError
    
    def exists(self, path: str) -> bool:
        raise NotImplementedError
    
    def url(self, path: str, expires: int = None) -> str:
        raise NotImplementedError
    
    def list(self, prefix: str = "") -> List[str]:
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage"""
    
    def __init__(self, base_path: str = "./uploads", base_url: str = "/uploads"):
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _full_path(self, path: str) -> Path:
        return self.base_path / path
    
    def upload(self, file, path: str = None) -> str:
        """Upload file to local storage"""
        # Handle different file types
        if hasattr(file, 'read'):
            content = file.read()
            filename = getattr(file, 'filename', None) or f"{secrets.token_hex(8)}"
        elif isinstance(file, bytes):
            content = file
            filename = f"{secrets.token_hex(8)}"
        else:
            raise ValueError("Invalid file type")
        
        # Generate path if not provided
        if not path:
            ext = Path(filename).suffix if filename else ""
            path = f"{datetime.now().strftime('%Y/%m/%d')}/{secrets.token_hex(8)}{ext}"
        
        # Ensure directory exists
        full_path = self._full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_path.write_bytes(content)
        
        return path
    
    def download(self, path: str) -> bytes:
        """Download file from local storage"""
        full_path = self._full_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_bytes()
    
    def delete(self, path: str) -> bool:
        """Delete file from local storage"""
        full_path = self._full_path(path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        return self._full_path(path).exists()
    
    def url(self, path: str, expires: int = None) -> str:
        """Get URL for file"""
        return f"{self.base_url}/{path}"
    
    def list(self, prefix: str = "") -> List[str]:
        """List files with prefix"""
        search_path = self.base_path / prefix if prefix else self.base_path
        if not search_path.exists():
            return []
        
        files = []
        for item in search_path.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(self.base_path))
                files.append(rel_path)
        return files


class S3Storage(StorageBackend):
    """Amazon S3 storage backend"""
    
    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        access_key: str = None,
        secret_key: str = None,
        endpoint_url: str = None  # For S3-compatible services like MinIO
    ):
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url
        self._client = None
        self._access_key = access_key
        self._secret_key = secret_key
    
    @property
    def client(self):
        """Lazy load boto3 client"""
        if self._client is None:
            try:
                import boto3
            except ImportError:
                raise ImportError("boto3 not installed. Run: pip install boto3")
            
            config = {
                "region_name": self.region
            }
            
            if self._access_key and self._secret_key:
                config["aws_access_key_id"] = self._access_key
                config["aws_secret_access_key"] = self._secret_key
            
            if self.endpoint_url:
                config["endpoint_url"] = self.endpoint_url
            
            self._client = boto3.client("s3", **config)
        
        return self._client
    
    def upload(self, file, path: str = None) -> str:
        """Upload file to S3"""
        # Handle different file types
        if hasattr(file, 'read'):
            content = file.read()
            filename = getattr(file, 'filename', None) or f"{secrets.token_hex(8)}"
            content_type = getattr(file, 'content_type', None)
        elif isinstance(file, bytes):
            content = file
            filename = f"{secrets.token_hex(8)}"
            content_type = None
        else:
            raise ValueError("Invalid file type")
        
        # Generate path if not provided
        if not path:
            ext = Path(filename).suffix if filename else ""
            path = f"{datetime.now().strftime('%Y/%m/%d')}/{secrets.token_hex(8)}{ext}"
        
        # Detect content type
        if not content_type:
            content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        
        # Upload to S3
        self.client.put_object(
            Bucket=self.bucket,
            Key=path,
            Body=content,
            ContentType=content_type
        )
        
        return path
    
    def download(self, path: str) -> bytes:
        """Download file from S3"""
        response = self.client.get_object(Bucket=self.bucket, Key=path)
        return response["Body"].read()
    
    def delete(self, path: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False
    
    def url(self, path: str, expires: int = 3600) -> str:
        """Get presigned URL for file"""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": path},
            ExpiresIn=expires
        )
    
    def list(self, prefix: str = "") -> List[str]:
        """List files with prefix"""
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix
        )
        return [obj["Key"] for obj in response.get("Contents", [])]


class GCSStorage(StorageBackend):
    """Google Cloud Storage backend"""
    
    def __init__(
        self,
        bucket: str,
        credentials_path: str = None
    ):
        self.bucket_name = bucket
        self.credentials_path = credentials_path
        self._client = None
        self._bucket = None
    
    @property
    def bucket(self):
        """Lazy load GCS bucket"""
        if self._bucket is None:
            try:
                from google.cloud import storage
            except ImportError:
                raise ImportError("google-cloud-storage not installed. Run: pip install google-cloud-storage")
            
            if self.credentials_path:
                self._client = storage.Client.from_service_account_json(self.credentials_path)
            else:
                self._client = storage.Client()
            
            self._bucket = self._client.bucket(self.bucket_name)
        
        return self._bucket
    
    def upload(self, file, path: str = None) -> str:
        """Upload file to GCS"""
        if hasattr(file, 'read'):
            content = file.read()
            filename = getattr(file, 'filename', None) or f"{secrets.token_hex(8)}"
        elif isinstance(file, bytes):
            content = file
            filename = f"{secrets.token_hex(8)}"
        else:
            raise ValueError("Invalid file type")
        
        if not path:
            ext = Path(filename).suffix if filename else ""
            path = f"{datetime.now().strftime('%Y/%m/%d')}/{secrets.token_hex(8)}{ext}"
        
        blob = self.bucket.blob(path)
        blob.upload_from_string(content)
        
        return path
    
    def download(self, path: str) -> bytes:
        """Download file from GCS"""
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()
    
    def delete(self, path: str) -> bool:
        """Delete file from GCS"""
        try:
            blob = self.bucket.blob(path)
            blob.delete()
            return True
        except:
            return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        blob = self.bucket.blob(path)
        return blob.exists()
    
    def url(self, path: str, expires: int = 3600) -> str:
        """Get signed URL for file"""
        blob = self.bucket.blob(path)
        return blob.generate_signed_url(expiration=timedelta(seconds=expires))
    
    def list(self, prefix: str = "") -> List[str]:
        """List files with prefix"""
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]


class ZenStorage:
    """
    Zen Mode Storage - Unified cloud storage API.
    
    Usage:
        from pyx import storage
        
        # Configure (choose one)
        storage.use_local("./uploads")
        storage.use_s3(bucket="my-bucket", region="ap-southeast-1")
        storage.use_gcs(bucket="my-bucket")
        
        # Upload
        path = storage.upload(file, folder="avatars")
        url = storage.url(path)
        
        # Download
        content = storage.download(path)
        
        # Delete
        storage.delete(path)
        
        # List files
        files = storage.list("avatars/")
    """
    
    def __init__(self):
        self._backend: StorageBackend = LocalStorage()
    
    def use_local(self, path: str = "./uploads", base_url: str = "/uploads"):
        """Use local filesystem storage"""
        self._backend = LocalStorage(path, base_url)
        return self
    
    def use_s3(
        self,
        bucket: str,
        region: str = "us-east-1",
        access_key: str = None,
        secret_key: str = None,
        endpoint_url: str = None
    ):
        """Use Amazon S3 storage"""
        self._backend = S3Storage(
            bucket=bucket,
            region=region,
            access_key=access_key,
            secret_key=secret_key,
            endpoint_url=endpoint_url
        )
        return self
    
    def use_gcs(self, bucket: str, credentials_path: str = None):
        """Use Google Cloud Storage"""
        self._backend = GCSStorage(
            bucket=bucket,
            credentials_path=credentials_path
        )
        return self
    
    def upload(self, file, folder: str = None, filename: str = None) -> str:
        """
        Upload file to storage.
        
        Args:
            file: File object, bytes, or UploadFile
            folder: Optional folder/prefix
            filename: Optional custom filename
            
        Returns:
            Path to uploaded file
        """
        path = None
        if folder and filename:
            path = f"{folder}/{filename}"
        elif folder:
            ext = ""
            if hasattr(file, 'filename') and file.filename:
                ext = Path(file.filename).suffix
            path = f"{folder}/{secrets.token_hex(8)}{ext}"
        
        return self._backend.upload(file, path)
    
    def download(self, path: str) -> bytes:
        """Download file from storage"""
        return self._backend.download(path)
    
    def delete(self, path: str) -> bool:
        """Delete file from storage"""
        return self._backend.delete(path)
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        return self._backend.exists(path)
    
    def url(self, path: str, expires: int = 3600) -> str:
        """Get URL for file"""
        return self._backend.url(path, expires)
    
    def list(self, prefix: str = "") -> List[str]:
        """List files with prefix"""
        return self._backend.list(prefix)
    
    # Aliases
    put = upload
    get = download
    remove = delete


# Zen Mode instance
storage = ZenStorage()


__all__ = [
    'storage', 'ZenStorage',
    'LocalStorage', 'S3Storage', 'GCSStorage',
    'StorageBackend'
]
