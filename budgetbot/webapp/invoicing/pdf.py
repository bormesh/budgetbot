# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import datetime
import logging
import os
import re
import shutil
import uuid

log = logging.getLogger(__name__)

class PDFManager:
    """
    Handles PDF file operations for invoices.
    """
    
    def __init__(self, config_wrapper):
        """
        Initialize the PDFManager with a config wrapper.
        
        Args:
            config_wrapper: ConfigWrapper instance with pdf_storage_path property
        """
        self.cw = config_wrapper
        self._ensure_storage_path_exists()
    
    def _ensure_storage_path_exists(self):
        """
        Create the PDF storage directory if it doesn't exist.
        """
        storage_path = self.cw.pdf_storage_path
        if not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path, exist_ok=True)
                log.info(f"Created PDF storage directory: {storage_path}")
            except Exception as e:
                log.error(f"Failed to create PDF storage directory: {e}")
                raise
    
    def _generate_filename(self, original_filename, invoice_uuid):
        """
        Generate a sanitized, unique filename for the uploaded PDF.
        
        Args:
            original_filename: Original uploaded filename
            invoice_uuid: UUID of the associated invoice
            
        Returns:
            A sanitized filename including invoice UUID and timestamp
        """
        # Extract file extension from original filename
        _, ext = os.path.splitext(original_filename)
        if not ext or ext.lower() != '.pdf':
            ext = '.pdf'  # Force PDF extension
            
        # Remove special characters from original filename
        safe_name = re.sub(r'[^\w\-\.]', '_', original_filename)
        
        # Generate timestamped filename with invoice UUID
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"invoice_{invoice_uuid}_{timestamp}{ext}"
    
    def get_file_path(self, filename):
        """
        Get the absolute file path for a stored PDF.
        
        Args:
            filename: Filename of the PDF
            
        Returns:
            Absolute path to the PDF file
        """
        return os.path.join(self.cw.pdf_storage_path, filename)
    
    def save_pdf(self, uploaded_file, original_filename, invoice_uuid):
        """
        Save an uploaded PDF file to the storage location.
        
        Args:
            uploaded_file: File-like object containing the uploaded PDF data
            original_filename: Original filename from the upload
            invoice_uuid: UUID of the associated invoice
            
        Returns:
            Saved filename
        """
        filename = self._generate_filename(original_filename, invoice_uuid)
        file_path = self.get_file_path(filename)
        
        try:
            # Save the uploaded file
            with open(file_path, 'wb') as dest:
                if hasattr(uploaded_file, 'read'):
                    # If it's a file-like object with read method
                    shutil.copyfileobj(uploaded_file, dest)
                else:
                    # If it's bytes data
                    dest.write(uploaded_file)
                    
            log.info(f"PDF saved successfully: {filename}")
            return filename
        except Exception as e:
            log.error(f"Failed to save PDF: {e}")
            raise
    
    def delete_pdf(self, filename):
        """
        Delete a PDF file from storage.
        
        Args:
            filename: Filename of the PDF to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not filename:
            return False
            
        file_path = self.get_file_path(filename)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log.info(f"PDF deleted successfully: {filename}")
                return True
            else:
                log.warning(f"PDF file not found for deletion: {filename}")
                return False
        except Exception as e:
            log.error(f"Failed to delete PDF: {e}")
            return False
    
    def get_pdf_url(self, filename):
        """
        Generate a URL for accessing the PDF.
        
        In a real application, this might generate signed URLs or
        handle authentication. For now, it just returns the relative path.
        
        Args:
            filename: Filename of the PDF
            
        Returns:
            URL path to access the PDF
        """
        if not filename:
            return None
            
        return f"/pdfs/{filename}"