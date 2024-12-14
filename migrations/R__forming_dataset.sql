select count(1) from lot_winner;

create table dataset as
with tmp as (
    select
        lw.advertisement_id
        , lw.lot_id
        , lw.fw_item_price
        , lw.fw_total_price
        , lw.fw_discount
        , lw.fw_total_price_wdiscount
        , lw.sw_item_price
        , lw.sw_total_price
        , lw.sw_discount
        , lw.sw_total_price_wdiscount
        , gl.lot_number
        , gl.lot_name
        , gl.lot_description
        , gl.lot_status_id
        , gl.is_union_lots
        , gl.total_count
        , gl.total_amount
        , gl.customer_id
        , gl.is_dumping
        , gl.plan_trade_method_id
        , gl.fact_trade_method_id
        , gl.psd_sign
        , gl.is_consulting_services
        , gl.single_org_sign
        , gl.is_light_industry
        , gl.is_construction_work
        , gl.is_disable_person_advertisement
        , gl.plans_ids
        , ga.advertisement_number
        , ga.advertisement_name
        , ga.total_sum as ad_total_sum
        , ga.lots_count as ad_lots_count
        , ga.trade_method_id as ad_trade_method_id
        , ga.subject_type_id as ad_subject_type_id
        , ga.customer_id as ad_customer_id
        , ga.advertisement_status_id
        , ga.start_date as ad_start_date
        , ga.repeat_start_date as ad_repeat_start_date
        , ga.end_date as ad_end_date
        , ga.repeat_end_date as ad_repeat_end_date
        , ga.publish_date as ad_publish_date
        , ga.itogi_date_public as ad_itogi_date_public
        , ga.trade_type_id as ad_trade_type_id
        , ga.disable_person_id as ad_disable_person_id
        , ga.single_org_sign as ad_single_org_sign
        , ga.is_light_industry as ad_is_light_industry
        , ga.is_construction_work as ad_is_construction_work
        , ga.purchase_type_id as ad_purchase_type_id
        , ga.fin_years as ad_fin_years
        , ga.katos as ad_katos
    from lot_winner lw
    INNER JOIN gz_lot gl
        ON lw.lot_id = gl.lot_id
        AND lw.advertisement_id = gl.advertisement_id
    INNER JOIN gz_advertisement ga
        ON lw.advertisement_id = ga.advertisement_id
)
select * from tmp;


-- не все закупки были успешно завершены, от части из них отказались/часть не состоялась, поэтому мы взяли только те закупки которые были успешно завершены
-- т.е те по которым все состоялось
-- create table dataset_v1 as
select * from dataset
where
    advertisement_status_id = 350
    and ad_start_date >= to_date('2020-01-01', 'YYYY-MM-DD');

