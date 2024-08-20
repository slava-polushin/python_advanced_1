CREATE SCHEMA IF NOT EXISTS taxi;

ALTER ROLE app SET search_path TO taxi, public;

-- Технологическая таблица alembic
CREATE TABLE IF NOT EXISTS taxi.alembic_version (
	version_num varchar(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
insert into taxi.alembic_version(version_num)
values('35e3154777a8');

-- Ниже создается структура функциональной части БД
-- Создана для того, чтобы миграция alembic была пустой; вся структура БД уже совпадает с models

CREATE OR REPLACE FUNCTION taxi.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = now();
    RETURN NEW;
end;
$$ language 'plpgsql';

-- Клиенты сервиса такси
CREATE TABLE IF NOT EXISTS taxi.clients(
    client_id BIGSERIAL NOT NULL PRIMARY KEY,
    client_name VARCHAR NOT NULL,
    comment TEXT,
    created_at TIMESTAMP with time zone default now(),
    modified_at TIMESTAMP with time zone default now()
  );
COMMENT ON TABLE taxi.clients is 'Клиенты сервиса такси';

COMMENT ON COLUMN taxi.clients.client_id IS 'Идентификатор пользователя';
COMMENT ON COLUMN taxi.clients.client_name IS 'Имя клиента';
COMMENT ON COLUMN taxi.clients.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.clients.created_at is 'Дата создания записи клиента';
COMMENT ON COLUMN taxi.clients.modified_at is 'Дата изменения записи клиента';

create or replace TRIGGER update_clients_modtime
    BEFORE UPDATE ON taxi.clients
    FOR EACH ROW EXECUTE FUNCTION taxi.update_modified_column();


-- Заказы такси
CREATE TABLE IF NOT EXISTS taxi.orders(
    order_id BIGSERIAL NOT NULL PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES taxi.clients,
    start_address VARCHAR NOT NULL,
    start_latitude NUMERIC(6,5),
    start_longitude NUMERIC(6,5),
    finish_address VARCHAR,
    finish_latitude NUMERIC(6,5),
    finish_longitude NUMERIC(6,5),
    price NUMERIC(18,2),
    comment TEXT,
    baby_chair_fl BOOLEAN,
    created_at TIMESTAMP with time zone default now(),
    modified_at TIMESTAMP with time zone default now()
  );
COMMENT ON TABLE taxi.orders is 'Заказы такси';

COMMENT ON COLUMN taxi.orders.order_id IS 'Идентификатор заказа';
COMMENT ON COLUMN taxi.orders.client_id IS 'Идентификатор пользователя';
COMMENT ON COLUMN taxi.orders.start_address IS 'Адрес начала поездки';
COMMENT ON COLUMN taxi.orders.start_latitude IS 'широта точки старта';
COMMENT ON COLUMN taxi.orders.start_longitude IS 'долгота точки старта';
COMMENT ON COLUMN taxi.orders.finish_address IS 'Адрес завершения поездки';
COMMENT ON COLUMN taxi.orders.finish_latitude IS 'широта точки финиша';
COMMENT ON COLUMN taxi.orders.finish_longitude IS 'долгота точки финиша';
COMMENT ON COLUMN taxi.orders.price IS 'цена поездки';
COMMENT ON COLUMN taxi.orders.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.orders.baby_chair_fl IS 'признак необходимости детского кресла';
COMMENT ON COLUMN taxi.orders.created_at is 'Дата создания заказа';
COMMENT ON COLUMN taxi.orders.modified_at is 'Дата изменения заказа';

CREATE INDEX IF NOT EXISTS orders_client_id_idx ON taxi.orders(client_id);

create or replace TRIGGER update_orders_modtime
    BEFORE UPDATE ON taxi.orders
    FOR EACH ROW EXECUTE FUNCTION taxi.update_modified_column();


-- Автомобили такси
CREATE TABLE IF NOT EXISTS taxi.cars(
    car_id BIGSERIAL NOT NULL PRIMARY KEY,
    model VARCHAR,
    color VARCHAR,
    production_date DATE,
    vin_number VARCHAR,
    reg_number VARCHAR,
    comment TEXT,
    created_at TIMESTAMP with time zone default now(),
    modified_at TIMESTAMP with time zone default now()
  );
COMMENT ON TABLE taxi.cars is 'Автомобили такси';

COMMENT ON COLUMN taxi.cars.car_id IS 'Идентификатор автомобиля';
COMMENT ON COLUMN taxi.cars.model IS 'Модель автомобиля';
COMMENT ON COLUMN taxi.cars.color IS 'Цвет автомобиля';
COMMENT ON COLUMN taxi.cars.production_date IS 'Дата производства';
COMMENT ON COLUMN taxi.cars.vin_number IS 'Номер VIN';
COMMENT ON COLUMN taxi.cars.reg_number IS 'Регистрационный номер';
COMMENT ON COLUMN taxi.cars.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.cars.created_at is 'Дата создания записи';
COMMENT ON COLUMN taxi.cars.modified_at is 'Дата изменения записи';

CREATE INDEX IF NOT EXISTS cars_model_idx ON taxi.cars(model);
CREATE INDEX IF NOT EXISTS cars_vin_number_idx ON taxi.cars(vin_number);
CREATE INDEX IF NOT EXISTS cars_reg_number_idx ON taxi.cars(reg_number);

create or replace TRIGGER update_cars_modtime
    BEFORE UPDATE ON taxi.cars
    FOR EACH ROW EXECUTE FUNCTION taxi.update_modified_column();


-- История статусов заказов такси
CREATE TABLE IF NOT EXISTS taxi.order_status(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES taxi.orders,
    status VARCHAR NOT NULL,
    car_id BIGINT REFERENCES taxi.cars,
    comment TEXT,
    start_at TIMESTAMP,
    finish_at TIMESTAMP,
    unpaid_rest NUMERIC(18,2),
    created_at TIMESTAMP with time zone default now()
);
COMMENT ON TABLE taxi.order_status is 'История статусов заказов такси. Столбцы начиная с car_id необязательны, и заполняются по мере назначения автомобиля, начала поездки, завершения поездки, оплаты поездки соответственно';

COMMENT ON COLUMN taxi.order_status.id IS 'Идентификатор записи истории заказа';
COMMENT ON COLUMN taxi.order_status.order_id IS 'Идентификатор заказа';
COMMENT ON COLUMN taxi.order_status.status IS 'Статус заказа, может быть равен: {created, car_assigned, trip_started, trip_finished, cancelled}';
COMMENT ON COLUMN taxi.order_status.car_id IS 'Идентификатор автомобиля';
COMMENT ON COLUMN taxi.order_status.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.order_status.start_at IS 'Время начала поездки';
COMMENT ON COLUMN taxi.order_status.finish_at IS 'Время завершения поездки';
COMMENT ON COLUMN taxi.order_status.unpaid_rest IS 'Неоплаченный остаток';
COMMENT ON COLUMN taxi.order_status.created_at is 'Дата создания исторической записи заказа';

CREATE INDEX IF NOT EXISTS order_status_order_id_idx ON taxi.order_status(order_id);
CREATE INDEX IF NOT EXISTS order_status_car_id_idx ON taxi.order_status(car_id);


-- История состояний автомобиля
CREATE TABLE IF NOT EXISTS taxi.car_status(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    car_id BIGINT NOT NULL REFERENCES taxi.cars,
    status VARCHAR NOT NULL,
    current_latitude NUMERIC(6,5),
    current_longitude NUMERIC(6,5),
    order_id BIGINT REFERENCES taxi.orders,
    comment TEXT,
    created_at TIMESTAMP with time zone default now()
);
COMMENT ON TABLE taxi.car_status is 'История состояний автомобиля';

COMMENT ON COLUMN taxi.car_status.id IS 'Идентификатор записи состояния автомобиля';
COMMENT ON COLUMN taxi.car_status.car_id IS 'Идентификатор автомобиля';
COMMENT ON COLUMN taxi.car_status.status IS 'Статус автомобиля, может быть равен: {free, busy, broken, driver_missing}';
COMMENT ON COLUMN taxi.car_status.current_latitude IS 'Широта текущего местоположения';
COMMENT ON COLUMN taxi.car_status.current_longitude IS 'Долгота текущего местоположения';
COMMENT ON COLUMN taxi.car_status.order_id IS 'Заказ, на который назначен автомобиль на текущий момент (может быть пустым)';
COMMENT ON COLUMN taxi.car_status.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.car_status.created_at is 'Дата создания исторической записи заказа';

CREATE INDEX IF NOT EXISTS car_status_car_id_idx ON taxi.car_status(car_id);
CREATE INDEX IF NOT EXISTS car_status_order_id_idx ON taxi.car_status(order_id);


-- Водители автомобилей
CREATE TABLE IF NOT EXISTS taxi.drivers(
    driver_id BIGSERIAL NOT NULL PRIMARY KEY,
    driver_name VARCHAR NOT NULL,
    driver_license VARCHAR NOT NULL,
    comment TEXT,
    created_at TIMESTAMP with time zone default now(),
    modified_at TIMESTAMP with time zone default now()
  );
COMMENT ON TABLE taxi.drivers is 'Водители автомобилей';

COMMENT ON COLUMN taxi.drivers.driver_id IS 'Идентификатор водителя';
COMMENT ON COLUMN taxi.drivers.driver_name IS 'Имя водителя';
COMMENT ON COLUMN taxi.drivers.driver_license IS 'Номер водительского удостоверения';
COMMENT ON COLUMN taxi.drivers.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.drivers.created_at is 'Дата создания записи клиента';
COMMENT ON COLUMN taxi.drivers.modified_at is 'Дата изменения записи клиента';

create or replace TRIGGER update_drivers_modtime
    BEFORE UPDATE ON taxi.drivers
    FOR EACH ROW EXECUTE FUNCTION taxi.update_modified_column();


-- Назначение водителей автомобилям
CREATE TABLE IF NOT EXISTS taxi.car_drivers(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    car_id BIGINT NOT NULL REFERENCES taxi.cars,
    driver_id BIGINT REFERENCES taxi.drivers,
    fromdate DATE NOT NULL,
    comment TEXT,
    created_at TIMESTAMP with time zone default now(),
    modified_at TIMESTAMP with time zone default now()
  );
COMMENT ON TABLE taxi.car_drivers is 'Назначение водителей автомобилям';

COMMENT ON COLUMN taxi.car_drivers.id IS 'Идентификатор записи назначения водителя автомобилю';
COMMENT ON COLUMN taxi.car_drivers.car_id IS 'Идентификатор автомобиля';
COMMENT ON COLUMN taxi.car_drivers.driver_id IS 'Идентификатор водителя';
COMMENT ON COLUMN taxi.car_drivers.fromdate IS 'Дата, с которой водитель назначен на автомобиль';
COMMENT ON COLUMN taxi.car_drivers.comment IS 'Комментарий';
COMMENT ON COLUMN taxi.car_drivers.created_at is 'Дата создания записи назначения';
COMMENT ON COLUMN taxi.car_drivers.modified_at is 'Дата изменения записи назначения';

CREATE INDEX IF NOT EXISTS car_drivers_car_id_idx ON taxi.car_drivers(car_id);
CREATE INDEX IF NOT EXISTS car_drivers_driver_id_idx ON taxi.car_drivers(driver_id);

create or replace TRIGGER update_car_drivers_modtime
    BEFORE UPDATE ON taxi.car_drivers
    FOR EACH ROW EXECUTE FUNCTION taxi.update_modified_column();

