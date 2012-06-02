# -*- coding: utf-8 -*-
#from base.mensagem import PresenteMensagem
from gerenciadores.fifo_local import FifoLocal
from gerenciadores.gerenciador_memoria_local_fixo import GerenciadorMemoriaLocalFixo


class FifoLocalFixo(FifoLocal, GerenciadorMemoriaLocalFixo):

    def __init__(self, simulador):
        super(FifoLocalFixo, self).__init__(simulador)
