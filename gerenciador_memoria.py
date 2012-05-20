# -*- coding: utf-8 -*-
class GerenciadorMemoria(object):
    
    def __init__(self, simulador):
        self.simulador = simulador

    def descobre_pagina(self, endereco):
        return int(endereco[:-self.simulador.numero_bits_pagina()],2)
    
    def alocacao_inicial(self): pass

    def continua_acesso(self, processo, entrada_pagina):pass

    def acessar(self, num_processo, tipo, endereco): 
        processo = self.simulador.processos[num_processo]
        num_pagina = self.descobre_pagina(endereco)
        pagina = processo.paginas[num_pagina]
        entrada_pagina = processo.tabela_paginas[num_pagina]
        if tipo == "W": 
            entrada_pagina.modificado = 1
        self.continua_acesso(processo, pagina, entrada_pagina)
