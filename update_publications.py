import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os
import time

def get_google_scholar_publications(author_query, max_results=20):
    """Fetch publications from Google Scholar using web scraping."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Search for the author first to get their author ID
    search_url = "https://scholar.google.com/citations"
    params = {
        'view_op': 'search_authors',
        'mauthors': author_query,
        'hl': 'en'
    }
    
    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first author result
        author_links = soup.select('h3.gs_ai_name a')
        if not author_links:
            print(f"No author found for query: {author_query}")
            return []
        
        # Extract author ID from the first result
        author_url = author_links[0]['href']
        author_id = None
        if 'user=' in author_url:
            author_id = author_url.split('user=')[1].split('&')[0]
        
        if not author_id:
            print("Could not extract author ID")
            return []
        
        print(f"Found author ID: {author_id}")
        
        # Now get the author's publications
        publications_url = "https://scholar.google.com/citations"
        pub_params = {
            'user': author_id,
            'hl': 'en',
            'cstart': 0,
            'pagesize': max_results
        }
        
        time.sleep(2)  # Be respectful to Google's servers
        pub_response = requests.get(publications_url, params=pub_params, headers=headers, timeout=30)
        pub_response.raise_for_status()
        
        pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
        
        publications = []
        
        # Extract publication information
        pub_rows = pub_soup.select('tr.gsc_a_tr')
        
        for row in pub_rows[:max_results]:
            try:
                title_elem = row.select_one('a.gsc_a_at')
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                link = "https://scholar.google.com" + title_elem['href']
                
                # Get authors and venue
                details = row.select('div.gs_gray')
                authors = details[0].get_text().strip() if len(details) > 0 else ""
                venue = details[1].get_text().strip() if len(details) > 1 else ""
                
                # Get year and citations
                year_elem = row.select_one('span.gsc_a_y')
                year = year_elem.get_text().strip() if year_elem else ""
                
                citations_elem = row.select_one('a.gsc_a_c')
                citations = citations_elem.get_text().strip() if citations_elem else "0"
                
                # Parse year for sorting
                try:
                    year_int = int(year) if year else 0
                except ValueError:
                    year_int = 0
                
                publications.append({
                    'title': title,
                    'link': link,
                    'authors': authors,
                    'venue': venue,
                    'year': year,
                    'year_int': year_int,
                    'citations': citations
                })
                
            except Exception as e:
                print(f"Error parsing publication: {e}")
                continue
        
        # Sort by year (most recent first)
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        return publications
        
    except requests.RequestException as e:
        print(f"Error fetching data from Google Scholar: {e}")
        return []
    except Exception as e:
        print(f"Error parsing Google Scholar data: {e}")
        return []

def update_html_with_publications(publications, html_file):
    """Update the index.html file with publications section."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create the publications section HTML
    pub_items = []
    for pub in publications:
        # Format the publication entry
        authors_text = pub['authors'] if pub['authors'] else "Authors not available"
        venue_text = pub['venue'] if pub['venue'] else ""
        year_text = f" ({pub['year']})" if pub['year'] else ""
        citations_text = f" - Cited by {pub['citations']}" if pub['citations'] and pub['citations'] != "0" else ""
        
        # Create publication description
        description_parts = []
        if authors_text:
            description_parts.append(authors_text)
        if venue_text:
            description_parts.append(venue_text)
        
        description = " - ".join(description_parts) + year_text + citations_text
        
        pub_item = f'<li><a href="{pub["link"]}" target="_blank">{pub["title"]}</a> - {description}</li>'
        pub_items.append(pub_item)
    
    publications_html = f'''<h2 id="publications">Recent Publications</h2>
<ul>
    {chr(10).join([f"    {item}" for item in pub_items])}
</ul>'''
    
    # Find where to insert the publications section (after projects, before research)
    projects_end_pattern = r'</ul>\s*<hr>\s*<h2 id="research">'
    
    if re.search(projects_end_pattern, content):
        # Insert publications section between projects and research
        new_content = re.sub(
            projects_end_pattern,
            f'</ul>\n\n<hr>\n\n{publications_html}\n\n<hr>\n\n<h2 id="research">',
            content,
            count=1
        )
    else:
        # Fallback: insert after projects section
        projects_pattern = r'(<h2 id="projects">Recent Projects</h2>\s*<ul>.*?</ul>)'
        if re.search(projects_pattern, content, flags=re.DOTALL):
            new_content = re.sub(
                projects_pattern,
                f'\\1\n\n<hr>\n\n{publications_html}',
                content,
                flags=re.DOTALL,
                count=1
            )
        else:
            print("Could not find suitable location to insert publications section")
            return
    
    # Update navigation to include publications
    nav_pattern = r'(<li><a href="#projects">Recent Projects</a></li>)'
    nav_replacement = '\\1\n    <li><a href="#publications">Recent Publications</a></li>'
    new_content = re.sub(nav_pattern, nav_replacement, new_content)
    
    # Write the updated content back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    # Author query - you can modify this to match your Google Scholar profile
    AUTHOR_QUERY = 'Kyle Mathewson University of Alberta'
    
    # Path to your index.html file
    HTML_FILE = 'index.html'
    
    # Maximum number of publications to fetch
    MAX_RESULTS = 15
    
    print(f"Fetching publications for: {AUTHOR_QUERY}")
    
    # Get publications from Google Scholar
    publications = get_google_scholar_publications(AUTHOR_QUERY, MAX_RESULTS)
    
    if publications:
        print(f"Found {len(publications)} publications")
        
        # Update the HTML file
        update_html_with_publications(publications, HTML_FILE)
        
        print(f"Updated {HTML_FILE} with {len(publications)} publications.")
        
        # Print first few publications for verification
        print("\nFirst few publications:")
        for i, pub in enumerate(publications[:3]):
            print(f"{i+1}. {pub['title']} ({pub['year']})")
    else:
        print("No publications found. Please check the author query or try again later.") 