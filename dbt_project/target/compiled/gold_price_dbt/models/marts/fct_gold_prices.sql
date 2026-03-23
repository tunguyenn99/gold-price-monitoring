with staging as (
    select * from "postgres"."gold_marts"."stg_gold_prices"
),
hourly_metrics as (
    select
        brand,
        date_trunc('hour', price_timestamp) as price_hour,
        avg(buy_price) as avg_buy_price,
        avg(sell_price) as avg_sell_price,
        min(buy_price) as min_buy_price,
        max(buy_price) as max_buy_price,
        count(*) as data_points
    from staging
    group by 1, 2
)
select * from hourly_metrics