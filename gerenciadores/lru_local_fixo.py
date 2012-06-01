# -*- coding: utf-8 -*-
#from base.mensagem import PresenteMensagem
from gerenciadores.lru_local import LRULocal


class LRULocalFixo(LRULocal):

    def continua_acesso(self, processo, pagina, entrada_tp):
        if entrada_tp.presente:
            # remove processo da fila de referencias e coloca no final
            # final da fila indica acessos mais recentes
            self.processos_na_mp.remove(processo)
            self.processos_na_mp.append(processo)
        elif not processo.estaSuspenso():
            # se processo está na MP
            self.substitui_pagina_lru(processo, pagina)
        else:
            # se processo não estiver na MP
            # suspende processos na ordem LRU até liberar espaço suficiente
            # na MP para o conjunto residente e carrega o conjunto fixo
            self.alocar_n_paginas(
                processo,
                pagina.numero,
                processo.maximo_quadros,
                ordem=list(reversed(self.processos_na_mp)),
            )
        # remove quadro da fila de referencias e coloca no final da fila
        # o final da fila indica acessos mais recentes
        processo.referencias.remove(entrada_tp.quadro)
        processo.referencias.append(entrada_tp.quadro)
