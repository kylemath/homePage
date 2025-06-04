import re
from bs4 import BeautifulSoup
import os
import signal
import sys
import time

# Add timeout handling
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

# Set up signal handler for timeout
signal.signal(signal.SIGALRM, timeout_handler)

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

def get_google_scholar_publications_scholarly(author_name, author_id=None):
    """Fetch ALL publications from Google Scholar using the scholarly library."""
    print(f"[DEBUG] Entered get_google_scholar_publications_scholarly()", flush=True)
    
    if not author_id:
        print(f"[ERROR] No author ID provided, cannot proceed without author search", flush=True)
        return []
    
    try:
        print(f"[DEBUG] About to import scholarly inside function...", flush=True)
        from scholarly import scholarly
        print(f"[DEBUG] Successfully imported scholarly inside function", flush=True)
        
        print(f"[DEBUG] Bypassing author search, using direct ID: {author_id}", flush=True)
        
        # Set timeout for the entire operation (4 minutes)
        signal.alarm(240)
        
        # Instead of searching and filling author profile, directly get publications
        # using the citations URL approach
        print(f"[DEBUG] Getting publications directly from citations page...", flush=True)
        
        # Parse publications from all pages
        publications = []
        
        # Get all publications with pagination
        start = 0
        page_size = 100  # Request larger page size
        
        while True:
            # Construct the citations URL with pagination
            citations_url = f"/citations?user={author_id}&hl=en&oi=ao&cstart={start}&pagesize={page_size}"
            print(f"[DEBUG] Getting page starting at {start}: {citations_url}", flush=True)
            
            # Use scholarly's internal navigation to get the page
            from scholarly._navigator import Navigator
            nav = Navigator()
            
            print(f"[DEBUG] Getting citations page soup...", flush=True)
            soup = nav._get_soup(citations_url)
            print(f"[DEBUG] Got citations page successfully", flush=True)
            
            # Find all publication rows on this page
            pub_rows = soup.find_all('tr', class_='gsc_a_tr')
            
            if not pub_rows:
                print(f"[DEBUG] No more publications found on page starting at {start}", flush=True)
                break
            
            page_publications = len(pub_rows)
            print(f"[DEBUG] Found {page_publications} publication rows on this page", flush=True)
            
            # Process publications on this page
            for i, row in enumerate(pub_rows):
                pub_index = start + i
                try:
                    print(f"[DEBUG] Processing publication {pub_index+1}: {len(publications)+1} total so far", flush=True)
                    
                    # Extract title and link
                    title_cell = row.find('td', class_='gsc_a_t')
                    if not title_cell:
                        continue
                        
                    title_link = title_cell.find('a')
                    title = title_link.text.strip() if title_link else 'Unknown Title'
                    
                    print(f"[DEBUG] Title: {title[:50]}...", flush=True)
                    
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
                    
                    publications.append({
                        'title': title,
                        'authors': authors,
                        'first_author': first_author,
                        'year': year,
                        'year_int': year_int,
                        'venue': '',  # We'll get this from the basic approach
                        'url': full_url
                    })
                    
                    print(f"[DEBUG] Successfully processed: {title[:30]}... ({year}) - {first_author}", flush=True)
                    
                    # Add small delay between publications to be respectful
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process publication {pub_index+1}: {e}", flush=True)
                    continue
            
            # Check if we should continue to next page
            if page_publications < page_size:
                print(f"[DEBUG] Got {page_publications} publications (less than {page_size}), assuming last page", flush=True)
                break
            
            # Move to next page
            start += page_publications
            print(f"[DEBUG] Moving to next page, new start: {start}", flush=True)
            
            # Add delay between pages
            time.sleep(2)
        
        # Sort publications by year (most recent first)
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        print(f"\n[DEBUG] Successfully fetched and sorted {len(publications)} total publications:", flush=True)
        for i, pub in enumerate(publications[:5], 1):  # Show first 5 as preview
            print(f"  {i}. {pub['title'][:60]}... ({pub['year']}) - {pub['first_author']}", flush=True)
        if len(publications) > 5:
            print(f"  ... and {len(publications) - 5} more", flush=True)
        
        # Clear the alarm
        signal.alarm(0)
        return publications
        
    except ImportError:
        print("[ERROR] 'scholarly' library not installed. Install with: pip install scholarly", flush=True)
        signal.alarm(0)
        return []
    except TimeoutError:
        print("[ERROR] Google Scholar request timed out after 4 minutes", flush=True)
        signal.alarm(0)
        return []
    except Exception as e:
        print(f"[ERROR] Error fetching data from Google Scholar: {e}", flush=True)
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}", flush=True)
        signal.alarm(0)
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
    
    # Force unbuffered output for GitHub Actions
    sys.stdout.reconfigure(line_buffering=True)
    
    print("[DEBUG] Script started - main() called", flush=True)
    
    # Default author name
    author_name = "Kyle E Mathewson"
    author_id = "wgK6LCYAAAAJ"  # Kyle's Google Scholar ID
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        author_name = sys.argv[1]
    
    # Override author ID if provided as second argument
    if len(sys.argv) > 2:
        author_id = sys.argv[2]
    
    print(f"[DEBUG] Configuration: author={author_name}, id={author_id}", flush=True)
    print(f"[DEBUG] Fetching ALL publications for: {author_name}", flush=True)
    if author_id:
        print(f"[DEBUG] Using Google Scholar ID: {author_id}", flush=True)
    print("[DEBUG] Note: This may take a while as we fetch all publication information...", flush=True)
    
    # Test if scholarly library can be imported
    try:
        print("[DEBUG] Attempting to import scholarly library...", flush=True)
        from scholarly import scholarly
        print("[DEBUG] Scholarly library imported successfully", flush=True)
    except ImportError as e:
        print(f"[ERROR] Cannot import scholarly: {e}", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error importing scholarly: {e}", flush=True)
        sys.exit(1)
    
    # Fetch all publications
    print("[DEBUG] About to call get_google_scholar_publications_scholarly()", flush=True)
    publications = get_google_scholar_publications_scholarly(author_name, author_id=author_id)
    print(f"[DEBUG] Returned from get_google_scholar_publications_scholarly() with {len(publications) if publications else 0} publications", flush=True)
    
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