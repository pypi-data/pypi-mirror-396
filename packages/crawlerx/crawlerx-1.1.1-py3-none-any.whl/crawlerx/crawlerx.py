import argparse
import os
import json
import threading
import sys
import queue
import signal
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from urllib.parse import urlparse, parse_qs, urljoin, urldefrag, urlencode, quote
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pickle

# Global for signal handling
state_to_save = None
output_path_global = None
domain_global = None
stop_event = threading.Event()

# Common paths for discovery
COMMON_PATHS = [
    '/admin', '/administrator', '/login', '/wp-admin', '/wp-login.php',
    '/api', '/api/v1', '/api/v2', '/rest', '/graphql',
    '/backup', '/backups', '/old', '/test', '/dev', '/staging',
    '/config', '/configuration', '/settings', '/setup',
    '/upload', '/uploads', '/files', '/documents', '/media',
    '/static', '/assets', '/public', '/private',
    '/user', '/users', '/account', '/profile', '/dashboard',
    '/search', '/cart', '/checkout', '/payment',
    '/robots.txt', '/sitemap.xml', '/.git', '/.env', '/phpinfo.php'
]

# JavaScript noise to filter out
JS_NOISE = [
    'Msxml2.XMLHTTP', 'Microsoft.XMLHTTP', 'ActiveXObject',
    'XMLHttpRequest', 'text/xml', 'text/html', 'application/json',
    'text/plain', 'application/x-www-form-urlencoded',
    'Netscape', 'Microsoft', 'Windows', 'Linux', 'Mac',
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS',
    'true', 'false', 'null', 'undefined', 'NaN'
]

def signal_handler(sig, frame):
    print("\n[!] Crawling stopped by user (Ctrl+C).", flush=True)
    stop_event.set()
    if output_path_global:
        save_crawl_state(state_to_save, output_path_global, domain_global)
        print(f"[*] Crawl state saved to {os.path.join(output_path_global, 'crawl_state.pkl')}", flush=True)
    sys.exit(0)

def is_valid_url(url, headers, session):
    try:
        result = session.head(url, timeout=args.timeout, headers=headers, allow_redirects=True)
        return result.status_code < 400
    except requests.RequestException:
        return False

def get_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.replace('www.', '')

def create_output_directory(base_url, output_dir):
    domain = get_domain(base_url)
    folder_name = f"crawlerx_{domain}"
    output_path = os.path.join(output_dir, folder_name)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(os.path.join(output_path, 'endpoints'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'get'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'post'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'api'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'resources'), exist_ok=True)
    if args.structure:
        os.makedirs(os.path.join(output_path, 'structure'), exist_ok=True)
    return output_path, domain, folder_name

def save_crawl_state(state, output_path, domain):
    state_file = os.path.join(output_path, 'crawl_state.pkl')
    with open(state_file, 'wb') as f:
        pickle.dump(state, f)

def is_valid_discovered_url(url, base_url):
    """Enhanced URL validation to filter false positives"""
    try:
        parsed = urlparse(url)
        
        # Must have valid scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Must have netloc
        if not parsed.netloc:
            return False
        
        # Filter out JavaScript noise
        path = parsed.path
        for noise in JS_NOISE:
            if noise in path:
                return False
        
        # Path shouldn't contain spaces or special chars
        if ' ' in path or '\n' in path or '\t' in path:
            return False
        
        # Filter out JavaScript code patterns
        if any(x in path for x in ['function', 'var ', 'let ', 'const ', '()', '=>']):
            return False
        
        # Must be within domain
        if not is_within_domain(url, base_url):
            return False
        
        # Check exclusions
        if should_exclude(url, args.exclude):
            return False
        
        return True
    
    except Exception:
        return False

def write_endpoints(all_urls, output_path):
    """Save all discovered endpoints"""
    if not output_path or not all_urls:
        return
    
    # Filter and validate URLs
    valid_urls = {url for url in all_urls if url.startswith('http')}
    
    urls_with_params = set()
    urls_without_params = set()
    
    for url in valid_urls:
        if parse_qs(urlparse(url).query):
            urls_with_params.add(url)
        else:
            urls_without_params.add(url)
    
    # Save all endpoints
    with open(os.path.join(output_path, 'endpoints', 'all_endpoints.txt'), 'w', encoding='utf-8') as f:
        for url in sorted(valid_urls):
            f.write(f"{url}\n")
    
    with open(os.path.join(output_path, 'endpoints', 'all_endpoints.json'), 'w', encoding='utf-8') as f:
        json.dump(list(sorted(valid_urls)), f, indent=2)
    
    # Save parameterized endpoints
    if urls_with_params:
        with open(os.path.join(output_path, 'endpoints', 'parameterized.txt'), 'w', encoding='utf-8') as f:
            for url in sorted(urls_with_params):
                f.write(f"{url}\n")
        
        with open(os.path.join(output_path, 'endpoints', 'parameterized.json'), 'w', encoding='utf-8') as f:
            json.dump(list(sorted(urls_with_params)), f, indent=2)
    
    # Save non-parameterized endpoints
    if urls_without_params:
        with open(os.path.join(output_path, 'endpoints', 'non_parameterized.txt'), 'w', encoding='utf-8') as f:
            for url in sorted(urls_without_params):
                f.write(f"{url}\n")

def write_get_requests(get_params_data, output_path):
    """Save GET requests with parameters"""
    if not output_path or not get_params_data:
        return
    
    # Save all GET URLs
    all_get_urls = set()
    for item in get_params_data:
        all_get_urls.add(item['url'])
    
    with open(os.path.join(output_path, 'get', 'get_urls.txt'), 'w', encoding='utf-8') as f:
        for url in sorted(all_get_urls):
            f.write(f"{url}\n")
    
    # Save GET parameters details
    with open(os.path.join(output_path, 'get', 'get_params.json'), 'w', encoding='utf-8') as f:
        json.dump(get_params_data, f, indent=2)
    
    # Save raw GET requests
    for i, item in enumerate(get_params_data):
        parsed = urlparse(item['url'])
        path = parsed.path.lstrip('/') or 'index'
        basename = os.path.basename(path)
        if '.' in basename:
            name = '.'.join(basename.split('.')[:-1])
        else:
            name = basename
        
        filename = os.path.join(output_path, 'get', f"{name}_get_{i}.req")
        
        path_with_params = parsed.path
        if parsed.query:
            path_with_params += f"?{parsed.query}"
        
        raw_request = f"GET {path_with_params} HTTP/1.1\r\n"
        raw_request += f"Host: {parsed.netloc}\r\n"
        raw_request += "\r\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(raw_request)

def write_post_requests(post_params_data, output_path):
    """Save POST requests with body parameters"""
    if not output_path or not post_params_data:
        return
    
    # Save all POST URLs
    all_post_urls = set()
    for item in post_params_data:
        all_post_urls.add(item['url'])
    
    with open(os.path.join(output_path, 'post', 'post_urls.txt'), 'w', encoding='utf-8') as f:
        for url in sorted(all_post_urls):
            f.write(f"{url}\n")
    
    # Save POST parameters details
    with open(os.path.join(output_path, 'post', 'post_params.json'), 'w', encoding='utf-8') as f:
        json.dump(post_params_data, f, indent=2)
    
    # Save raw POST requests
    for i, item in enumerate(post_params_data):
        parsed = urlparse(item['url'])
        path = parsed.path.lstrip('/') or 'index'
        basename = os.path.basename(path)
        if '.' in basename:
            name = '.'.join(basename.split('.')[:-1])
        else:
            name = basename
        
        filename = os.path.join(output_path, 'post', f"{name}_post_{i}.req")
        
        body = urlencode(item['params'])
        
        path_full = parsed.path
        if parsed.query:
            path_full += f"?{parsed.query}"
        
        raw_request = f"POST {path_full} HTTP/1.1\r\n"
        raw_request += f"Host: {parsed.netloc}\r\n"
        raw_request += "Content-Type: application/x-www-form-urlencoded\r\n"
        raw_request += f"Content-Length: {len(body)}\r\n"
        raw_request += "\r\n"
        raw_request += body
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(raw_request)

def write_api_endpoints(api_urls, output_path):
    """Save discovered API endpoints"""
    if not output_path or not api_urls:
        return
    
    with open(os.path.join(output_path, 'api', 'api_endpoints.txt'), 'w', encoding='utf-8') as f:
        for url in sorted(api_urls):
            f.write(f"{url}\n")
    
    with open(os.path.join(output_path, 'api', 'api_endpoints.json'), 'w', encoding='utf-8') as f:
        json.dump(list(sorted(api_urls)), f, indent=2)

def write_resources(resource_data, output_path):
    """Save categorized resources"""
    if not output_path or not resource_data:
        return
    
    categorized = {
        'images': set(),
        'scripts': set(),
        'stylesheets': set(),
        'fonts': set(),
        'media': set(),
        'documents': set(),
        'other': set()
    }
    
    for url, resource_type in resource_data:
        if url.startswith('http'):
            categorized[resource_type].add(url)
    
    for category, urls in categorized.items():
        if urls:
            with open(os.path.join(output_path, 'resources', f"{category}.txt"), 'w', encoding='utf-8') as f:
                for url in sorted(urls):
                    f.write(f"{url}\n")
            
            with open(os.path.join(output_path, 'resources', f"{category}.json"), 'w', encoding='utf-8') as f:
                json.dump(list(sorted(urls)), f, indent=2)

def write_structure_tree(tree_data, output_path=None):
    def build_ascii_tree(urls, base_netloc):
        if not urls:
            return "No URLs found to build site structure."
        tree = {}
        for url in sorted(urls):
            parsed = urlparse(url)
            netloc = parsed.netloc
            path = parsed.path or '/'
            if parsed.query:
                path += f"?{parsed.query}"
            components = [netloc] + [comp for comp in path.split('/') if comp]
            current = tree
            for i, comp in enumerate(components):
                if comp not in current:
                    current[comp] = {'__url__': url, '__children__': {}}
                current = current[comp]['__children__']
        def render_tree(node, prefix="", depth=0):
            lines = []
            keys = sorted([k for k in node.keys() if k != '__children__' and k != '__url__'])
            for i, key in enumerate(keys):
                is_last = i == len(keys) - 1
                line_prefix = prefix + ("└── " if is_last else "├── ")
                lines.append(f"{line_prefix}{key}")
                child_lines = render_tree(node[key]['__children__'], prefix + ("    " if is_last else "│   "), depth + 1)
                lines.extend(child_lines)
            return lines
        return "\n".join([f"Site Structure for {base_netloc}:"] + render_tree(tree))
   
    base_netloc = urlparse(next(iter(tree_data), '')).netloc if tree_data else "unknown"
    ascii_tree = build_ascii_tree(tree_data, base_netloc)
    if output_path:
        filename = os.path.join(output_path, 'structure', 'structure.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(ascii_tree)
    return ascii_tree

def can_fetch(url, user_agent, headers, session):
    if stop_event.is_set():
        return False
    
    if not args.respect_robots:
        return True
    
    rp = RobotFileParser()
    try:
        robots_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt"
        response = session.get(robots_url, timeout=args.timeout, headers=headers)
        rp.set_url(robots_url)
        rp.parse(response.text.splitlines())
        return rp.can_fetch(user_agent, url)
    except requests.RequestException:
        return True

def should_exclude(url, exclude_extensions):
    if not exclude_extensions:
        return False
    exclude_list = [ext.strip() for ext in exclude_extensions.split(',')]
    return any(url.lower().endswith(f'.{ext}') for ext in exclude_list)

def is_within_domain(url, base_url):
    base_netloc = urlparse(base_url).netloc.replace('www.', '')
    url_netloc = urlparse(url).netloc.replace('www.', '')
    
    if args.sub:
        return base_netloc in url_netloc or url_netloc.endswith(f".{base_netloc}")
    return base_netloc == url_netloc

def categorize_resource(url):
    """Categorize resource by file extension"""
    url_lower = url.lower()
    
    if any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp']):
        return 'images'
    elif url_lower.endswith('.js'):
        return 'scripts'
    elif url_lower.endswith('.css'):
        return 'stylesheets'
    elif any(url_lower.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.eot', '.otf']):
        return 'fonts'
    elif any(url_lower.endswith(ext) for ext in ['.mp4', '.mp3', '.webm', '.ogg', '.wav', '.avi']):
        return 'media'
    elif any(url_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz']):
        return 'documents'
    else:
        return 'other'

def fuzz_parameters(url, session, all_urls, lock):
    """Fuzz numeric and common parameter values"""
    if not args.fuzz_params:
        return
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    if not query_params:
        return
    
    fuzzed_urls = set()
    
    for param, values in query_params.items():
        if values and values[0].isdigit():
            base_val = int(values[0])
            for i in range(max(1, base_val - 2), base_val + 10):
                new_params = query_params.copy()
                new_params[param] = [str(i)]
                new_query = urlencode(new_params, doseq=True)
                fuzzed_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                fuzzed_urls.add(fuzzed_url)
    
    for fuzzed_url in fuzzed_urls:
        if stop_event.is_set():
            break
        try:
            resp = session.head(fuzzed_url, timeout=args.timeout, allow_redirects=True)
            if resp.status_code < 400:
                with lock:
                    all_urls.add(fuzzed_url)
                if args.verbose:
                    print(f"[FUZZ] Found: {fuzzed_url}", flush=True)
        except requests.RequestException:
            pass

def probe_common_paths(base_url, session, all_urls, lock):
    """Probe for common paths and files"""
    if not args.common_paths:
        return
    
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    for path in COMMON_PATHS:
        if stop_event.is_set():
            break
        
        test_url = f"{base}{path}"
        
        try:
            resp = session.head(test_url, timeout=args.timeout, allow_redirects=False)
            if resp.status_code < 400:
                with lock:
                    all_urls.add(test_url)
                if args.verbose:
                    print(f"[PATH] Found: {test_url} (Status: {resp.status_code})", flush=True)
        except requests.RequestException:
            pass
        
        time.sleep(args.delay)

def extract_urls_from_html(soup, base_url):
    """Extract all URLs from HTML elements"""
    urls = set()
    
    tag_attributes = [
        ('a', ['href']),
        ('link', ['href']),
        ('form', ['action']),
        ('img', ['src', 'data-src', 'data-lazy-src']),
        ('script', ['src']),
        ('iframe', ['src']),
        ('video', ['src', 'poster']),
        ('audio', ['src']),
        ('source', ['src', 'srcset']),
        ('button', ['formaction']),
        ('object', ['data']),
        ('embed', ['src']),
        ('meta', ['content']),
        ('base', ['href']),
    ]
    
    for tag_name, attrs in tag_attributes:
        for tag in soup.find_all(tag_name):
            for attr in attrs:
                url = tag.get(attr)
                if url:
                    try:
                        if tag_name == 'meta' and attr == 'content':
                            if 'url=' in url.lower():
                                match = re.search(r'url=(.*?)(?:$|;|\s)', url, re.I)
                                if match:
                                    url = match.group(1)
                                else:
                                    continue
                            else:
                                continue
                        
                        if attr == 'srcset':
                            srcset_urls = re.findall(r'(\S+?)(?:\s+\d+[wx])?(?:,|$)', url)
                            for srcset_url in srcset_urls:
                                full_url = urljoin(base_url, srcset_url.strip())
                                full_url = urldefrag(full_url)[0]
                                if is_valid_discovered_url(full_url, base_url):
                                    urls.add(full_url)
                        else:
                            # Handle URLs - don't strip too aggressively
                            url_clean = url.strip()
                            
                            # Special handling for relative URLs with parameters (like showimage.php?file=...)
                            # urljoin handles these correctly
                            full_url = urljoin(base_url, url_clean)
                            full_url = urldefrag(full_url)[0]
                            
                            if is_valid_discovered_url(full_url, base_url):
                                urls.add(full_url)
                                
                                # Also extract the URL without size/dimension parameters for images
                                # e.g., showimage.php?file=./pictures/6.jpg&size=160 -> also add showimage.php?file=./pictures/6.jpg
                                if tag_name == 'img' and '&' in full_url:
                                    parsed = urlparse(full_url)
                                    if parsed.query:
                                        params = parse_qs(parsed.query)
                                        # If there's a 'file' or 'image' or 'src' parameter, create a version without size params
                                        for key_param in ['file', 'image', 'src', 'path', 'img']:
                                            if key_param in params:
                                                clean_params = {k: v for k, v in params.items() if k not in ['size', 'width', 'height', 'w', 'h', 'thumb', 'thumbnail']}
                                                if clean_params != params:  # Only if we actually removed something
                                                    clean_query = urlencode(clean_params, doseq=True)
                                                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"
                                                    if is_valid_discovered_url(clean_url, base_url):
                                                        urls.add(clean_url)
                                                break
                    except (ValueError, AttributeError, Exception):
                        pass
    
    # Extract from data-* attributes
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.startswith('data-') and attr not in ['data-src', 'data-lazy-src']:
                value = tag.get(attr)
                if value and isinstance(value, str) and ('/' in value or value.startswith('http') or '?' in value):
                    try:
                        full_url = urljoin(base_url, value.strip())
                        full_url = urldefrag(full_url)[0]
                        if is_valid_discovered_url(full_url, base_url):
                            urls.add(full_url)
                    except ValueError:
                        pass
    
    return urls

def extract_urls_from_javascript(soup, base_url):
    """Extract URLs from inline JavaScript and event handlers"""
    urls = set()
    
    for script in soup.find_all('script'):
        if not script.get('src') and script.string:
            extracted = extract_urls_from_text(script.string, base_url)
            urls.update(extracted)
    
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.startswith('on') or attr in ['style']:
                value = tag.get(attr)
                if value:
                    extracted = extract_urls_from_text(value, base_url)
                    urls.update(extracted)
    
    return urls

def extract_urls_from_text(text, base_url):
    """Extract URLs from arbitrary text with better filtering"""
    urls = set()
    
    patterns = [
        r'(?:https?:)?//[^\s"\'\)<>]+',
        r'(?:["\']|(?:url\())(/[^\s"\')<>]+)',
        r'["\']([/\w\-\.]+(?:/[\w\-\.]*)*(?:\?[^\s"\']*)?)["\']',
        r'(?:fetch|ajax|get|post|put|delete|axios)\s*\(\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.I)
        for match in matches:
            url = match[0] if isinstance(match, tuple) else match
            url = url.strip().strip('"\'()[]')
            
            if len(url) < 2 or url in ['/', '#'] or url.startswith('data:'):
                continue
            
            try:
                full_url = urljoin(base_url, url)
                full_url = urldefrag(full_url)[0]
                
                if is_valid_discovered_url(full_url, base_url):
                    urls.add(full_url)
            except (ValueError, Exception):
                pass
    
    return urls

def extract_api_endpoints(soup, response_text, base_url):
    """Extract potential API endpoints"""
    api_urls = set()
    
    api_patterns = [
        r'["\']([/\w\-]+/api/[^\s"\']*)["\']',
        r'["\']([/\w\-]+/v\d+/[^\s"\']*)["\']',
        r'["\']([/\w\-]+/rest/[^\s"\']*)["\']',
        r'["\']([/\w\-]+/graphql[^\s"\']*)["\']',
        r'["\']([/\w\-]+\.json[^\s"\']*)["\']',
        r'["\']([/\w\-]+\.xml[^\s"\']*)["\']',
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, response_text, re.I)
        for match in matches:
            try:
                full_url = urljoin(base_url, match)
                full_url = urldefrag(full_url)[0]
                if is_valid_discovered_url(full_url, base_url):
                    api_urls.add(full_url)
            except ValueError:
                pass
    
    return api_urls

def extract_get_post_data(soup, base_url):
    """Extract GET and POST data from forms"""
    get_data = []
    post_data = []
    
    for form in soup.find_all('form'):
        action = form.get('action')
        form_url = urljoin(base_url, action) if action else base_url
        form_url = urldefrag(form_url)[0]
        
        if not is_valid_discovered_url(form_url, base_url):
            continue
        
        method = form.get('method', 'GET').upper()
        
        # Extract form inputs
        params = {}
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            name = input_tag.get('name')
            if name:
                value = input_tag.get('value', '')
                input_type = input_tag.get('type', 'text')
                
                if not value:
                    if input_type == 'email':
                        value = 'test@example.com'
                    elif input_type == 'password':
                        value = 'password123'
                    elif input_type == 'number':
                        value = '1'
                    elif input_type == 'checkbox':
                        value = 'on'
                    elif input_type == 'radio':
                        value = 'option1'
                    else:
                        value = 'test'
                
                params[name] = value
        
        if params:
            if method == 'POST':
                post_data.append({
                    'url': form_url,
                    'params': params
                })
            else:  # GET
                # Build URL with parameters
                query_string = urlencode(params)
                get_url = f"{form_url}?{query_string}" if '?' not in form_url else f"{form_url}&{query_string}"
                get_data.append({
                    'url': get_url,
                    'params': params
                })
    
    return get_data, post_data

def parse_headers(header_string):
    headers = {}
    if not header_string:
        return headers
    try:
        for header in header_string.split(';'):
            header = header.strip()
            if not header:
                continue
            if ':' not in header:
                continue
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    except Exception as e:
        if args.verbose:
            print(f"Error parsing headers: {e}", flush=True)
    return headers

def crawl_url(current_url, current_depth, session, visited, all_urls, get_params_data, get_hashes, post_params_data, post_hashes, api_urls, resource_data, to_visit, lock, stop_event, output_path):
    """Crawl a single URL"""
    if stop_event.is_set():
        return
    
    if current_depth > args.depth:
        return
    
    with lock:
        if current_url in visited:
            return
        visited.add(current_url)
    
    if not can_fetch(current_url, args.ua, session.headers, session):
        if args.verbose:
            print(f"[!] Blocked by robots.txt: {current_url}", flush=True)
        return
    
    if args.verbose:
        print(f"[*] Crawling: {current_url} (Depth: {current_depth})", flush=True)
    
    try:
        if stop_event.is_set():
            return
        
        response = session.get(current_url, timeout=args.timeout, allow_redirects=True)
        
        if response.status_code >= 400:
            if args.verbose:
                print(f"[!] Status {response.status_code}: {current_url}", flush=True)
            return
        
        with lock:
            all_urls.add(current_url)
        
        # Check if URL has GET parameters
        parsed = urlparse(current_url)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if query_params:
                param_dict = {k: v[0] if v else '' for k, v in query_params.items()}
                get_hash = hash((current_url, frozenset(param_dict.items())))
                with lock:
                    if get_hash not in get_hashes:
                        get_params_data.append({
                            'url': current_url,
                            'params': param_dict
                        })
                        get_hashes.add(get_hash)
                        if args.verbose:
                            print(f"[GET] {current_url}", flush=True)
        
        # Fuzz parameters if enabled
        fuzz_parameters(current_url, session, all_urls, lock)
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        # Handle CSS
        if 'text/css' in content_type or current_url.lower().endswith('.css'):
            css_urls = extract_urls_from_text(response.text, current_url)
            with lock:
                for url in css_urls:
                    if is_valid_discovered_url(url, current_url):
                        resource_data.add((url, categorize_resource(url)))
                        all_urls.add(url)
            return
        
        # Handle JavaScript
        if 'javascript' in content_type or current_url.lower().endswith('.js'):
            js_urls = extract_urls_from_text(response.text, current_url)
            js_api_urls = extract_api_endpoints(None, response.text, current_url)
            with lock:
                for url in js_urls:
                    if is_valid_discovered_url(url, current_url):
                        resource_data.add((url, categorize_resource(url)))
                        all_urls.add(url)
                for url in js_api_urls:
                    if is_valid_discovered_url(url, current_url):
                        api_urls.add(url)
                        all_urls.add(url)
            return
        
        # Handle JSON/XML
        if any(ct in content_type for ct in ['json', 'xml']):
            text_urls = extract_urls_from_text(response.text, current_url)
            with lock:
                for url in text_urls:
                    if is_valid_discovered_url(url, current_url):
                        all_urls.add(url)
                api_urls.add(current_url)
            return
        
        # Handle non-HTML
        if 'text/html' not in content_type:
            with lock:
                resource_data.add((current_url, categorize_resource(current_url)))
            return
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract everything
        html_urls = extract_urls_from_html(soup, current_url)
        js_urls = extract_urls_from_javascript(soup, current_url)
        api_endpoints = extract_api_endpoints(soup, response.text, current_url)
        page_get_data, page_post_data = extract_get_post_data(soup, current_url)
        
        discovered_urls = html_urls | js_urls | api_endpoints
        
        with lock:
            # Validate and add URLs
            for url in discovered_urls:
                if is_valid_discovered_url(url, current_url):
                    all_urls.add(url)
                    # Show interesting URLs in verbose mode
                    if args.verbose:
                        parsed = urlparse(url)
                        if parsed.query:
                            params = parse_qs(parsed.query)
                            # Highlight URLs with interesting parameters
                            if any(key in params for key in ['file', 'path', 'img', 'image', 'src', 'url', 'page', 'id', 'cat']):
                                print(f"[INTERESTING] {url}", flush=True)
            
            for url in api_endpoints:
                if is_valid_discovered_url(url, current_url):
                    api_urls.add(url)
            
            # Add GET requests
            for get_item in page_get_data:
                get_hash = hash((get_item['url'], frozenset(get_item['params'].items())))
                if get_hash not in get_hashes:
                    get_params_data.append(get_item)
                    get_hashes.add(get_hash)
                    if args.verbose:
                        print(f"[GET] {get_item['url']}", flush=True)
            
            # Add POST requests
            for post_item in page_post_data:
                post_hash = hash((post_item['url'], frozenset(post_item['params'].items())))
                if post_hash not in post_hashes:
                    post_params_data.append(post_item)
                    post_hashes.add(post_hash)
                    if args.verbose:
                        print(f"[POST] {post_item['url']} ({len(post_item['params'])} params)", flush=True)
            
            # Categorize resources
            for url in discovered_urls:
                if is_valid_discovered_url(url, current_url):
                    category = categorize_resource(url)
                    resource_data.add((url, category))
            
            # Queue for crawling
            if current_depth < args.depth:
                for url in discovered_urls:
                    if is_valid_discovered_url(url, current_url) and url not in visited:
                        to_visit.put((url, current_depth + 1))
        
        # Incremental save
        if output_path:
            write_endpoints(all_urls, output_path)
            write_get_requests(get_params_data, output_path)
            write_post_requests(post_params_data, output_path)
            write_api_endpoints(api_urls, output_path)
            write_resources(resource_data, output_path)
        
        if not stop_event.is_set():
            time.sleep(args.delay)
    
    except requests.RequestException as e:
        if args.verbose:
            print(f"[!] Request failed: {current_url}: {e}", flush=True)
    except Exception as e:
        if args.verbose:
            print(f"[!] Error: {current_url}: {e}", flush=True)

def crawl(url):
    """Main crawling function"""
    global state_to_save, output_path_global
    
    visited = set()
    all_urls = set()
    get_params_data = []
    get_hashes = set()
    post_params_data = []
    post_hashes = set()
    api_urls = set()
    resource_data = set()
    lock = threading.Lock()
    to_visit = queue.Queue()
    
    to_visit.put((url, 0))
    
    # Resume from state
    if args.cont:
        try:
            with open(args.cont, 'rb') as f:
                state = pickle.load(f)
                visited = state.get('visited', set())
                all_urls = state.get('all_urls', set())
                get_params_data = state.get('get_params_data', [])
                get_hashes = {hash((g['url'], frozenset(g['params'].items()))) for g in get_params_data}
                post_params_data = state.get('post_params_data', [])
                post_hashes = {hash((p['url'], frozenset(p['params'].items()))) for p in post_params_data}
                api_urls = state.get('api_urls', set())
                resource_data = state.get('resource_data', set())
                
                for item in state.get('to_visit', []):
                    to_visit.put(item)
                
                print(f"[*] Resumed from {args.cont}", flush=True)
                print(f"[*] Loaded: {len(visited)} visited, {len(all_urls)} URLs", flush=True)
        except Exception as e:
            print(f"[!] Failed to load state: {e}", flush=True)
    
    # Setup session
    session = requests.Session()
    session.headers.update({'User-Agent': args.ua})
    
    if args.headers:
        session.headers.update(parse_headers(args.headers))
    
    if args.proxy:
        session.proxies.update(args.proxy)
    
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Probe common paths first
    if args.common_paths:
        print("[*] Probing common paths...", flush=True)
        probe_common_paths(url, session, all_urls, lock)
        for discovered_url in list(all_urls):
            to_visit.put((discovered_url, 0))
    
    def update_state():
        global state_to_save
        state_to_save = {
            'visited': visited.copy(),
            'all_urls': all_urls.copy(),
            'get_params_data': get_params_data.copy(),
            'post_params_data': post_params_data.copy(),
            'api_urls': api_urls.copy(),
            'resource_data': resource_data.copy(),
            'to_visit': list(to_visit.queue)
        }
    
    update_state()
    
    # Crawl with thread pool
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        
        while (not to_visit.empty() or futures) and not stop_event.is_set():
            while len(futures) < args.threads and not to_visit.empty() and not stop_event.is_set():
                try:
                    current_url, current_depth = to_visit.get_nowait()
                    
                    with lock:
                        if current_url in visited:
                            continue
                    
                    future = executor.submit(
                        crawl_url,
                        current_url,
                        current_depth,
                        session,
                        visited,
                        all_urls,
                        get_params_data,
                        get_hashes,
                        post_params_data,
                        post_hashes,
                        api_urls,
                        resource_data,
                        to_visit,
                        lock,
                        stop_event,
                        output_path_global
                    )
                    futures.append(future)
                
                except queue.Empty:
                    break
            
            if futures and not stop_event.is_set():
                done, pending = wait(futures, return_when=FIRST_COMPLETED, timeout=1.0)
                
                for future in done:
                    try:
                        future.result()
                    except Exception as e:
                        if args.verbose:
                            print(f"[!] Task failed: {e}", flush=True)
                
                futures = list(pending)
                update_state()
            
            time.sleep(0.01)
        
        if futures and not stop_event.is_set():
            wait(futures, timeout=10.0)
            for future in futures:
                try:
                    future.result()
                except Exception:
                    pass
        
        update_state()
    
    state_to_save['to_visit'] = []
    if output_path_global:
        save_crawl_state(state_to_save, output_path_global, domain_global)
    
    return all_urls, get_params_data, post_params_data, api_urls, resource_data

def main():
    global args, output_path_global, domain_global
    
    ascii_logo = r"""
	 ▄▄· ▄▄▄   ▄▄▄· ▄▄▌ ▐ ▄▌▄▄▌  ▄▄▄ .▄▄▄  ▐▄• ▄ 
	▐█ ▌▪▀▄ █·▐█ ▀█ ██· █▌▐███•  ▀▄.▀·▀▄ █· █▌█▌▪	            ╦╔╦╗╔═╗┌─┐┬ ┬┬─┐┌┐ ┌─┐
	██ ▄▄▐▀▀▄ ▄█▀▀█ ██▪▐█▐▐▌██▪  ▐▀▀▪▄▐▀▀▄  ·██·     AUTHOR:    ║║║║╠═╣├─┘│ │├┬┘├┴┐│ │
	▐███▌▐█•█▌▐█ ▪▐▌▐█▌██▐█▌▐█▌▐▌▐█▄▄▌▐█•█▌▪▐█·█▌	            ╩╩ ╩╩ ╩┴  └─┘┴└─└─┘└─┘
	·▀▀▀ .▀  ▀ ▀  ▀  ▀▀▀▀ ▀▪.▀▀▀  ▀▀▀ .▀  ▀•▀▀ ▀▀
                                          
        CrawlerX - The Ultimate Web Crawler
    """
    print(ascii_logo)
    
    parser = argparse.ArgumentParser(description="CrawlerX - GET/POST Parameter Discovery")
    parser.add_argument('-u', '--url', required=True, help="Target URL")
    parser.add_argument('-o', '--output', default=None, help="Output directory")
    parser.add_argument('--structure', action='store_true', help="Generate site structure")
    parser.add_argument('-H', '--headers', default=None, help="Custom headers (Key1: Value1; Key2: Value2)")
    parser.add_argument('--threads', type=int, default=5, help="Threads (1-20, default: 5)")
    parser.add_argument('--depth', type=int, default=2, help="Max depth (default: 2)")
    parser.add_argument('--ua', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', help="User-Agent")
    parser.add_argument('--exclude', default='', help="Exclude extensions (pdf,zip)")
    parser.add_argument('--sub', action='store_true', help="Include subdomains")
    parser.add_argument('--proxy', default=None, help="Proxy (http://proxy:port)")
    parser.add_argument('--timeout', type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument('--delay', type=float, default=0.1, help="Delay (default: 0.1)")
    parser.add_argument('--cont', default=None, help="Resume from state file")
    parser.add_argument('--verbose', action='store_true', help="Verbose output")
    parser.add_argument('--respect-robots', action='store_true', help="Respect robots.txt (default: False)")
    parser.add_argument('--fuzz-params', action='store_true', help="Fuzz parameter values")
    parser.add_argument('--common-paths', action='store_true', help="Probe common paths")
    
    args = parser.parse_args()
    args.threads = max(1, min(args.threads, 20))
    
    print(f"[*] Threads: {args.threads}", flush=True)
    print(f"[*] Depth: {args.depth}", flush=True)
    if args.fuzz_params:
        print(f"[*] Parameter fuzzing: ENABLED", flush=True)
    if args.common_paths:
        print(f"[*] Common path probing: ENABLED", flush=True)
    
    if not args.url.startswith(('http://', 'https://')):
        args.url = f"https://{args.url}"
        print(f"[*] URL: {args.url}", flush=True)
    
    if args.proxy:
        args.proxy = {'http': args.proxy, 'https': args.proxy}
    
    session = requests.Session()
    headers = parse_headers(args.headers) if args.headers else {}
    
    if not is_valid_url(args.url, headers, session):
        print(f"[!] URL unreachable: {args.url}", flush=True)
        return
    
    if args.output:
        output_path, domain, folder_name = create_output_directory(args.url, args.output)
        output_path_global = output_path
        domain_global = domain
        print(f"[*] Output: {output_path}", flush=True)
    else:
        output_path, domain = None, get_domain(args.url)
        output_path_global = None
    
    print(f"[*] Starting crawl: {args.url}", flush=True)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        all_urls, get_params_data, post_params_data, api_urls, resource_data = crawl(args.url)
    except Exception as e:
        print(f"[!] Crawl failed: {e}", flush=True)
        all_urls, get_params_data, post_params_data, api_urls, resource_data = set(), [], [], set(), set()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"[*] CRAWL COMPLETE")
    print(f"{'='*60}")
    print(f"[+] URLs discovered: {len(all_urls)}")
    print(f"[+] GET requests: {len(get_params_data)}")
    print(f"[+] POST requests: {len(post_params_data)}")
    print(f"[+] API endpoints: {len(api_urls)}")
    print(f"[+] Resources: {len(resource_data)}")
    
    categorized_count = {}
    for url, category in resource_data:
        categorized_count[category] = categorized_count.get(category, 0) + 1
    
    for category, count in sorted(categorized_count.items()):
        print(f"    - {category}: {count}")
    
    if output_path:
        print(f"\n[*] Results saved to: {output_path}")
        print(f"    - endpoints/    : All discovered URLs")
        print(f"    - get/          : GET requests (params in URL)")
        print(f"    - post/         : POST requests (params in body)")
        print(f"    - api/          : API endpoints")
        print(f"    - resources/    : Categorized resources")
        
        if args.structure and all_urls:
            ascii_tree = write_structure_tree(all_urls, output_path)
            print(f"    - structure/    : Site structure")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
