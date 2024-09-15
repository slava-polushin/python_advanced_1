"""
Описание моделей данных.

База для кода получена из созданной структуры БД утилитой sqlacodegen_v2
sqlacodegen_v2 postgresql://app:mypassword@localhost:5432/taxi
"""

from frozendict import frozendict
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKeyConstraint, Index, Numeric, PrimaryKeyConstraint, UniqueConstraint, String, Text, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Cars(Base):
    __tablename__ = 'cars'
    __table_args__ = (
        PrimaryKeyConstraint('car_id', name='cars_pkey'),
        Index('cars_model_idx', 'model'),
        Index('cars_reg_number_idx', 'reg_number'),
        Index('cars_vin_number_idx', 'vin_number'),
        {'comment': 'Автомобили такси'}
    )

    car_id = mapped_column(BigInteger, comment='Идентификатор автомобиля')
    model = mapped_column(String, comment='Модель автомобиля')
    color = mapped_column(String, comment='Цвет автомобиля')
    production_date = mapped_column(Date, comment='Дата производства')
    vin_number = mapped_column(String, comment='Номер VIN')
    reg_number = mapped_column(String, comment='Регистрационный номер')
    comment = mapped_column(Text, comment='Комментарий')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания записи')
    modified_at = mapped_column(DateTime(True), server_default=text(
        'now()'), server_onupdate=text('now()'), comment='Дата изменения записи')

    car_drivers: Mapped[List['CarDrivers']] = relationship(
        'CarDrivers', uselist=True, back_populates='car')
    car_status: Mapped[List['CarStatus']] = relationship(
        'CarStatus', uselist=True, back_populates='car')
    order_status: Mapped[List['OrderStatus']] = relationship(
        'OrderStatus', uselist=True, back_populates='car')


class Clients(Base):
    __tablename__ = 'clients'
    __table_args__ = (
        PrimaryKeyConstraint('client_id', name='clients_pkey'),
        {'comment': 'Клиенты сервиса такси'}
    )

    client_id = mapped_column(BigInteger, comment='Идентификатор пользователя')
    client_name = mapped_column(String, nullable=False, comment='Имя клиента')
    comment = mapped_column(Text, comment='Комментарий')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания записи клиента')
    modified_at = mapped_column(DateTime(True), server_default=text(
        'now()'), server_onupdate=text('now()'), comment='Дата изменения записи клиента')

    orders: Mapped[List['Orders']] = relationship(
        'Orders', uselist=True, back_populates='client')


class Drivers(Base):
    __tablename__ = 'drivers'
    __table_args__ = (
        PrimaryKeyConstraint('driver_id', name='drivers_pkey'),
        {'comment': 'Водители автомобилей'}
    )

    driver_id = mapped_column(BigInteger, comment='Идентификатор водителя')
    driver_name = mapped_column(String, nullable=False, comment='Имя водителя')
    driver_license = mapped_column(
        String, nullable=False, comment='Номер водительского удостоверения')
    comment = mapped_column(Text, comment='Комментарий')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания записи клиента')
    modified_at = mapped_column(DateTime(True), server_default=text(
        'now()'), server_onupdate=text('now()'), comment='Дата изменения записи клиента')

    car_drivers: Mapped[List['CarDrivers']] = relationship(
        'CarDrivers', uselist=True, back_populates='driver')


class CarDrivers(Base):
    __tablename__ = 'car_drivers'
    __table_args__ = (
        ForeignKeyConstraint(['car_id'], ['cars.car_id'],
                             name='car_drivers_car_id_fkey'),
        ForeignKeyConstraint(
            ['driver_id'], ['drivers.driver_id'], name='car_drivers_driver_id_fkey'),
        PrimaryKeyConstraint('id', name='car_drivers_pkey'),
        UniqueConstraint('car_id', 'fromdate', name='car_drivers_altkey'),
        Index('car_drivers_car_id_idx', 'car_id', 'fromdate'),
        {'comment': 'Назначение водителей автомобилям'}
    )

    id = mapped_column(
        BigInteger, comment='Идентификатор записи назначения водителя автомобилю')
    car_id = mapped_column(BigInteger, nullable=False,
                           comment='Идентификатор автомобиля')
    driver_id = mapped_column(BigInteger, comment='Идентификатор водителя')
    fromdate = mapped_column(
        Date, nullable=False, comment='Дата, с которой водитель назначен на автомобиль')
    comment = mapped_column(Text, comment='Комментарий')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания записи назначения')
    modified_at = mapped_column(DateTime(True), server_default=text(
        'now()'), server_onupdate=text('now()'), comment='Дата изменения записи назначения')

    car: Mapped['Cars'] = relationship('Cars', back_populates='car_drivers')
    driver: Mapped[Optional['Drivers']] = relationship(
        'Drivers', back_populates='car_drivers')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        ForeignKeyConstraint(
            ['client_id'], ['clients.client_id'], name='orders_client_id_fkey'),
        PrimaryKeyConstraint('order_id', name='orders_pkey'),
        Index('orders_client_id_idx', 'client_id'),
        {'comment': 'Заказы такси'}
    )

    order_id = mapped_column(BigInteger, comment='Идентификатор заказа')
    client_id = mapped_column(
        BigInteger, nullable=False, comment='Идентификатор пользователя')
    start_address = mapped_column(
        String, nullable=False, comment='Адрес начала поездки')
    start_latitude = mapped_column(
        Numeric(7, 5), comment='широта точки старта')
    start_longitude = mapped_column(
        Numeric(8, 5), comment='долгота точки старта')
    finish_address = mapped_column(String, comment='Адрес завершения поездки')
    finish_latitude = mapped_column(
        Numeric(7, 5), comment='широта точки финиша')
    finish_longitude = mapped_column(
        Numeric(8, 5), comment='долгота точки финиша')
    price = mapped_column(Numeric(18, 2), comment='цена поездки')
    comment = mapped_column(Text, comment='Комментарий')
    baby_chair_fl = mapped_column(
        Boolean, comment='признак необходимости детского кресла')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания заказа')
    modified_at = mapped_column(DateTime(True), server_default=text(
        'now()'), server_onupdate=text('now()'), comment='Дата изменения заказа')

    client: Mapped['Clients'] = relationship(
        'Clients', back_populates='orders')
    car_status: Mapped[List['CarStatus']] = relationship(
        'CarStatus', uselist=True, back_populates='order')
    order_status: Mapped[List['OrderStatus']] = relationship(
        'OrderStatus', uselist=True, back_populates='order')


class CarStatus(Base):
    __tablename__ = 'car_status'
    __table_args__ = (
        ForeignKeyConstraint(['car_id'], ['cars.car_id'],
                             name='car_status_car_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.order_id'],
                             name='car_status_order_id_fkey'),
        PrimaryKeyConstraint('id', name='car_status_pkey'),
        Index('car_status_car_id_idx', 'car_id'),
        Index('car_status_order_id_idx', 'order_id'),
        {'comment': 'История состояний автомобиля'}
    )

    id = mapped_column(
        BigInteger, comment='Идентификатор записи состояния автомобиля')
    car_id = mapped_column(BigInteger, nullable=False,
                           comment='Идентификатор автомобиля')
    status = mapped_column(
        String, nullable=False, comment='Статус автомобиля, может быть равен: {free, busy, broken, driver_missing}')
    current_latitude = mapped_column(
        Numeric(7, 5), comment='Широта текущего местоположения')
    current_longitude = mapped_column(
        Numeric(8, 5), comment='Долгота текущего местоположения')
    order_id = mapped_column(
        BigInteger, comment='Заказ, на который назначен автомобиль на текущий момент (может быть пустым)')
    comment = mapped_column(Text, comment='Комментарий')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания исторической записи заказа')

    car: Mapped['Cars'] = relationship('Cars', back_populates='car_status')
    order: Mapped[Optional['Orders']] = relationship(
        'Orders', back_populates='car_status')


orderStatuses = frozendict({'created': 'created',
                            'car_assigned': 'car_assigned',
                            'trip_started': 'trip_started',
                            'trip_finished': 'trip_finished',
                            'cancelled': 'cancelled'
                            })


class OrderStatus(Base):
    __tablename__ = 'order_status'
    __table_args__ = (
        ForeignKeyConstraint(['car_id'], ['cars.car_id'],
                             name='order_status_car_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.order_id'],
                             name='order_status_order_id_fkey'),
        PrimaryKeyConstraint('id', name='order_status_pkey'),
        Index('order_status_car_id_idx', 'car_id'),
        Index('order_status_order_id_idx', 'order_id'),
        {'comment': 'История статусов заказов такси. Столбцы начиная с car_id '
         'необязательны, и заполняются по мере назначения автомобиля, '
         'начала поездки, завершения поездки, оплаты поездки соответственно'}
    )

    id = mapped_column(
        BigInteger, comment='Идентификатор записи истории заказа')
    order_id = mapped_column(BigInteger, nullable=False,
                             comment='Идентификатор заказа')
    status = mapped_column(
        String, nullable=False, comment='Статус заказа, может быть равен: {created, car_assigned, trip_started, trip_finished, cancelled}')
    car_id = mapped_column(BigInteger, comment='Идентификатор автомобиля')
    comment = mapped_column(Text, comment='Комментарий')
    start_at = mapped_column(DateTime, comment='Время начала поездки')
    finish_at = mapped_column(DateTime, comment='Время завершения поездки')
    unpaid_rest = mapped_column(Numeric(18, 2), comment='Неоплаченный остаток')
    created_at = mapped_column(DateTime(True), server_default=text(
        'now()'), comment='Дата создания исторической записи заказа')

    car: Mapped[Optional['Cars']] = relationship(
        'Cars', back_populates='order_status')
    order: Mapped['Orders'] = relationship(
        'Orders', back_populates='order_status')
