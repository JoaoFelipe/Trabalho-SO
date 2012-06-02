# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria_global import GerenciadorMemoriaGlobal
from collections import deque
#from base.mensagem import PresenteMensagem


class LRUGlobal(GerenciadorMemoriaGlobal):

    def __init__(self, simulador):
        super(LRUGlobal, self).__init__(simulador)
        self.referencias = deque()

    def retira_pagina(self):
        """
        Seleciona quadro pela fila de referências
        """
        vazio = self.referencias.popleft()
        self.desalocar_quadro(vazio)
        return vazio

    def acessa_presente(self, quadro):
        """
        Passa página acessada para final da fila de referências
        """
        if quadro in self.referencias:
            self.referencias.remove(quadro)
        self.referencias.append(quadro)

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Passa página alocada para final da fila de referências
        """
        super(LRUGlobal, self).alocar_pagina_no_quadro(quadro, pagina, entrada_tp)
        self.acessa_presente(quadro)

    def desalocar_quadro(self, quadro, remover=False):
        """
        Remove referencia do quadro desalocado da lista de referências
        """
        super(LRUGlobal, self).desalocar_quadro(quadro, remover)
        if quadro in self.referencias:
            self.referencias.remove(quadro)
