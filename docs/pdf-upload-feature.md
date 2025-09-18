# PDF Upload Feature Documentation

## Overview

The PDF Upload feature allows users to attach PDF files to invoices, store them on the server, and view them directly from the web interface. This feature is designed to support the use case where users generate invoice PDFs externally and want to store them with the invoice record in the system.

## Configuration

The PDF storage location is configured in the application's YAML configuration files:

```yaml
app:
    # Other app settings...
    pdf_storage_path: /path/to/pdf/storage
```

The system uses the following defaults:
- Development: `/tmp/budgetbot/pdfs`
- Production: `/var/lib/budgetbot/pdfs`

## Implementation Details

### Components

1. **ConfigWrapper Extension**
   - Added `pdf_storage_path` property to access the configured storage location
   - Provides a default fallback path if not specified in config

2. **PDF Manager**
   - Core class that handles PDF file operations
   - Ensures storage directory exists
   - Manages file naming, saving, deletion, and URL generation
   - Sanitizes filenames for security

3. **API Endpoints**
   - `POST /api/invoices/{uuid}/upload-pdf` - Upload a PDF file
   - `POST /api/invoices/{uuid}/delete-pdf` - Delete an attached PDF
   - `GET /pdfs/{filename}` - Serve a PDF file

4. **UI Integration**
   - Added PDF upload field to invoice form
   - Display view/delete controls for existing PDFs
   - File type validation (.pdf only)

### File Storage

PDFs are stored with sanitized filenames that include:
- Invoice UUID
- Timestamp
- Original filename (sanitized)

Example: `invoice_123e4567-e89b-12d3-a456-426614174000_20250526_110523.pdf`

### Security Considerations

1. **File Type Validation**
   - Server-side validation ensures only PDF files are accepted
   - Client-side validation via `accept=".pdf"` attribute

2. **Path Sanitization**
   - Prevents directory traversal attacks
   - Removes special characters from filenames

3. **Access Control**
   - All PDF endpoints require authentication
   - Same permissions as invoice access

## Usage Flow

1. **Uploading a PDF**
   - When creating/editing an invoice, user selects a PDF file
   - File is uploaded via AJAX before form submission
   - On successful upload, the PDF path is stored in the invoice record

2. **Viewing a PDF**
   - Users can view PDFs directly in the browser
   - PDF viewer opens in a new tab via the "View PDF" button

3. **Deleting a PDF**
   - Users can delete attached PDFs via the "Delete PDF" button
   - This removes both the file from disk and the reference from the invoice

## Future Enhancements

1. **PDF Generation**
   - Automatic PDF generation from invoice data
   - Customizable PDF templates

2. **Multiple Files**
   - Support for attaching multiple files to an invoice
   - Additional file types beyond PDFs

3. **File Compression**
   - Optimize PDFs for storage
   - Implement file size limits

4. **Advanced Security**
   - Document encryption
   - Access logging for sensitive documents