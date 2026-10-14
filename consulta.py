"""Consulta simples para o print da entrega."""
from sqlalchemy import func, select

from model import Produto, Session, Venda

with Session() as sessao:
    total_produtos = sessao.scalar(select(func.count()).select_from(Produto))
    total_vendas = sessao.scalar(select(func.count()).select_from(Venda))
    print(f"Produtos cadastrados: {total_produtos}")
    print(f"Vendas registradas:   {total_vendas}")

    print("\nOs 5 primeiros produtos:")
    for p in sessao.scalars(select(Produto).order_by(Produto.id_produto).limit(5)):
        print(" ", p)

    print("\nAs 5 primeiras vendas (com o nome do produto):")
    for v in sessao.scalars(select(Venda).order_by(Venda.id_venda).limit(5)):
        print(f"  Venda {v.id_venda} | {v.data_venda} | {v.produto.nome} | qtd {v.quantidade} | R$ {v.valor_total}")
