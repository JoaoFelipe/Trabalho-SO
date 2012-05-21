import unittest
from base.simulador import Simulador, TamanhoMemoriaFisicaException
from base.simulador import TamanhoMemoriaSecundariaException, EnderecoLogicoInvalidoException
from gerenciadores.gerenciador_memoria import GerenciadorMemoria


class GerenciadorTest(GerenciadorMemoria):
    def acessar(self, num_processo, tipo, endereco):
        return {'processo': num_processo, 'tipo': tipo, 'endereco': endereco}


class TestSimulador(unittest.TestCase):

    def setUp(self):
        self.tamanhos = {
            'pagina': 1024,
            'endereco_logico': 32,
            'memoria_fisica': 8 * 1024,
            'memoria_secundaria': 100 * 1024,
            'processos': [2000, 1000, 3000, 5000, 7000, 2000, 8000],
        }

    def test_criarSimuladorCerto(self):
        simulador = Simulador(**self.tamanhos)
        self.assertEqual(simulador.tamanho_pagina, self.tamanhos['pagina'])
        self.assertEqual(simulador.tamanho_endereco_logico, self.tamanhos['endereco_logico'])
        self.assertEqual(simulador.tamanho_memoria_fisica, self.tamanhos['memoria_fisica'])
        self.assertEqual(simulador.tamanho_memoria_secundaria, self.tamanhos['memoria_secundaria'])
        self.assertEqual(len(simulador.processos), 7)
        self.assertEqual(len(simulador.quadros), 8)

    def test_erroAoCriarSimuladorComTamanhoDaMemoriaFisicaNaoMultiploDePagina(self):
        self.tamanhos['memoria_fisica'] = self.tamanhos['memoria_fisica'] - 1
        with self.assertRaises(TamanhoMemoriaFisicaException):
            Simulador(**self.tamanhos)

    def test_erroAoCriarSimuladorComTamanhoDaMemoriaSecundariaNaoSuficiente(self):
        self.tamanhos['memoria_secundaria'] = 1
        with self.assertRaises(TamanhoMemoriaSecundariaException):
            Simulador(**self.tamanhos)

    def test_acessarP1_R_10(self):
        self.tamanhos['endereco_logico'] = 8
        resultado = {'processo': 1, 'tipo': 'R', 'endereco': '00000010'}
        self.tamanhos['gerenciador_memoria'] = GerenciadorTest
        simulador = Simulador(**self.tamanhos)
        self.assertEquals(resultado, simulador.acessar('P1 R 10'))

    def test_acessarP1_R_2_2(self):
        self.tamanhos['endereco_logico'] = 8
        resultado = {'processo': 1, 'tipo': 'R', 'endereco': '00000010'}
        self.tamanhos['gerenciador_memoria'] = GerenciadorTest
        simulador = Simulador(**self.tamanhos)
        self.assertEquals(resultado, simulador.acessar('P1 R (2)2'))

    def test_falha_ao_acessar_endereco_logico_maior_do_que_max(self):
        self.tamanhos['endereco_logico'] = 2
        self.tamanhos['gerenciador_memoria'] = GerenciadorTest
        simulador = Simulador(**self.tamanhos)
        with self.assertRaises(EnderecoLogicoInvalidoException):
            simulador.acessar('P1 R 100')


if __name__ == '__main__':
    unittest.main()
