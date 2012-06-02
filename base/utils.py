from math import ceil
from copy import copy


def divisao_inteira_superior(x, y):
    return int(ceil((1.0 * x) / y))


class EqualByAttributes(object):
    def __eq__(self, outro):
        return self.__dict__ == outro.__dict__


class EqualByUnicode(object):
    def __eq__(self, outro):
        return unicode(self) == unicode(outro)


class HistoricoQuadros(list):
    def __init__(self, simulador, *args, **kwargs):
        super(HistoricoQuadros, self).__init__(*args, **kwargs)
        self.simulador = simulador
        self.historico = []
        self.historico_tp = []

    def append(self, x):
        super(HistoricoQuadros, self).append(x)
        self.historico.append(self.simulador.quadros[:])
        self.historico_tp.append({pagina: copy(pagina.entrada_tp) for processo in self.simulador.processos.values() for pagina in processo.paginas})

