# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria, GerenciadorLocal
from collections import deque


class LRULocal(GerenciadorMemoria, GerenciadorLocal):

    def __init__(self, simulador):
        super(LRULocal, self).__init__(simulador)
        self.processos_na_mp = deque()
        self.quadros_por_processo()
        for i, processo in enumerate(self.simulador.processos):
            processo.referencias = deque()
            processo.conjunto_residente = []

    def substitui_pagina_lru(self, processo, pagina):
        """
        Seleciona quadro a ser retirado pela política LRU
        Retira a página do quadros
        Aloca nova pagina ao quadro
        """
        vazio = self.retira_pagina_lru(processo)
        self.alocar_pagina_no_quadro(vazio, pagina)

    def retira_pagina_lru(self, processo):
        """
        Seleciona quadro do inicio da fila de referencias para desalocar
        Desaloca pagina do quadro selecionado
        """
        vazio = processo.referencias.popleft()
        self.desalocar_quadro(vazio)
        return vazio

    def suspender_processo(self, processo):
        """
        Sobreescrevendo método de suspender processo para atualizar:
        -lista de quadros em MP (deixar vazia)
        -ponteiro do processo na lista de ponteiros (deixar == -1)
        """
        super(LRULocal, self).suspender_processo(processo)
        self.processos_na_mp.remove(processo)
        processo.conjunto_residente = []
        processo.referencias = deque()

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Sobreescrevendo método de alocar página para:

        --definir que se uma página de um processo suspenso for carregada,
        o processo deixa de ser suspenso:
        ----é adicionado a um deque de processos, para LRU de processos
        ----referencias de paginas do processo inicializada, para a LRU interna

        --definir que se um quadro que não estava no conjunto residente
        for alocado ao processo, ele deve entrar no conjunto residente e a
        a referencia a ele deve ser adicionada ao final da fila para a
        LRU interna de páginas
        """
        processo = pagina.processo
        if processo.estaSuspenso():
            self.processos_na_mp.append(processo)
            processo.referencias = deque()
        if quadro not in processo.conjunto_residente:
            processo.conjunto_residente.append(quadro)
        super(LRULocal, self).alocar_pagina_no_quadro(
            quadro,
            pagina,
            entrada_tp=entrada_tp
        )
        processo.referencias.append(quadro)
