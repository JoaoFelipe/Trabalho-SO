from fifo_global import FifoGlobal
from pyg import PygameInterface
from simulador import Simulador

if __name__ == '__main__':
    tamanhos = {
        'pagina': 1024,
        'endereco_logico': 32,
        'memoria_fisica': 4*1024,
        'memoria_secundaria': 100*1024,
        'processos': [2000, 2000, 3000, 5000, 7000, 2000, 8000, 9000],
    }

    simulador = Simulador(gerenciador_memoria=FifoGlobal, **tamanhos)
    PygameInterface(simulador).game_loop()
