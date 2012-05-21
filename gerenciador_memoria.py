# -*- coding: utf-8 -*-
from mensagem import QuadroModificadoMensagem
from mensagem import CarregadaMensagem, ModificadaMensagem
from utils import teto_inteiro


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

    def suspender_processo(self, processo):
        """
        Suspende processo, desalocando todos seus blocos da MP
        """
        for quadro in processo.quadros:
            self.desalocar_quadro(quadro)

    def alocar_paginas_por_localidade(self, processo, pagina_inicial, quantidade):
        """
        Aloca 'quantidade' páginas na MP, seguindo o principio da localidade
        Para pagina inicial 8, em um processo com 11 paginas[0..10]
        alocando 5 na MP, o resultado será:
            8, 9, 10, 7, 6
        No FIFO local, os quadros em que serão alocadas estas páginas serão percorridos nesta ordem
        """
        quadros_inseridos = []
        # não é possível alocar mais quadros do que esta disponivel na MP
        quantidade = min(quantidade, self.simulador.quadros.count(None))

        base = atual = pagina_inicial
        restante = quantidade
        incremento = 1
        while restante > 0 and atual >= 0:
            # procura quadro vazio na MP e coloca pagina na MP
            quadro = self.simulador.quadros.index(None)
            pagina = processo.paginas[atual]
            if not pagina in self.simulador.quadros:
                self.alocar_pagina_no_quadro(quadro, pagina)
                quadros_inseridos.append(quadro)
                restante -= 1
                # se chegar no limite do numero de paginas do processo
                # inverte o loop a partir da pagina acessada
            atual += incremento
            if atual >= len(processo.paginas):
                incremento = -1
                atual = base - 1
        return quadros_inseridos

    def alocar_n_paginas(self, processo, pagina_inicial, quantidade, ordem=None):
        """
        Suspende processos para liberar espaço suficiente para alocar 'quantidade' páginas
        """
        # se ordem não foi definida, pega uma ordem qualquer
        if ordem is None:
            ordem = list(set(pagina.processo for pagina in self.simulador.quadros if pagina is not None))
        # não é possível alocar mais quadros do que o tamanho da MP
        quantidade = min(quantidade, len(self.simulador.quadros))

        reserva = []
        # enquanto quantidade de quadros disponíveis na MP não é compatível com
        # numero de quadros necessitados pelo processo
        while self.simulador.quadros.count(None) < quantidade and ordem:
            # seleciona processo para suspender
            esvaziar_processo = ordem.pop()
            if esvaziar_processo != processo:
                self.suspender_processo(esvaziar_processo)
            else:
                reserva.append(esvaziar_processo)

        # Restaura ordem da fila caso algum processo não tenha sido suspenso
        while ordem:
            reserva.append(ordem.pop())
        while reserva:
            ordem.append(reserva.pop())

        # carrega conjunto residente fixo para a memória
        self.alocar_paginas_por_localidade(
            processo,
            pagina_inicial,
            quantidade
        )


class GerenciadorLocal(object):

    def quadros_por_processo(self):
        """
        Calcula quantidade de quadros por processo,
        Tomando como base o espaço disponível em MP e o número
        de páginas dos dos processos a serem executados

        razao = (numero de quadros da MP) / (total de paginas da MS)
        numero de quadros para Px = teto[razao * (numero de páginas de Px)]
        """
        paginas_de_cada_processo = [len(processo.paginas) for processo in self.simulador.processos]
        razao = len(self.simulador.quadros) / (sum(paginas_de_cada_processo) + .0)
        quadros_por_processo = [teto_inteiro(razao * numero_paginas) for numero_paginas in paginas_de_cada_processo]
        return quadros_por_processo
