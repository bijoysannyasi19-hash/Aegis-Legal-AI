import io
import re
from datetime import datetime
from typing import List, Dict, Any
import pypdf
import docx
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    chunk_index: int
    text: str
    document_id: str
    document_title: str
    upload_date: str
    metadata: Dict[str, Any]

class DocumentParser:
    def __init__(self):
        pass

    def _mask_pii(self, text: str) -> str:
        """
        Masks PII data such as emails, phone numbers, and full names using regex NLP heuristics.
        """
        try:
            # Scrub Emails
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
            
            # Scrub Phone Numbers (US/International standard formats)
            phone_pattern = r'(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
            text = re.sub(phone_pattern, '[PHONE REDACTED]', text)
            
            # Scrub Full Names (Basic Heuristic: Two capitalized words)
            name_pattern = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'
            text = re.sub(name_pattern, '[NAME REDACTED]', text)
            
            return text
        except Exception as e:
            print(f"Error during PII masking: {str(e)}")
            return text  # Return original if regex engine fails

    def parse_pdf(self, file_content: bytes) -> str:
        """Extracts text from PDF files safely."""
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_content))
            text_blocks = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_blocks.append(page_text)
            return "\n\n".join(text_blocks)
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")
            return ""

    def parse_docx(self, file_content: bytes) -> str:
        """Extracts text from DOCX files safely."""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            paragraphs = []
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    paragraphs.append(text)
            return "\n\n".join(paragraphs)
        except Exception as e:
            print(f"Error parsing DOCX: {str(e)}")
            return ""
        
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Splits text strictly at logical double-newline boundaries (\n\n) 
        to keep legal clauses intact.
        """
        try:
            paragraphs = text.split('\n\n')
            
            cleaned_paragraphs = []
            for p in paragraphs:
                cleaned = p.strip()
                # Replace inner single newlines with space to make the paragraph continuous
                cleaned = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned)
                if cleaned and len(cleaned) > 10:
                    cleaned_paragraphs.append(cleaned)
                    
            return cleaned_paragraphs
        except Exception as e:
            print(f"Error during chunking: {str(e)}")
            return []

    def process_document(
        self, 
        file_content: bytes, 
        filename: str, 
        document_id: str
    ) -> List[DocumentChunk]:
        """
        Processes a document, masks PII, extracts text, chunks it by paragraph,
        and appends mandatory metadata to every single chunk.
        """
        try:
            if filename.lower().endswith('.pdf'):
                text = self.parse_pdf(file_content)
            elif filename.lower().endswith('.docx'):
                text = self.parse_docx(file_content)
            else:
                raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
                
            if not text:
                return []

            # Execute PII Masking pipeline
            scrubbed_text = self._mask_pii(text)
            
            # Chunk strictly by double newlines
            paragraphs = self._split_into_paragraphs(scrubbed_text)
            
            chunks = []
            upload_date = datetime.utcnow().isoformat()
            
            for index, paragraph in enumerate(paragraphs):
                chunk = DocumentChunk(
                    chunk_index=index,
                    text=paragraph,
                    document_id=document_id,
                    document_title=filename,
                    upload_date=upload_date,
                    metadata={
                        "document_id": document_id,
                        "document_title": filename,
                        "chunk_index": index,
                        "upload_date": upload_date
                    }
                )
                chunks.append(chunk)
                
            return chunks
        except Exception as e:
            print(f"Critical error processing document {filename}: {str(e)}")
            return []
