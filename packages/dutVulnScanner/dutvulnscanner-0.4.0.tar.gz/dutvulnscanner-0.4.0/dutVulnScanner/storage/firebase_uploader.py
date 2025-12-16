"""Firebase Storage integration for uploading PDF reports."""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FirebaseUploadError(Exception):
    """Exception raised when Firebase upload fails."""
    pass


class FirebaseUploader:
    """
    Handle PDF report uploads to Firebase Storage.
    
    Uploads PDF files to Firebase Storage and returns public URLs.
    Organizes files by scan_id: reports/{scan_id}/report.pdf
    """
    
    def __init__(self, credentials_path: Optional[str] = None, bucket_name: Optional[str] = None):
        """
        Initialize Firebase uploader.
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            bucket_name: Firebase Storage bucket name
            
        Raises:
            FirebaseUploadError: If initialization fails
        """
        self.credentials_path = credentials_path or os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.bucket_name = bucket_name or os.getenv("FIREBASE_STORAGE_BUCKET")
        self.bucket = None
        self._initialized = False
    
    def _initialize_firebase(self):
        """
        Initialize Firebase Admin SDK.
        
        Raises:
            FirebaseUploadError: If initialization fails
        """
        if self._initialized:
            return
        
        # Check credentials file
        if not self.credentials_path:
            raise FirebaseUploadError(
                "Firebase credentials path not provided. "
                "Set FIREBASE_CREDENTIALS_PATH in .env or pass credentials_path parameter."
            )
        
        credentials_file = Path(self.credentials_path)
        if not credentials_file.exists():
            raise FirebaseUploadError(
                f"Firebase credentials file not found: {self.credentials_path}"
            )
        
        try:
            import firebase_admin
            from firebase_admin import credentials, storage
            
            # Initialize Firebase app if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(str(credentials_file))
                
                # Initialize without specifying bucket - Firebase will use default
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized without explicit bucket (will use default)")
            
            # Get storage bucket
            # If bucket_name specified, use it; otherwise use default from project
            try:
                if self.bucket_name:
                    self.bucket = storage.bucket(self.bucket_name)
                    logger.info(f"Using specified bucket: {self.bucket_name}")
                else:
                    # Try to get default bucket
                    self.bucket = storage.bucket()
                    logger.info(f"Using default bucket: {self.bucket.name}")
            except Exception as bucket_error:
                # If no default bucket, try with project_id.appspot.com format
                import json
                with open(credentials_file, 'r') as f:
                    cred_data = json.load(f)
                    project_id = cred_data.get('project_id')
                
                if project_id:
                    default_bucket = f"{project_id}.appspot.com"
                    logger.info(f"Trying default bucket name: {default_bucket}")
                    self.bucket = storage.bucket(default_bucket)
                else:
                    raise FirebaseUploadError(
                        f"Could not determine storage bucket. "
                        f"Please create a Storage bucket in Firebase Console or specify FIREBASE_STORAGE_BUCKET in .env"
                    )
            
            self._initialized = True
            logger.info(f"Firebase initialized successfully. Bucket: {self.bucket.name}")
            
        except ImportError:
            raise FirebaseUploadError(
                "firebase-admin package not found. "
                "Install it with: pip install firebase-admin"
            )
        except Exception as e:
            raise FirebaseUploadError(f"Failed to initialize Firebase: {str(e)}")
    
    def upload_pdf(
        self, 
        pdf_path: Path, 
        scan_id: str,
        custom_path: Optional[str] = None
    ) -> str:
        """
        Upload PDF file to Firebase Storage.
        
        Args:
            pdf_path: Path to PDF file to upload
            scan_id: Unique scan ID
            custom_path: Optional custom storage path (default: reports/{scan_id}/report.pdf)
            
        Returns:
            Public URL of uploaded PDF
            
        Raises:
            FirebaseUploadError: If upload fails
        """
        # Initialize Firebase if not already done
        self._initialize_firebase()
        
        # Validate PDF file
        if not pdf_path.exists():
            raise FirebaseUploadError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise FirebaseUploadError(f"File is not a PDF: {pdf_path}")
        
        try:
            # Determine storage path
            if custom_path:
                storage_path = custom_path
            else:
                storage_path = f"reports/{scan_id}/report.pdf"
            
            logger.info(f"Uploading PDF to Firebase Storage: {storage_path}")
            
            # Upload file
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(str(pdf_path), content_type='application/pdf')
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(f"PDF uploaded successfully. URL: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload PDF to Firebase: {str(e)}")
            raise FirebaseUploadError(f"Upload failed: {str(e)}")
    
    def upload_pdf_with_metadata(
        self,
        pdf_path: Path,
        scan_id: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Upload PDF with additional metadata.
        
        Args:
            pdf_path: Path to PDF file
            scan_id: Unique scan ID
            metadata: Optional metadata dict (e.g., scan target, timestamp)
            
        Returns:
            Dictionary containing:
                - url: Public URL
                - uploaded_at: Upload timestamp
                - size_bytes: File size
                - metadata: Custom metadata
        """
        # Upload PDF
        url = self.upload_pdf(pdf_path, scan_id)
        
        # Get file info
        file_size = pdf_path.stat().st_size
        
        result = {
            "url": url,
            "uploaded_at": datetime.now().isoformat(),
            "size_bytes": file_size,
            "scan_id": scan_id
        }
        
        if metadata:
            result["metadata"] = metadata
        
        return result


def upload_pdf_to_firebase(
    pdf_path: Path,
    scan_id: str,
    credentials_path: Optional[str] = None,
    bucket_name: Optional[str] = None
) -> str:
    """
    Convenience function to upload PDF to Firebase Storage.
    
    Args:
        pdf_path: Path to PDF file
        scan_id: Unique scan ID
        credentials_path: Optional path to credentials file
        bucket_name: Optional bucket name
        
    Returns:
        Public URL of uploaded PDF
        
    Raises:
        FirebaseUploadError: If upload fails
    """
    uploader = FirebaseUploader(credentials_path, bucket_name)
    return uploader.upload_pdf(pdf_path, scan_id)
