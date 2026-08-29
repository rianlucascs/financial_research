

from random import randint


def jittered_delay(min_seconds: int = 5, max_seconds: int = 20) -> int:
    """Retorna um atraso aleatório em segundos, para espaçar requisições."""
    
    return randint(min_seconds, max_seconds)