# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria
#from base.mensagem import PresenteMensagem


class GerenciadorMemoriaLocalFixo(GerenciadorMemoria):

    def __init__(self, simulador):
        super(GerenciadorMemoriaLocalFixo, self).__init__(simulador)

    def continua_acesso(self, processo, pagina, entrada_tp):
        if not entrada_tp.presente:
            # página não está na MP
            if not processo.estaSuspenso():
                # se processo está na MP
                self.substitui_pagina(processo, pagina)
            else:
                # se processo não estiver na MP
                # suspende processos na ordem da política até liberar espaço
                # na MP para o conjunto residente e carrega o conjunto fixo
                self.alocar_n_paginas(
                    processo,
                    pagina.numero,
                    processo.maximo_quadros,
                    ordem=list(reversed(self.processos_na_mp)),
                )
        # após carregar página, ou verificar que ela está presente,
        # acessa de acordo com a política
        self.acessa_presente(pagina.entrada_tp.quadro)

    def substitui_pagina(self, processo, pagina):
        """
        Seleciona quadro a ser retirado pela política
        Retira a página do quadro
        Aloca nova pagina ao quadro
        """
        vazio = self.retira_pagina(processo)
        self.alocar_pagina_no_quadro(vazio, pagina)

    def retira_pagina(self):
        """
        Implementa o modo de retirar a página em cada política
        """
        pass

    def acessa_presente(self, quadro):
        """
        Implementa o que fazer quando acessar algum presente em cada política
        """
        pass
