# -*- coding: utf-8 -*-

class EnderecoMensagem(object):
    def __init__(self, linha):
        self.linha = linha

    def __unicode__(self):
        return u"Executando instrução: "+ self.linha

class TerminouMensagem(object):
    def __unicode__(self):
        return u"Execução finalizada"

class ModificadaMensagem(object):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Página %s do processo %s salva na memória secundária" % (self.pagina.numero, self.pagina.processo.identificador)

class PresenteMensagem(object):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Página %s do processo %s já está na memória principal" % (self.pagina.numero, self.pagina.processo.identificador)

class CarregadaMensagem(object):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Página %s do processo %s foi carregada na memória principal" % (self.pagina.numero, self.pagina.processo.identificador)

class QuadroModificadoMensagem(object):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Quadro com página %s do processo %s foi modificado" % (self.pagina.numero, self.pagina.processo.identificador)
