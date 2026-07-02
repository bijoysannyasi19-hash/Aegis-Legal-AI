from app.core.ingestion import DocumentParser
from app.core.hybrid_search import HybridSearchEngine
from app.core.generator import GeneratorPipeline

# Instantiate application core engines as singleton lifecycles
document_parser = DocumentParser()
search_engine = HybridSearchEngine()
generator_pipeline = GeneratorPipeline()

def get_document_parser() -> DocumentParser:
    return document_parser

def get_search_engine() -> HybridSearchEngine:
    return search_engine

def get_generator_pipeline() -> GeneratorPipeline:
    return generator_pipeline
