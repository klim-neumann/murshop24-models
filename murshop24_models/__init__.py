from __future__ import annotations

import datetime

import sqlalchemy as sqla
from sqlalchemy import orm, sql
from sqlalchemy.ext import asyncio as sqla_asyncio

from murshop24_models import enums


class Base(orm.DeclarativeBase, sqla_asyncio.AsyncAttrs):
    pass


class TgOperator(Base):
    __tablename__ = "tg_operator"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    tg_username: orm.Mapped[str] = orm.mapped_column(unique=True)
    tg_bots: orm.Mapped[list[TgBot]] = orm.relationship(back_populates="tg_operator")

    def __str__(self) -> str:
        return self.tg_username


class TgReviewsChannel(Base):
    __tablename__ = "tg_reviews_channel"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    invite_link: orm.Mapped[str] = orm.mapped_column(unique=True)
    tg_bots: orm.Mapped[list[TgBot]] = orm.relationship(
        back_populates="tg_reviews_channel"
    )

    def __str__(self) -> str:
        return str(self.invite_link)


class TgBot(Base):
    __tablename__ = "tg_bot"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    token: orm.Mapped[str] = orm.mapped_column(unique=True)
    tg_id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, unique=True)
    tg_username: orm.Mapped[str] = orm.mapped_column(unique=True)
    is_running: orm.Mapped[bool] = orm.mapped_column(server_default=sql.false())
    tg_operator_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("tg_operator.id")
    )
    tg_reviews_channel_id: orm.Mapped[int | None] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("tg_reviews_channel.id")
    )
    tg_operator: orm.Mapped[TgOperator] = orm.relationship(back_populates="tg_bots")
    tg_reviews_channel: orm.Mapped[TgReviewsChannel | None] = orm.relationship(
        back_populates="tg_bots"
    )

    def __str__(self) -> str:
        return self.tg_username


class TgCustomer(Base):
    __tablename__ = "tg_customer"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    tg_id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, unique=True)
    tg_first_name: orm.Mapped[str]
    tg_last_name: orm.Mapped[str | None]
    tg_username: orm.Mapped[str | None] = orm.mapped_column(unique=True)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        server_default=sql.func.now()
    )
    orders: orm.Mapped[list[Order]] = orm.relationship(back_populates="tg_customer")

    def __str__(self) -> str:
        string = self.tg_first_name
        if self.tg_last_name is not None:
            string = f"{string} {self.tg_last_name}"
        if self.tg_username is not None:
            string = f"{string} @{self.tg_username}"
        return string


class City(Base):
    __tablename__ = "city"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    districts: orm.Mapped[list[District]] = orm.relationship(back_populates="city")

    def __str__(self) -> str:
        return self.name


class District(Base):
    __tablename__ = "district"
    __table_args__ = (sqla.UniqueConstraint("name", "city_id"),)

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    name: orm.Mapped[str]
    city_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("city.id")
    )
    city: orm.Mapped[City] = orm.relationship(back_populates="districts")
    district_product_units: orm.Mapped[list[DistrictProductUnit]] = orm.relationship(
        back_populates="district"
    )
    product_units: orm.Mapped[list[ProductUnit]] = orm.relationship(
        secondary="district_product_unit", back_populates="districts", viewonly=True
    )
    orders: orm.Mapped[list[Order]] = orm.relationship(back_populates="district")

    def __str__(self) -> str:
        return f"{self.city}, {self.name}"


class Product(Base):
    __tablename__ = "product"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    description: orm.Mapped[str | None] = orm.mapped_column(sqla.Text)
    product_units: orm.Mapped[list[ProductUnit]] = orm.relationship(
        back_populates="product"
    )

    def __str__(self) -> str:
        return self.name


class ProductUnit(Base):
    __tablename__ = "product_unit"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    count: orm.Mapped[int]
    count_type: orm.Mapped[enums.ProductUnitCountType]
    product_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("product.id")
    )
    product: orm.Mapped[Product] = orm.relationship(back_populates="product_units")
    district_product_units: orm.Mapped[list[DistrictProductUnit]] = orm.relationship(
        back_populates="product_unit"
    )
    districts: orm.Mapped[list[District]] = orm.relationship(
        secondary="district_product_unit", back_populates="product_units", viewonly=True
    )
    orders: orm.Mapped[list[Order]] = orm.relationship(back_populates="product_unit")

    @staticmethod
    def create_str(product_unit: ProductUnit) -> str:
        match product_unit.count_type:
            case enums.ProductUnitCountType.MILLIGRAM:
                string = f"{product_unit.count / 1000:g}г"
            case enums.ProductUnitCountType.PIECE:
                string = f"{product_unit.count}шт"
        return string

    def __str__(self) -> str:
        count_str = ProductUnit.create_str(self)
        return f"{self.product} {count_str}"


class DistrictProductUnit(Base):
    __tablename__ = "district_product_unit"

    district_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("district.id"), primary_key=True
    )
    product_unit_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("product_unit.id"), primary_key=True
    )
    price: orm.Mapped[int]
    district: orm.Mapped[District] = orm.relationship(
        back_populates="district_product_units"
    )
    product_unit: orm.Mapped[ProductUnit] = orm.relationship(
        back_populates="district_product_units"
    )


class Bank(Base):
    __tablename__ = "bank"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    bank_accounts: orm.Mapped[list[BankAccount]] = orm.relationship(
        back_populates="bank"
    )

    def __str__(self) -> str:
        return self.name


class BankAccount(Base):
    __tablename__ = "bank_account"

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    card_number: orm.Mapped[str] = orm.mapped_column(unique=True)
    phone_number: orm.Mapped[str | None] = orm.mapped_column(unique=True)
    bank_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("bank.id")
    )
    bank: orm.Mapped[Bank] = orm.relationship(back_populates="bank_accounts")
    orders: orm.Mapped[list[Order]] = orm.relationship(back_populates="bank_account")

    def __str__(self) -> str:
        return f"{self.bank}, {self.card_number}"


class QiwiWalletAccount(Base):
    __tablename__ = "qiwi_wallet_account"
    __table_args__ = (
        sqla.CheckConstraint("(phone_number IS NOT NULL) OR (nickname IS NOT NULL)"),
    )

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    phone_number: orm.Mapped[str | None] = orm.mapped_column(unique=True)
    nickname: orm.Mapped[str | None] = orm.mapped_column(unique=True)
    orders: orm.Mapped[list[Order]] = orm.relationship(
        back_populates="qiwi_wallet_account"
    )

    def __str__(self) -> str:
        if self.nickname is not None:
            string = self.nickname
        else:
            assert self.phone_number is not None
            string = self.phone_number
        return string


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (
        sqla.CheckConstraint(
            "(bank_account_id IS NOT NULL) OR (qiwi_wallet_account_id IS NOT NULL)"
        ),
    )

    id: orm.Mapped[int] = orm.mapped_column(sqla.BigInteger, primary_key=True)
    price: orm.Mapped[int]
    status: orm.Mapped[enums.OrderStatus] = orm.mapped_column(
        server_default=enums.OrderStatus.PAYMENT_WAITING
    )
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        server_default=sql.func.now()
    )
    tg_customer_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("tg_customer.id")
    )
    district_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("district.id")
    )
    product_unit_id: orm.Mapped[int] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("product_unit.id")
    )
    bank_account_id: orm.Mapped[int | None] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("bank_account.id")
    )
    qiwi_wallet_account_id: orm.Mapped[int | None] = orm.mapped_column(
        sqla.BigInteger, sqla.ForeignKey("qiwi_wallet_account.id")
    )
    tg_customer: orm.Mapped[TgCustomer] = orm.relationship(back_populates="orders")
    district: orm.Mapped[District] = orm.relationship(back_populates="orders")
    product_unit: orm.Mapped[ProductUnit] = orm.relationship(back_populates="orders")
    bank_account: orm.Mapped[BankAccount | None] = orm.relationship(
        back_populates="orders"
    )
    qiwi_wallet_account: orm.Mapped[QiwiWalletAccount | None] = orm.relationship(
        back_populates="orders"
    )

    def __str__(self) -> str:
        return str(self.id)
