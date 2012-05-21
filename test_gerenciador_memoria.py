import unittest
from simulador import Simulador
from mensagem import QuadroModificadoMensagem, CarregadaMensagem, ModificadaMensagem


class TestGerenciadorMemoria(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 4 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(**tamanhos)

    def _p0_pagx(self, x):
        processo_0 = self.simulador.processos[0]
        return processo_0.paginas[x]

    def test_acessar_com_modificao(self):
        simulador = self.simulador
        simulador.linhas = ["P0 W (0)2"]
        simulador.next()
        p0_pag0 = self._p0_pagx(0)
        self.assertIn(QuadroModificadoMensagem(p0_pag0), simulador.mudancas)
        self.assertEquals(1, p0_pag0.entrada_tp.modificado)

    def test_descobre_pagina(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        simulador.tamanho_endereco_logico = 7
        simulador.tamanho_pagina = 8  # offset = 3
        # tamanho identificador pagina = 4
        self.assertEqual(5, gm.descobre_pagina("0101000"))
        self.assertEqual(7, gm.descobre_pagina("0111000"))
        self.assertEqual(7, gm.descobre_pagina("0111011"))

    def test_alocar_pagina_no_quadro(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = self._p0_pagx(0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        self.assertEqual(0, p0_pag0.entrada_tp.quadro)
        self.assertEqual(1, p0_pag0.entrada_tp.presente)
        self.assertEqual(p0_pag0, simulador.quadros[0])
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)

    def test_desalocar_quadro_sem_modificacao(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = self._p0_pagx(0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.desalocar_quadro(0)
        self.assertEqual(0, p0_pag0.entrada_tp.presente)
        self.assertEqual(0, p0_pag0.entrada_tp.modificado)
        self.assertEqual(None, simulador.quadros[0])
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)

    def test_desalocar_quadro_com_modificacao(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = self._p0_pagx(0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        p0_pag0.entrada_tp.modificado = 1
        gm.desalocar_quadro(0)
        self.assertEqual(0, p0_pag0.entrada_tp.presente)
        self.assertEqual(0, p0_pag0.entrada_tp.modificado)
        self.assertEqual(None, simulador.quadros[0])
        self.assertIn(ModificadaMensagem(p0_pag0), simulador.mudancas)
