import re
from bs4 import BeautifulSoup
import os

def get_google_scholar_publications_scholarly(author_name, max_results=20):
    """Fetch publications from Google Scholar using the scholarly library."""
    try:
        from scholarly import scholarly
        
        print(f"Searching for author: {author_name}")
        
        # Search for the author
        search_query = scholarly.search_author(author_name)
        author = next(search_query)
        
        print(f"Found author: {author.get('name', 'Unknown')}")
        
        # Fill in the author's details to get publications
        author = scholarly.fill(author)
        
        publications = []
        
        # Process publications
        for i, pub in enumerate(author.get('publications', [])[:max_results]):
            try:
                # Fill in publication details
                pub_filled = scholarly.fill(pub)
                
                # Extract information
                title = pub_filled['bib'].get('title', 'Unknown Title')
                authors = pub_filled['bib'].get('author', '')
                venue = pub_filled['bib'].get('venue', '') or pub_filled['bib'].get('journal', '')
                year = pub_filled['bib'].get('pub_year', '')
                citations = pub_filled.get('num_citations', 0)
                
                # Get the link if available
                link = pub_filled.get('pub_url', '') or pub_filled.get('eprint_url', '')
                if not link:
                    # Construct Google Scholar link
                    author_id = pub_filled.get('author_id', '')
                    citation_id = pub_filled.get('citation_id', '')
                    if citation_id:
                        link = f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={author_id}:{citation_id}"
                
                # Parse year for sorting
                try:
                    year_int = int(year) if year else 0
                except (ValueError, TypeError):
                    year_int = 0
                
                publications.append({
                    'title': title,
                    'link': link,
                    'authors': authors,
                    'venue': venue,
                    'year': str(year),
                    'year_int': year_int,
                    'citations': str(citations) if citations else "0"
                })
                
                print(f"  {i+1}. {title} ({year})")
                
            except Exception as e:
                print(f"Error processing publication {i+1}: {e}")
                continue
        
        # Sort by year (most recent first)
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        return publications
        
    except ImportError:
        print("scholarly library not found. Please install it with: pip install scholarly")
        return []
    except Exception as e:
        print(f"Error fetching data from Google Scholar: {e}")
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
        
        if pub['link']:
            pub_item = f'<li><a href="{pub["link"]}" target="_blank">{pub["title"]}</a> - {description}</li>'
        else:
            pub_item = f'<li>{pub["title"]} - {description}</li>'
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
    # Author name - modify this to match your Google Scholar profile
    AUTHOR_NAME = 'Kyle Mathewson'
    
    # Path to your index.html file
    HTML_FILE = 'index.html'
    
    # Maximum number of publications to fetch
    MAX_RESULTS = 15
    
    print(f"Fetching publications for: {AUTHOR_NAME}")
    print("Note: This may take a while as we fetch detailed publication information...")
    
    # Get publications from Google Scholar using scholarly library
    publications = get_google_scholar_publications_scholarly(AUTHOR_NAME, MAX_RESULTS)
    
    if publications:
        print(f"\nFound {len(publications)} publications")
        
        # Update the HTML file
        update_html_with_publications(publications, HTML_FILE)
        
        print(f"Updated {HTML_FILE} with {len(publications)} publications.")
        
        # Print first few publications for verification
        print("\nRecent publications:")
        for i, pub in enumerate(publications[:5]):
            print(f"{i+1}. {pub['title']} ({pub['year']})")
    else:
        print("No publications found. Please check the author name or try again later.") 