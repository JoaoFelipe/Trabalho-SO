import unittest
from base.processo import Processo, EntradaTP


class TestProcesso(unittest.TestCase):

    def test_criarProcessoCom2PaginasComFragmentacao(self):
        processo = Processo(0, 516, 512)
        self.assertEqual(len(processo.paginas), 2)
        self.assertEqual(processo.paginas[0].tamanho, 512)
        self.assertEqual(processo.paginas[1].tamanho, 4)
        self.assertEqual(processo.tabela_paginas, [EntradaTP(0, 0, None), EntradaTP(0, 0, None)])

    def test_criarProcessoCom2PaginasSemFragmentacao(self):
        processo = Processo(0, 1024, 512)
        self.assertEqual(len(processo.paginas), 2)
        self.assertEqual(processo.paginas[0].tamanho, 512)
        self.assertEqual(processo.paginas[1].tamanho, 512)
        self.assertEqual("P 0 Pag 1", str(processo.paginas[1]))
        self.assertEqual(processo.tabela_paginas, [EntradaTP(0, 0, None), EntradaTP(0, 0, None)])

    def test_adicionarMetodo(self):
        processo = Processo(0, 1024, 512)
        processo.add_method(lambda s: 1.0, "ratio")
        self.assertEqual(1.0, processo.ratio())

    def test_adicionarMetodoComFuncaoSeparada(self):
        def ratio(self):
            return 1.0
        processo = Processo(0, 1024, 512)
        processo.add_method(ratio)
        self.assertEqual(1.0, processo.ratio())
