# -*- coding: utf-8 -*-
from gerenciadores.gerenciador_memoria import GerenciadorMemoria
#from base.mensagem import PresenteMensagem


class GerenciadorMemoriaGlobal(GerenciadorMemoria):

    def __init__(self, simulador):
        super(GerenciadorMemoriaGlobal, self).__init__(simulador)

    def continua_acesso(self, processo, pagina, entrada_tp):
        # se pagina não estiver na MP
        if not entrada_tp.presente:
            # carrega página acessada para MP
            self.substitui_pagina(processo, pagina)
        # após carregar página, ou verificar que ela está presente,
        # acessa de acordo com a política
        self.acessa_presente(entrada_tp.quadro)

    def substitui_pagina(self, processo, pagina):
        """
        Se existir espaço vazio na MP, usa o espaço vazio
        Caso contrário, utiliza a política para substituir página
        """
        if None in self.simulador.quadros:
            vazio = self.simulador.quadros.index(None)
        else:
            vazio = self.retira_pagina()
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
