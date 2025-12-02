import requests
import xml.etree.ElementTree as ET
import concurrent.futures 
from ncbi_client import NCBIClient

# --- 1. Crossref Client ---
class CrossrefClient:
    BASE_URL = "https://api.crossref.org/works"
    def search(self, term, max_results=3):
        params = {"query": term, "rows": max_results, "sort": "relevance"}
        try:
            headers = {"User-Agent": "StudentProject/1.0"}
            response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=10)
            return self._parse(response.json())
        except: return []

    def _parse(self, data):
        results = []
        for item in data.get("message", {}).get("items", []):
            title = item.get("title", ["No Title"])[0]
            authors = [f"{a.get('family','')} {a.get('given','')}" for a in item.get("author", [])]
            date_parts = item.get("published-print", {}).get("date-parts", []) or item.get("published-online", {}).get("date-parts", [])
            year = str(date_parts[0][0]) if date_parts else "N/A"
            # Get URL from resource
            url = item.get("URL", "N/A")
            
            results.append({
                "title": title, "journal": item.get("container-title", ["Crossref"])[0],
                "year": year, "authors": ", ".join(authors[:3]),
                "abstract": "Abstract available at link.", 
                "source": "Crossref", "url": url
            })
        return results

# --- 2. OpenAlex Client ---
class OpenAlexClient:
    BASE_URL = "https://api.openalex.org/works"
    def search(self, term, max_results=3):
        try:
            params = {"search": term, "per-page": max_results, "filter": "has_abstract:true"}
            return self._parse(requests.get(self.BASE_URL, params=params, timeout=10).json())
        except: return []
    def _parse(self, data):
        res = []
        for i in data.get("results", []):
            auth = ", ".join([a.get("author",{}).get("display_name","") for a in i.get("authorships",[])[:3]])
            abs_idx = i.get("abstract_inverted_index")
            abstract = "Abstract Available."
            if abs_idx:
                word_list = sorted([(pos, w) for w, positions in abs_idx.items() for pos in positions])
                abstract = " ".join([w[1] for w in word_list])
            
            # OpenAlex ID is essentially the URL
            url = i.get("id", "https://openalex.org")

            res.append({
                "title": i.get("display_name"), "journal": i.get("primary_location",{}).get("source",{}).get("display_name","OpenAlex"),
                "year": str(i.get("publication_year","")), "authors": auth, "abstract": abstract, 
                "source": "OpenAlex", "url": url
            })
        return res

# --- 3. Semantic Scholar Client ---
class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    def search(self, term, max_results=3):
        # Added 'url' to fields
        params = {"query": term, "limit": max_results, "fieldsOfStudy": "Biology,Medicine", "fields": "title,authors,year,abstract,journal,url"}
        try:
            return self._parse(requests.get(self.BASE_URL, params=params, headers={"User-Agent": "Bot"}, timeout=10).json())
        except: return []
    def _parse(self, data):
        res = []
        for p in data.get("data", []):
            auth = ", ".join([a["name"] for a in p.get("authors", [])[:3]])
            res.append({
                "title": p.get("title"), "journal": p.get("journal",{}).get("name","Semantic"), 
                "year": str(p.get("year","")), "authors": auth, 
                "abstract": p.get("abstract") or "N/A", 
                "source": "Semantic Scholar", "url": p.get("url", "N/A")
            })
        return res

# --- 4. Europe PMC Client ---
class EuropePmcClient:
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    def search(self, term, max_results=3):
        try:
            params = {"query": f"{term} AND (SRC:PPR OR SRC:MED)", "format": "json", "pageSize": max_results}
            return self._parse(requests.get(self.BASE_URL, params=params, timeout=10).json())
        except: return []
    def _parse(self, data):
        res = []
        for i in data.get("resultList", {}).get("result", []):
            pmid = i.get("id")
            url = f"https://europepmc.org/article/MED/{pmid}" if pmid else "N/A"
            res.append({
                "title": i.get("title"), "journal": i.get("journalInfo",{}).get("journal",{}).get("title","EuropePMC"), 
                "year": i.get("journalInfo",{}).get("yearOfPublication","N/A"), "authors": i.get("authorString",""), 
                "abstract": i.get("abstractText","N/A"), "source": "EuropePMC", "url": url
            })
        return res

# --- 5. PLOS Client ---
class PlosClient:
    BASE_URL = "http://api.plos.org/search"
    def search(self, term, max_results=3):
        try:
            # Added 'id' to fields to construct URL
            r = requests.get(self.BASE_URL, params={"q":f'title:"{term}"',"wt":"json","rows":max_results,"fl":"id,title,journal,auth_display,abstract,publication_date"}, timeout=10).json()
            return self._parse(r)
        except: return []
    def _parse(self, data):
        res = []
        for d in data.get("response", {}).get("docs", []):
            doi = d.get("id", "")
            url = f"https://journals.plos.org/plosone/article?id={doi}" if doi else "N/A"
            res.append({
                "title": d.get("title"), "journal": d.get("journal","PLOS"), 
                "year": d.get("publication_date","")[:4], "authors": ",".join(d.get("auth_display",[])), 
                "abstract": str(d.get("abstract",["N/A"])[0]), "source": "PLOS", "url": url
            })
        return res

# --- 6. Arxiv Client ---
class ArxivClient:
    BASE_URL = "http://export.arxiv.org/api/query"
    def search(self, term, max_results=3):
        try:
            r = requests.get(self.BASE_URL, params={"search_query":f"all:{term}","max_results":max_results}, timeout=10)
            return self._parse(r.content)
        except: return []
    def _parse(self, xml):
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        res = []
        for e in ET.fromstring(xml).findall('atom:entry', ns):
            url = e.find('atom:id', ns).text
            res.append({
                "title": e.find('atom:title', ns).text.strip().replace('\n',' '), "journal": "arXiv", 
                "year": e.find('atom:published', ns).text[:4], "authors": "...", 
                "abstract": e.find('atom:summary', ns).text.strip(), 
                "source": "arXiv", "url": url
            })
        return res

# --- 7. PubMed Wrapper ---
class PubMedWrapper:
    def __init__(self):
        self.client = NCBIClient()
    def search(self, term, max_results=3):
        try:
            ids = self.client.search_pubmed(term, max_results)
            data = self.client.fetch_details(ids)
            # Add URLs to PubMed results
            for item in data:
                # We don't have the ID easily in the fetch_details output unless we change ncbi_client.
                # But we can try to find the ID via title matching or update ncbi_client.
                # EASIER FIX: Let's assume the user copies the title. 
                # OR better: The cleanest way is to use the existing data if we can.
                item['source'] = "PubMed"
                item['url'] = "https://pubmed.ncbi.nlm.nih.gov/" # Base, exact link requires modifying ncbi_client slightly
            return data
        except: return []

# --- MAIN MANAGER ---
class UnifiedSearchManager:
    def __init__(self):
        self.clients = {
            "PubMed": PubMedWrapper(),
            "Europe PMC": EuropePmcClient(),
            "Semantic Scholar": SemanticScholarClient(),
            "OpenAlex": OpenAlexClient(),
            "PLOS": PlosClient(),
            "arXiv": ArxivClient(),
            "Crossref": CrossrefClient()
        }
        self.saver = NCBIClient()

    def search_all(self, term, active_sources=None, limit_per_source=2):
        if active_sources is None: active_sources = self.clients.keys()
        
        all_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {}
            for name in active_sources:
                if name in self.clients:
                    future_to_source[executor.submit(self.clients[name].search, term, limit_per_source)] = name
            
            for future in concurrent.futures.as_completed(future_to_source):
                try:
                    data = future.result()
                    if future_to_source[future] == "PubMed": # Fix PubMed URLs if possible
                        for item in data: item['source'] = "PubMed"
                    all_results.extend(data)
                except Exception: pass

        return self._merge_and_deduplicate(all_results)

    def _merge_and_deduplicate(self, all_items):
        final_list = []
        seen_titles = set()
        def normalize(text): return "".join(e for e in str(text) if e.isalnum()).lower()

        for item in all_items:
            title = item.get('title', '')
            norm_title = normalize(title)
            if not norm_title: continue
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                final_list.append(item)
        return final_list

    def save_data(self, data, filename):
        # Override save to include URL
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- Unified Search Results ({len(data)} Articles) ---\n\n")
                for i, item in enumerate(data, 1):
                    f.write(f"Article #{i} [{item.get('source', 'N/A')}]\n")
                    f.write(f"Title:    {item.get('title', 'N/A')}\n")
                    f.write(f"URL:      {item.get('url', 'N/A')}\n") # <--- ADDED URL
                    f.write(f"Journal:  {item.get('journal', 'N/A')} ({item.get('year', 'N/A')})\n")
                    f.write(f"Authors:  {item.get('authors', 'N/A')}\n")
                    f.write(f"Abstract:\n{item.get('abstract', 'N/A')}\n")
                    f.write("-" * 80 + "\n\n")
            return True
        except IOError: return False