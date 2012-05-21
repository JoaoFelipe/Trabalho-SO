# -*- coding: utf-8 -*-
from mensagem import PresenteMensagem
from fifo_local import FifoLocal


class FifoLocalFixo(FifoLocal):

    def continua_acesso(self, processo, pagina, entrada_tp):
        if entrada_tp.presente:
            # página já está na MP, apenas acessa
            self.simulador.mudancas.append(PresenteMensagem(pagina))
        elif not processo.estaSuspenso():
            # se processo está na MP
            self.substitui_pagina_fifo(processo, pagina)
        else:
            # se processo não estiver na MP
            # suspende processos na ordem FIFO até liberar espaço suficiente
            # na MP para o conjunto residente e carrega o conjunto fixo
            self.alocar_n_paginas(
                processo,
                pagina.numero,
                processo.maximo_quadros,
                ordem=self.processos_na_mp,
            )
