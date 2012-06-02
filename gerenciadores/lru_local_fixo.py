# -*- coding: utf-8 -*-
#from base.mensagem import PresenteMensagem
from gerenciadores.lru_local import LRULocal
from gerenciadores.gerenciador_memoria_local_fixo import GerenciadorMemoriaLocalFixo


class LRULocalFixo(LRULocal, GerenciadorMemoriaLocalFixo):

    def __init__(self, simulador):
        super(LRULocalFixo, self).__init__(simulador)

    def acessa_presente(self, quadro):
        """
        Coloca processo acessado no final da fila de referencias de processos
        Coloca quadro acessado no final da fila de referencias do quadro
        """
        pagina = self.simulador.quadros[quadro]
        processo = pagina.processo
        if processo in self.processos_na_mp:
            self.processos_na_mp.remove(processo)
        self.processos_na_mp.append(processo)
        if quadro in processo.referencias:
            processo.referencias.remove(quadro)
        processo.referencias.append(quadro)
