from gerenciador_memoria import GerenciadorMemoria
from mensagem import ModificadaMensagem, CarregadaMensagem, PresenteMensagem

class FifoGlobal(GerenciadorMemoria):

	def __init__(self, simulador):
		super(FifoGlobal,self).__init__(simulador)
		self.ponteiro = 0

	def continua_acesso(self, processo, pagina, entrada_pagina):
		if not entrada_pagina.presente :
			if None in self.simulador.quadros:
				vazio = self.simulador.quadros.index(None) 
			else:
				esvaziar = self.ponteiro
				self.ponteiro += 1
				pagina_retirada = self.simulador.quadros[esvaziar]
				entrada_tp = pagina_retirada.processo.tabela_paginas[pagina_retirada.numero]
				if entrada_tp.modificado:
					self.simulador.mudancas.append(ModificadaMensagem(pagina_retirada))
				entrada_tp.presente = 0
				entrada_tp.modificado = 0
				vazio = esvaziar
			entrada_pagina.quadro = vazio
			entrada_pagina.presente = 1
			self.simulador.quadros[vazio] = pagina
			self.simulador.mudancas.append(CarregadaMensagem(pagina))
		else:
			self.simulador.mudancas.append(PresenteMensagem(pagina))