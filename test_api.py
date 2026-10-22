from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app, get_db
from model import Base, Produto, Venda


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        with TestSession() as sessao:
            yield sessao

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        c.TestSession = TestSession
        yield c
    app.dependency_overrides.clear()


def test_cadastrar_listar_e_buscar_produto(client):
    novo = {"nome": "Arroz 5kg", "categoria": "Mercearia", "preco_unitario": "28.90"}
    r = client.post("/produtos", json=novo)
    assert r.status_code == 201
    criado = r.json()
    assert criado["id_produto"] == 1
    assert criado["nome"] == "Arroz 5kg"

    lista = client.get("/produtos").json()
    assert [p["id_produto"] for p in lista] == [1]

    r = client.get("/produtos/1")
    assert r.status_code == 200
    assert Decimal(r.json()["preco_unitario"]) == Decimal("28.90")


def test_produto_inexistente_retorna_404(client):
    r = client.get("/produtos/999")
    assert r.status_code == 404


def test_resumo_agregado(client):
    with client.TestSession() as s:
        a = Produto(nome="A", categoria="X", preco_unitario=Decimal("10.00"))
        b = Produto(nome="B", categoria="X", preco_unitario=Decimal("20.00"))
        s.add_all([a, b])
        s.flush()
        s.add(Venda(id_produto=a.id_produto, data_venda=date(2025, 1, 1),
                    quantidade=3, valor_total=Decimal("30.00")))
        s.commit()

    r = client.get("/resumo")
    assert r.status_code == 200
    assert r.json() == {
        "total_produtos": 2,
        "preco_medio": 15.0,
        "total_vendas": 1,
        "faturamento_total": 30.0,
    }