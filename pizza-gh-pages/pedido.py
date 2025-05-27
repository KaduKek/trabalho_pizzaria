import datetime
from typing import List, Dict

class ItemPedido:
    def __init__(self, tipo: str, nome: str, detalhes: Dict = None, quantidade: int = 1):
        self.tipo = tipo
        self.nome = nome
        self.detalhes = detalhes or {}
        self.quantidade = quantidade

    def __str__(self) -> str:
        if self.tipo == "pizza":
            adicionais = ", ".join(self.detalhes.get('adicionais', [])) if self.detalhes.get('adicionais') else "Nenhum"
            return f"{self.quantidade}x Pizza {self.nome} ({self.detalhes.get('tamanho', 'Média')}) - Adicionais: {adicionais}"
        else:
            return f"{self.quantidade}x {self.nome}"

class Pedido:
    def __init__(self, numero: int, cliente: str, itens: List[ItemPedido] = None,
                 observacoes: str = "", data_hora: datetime.datetime = None):
        self.numero = numero
        self.cliente = cliente
        self.itens = itens or []
        self.observacoes = observacoes
        self.data_hora = data_hora or datetime.datetime.now()
        self.status = "Pendente"
        self.tempo_preparo = self._calcular_tempo_preparo()

    def _calcular_tempo_preparo(self):
        return 15 + 5 * len(self.itens)