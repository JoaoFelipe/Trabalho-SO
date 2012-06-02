# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria, GerenciadorLocal
from collections import deque


class LRULocal(GerenciadorMemoria, GerenciadorLocal):

    def __init__(self, simulador):
        super(LRULocal, self).__init__(simulador)
        self.processos_na_mp = deque()
        for processo in self.simulador.processos.values():
            self.criar_processo(processo)

    def retira_pagina(self, processo):
        """
        Seleciona quadro do inicio da fila de referencias para desalocar
        Desaloca pagina do quadro selecionado
        """
        vazio = processo.referencias.popleft()
        self.desalocar_quadro(vazio)
        return vazio

    def suspender_processo(self, processo, remover=False):
        """
        Apaga conjunto_residente e referencias ao suspender_processo
        """
        super(LRULocal, self).suspender_processo(processo, remover=remover)
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

    def criar_processo(self, processo):
        """
        Cria processo, definindo deque de referencias vazio e
        conjunto_residente vazio
        Também define o numero maximo de quadros para o processos
        """
        processo.referencias = deque()
        processo.conjunto_residente = []
        self.quadros_para_processo(processo)

    def desalocar_quadro(self, quadro, remover=False):
        """
        Remove quadro do conjunto_residente do processo
        Remove processo da fila de processos na mp, se não sobrarem quadros do processo na MP
        """
        pagina = self.simulador.quadros[quadro]
        super(LRULocal, self).desalocar_quadro(quadro, remover)
        if pagina:
            processo = pagina.processo
            if quadro in processo.referencias:
                processo.referencias.remove(quadro)
            if processo.estaSuspenso() and processo in self.processos_na_mp:
                self.processos_na_mp.remove(processo)
                processo.conjunto_residente = []
                processo.referencias = deque()
