# -*- coding: utf-8 -*-
from base.utils import EqualByUnicode


class EnderecoMensagem(EqualByUnicode):
    def __init__(self, linha):
        self.linha = linha

    def __unicode__(self):
        return u"Executando instrução: %s" % (self.linha)


class TerminouMensagem(EqualByUnicode):
    def __unicode__(self):
        return u"Execução finalizada"


class ModificadaMensagem(EqualByUnicode):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Página %s do processo %s salva na memória secundária" % (self.pagina.numero, self.pagina.processo.identificador)


# class PresenteMensagem(EqualByUnicode):
#     def __init__(self, pagina):
#         self.pagina = pagina

#     def __unicode__(self):
#         return u"Página %s do processo %s já está na memória principal" % (self.pagina.numero, self.pagina.processo.identificador)


class CarregadaMensagem(EqualByUnicode):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Página %s do processo %s foi carregada na memória principal" % (self.pagina.numero, self.pagina.processo.identificador)


class QuadroModificadoMensagem(EqualByUnicode):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Quadro com página %s do processo %s foi modificado" % (self.pagina.numero, self.pagina.processo.identificador)


class QuadroDesalocadoMensagem(EqualByUnicode):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Quadro com página %s do processo %s foi desalocado" % (self.pagina.numero, self.pagina.processo.identificador)


class QuadroAcessadoMensagem(EqualByUnicode):
    def __init__(self, pagina):
        self.pagina = pagina

    def __unicode__(self):
        return u"Quadro com página %s do processo %s foi acessado" % (self.pagina.numero, self.pagina.processo.identificador)


class CriarProcessoMensagem(EqualByUnicode):
    def __init__(self, processo):
        self.processo = processo

    def __unicode__(self):
        return u"Processo P%s foi criado" % (self.processo.identificador)


class RemoverProcessoMensagem(EqualByUnicode):
    def __init__(self, processo):
        self.processo = processo

    def __unicode__(self):
        return u"Processo P%s foi removido" % (self.processo.identificador)
