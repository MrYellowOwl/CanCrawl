import socket
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
import queue
import threading

YELLOW = "\033[38;2;255;241;0m"
GREEN = "\033[38;2;0;255;0m"
RED = "\033[38;2;255;0;0m"
RESET = "\033[0m"

NUM_THREADS = 100
TIMEOUT_SECONDS = 30

def print_banner():
    print(YELLOW)
    print("          (,#                                                       @ &         ")
    print("         ,&#,&*                                                   #& &&         ")
    print("         .(&@.#&%                                               &&**&&,*        ")
    print("         &&#*&&,*&&&                                        .&&&.(&& &&%        ")
    print("           %&&&&&&#/&&&         &               *        ,&&&,&&&&&&&#          ")
    print("         .@&&&%%&&&&&%(&(       .&&*         (&&        &&,&&&&&&%&&&&&         ")
    print("         (*,,*#&&&&&&&&/&.%.     /%,%&#&&#&&#,&.     ,((&%&&&&&&&&(,,,*/        ")
    print("            .   &&&&&&&&.&.(./#/.&%&   &&&  ,%&(,((*.//&#&&&%&&&#  .            ")
    print("           .%&&&( (&&&&%,*&#**..*..&&&(#(&#@&%*,,../.&(% &&&&&, %&&&%           ")
    print("               ,&&&/.&/#&& .%*#&#. %##&%#&&(%# ,%&*##,,&&*%& #&&&               ")
    print("                   &.&%,&&%.*&%  ,%&&% &&&.&&&#.  &&.,&&%*&%,&                  ")
    print("                           *%&&&&(.&&#,&&@,/@& %&&&@#.                          ")
    print("                                     &&&&&&#                                    ")
    print("                               /@.(    *@.   /,/&,                              ")
    print("                                #& %.*.&/&( (/,&,.                              ")
    print("                                  %%,&.&&&.& &(                                 ")
    print("                                     % &&& *                                    ")
    print(" ▄████▄   ▄▄▄       ███▄    █     ▄████▄   ██▀███   ▄▄▄       █     █░ ██▓      ")
    print("▒██▀ ▀█  ▒████▄     ██ ▀█   █    ▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▓█░ █ ░█░▓██▒      ")
    print("▒▓█    ▄ ▒██  ▀█▄  ▓██  ▀█ ██▒   ▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▒█░ █ ░█ ▒██░      ")
    print("▒▓▓▄ ▄██▒░██▄▄▄▄██ ▓██▒  ▐▌██▒   ▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ░█░ █ ░█ ▒██░      ")
    print("▒ ▓███▀ ░ ▓█   ▓██▒▒██░   ▓██░   ▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒░░██▒██▓ ░██████▒  ")
    print("░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒    ░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▓░▒ ▒  ░ ▒░▓  ░  ")
    print("  ░  ▒     ▒   ▒▒ ░░ ░░   ░ ▒░     ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░  ▒ ░ ░  ░ ░ ▒  ░  ")
    print("░          ░   ▒      ░   ░ ░    ░          ░░   ░   ░   ▒     ░   ░    ░ ░     ")
    print("░ ░            ░  ░         ░    ░ ░         ░           ░  ░    ░        ░  ░  ")
    print("░                                ░                                            ")
    print("-By Mr Yellow Owl")
    print(RESET)

class DiscoveryWebCrawler:

    def __init__(self, domain, levels):
        self.domain = domain
        self.q = queue.Queue()
        self.urls = []
        self.levels_to_crawl = levels

    def resolve_ip(self, domain):
        try:
            ip_address = socket.gethostbyname(domain)
            print(f"Resolved IP address for {domain}: {ip_address}")
            return ip_address
        except socket.gaierror:
            print(f"{RED}Error: Could not resolve IP address for {domain}{RESET}")
            return None

    def crawl_url(self, crawl_url, current_level):
        s = requests.Session()
        try:
            r = s.get(crawl_url, verify=True, timeout=TIMEOUT_SECONDS)
            r.raise_for_status()  
            soup = BeautifulSoup(r.content, 'html.parser') 
            links = soup.find_all('a')
            for url in links:
                try:
                    url = url.get('href')
                    if url and url[0] == '/':
                        url = self.domain + url
                    if url and url.split("/")[2] == self.domain.split('/')[2] and url not in [u['url'] for u in self.urls]:
                        self.urls.append({'url': url, 'level': current_level})
                        if current_level + 1 < self.levels_to_crawl:
                            self.q.put({'url': url, 'level': current_level + 1})
                except Exception as e:
                    pass
        except requests.RequestException as e:
            print(f"{RED}Error crawling {crawl_url}: {e}{RESET}")

    def worker(self):
        while 1:
            crawl_url_dict = self.q.get()
            self.crawl_url(crawl_url_dict['url'], crawl_url_dict['level'])
            self.q.task_done()

    def start(self):
        self.q.put({'url': self.domain, 'level': 0})
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
        self.q.join()

if __name__ == "__main__":
    print_banner()

    while True:
        input_domain = input("Enter a domain, URL, or IP to crawl: ")
        if input_domain.startswith("http://") or input_domain.startswith("https://"):
            domain = input_domain
            break
        else:
            try:
                socket.inet_pton(socket.AF_INET, input_domain)
                domain = f"http://{input_domain}"
                break
            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, input_domain)
                    domain = f"http://{input_domain}"
                    break
                except socket.error:
                    domain = f"http://{input_domain}"
                    break

    levels = int(input("Enter the number of levels to crawl: "))

    web_crawler = DiscoveryWebCrawler(domain, levels)

    print(f"{YELLOW}Crawling {domain}...{RESET}")
    web_crawler.start()
    print(f"{GREEN}Crawling completed!{RESET}")

    for i in range(levels):
        print(f"\n{GREEN}Level {i+1} URLs{RESET}")
        for url_info in web_crawler.urls:
            if url_info['level'] == i:
                print(url_info['url'])
