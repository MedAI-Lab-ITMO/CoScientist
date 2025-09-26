import pytest
import os
import uuid
from dotenv import load_dotenv
from pathlib import Path

from ChemCoScientist.paper_analysis.chroma_db_operations import ChromaClient, ChromaDBPaperStore, process_all_documents
from ChemCoScientist.paper_analysis.question_processing import process_question, simple_query_llm
from CoScientist.paper_parser.s3_connection import S3BucketService

from definitions import CONFIG_PATH, ROOT_DIR

load_dotenv(CONFIG_PATH)
PAPERS_STORAGE_PATH = os.path.join(ROOT_DIR, "ChemCoScientist/tests/integration/data")
PARSE_RESULTS_PATH = os.path.join(ROOT_DIR, "ChemCoScientist/tests/integration/parse_results")
QUESTION = "Are there any compounds for which IR was taken? If there are, write me the abbreviations of those compounds that were taken in pure form."
VISION_LLM_URL = os.environ["VISION_LLM_URL"]

def _unique(name: str) -> str:
    """Generates a unique collection or bucket name by appending a random 8-character UUID suffix."""
    return f"{name}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def client() -> ChromaClient:
    """Fixture providing a ChromaDB client instance."""
    return ChromaClient()

@pytest.fixture(scope="class")
def s3_service():
    """Fixture that creates an s3 service with a temporary bucket for testing and deletes the bucket afterwards."""
    bucket_name = _unique("tests-integration")
    s3_service = S3BucketService(
    endpoint=os.getenv("ENDPOINT_URL"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    bucket_name=bucket_name)
    yield s3_service
    try:
        client = s3_service.create_s3_client()
        resp = client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in resp:
            for obj in resp["Contents"]:
                client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        s3_service.del_bucket(bucket_name)
    except Exception as e:
        print(f"[WARN] Failed to cleanup S3 bucket {bucket_name}: {e}")

@pytest.fixture(scope="class")
def collection_names() -> dict[str, str]:
    """Fixture providing unique names for test ChromaDB collections."""
    return {
        "sum": _unique("tests_paper_summaries_img2txt"),
        "txt": _unique("tests_text_context_img2txt"),
        "img": _unique("tests_image_context"),
    }
    
@pytest.fixture(scope="class")
def paper_store(collection_names: dict[str, str]):
    """Fixture providing a ChromaDBPpaperStore instance."""
    return ChromaDBPaperStore(
            sum_collection_name=collection_names["sum"],
            txt_collection_name=collection_names["txt"],
            img_collection_name=collection_names["img"]
        )

@pytest.mark.incremental
class TestPaperAnalysis:
    """
    Integration test suite for ChromaDB collections, PDF upload, question answering,
    and user article querying.
    """
    def test_01_create_collection(self,
                                  client: ChromaClient,
                                  paper_store: ChromaDBPaperStore,
                                  collection_names: dict[str, str]) -> None:
        """Test that ChromaDB collections can be created successfully."""
        collections_list = [c.name for c in client.show_collections()]
        assert collection_names["sum"] in collections_list
        assert collection_names["txt"] in collections_list
        assert collection_names["img"] in collections_list
    
    def test_02_upload_pdf(collection_names: dict[str, str],
                           paper_store: ChromaDBPaperStore,
                           s3_service,
                           ) -> None:
        """Test that the PDF upload script runs without errors.""" 
        paper_store.run_marker_pdf(PAPERS_STORAGE_PATH, PARSE_RESULTS_PATH)
        del paper_store
        process_all_documents(Path(PARSE_RESULTS_PATH), s3_service)
    
    def test_03_query(self, paper_store: ChromaDBPaperStore) -> None:
        """Test that querying the database with a predefined question returns a valid answer and metadata."""
        result = process_question(QUESTION, paper_store)
        assert "answer" in result
        assert "metadata" in result
        assert isinstance(result["answer"], str)
        assert result["answer"].strip() != ""
        meta = result["metadata"]
        assert isinstance(meta, dict)
        for field in ("text_context", "image_context", "metadata"):
            assert field in meta
            assert meta[field] not in (None, "", [], {})
    
    def test_04_delete_collection(self,
                                  client: ChromaClient,
                                  collection_names: dict[str, str]) -> None:
        """Test that a specific ChromaDB collection can be deleted."""
        client.delete_collection(collection_names["sum"])
        client.delete_collection(collection_names["txt"])
        client.delete_collection(collection_names["img"])
        collections_list = [c.name for c in client.show_collections()]
        assert collection_names["sum"] not in collections_list
        assert collection_names["txt"] not in collections_list
        assert collection_names["img"] not in collections_list
    
    def test_05_query_user_article(self) -> None:
        """Test that querying user-uploaded PDFs with the Vision LLM returns an answer."""
        pdfs_dirs = [os.path.join(PAPERS_STORAGE_PATH, f)
                     for f in os.listdir(PAPERS_STORAGE_PATH)
                     if f.lower().endswith(".pdf")]
        result = simple_query_llm(VISION_LLM_URL, QUESTION, pdfs_dirs)
        print(result)
        assert "answer" in result
        assert isinstance(result["answer"], str)