# -*- coding: utf-8 -*-
from fifo_local import FifoLocal
from mensagem import PresenteMensagem

VERIFICAO = 4
RATIO_MIN = 0.3
RATIO_MAX = 0.7
RESTO = 0


class FifoLocalVariavel(FifoLocal):

    def __init__(self, simulador):
        super(FifoLocalVariavel, self).__init__(simulador)
        for processo in simulador.processos:
            processo.falhas = 0
            processo.acessos = 0
            processo.add_method(lambda s: 1.0 * s.falhas / s.acessos, "ratio")

    def ajusta_processo_na_mp(self, processo, pagina):
        """
        Verifica o ratio do processo que está na MP:
        se < RATIO_MIN: diminui conjunto residente do processo
          desalocando um pelo FIFO
        se > RATIO_MAX: aumenta conjunto residente do processo
          carrega uma pagina proxima da pagina acessada (ou a propria)
          se for necessario, suspende algum processos
        """
        alocou = False
        if processo.acessos % VERIFICAO == RESTO:
            if processo.ratio() < RATIO_MIN and processo.maximo_quadros > 1:
                processo.maximo_quadros -= 1
                vazio = self.retira_pagina_fifo(processo)
                processo.conjunto_residente.remove(vazio)
                # verifica se página acessada estava no quadro removido
                if pagina.entrada_tp.quadro == vazio:
                    self.substitui_pagina_fifo(processo, pagina)
                    alocou = True
            elif processo.ratio() > RATIO_MAX and processo.maximo_quadros < len(self.simulador.quadros):
                processo.maximo_quadros += 1
                self.alocar_n_paginas(
                    processo,
                    pagina.numero,
                    1,
                    ordem=self.processos_na_mp,
                )
                alocou = True
        return alocou

    def ajusta_processo_na_ms(self, processo):
        """
        Verifica o ratio do processo que está na MS:
        se < RATIO_MIN: diminui numero maximo_quadros do processo
        se > RATIO_MAX: aumenta numero maximo_quadros do processo
        """
        if processo.acessos % VERIFICAO == RESTO:
            if processo.ratio() < RATIO_MIN and processo.maximo_quadros > 1:
                processo.maximo_quadros -= 1
            elif processo.ratio() > RATIO_MAX and processo.maximo_quadros < len(self.simulador.quadros):
                processo.maximo_quadros += 1

    def continua_acesso(self, processo, pagina, entrada_tp):
        processo.acessos += 1
        if not entrada_tp.presente:
            processo.falhas += 1
        if not processo.estaSuspenso():

            # se processo estiver na MP
            alocou = self.ajusta_processo_na_mp(processo, pagina)
            if not alocou and entrada_tp.presente:
                # já estava presente antes de ajustar tamanho
                self.simulador.mudancas.append(PresenteMensagem(pagina))
            elif not alocou:
                # pagina acessada não está presente na MP
                self.substitui_pagina_fifo(processo, pagina)
        else:
            # se processo não estiver na MP
            self.ajusta_processo_na_ms(processo)

            # suspende processos na ordem FIFO até liberar espaço suficiente
            # na MP para o conjunto residente e carrega o conjunto fixo
            self.alocar_n_paginas(
                processo,
                pagina.numero,
                processo.maximo_quadros,
                ordem=self.processos_na_mp,
            )
