import unittest
from simulador import Simulador
from fifo_local_variavel import FifoLocalVariavel
from mensagem import CarregadaMensagem, PresenteMensagem


class TestFifoLocalVariavel(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 10 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 4000, 9000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(
            gerenciador_memoria=FifoLocalVariavel,
            **tamanhos
        )

    def test_fora_verificacao_acessa_pagina_que_esta_na_mp(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0 = p0.paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.linhas = ["P0 R (0)2"]
        self.assertEqual(0, p0.acessos)
        self.assertEqual(0, p0.falhas)
        simulador.next()
        self.assertIn(PresenteMensagem(p0_pag0), simulador.mudancas)
        self.assertEqual(1, p0.acessos)
        self.assertEqual(0, p0.falhas)
        self.assertEqual(0, p0.ratio())

    def test_durante_verificacao_pagina_que_esta_na_mp_eq(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0 = p0.paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.linhas = ["P0 R (0)2"]
        p0.acessos = 3
        p0.falhas = 2
        simulador.next()
        self.assertIn(PresenteMensagem(p0_pag0), simulador.mudancas)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(2, p0.falhas)
        self.assertEqual(0.5, p0.ratio())

    def test_durante_verificacao_pagina_que_esta_na_mp_lt_falha(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0.maximo_quadros = 2
        p0_pag0, p0_pag1 = p0.paginas[:2]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (0)2"]
        p0.acessos = 3
        p0.falhas = 0
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)
        self.assertEqual(1, p0.maximo_quadros)
        self.assertEqual(1, len(p0.conjunto_residente))
        self.assertEqual([1], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(0, p0.falhas)
        self.assertEqual(0, p0.ratio())

    def test_durante_verificacao_pagina_que_esta_na_mp_lt_ok(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0.maximo_quadros = 2
        p0_pag0, p0_pag1 = p0.paginas[:2]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (0)2"]
        p0.acessos = 3
        p0.falhas = 0
        p0.ponteiro = 1
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual(1, p0.maximo_quadros)
        self.assertEqual(1, len(p0.conjunto_residente))
        self.assertEqual([0], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(0, p0.falhas)
        self.assertEqual(0, p0.ratio())

    def test_durante_verificacao_pagina_que_esta_na_mp_gt(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0.maximo_quadros = 2
        p0_pag0, p0_pag1, p0_pag2 = p0.paginas[:3]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (0)2"]
        p0.acessos = 3
        p0.falhas = 3
        p0.ponteiro = 1
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual(p0_pag2, simulador.quadros[2])
        self.assertEqual(3, p0.maximo_quadros)
        self.assertEqual(3, len(p0.conjunto_residente))
        self.assertEqual([0, 1, 2], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(3, p0.falhas)
        self.assertEqual(0.75, p0.ratio())

    def test_fora_verificacao_acessa_pagina_fora_da_mp_processo_na_mp(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = p0.paginas[:3]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (2049)2"]
        self.assertEqual(0, p0.acessos)
        self.assertEqual(0, p0.falhas)
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual([0, 1], p0.conjunto_residente)
        self.assertEqual(1, p0.acessos)
        self.assertEqual(1, p0.falhas)
        self.assertEqual(1, p0.ratio())
        quadro_0 = simulador.quadros[0]
        self.assertEquals(quadro_0, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertEqual(0, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(1, p0.ponteiro)

    def test_dentro_verificacao_pagina_fora_da_mp_processo_na_mp_eq(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = p0.paginas[:3]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (2049)2"]
        p0.acessos = 3
        p0.falhas = 1
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual([0, 1], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(2, p0.falhas)
        self.assertEqual(0.5, p0.ratio())
        quadro_0 = simulador.quadros[0]
        self.assertEquals(quadro_0, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertEqual(0, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(1, p0.ponteiro)

    def test_dentro_verificacao_pagina_fora_da_mp_processo_na_mp_lt(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = p0.paginas[:3]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (2049)2"]
        p0.acessos = 3
        p0.falhas = 0
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual([1], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(1, p0.falhas)
        self.assertEqual(0.25, p0.ratio())
        quadro_1 = simulador.quadros[1]
        self.assertEquals(quadro_1, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertEqual(1, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(0, p0.ponteiro)

    def test_dentro_verificacao_pagina_fora_da_mp_processo_na_mp_gt(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = p0.paginas[:3]
        gm.alocar_n_paginas(p0, 0, 2, [])
        simulador.linhas = ["P0 R (2049)2"]
        p0.acessos = 3
        p0.falhas = 3
        self.assertEqual([0, 1], p0.conjunto_residente)
        simulador.next()
        self.assertEqual([0, 1, 2], p0.conjunto_residente)
        self.assertEqual(4, p0.acessos)
        self.assertEqual(4, p0.falhas)
        self.assertEqual(1, p0.ratio())
        quadro_2 = simulador.quadros[2]
        self.assertEquals(quadro_2, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertEqual(2, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(0, p0.ponteiro)

    def test_fora_verificacao_acessa_pagina_de_processo_suspenso(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0, p1, p2 = simulador.processos[:3]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p1_pag0 = p1.paginas[0]
        p2_pag0, p2_pag1, p2_pag2 = p2.paginas[:3]
        p0.maximo_quadros = 2
        p1.maximo_quadros = 1
        p2.maximo_quadros = 3
        gm.alocar_pagina_no_quadro(2, p1_pag0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.linhas = ["P2 R (2049)2"]
        self.assertEqual(0, p2.acessos)
        self.assertEqual(0, p2.falhas)
        simulador.next()
        self.assertEqual(1, p2.acessos)
        self.assertEqual(1, p2.falhas)
        self.assertEqual(1, p2.ratio())
        carregadas = [p2_pag2, p2_pag1, p2_pag0]
        self.assertEquals(carregadas + [None], simulador.quadros)
        for pag in carregadas:
            self.assertIn(CarregadaMensagem(pag), simulador.mudancas)
        self.assertEqual([0, 1, 2], p2.conjunto_residente)
        self.assertEqual([], p1.conjunto_residente)
        self.assertEqual([], p0.conjunto_residente)
        self.assertEqual(0, p2.ponteiro)

    def test_dentro_verificacao_acessa_pagina_de_processo_suspenso_eq(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0, p1, p2 = simulador.processos[:3]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p1_pag0 = p1.paginas[0]
        p2_pag0, p2_pag1, p2_pag2 = p2.paginas[:3]
        p0.maximo_quadros = 2
        p1.maximo_quadros = 1
        p2.maximo_quadros = 3
        gm.alocar_pagina_no_quadro(2, p1_pag0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.linhas = ["P2 R (2049)2"]
        p2.acessos = 3
        p2.falhas = 1
        simulador.next()
        self.assertEqual(4, p2.acessos)
        self.assertEqual(2, p2.falhas)
        self.assertEqual(0.5, p2.ratio())
        carregadas = [p2_pag2, p2_pag1, p2_pag0]
        self.assertEquals(carregadas + [None], simulador.quadros)
        for pag in carregadas:
            self.assertIn(CarregadaMensagem(pag), simulador.mudancas)
        self.assertEqual([0, 1, 2], p2.conjunto_residente)
        self.assertEqual([], p1.conjunto_residente)
        self.assertEqual([], p0.conjunto_residente)
        self.assertEqual(0, p2.ponteiro)

    def test_dentro_verificacao_acessa_pagina_de_processo_suspenso_lt(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0, p1, p2, p3 = simulador.processos[:4]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p1_pag0 = p1.paginas[0]
        p3_pag0, p3_pag1, p3_pag2, p3_pag3 = p3.paginas[:4]
        p0.maximo_quadros = 2
        p1.maximo_quadros = 1
        p3.maximo_quadros = 3
        gm.alocar_pagina_no_quadro(2, p1_pag0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.linhas = ["P3 R (2049)2"]
        p3.acessos = 3
        p3.falhas = 0
        simulador.next()
        self.assertEqual(4, p3.acessos)
        self.assertEqual(1, p3.falhas)
        self.assertEqual(0.25, p3.ratio())
        carregadas = [p3_pag2, p3_pag3]
        self.assertEquals([p0_pag0, p0_pag1] + carregadas, simulador.quadros)
        for pag in carregadas:
            self.assertIn(CarregadaMensagem(pag), simulador.mudancas)
        self.assertEqual([2, 3], p3.conjunto_residente)
        self.assertEqual([], p1.conjunto_residente)
        self.assertEqual([0, 1], p0.conjunto_residente)
        self.assertEqual(0, p3.ponteiro)

    def test_dentro_verificacao_acessa_pagina_de_processo_suspenso_gt(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0, p1, p2, p3 = simulador.processos[:4]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p1_pag0 = p1.paginas[0]
        p3_pag0, p3_pag1, p3_pag2, p3_pag3 = p3.paginas[:4]
        p0.maximo_quadros = 2
        p1.maximo_quadros = 1
        p3.maximo_quadros = 3
        gm.alocar_pagina_no_quadro(2, p1_pag0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.linhas = ["P3 R (2049)2"]
        p3.acessos = 3
        p3.falhas = 3
        simulador.next()
        self.assertEqual(4, p3.acessos)
        self.assertEqual(4, p3.falhas)
        self.assertEqual(1, p3.ratio())
        carregadas = [p3_pag2, p3_pag3, p3_pag1, p3_pag0]
        self.assertEquals(carregadas, simulador.quadros)
        for pag in carregadas:
            self.assertIn(CarregadaMensagem(pag), simulador.mudancas)
        self.assertEqual([0, 1, 2, 3], p3.conjunto_residente)
        self.assertEqual([], p1.conjunto_residente)
        self.assertEqual([], p0.conjunto_residente)
        self.assertEqual(0, p3.ponteiro)
