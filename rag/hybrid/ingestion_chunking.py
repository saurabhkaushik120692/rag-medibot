from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker
from transformers import AutoTokenizer
from docling.document_converter import DocumentConverter
# from docling_core.transforms.chunker import HierarchicalChunker
# from hierarchical.postprocessor import ResultPostprocessor

# 1. Access Roles Mapping configuration
ROLE_ACCESS_MAPPING = {
    "general": ["doctor", "admin", "nurse", "billing_executive", "technician"],
    "clinical": ["doctor", "admin"],
    "nursing": ["nurse", "doctor", "admin"],
    "billing": ["billing_executive", "admin"],
    "equipment": ["technician", "admin"]
}

def determine_chunk_type(chunk) -> str:
    """Classifies a chunk based on its constituent document items."""
    labels = {item.label for item in chunk.meta.doc_items if hasattr(item, "label")}
    
    # Check for table items
    if any("table" in str(label).lower() for label in labels):
        return "table"
    # Check for code items
    if any("code" in str(label).lower() for label in labels):
        return "code"
    # Check for heading/header items
    if any("header" in str(label).lower() or "title" in str(label).lower() for label in labels):
        return "heading"
    
    return "text"

def process_data_directory(data_dir_path: str, embed_model: str):
    data_dir = Path(data_dir_path)
    
    # Configure Docling Converter
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    tokenizer = AutoTokenizer.from_pretrained(embed_model)
    chunker = HybridChunker(
                            tokenizer=tokenizer,
                            max_tokens=256,
                            merge_peers=True
                            )
    # chunker   = HierarchicalChunker()

    data = []
    # Supported formats
    supported_extensions = {".pdf", ".md"}
    
    # Iterate through all files in subfolders of 'data/'
    for filepath in data_dir.glob("**/*"):
        if filepath.is_file() and filepath.suffix.lower() in supported_extensions:
            # 2. Extract Collection from the immediate parent subfolder name
            collection_name = filepath.parent.name.lower()
            
            # Ensure it is a valid collection we support
            if collection_name not in ROLE_ACCESS_MAPPING:
                print(f"Skipping file {filepath.name} because subfolder '{collection_name}' is not a recognized collection.")
                continue
            
            # Resolve access roles for this collection
            access_roles = ROLE_ACCESS_MAPPING[collection_name]
            source_document = filepath.name
            
            print(f"Processing: {source_document} | Collection: {collection_name} | Roles: {access_roles}")
            
            # Convert file using Docling
            try:
                result = converter.convert(filepath)
                doc = result.document

                # converter = DocumentConverter()
                # result = converter.convert(filepath)
                # ResultPostprocessor(result).process()
                # doc=result.document

                chunks = list(chunker.chunk(doc))
                
                # Format each chunk with the required metadata schema
                for idx, chunk in enumerate(chunks):


                    contextualized_text = chunker.contextualize(chunk)
                    
                    # 3. Construct Metadata Payload
                    metadata = {
                        "source_document": source_document,                 # Original filename
                        "collection": collection_name,                       # e.g., clinical, billing
                        "access_roles": access_roles,                       # List of permitted roles
                        "section_title": chunk.meta.headings,                # Headings under which this chunk falls
                        "chunk_type": determine_chunk_type(chunk),           # text, table, heading, code
                        # "pages": list(set(prov.page_no for prov in chunk.meta.doc_items if hasattr(prov, 'page_no') or (hasattr(prov, 'prov') and prov.prov))),
                        "chunk_index": idx
                    }
                    
                    data.append({
                        "page_content": contextualized_text,
                        "raw_text": chunk.text,
                        "metadata": metadata
                    })
                    
            except Exception as e:
                print(f"Error processing {source_document}: {e}")
                
    return data