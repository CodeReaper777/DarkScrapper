import hashlib

def normalize_urls(url):
    if url is None:
        return ""
    url = url.lower()
    if url.startswith('http://'):
        url = url[len('http://'):]
    elif url.startswith('https://'):
        url = url[len('https://'):]
    
    url = url.split('/',1)[0]
    if not url.endswith('.onion'):
        return ""
    return "http://"+ url

def load_urls(urls: str):
    s = set()
    with open(urls, 'r')as f:
        for line in f:
            url = normalize_urls(line)
            if url:
                s.add(url)
    return sorted(s)

def load_hashes(blacklist_path: str):
    s = set()
    with open(blacklist_path,'r')as b:
        for line in b:
            h = line.lower()
            if h:
                s.add(h)
    return sorted(s)

def url_to_md5(url:str) -> str:
    if url is None:
        return ""
    
    if url.startswith('http://'):
        domain = url[len('http://'):]
    elif url.startswith('https://'):
        domain = url[len('https://'):]
    else:
        domain = url
    
    if domain.endswith('/'):
        domain = domain[:-1]
    
    return hashlib.md5(domain.encode('utf-8')).hexdigest()