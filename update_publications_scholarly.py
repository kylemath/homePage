import re
from bs4 import BeautifulSoup
import os

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
    try:
        from scholarly import scholarly
        
        print(f"Searching for author: {author_name}")
        
        if author_id:
            # Use specific author ID if provided
            print(f"Using author ID: {author_id}")
            try:
                author = scholarly.search_author_id(author_id)
                author = scholarly.fill(author)
            except Exception as e:
                print(f"Error with author ID {author_id}: {e}")
                print("Falling back to name search...")
                search_query = scholarly.search_author(author_name)
                author = next(search_query)
                author = scholarly.fill(author)
        else:
            # Search for the author by name
            search_query = scholarly.search_author(author_name)
            author = next(search_query)
            author = scholarly.fill(author)
        
        print(f"Found author: {author.get('name', 'Unknown')}")
        
        publications = []
        
        # Fetch ALL publications
        total_publications = len(author.get('publications', []))
        print(f"Fetching all {total_publications} publications...")
        
        # Process all publications
        for i, pub in enumerate(author.get('publications', [])):
            try:
                # Fill publication details
                pub_filled = scholarly.fill(pub)
                
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
                
                print(f"Processed {i+1}/{total_publications}: {title} ({year}) - {first_author}")
                
            except Exception as e:
                print(f"Error processing publication {i}: {e}")
                continue
        
        # Sort publications by year (most recent first)
        publications.sort(key=lambda x: x['year_int'], reverse=True)
        
        print(f"\nFetched and sorted {len(publications)} total publications:")
        for i, pub in enumerate(publications[:10], 1):  # Show first 10 as preview
            print(f"{i}. {pub['title']} ({pub['year']}) - {pub['first_author']}")
        if len(publications) > 10:
            print(f"... and {len(publications) - 10} more")
        
        return publications
        
    except ImportError:
        print("Error: 'scholarly' library not installed. Install with: pip install scholarly")
        return []
    except Exception as e:
        print(f"Error fetching data from Google Scholar: {e}")
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
        pattern = r'(<h2 id="publications">Recent Publications</h2>\s*<ul>)(.*?)(</ul>)'
        replacement = rf'\1\n{publications_html}\3'
        
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
    
    # Default author name
    author_name = "Kyle E Mathewson"
    author_id = "wgK6LCYAAAAJ"  # Kyle's Google Scholar ID
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        author_name = sys.argv[1]
    
    # Override author ID if provided as second argument
    if len(sys.argv) > 2:
        author_id = sys.argv[2]
    
    print(f"Fetching ALL publications for: {author_name}")
    if author_id:
        print(f"Using Google Scholar ID: {author_id}")
    print("Note: This may take a while as we fetch all publication information...")
    
    # Fetch all publications
    publications = get_google_scholar_publications_scholarly(author_name, author_id=author_id)
    
    if publications:
        print(f"\nFound {len(publications)} total publications")
        
        # Update HTML file
        success = update_html_with_publications(publications)
        if success:
            print(f"\nSuccessfully updated index.html with all {len(publications)} publications!")
        else:
            print("\nFailed to update HTML file")
    else:
        print("No publications found. Please check the author name or try again later.")
        # Still update HTML with placeholder
        update_html_with_publications([])

if __name__ == "__main__":
    main() 