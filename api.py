from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session as SessionType

from model import Produto, Session, Venda

app = FastAPI(title="API de Produtos e Vendas")


class ProdutoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=50)
    preco_unitario: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class ProdutoOut(ProdutoIn):
    model_config = ConfigDict(from_attributes=True)
    id_produto: int


class Resumo(BaseModel):
    total_produtos: int
    preco_medio: float
    total_vendas: int
    faturamento_total: float


def get_db():
    with Session() as sessao:
        yield sessao


@app.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(db: SessionType = Depends(get_db)):
    return db.scalars(select(Produto).order_by(Produto.id_produto)).all()


@app.get("/produtos/{id_produto}", response_model=ProdutoOut)
def buscar_produto(id_produto: int, db: SessionType = Depends(get_db)):
    produto = db.get(Produto, id_produto)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.post("/produtos", response_model=ProdutoOut, status_code=201)
def cadastrar_produto(dados: ProdutoIn, db: SessionType = Depends(get_db)):
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@app.get("/resumo", response_model=Resumo)
def resumo(db: SessionType = Depends(get_db)):
    total_produtos = db.scalar(select(func.count()).select_from(Produto))
    preco_medio = db.scalar(select(func.avg(Produto.preco_unitario)))
    total_vendas = db.scalar(select(func.count()).select_from(Venda))
    faturamento = db.scalar(select(func.sum(Venda.valor_total)))
    return Resumo(
        total_produtos=total_produtos or 0,
        preco_medio=round(float(preco_medio or 0), 2),
        total_vendas=total_vendas or 0,
        faturamento_total=round(float(faturamento or 0), 2),
    )