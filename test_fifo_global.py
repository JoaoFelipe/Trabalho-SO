import unittest
from simulador import Simulador
from fifo_global import FifoGlobal
from mensagem import CarregadaMensagem, PresenteMensagem, ModificadaMensagem


class TestFifoGlobal(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 4 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(gerenciador_memoria=FifoGlobal, **tamanhos)

    def _p0_pagx(self, x):
        processo_0 = self.simulador.processos[0]
        return processo_0.paginas[x]

    def _qx_p0_pagx(self, x):
        quadro_x = self.simulador.quadros[x]
        p0_pagx = self._p0_pagx(0)
        return quadro_x, p0_pagx

    def test_acessa_pagina_que_nao_esta_na_mp(self):
        simulador = self.simulador
        simulador.linhas = ["P0 R (0)2"]
        simulador.next()
        quadro_0, p0_pag0 = self._qx_p0_pagx(0)
        self.assertEquals(quadro_0, p0_pag0)
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)
        self.assertEquals(0, p0_pag0.entrada_tp.quadro)
        self.assertEquals(1, p0_pag0.entrada_tp.presente)

    def test_acessa_pagina_que_esta_na_mp(self):
        simulador = self.simulador
        quadro_0, p0_pag0 = self._qx_p0_pagx(0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.linhas = ["P0 R (0)2"]
        simulador.next()
        quadro_0, p0_pag0 = self._qx_p0_pagx(0)
        self.assertIn(PresenteMensagem(p0_pag0), simulador.mudancas)

    def test_acessa_pagina_fora_da_mp_com_mp_cheia_ponteiro_inicio(self):
        simulador = self.simulador
        _, p0_pag0 = self._qx_p0_pagx(0)
        _, p0_pag1 = self._qx_p0_pagx(1)
        _, p0_pag2 = self._qx_p0_pagx(2)
        _, p0_pag3 = self._qx_p0_pagx(3)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        simulador.linhas = ["P0 R (6500)2"]
        simulador.next()
        p0_pag6 = self._p0_pagx(6)
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertEqual(1, simulador.gerenciador_memoria.ponteiro)

    def test_acessa_pagina_fora_da_mp_com_mp_cheia_ponteiro_final(self):
        simulador = self.simulador
        _, p0_pag0 = self._qx_p0_pagx(0)
        _, p0_pag1 = self._qx_p0_pagx(1)
        _, p0_pag2 = self._qx_p0_pagx(2)
        _, p0_pag3 = self._qx_p0_pagx(3)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        simulador.linhas = ["P0 R (6500)2"]
        simulador.gerenciador_memoria.ponteiro = 3
        simulador.next()
        p0_pag6 = self._p0_pagx(6)
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertEqual(0, simulador.gerenciador_memoria.ponteiro)

    def test_retira_pagina_modificada(self):
        simulador = self.simulador
        _, p0_pag0 = self._qx_p0_pagx(0)
        _, p0_pag1 = self._qx_p0_pagx(1)
        _, p0_pag2 = self._qx_p0_pagx(2)
        _, p0_pag3 = self._qx_p0_pagx(3)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(0, p0_pag0)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(1, p0_pag1)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(2, p0_pag2)
        simulador.gerenciador_memoria.alocar_pagina_no_quadro(3, p0_pag3)
        p0_pag0.entrada_tp.modificado = 1
        simulador.linhas = ["P0 R (6500)2"]
        simulador.next()
        p0_pag6 = self._p0_pagx(6)
        self.assertIn(CarregadaMensagem(p0_pag6), simulador.mudancas)
        self.assertIn(ModificadaMensagem(p0_pag0), simulador.mudancas)
