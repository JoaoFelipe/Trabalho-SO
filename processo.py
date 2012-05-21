# -*- coding: utf-8 -*-
from collections import namedtuple
from utils import EqualByAttributes, divisao_inteira_superior


class Pagina(namedtuple('Pagina', ['processo', 'numero', 'tamanho'])):

    def __str__(self):
        return "P %i Pag %i" % (self.processo.identificador, self.numero)

    @property
    def entrada_tp(self):
        return self.processo.tabela_paginas[self.numero]


class EntradaTP(EqualByAttributes):

    def __init__(self, presente, modificado, quadro):
        self.presente = presente
        self.modificado = modificado
        self.quadro = quadro


class Processo(object):

    def __init__(self, identificador, tamanho, tamanho_pagina):
        self.identificador = identificador
        self.tamanho = tamanho
        numero_paginas = divisao_inteira_superior(tamanho, tamanho_pagina)

        # Instancia páginas do processo
        self.paginas = [Pagina(self, i, tamanho_pagina) for i in xrange(numero_paginas)]
        # Define tamanho ocupado dentro da última página
        if tamanho % tamanho_pagina != 0:
            self.paginas[-1] = Pagina(self, numero_paginas - 1, (tamanho % tamanho_pagina))
        # Monta uma EntradaTP para cada pagina
        self.tabela_paginas = [EntradaTP(0, 0, None) for _ in self.paginas]

    @property
    def quadros(self):
        try:
            return self.conjunto_residente
        except AttributeError:
            return [entrada_tp.quadro for entrada_tp in self.tabela_paginas if entrada_tp.presente]

    def estaSuspenso(self):
        return len(self.quadros) == 0
