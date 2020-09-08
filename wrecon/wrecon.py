import requests,  urllib3, argparse, sys, re,os,colorama
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# coloring the prompt letters
colorama.init()

urllib3.disable_warnings()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED

scan_robots_and_sitemap = True

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
        
        return parser

    def is_fragment_identifier(self,url):
        if url is None:
            return False
        if '#' in url:
            return True
        return False

    def is_valid_url(self,url):
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url) is not None

    def request_get(self,url):

        data = Url(url,400,'','','')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        headers = {'User-Agent': user_agent}

        if(not self.is_valid_url(url)):
            return data
        try:
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
        except:
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
        url = root.data
        if indice == 1:
            root = self.crawl(root.data)
            return root
        else:
            root = self.crawl(root.data)
            for kids in root:
            ## print("kid: "+ kids.data)
                ## avoid loopings
                if not(str(kids.data) ==  str(url) or str(kids.data) ==  str(url+'/') ):
                    kids.children =  self.start(kids,indice-1)     
            return root

    def capture(self,url,href): 
        ## check if it is a link inside the tags   
        if self.is_fragment_identifier(href):
            href = url+'/'+ href
        else:
            href = urljoin(url, href)
            href_analize = urlparse(href)
            href = href_analize.scheme + "://" + href_analize.netloc + href_analize.path
        return href

    def robots(self,url):
        empty = ''
        urls_scanned = []
        ## root of website to get the robots.txt and sitemap.xml
        parsed_uri = urlparse(url)
        url_root = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        
        link_robots=url_root+'robots.txt'
        data = self.request_get(link_robots)
        if data.status_code == 200:
            urls_scanned.append(Tree(link_robots))
            texto = data.text.splitlines()
            for linha in texto:
                if ' /' in linha:
                    link = linha.split(' /')[1]
                    if link is not empty:
                            urls_scanned.append(Tree(url+'/'+link))

        link_sitemap=url_root+'sitemap.xml'
        data = self.request_get(link_sitemap)
        if data.status_code == 200:
            urls_scanned.append(Tree(link_sitemap))
            texto = data.text.splitlines()
            for linha in texto:
                if '<loc>' in linha:
                    start = linha.find("<loc>") + len("<loc>")
                    end = linha.find("</loc>")
                    link = linha[start:end]
                    if link is not empty:
                        insercao = Tree(link)
                        if insercao not in urls_scanned:
                            urls_scanned.append(Tree(link))
        return urls_scanned


    def crawl(self,url):
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
                        candidate = Tree(self.capture(url,href))
                        is_already_in_the_tree = False
                        for kids in children:
                            if candidate.data in kids.data:
                                is_already_in_the_tree = True
                        if(not is_already_in_the_tree):
                            ##print(candidate.data)   
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
    ## receive parameters
    try:
        args = Wrecon.parse_args().parse_args(sys.argv[1:])
        url = args.url
        max_urls = args.max_urls
    except:
        print('usage: wrecon.py [-h] [-u URL] [-r MAX_URLS]')

    w=Wrecon()
    ## validate URL
    if not w.is_valid_url(url):
        ## invalid url
        print('The parameter URL are badly formed or contains invalid characters. Follow the example: http://localhost:800/')
    else:
        try:
            ## create root e call start method
            root = Tree(url)
            root.children = w.start (root,max_urls)

            ## print results
            print(root)
        except:
            print('Sorry, an error occurred while processing your request')
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)