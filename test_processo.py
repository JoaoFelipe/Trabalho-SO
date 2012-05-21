import unittest
from processo import Processo, EntradaTP


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
        self.assertEqual(processo.tabela_paginas, [EntradaTP(0, 0, None), EntradaTP(0, 0, None)])

if __name__ == '__main__':
    unittest.main()
