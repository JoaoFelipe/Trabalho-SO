# -*- coding: utf-8 -*-
from collections import deque
from gerenciadores.gerenciador_memoria import GerenciadorMemoria, GerenciadorLocal


class FifoLocal(GerenciadorMemoria, GerenciadorLocal):

    def __init__(self, simulador):
        super(FifoLocal, self).__init__(simulador)
        self.processos_na_mp = deque()
        for processo in self.simulador.processos.values():
            self.criar_processo(processo)

    def retira_pagina(self, processo):
        """
        Seleciona quadro do ponteiro para desalocar
        Avança ponteiro (e volta para 0 se passar do numero de quadros)
        Desaloca pagina do quadro selecionado
        """
        vazio = processo.conjunto_residente[processo.ponteiro]
        self.desalocar_quadro(vazio)
        return vazio

    def suspender_processo(self, processo, remover=False):
        """
        Suspende processo e apaga conjunto residente
        """
        super(FifoLocal, self).suspender_processo(processo, remover=remover)
        processo.conjunto_residente = []
        processo.ponteiro = -1

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Aloca pagina no quadro pelo FIFO

        Se pagina de processo suspenso for carregada, processo deixa de ser suspenso
        -> processo adicionado na fila de processos
        -> ponteiro da fila de páginas definido

        Se quadro não estiver no conjunto residente, adicioná-lo
        """
        processo = pagina.processo
        if processo.estaSuspenso():
            self.processos_na_mp.append(processo)
            processo.ponteiro = 0
        if quadro not in processo.conjunto_residente:
            processo.conjunto_residente.append(quadro)
        super(FifoLocal, self).alocar_pagina_no_quadro(
            quadro,
            pagina,
            entrada_tp=entrada_tp
        )

    def criar_processo(self, processo):
        """
        Cria processo, definindo ponteiro inicial como -1
        e conjunto_residente vazio
        Também define o numero maximo de quadros para o processos
        """
        processo.ponteiro = -1
        processo.conjunto_residente = []
        self.quadros_para_processo(processo)

    def desalocar_quadro(self, quadro, remover=False):
        """
        Avança ponteiro do processo (e volta para 0 se passar do numero de quadros)
        Remove processo da fila de processos na mp, se não sobrarem quadros do processo na MP
        """
        pagina = self.simulador.quadros[quadro]
        super(FifoLocal, self).desalocar_quadro(quadro, remover)
        if pagina:
            processo = pagina.processo
            if processo.ponteiro == quadro:
                processo.ponteiro = (processo.ponteiro + 1) % len(processo.quadros)
            if processo.estaSuspenso() and processo in self.processos_na_mp:
                self.processos_na_mp.remove(processo)
                processo.conjunto_residente = []
                processo.ponteiro = -1
