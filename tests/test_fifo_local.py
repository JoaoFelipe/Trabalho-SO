import unittest
from base.simulador import Simulador
from gerenciadores.fifo_local import FifoLocal


class TestFifoLocal(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 8 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [7000, 2000, 3000, 8000, 9000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(gerenciador_memoria=FifoLocal, **tamanhos)

    def test_criar_processo(self):
        simulador = self.simulador
        simulador.linhas = ["P8 C (2000)2"]
        simulador.next()
        processo = simulador.processos.values()[-1]
        self.assertEqual(-1, processo.ponteiro)
        self.assertEqual([], processo.conjunto_residente)
        self.assertEqual(2, processo.maximo_quadros)

    def test_desalocar_quadro(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        processo = simulador.processos.values()[-1]
        pagina = processo.paginas[0]
        pagina1 = processo.paginas[1]
        pagina.entrada_tp.modificado = 1
        gm.alocar_pagina_no_quadro(0, pagina)
        gm.alocar_pagina_no_quadro(1, pagina1)
        self.assertEqual(0, processo.ponteiro)
        gm.desalocar_quadro(0)
        self.assertEqual(1, processo.ponteiro)

    def test_retira_pagina_fifo_ponteiro_0(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        gm.alocar_n_paginas(p0, 0, 4, [])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        quadro = gm.retira_pagina(p0)
        self.assertEqual(0, quadro)
        memoria = [
            None,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            None,
            None,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)
        self.assertEqual(1, p0.ponteiro)

    def test_retira_pagina_fifo_ponteiro_maximo(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        gm.alocar_n_paginas(p0, 0, 4, [])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        p0.maximo_quadros = 4
        p0.ponteiro = 3
        quadro = gm.retira_pagina(p0)
        self.assertEqual(3, quadro)
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            None,
            None,
            None,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)
        self.assertEqual(0, p0.ponteiro)

    def test_suspender_processo(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0, p1 = simulador.processos.values()[:2]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p1_pag0 = p1.paginas[0]
        p0.maximo_quadros = 2
        p1.maximo_quadros = 1
        gm.alocar_pagina_no_quadro(2, p1_pag0)
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        self.assertEqual([0, 1], p0.conjunto_residente)
        self.assertEqual(0, p0.ponteiro)
        self.assertEqual(2, len(gm.processos_na_mp))
        gm.suspender_processo(p0)
        self.assertEqual(1, len(gm.processos_na_mp))
        self.assertEqual([], p0.conjunto_residente)
        self.assertEqual(-1, p0.ponteiro)
        self.assertEquals([None, None, p1_pag0, None], simulador.quadros)

    def test_alocar_pagina_no_quadro(self):
        simulador = self.simulador
        simulador.quadros = [None] * 4
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        p0_pag0, p0_pag1 = p0.paginas[:2]
        p0.maximo_quadros = 2
        self.assertEqual(-1, p0.ponteiro)
        self.assertEqual(0, len(gm.processos_na_mp))
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        self.assertEqual(0, p0.ponteiro)
        self.assertEqual(1, len(gm.processos_na_mp))
        self.assertEqual([0], p0.conjunto_residente)
        gm.alocar_pagina_no_quadro(1, p0_pag1)
        self.assertEqual([0, 1], p0.conjunto_residente)
        self.assertEqual(0, p0.ponteiro)
        self.assertEqual(1, len(gm.processos_na_mp))
