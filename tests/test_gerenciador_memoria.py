import unittest
from base.simulador import Simulador
from base.mensagem import QuadroModificadoMensagem, CarregadaMensagem, ModificadaMensagem


class TestGerenciadorMemoria(unittest.TestCase):

    def setUp(self):
        tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 8 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [8000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
        }

        self.simulador = Simulador(**tamanhos)

    def test_acessar_com_modificao(self):
        simulador = self.simulador
        simulador.linhas = ["P0 W (0)2"]
        simulador.next()
        p0_pag0 = simulador.processos[0].paginas[0]
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
        p0_pag0 = simulador.processos[0].paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        self.assertEqual(0, p0_pag0.entrada_tp.quadro)
        self.assertEqual(1, p0_pag0.entrada_tp.presente)
        self.assertEqual(p0_pag0, simulador.quadros[0])
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)

    def test_desalocar_quadro_sem_modificacao(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.desalocar_quadro(0)
        self.assertEqual(0, p0_pag0.entrada_tp.presente)
        self.assertEqual(0, p0_pag0.entrada_tp.modificado)
        self.assertEqual(None, simulador.quadros[0])
        self.assertIn(CarregadaMensagem(p0_pag0), simulador.mudancas)

    def test_desalocar_quadro_com_modificacao(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        p0_pag0.entrada_tp.modificado = 1
        gm.desalocar_quadro(0)
        self.assertEqual(0, p0_pag0.entrada_tp.presente)
        self.assertEqual(0, p0_pag0.entrada_tp.modificado)
        self.assertEqual(None, simulador.quadros[0])
        self.assertIn(ModificadaMensagem(p0_pag0), simulador.mudancas)

    def test_suspender_processo(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag0 = simulador.processos[0].paginas[0]
        p0_pag1 = simulador.processos[0].paginas[1]
        p0_pag2 = simulador.processos[0].paginas[2]
        p1_pag0 = simulador.processos[1].paginas[0]
        gm.alocar_pagina_no_quadro(0, p0_pag0)
        gm.alocar_pagina_no_quadro(1, p1_pag0)
        gm.alocar_pagina_no_quadro(2, p0_pag1)
        gm.alocar_pagina_no_quadro(3, p0_pag2)
        gm.suspender_processo(simulador.processos[0])
        self.assertEqual(None, simulador.quadros[0])
        self.assertEqual(p1_pag0, simulador.quadros[1])
        self.assertEqual(None, simulador.quadros[2])
        self.assertEqual(None, simulador.quadros[3])

    def test_alocar_paginas_por_localidade(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0_pag6 = simulador.processos[0].paginas[6]
        gm.alocar_pagina_no_quadro(2, p0_pag6)
        inicial = 5
        quantidade = 4
        processo = simulador.processos[0]
        quadros = gm.alocar_paginas_por_localidade(processo, inicial, quantidade)
        self.assertEqual([0, 1, 3, 4], quadros)
        p0_pag5 = simulador.processos[0].paginas[5]
        p0_pag7 = simulador.processos[0].paginas[7]
        p0_pag4 = simulador.processos[0].paginas[4]
        p0_pag3 = simulador.processos[0].paginas[3]
        self.assertEqual(p0_pag5, simulador.quadros[0])
        self.assertEqual(p0_pag7, simulador.quadros[1])
        self.assertEqual(p0_pag6, simulador.quadros[2])
        self.assertEqual(p0_pag4, simulador.quadros[3])
        self.assertEqual(p0_pag3, simulador.quadros[4])

    def test_alocar_paginas_por_localidade_maior_do_que_MP(self):
        simulador = self.simulador
        simulador.quadros = [None] * 3
        gm = simulador.gerenciador_memoria
        inicial = 5
        quantidade = 4
        processo = simulador.processos[0]
        quadros = gm.alocar_paginas_por_localidade(processo, inicial, quantidade)
        self.assertEqual([0, 1, 2], quadros)
        p0_pag5 = simulador.processos[0].paginas[5]
        p0_pag6 = simulador.processos[0].paginas[6]
        p0_pag7 = simulador.processos[0].paginas[7]
        self.assertEqual(p0_pag5, simulador.quadros[0])
        self.assertEqual(p0_pag6, simulador.quadros[1])
        self.assertEqual(p0_pag7, simulador.quadros[2])

    def test_alocar_paginas_por_localidade_maior_do_que_MP_disponivel(self):
        simulador = self.simulador
        simulador.quadros = [None] * 3
        gm = simulador.gerenciador_memoria
        p0_pag6 = simulador.processos[0].paginas[6]
        gm.alocar_pagina_no_quadro(2, p0_pag6)
        inicial = 5
        quantidade = 4
        processo = simulador.processos[0]
        quadros = gm.alocar_paginas_por_localidade(processo, inicial, quantidade)
        self.assertEqual([0, 1], quadros)
        p0_pag5 = simulador.processos[0].paginas[5]
        p0_pag7 = simulador.processos[0].paginas[7]
        p0_pag6 = simulador.processos[0].paginas[6]
        self.assertEqual(p0_pag5, simulador.quadros[0])
        self.assertEqual(p0_pag7, simulador.quadros[1])
        self.assertEqual(p0_pag6, simulador.quadros[2])

    def test_alocar_paginas_por_localidade_maior_do_que_tamanho_processo(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        inicial = 0
        quantidade = 4
        processo = simulador.processos[1]
        quadros = gm.alocar_paginas_por_localidade(processo, inicial, quantidade)
        self.assertEqual([0, 1], quadros)
        p1_pag0 = simulador.processos[1].paginas[0]
        p1_pag1 = simulador.processos[1].paginas[1]
        self.assertEqual(p1_pag0, simulador.quadros[0])
        self.assertEqual(p1_pag1, simulador.quadros[1])

    def test_alocar_n_paginas_vazio(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0 = simulador.processos[0]
        gm.alocar_n_paginas(p0, 0, 4, [])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            None,
            None,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)

    def test_alocar_n_paginas_com_ordem(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0, p1, p2 = simulador.processos[:3]
        gm.alocar_n_paginas(p0, 0, 4, [])
        gm.alocar_n_paginas(p1, 0, 2, [p0])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        p1_pag0, p1_pag1 = p1.paginas[:2]
        p2_pag0, p2_pag1, p2_pag2 = p2.paginas[:3]
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p1_pag0,
            p1_pag1,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)
        gm.alocar_n_paginas(p2, 0, 3, [p0, p1])
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p2_pag0,
            p2_pag1,
            p2_pag2,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)

    def test_alocar_n_paginas_com_ordem_sem_suspender_processo(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0, p1 = simulador.processos[:2]
        gm.alocar_n_paginas(p0, 0, 4, [])
        gm.alocar_n_paginas(p1, 0, 2, [p0])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        p0_pag5, p0_pag6, p0_pag7 = p0.paginas[5:8]
        p1_pag0, p1_pag1 = p1.paginas[:2]
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p1_pag0,
            p1_pag1,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)
        gm.alocar_n_paginas(p0, 6, 3, [p1, p0])
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p0_pag6,
            p0_pag7,
            p0_pag5,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)

    def test_alocar_n_paginas_com_ordem_sem_suspender_processo_memoria_cheia(self):
        simulador = self.simulador
        simulador.quadros = [None] * 6
        gm = simulador.gerenciador_memoria
        p0, p1 = simulador.processos[:2]
        gm.alocar_n_paginas(p0, 0, 4, [])
        gm.alocar_n_paginas(p1, 0, 2, [p0])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        p0_pag5, p0_pag6, p0_pag7 = p0.paginas[5:8]
        p1_pag0, p1_pag1 = p1.paginas[:2]
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p1_pag0,
            p1_pag1,
        ]
        self.assertEqual(memoria, simulador.quadros)
        gm.alocar_n_paginas(p0, 6, 3, [p1, p0])
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p0_pag6,
            p0_pag7,
        ]
        self.assertEqual(memoria, simulador.quadros)

    def test_alocar_n_paginas_restaurar_ordem(self):
        simulador = self.simulador
        gm = simulador.gerenciador_memoria
        p0, p1, p2 = simulador.processos[:3]
        gm.alocar_n_paginas(p0, 0, 4, [])
        gm.alocar_n_paginas(p1, 0, 2, [p0])
        p0_pag0, p0_pag1, p0_pag2, p0_pag3 = p0.paginas[:4]
        p0_pag6, p0_pag7 = p0.paginas[6:8]
        p1_pag0, p1_pag1 = p1.paginas[:2]
        p2_pag0, p2_pag1, p2_pag2 = p2.paginas[:3]
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p1_pag0,
            p1_pag1,
            None,
            None,
        ]
        self.assertEqual(memoria, simulador.quadros)
        gm.alocar_n_paginas(p2, 0, 2, [p0, p1])
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p1_pag0,
            p1_pag1,
            p2_pag0,
            p2_pag1,
        ]
        self.assertEqual(memoria, simulador.quadros)
        ordem = [p2, p1, p0]
        gm.alocar_n_paginas(p0, 6, 2, ordem)
        memoria = [
            p0_pag0,
            p0_pag1,
            p0_pag2,
            p0_pag3,
            p0_pag6,
            p0_pag7,
            p2_pag0,
            p2_pag1,
        ]
        self.assertEqual(memoria, simulador.quadros)
        self.assertEqual([p2, p0], ordem)

if __name__ == '__main__':
    unittest.main()
