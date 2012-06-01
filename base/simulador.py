# -*- coding: utf-8 -*-

from math import log
from collections import OrderedDict
from base.processo import Processo
from base.mensagem import EnderecoMensagem, TerminouMensagem
from base.utils import HistoricoQuadros
from gerenciadores.gerenciador_memoria import GerenciadorMemoria


class TamanhoMemoriaFisicaException(Exception):
    def __str__(self):
        return "O Tamanho da memória física deve ser múltiplo do quadro"


class TamanhoMemoriaSecundariaException(Exception):
    def __str__(self):
        return "O Tamanho da memória secundária não é suficiente para alocar todos processos"


class EnderecoLogicoInvalidoException(Exception):
    def __init__(self, endereco):
        self.endereco = endereco

    def __str__(self):
        return "O endereco lógico %s é maior do que o tamanho do endereço lógico" % (self.endereco)


class Simulador(object):

    def __init__(self, pagina, endereco_logico, memoria_fisica, memoria_secundaria, processos, arquivo="processos", gerenciador_memoria=GerenciadorMemoria):
        self.ler_arquivo_de_processos(arquivo)
        #Verifica se tamanho da memória física é multiplo do tamanho da página
        if memoria_fisica % pagina != 0:
            raise TamanhoMemoriaFisicaException
        #Verifica se memória secundária possui espaço suficiente para guardar processos
        if sum(processos) > memoria_secundaria:
            raise TamanhoMemoriaSecundariaException

        self.tamanho_pagina = pagina
        self.tamanho_endereco_logico = endereco_logico
        self.tamanho_memoria_fisica = memoria_fisica
        self.tamanho_memoria_secundaria = memoria_secundaria
        self.mudancas = HistoricoQuadros(self)
        # Monta lista de processos pelos tamanhos dos processos - Pode representar a memoria secundaria
        self.processos = OrderedDict([(i, Processo(i, processos[i], pagina)) for i in xrange(len(processos))])

        # Monta a lista de quadros - representa a memoria principal
        self.quadros = [None] * (memoria_fisica / pagina)
        self.gerenciador_memoria = gerenciador_memoria(self)

    def numero_bits_pagina(self):
        return int(log(self.tamanho_pagina, 2))

    def acessar(self, linha):
        processo, tipo, endereco = linha.split(' ')

        #Tirar o P
        num_processo = int(processo[1:])

        # Transformar em binario se for da forma (X)2
        if '2' in endereco:
            endereco = bin(int(endereco[1:-2]))[2:]

        #Completar bits de endereco
        endereco = "0" * (self.tamanho_endereco_logico - len(endereco)) + endereco

        # Verifica se tamanho do endereço é maior do que tamanho do endereço lógico
        if len(endereco) > self.tamanho_endereco_logico:
            raise EnderecoLogicoInvalidoException(endereco)

        return self.gerenciador_memoria.acessar(num_processo, tipo, endereco)

    def ler_arquivo_de_processos(self, arquivo):
        self.linhas = []
        self.ponteiro = -1
        with open(arquivo) as arquivo:
            for linha in arquivo:
                self.linhas.append(linha.split('\n')[0])

    def next(self):
        self.mudancas = HistoricoQuadros(self)
        self.ponteiro += 1
        if self.ponteiro < len(self.linhas):
            self.mudancas.append(EnderecoMensagem(self.linhas[self.ponteiro]))
            self.acessar(self.linhas[self.ponteiro])
        else:
            self.mudancas.append(TerminouMensagem())

    def add_processo(self, identificador, tamanho):
        self.processos[identificador] = Processo(identificador, tamanho, self.tamanho_pagina)
        return self.processos[identificador]

    def remover_processo(self, processo):
        del self.processos[processo.identificador]
