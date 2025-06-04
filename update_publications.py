import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os
import time

def parse_first_author(authors_string):
    """Parse authors string to extract first author and add 'et al.' if multiple authors."""
    if not authors_string or authors_string == 'Unknown Authors':
        return 'Unknown Authors'
    
    # Split by common separators
    authors = re.split(r'[,;&]|\sand\s', authors_string.strip())
    
    if len(authors) == 0:
        return 'Unknown Authors'
    
    first_author = authors[0].strip()
    
    # If there's more than one author, add "et al."
    if len(authors) > 1:
        return f"{first_author} et al."
    else:
        return first_author

def get_google_scholar_publications(author_query, author_id="wgK6LCYAAAAJ"):
    """Fetch ALL publications from Google Scholar using basic web scraping."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Using known author ID: {author_id}")
    
    try:
        # Fetch all publications by iterating through pages
        all_publications = []
        start = 0
        page_size = 100  # Maximum publications per page
        
        while True:
            # Get publications page with pagination
            publications_url = f"https://scholar.google.com/citations?user={author_id}&hl=en&oi=ao&cstart={start}&pagesize={page_size}"
            
            print(f"Fetching page starting at {start}: {publications_url}")
            
            # Add delay to be respectful
            if start > 0:
                time.sleep(2)
            
            response = requests.get(publications_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all publication entries on this page
            pub_rows = soup.find_all('tr', class_='gsc_a_tr')
            
            if not pub_rows:
                print(f"No more publications found. Total fetched: {len(all_publications)}")
                break
            
            print(f"Processing page starting at {start}, found {len(pub_rows)} publications...")
            
            page_publications = []
            for i, row in enumerate(pub_rows):
                try:
                    # Extract title and link
                    title_cell = row.find('td', class_='gsc_a_t')
                    if not title_cell:
                        continue
                        
                    title_link = title_cell.find('a')
                    title = title_link.text.strip() if title_link else 'Unknown Title'
                    
                    # Extract authors and venue info
                    author_venue = title_cell.find('div', class_='gs_gray')
                    authors = author_venue.text.strip() if author_venue else 'Unknown Authors'
                    
                    # Parse to get first author et al.
                    first_author = parse_first_author(authors)
                    
                    # Extract year
                    year_cell = row.find('td', class_='gsc_a_y')
                    year_span = year_cell.find('span') if year_cell else None
                    year = year_span.text.strip() if year_span else 'Unknown Year'
                    
                    # Parse year for sorting
                    try:
                        year_int = int(year) if year and year != 'Unknown Year' else 0
                    except (ValueError, TypeError):
                        year_int = 0
                    
                    # Try to get the full publication URL
                    citation_link = title_link.get('href', '') if title_link else ''
                    full_url = f"https://scholar.google.com{citation_link}" if citation_link else ''
                    
                    page_publications.append({
                        'title': title,
                        'authors': authors,
                        'first_author': first_author,
                        'year': year,
                        'year_int': year_int,
                        'venue': '',  # Basic scraping doesn't easily get venue separately
                        'url': full_url
                    })
                    
                    print(f"Processed: {title[:50]}... ({year}) - {first_author}")
                    
                except Exception as e:
                    print(f"Error processing publication {i}: {e}")
                    continue
            
            all_publications.extend(page_publications)
            
            # Check if we should continue to next page
            if len(pub_rows) < page_size:
                print(f"Reached last page. Total publications: {len(all_publications)}")
                break
            
            start += page_size
        
        # Sort publications by year (most recent first)
        all_publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        print(f"\nFetched and sorted {len(all_publications)} total publications:")
        for i, pub in enumerate(all_publications[:10], 1):  # Show first 10 as preview
            print(f"{i}. {pub['title']} ({pub['year']}) - {pub['first_author']}")
        if len(all_publications) > 10:
            print(f"... and {len(all_publications) - 10} more")
        
        return all_publications
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google Scholar: {e}")
        return []
    except Exception as e:
        print(f"Error parsing Google Scholar data: {e}")
        return []

def update_html_with_publications(publications, html_file="index.html"):
    """Update the HTML file with publications data."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create publications HTML
        if publications:
            publications_html = ""
            for pub in publications:
                venue_text = f" {pub['venue']}" if pub['venue'] else ""
                if pub['url']:
                    publications_html += f'    <li><a href="{pub["url"]}" target="_blank">{pub["title"]}</a> - {pub["first_author"]} ({pub["year"]}){venue_text}</li>\n'
                else:
                    publications_html += f'    <li>{pub["title"]} - {pub["first_author"]} ({pub["year"]}){venue_text}</li>\n'
        else:
            publications_html = '    <li><em>Publications are automatically updated from <a href="https://scholar.google.com/citations?user=wgK6LCYAAAAJ" target="_blank">Google Scholar</a>. If this section appears empty, the automated script may need to be run.</em></li>\n'
        
        # Replace the publications section
        pattern = r'(<h2 id="publications">Recent Publications</h2>\s*<)(ul|ol reversed)(>)(.*?)(</)(ul|ol)(>)'
        replacement = rf'\1ol reversed\3\n{publications_html}\5ol\7'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully updated {html_file} with {len(publications)} publications")
            return True
        else:
            print("No publications section found in HTML file")
            return False
            
    except Exception as e:
        print(f"Error updating HTML file: {e}")
        return False

def main():
    import sys
    
    # Default author query
    author_query = "Kyle Mathewson University of Alberta"
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        author_query = sys.argv[1]
    
    print(f"Fetching ALL publications for: {author_query}")
    print("Note: This may take a while as we fetch all publication information...")
    
    # Fetch all publications
    publications = get_google_scholar_publications(author_query)
    
    if publications and len(publications) >= 50:  # Require at least 50 publications (Kyle has ~102)
        print(f"\nFound {len(publications)} total publications")
        
        # Update HTML file
        success = update_html_with_publications(publications)
        if success:
            print(f"\nSuccessfully updated index.html with all {len(publications)} publications!")
            sys.exit(0)  # Success
        else:
            print("\nFailed to update HTML file")
            sys.exit(1)  # Failure
    else:
        print(f"Insufficient publications found ({len(publications) if publications else 0}). Not updating to prevent overwriting good content.")
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main() 