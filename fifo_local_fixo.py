# -*- coding: utf-8 -*-
from collections import deque as queue
from gerenciador_memoria import GerenciadorMemoria, GerenciadorLocal
from mensagem import PresenteMensagem


class FifoLocalFixo(GerenciadorMemoria, GerenciadorLocal):

    def __init__(self, simulador):
        super(FifoLocalFixo, self).__init__(simulador)
        self.processos_na_mp = queue()
        quadros_processo = self.quadros_por_processo()
        for i, processo in enumerate(self.simulador.processos):
            processo.maximo_quadros = quadros_processo[i]
            processo.ponteiro = -1
            processo.conjunto_residente = []

    def continua_acesso(self, processo, pagina, entrada_tp):
        if entrada_tp.presente:
            # página já está na MP, apenas acessa
            self.simulador.mudancas.append(PresenteMensagem(pagina))
        elif not processo.estaSuspenso():
            # se processo está na MP
            # seleciona quadro do ponteiro para esvaziar
            # avança ponteiro (e volta para 0 se passar do numero de quadros)
            vazio = processo.conjunto_residente[processo.ponteiro]
            processo.ponteiro = (processo.ponteiro + 1) % processo.maximo_quadros
            self.desalocar_quadro(vazio)
            # coloca página acessada na MP
            self.alocar_pagina_no_quadro(vazio, pagina)
        else:
            # se processo não estiver na MP
            # enquanto quantidade de quadros disponíveis na MP não é compatível com
            # numero de quadros necessitados pelo processo
            while self.simulador.quadros.count(None) < processo.maximo_quadros:
                # seleciona processo para suspender
                esvaziar_processo = self.processos_na_mp.pop()
                self.suspender_processo(esvaziar_processo)
            # carrega conjunto residente fixo para a memória
            self.alocar_paginas_por_localidade(
                processo,
                pagina.numero,
                processo.maximo_quadros
            )

    def suspender_processo(self, processo):
        """
        Sobreescrevendo método de suspender processo para atualizar:
        -lista de quadros em MP (deixar vazia)
        -ponteiro do processo na lista de ponteiros (deixar == -1)
        """
        super(FifoLocalFixo, self).suspender_processo(processo)
        processo.conjunto_residente = []
        processo.ponteiro = -1

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Sobreescrevendo método de alocar página para:

        --definir que se uma página de um processo suspenso for carregada,
        o processo deixa de ser suspenso:
        ----é adicionado a uma fila de processos, para FIFO de processos
        ----ponteiro interno dele passa a ser 0, para a FIFO interna de suas páginas

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
        super(FifoLocalFixo, self).alocar_pagina_no_quadro(quadro, pagina, entrada_tp=entrada_tp)
