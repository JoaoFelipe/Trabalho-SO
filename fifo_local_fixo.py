# -*- coding: utf-8 -*-
from gerenciador_memoria import GerenciadorMemoria
from mensagem import ModificadaMensagem, CarregadaMensagem, PresenteMensagem
from utils import teto_inteiro

class FifoLocalFixo(GerenciadorMemoria):

    def __init__(self, simulador):
        super(FifoLocalFixo,self).__init__(simulador)
        self.processos_na_mp = []
        self.ponteiro = [-1]*len(self.simulador.processos)
        self.quadros_processo = self.quadros_por_processo()
        self.quadros_alocados_por_processo = []
        for i in xrange(len(self.simulador.processos)):
            self.quadros_alocados_por_processo.append([])


    def quadros_por_processo(self):
        # cálculo da quntidade de quadros por processo, tomando como base 
        # o espaço disponível em MP e numero de páginas dos processos a serem executados
        # razao = (numero de quadros da MP) / (total de paginas da MS)
        # numero de quadros Px = teto[razao * (numero de páginas de Px)] 
        paginas_de_cada_processo = [len(processo.paginas) for processo in self.simulador.processos]
        razao = len(self.simulador.quadros)/(sum(paginas_de_cada_processo)+.0)
        quadros_por_processo = [teto_inteiro(razao*numero_paginas) for numero_paginas in paginas_de_cada_processo]
        return quadros_por_processo

    def continua_acesso(self, processo, pagina, entrada_tp):
        ponteiro = self.ponteiro[processo.identificador]
        if entrada_tp.presente:
            # página já está na MP, apenas acessa
            self.simulador.mudancas.append(PresenteMensagem(pagina))
        elif ponteiro != -1:
            # se processo está na MP
            # seleciona quadro do ponteiro para esvaziar
            # avança ponteiro (e volta para 0 se passar do numero de quadros)
            esvaziar = self.quadros_alocados_por_processo[processo.identificador][ponteiro]

            self.ponteiro[processo.identificador] = (ponteiro + 1) % self.quadros_processo[processo.identificador]

            pagina_retirada = self.simulador.quadros[esvaziar]
            entrada_tp_retirada = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
            # se for modificada, salva na memória secundária
            if entrada_tp_retirada.modificado:
                self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
            # reseta informacoes da página retirada 
            entrada_tp_retirada.presente = 0
            entrada_tp_retirada.modificado = 0
            vazio = esvaziar
            # coloca página acessada na MP
            entrada_tp.quadro = vazio
            entrada_tp.presente = 1
            self.simulador.quadros[vazio] = pagina
            self.simulador.mudancas.append(CarregadaMensagem(pagina))
        else:
            # se processo não estiver na MP
            # enquanto quantidade de quadros disponíveis na MP não é compatível com
            # numero de quadros necessitados pelo processo
            while self.simulador.quadros.count(None) < self.quadros_processo[processo.identificador]:
                # seleciona processo para suspender
                esvaziar_processo = self.processos_na_mp.pop(0)
                # percorre quadros alocados para o processo
                # desaloca quadro da MP
                for esvaziar in self.quadros_alocados_por_processo[esvaziar_processo.identificador]:
                    pagina_retirada = self.simulador.quadros[esvaziar]
                    entrada_tp_retirada = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
                    # se for modificada, salva na memória secundária
                    if entrada_tp_retirada.modificado:
                        self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
                    # reseta informacoes da página retirada 
                    entrada_tp_retirada.presente = 0
                    entrada_tp_retirada.modificado = 0
                    self.simulador.quadros[esvaziar] = None
                self.quadros_alocados_por_processo[esvaziar_processo.identificador] = []
                self.ponteiro[esvaziar_processo.identificador] = -1
            # adiciona processo na fila de processos        
            self.processos_na_mp.append(processo)
            self.ponteiro[processo.identificador] = 0
            numero_base = pagina.numero
            numero_pagina_atual = pagina.numero
            # descobre numero de paginas a serem carregadas na MP
            carregar = self.quadros_processo[processo.identificador]
            incremento = 1
            while carregar > 0:
                carregar -= 1
                entrada_tp = processo.tabela_paginas[numero_pagina_atual]
                pagina = processo.paginas[numero_pagina_atual]
                # procura quadro vazio na MP e coloca pagina acessada na MP
                vazio = self.simulador.quadros.index(None) 
                entrada_tp.quadro = vazio
                entrada_tp.presente = 1
                self.simulador.mudancas.append(CarregadaMensagem(pagina))
                self.simulador.quadros[vazio] = pagina
                self.quadros_alocados_por_processo[processo.identificador].append(vazio)
                numero_pagina_atual += incremento
                # se chegar no limite do numero de paginas do processo
                # inverte o loop a partir da pagina acessada
                if numero_pagina_atual >= len(processo.paginas):
                    incremento = -1
                    numero_pagina_atual = numero_base - 1

            