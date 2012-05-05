# -*- coding: utf-8 -*-

from processo import Processo
from gerenciador_memoria import GerenciadorMemoria

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
        return "O endereco lógico %s é maior do que o tamanho do endereço lógico"%(self.endereco)


class Simulador(object):

    def __init__(self, pagina, endereco_logico, memoria_fisica, memoria_secundaria, processos, gerenciador_memoria=GerenciadorMemoria):
        if memoria_fisica % pagina != 0:
            raise TamanhoMemoriaFisicaException
        if sum(processos) > memoria_secundaria:
            raise TamanhoMemoriaSecundariaException
        self.gerenciador_memoria = gerenciador_memoria(self)
        self.tamanho_pagina = pagina
        self.tamanho_endereco_logico = endereco_logico
        self.tamanho_memoria_fisica = memoria_fisica
        self.tamanho_memoria_secundaria = memoria_secundaria
        # Monta lista de processos pelos tamanhos dos processos - Pode representar a memoria secundaria
        self.processos = [Processo(i, processos[i], pagina) for i in xrange(len(processos))]
        # Monta a lista de quadros - representa a memoria principal
        self.quadros = [None] * (memoria_fisica / pagina)
        self.gerenciador_memoria.alocacao_inicial()
        
    def acessar(self, linha):
        processo, tipo, endereco = linha.split(' ')
        num_processo = int(processo[1:]) #Tirar o P
        if '2' in endereco:
            endereco = bin(int(endereco[1:-2]))[2:] # Transformar em binario se for da forma (X)2
        endereco = "0"*(self.tamanho_endereco_logico-len(endereco)) + endereco #Completar bits de endereco
        if len(endereco) > self.tamanho_endereco_logico:
            raise EnderecoLogicoInvalidoException(endereco)
        return self.gerenciador_memoria.acessar(num_processo, tipo, endereco)
