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
    
    try:
        print(f"[DEBUG] About to import scholarly inside function...", flush=True)
        from scholarly import scholarly
        print(f"[DEBUG] Successfully imported scholarly inside function", flush=True)
        
        print(f"[DEBUG] Starting search for author: {author_name}", flush=True)
        
        # Set timeout for the entire operation (4 minutes)
        signal.alarm(240)
        
        if author_id:
            # Use specific author ID if provided
            print(f"[DEBUG] Using author ID: {author_id}")
            try:
                print(f"[DEBUG] Calling scholarly.search_author_id...")
                author = scholarly.search_author_id(author_id)
                print(f"[DEBUG] Got author object, calling scholarly.fill...")
                author = scholarly.fill(author)
                print(f"[DEBUG] Author filled successfully")
            except Exception as e:
                print(f"[DEBUG] Error with author ID {author_id}: {e}")
                print("[DEBUG] Falling back to name search...")
                search_query = scholarly.search_author(author_name)
                author = next(search_query)
                author = scholarly.fill(author)
        else:
            # Search for the author by name
            print(f"[DEBUG] Calling scholarly.search_author...")
            search_query = scholarly.search_author(author_name)
            print(f"[DEBUG] Getting first result...")
            author = next(search_query)
            print(f"[DEBUG] Filling author details...")
            author = scholarly.fill(author)
        
        print(f"[DEBUG] Found author: {author.get('name', 'Unknown')}")
        
        publications = []
        
        # Fetch ALL publications
        total_publications = len(author.get('publications', []))
        print(f"[DEBUG] Total publications to process: {total_publications}")
        
        # Process publications in smaller batches to identify problematic ones
        batch_size = 10
        for batch_start in range(0, total_publications, batch_size):
            batch_end = min(batch_start + batch_size, total_publications)
            print(f"[DEBUG] Processing batch {batch_start}-{batch_end-1} of {total_publications}")
            
            batch_pubs = author.get('publications', [])[batch_start:batch_end]
            
            for i, pub in enumerate(batch_pubs):
                pub_index = batch_start + i
                try:
                    print(f"[DEBUG] Processing publication {pub_index+1}/{total_publications}")
                    
                    # Get basic info first
                    title_preview = pub.get('bib', {}).get('title', 'Unknown Title')[:50]
                    print(f"[DEBUG] Publication preview: {title_preview}...")
                    
                    # Fill publication details - this is where it might hang
                    print(f"[DEBUG] Calling scholarly.fill for publication {pub_index+1}...")
                    pub_filled = scholarly.fill(pub)
                    print(f"[DEBUG] Publication {pub_index+1} filled successfully")
                    
                    title = pub_filled.get('bib', {}).get('title', 'Unknown Title')
                    authors = pub_filled.get('bib', {}).get('author', 'Unknown Authors')
                    year = pub_filled.get('bib', {}).get('pub_year', 'Unknown Year')
                    venue = pub_filled.get('bib', {}).get('venue', '')
                    url = pub_filled.get('pub_url', pub_filled.get('eprint_url', ''))
                    
                    # Parse to get first author et al.
                    first_author = parse_first_author(authors)
                    
                    # Parse year for sorting
                    try:
                        year_int = int(year) if year and year != 'Unknown Year' else 0
                    except (ValueError, TypeError):
                        year_int = 0
                    
                    publications.append({
                        'title': title,
                        'authors': authors,
                        'first_author': first_author,
                        'year': year,
                        'year_int': year_int,
                        'venue': venue,
                        'url': url
                    })
                    
                    print(f"[DEBUG] Successfully processed {pub_index+1}/{total_publications}: {title[:50]}... ({year}) - {first_author}")
                    
                    # Add small delay between publications to be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process publication {pub_index+1}: {e}")
                    print(f"[ERROR] Publication that failed: {pub}")
                    continue
            
            # Add delay between batches
            print(f"[DEBUG] Completed batch {batch_start}-{batch_end-1}, pausing...")
            time.sleep(2)
        
        # Sort publications by year (most recent first)
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        print(f"\n[DEBUG] Successfully fetched and sorted {len(publications)} total publications:")
        for i, pub in enumerate(publications[:5], 1):  # Show first 5 as preview
            print(f"  {i}. {pub['title'][:60]}... ({pub['year']}) - {pub['first_author']}")
        if len(publications) > 5:
            print(f"  ... and {len(publications) - 5} more")
        
        # Clear the alarm
        signal.alarm(0)
        return publications
        
    except ImportError:
        print("[ERROR] 'scholarly' library not installed. Install with: pip install scholarly")
        signal.alarm(0)
        return []
    except TimeoutError:
        print("[ERROR] Google Scholar request timed out after 4 minutes")
        signal.alarm(0)
        return []
    except Exception as e:
        print(f"[ERROR] Error fetching data from Google Scholar: {e}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
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