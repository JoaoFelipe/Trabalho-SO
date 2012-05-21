import unittest
from simulador import Simulador
from fifo_local_fixo import FifoLocalFixo
from mensagem import CarregadaMensagem, PresenteMensagem, ModificadaMensagem


class TestFifoLocalFixo(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 10 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 8000, 9000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(gerenciador_memoria=FifoLocalFixo, **tamanhos)

    def test_acessa_pagina_que_esta_na_mp(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.linhas = ["P0 R (0)2"]
        simulador.next()
        self.assertIn(PresenteMensagem(p0_pag0), simulador.mudancas)

    def test_acessa_pagina_que_nao_esta_na_mp_de_processo_que_esta_na_mp_ponteiro_0(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        processo = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = simulador.processos[0].paginas[:3]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.linhas = ["P0 R (2049)2"]
        simulador.next()
        quadro_0 = simulador.quadros[0]
        self.assertEquals(quadro_0, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertEqual(0, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(1, processo.ponteiro)

    def test_acessa_pagina_que_nao_esta_na_mp_de_processo_que_esta_na_mp_ponteiro_1_max_quadros_1(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        processo = simulador.processos[0]
        p0_pag0, p0_pag1, p0_pag2 = simulador.processos[0].paginas[:3]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        processo.ponteiro = 1
        p0_pag1.entrada_tp.modificado = 1
        simulador.linhas = ["P0 R (2049)2"]
        simulador.next()
        quadro_1 = simulador.quadros[1]
        self.assertEquals(quadro_1, p0_pag2)
        self.assertIn(CarregadaMensagem(p0_pag2), simulador.mudancas)
        self.assertIn(ModificadaMensagem(p0_pag1), simulador.mudancas)
        self.assertEqual(1, p0_pag2.entrada_tp.quadro)
        self.assertEqual(1, p0_pag2.entrada_tp.presente)
        self.assertEqual(0, processo.ponteiro)

    def test_acessa_pagina_de_processo_suspenso(self):
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
        simulador.next()
        carregadas = [p2_pag2, p2_pag1, p2_pag0]
        self.assertEquals(carregadas + [None], simulador.quadros)
        for pag in carregadas:
            self.assertIn(CarregadaMensagem(pag), simulador.mudancas)
        self.assertEqual([0, 1, 2], p2.conjunto_residente)
        self.assertEqual([], p1.conjunto_residente)
        self.assertEqual([], p0.conjunto_residente)
        self.assertEqual(0, p2.ponteiro)
