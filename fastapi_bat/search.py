from fastapi import APIRouter, Query
from typing import Optional
import os
import re
from pathlib import Path
from config import settings

router = APIRouter()

# Constants
SIDE_CHARS = 15

def list_files(search_dir: Optional[str] = None, search_in: list = None) -> list:
    """Recursively list all files in a directory with specified extensions"""
    if search_in is None:
        search_in = settings.search_extensions
    if search_dir is None:
        search_dir = settings.search_dir
    
    result = []
    search_path = Path(search_dir)
    
    if search_path.is_dir():
        for item in search_path.rglob('*'):
            if item.is_file() and item.suffix.lstrip('.') in search_in:
                result.append(str(item))
    
    return result

def get_file_extension(filename: str) -> str:
    """Get the extension of a file"""
    return Path(filename).suffix.lstrip('.')

def find_in_text(text: str, search_term: str, case_sensitive: bool = False) -> list:
    """Find all occurrences of search term in text"""
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(search_term), flags)
    matches = []
    for match in pattern.finditer(text):
        matches.append((match.group(), match.start(), match.end()))
    return matches

@router.get("/search")
async def search(
    s: str = Query(..., alias="s", description="Search term"),
    filter_pattern: str = Query("*", alias="filter", description="Filter pattern for file search"),
    template: str = Query("<h5 class='search_title'><a target='_top' href='#{href}' class='search_link'>#{title}</a></h5><p>...#{token}...</p><p class='match'><em>Terms matched: #{count} - URL: #{href}</em></p>", description="Result template"),
    live_count: Optional[int] = Query(None, alias="liveCount", description="Limit for live search results"),
    live_search: Optional[str] = Query(None, alias="liveSearch", description="Live search flag")
):
    """
    Search functionality similar to rd-search.php
    """
    if not s or s == "?s=":
        s = ""
    
    # Replace + with space in search term
    search_term = s.replace('+', ' ')
    search_term_lower = search_term.lower()
    search_term_length = len(search_term)
    
    # Starting search directory (relative to the web root)
    search_dir = ".."  # Adjust this based on your site structure
    
    # File extensions to search in
    search_in = ['html', 'htm']
    
    # Get all files to search
    files = list_files(search_dir, search_in)
    
    final_result = []
    file_count = 0
    
    for file_path in files:
        # Skip if filter doesn't match
        if filter_pattern != "*" and not Path(file_path).match(filter_pattern):
            continue
            
        try:
            # Check file size
            if os.path.getsize(file_path) == 0:
                continue
                
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                contents = f.read()
            
            # Extract page title
            title_match = re.search(r'<title>(.*?)</title>', contents, re.IGNORECASE)
            page_title = title_match.group(1) if title_match else ""
            
            # Extract body content
            body_match = re.search(r'<body.*?>(.*?)</body>', contents, re.DOTALL | re.IGNORECASE)
            body_content = body_match.group(1) if body_match else contents
            
            # Remove HTML tags and normalize whitespace
            clean_content = re.sub(r'<[^>]+>', ' ', body_content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            # Find occurrences of search term
            found_matches = []
            for match in re.finditer(re.escape(search_term), clean_content, re.IGNORECASE):
                found_matches.append((match.group(), match.start(), match.end()))
            
            # Process results
            result_item = {
                'page_title': page_title,
                'file_name': file_path,
                'search_result': []
            }
            
            # Add meta information based on template tokens
            template_tokens = re.findall(r'#\{((?!title|href|token|count)[a-z]*)\}', template, re.IGNORECASE)
            for token in template_tokens:
                meta_match = re.search(r'<meta\s+name=[\'"]' + re.escape(token) + r'[\'"]\s+content=[\'"](.*)[\'"]\s*>', contents, re.IGNORECASE)
                if meta_match:
                    result_item[token] = meta_match.group(1)
            
            # Generate result snippets
            for match in found_matches:
                _, pos_start, pos_end = match
                
                # Calculate snippet boundaries
                side_chars = SIDE_CHARS
                if pos_start < SIDE_CHARS:
                    actual_start = 0
                    side_chars = pos_start
                else:
                    actual_start = pos_start - side_chars
                
                if live_search:
                    pos_end = pos_start + search_term_length + SIDE_CHARS + 15
                else:
                    pos_end = pos_start + search_term_length + SIDE_CHARS * 9
                
                snippet = clean_content[actual_start:pos_end]
                
                # Highlight search term in snippet
                highlighted_snippet = re.sub(
                    re.escape(search_term), 
                    f'<span class="search">{search_term}</span>', 
                    snippet, 
                    flags=re.IGNORECASE
                )
                
                result_item['search_result'].append(highlighted_snippet)
            
            # Add empty result if no matches found
            if not found_matches:
                result_item['search_result'].append('')
                
            final_result.append(result_item)
            file_count += 1
            
        except Exception as e:
            # Skip files that can't be read
            print(f"Error reading file {file_path}: {str(e)}")
            continue
    
    # Sort results by number of matches (descending)
    final_result.sort(key=lambda x: len(x['search_result']), reverse=True)
    
    # Prepare response
    results = []
    match_count = 0
    
    for item in final_result:
        if item['search_result'] and any(item['search_result']):
            match_count += 1
            # Limit results if live search is enabled
            if live_search and live_count and len(results) >= live_count:
                continue
                
            # Apply template to format result
            replacement_values = [
                item['page_title'],
                item['file_name'],
                item['search_result'][0] if item['search_result'] else '',
                len(item['search_result'])
            ]
            
            formatted_result = template
            formatted_result = formatted_result.replace('#{title}', replacement_values[0])
            formatted_result = formatted_result.replace('#{href}', replacement_values[1])
            formatted_result = formatted_result.replace('#{token}', replacement_values[2])
            formatted_result = formatted_result.replace('#{count}', str(replacement_values[3]))
            
            # Replace any additional template tokens
            for token in template_tokens:
                token_value = item.get(token, '')
                formatted_result = formatted_result.replace(f'#{{{token}}}', str(token_value))
            
            results.append({
                'title': item['page_title'],
                'href': item['file_name'],
                'snippet': item['search_result'][0] if item['search_result'] else '',
                'count': len(item['search_result']),
                'formatted': formatted_result
            })
    
    # Prepare final response
    response_html = f"""
    <div id="search-results">
        {f"<div class='search-quick-result'>Quick Results</div>" if live_search else ""}
        <ol class="search_list">
    """
    
    if match_count > 0:
        for result in results:
            response_html += f"""
            <li class="result-item">
                {result['formatted']}
            </li>
            """
    else:
        response_html += f'<li><div class="search_error">No results found for "<span class="search">{search_term}</span>"<div/></li>'
    
    # Add link to see all results if in live search mode
    if live_search and match_count > 0:
        response_html += f"""
        <li class="search_all">
            <a href='search-results.html?s={s}&filter={filter_pattern}' class="search_submit">
                See other {sum(len(item['search_result']) for item in final_result)} {f"result on " if sum(len(item['search_result']) for item in final_result) < 2 else "results"}
            </a>
        </li>
        """
    
    response_html += """
        </ol>
    </div>
    """
    
    return {
        "query": search_term,
        "results_count": match_count,
        "total_matches": sum(len(item['search_result']) for item in final_result),
        "results": results,
        "html": response_html
    }