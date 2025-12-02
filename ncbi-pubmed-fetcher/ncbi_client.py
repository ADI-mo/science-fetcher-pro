import requests
import json
import xml.etree.ElementTree as ET

class NCBIClient:
    """
    Handles interactions with the NCBI Entrez API (E-utilities).
    """
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key=None, tool_name="day04_assignment"):
        self.api_key = api_key
        self.tool_name = tool_name

    def _get_base_params(self):
        params = {
            "tool": self.tool_name,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search_pubmed(self, term, max_results=5):
        """
        Searches PubMed using JSON return mode.
        """
        url = f"{self.BASE_URL}/esearch.fcgi"
        params = self._get_base_params()
        params.update({
            "db": "pubmed",
            "term": term,
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
        """
        Fetches FULL details including ABSTRACT using 'efetch' (XML format).
        Returns a clean list of dictionaries.
        """
        if not id_list:
            return []

        url = f"{self.BASE_URL}/efetch.fcgi"
        params = self._get_base_params()
        params.update({
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"  # Must use XML to get abstracts reliably
        })

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            results = []

            # Iterate over each article in the XML
            for article in root.findall(".//PubmedArticle"):
                # Extract basic info
                title = article.findtext(".//ArticleTitle") or "No Title"
                journal = article.findtext(".//Journal/Title") or "Unknown Journal"
                
                # Extract Year
                year = article.findtext(".//PubDate/Year")
                if not year:
                    year = article.findtext(".//PubDate/MedlineDate")
                
                # --- FIX: Better Abstract Extraction ---
                abstract_texts = article.findall(".//AbstractText")
                full_abstract_parts = []
                for t in abstract_texts:
                    part_text = "".join(t.itertext())
                    if part_text:
                        full_abstract_parts.append(part_text)
                
                abstract = " ".join(full_abstract_parts)
                if not abstract:
                    abstract = "No Abstract Available."

                # Extract Authors
                authors = []
                for author in article.findall(".//Author"):
                    last = author.findtext("LastName")
                    initials = author.findtext("Initials")
                    if last and initials:
                        authors.append(f"{last} {initials}")
                
                results.append({
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
        """
        Saves the data to a readable TEXT file (.txt).
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- Search Results ({len(data)} Articles) ---\n\n")
                
                for i, item in enumerate(data, 1):
                    f.write(f"Article #{i} [{item.get('source', 'N/A')}]\n") # Updated to show Source
                    f.write(f"Title:    {item.get('title', 'N/A')}\n")
                    f.write(f"Journal:  {item.get('journal', 'N/A')} ({item.get('year', 'N/A')})\n")
                    f.write(f"Authors:  {item.get('authors', 'N/A')}\n")
                    f.write(f"Abstract:\n{item.get('abstract', 'N/A')}\n")
                    f.write("-" * 80 + "\n\n")
                    
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False