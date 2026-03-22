
  create view "postgres"."gold_marts"."stg_gold_prices__dbt_tmp"
    
    
  as (
    with parent as (
    select * from "postgres"."gold_raw"."raw_prices"
),
child as (
    -- dlt by default flattens nested lists into child tables with __entries suffix
    select * from "postgres"."gold_raw"."raw_prices__entries"
),
joined as (
    select
        p.timestamp::timestamp as price_timestamp,
        p.date::date as price_date,
        c.brand,
        c.buy::numeric as buy_price,
        c.sell::numeric as sell_price
    from parent p
    join child c on p._dlt_id = c._dlt_parent_id
)
select * from joined
  );