import requests,  urllib3
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama

# para colorir as letras do prompt
colorama.init()

urllib3.disable_warnings()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED

boolean = False

# Clase de arvore de url
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

def crawl(url):
    ##Retorna todos os URLs encontradas entre as tags
    children =[]
    global boolean
    if not boolean: 
        children =robots(url)
    boolean = True

    tags = [["a","href"],["link","href"],["script","src"],["img","src"],["source","src"]]
    try: 
        soup = BeautifulSoup(requests.get(url,verify=False, timeout=3).content, "html.parser")	
        for tag in tags:
            for a_tag in (soup.findAll(tag[0])):
                href = a_tag.attrs.get(tag[1])
                if valida_call_back_url(url) :
                    valida = Tree(captura(url,href))
                    verifica_se_ja_esta_na_arvore = False
                    for kids in children:
                        if valida.data in kids.data:
                            verifica_se_ja_esta_na_arvore = True
                    if(not verifica_se_ja_esta_na_arvore):
                       ## print(valida.data)   
                        children.append( valida)
    except requests.exceptions.Timeout:
        print(f"{RED} Timeout: :{RESET}"+url)
    except:
        print(f"{RED} erro: :{RESET}"+url)
    return children 

def captura(url,href): 
    ## verifica se é um link dentro das tags    
    if complementarLinks(href):
        href = url+'/'+ href
    else:
        href = urljoin(url, href)
        href_analisada = urlparse(href)
        href = href_analisada.scheme + "://" + href_analisada.netloc + href_analisada.path
    ## definie se eh url interna ou externa
    nome_dominio = urlparse(url).netloc
    if nome_dominio not in href:
        return href  
    else:
        return href

def valida_call_back_url(url):
    validar = ['#','googleapis','styleshout','javascript://','use.fontawesome']

    if url is not None:
        for palavra in validar:
            if palavra in url:
                    return False
        try:           
            data = requests.get(url,verify=False, timeout=3)
            if data.status_code == 200:
                if  'image' not in data.headers['Content-Type']:
                    return True
        except requests.exceptions.Timeout:
            return False
        except urllib3.exceptions.InsecureRequestWarning:
            return False


def robots(url):
    urls_internas = []
    link_robots=url+'/robots.txt'
    try:
        data = requests.get(link_robots,verify=False, timeout=3)
        if data.status_code == 200:
            urls_internas.append(Tree(link_robots))
            texto = data.text.splitlines()
            for linha in texto:
                if ' /' in linha:
                    link = linha.split(' /')[1]
                    if link is not "":
                            urls_internas.append(Tree(url+'/'+link))
    except requests.exceptions.Timeout:
                    print('Timeout')

    link_sitemap=url+'/sitemap.xml'
    try:
        data = requests.get(link_sitemap,verify=False, timeout=3)
        if data.status_code == 200:
            urls_internas.append(Tree(link_sitemap))
            texto = data.text.splitlines()
            for linha in texto:
                if '<loc>' in linha:
                    start = linha.find("<loc>") + len("<loc>")
                    end = linha.find("</loc>")
                    link = linha[start:end]
                    if link is not "":
                        insercao = Tree(link)
                        if insercao not in urls_internas:
                            urls_internas.append(Tree(link))
    except requests.exceptions.Timeout:
                    print('Timeout')
    except :
                    print('Timeout')
    return urls_internas

def complementarLinks(url):
    if url is None:
        return False
    if '#' in url:
        return True
    return False

def url_eh_valida(url):
    urlAnalisada = urlparse(url)
    return bool(urlAnalisada.netloc) and bool(urlAnalisada.scheme)

def inicializa( root,indice):
    if indice == 1:
        root = crawl(root.data)
        return root
    else:
        root = crawl(root.data)
        for kids in root:
           ## print("kid: "+ kids.data)
            kids.children =  inicializa(kids,indice-1)     
        return root


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WRecon")
    parser.add_argument("url", help="Extrator de urls")
    parser.add_argument("-r", "--max-urls", help="Número máximo de chamadas recursivas, default é zero.", default=0, type=int)


    print(" __        ______                      ")
    print(" \ \      / /  _ \ ___  ___ ___  _ __  ")
    print("  \ \ /\ / /| |_) / _ \/ __/ _ \| '_ \ ")
    print("   \ V  V / |  _ <  __/ (_| (_) | | | |")
    print("    \_/\_/  |_| \_\___|\___\___/|_| |_|")
    
    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls

    parsed_uri = urlparse(url)
    url_raiz = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    indice=0
    
    root = Tree(url)
    
    root.children = inicializa (root,max_urls)

    print(root)