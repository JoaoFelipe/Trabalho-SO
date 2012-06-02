# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria_global import GerenciadorMemoriaGlobal
#from base.mensagem import PresenteMensagem


class FifoGlobal(GerenciadorMemoriaGlobal):

    def __init__(self, simulador):
        super(FifoGlobal, self).__init__(simulador)
        self.ponteiro = 0

    def retira_pagina(self):
        """
        Seleciona a página que está no ponteiro
        """
        vazio = self.ponteiro
        self.desalocar_quadro(vazio)
        return vazio

    def desalocar_quadro(self, quadro, remover=False):
        """
        Se estiver desalocando a página que está no ponteiro,
        avança o ponteiro
        """
        super(FifoGlobal, self).desalocar_quadro(quadro, remover)
        if self.ponteiro == quadro:
            self.ponteiro = (self.ponteiro + 1) % len(self.simulador.quadros)
