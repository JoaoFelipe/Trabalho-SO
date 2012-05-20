# -*- coding: utf-8 -*-
import os, sys, pygame
from pygame.locals import *
from simulador import Simulador
from processo import EntradaTP
from collections import namedtuple
from functools import partial

PRETO = 0, 0, 0
BRANCO = 255, 255, 255
AZUL = 0, 0, 255

DIMENSOES = WIDTH, HEIGHT = 800, 600
TITULO = 'Simulador'

ALTURA_BLOCO = int(0.05 * HEIGHT)
LARGURA_BLOCO = int(0.175 * WIDTH)

ALTURA_ENTRADA_TP = int(0.05 * HEIGHT)
LARGURA_ENTRADA_TP = int(0.3 * WIDTH)

ESPACO_BIT = ALTURA_ENTRADA_TP


MP_TEXT_X = int(0.025 * WIDTH)
POSICAO_MP = int(0.05 * WIDTH)
POSICAO_MS = int(0.775 * WIDTH)
POSICAO_TP = int(0.35 * WIDTH)

TAMANHO_MENSAGEM = int(0.1 * HEIGHT)

class Button(namedtuple('Button', ['x', 'y', 'width', 'height', 'function'])):

    def __contains__(self, clique):
        return self.x <= clique[0] <= self.x+self.width and self.y <= clique[1] <= self.y+self.height 



def calcular_cor(num, processos):
    #tamanho = (255*(256**2) + 255*256 + 255) / (len(processos)+2)
    #cor = tamanho*(num+1)
    #corb = bin(cor)[2:]
    to_bin = lambda x: bin(x)[2:]

    cor = list(to_bin(int('FFFFFF', 16)))
    
    index = 0
    numb = to_bin(num)
    numb = "0"*(len(to_bin(processos)) - len(numb)) + numb
    for l in numb:
        cor[index] = str(int(cor[index] == l))
        index = index + 8
        if index >= 24:
            index -= 23
            if index >= 8:
                index -= 8
        
    corb = ''.join(cor)        
    return (int(corb[0:8],2), int(corb[8:16],2), int(corb[16:24],2))



class PygameInterface(object):

    def __init__(self,simulador):
        if not pygame.font: print 'Fontes desabilitadas'
        pygame.init()
        self.width, self.height = DIMENSOES 
        self.screen = pygame.display.set_mode(DIMENSOES)
        pygame.display.set_caption('Titulo')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.scroll = ALTURA_BLOCO
        self.buttons = []
        self.clique = []

        self.simulador = simulador
        
        self.processo_selecionado = self.simulador.processos[0]
        self.final_MP = -max(self.imprimir_MP(), self.imprimir_MS()) + self.height    
        self.final_TP = self.imprimir_TP(max(self.simulador.processos, key=lambda x:len(x.paginas)))

        self.velocidade_scroll = 10
        self.scroll_pressionado = 0

    
    def imprimir_pagina(self, pagina, x, y):
        centerx = x + LARGURA_BLOCO / 2
        centery = self.scroll + y + ALTURA_BLOCO / 2
        pagtext = self.font.render(str(pagina), 1, PRETO)
        pagrect = pagtext.get_rect(centerx=centerx, centery=centery)
        self.screen.blit(pagtext, pagrect)
        
    def imprimir_bloco(self, x, y, cor):
        rect = pygame.Rect(x, self.scroll+y, LARGURA_BLOCO, ALTURA_BLOCO)
        pygame.draw.rect(self.screen, cor, rect, 0)     
        pygame.draw.rect(self.screen, AZUL, rect, 1)
        
    def imprimir_entrada_tp(self, entrada, x, y, cor):
        rectp = pygame.Rect(x, self.scroll+y, ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rectp, 1)    
        text = self.font.render(str(entrada.presente), 1, BRANCO)
        textrect = text.get_rect(center=rectp.center)
        self.screen.blit(text, textrect)
        
        rectm = pygame.Rect(x+ESPACO_BIT, self.scroll+y, ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rectm, 1)
        text = self.font.render(str(entrada.modificado), 1, BRANCO)
        textrect = text.get_rect(center=rectm.center)
        self.screen.blit(text, textrect)
        
        rect = pygame.Rect(x+2*ESPACO_BIT, self.scroll+y, LARGURA_ENTRADA_TP-2*ESPACO_BIT, ALTURA_ENTRADA_TP)
        pygame.draw.rect(self.screen, cor, rect, 1)
        text = self.font.render(str(entrada.quadro), 1, BRANCO)
        textrect = text.get_rect(center=rect.center)
        self.screen.blit(text, textrect)     
        #pygame.draw.rect(self.screen, AZUL, rect, 1)    
        
    def imprimir_numero(self, y, num):
        centerx = MP_TEXT_X
        centery = self.scroll + y + ALTURA_BLOCO / 2
        quadtext = self.font.render(str(num), 1, BRANCO)
        quadrect = quadtext.get_rect(centerx=centerx, centery=centery)
        self.screen.blit(quadtext, quadrect)
    
    def imprimir_MP(self):    
        text = self.font.render(u"Memória principal", 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_MP + LARGURA_BLOCO / 2,centery=self.scroll + ALTURA_BLOCO / 2)
        self.screen.blit(text, textrect)
        y = ALTURA_BLOCO
        for i,pagina in enumerate(self.simulador.quadros):
            cor = BRANCO if pagina == None else calcular_cor(pagina.processo.identificador, len(self.simulador.processos))
            self.imprimir_bloco(POSICAO_MP, y, cor)
            if not pagina == None:
                self.imprimir_pagina(pagina, POSICAO_MP, y)            
            self.imprimir_numero(y, i)
            y += ALTURA_BLOCO
        return y + ALTURA_BLOCO

    def imprimir_MS(self):    
        text = self.font.render(u"Memória secundária", 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_MS + LARGURA_BLOCO / 2,centery=self.scroll + ALTURA_BLOCO / 2)
        self.screen.blit(text, textrect)
        y = ALTURA_BLOCO
        for i, processo in enumerate(self.simulador.processos):
            inicio = y
            cor = calcular_cor(processo.identificador, len(self.simulador.processos)) 
            for j, pagina in enumerate(processo.paginas):
                self.imprimir_bloco(POSICAO_MS, y, cor)
                self.imprimir_pagina(pagina, POSICAO_MS, y)            
                y += ALTURA_BLOCO
               
            button = Button(POSICAO_MS, inicio, LARGURA_BLOCO, y-inicio, partial(self._set_processo_selecionado, processo))
            self.buttons.append(button)
        return y + ALTURA_BLOCO

    def imprimir_TP(self, processo):    
        text = self.font.render(u"Tabela de páginas de P"+str(processo.identificador), 1, BRANCO)
        textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2,centery=self.scroll + ALTURA_ENTRADA_TP / 2)
        self.screen.blit(text, textrect)
        y = ALTURA_ENTRADA_TP
        cor = calcular_cor(processo.identificador, len(self.simulador.processos)) 
        self.imprimir_entrada_tp(EntradaTP("P", "M", "Quadro"), POSICAO_TP, y, cor)
        y += ALTURA_ENTRADA_TP
        for i, entrada in enumerate(processo.tabela_paginas):
            self.imprimir_entrada_tp(entrada, POSICAO_TP, y, cor)
            y += ALTURA_ENTRADA_TP
        return y + ALTURA_ENTRADA_TP

    def imprimir_mensagem(self):
        rect = pygame.Rect(0, HEIGHT-TAMANHO_MENSAGEM, WIDTH, TAMANHO_MENSAGEM)
        pygame.draw.rect(self.screen, BRANCO, rect, 0)
            
        posicao = HEIGHT-TAMANHO_MENSAGEM + 5
        for mudanca in self.simulador.mudancas:
            posicao += 12
            text = self.font.render(unicode(mudanca), 1, PRETO)
            textrect = text.get_rect(x=12,centery=posicao)
            self.screen.blit(text, textrect)

#        posicao += 12
#        for i, linha in enumerate(self.simulador.linhas):
#            posicao += 12
#            text = self.font.render(linha + ('*' if self.simulador.ponteiro == i else ''), 1, BRANCO)
#            textrect = text.get_rect(centerx=POSICAO_TP + LARGURA_ENTRADA_TP / 2,centery=self.scroll + self.final_TP + ALTURA_ENTRADA_TP / 2 + posicao)
#            self.screen.blit(text, textrect)
        



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
                    self.simulador.next()
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
        self.imprimir_mensagem()

    def game_loop(self):
        while 1:
            self.clock.tick(60)
            self.eventos()       
            self.update()
            self.screen.fill(PRETO)
            self.imprimir()
            pygame.display.flip()
    
        

