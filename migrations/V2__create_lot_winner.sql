create table lot_winner as
with t_first_winner as (
    select
        gl.advertisement_id
        , gl.lot_id
        , LEAST(application_lot_price, application_lot_amount) as item_price
        , GREATEST(application_lot_price, application_lot_amount) as total_price
        , application_lot_discount_value as discount
        , CASE
            WHEN application_lot_discount_price = 0 THEN
                GREATEST(application_lot_price, application_lot_amount)
            ELSE
                LEAST(
                    GREATEST(application_lot_price, application_lot_amount)
                    , application_lot_discount_price
                )
          END as total_price_wdiscount
        , row_number() over (partition by supplier_id, lot_id order by prot_id desc) as row_num
    from goszakup_supplier_application_lot gl
    where application_lot_status_id = 360 and date_apply >= to_date('2020-01-01', 'YYYY-MM-DD')
), first_winner as (
    select
        advertisement_id
        , lot_id
        , item_price
        , total_price
        , discount
        , total_price_wdiscount
    from t_first_winner where row_num = 1
), t_second_winner_candidate as (
    select
        gl.advertisement_id
        , gl.lot_id
        , LEAST(application_lot_price, application_lot_amount) as item_price
        , GREATEST(application_lot_price, application_lot_amount) as total_price
        , application_lot_discount_value as discount
        , CASE
            WHEN application_lot_discount_price = 0 THEN
                GREATEST(application_lot_price, application_lot_amount)
            ELSE
                LEAST(
                    GREATEST(application_lot_price, application_lot_amount)
                    , application_lot_discount_price
                )
          END as total_price_wdiscount
        , row_number() over (partition by supplier_id, lot_id order by prot_id desc) as row_num
    from goszakup_supplier_application_lot gl
    where application_lot_status_id != 360 and date_apply >= to_date('2020-01-01', 'YYYY-MM-DD')
), second_winner as (
    select
        advertisement_id
        , lot_id
        , item_price
        , total_price
        , discount
        , total_price_wdiscount
        , row_number() over (partition by lot_id order by total_price_wdiscount) as second_winner_rnk
    from t_second_winner_candidate where row_num = 1
)
SELECT
    fw.advertisement_id as "advertisement_id"
    , fw.lot_id as "lot_id"
    , fw.item_price as "fw_item_price"
    , fw.total_price as "fw_total_price"
    , fw.discount as "fw_discount"
    , fw.total_price_wdiscount as "fw_total_price_wdiscount"
    , sw.item_price as "sw_item_price"
    , sw.total_price as "sw_total_price"
    , sw.discount as "sw_discount"
    , sw.total_price_wdiscount as "sw_total_price_wdiscount"
FROM first_winner fw
LEFT JOIN second_winner sw
    ON fw.lot_id = sw.lot_id
    AND fw.advertisement_id = sw.advertisement_id
    AND sw.second_winner_rnk = 1;


CREATE INDEX idx_lot_winner_advertisement
ON lot_winner (advertisement_id);

CREATE INDEX idx_lot_winner_lot
ON lot_winner (lot_id);
