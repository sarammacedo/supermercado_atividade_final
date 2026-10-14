"""Grava registros de exemplo: 10 produtos e 30 vendas (40 registros no total)."""
import random
from datetime import date, timedelta
from decimal import Decimal

from model import Produto, Session, Venda

PRODUTOS = [
    ("Arroz 5kg", "Mercearia", "28.90"),
    ("Feijão 1kg", "Mercearia", "8.50"),
    ("Leite integral 1L", "Laticínios", "5.20"),
    ("Queijo mussarela 500g", "Laticínios", "24.00"),
    ("Café 500g", "Mercearia", "19.90"),
    ("Refrigerante 2L", "Bebidas", "9.80"),
    ("Cerveja lata 350ml", "Bebidas", "4.50"),
    ("Sabão em pó 1kg", "Limpeza", "14.30"),
    ("Detergente 500ml", "Limpeza", "2.90"),
    ("Frango congelado 1kg", "Carnes", "13.50"),
]


def popular():
    rng = random.Random(42)  # semente fixa: mesmos dados em toda execução

    with Session() as sessao:
        if sessao.query(Produto).count() > 0:
            print("O banco já tem dados; nada foi inserido.")
            return

        produtos = [
            Produto(nome=n, categoria=c, preco_unitario=Decimal(p)) for n, c, p in PRODUTOS
        ]
        sessao.add_all(produtos)
        sessao.flush()  # gera os id_produto

        inicio = date(2025, 1, 1)
        vendas = []
        for _ in range(30):
            produto = rng.choice(produtos)
            quantidade = rng.randint(1, 20)
            vendas.append(
                Venda(
                    id_produto=produto.id_produto,
                    data_venda=inicio + timedelta(days=rng.randint(0, 364)),
                    quantidade=quantidade,
                    valor_total=produto.preco_unitario * quantidade,
                )
            )
        sessao.add_all(vendas)
        sessao.commit()
        print(f"Inseridos {len(produtos)} produtos e {len(vendas)} vendas.")


if __name__ == "__main__":
    popular()
