# -*- coding: utf-8 -*-
from gerenciador_memoria import GerenciadorMemoria
from mensagem import ModificadaMensagem, CarregadaMensagem, PresenteMensagem
from utils import teto_inteiro

VERIFICAO = 4
RATIO_MIN = 0.3
RATIO_MAX = 0.7

class FifoLocalVariavel(GerenciadorMemoria):

    def __init__(self, simulador):
        super(FifoLocalVariavel,self).__init__(simulador)
        self.processos_na_mp = []
        self.ponteiro = [-1]*len(self.simulador.processos)
        self.quadros_processo = self.quadros_por_processo()
        self.quadros_alocados_por_processo = []
        for i in xrange(len(self.simulador.processos)):
            self.quadros_alocados_por_processo.append([])
        self.falhas = [0]*len(self.simulador.processos)
        self.acessos = [0]*len(self.simulador.processos)


    def quadros_por_processo(self):
        # cálculo da quntidade de quadros por processo, tomando como base 
        # o espaço disponível em MP e numero de páginas dos processos a serem executados
        # razao = (numero de quadros da MP) / (total de paginas da MS)
        # numero de quadros Px = teto[razao * (numero de páginas de Px)] 
        paginas_de_cada_processo = [len(processo.paginas) for processo in self.simulador.processos]
        razao = len(self.simulador.quadros)/(sum(paginas_de_cada_processo)+.0)
        quadros_por_processo = [teto_inteiro(razao*numero_paginas) for numero_paginas in paginas_de_cada_processo]
        return quadros_por_processo

    def log(self):
        print self.processos_na_mp 
        print self.ponteiro
        print self.quadros_processo 
        print self.quadros_alocados_por_processo 
        print self.falhas
        print self.acessos 
        print [1.0*self.falhas[i]/self.acessos[i] if self.acessos[i] != 0 else float('inf') for i in range(len(self.acessos))]


    def continua_acesso(self, processo, pagina, entrada_tp):
        self.log()
        self.acessos[processo.identificador] += 1
        ponteiro = self.ponteiro[processo.identificador]
        if entrada_tp.presente:
            # página já está na MP, apenas acessa
            self.simulador.mudancas.append(PresenteMensagem(pagina))
            if self.acessos[processo.identificador] % VERIFICAO == 1:
                ratio = 1.0*self.falhas[processo.identificador]/self.acessos[processo.identificador]
                if ratio < RATIO_MIN and self.quadros_processo[processo.identificador] > 1:
                    self.quadros_processo[processo.identificador] -= 1
                    # seleciona quadro do ponteiro para esvaziar
                    # avança ponteiro (e volta para 0 se passar do numero de quadros)
                    esvaziar = self.quadros_alocados_por_processo[processo.identificador].pop(ponteiro)
                    self.ponteiro[processo.identificador] = (ponteiro + 1) % self.quadros_processo[processo.identificador]
                    pagina_retirada = self.simulador.quadros[esvaziar]
                    entrada_tp_retirada = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
                    # se for modificada, salva na memória secundária
                    if entrada_tp_retirada.modificado:
                        self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
                    # reseta informacoes da página retirada 
                    entrada_tp_retirada.presente = 0
                    entrada_tp_retirada.modificado = 0
                    self.simulador.quadros[esvaziar] = None
                elif ratio > RATIO_MAX and self.quadros_processo[processo.identificador] < len(self.simulador.quadros):
                    self.quadros_processo[processo.identificador] += 1
                    # enquanto quantidade de quadros disponíveis na MP não é compatível com
                    # numero de quadros necessitados pelo processo
                    if not self.simulador.quadros.count(None):
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
                    vazio = self.simulador.quadros.index(None) 
                    numero_base = pagina.numero
                    numero_pagina_atual = pagina.numero
                    # descobre numero de paginas a serem carregadas na MP
                    achou = False
                    incremento = 1
                    while not achou:
                        entrada_tp = processo.tabela_paginas[numero_pagina_atual]
                        pagina = processo.paginas[numero_pagina_atual]
                        if pagina in self.simulador.quadros:
                            numero_pagina_atual += incremento
                            # se chegar no limite do numero de paginas do processo
                            # inverte o loop a partir da pagina acessada
                            if numero_pagina_atual >= len(processo.paginas):
                                incremento = -1
                                numero_pagina_atual = numero_base - 1
                        else:
                            achou = True

                    entrada_tp.quadro = vazio
                    entrada_tp.presente = 1
                    self.simulador.mudancas.append(CarregadaMensagem(pagina))
                    self.simulador.quadros[vazio] = pagina
                    self.quadros_alocados_por_processo[processo.identificador].append(vazio)
                    numero_pagina_atual += incremento
                        
                  
        elif ponteiro != -1:
            # se processo está na MP
            vazio = None
            self.falhas[processo.identificador] += 1
            if self.acessos[processo.identificador] % VERIFICAO == 1:
                ratio = 1.0*self.falhas[processo.identificador]/self.acessos[processo.identificador]
                if ratio < RATIO_MIN and self.quadros_processo[processo.identificador] > 1:
                    self.quadros_processo[processo.identificador] -= 1
                    # seleciona quadro do ponteiro para esvaziar
                    # avança ponteiro (e volta para 0 se passar do numero de quadros)
                    esvaziar = self.quadros_alocados_por_processo[processo.identificador].pop(ponteiro)
                    self.ponteiro[processo.identificador] = (ponteiro + 1) % self.quadros_processo[processo.identificador]
                    pagina_retirada = self.simulador.quadros[esvaziar]
                    entrada_tp_retirada = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
                    # se for modificada, salva na memória secundária
                    if entrada_tp_retirada.modificado:
                        self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
                    # reseta informacoes da página retirada 
                    entrada_tp_retirada.presente = 0
                    entrada_tp_retirada.modificado = 0
                    self.simulador.quadros[esvaziar] = None
                elif ratio > RATIO_MAX and self.quadros_processo[processo.identificador] < len(self.simulador.quadros):
                    self.quadros_processo[processo.identificador] += 1
                    # enquanto quantidade de quadros disponíveis na MP não é compatível com
                    # numero de quadros necessitados pelo processo
                    if not self.simulador.quadros.count(None):
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
                    vazio = self.simulador.quadros.index(None) 

            if not vazio:
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
            if self.acessos[processo.identificador] % VERIFICAO == 1:
                ratio = 1.0*self.falhas[processo.identificador]/self.acessos[processo.identificador]
                if ratio < RATIO_MIN and self.quadros_processo[processo.identificador] > 1:
                    self.quadros_processo[processo.identificador] -= 1
                elif ratio > RATIO_MAX and self.quadros_processo[processo.identificador] < len(self.simulador.quadros):
                    self.quadros_processo[processo.identificador] += 1
                    

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

            self.falhas[processo.identificador] += 1
        self.log()