import requests,re
from bs4 import BeautifulSoup
import os
from rich import print

def extract_urls(output="./data"):  
    url = 'https://ahmia.fi/onions/'
    blacklist_url = 'https://ahmia.fi/blacklist/banned/'
    timeout=60
    user_agent={"User-Agent":"...."}
    session = requests.Session()

    try:
        print("[blue][+] Crawling for .onion urls....[/blue]")
        res = session.get(url,timeout=timeout,headers=user_agent)
        print(f'[bold green][*] Done![/bold green]')
        print(f'[blue][+] Getting Banned url list....[/blue]')
    
        bres = session.get(blacklist_url,timeout=timeout,headers=user_agent)
        print(f'[bold green][*] Done![/bold green]')
        
        soap = BeautifulSoup(res.text,'html.parser')
        for br_tag in soap.find_all('br'):
            br_tag.decompose()
        # print(soap.prettify())

        if not os.path.exists(output):
            os.makedirs(output)

        saveurl = os.path.join(output, 'onion_urls.txt')
        saveb = os.path.join(output, 'onion_blacklist_urls.txt')

        fetched_urls = soap.get_text()
        pattern = r"https?://[a-z2-7]{56}\.onion/?"
        onion_urls = re.findall(pattern,fetched_urls)
    
        unique_urls = set(onion_urls)
        b_set = []
        with open(saveurl,"w+")as f:
            for url in unique_urls:
                f.write(url+'\n')
            print(f'[bold green][*] Successfully extracted urls and saved in {saveurl} with {len(unique_urls)} urls[/bold green]')
        with open(saveb,"w+")as f:
            f.write(bres.text)
            with open(saveb,'r')as j:
                for line in j:
                    b_set.append(line)
            print(f'[bold green][*] Successfully extracted blacklisted hashes and saved in {saveb} with {len(b_set)} urls[/bold green]')
        
        # print(unique_urls)
    except requests.exceptions.RequestException as e:
        print(f'[bold red]Request Execption: {e} [/bold red]')
    except Exception as e:
        print(f'[bold red]Error: {e}[/bold red]')
