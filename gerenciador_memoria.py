# -*- coding: utf-8 -*-
from mensagem import QuadroModificadoMensagem
from mensagem import CarregadaMensagem, ModificadaMensagem


class GerenciadorMemoria(object):

    def __init__(self, simulador):
        self.simulador = simulador

    def continua_acesso(self, processo, pagina, entrada_pagina):
        """
        Implementa o acesso específico de cada política
        """
        pass

    def acessar(self, num_processo, tipo, endereco):
        """
        Acesso geral, usado por todas políticas de GM
        Se for acesso de modificação, seta o bit modificado
        da TP como 1
        """
        processo = self.simulador.processos[num_processo]
        num_pagina = self.descobre_pagina(endereco)
        pagina = processo.paginas[num_pagina]
        entrada_tp = processo.tabela_paginas[num_pagina]
        self.continua_acesso(processo, pagina, entrada_tp)
        # se página foi modificada, seta bit M para 1
        if tipo == "W":
            entrada_tp.modificado = 1
            self.simulador.mudancas.append(QuadroModificadoMensagem(pagina))

    def descobre_pagina(self, endereco):
        """
        Descobre o número da página:
        Pega os primeiros X bits do endereco e converte para int
        X = (Total de bits do endereco) - (Numero de bits do offset da pagina)
        """
        return int(endereco[:-self.simulador.numero_bits_pagina()], 2)

    def alocar_pagina_no_quadro(self, quadro, pagina, entrada_tp=None):
        """
        Coloca 'pagina' no 'quadro' da MP
        Na tabela de páginas, coloca o número do quadro e o bit presente = 1
        """
        if entrada_tp is None:
            entrada_tp = pagina.entrada_tp
        entrada_tp.quadro = quadro
        entrada_tp.presente = 1
        self.simulador.quadros[quadro] = pagina
        self.simulador.mudancas.append(CarregadaMensagem(pagina))

    def desalocar_quadro(self, quadro):
        """
        Desaloca quadro da MP
        Seta bit presente e modificado da pagina na TP para 0
        Se quadro foi modificado, indica a passagem dele para a MS
        """
        pagina = self.simulador.quadros[quadro]
        entrada_tp = pagina.entrada_tp
        # se for modificada, salva na memória secundária
        if entrada_tp.modificado:
            self.simulador.mudancas.append(ModificadaMensagem(pagina))
        # reseta informacoes da página retirada
        entrada_tp.presente = 0
        entrada_tp.modificado = 0
        self.simulador.quadros[quadro] = None
