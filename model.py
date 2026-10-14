"""Model do projeto: classes SQLAlchemy (uma por tabela) e acesso ao banco."""
import os
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

# Lê as variáveis do arquivo .env (que NÃO vai para o GitHub)
load_dotenv()

url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url, echo=False)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Produto(Base):
    __tablename__ = "produto"

    id_produto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    vendas: Mapped[list["Venda"]] = relationship(back_populates="produto")

    def __repr__(self) -> str:
        return f"Produto(id={self.id_produto}, nome={self.nome!r}, preco={self.preco_unitario})"


class Venda(Base):
    __tablename__ = "venda"

    id_venda: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_produto: Mapped[int] = mapped_column(ForeignKey("produto.id_produto"), nullable=False)
    data_venda: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    produto: Mapped["Produto"] = relationship(back_populates="vendas")

    def __repr__(self) -> str:
        return (
            f"Venda(id={self.id_venda}, produto={self.id_produto}, "
            f"data={self.data_venda}, qtd={self.quantidade}, total={self.valor_total})"
        )
