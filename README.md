# DarkScrapper

A fast multi-threaded `.onion` URL checker powered by **Python + Tor multiple instances**.

This tool helps you:

* Check thousands of `.onion` URLs quickly
* Use separate Tor instances for better speed + stability
* Detect reachable, unreachable, and error URLs
* Avoid Tor rate limits by auto‑routing requests through different SOCKS ports

---

## Features (Minimal)

* Multi-threaded URL checking
* Multiple Tor instance support
* Automatic torrc generation
* Auto-stop all running instances
* Clean JSON + TXT output

---

## Requirements

* Python 3.8+
* Tor installed (`sudo apt install tor`)
* `requests`, `stem`, `tqdm`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Installation

Clone the repo:

```bash
git clone https://github.com/CodeReaper777/DarkScrapper.git
cd DarkScrapper
```

---

## Usage (Minimum)


Create/Start/Stop Tor Instances

```bash
sudo python3 multi-tor.py
```

For Crawling .onion sites:

```bash
python3 darkscrapper.py crawl 
```
For Checking .onion sites availability (alive/dead):

```bash
python3 darkscrapper.py check -u ./data/onion_urls.txt -b ./data/onion_blacklist_urls.txt -t 20 
```
Enter:

* -u: Input file path of .onion sites
* -b: blacklisted md5 hash of the .onion sites.
* -t: threads (keep upto 30 for 5 instance of tor for better accuracy)

Outputs saved under:

```
output/results.json
output/alive.txt
output/dead.txt
```
