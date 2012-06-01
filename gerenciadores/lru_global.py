# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria
from collections import deque
#from base.mensagem import PresenteMensagem


class LRUGlobal(GerenciadorMemoria):

    def __init__(self, simulador):
        super(LRUGlobal, self).__init__(simulador)
        self.referencias = deque()

    def continua_acesso(self, processo, pagina, entrada_tp):
        # se pagina não estiver na MP
        if not entrada_tp.presente:
            # se existir espaço vazio na MP
            if None in self.simulador.quadros:
                # seleciona quadro vazio
                vazio = self.simulador.quadros.index(None)
            else:
                # seleciona quadro do inicio da fila de referencias
                # desaloca quadro selecionado
                vazio = self.referencias.popleft()
                self.desalocar_quadro(vazio)
            # coloca página acessada na MP
            self.alocar_pagina_no_quadro(vazio, pagina, entrada_tp=entrada_tp)
            # coloca quadro no final da fila de referencias
            self.referencias.append(entrada_tp.quadro)
        else:
            # remove quadro da fila de referencias e coloca no final
            # final da fila indica acessos mais recentes
            self.referencias.remove(entrada_tp.quadro)
            self.referencias.append(entrada_tp.quadro)
