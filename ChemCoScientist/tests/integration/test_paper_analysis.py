import pytest
import subprocess
import sys, os
import uuid
from dotenv import load_dotenv

from ChemCoScientist.paper_analysis.chroma_db_operations import ChromaClient, CustomEmbeddingFunction
from ChemCoScientist.paper_analysis.question_processing import process_question, simple_query_llm
from CoScientist.paper_parser.s3_connection import S3BucketService

from definitions import CONFIG_PATH, ROOT_DIR

load_dotenv(CONFIG_PATH)
BUCKET_NAME = "tests-integration"
DB_PAPERS_STORAGE_PATH = os.path.join(ROOT_DIR, "ChemCoScientist/tests/integration/data_db")
QUESTION_DB = "What is the IUPAC nomenclature name and the molecular weight of TEMPO?"
USER_PAPERS_STORAGE_PATH = os.path.join(ROOT_DIR, "ChemCoScientist/tests/integration/data_user")
QUESTION_USER = "Are there any compounds for which IR was taken? If there are, write me the abbreviations of those compounds that were taken in pure form."
VISION_LLM_URL = os.environ["VISION_LLM_URL"]

def _unique(name: str) -> str:
    """Generates a unique collection name by appending a random 8-character UUID suffix."""
    return f"{name}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def client() -> ChromaClient:
    """Fixture providing a ChromaDB client instance."""
    return ChromaClient()

@pytest.fixture
def s3_test_bucket() -> S3BucketService:
    """Fixture that creates a temporary S3 bucket for testing and deletes it afterwards."""
    s3_service = S3BucketService(
    endpoint=os.getenv("ENDPOINT_URL"),
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    bucket_name=BUCKET_NAME
    )
    s3_service.create_new_bucket(BUCKET_NAME)
    yield s3_service
    try:
        client = s3_service.create_s3_client()
        resp = client.list_objects_v2(Bucket=BUCKET_NAME)
        if "Contents" in resp:
            for obj in resp["Contents"]:
                client.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])
        s3_service.del_bucket(BUCKET_NAME)
    except Exception as e:
        print(f"[WARN] Failed to cleanup S3 bucket {BUCKET_NAME}: {e}")

@pytest.fixture
def collection_names() -> dict[str, str]:
    """Fixture providing unique names for test ChromaDB collections."""
    return {
        "sum": _unique("tests_paper_summaries_img2txt"),
        "txt": _unique("tests_text_context_img2txt"),
        "img": _unique("tests_image_context"),
    }

@pytest.fixture
def create_temp_collection(client: ChromaClient, collection_names: dict[str, str]):
    """Fixture that creates temporary ChromaDB collections for testing"and deletes them afterwards."""
    sum_collection = client.get_or_create_chroma_collection(
        collection_names["sum"], CustomEmbeddingFunction()
    )
    txt_collection = client.get_or_create_chroma_collection(
        collection_names["txt"], CustomEmbeddingFunction()
    )
    img_collection = client.get_or_create_chroma_collection(
        collection_names["img"], CustomEmbeddingFunction()
    )
    yield sum_collection, txt_collection, img_collection
    for name in collection_names.values():
        try:
            client.delete_collection(name)
        except Exception:
            pass  # already deleted in a test 04 or not found because it was not created in a test 01

@pytest.mark.incremental
class TestPaperAnalysis:
    """
    Integration test suite for ChromaDB collections, PDF upload, question answering,
    and user article querying.
    """
    def test_01_create_collection(self, create_temp_collection, client: ChromaClient) -> None:
        """Test that ChromaDB collections can be created successfully."""
        sum_collection, txt_collection, img_collection = create_temp_collection
        collections_list = [c.name for c in client.show_collections()]
        assert sum_collection.name in collections_list
        assert txt_collection.name in collections_list
        assert img_collection.name in collections_list
    
    def test_02_upload_pdf(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that the PDF upload script runs without errors."""
        monkeypatch.setenv("PAPERS_STORAGE_PATH", str(DB_PAPERS_STORAGE_PATH))
        result = subprocess.run(
        [sys.executable, "ChemCoScientist/paper_analysis/chroma_db_operations.py"],
        capture_output=True,
        text=True,
        env=os.environ
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
    
    def test_03_query(self) -> None:
        """Test that querying the database with a predefined question returns a valid answer and metadata."""
        result = process_question(QUESTION_DB)
        assert "answer" in result
        assert "metadata" in result
        assert isinstance(result["answer"], str)
        assert result["answer"].strip() != ""
        meta = result["metadata"]
        assert isinstance(meta, dict)
        for field in ("text_context", "image_context", "metadata"):
            assert field in meta
            assert meta[field] not in (None, "", [], {})
    
    def test_04_delete_collection(self, client, create_temp_collection, collection_names: dict[str, str]) -> None:
        """Test that a specific ChromaDB collection can be deleted."""
        name_to_delete = collection_names["sum"]
        client.delete_collection(name_to_delete)
        collections_list = [c.name for c in client.show_collections()]
        assert name_to_delete not in collections_list
    
    def test_05_query_user_article(self) -> None:
        """Test that querying user-uploaded PDFs with the Vision LLM returns an answer."""
        pdfs_dirs = [os.path.join(USER_PAPERS_STORAGE_PATH, f)
                     for f in os.listdir(USER_PAPERS_STORAGE_PATH)
                     if f.lower().endswith(".pdf")]
        result = simple_query_llm(VISION_LLM_URL, QUESTION_USER, pdfs_dirs)
        print(result)
        assert "answer" in result
        assert isinstance(result["answer"], str)