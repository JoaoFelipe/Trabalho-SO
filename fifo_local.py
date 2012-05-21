# -*- coding: utf-8 -*-
from collections import deque as queue
from gerenciador_memoria import GerenciadorMemoria, GerenciadorLocal


class FifoLocal(GerenciadorMemoria, GerenciadorLocal):

    def __init__(self, simulador):
        super(FifoLocal, self).__init__(simulador)
        self.processos_na_mp = queue()
        quadros_processo = self.quadros_por_processo()
        for i, processo in enumerate(self.simulador.processos):
            processo.maximo_quadros = quadros_processo[i]
            processo.ponteiro = -1
            processo.conjunto_residente = []

    def substitui_pagina_fifo(self, processo, pagina):
        """
        Seleciona quadro a ser retirado pela política FIFO
        Retira a página do quadros
        Aloca nova pagina ao quadro
        """
        vazio = self.retira_pagina_fifo(processo)
        self.alocar_pagina_no_quadro(vazio, pagina)

    def retira_pagina_fifo(self, processo):
        """
        Seleciona quadro do ponteiro para desalocar
        Avança ponteiro (e volta para 0 se passar do numero de quadros)
        Desaloca pagina do quadro selecionado
        """
        vazio = processo.conjunto_residente[processo.ponteiro]
        processo.ponteiro = (processo.ponteiro + 1) % processo.maximo_quadros
        self.desalocar_quadro(vazio)
        return vazio

    def suspender_processo(self, processo):
        """
        Sobreescrevendo método de suspender processo para atualizar:
        -lista de quadros em MP (deixar vazia)
        -ponteiro do processo na lista de ponteiros (deixar == -1)
        """
        super(FifoLocal, self).suspender_processo(processo)
        processo.conjunto_residente = []
        processo.ponteiro = -1

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Sobreescrevendo método de alocar página para:

        --definir que se uma página de um processo suspenso for carregada,
        o processo deixa de ser suspenso:
        ----é adicionado a uma fila de processos, para FIFO de processos
        ----ponteiro interno dele passa a ser 0, para a FIFO interna de páginas

        --definir que se um quadro que não estava no conjunto residente
        for alocado ao processo, ele deve entrar no conjunto residente
        (isso é válido para quando o processo está sendo carregado,
        a FIFO interna segue a ordem de adição ao conjunto residente)
        """
        processo = pagina.processo
        if processo.estaSuspenso():
            self.processos_na_mp.appendleft(processo)
            processo.ponteiro = 0
        if quadro not in processo.conjunto_residente:
            processo.conjunto_residente.append(quadro)
        super(FifoLocal, self).alocar_pagina_no_quadro(
            quadro,
            pagina,
            entrada_tp=entrada_tp
        )
