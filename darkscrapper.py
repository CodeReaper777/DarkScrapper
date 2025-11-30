import argparse
from rich import print
import sys
from code.checker import run_checker, get_proxy, load_proxies, check_instance
from code.crawler import extract_urls
from code.checker import DEFAULT_THREAD, DEFAULT_TIMEOUT, DEFAULT_RETIRES

def main():
    parser = argparse.ArgumentParser(
        description="Onion URL Crawler and Parser"
    )
    sub = parser.add_subparsers(dest="command")

    crawl_cmd = sub.add_parser("crawl", help="Crawl for .onion links from ahmia")
    crawl_cmd.add_argument("--output",default="./data",help="Directory to save URLs and blacklist files")
    
    check =sub.add_parser("check", help="Checks for availability of the .onion urls")
    check.add_argument("-u","--urls",required=True,help="Onion URL list to check")
    check.add_argument("-b","--blacklist",required=True,help="Blacklisted MD5 Onion list")
    check.add_argument("-t","--threads",type=int,default=DEFAULT_THREAD,help="Number of threads (default=50)")
    check.add_argument("--timeout",type=int,default=DEFAULT_TIMEOUT,help="Maximum wait time to load (default: 10)")
    check.add_argument("--retires",type=int,default=DEFAULT_RETIRES,help="Retries for transient errors (default: 2)")

    arg = parser.parse_args()

    if arg.command == "crawl":
        print("[bold green][+] Starting the crawler [/bold green]")
        extract_urls(arg.output)
        print("[bold green][+] URL & Blacklisted extracted successfully [/bold green]")
    elif arg.command == "check":
        load_proxies()
        if not get_proxy() and check_instance:
            print("[red][!] First start the Tor instance.")
            print("[yellow][*] Run: sudo python multi-tor.py")
            sys.exit(1)
        print("[bold green][+] Starting the onion URL check [/bold green]")
        # print(PROXIES)
        run_checker(arg.urls, arg.blacklist, arg.threads, arg.retires, arg.timeout)
        # print("[bold green][+] Starting the onion URL check [/bold green]")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
