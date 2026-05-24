#from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form

from app.db.repositories.document_repo import (
    #create_document_metadata,
    delete_document_by_id,
    get_document_by_id,
    list_documents,
)
from app.schemas.document_schema import (
    DeleteDocumentResponse,
    DocumentItem,
    IngestTextRequest,
    IngestTextResponse,
    ListDocumentsResponse,
    UploadTextFileResponse,
    UploadPdfFileResponse,
    UploadDocxFileResponse,
)
# from app.services.chunker import chunk_text, chunk_pages
# from app.services.embedder import embed_texts
from app.services.vector_store import delete_document_vectors#, upsert_chunks
from app.services.pdf_parser import extract_text_from_pdf
from app.services.docx_parser import extract_text_from_docx
from app.services.document_ingestion import ingest_pages_document, ingest_text_document


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/ingest-text", response_model=IngestTextResponse)
def ingest_text(request: IngestTextRequest):
    """
    Ingest raw text into the RAG system:
    text -> chunks -> embeddings -> Pinecone -> MongoDB metadata.
    """
    try:
        result = ingest_text_document(
            text=request.text,
            title=request.title,
            user_id=request.user_id,
            source_type="text",
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return IngestTextResponse(
            document_id=result["document_id"],
            title=result["title"],
            user_id=result["user_id"],
            chunk_count=result["chunk_count"],
            message="Text ingested successfully.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Text ingestion failed: {str(exc)}",
        )


@router.post("/upload-txt", response_model=UploadTextFileResponse)
async def upload_txt_file(
    file: UploadFile = File(...),
    title: str = Form(default="Untitled TXT Document"),
    user_id: str = Form(default="demo_user"),
    chunk_size: int = Form(default=120),
    chunk_overlap: int = Form(default=30),
):
    """
    Upload a .txt file and ingest it into the RAG system.
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File name is required.",
            )

        if not file.filename.lower().endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail="Only .txt files are supported by this endpoint.",
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Could not decode file. Please upload a UTF-8 encoded .txt file.",
                )

        result = ingest_text_document(
            text=text,
            title=title,
            user_id=user_id,
            source_type="txt",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return UploadTextFileResponse(
            document_id=result["document_id"],
            title=result["title"],
            file_name=file.filename,
            user_id=result["user_id"],
            chunk_count=result["chunk_count"],
            message="TXT file uploaded and ingested successfully.",
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"TXT upload failed: {str(exc)}",
        )


@router.get("", response_model=ListDocumentsResponse)
def get_documents(
    user_id: str = Query(default="demo_user"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    List documents metadata from MongoDB.
    """
    try:
        documents = list_documents(
            user_id=user_id,
            limit=limit,
        )

        return ListDocumentsResponse(
            documents=documents,
            count=len(documents),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"List documents failed: {str(exc)}",
        )


@router.get("/{document_id}", response_model=DocumentItem)
def get_document_detail(
    document_id: str,
    user_id: str = Query(default="demo_user"),
):
    """
    Get one document metadata by document_id.
    """
    try:
        document = get_document_by_id(document_id)

        if not document or document.get("user_id") != user_id:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return document

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Get document detail failed: {str(exc)}",
        )


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(
    document_id: str,
    user_id: str = Query(default="demo_user"),
):
    """
    Delete document metadata from MongoDB and vectors from Pinecone.
    """
    try:
        document = get_document_by_id(document_id)

        if not document or document.get("user_id") != user_id:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        delete_document_vectors(
            document_id=document_id,
            user_id=user_id,
        )

        deleted = delete_document_by_id(
            document_id=document_id,
            user_id=user_id,
        )

        return DeleteDocumentResponse(
            document_id=document_id,
            user_id=user_id,
            deleted=deleted,
            message="Document deleted successfully.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Delete document failed: {str(exc)}",
        )
        
        
@router.post("/upload-pdf", response_model=UploadPdfFileResponse)
async def upload_pdf_file(
    file: UploadFile = File(...),
    title: str = Form(default="Untitled PDF Document"),
    user_id: str = Form(default="demo_user"),
    chunk_size: int = Form(default=120),
    chunk_overlap: int = Form(default=30),
):
    """
    Upload a PDF file and ingest it into the RAG system.
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File name is required.",
            )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only .pdf files are supported by this endpoint.",
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF file is empty.",
            )

        pages = extract_text_from_pdf(file_bytes)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the PDF. Scanned PDFs are not supported yet.",
            )

        result = ingest_pages_document(
            pages=pages,
            title=title,
            user_id=user_id,
            source_type="pdf",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            extra_metadata={
                "page_count": len(pages),
            },
        )

        return UploadPdfFileResponse(
            document_id=result["document_id"],
            title=result["title"],
            file_name=file.filename,
            user_id=result["user_id"],
            page_count=result["page_count"],
            chunk_count=result["chunk_count"],
            message="PDF file uploaded and ingested successfully.",
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF upload failed: {str(exc)}",
        )
        
        
@router.post("/upload-docx", response_model=UploadDocxFileResponse)
async def upload_docx_file(
    file: UploadFile = File(...),
    title: str = Form(default="Untitled DOCX Document"),
    user_id: str = Form(default="demo_user"),
    chunk_size: int = Form(default=120),
    chunk_overlap: int = Form(default=30),
):
    """
    Upload a DOCX file and ingest it into the RAG system.
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File name is required.",
            )

        if not file.filename.lower().endswith(".docx"):
            raise HTTPException(
                status_code=400,
                detail="Only .docx files are supported by this endpoint.",
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded DOCX file is empty.",
            )

        pages = extract_text_from_docx(file_bytes)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the DOCX file.",
            )

        result = ingest_pages_document(
            pages=pages,
            title=title,
            user_id=user_id,
            source_type="docx",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return UploadDocxFileResponse(
            document_id=result["document_id"],
            title=result["title"],
            file_name=file.filename,
            user_id=result["user_id"],
            chunk_count=result["chunk_count"],
            message="DOCX file uploaded and ingested successfully.",
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"DOCX upload failed: {str(exc)}",
        )