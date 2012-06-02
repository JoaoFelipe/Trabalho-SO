from base.pyg import PygameInterface
from base.simulador import Simulador

from gerenciadores import *

if __name__ == '__main__':
    tamanhos = {
        'pagina': 1024,
        'endereco_logico': 32,
        'memoria_fisica': 6 * 1024,
        'memoria_secundaria': 100 * 1024,
        'processos': [2000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
    }

    # gerenciador = FifoGlobal
    # gerenciador = FifoLocalFixo
    # gerenciador = FifoLocalVariavel
    # gerenciador = LRUGlobal
    gerenciador = LRULocalFixo
    simulador = Simulador(gerenciador_memoria=gerenciador, **tamanhos)
    PygameInterface(simulador).game_loop()
