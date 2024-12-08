CREATE TABLE public.goszakup_supplier_application_lot (
    application_id BIGINT
    , advertisement_id BIGINT
    , supplier_id BIGINT
    , supplier_biniin VARCHAR(12)
    , prot_id BIGINT
    , prot_number TEXT
    , date_apply TIMESTAMP
    , application_lot_id BIGINT
    , lot_id BIGINT
    , application_lot_price DECIMAL(15, 4)
    , application_lot_amount DECIMAL(15, 4)
    , application_lot_discount_value DECIMAL(15, 4)
    , application_lot_discount_price DECIMAL(15, 4)
    application_lot_status_id INT,
    application_lot_status_name VARCHAR(255),
    application_lot_status_code VARCHAR(50)
);

CREATE TABLE public.gz_lot (
    lot_id BIGINT PRIMARY KEY,
    lot_number VARCHAR(255),
    lot_name TEXT,
    lot_description TEXT,
    lot_status_id INT,
    is_union_lots INT,
    total_count INT,
    total_amount DECIMAL(18, 4),
    customer_id BIGINT,
    advertisement_id BIGINT,
    is_dumping INT,
    plan_trade_method_id INT,
    fact_trade_method_id INT,
    psd_sign INT,
    is_consulting_services INT,
    single_org_sign INT,
    is_light_industry INT,
    is_construction_work INT,
    is_disable_person_advertisement INT,
    plans_ids VARCHAR(255)
);


create table public.ref_gz_supplier_application_lot_status (
  id int
  , name varchar(255)
  , code varchar(50)
);



