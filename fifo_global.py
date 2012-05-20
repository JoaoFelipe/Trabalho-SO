# -*- coding: utf-8 -*-
from gerenciador_memoria import GerenciadorMemoria
from mensagem import ModificadaMensagem, CarregadaMensagem, PresenteMensagem

class FifoGlobal(GerenciadorMemoria):

	def __init__(self, simulador):
		super(FifoGlobal,self).__init__(simulador)
		self.ponteiro = 0

	def continua_acesso(self, processo, pagina, entrada_tp):
		# se pagina não estiver na MP
		if not entrada_tp.presente:
			# se existir espaço vazio na MP
			if None in self.simulador.quadros:
				# seleciona quadro vazio
				vazio = self.simulador.quadros.index(None) 
			else:
				# seleciona quadro do ponteiro para esvaziar
				# avança ponteiro (e volta para 0 se passar do numero de quadros)
				esvaziar = self.ponteiro
				self.ponteiro = (self.ponteiro + 1) % len(self.simulador.quadros)

				pagina_retirada = self.simulador.quadros[esvaziar]
				entrada_tp_retirada = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
				# se for modificada, salva na memória secundária
				if entrada_tp_retirada.modificado:
					self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
				# reseta informacoes da página retirada 
				entrada_tp_retirada.presente = 0
				entrada_tp_retirada.modificado = 0
				vazio = esvaziar
			# coloca página acessada na MP
			entrada_tp.quadro = vazio
			entrada_tp.presente = 1
			self.simulador.quadros[vazio] = pagina
			self.simulador.mudancas.append(CarregadaMensagem(pagina))
		else:
			# página já está na MP, apenas acessa
			self.simulador.mudancas.append(PresenteMensagem(pagina))