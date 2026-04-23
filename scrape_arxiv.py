import requests
import feedparser
from datetime import datetime
from collections import defaultdict

# =========================
# CONFIGURATION
# =========================

# List of group members (use format: "Surname Initial" or "Surname Name")
AUTHORS = [
    "Torlo Davide",
    "Alla Alessandro",
    "Visconti Giuseppe",
    "Puppo Gabriella",
    "Cacace Simone",
    "Carlini Elisabetta",
    "Noschese Silvia",
    "Taddei Tommaso",
    "Ciaramaglia Ilaria",
    "Coscetti Valentina",
    "Jiehong Liu",
    "Mayer Filippo",
    "Oliviero Alessio",
    "Tatafiore Giulia",
    "Tenna Tommaso"
]

# Add all authors with only initial of the name, e.g. "Torlo D" for "Torlo Davide"
AUTHORS = AUTHORS + [" ".join(a.split()[:-1]) + " " + a.split()[-1][0] for a in AUTHORS if len(a.split()) >= 2]

# arXiv category for numerical analysis
CATEGORY = "math.NA"

# Max results per query
MAX_RESULTS = 100

# Output file
OUTPUT_HTML = "arxiv_preprints.html"


# =========================
# FUNCTIONS
# =========================

def query_arxiv(author):
    """Query arXiv API for a given author"""
    base_url = "http://export.arxiv.org/api/query"
    query = f"search_query=cat:{CATEGORY}+AND+au:\"{author}\"&start=0&max_results={MAX_RESULTS}"
    url = f"{base_url}?{query}"
    
    response = requests.get(url)
    feed = feedparser.parse(response.text)
    
    return feed.entries


def normalize_title(title):
    """Normalize title for deduplication"""
    return " ".join(title.lower().split())


def collect_papers():
    """Collect and deduplicate papers from all authors"""
    papers = {}
    
    for author in AUTHORS:
        print("Querying arXiv for author:", author)
        entries = query_arxiv(author)
        
        for entry in entries:
            print("Processing paper:", entry.title)
            title_key = normalize_title(entry.title)
            
            if title_key not in papers:
                papers[title_key] = {
                    "title": entry.title,
                    "authors": [a.name for a in entry.authors],
                    "summary": entry.summary,
                    "link": entry.link,
                    "published": entry.published
                }
    
    return list(papers.values())


def format_date(date_str):
    """Format date nicely"""
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y-%m-%d")


def generate_html(papers):
    """Generate HTML page"""
    
    papers_sorted = sorted(papers, key=lambda x: x["published"], reverse=True)
    
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Preprints - Numerical Analysis Group</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 40px;
}
h1 {
    color: #2c3e50;
}
.paper {
    margin-bottom: 25px;
}
.title {
    font-weight: bold;
    font-size: 16px;
}
.authors {
    color: #555;
}
.date {
    font-size: 12px;
    color: #888;
}
.summary {
    margin-top: 5px;
}
</style>
</head>
<body>

<p>Last automatic update from arXiv:"""
    html+= f""" {datetime.now().strftime("%Y-%m-%d")}"""
    html+="""</p>
<hr>
"""
    
    for p in papers_sorted:
        html += f"""
<div class="paper">
    <div class="title">
        <a href="{p['link']}" target="_blank">{p['title']}</a>
    </div>
    <div class="authors">
        {", ".join(p['authors'])}
    </div>
    <div class="date">
        {format_date(p['published'])}
    </div>
    <div class="summary">
        {p['summary'][:300]}...
    </div>
</div>
"""
    
    html += """
</body>
</html>
"""
    
    return html


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("Fetching papers from arXiv...")
    papers = collect_papers()
    
    print(f"Found {len(papers)} unique papers.")
    
    html = generate_html(papers)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"HTML page generated: {OUTPUT_HTML}")