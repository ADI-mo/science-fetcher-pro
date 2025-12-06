import pytest
import requests
from unified_client import UnifiedSearchManager
from ncbi_client import NCBIClient

# --- Fixtures (הכנות לבדיקה) ---

@pytest.fixture
def manager():
    """יוצר מופע נקי של מנהל החיפושים לפני כל בדיקה"""
    return UnifiedSearchManager()

@pytest.fixture
def ncbi_client():
    """יוצר מופע של הקליינט של פאבמד"""
    return NCBIClient()

@pytest.fixture
def sample_xml_response():
    """מחזיר מחרוזת XML שמחקה תשובה אמיתית ותקינה מ-PubMed"""
    # תיקון קריטי: השנה נמצאת כעת בתוך JournalIssue -> PubDate
    # זה המבנה שהקוד שלך יודע לקרוא!
    return """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345678</PMID>
                <Article>
                    <ArticleTitle>Test Article Title for Pytest</ArticleTitle>
                    <Journal>
                        <Title>Journal of Testing</Title>
                        <JournalIssue>
                            <PubDate>
                                <Year>2024</Year>
                            </PubDate>
                        </JournalIssue>
                    </Journal>
                    <AuthorList>
                        <Author>
                            <LastName>Doe</LastName>
                            <Initials>J</Initials>
                        </Author>
                    </AuthorList>
                    <Abstract>
                        <AbstractText>This is a sample abstract.</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """

# --- Tests (הבדיקות עצמן) ---

def test_priority_logic(manager):
    """בדיקה קריטית: האם המערכת מעדיפה את PubMed על פני מקורות אחרים?"""
    
    high_priority = {
        "title": "Curing Code Bugs",
        "source": "PubMed",
        "url": "http://pubmed/1"
    }
    low_priority = {
        "title": "CURING CODE BUGS", 
        "source": "Crossref",
        "url": "http://crossref/1"
    }
    
    raw_results = [low_priority, high_priority]
    clean_results = manager._merge_and_deduplicate(raw_results)
    
    assert len(clean_results) == 1
    assert clean_results[0]["source"] == "PubMed"
    assert clean_results[0]["title"] == "Curing Code Bugs"

def test_ncbi_xml_parsing(ncbi_client, requests_mock, sample_xml_response):
    """בדיקה שהמערכת יודעת לקרוא XML של PubMed ולהפוך אותו למידע שימושי"""
    
    # 1. Mocking: מזייפים את האינטרנט
    requests_mock.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", text=sample_xml_response)
    
    # 2. Action: הרצת הפונקציה
    ids = ["12345678"]
    results = ncbi_client.fetch_details(ids)
    
    # 3. Assertions: בדיקת תוצאות
    assert len(results) == 1
    article = results[0]
    
    assert article["pmid"] == "12345678"
    assert article["title"] == "Test Article Title for Pytest"
    assert "Doe J" in article["authors"]
    # כעת זה יעבור כי ה-XML תוקן ומכיל את השנה במקום הנכון
    assert article["year"] == "2024"

def test_search_all_integration(manager, monkeypatch):
    """בדיקת אינטגרציה: האם הפונקציה הראשית קוראת לתתי-המערכות?"""
    
    def mock_search(*args, **kwargs):
        return [{"title": "Mock Result", "source": "PubMed", "url": "http://test.com"}]
    
    monkeypatch.setattr(manager.clients["PubMed"], "search", mock_search)
    
    results = manager.search_all("test term", active_sources=["PubMed"])
    
    assert len(results) == 1
    assert results[0]["title"] == "Mock Result"

def test_save_file(manager, tmp_path):
    """בדיקה שהשמירה לקובץ עובדת תקין"""
    
    data = [{"title": "Test Paper", "source": "Test", "year": "2024"}]
    file_path = tmp_path / "results.txt"
    
    success = manager.save_data(data, str(file_path))
    
    assert success is True
    content = file_path.read_text(encoding="utf-8")
    assert "SCIENTIFIC SEARCH RESULTS" in content
    assert "Test Paper" in content