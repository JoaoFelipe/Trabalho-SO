# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria
#from base.mensagem import PresenteMensagem


class FifoGlobal(GerenciadorMemoria):

    def __init__(self, simulador):
        super(FifoGlobal, self).__init__(simulador)
        self.ponteiro = 0

    def continua_acesso(self, processo, pagina, entrada_tp):
        # se pagina não estiver na MP
        if not entrada_tp.presente:
            # se existir espaço vazio na MP
            if None in self.simulador.quadros:
                # seleciona quadro vazio
                vazio = self.simulador.quadros.index(None)
            else:
                # seleciona quadro do ponteiro para desalocar
                # avança ponteiro (e volta para 0 se passar do numero de quadros)
                vazio = self.ponteiro
                self.ponteiro = (self.ponteiro + 1) % len(self.simulador.quadros)
                self.desalocar_quadro(vazio)
            # coloca página acessada na MP
            self.alocar_pagina_no_quadro(vazio, pagina, entrada_tp=entrada_tp)
        else:
            pass
            # página já está na MP, apenas acessa
            # self.simulador.mudancas.append(PresenteMensagem(pagina))
