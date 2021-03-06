# -*- coding: utf-8 -*-
from base.mensagem import QuadroModificadoMensagem
from base.mensagem import CarregadaMensagem, ModificadaMensagem, QuadroDesalocadoMensagem, QuadroAcessadoMensagem, CriarProcessoMensagem, RemoverProcessoMensagem


LIMITE = 0.4
MENOR = 0.3
MAIOR = 0.6


class GerenciadorMemoria(object):

    def __init__(self, simulador):
        self.simulador = simulador

    def continua_acesso(self, processo, pagina, entrada_pagina):
        """
        Implementa o acesso específico de cada política
        """
        pass

    def criar_processo(self, processo):
        """
        Implementa a criacao de processo específica de cada política
        """
        pass

    def remover_processo(self, processo):
        """
        Implementa a remocao de processo específica de cada política
        """
        pass

    def acessar(self, num_processo, tipo, endereco):
        """
        Acesso geral, usado por todas políticas de GM
        Se for leitura ou escrita, acessa processo com a política de GM:
        (self.continua_acesso(processo, pagina, entrada_tp))
        Se for escrita, seta o bit modificado da TP como 1
        Se for criação, adiciona processo no simulador e cria processo setando
        valores padrões de cada política (self.criar_processo(processo))
        Se for fechar, desaloca quadros do processo e remove processo setando
        valores padrões de cada política (self.remover_processo(processo))
        """
        if tipo in ['R', 'W']:
            processo = self.simulador.processos[num_processo]
            self.processo_acessado = processo
            num_pagina = self.descobre_pagina(endereco)
            pagina = processo.paginas[num_pagina]
            entrada_tp = processo.tabela_paginas[num_pagina]
            self.continua_acesso(processo, pagina, entrada_tp)
            # se página foi modificada, seta bit M para 1
            if tipo == "W":
                self.simulador.mudancas.append(QuadroModificadoMensagem(pagina))
                entrada_tp.modificado = 1
            else:
                self.simulador.mudancas.append(QuadroAcessadoMensagem(pagina))
        elif tipo == 'C':
            processo = self.simulador.add_processo(num_processo, int(endereco, 2))
            self.criar_processo(processo)
            self.simulador.mudancas.append(CriarProcessoMensagem(processo))
        elif tipo == 'D':
            processo = self.simulador.processos[num_processo]
            self.suspender_processo(processo, remover=True)
            self.simulador.remover_processo(processo)
            self.remover_processo(processo)
            self.simulador.mudancas.append(RemoverProcessoMensagem(processo))

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
        if (self.simulador.quadros[quadro] != None):
            self.simulador.mudancas.append(QuadroDesalocadoMensagem(self.simulador.quadros[quadro]))
        self.simulador.mudancas.append(CarregadaMensagem(pagina))
        self.simulador.quadros[quadro] = pagina

    def desalocar_quadro(self, quadro, remover=False):
        """
        Desaloca quadro da MP
        Seta bit presente e modificado da pagina na TP para 0
        Se quadro foi modificado, indica a passagem dele para a MS
        """
        pagina = self.simulador.quadros[quadro]
        entrada_tp = pagina.entrada_tp
        if entrada_tp.presente:
            # se for modificada, salva na memória secundária
            if entrada_tp.modificado and not remover:
                self.simulador.mudancas.append(ModificadaMensagem(pagina))
            # reseta informacoes da página retirada
            self.simulador.mudancas.append(QuadroDesalocadoMensagem(pagina))
            entrada_tp.presente = 0
            entrada_tp.modificado = 0
            self.simulador.quadros[quadro] = None

    def suspender_processo(self, processo, remover=False):
        """
        Suspende processo, desalocando todos seus blocos da MP
        """
        for quadro in processo.quadros:
            self.desalocar_quadro(quadro, remover=remover)

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

    def quadros_para_processo(self, processo):
        """
        Calcula quantidade de quadros para processo,
        Tomando como base o espaço disponível em MP e o número
        de páginas do processo

        razao = (total de paginas do processo) / (numero de quadros da MP)
        se razao < LIMITE (0.4), então
            numero de quadros para Px = MENOR (0.3) * tamanho_memoria
        senao
            numero de quadros para Px = MAIOR (0.6) * tamanho_memoria
        """
        simulador = self.simulador
        tamanho_processo = float(len(processo.paginas))
        tamanho_memoria = len(simulador.quadros)
        razao = tamanho_processo / tamanho_memoria
        if razao < LIMITE:
            processo.maximo_quadros = int(round(tamanho_memoria * MENOR))
        else:
            processo.maximo_quadros = int(round(tamanho_memoria * MAIOR))
