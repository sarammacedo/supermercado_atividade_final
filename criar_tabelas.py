"""Cria as tabelas produto e venda no banco (venda.id_produto -> produto.id_produto)."""
from model import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabelas criadas:", ", ".join(Base.metadata.tables.keys()))
