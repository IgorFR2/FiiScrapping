from bs4 import BeautifulSoup
import requests
import time

class Fii:
    def __init__(self, ticket, tipo, subtipo, patrimonio, rendimentoMedio, cotas, yeldMedio, pagamentoMedio):
        self.ticket = ticket
        self.tipo = tipo
        self.subtipo = subtipo
        self.patrimonio = patrimonio
        self.rendimentoMedio = rendimentoMedio
        self.cotas = cotas
        self.yeldMedio = yeldMedio
        self.pagamentoMedio = pagamentoMedio
        self.valorReal = round(patrimonio/cotas,2)
# OK
def CarregarPagina(url):
    if(url[-5:] == ".html"):
        with open(url, 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')
    else:
        return BeautifulSoup(requests.get(url.replace(' ','+')).text, 'html.parser')
# OK
def BuscarRotulos(url):
    soup = CarregarPagina(url)
    rotulos = []
    for span in soup.find_all('span', {'class':'ticker'}):
        rotulos.append(span.get_text())
    return rotulos
# OK
def SalvarRotulos(rotulos):
    with open("rotulos.txt",'w') as f:
        for rotulo in rotulos:
            f.write(rotulo+"\n")
# OK
def CarregarRotulos():
    with open("rotulos.txt",'r') as f:
        rotulos = f.read()
    return rotulos.split('\n')

# Construindo
def BuscarDadosFII(url,rotulos):
    colecao = []
    for rotulo in rotulos:
        print("Iniciando busca de ",rotulo,"...")
        # Buscar página
        pagina = CarregarPagina(url+rotulo)
        #pagina = CarregarPagina("FOFT11.html") # MOCK

        # Separar divs importantes
        #1) Índices:
        '''
         - 4 Divs com 2 spans (classes "value", "title"):
         -- 0: ultima % DY
         -- 1: ultimo rendimento (ha span R$)
         -- 2: patrimônio líquido (ha span R$)
         -- 3: VP por cota (ha span R$)
         '''
        indices = pagina.find('div', {'id':'informations--indexes'}).findAll('div')
        # Se não tiver índices válidos, ignore
        indices[1].find('span',{'class':'currency'}).decompose()
        if(float(indices[1].span.string.replace(',','.'))>0):
            # 2) Informações básicas
            '''
            - 2 Divs:
            -- 4 Divs com 2 span cada (classes "title", "value"):
            --- Nome no pregão
            --- Tipo
            --- Tipo ANBIMA
            --- Registro
            -- 3 Divs com 2 span cada ("title", "value")
            --- Cotas
            --- Cotistas
            --- CNPJ
            '''
            infoBasicas = pagina.find('div', {'id':'informations--basic'}).findAll('div',{'class':'row'})
            [tipo,subtipo] = infoBasicas[0].contents[3].find('span',{'class':'value'}).string.split(':')
            cotas = int(infoBasicas[1].contents[1].find('span',{'class':'value'}).string.replace('.',''))
            patrimonio = cotas * float(indices[3].contents[1].contents[1].string.replace(',',''))
            # 3) Tabela dos ultimos proventos
            '''
            - thead e tbody:
            -- tbody com N tr (0<=N<=12?)
            --- Data base (?)
            --- Data pgto
            --- Cotação
            --- DY
            --- Rendimento
            '''
            proventos = pagina.find('table', {'id': 'last-revenues--table'}).tbody.findAll('tr')
            rendimentoMedio = yeldMedio = pagamentoMedio = elementos = 0
            for child in proventos:
                pagamentoMedio += int(child.contents[3].string.split('/')[0])
                rendimentoMedio += float(child.contents[9].string.replace('R$','').replace(",","."))
                yeldMedio += float(child.contents[7].string.replace('%', '').replace(",", "."))
                elementos+=1
            colecao.append( Fii(rotulo.upper(),tipo,subtipo,patrimonio,rendimentoMedio,cotas,yeldMedio,pagamentoMedio) )
        else:
            print("Rotulo "+rotulo.upper()+" iniciando operações no mercado, pulando.")
    print("Processo de busca da lista concluída.")
    return colecao

url = "https://fiis.com.br/"
url_lista = url + "lista-de-fundos-imobiliarios/"
id_tabela = "items-wrapper"
#SalvarRotulos(BuscarRotulos(url_lista))
lista = BuscarDadosFII(url,CarregarRotulos())