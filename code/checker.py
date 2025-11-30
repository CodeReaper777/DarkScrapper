import requests
import argparse
import random
import threading
from rich import print
from rich.console import Console
from rich.panel import Panel
import subprocess
import csv
import time
import itertools
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import load_urls, load_hashes, url_to_md5
# from utils import load_urls, load_hashes, url_to_md5

PROXIES = []
console = Console()
def get_proxy():
    return len(PROXIES) >0

def check_instance():
    process = subprocess.run(["ss", "-tulnp", "|", "grep", "905"],check=True,capture_output=True,text=True)
    out = process.stdout
    if out:
        print(process.stdout)
        return True
    else:
        return False

def load_proxies():
    PROXIES.clear()
    file = "./proxy.txt"
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file,'r') as f:
            for port in f:
                port = port.strip()
                if port:
                    PROXIES.append({
                        "http": f"socks5h://127.0.0.1:{port}",
                        "https": f"socks5h://127.0.0.1:{port}"
                    })
    return PROXIES
DEFAULT_TIMEOUT=5
DEFAULT_RETIRES=2
DEFAULT_THREAD=30

proxies = itertools.cycle(PROXIES)
user_agent={"User-Agent":"Mozilla/5.0 (compatible; OnionChecker/1.0)"}
_thread_local = threading.local()

def get_session():
    sess = getattr(_thread_local,"session",None)
    if sess is None:
        sess = requests.Session()
        sess.proxies = next(proxies)
        sess.headers.update(user_agent)
        sess.headers["Connection"] = "close"
        _thread_local.session  = sess
    return sess

def check_url(url:str, blacklist:set, timeout:int, retries:int):

    results = {"url": url, "md5": url_to_md5(url), "code": None, "status":None, "response_time":None}

    if results["md5"] in blacklist:
        results["status"] = "BLACKLIST"
        return results
    
    attempts = 0
    while attempts < retries:
        attempts += 1
        try: 
            sess = get_session()
            start = time.time()
            resp = sess.get(url,timeout=timeout,stream=True)
            elapsed = time.time() - start
            results["code"] = resp.status_code
            results["response_time"] = round(elapsed,3)
            code = results["code"]

            if 200 <= code <= 399:
                results["status"] = "ALIVE"
            elif 400 <= code <= 599:
                results["status"] = "DEAD"
            else: 
                results["status"] = "UNKNOWN"
            return results
            
        except requests.exceptions.Timeout:
            results["status"] = "TIMEOUT"
            if attempts < retries:
                time.sleep(random.uniform(0.5,1.5))
                continue
            return results
        except requests.exceptions.RequestException:
            results["status"] =  "UNREACHABLE"
            if attempts < retries:
                time.sleep(random.uniform(0.5,1.5))
                continue
            return results
        
    results["status"] = results["status"] or "UNKNOWN"
    return results


def run_checker(url: str, blacklist: str, threads:int, retries:int, timeout:int):
    urls = load_urls(url)
    hashes = load_hashes(blacklist)
    # print(PROXIES)
    print(f"[+] Loaded {len(urls)} unique normalized onion URLs")
    print(f"[+] Loaded {len(hashes)} blacklist MD5 hashes")

    results = []
    with ThreadPoolExecutor(max_workers=threads)as ex:
        futures = {ex.submit(check_url,u,hashes,timeout,retries): u for u in urls}
        for fut in tqdm(as_completed(futures), total=len(futures),desc="Checking",unit="url"):
            try:
                res = fut.result()
            except Exception as e:
                res = {"url": futures[fut], "md5": url_to_md5(futures[fut]), "status": "UNREACHABLE", "code": None, "response_time": None}
            results.append(res)

    category = {"ALIVE": [],"DEAD": [],"TIMEOUT": [],"UNREACHABLE": [],"BLACKLIST":[],"UNKNOWN":[]}

    for r in results:
        category.setdefault(r["status"], []).append(r)
    output = './output'
    if not os.path.exists(output):
        os.makedirs(output)

    for cat, items in category.items():
        f = f"{os.path.join(output,cat.lower())}.txt"
        with open(f,'w')as g:
            for i in items:
                g.write(i["url"]+'\n')
        print(f"[bold green][+] Wrote {len(items)} entries to {f} [/bold green]")

    csvfile = os.path.join(output,"result.csv")
    with open(csvfile, "w", newline="",encoding='utf-8') as cf:
        w = csv.writer(cf)
        w.writerow(["url","status","code","response_time","md5"])

        for r in results:
            w.writerow([r["url"],r["status"],r["code"],r["response_time"],r["md5"]])
    print(f"[bold green][+] Wrote details to {csvfile}[/bold green]")

    summary = {status: len(items) for status, items in category.items()}
    report_text = "\n".join([f"{k:<12}: {v}" for k, v in summary.items()])
    console.print(Panel(report_text, title="ONION CHECK REPORT", expand=False, style="bold cyan"))

def get_args():
    p = argparse.ArgumentParser(description="Tor Onion Alive Checker")
    p.add_argument("-u", "--urls", required=True, help="Path to onion URLs file (one per line)")
    p.add_argument("-b", "--blacklist", required=True, help="Path to blacklist MD5 file (one per line)")
    p.add_argument("-t", "--threads", type=int, default=DEFAULT_THREAD, help="Number of worker threads (default: 50)")
    p.add_argument("--retries", type=int, default=DEFAULT_RETIRES, help="Retries for transient errors (default: 2)")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-request timeout in seconds (default: 10)")
    return p.parse_args()

# if __name__ == "__main__":
#     arg = get_args()
#     if not get_proxy():
#         print("[red][!] First start the Tor instance.")
#         print("[yellow][*] Run: sudo python multi-tor.py")
#         sys.exit(1)
#     print('[+] Starting TOR checker (make sure TOR is running.')
#     run_checker(arg.urls, arg.blacklist, arg.threads, arg.retries, arg.timeout)