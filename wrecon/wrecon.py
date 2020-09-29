import requests,  urllib3, argparse, sys, re,os,colorama
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# coloring the prompt letters
colorama.init()

urllib3.disable_warnings()

GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED

scan_robots_and_sitemap = True
verbose = False
output = None
cookie = None

# Url tree class
class Tree (object):
    def __init__(self, data):
        self.children = []
        self.data = data

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.data)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<tree node representation>'

class Url (object):
    def __init__(self,adress, status_code,headers,text,content):
        self.adress = adress
        self.status_code = status_code
        self.headers = headers
        self.text = text
        self.content = content

class Wrecon:

    def parse_args():
        parser = argparse.ArgumentParser(description="WRecon")
        parser.add_argument("-u", "--url", help="Url link", required=True)
        parser.add_argument("-r", "--max-urls", help="Maximum number of recursive calls, default is one.", default=1, type=int)
        parser.add_argument('--disable-robots', help="Disable search for files robots.txt and sitemap.xml", action='store_false', default=True )
        parser.add_argument('--cookie', help="HTTP Cookie header value (e.g. \"PHPSESSID=a8d127e..\")", default=None)
        parser.add_argument("-v", "--verbose", help="Be a little more verbose and show urls before coming to a conclusion", action='store_true', default=False )
        parser.add_argument("-o", "--output", help="Directs the output to a name of your choice", default=None)
        return parser

    def is_fragment_identifier(self,url):
        if url is None:
            return False
        if '#' in url:
            return True
        return False

    def is_valid_cookie(self,input):
        if input is None:
            return False
        if '=' not in input:
            return False
        if len(input) < 3:
            return False
        return True

    def is_valid_url(self,url):
        if url is None:
            return False
        
        if url.count('://') > 1:
            return False

        regex = re.compile(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

        return re.match(regex, url) is not None

    def request_get(self,url):

        data = Url(url,400,'','','')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        headers = {'User-Agent': user_agent}

        if(not self.is_valid_url(url)):
            return data
        try:
            global cookie
            if cookie:
                my_cookies = {cookie.split('=')[0]: cookie.split('=')[1]}
                call = requests.get(url,verify=False, timeout=3, headers=headers,cookies= my_cookies)    
            else:    
                call = requests.get(url,verify=False, timeout=3, headers=headers)        
            call.raise_for_status()
            if call.status_code == 200:
                return call
        except requests.exceptions.Timeout:
            print(f"{RED} Timeout: {RESET}"+url)
            return data
        except requests.exceptions.TooManyRedirects:
            print(f"{RED} TooManyRedirects: {RESET}"+url)
            return data
        except urllib3.exceptions.InsecureRequestWarning:
            print(f"{RED} InsecureRequestWarning: {RESET}"+url)
            return data
        except requests.exceptions.HTTPError:
            print(f"{RED} HTTPError: {RESET}"+url)
            return data
        except requests.exceptions.ConnectionError:
            return data
        except urllib3.exceptions.NewConnectionError:
            return data


    def remove_outliers_from_recursive(self,url):
        invalid_tags = ['#','googleapis','styleshout','javascript://','use.fontawesome']

        #if url is null
        if url is  None:
            return False
            
        ## if the url contais outliers case
        if any(tag in url for tag in invalid_tags):
            return False

                # if the request is not a web page      
        data = self.request_get(url)
        if data.status_code == 200:
            if  'image' not in data.headers['Content-Type']:
                return True
    
    def start(self, root,indice):
        global verbose
        url = root.data
        if indice == 1:
            root = self.crawl(root.data)
            return root
        else:
            root = self.crawl(root.data)
            for kids in root:
                if(verbose):
                    print(f"{YELLOW} [Recusive]: {RESET}"+kids.data)
                ## avoid loopings
                if not(str(kids.data) ==  str(url) or str(kids.data) ==  str(url+'/') ):
                    kids.children =  self.start(kids,indice-1)     
            return root

    def capture(self,url,href): 
        ## check if it is a link inside the tags   
        if self.is_fragment_identifier(href):
            href = url+ '/'+href
        elif href is not None:
            if href[0:2] == '//':
                href = 'https:' + href
            else:
                if 'http' not in href:
                    href = urljoin(url, href)
                    href_analize = urlparse(href)
                    href = href_analize.scheme + "://" + href_analize.netloc + href_analize.path

        return href


    def robots(self,url):
        empty = ''
        urls_scanned = []
        list_sitemap = []
        ## root of website to get the robots.txt and sitemap.xml
        parsed_uri = urlparse(url)
        url_root = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        
        link_robots=url_root+'robots.txt'
        data = self.request_get(link_robots)
        if data.status_code == 200:
            urls_scanned.append(Tree(link_robots))
            text = data.text.splitlines()
            for line in text:
                if ' /' in line:
                    link = line.split(' /')[1]
                    if link is not empty:
                            urls_scanned.append(Tree(url_root+link))
            for line in text:
                if 'sitemap' in line:
                    link = line.split(' ')[1]
                    if link is not empty:
                            list_sitemap.append(link)

        list_sitemap.append(url_root+'sitemap.xml')
        
        for link_sitemap in list_sitemap:
            data = self.request_get(link_sitemap)
            if data.status_code == 200:
                urls_scanned.append(Tree(link_sitemap))
                text = data.text.splitlines()
                for line in text:
                    if '<loc>' in line:
                        start = line.find("<loc>") + len("<loc>")
                        end = line.find("</loc>")
                        link = line[start:end]
                        if link is not empty:
                            insercao = Tree(link)
                            if insercao not in urls_scanned:
                                urls_scanned.append(Tree(link))
        return urls_scanned


    def crawl(self,url):
        global verbose
        ##Returns all URLs found between tags
        children =[]
        global scan_robots_and_sitemap
        if scan_robots_and_sitemap: 
            children =self.robots(url)
        scan_robots_and_sitemap = False

        if self.remove_outliers_from_recursive(url) :
            tags = [["a","href"],["link","href"],["script","src"],["img","src"],["source","src"]]
            request = self.request_get(url)
            if request.status_code == 200: 
                soup = BeautifulSoup(request.content, "html.parser")	
                for tag in tags:
                    for a_tag in (soup.findAll(tag[0])):
                        href = a_tag.attrs.get(tag[1])
                        url_candidate = self.capture(url,href)
                        if self.is_valid_url(url_candidate):
                            candidate = Tree(url_candidate)
                            is_already_in_the_tree = False
                            for kids in children:
                                if candidate.data in kids.data:
                                    is_already_in_the_tree = True
                            if(not is_already_in_the_tree):
                                if(verbose):
                                    print(f"{GREEN} [url]: {RESET}"+candidate.data) 
                                children.append( candidate)
        return children

def main():
   
    print(" __        ______                      ")
    print(" \ \      / /  _ \ ___  ___ ___  _ __  ")
    print("  \ \ /\ / /| |_) / _ \/ __/ _ \| '_ \ ")
    print("   \ V  V / |  _ <  __/ (_| (_) | | | |")
    print("    \_/\_/  |_| \_\___|\___\___/|_| |_|")
    
    url =''
    max_urls = ''
    w=Wrecon()
    ## receive parameters
    try:
        args = Wrecon.parse_args().parse_args(sys.argv[1:])
        
        if(not w.is_valid_url(args.url.rstrip('//'))):
            print('The parameter URL are badly formed or contains invalid characters. Follow the example: http://localhost:800/')
            raise TypeError("not a valid URL")

        ##Remove last character if it's a backslash
        url = args.url.rstrip('//')
        max_urls = args.max_urls

        if w.is_valid_cookie(args.cookie):
            global cookie
            cookie = args.cookie

        global scan_robots_and_sitemap
        scan_robots_and_sitemap = args.disable_robots
        
        global verbose
        verbose = args.verbose
        
        global output
        output = args.output

    except:
        print('usage: wrecon.py [-h] [-u URL] [-r MAX_URLS]')
   
    ## create root e call start method
    root = Tree(url)
    root.children = w.start (root,max_urls)

    ## print results
    if output is not None:
        print(root,file=open(str(output)+".txt","w"))
    else:            
        print(root)

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)