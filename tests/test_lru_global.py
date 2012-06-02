import unittest
from collections import deque
from base.simulador import Simulador
from base.mensagem import CarregadaMensagem, ModificadaMensagem
from base.mensagem import QuadroAcessadoMensagem
from gerenciadores.lru_global import LRUGlobal


class TestLRUGlobal(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 4 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(gerenciador_memoria=LRUGlobal, **tamanhos)

    def test_desalocar_quadro(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        gm.desalocar_quadro(0)
        self.assertEqual(deque(), gm.referencias)

    def test_acessa_pagina_que_nao_esta_na_mp(self):
        simulador = self.simulador
        simulador.linhas = ["P0 R (0)2"]
        simulador.next()
        quadro_0 = simulador.quadros[0]
        p0_pag0 = simulador.processos[0].paginas[0]
        self.assertEquals(quadro_0, p0_pag0)
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)
        self.assertEquals(0, p0_pag0.entrada_tp.quadro)
        self.assertEquals(1, p0_pag0.entrada_tp.presente)

    def test_acessa_pagina_que_esta_na_mp(self):
        simulador = self.simulador
        p0_pag0 = simulador.processos[0].paginas[0]
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.linhas = ["P0 R (0)2"]
        simulador.next()
        p0_pag0 = simulador.processos[0].paginas[0]
        self.assertIn(QuadroAcessadoMensagem(p0_pag0), simulador.mudancas)

    def test_acessa_pagina_fora_da_mp_com_mp_cheia_deque_na_ordem(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        processo = simulador.processos[0]
        p0_pag0 = processo.paginas[0]
        p0_pag1 = processo.paginas[1]
        p0_pag2 = processo.paginas[2]
        p0_pag3 = processo.paginas[3]
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        simulador.linhas = ["P0 R (6500)2"]
        simulador.next()
        p0_pag6 = simulador.processos[0].paginas[6]
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertEqual(deque([1, 2, 3, 0]), gm.referencias)

    def test_acessa_pagina_fora_da_mp_com_mp_cheia_deque_fora_de_ordem(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        p0_pag1 = simulador.processos[0].paginas[1]
        p0_pag2 = simulador.processos[0].paginas[2]
        p0_pag3 = simulador.processos[0].paginas[3]
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        gm.referencias = deque([2, 0, 1, 3])
        simulador.linhas = ["P0 R (6500)2"]
        simulador.next()
        p0_pag6 = simulador.processos[0].paginas[6]
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertEqual(deque([0, 1, 3, 2]), gm.referencias)

    def test_retira_pagina_modificada(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        p0_pag1 = simulador.processos[0].paginas[1]
        p0_pag2 = simulador.processos[0].paginas[2]
        p0_pag3 = simulador.processos[0].paginas[3]
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        p0_pag0.entrada_tp.modificado = 1
        gm.referencias = deque([0, 1, 2, 3])
        simulador.linhas = ["P0 R (6500)2"]
        simulador.next()
        p0_pag6 = simulador.processos[0].paginas[6]
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertIn(ModificadaMensagem(p0_pag0), simulador.mudancas)
        self.assertEqual(deque([1, 2, 3, 0]), gm.referencias)
