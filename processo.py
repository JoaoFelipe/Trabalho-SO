from math import ceil
from collections import namedtuple
from utils import EqualByAttributes


divisao_inteira_superior = lambda x, y: int(ceil((1.0*x)/y))

class Pagina(namedtuple('Pagina', ['processo', 'numero', 'tamanho'])):
    def __str__(self):
        return "P"+str(self.processo.identificador)+" Pag "+str(self.numero) 

class EntradaTP(EqualByAttributes):

    def __init__(self, presente, modificado, quadro):
        self.presente = presente
        self.modificado = modificado
        self.quadro = quadro


class Processo(object):

    def __init__(self, identificador, tamanho, tamanho_pagina):
        self.identificador = identificador 
        self.tamanho = tamanho
        # Talvez nao seja necessario ter a divisao de paginas do processo, mas fiz a divisao:
        numero_paginas = divisao_inteira_superior(tamanho, tamanho_pagina)
        self.paginas = [Pagina(self, i, tamanho_pagina) for i in xrange(numero_paginas)]
        if tamanho % tamanho_pagina != 0:
            self.paginas[-1] = Pagina(self, numero_paginas-1, (tamanho % tamanho_pagina))
        # Monta uma EntradaTP para cada pagina
        self.tabela_paginas = [EntradaTP(0, 0, None) for _ in self.paginas]
            

