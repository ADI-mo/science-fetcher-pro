import requests
import xml.etree.ElementTree as ET

class NCBIClient:
    """
    Handles interactions with the NCBI Entrez API (E-utilities).
    """
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key=None, tool_name="day06_assignment"):
        self.api_key = api_key
        self.tool_name = tool_name

    def _get_base_params(self):
        params = {"tool": self.tool_name}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search_pubmed(self, term, max_results=5):
        """
        Searches PubMed. Adds logic to restrict to English where possible via the query.
        """
        url = f"{self.BASE_URL}/esearch.fcgi"
        params = self._get_base_params()
        
        # Enforce English language in the search query itself
        search_term = f"{term} AND English[Language]"
        
        params.update({
            "db": "pubmed",
            "term": search_term,
            "retmax": max_results,
            "sort": "relevance",
            "retmode": "json"
        })

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def fetch_details(self, id_list):
        if not id_list:
            return []

        url = f"{self.BASE_URL}/efetch.fcgi"
        params = self._get_base_params()
        params.update({
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        })

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            results = []

            for article in root.findall(".//PubmedArticle"):
                # Extract basic info
                title = article.findtext(".//ArticleTitle") or "No Title"
                journal = article.findtext(".//Journal/Title") or "Unknown Journal"
                
                # Extract PMID for creating the link!
                pmid = article.findtext(".//MedlineCitation/PMID")
                
                # Extract Year
                year = article.findtext(".//PubDate/Year")
                if not year:
                    year = article.findtext(".//PubDate/MedlineDate")
                
                # Abstract
                abstract_texts = article.findall(".//AbstractText")
                full_abstract_parts = []
                for t in abstract_texts:
                    part_text = "".join(t.itertext())
                    if part_text:
                        full_abstract_parts.append(part_text)
                
                abstract = " ".join(full_abstract_parts)
                if not abstract:
                    abstract = "No Abstract Available."

                # Authors
                authors = []
                for author in article.findall(".//Author"):
                    last = author.findtext("LastName")
                    initials = author.findtext("Initials")
                    if last and initials:
                        authors.append(f"{last} {initials}")
                
                results.append({
                    "pmid": pmid, # Store ID
                    "title": title,
                    "journal": journal,
                    "year": year,
                    "authors": ", ".join(authors),
                    "abstract": abstract
                })
            
            return results

        except Exception as e:
            print(f"Error during fetch: {e}")
            return []

    def save_data(self, data, filename):
        # Base save function (GUI uses a more advanced one now)
        pass