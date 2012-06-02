# -*- coding: utf-8 -*-
import sys
import pygame
from collections import namedtuple
from functools import partial
from pygame.locals import *
from base.processo import EntradaTP
from base.mensagem import *
from gerenciadores import *

PRETO = 0, 0, 0
BRANCO = 255, 255, 255
AZUL = 0, 0, 255

DIMENSOES = WIDTH, HEIGHT = 800, 600
TITULO = 'Simulador'

ALTURA_BLOCO = int(0.05 * HEIGHT)
LARGURA_BLOCO = int(0.175 * WIDTH)
MODIFICADO = int((0.175 * 4 / 5) * WIDTH)

TAMANHO_SETA = int((0.175 * 1 / 5) * WIDTH)

ALTURA_ENTRADA_TP = int(0.05 * HEIGHT)
LARGURA_ENTRADA_TP = int(0.3 * WIDTH)

ESPACO_BIT = ALTURA_ENTRADA_TP


MP_TEXT_X = int(0.025 * WIDTH)
POSICAO_MP = int(0.05 * WIDTH)
POSICAO_MS = int(0.775 * WIDTH)
POSICAO_TP = int(0.35 * WIDTH)

TAMANHO_MENSAGEM = int(0.1 * HEIGHT)

TEMPO_ANIMACAO = 60

ALTURA_INSTRUCAO = int(0.025 * HEIGHT)


class Button(namedtuple('Button', ['x', 'y', 'width', 'height', 'function'])):

    def __contains__(self, clique):
        # Verifica se clique acertou o botão
        return self.x <= clique[0] <= self.x + self.width and self.y <= clique[1] <= self.y + self.height


class MovimentoPagina(namedtuple('MovimentoPagina', ['pagina', 'xi', 'yi', 'xf', 'yf'])):

    def __init__(self, *args, **kwargs):
        super(MovimentoPagina, self).__init__(*args, **kwargs)
        self.x = self.xi
        self.y = self.yi

    def move(self, tempo, t_max):
        self.x = int((self.xf - self.xi) * float(tempo) / float(t_max)) + self.xi
        self.y = int((self.yf - self.yi) * float(tempo) / float(t_max)) + self.yi

    def animar(self, interface):
        pagina = self.pagina
        interface.imprimir_bloco_de_pagina(pagina, self.x, self.y)


class MovimentoDesalocar(namedtuple('MovimentoDesalocar', ['pagina', 'xi', 'yi', 'xf', 'yf'])):

    def __init__(self, *args, **kwargs):
        super(MovimentoDesalocar, self).__init__(*args, **kwargs)
        self.x = self.xi
        self.y = self.yf

    def move(self, tempo, t_max):
        self.x = int((self.xf - self.xi) * float(tempo) / float(t_max)) + self.xi

    def animar(self, interface):
        x = self.x - self.xi
        y = self.y - self.yi
        rect = pygame.Rect(self.xi, interface.scroll + self.yi, x, y)
        pygame.draw.rect(interface.screen, BRANCO, rect, 0)
        pygame.draw.rect(interface.screen, AZUL, rect, 1)


class MovimentoModificar(namedtuple('MovimentoModificar', ['pagina', 'xi', 'yi', 'xf', 'yf'])):

    def __init__(self, *args, **kwargs):
        super(MovimentoModificar, self).__init__(*args, **kwargs)
        self.x = self.xi + MODIFICADO
        self.y = self.yf
        self.cadeia = MovimentoAcessar(*args, **kwargs)

    def move(self, tempo, t_max):
        self.x = int((self.xf - self.xi - MODIFICADO) * float(tempo) / float(t_max)) + self.xi + MODIFICADO
        self.cadeia.move(tempo, t_max)
        # self.y = int((self.yf - self.yi) * float(tempo) / float(t_max)) + self.yi

    def animar(self, interface):
        xi = self.xi + MODIFICADO + 1
        yi = self.yi + interface.scroll + 1
        tx = self.x - 1
        # ty = self.y + 2 * ALTURA_BLOCO - self.yf + interface.scroll - 1
        ty = self.yf + interface.scroll - 1
        xf = self.x - 1
        yf = self.yi + interface.scroll + 1
        pointlist = [(xi, yi), (tx, ty), (xf, yf)]
        pygame.draw.polygon(interface.screen, BRANCO, pointlist)
        rect = pygame.Rect(self.xi, interface.scroll + self.yi, LARGURA_BLOCO, ALTURA_BLOCO)
        pygame.draw.rect(interface.screen, AZUL, rect, 1)
        self.cadeia.animar(interface)


class MovimentoAcessar(namedtuple('MovimentoAcessar', ['pagina', 'xi', 'yi', 'xf', 'yf'])):

    def __init__(self, *args, **kwargs):
        super(MovimentoAcessar, self).__init__(*args, **kwargs)
        self.xs = self.xi + LARGURA_BLOCO + TAMANHO_SETA / 3
        self.ys = self.yi + ALTURA_BLOCO / 2

    def move(self, tempo, t_max):
        pass

    def animar(self, interface):
        xs, ys = self.xs, self.ys + interface.scroll
        xsf1, ysf1 = xs + TAMANHO_SETA / 3, ys - ALTURA_BLOCO / 3
        xsf2, ysf2 = xs + TAMANHO_SETA / 3, ys + ALTURA_BLOCO / 3
        xs2, ys2 = self.xs, self.ys + interface.scroll
        pointlist = [(xs, ys), (xsf1, ysf1), (xsf2, ysf2)]
        pygame.draw.polygon(interface.screen, BRANCO, pointlist)
        rect = pygame.Rect(xs + TAMANHO_SETA / 3, ys - ALTURA_BLOCO / 8, TAMANHO_SETA, ALTURA_BLOCO / 4)
        pygame.draw.rect(interface.screen, BRANCO, rect, 0)


#Faz cores aleatórias para cada processo
def calcular_cor(num, numero_processos):
    if numero_processos < 50:
        numero_processos = 50
    to_bin = lambda x: bin(x)[2:]

    cor = list(to_bin(int('FFFFFF', 16)))

    index = 0
    numb = to_bin(num)
    numb = "0" * (len(to_bin(numero_processos)) - len(numb)) + numb
    for l in numb:
        cor[index] = str(int(cor[index] == l))
        index = index + 8
        if index >= 24:
            index -= 23
            if index >= 8:
                index -= 8

    corb = ''.join(cor)
    return (int(corb[0:8], 2), int(corb[8:16], 2), int(corb[16:24], 2))


class PygameInterface(object):

    def __init__(self, simulador):
        if not pygame.font:
            print 'Fontes desabilitadas'
        pygame.init()
        self.width, self.height = DIMENSOES
        self.screen = pygame.display.set_mode(DIMENSOES)
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.scroll = ALTURA_BLOCO
        self.buttons = []
        self.clique = []

        self.simulador = simulador

        self.pagina_atual = None
        self.mensagem = ""
        self.passo = 0
        # while self.passo < 10:
        #     self.passo += 1
        #     self.pagina_atual = None
        #     self.simulador.next()
        self.estado = 0

        self.processo_selecionado = self.simulador.processos.values()[0]

        # Usado para calcular o scroll máximo
        self.final_MP = -max(self.imprimir_MP(), self.imprimir_MS()) + self.height - TAMANHO_MENSAGEM
        self.final_TP = self.imprimir_TP(max(self.simulador.processos.values(), key=lambda x: len(x.paginas)))

        self.velocidade_scroll = 10
        self.scroll_pressionado = 0

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, value):
        self.tempo = 0
        self.movimento = None
        self._estado = value
        # chegou no final
        if self._estado >= len(self.simulador.mudancas):
            self.quadros_aparentes([])
            if self.pagina_atual:
                xi, yi = self.posicao_de_pagina_na_MP(self.pagina_atual, self.quadros)
                self.movimento = MovimentoAcessar(self.pagina_atual, xi, yi, xi + LARGURA_BLOCO, yi + ALTURA_BLOCO)
        else:
            atual = self.simulador.mudancas[self._estado]
            self.mensagem = unicode(atual)
            if type(atual) == EnderecoMensagem:
                self.tempo = 30
                self.quadros_aparentes([0])
            elif type(atual) == TerminouMensagem:
                self.quadros_aparentes([])
            elif type(atual) == ModificadaMensagem:
                self.quadros_aparentes([0])
                quadros = self.simulador.mudancas.historico[self.estado]
                xi, yi = self.posicao_de_pagina_na_MP(atual.pagina, quadros)
                xf, yf = self.posicao_de_pagina_na_MS(atual.pagina)
                self.movimento = MovimentoPagina(atual.pagina, xi, yi, xf, yf)
            # elif type(atual) == PresenteMensagem:
            #     self.quadros_aparentes([1])
            elif type(atual) == CarregadaMensagem:
                self.quadros_aparentes([1])
                quadros = self.quadros
                self.quadros_aparentes([0])
                xi, yi = self.posicao_de_pagina_na_MS(atual.pagina)
                xf, yf = self.posicao_de_pagina_na_MP(atual.pagina, quadros)
                self.movimento = MovimentoPagina(atual.pagina, xi, yi, xf, yf)
            elif type(atual) == QuadroModificadoMensagem:
                self.quadros_aparentes([0])
                quadros = self.simulador.mudancas.historico[self.estado]
                xi, yi = self.posicao_de_pagina_na_MP(atual.pagina, quadros)
                self.movimento = MovimentoModificar(atual.pagina, xi, yi, xi + LARGURA_BLOCO, yi + ALTURA_BLOCO)
                self.pagina_atual = atual.pagina
            elif type(atual) == QuadroDesalocadoMensagem:
                self.quadros_aparentes([0])
                quadros = self.simulador.mudancas.historico[self.estado]
                xi, yi = self.posicao_de_pagina_na_MP(atual.pagina, quadros)
                self.movimento = MovimentoDesalocar(atual.pagina, xi, yi, xi + LARGURA_BLOCO, yi + ALTURA_BLOCO)
            elif type(atual) == QuadroAcessadoMensagem:
                self.quadros_aparentes([1])
                quadros = self.simulador.mudancas.historico[self.estado]
                xi, yi = self.posicao_de_pagina_na_MP(atual.pagina, quadros)
                self.movimento = MovimentoAcessar(atual.pagina, xi, yi, xi + LARGURA_BLOCO, yi + ALTURA_BLOCO)
                self.pagina_atual = atual.pagina
            elif type(atual) == CriarProcessoMensagem:
                self.quadros_aparentes([1])
                self.final_MP = -max(self.imprimir_MP(), self.imprimir_MS()) + self.height - TAMANHO_MENSAGEM
                self.final_TP = self.imprimir_TP(max(self.simulador.processos.values(), key=lambda x: len(x.paginas)))
            else:
                self.quadros_aparentes([1])

    def quadros_aparentes(self, tentativas=range(-1, 1)):
        self.quadros = None
        self.tp = None
        for i in tentativas:
            if self.estado + i < len(self.simulador.mudancas.historico) and self.estado + i >= 0:
                self.quadros = self.simulador.mudancas.historico[self.estado + i]
                self.tp = self.simulador.mudancas.historico_tp[self.estado + i]
            break
        if not self.quadros:
            self.quadros = self.simulador.quadros
            self.tp = {pagina: pagina.entrada_tp  for i, processo in self.simulador.processos.items() for pagina in processo.paginas}

    def imprimir_pagina(self, pagina, x, y):
        centerx = x + LARGURA_BLOCO / 2
        centery = self.scroll + y + ALTURA_BLOCO / 2
        pagtext = self.font.render(str(pagina), 1, PRETO)
        pagrect = pagtext.get_rect(centerx=centerx, centery=centery)
        self.screen.blit(pagtext, pagrect)

    def imprimir_bloco(self, x, y, cor):
        rect = pygame.Rect(x, self.scroll + y, LARGURA_BLOCO, ALTURA_BLOCO)
        pygame.draw.rect(self.screen, cor, rect, 0)
        pygame.draw.rect(self.screen, AZUL, rect, 1)

    def imprimir_bloco_de_pagina(self, pagina, x, y, alteracao=True):
        cor = BRANCO if pagina == None else calcular_cor(pagina.processo.identificador, len(self.simulador.processos))
        self.imprimir_bloco(x, y, cor)
        if not pagina == None:
            self.imprimir_pagina(pagina, x, y)
            if alteracao and self.tp[pagina].modificado:
                xi = x + MODIFICADO + 1
                yi = y + self.scroll + 1
                tx = x + LARGURA_BLOCO - 1
                ty = y + self.scroll + ALTURA_BLOCO - 1
                xf = x + LARGURA_BLOCO - 1
                yf = y + self.scroll + 1
                pointlist = [(xi, yi), (tx, ty), (xf, yf)]
                pygame.draw.polygon(self.screen, BRANCO, pointlist)
                rect = pygame.Rect(x, yi - 1, LARGURA_BLOCO, ALTURA_BLOCO)
                pygame.draw.rect(self.screen, AZUL, rect, 1)

    def imprimir_entrada_tp(self, entrada, x, y, cor):
        rectp = pygame.Rect(x, self.scroll + y, ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rectp, 1)
        text = self.font.render(str(entrada.presente), 1, BRANCO)
        textrect = text.get_rect(center=rectp.center)
        self.screen.blit(text, textrect)

        rectm = pygame.Rect(x + ESPACO_BIT, self.scroll + y, ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rectm, 1)
        text = self.font.render(str(entrada.modificado), 1, BRANCO)
        textrect = text.get_rect(center=rectm.center)
        self.screen.blit(text, textrect)

        rect = pygame.Rect(x + 2 * ESPACO_BIT, self.scroll + y, LARGURA_ENTRADA_TP - 2 * ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rect, 1)
        text = self.font.render(str(entrada.quadro), 1, BRANCO)
        textrect = text.get_rect(center=rect.center)
        self.screen.blit(text, textrect)

    def imprimir_numero(self, y, num):
        centerx = MP_TEXT_X
        centery = self.scroll + y + ALTURA_BLOCO / 2
        quadtext = self.font.render(str(num), 1, BRANCO)
        quadrect = quadtext.get_rect(centerx=centerx, centery=centery)
        self.screen.blit(quadtext, quadrect)

    def imprimir_MP(self):
        text = self.font.render(u"Memória principal", 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_MP + LARGURA_BLOCO / 2, centery=self.scroll + ALTURA_BLOCO / 2)
        self.screen.blit(text, textrect)
        y = ALTURA_BLOCO
        for i, pagina in enumerate(self.quadros):
            self.imprimir_bloco_de_pagina(pagina, POSICAO_MP, y)
            self.imprimir_numero(y, i)
            y += ALTURA_BLOCO
        return y + ALTURA_BLOCO

    def imprimir_MS(self):
        text = self.font.render(u"Memória secundária", 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_MS + LARGURA_BLOCO / 2, centery=self.scroll + ALTURA_BLOCO / 2)
        self.screen.blit(text, textrect)
        y = ALTURA_BLOCO
        for i, processo in self.simulador.processos.items():
            inicio = y
            for j, pagina in enumerate(processo.paginas):
                self.imprimir_bloco_de_pagina(pagina, POSICAO_MS, y, alteracao=False)
                y += ALTURA_BLOCO
            button = Button(POSICAO_MS, inicio, LARGURA_BLOCO, y - inicio, partial(self._set_processo_selecionado, processo))
            self.buttons.append(button)
        return y + ALTURA_BLOCO

    def imprimir_TP(self, processo):
        y = ALTURA_ENTRADA_TP / 2
        cor = calcular_cor(processo.identificador, len(self.simulador.processos))
        gerenciador = self.simulador.gerenciador_memoria

        text = self.font.render(u"Tabela de páginas de P" + str(processo.identificador), 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2, centery=self.scroll + y)
        self.screen.blit(text, textrect)
        y += ALTURA_ENTRADA_TP / 2
        self.imprimir_entrada_tp(EntradaTP("P", "M", "Quadro"), POSICAO_TP, y, cor)
        y += ALTURA_ENTRADA_TP
        for i, entrada in enumerate(processo.tabela_paginas):
            self.imprimir_entrada_tp(entrada, POSICAO_TP, y, cor)
            y += ALTURA_ENTRADA_TP

        y += ALTURA_ENTRADA_TP

        if type(gerenciador) == LRUGlobal:
            referencias = ' '.join([str(q) for q in gerenciador.referencias])
            text = self.font.render(u"Referencias - quadros: " + referencias, 1, BRANCO)
            textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2, centery=self.scroll + y)
            self.screen.blit(text, textrect)
            y += 20

        if type(gerenciador) == LRULocalFixo:
            referencias = ' '.join([str(q) for q in processo.referencias])
            text = self.font.render(u"Referencias - quadros: " + referencias, 1, BRANCO)
            textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2, centery=self.scroll + y)
            self.screen.blit(text, textrect)
            y += 20

        if type(gerenciador) == LRULocalFixo:
            referencias = ' '.join([str(p.identificador) for p in gerenciador.processos_na_mp])
            text = self.font.render(u"Referencias - processos: " + referencias, 1, BRANCO)
            textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2, centery=self.scroll + y)
            self.screen.blit(text, textrect)
            y += 20

        return y

    def imprimir_mensagem(self):
        if len(self.simulador.mudancas):
            text = self.font.render(unicode(self.passo) + u'- ' + unicode(self.simulador.mudancas[0]), 1, BRANCO)
            textrect = text.get_rect(x=12, centery=ALTURA_INSTRUCAO)
            self.screen.blit(text, textrect)

        rect = pygame.Rect(0, HEIGHT - TAMANHO_MENSAGEM, WIDTH, TAMANHO_MENSAGEM)
        pygame.draw.rect(self.screen, BRANCO, rect, 0)

        posicao = HEIGHT - TAMANHO_MENSAGEM
        mudancas = self.simulador.mudancas[self.estado:self.estado + 4]
        if len(mudancas) < 4 and len(self.simulador.mudancas) >= 4:
            mudancas = self.simulador.mudancas[len(self.simulador.mudancas) - 4:]
        elif len(mudancas) < 4:
            mudancas = self.simulador.mudancas
        for mudanca in mudancas:
            posicao += 12
            text = self.font.render(unicode(mudanca), 1, PRETO)
            textrect = text.get_rect(x=12, centery=posicao)
            self.screen.blit(text, textrect)

    def posicao_de_pagina_na_MP(self, pagina, quadros):
        y = ALTURA_BLOCO
        for i, p in enumerate(quadros):
            if p == pagina:
                return (POSICAO_MP, y)
            y += ALTURA_BLOCO
        return (None, None)

    def posicao_de_pagina_na_MS(self, pagina):
        y = ALTURA_BLOCO
        for i, processo in self.simulador.processos.items():
            for j, p in enumerate(processo.paginas):
                if p == pagina:
                    return (POSICAO_MS, y)
                y += ALTURA_BLOCO
        return (None, None)

    def animacao(self):
        if (self.movimento):
            self.movimento.move(self.tempo, TEMPO_ANIMACAO)
            self.movimento.animar(self)

    def _set_processo_selecionado(self, processo):
        self.processo_selecionado = processo

    def eventos(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_UP:
                    self.scroll_pressionado = 1
                if event.key == K_DOWN:
                    self.scroll_pressionado = -1
            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.passo += 1
                    self.simulador.next()
                    self.processo_selecionado = self.simulador.gerenciador_memoria.processo_acessado
                    self.estado = 0
                self.scroll_pressionado = 0

            elif event.type == MOUSEBUTTONDOWN:
                clique = list(pygame.mouse.get_pos())
                clique[1] = clique[1] - self.scroll
                buttons = [button for button in self.buttons if clique in button]
                if buttons:
                    self.clique = buttons
                else:
                    self.clique = tuple(clique)
            elif event.type == MOUSEBUTTONUP:
                clique = list(pygame.mouse.get_pos())
                clique[1] = clique[1] - self.scroll
                if isinstance(self.clique, list):
                    [button.function() for button in self.clique if clique in button]
                self.clique = []

    def update(self):
        self.tempo += 1
        if self.tempo >= TEMPO_ANIMACAO and self.estado < len(self.simulador.mudancas):
            self.estado += 1
        self.buttons = []
        self.scroll += self.scroll_pressionado * self.velocidade_scroll
        if isinstance(self.clique, tuple):
            clique = list(pygame.mouse.get_pos())
            clique[1] = clique[1] - self.scroll

            self.scroll += clique[1] - self.clique[1]

        if self.scroll <= self.final_MP:
            self.scroll = self.final_MP
            self.scroll_pressionado = 0

        if self.scroll >= ALTURA_BLOCO:
            self.scroll = ALTURA_BLOCO
            self.scroll_pressionado = 0

    def imprimir(self):
        self.imprimir_MP()
        self.imprimir_MS()
        self.imprimir_TP(self.processo_selecionado)

    def game_loop(self):
        while 1:
            self.clock.tick(60)
            self.eventos()
            self.update()
            self.screen.fill(PRETO)
            self.imprimir()
            self.animacao()
            self.imprimir_mensagem()
            # text = self.font.render(unicode(self.passo) + ' ' + unicode(self.estado) + ' ' + unicode(self.tempo) + unicode(self.mensagem), 1, BRANCO)
            # textrect = text.get_rect(center=(300, 300))
            # self.screen.blit(text, textrect)
            pygame.display.flip()
