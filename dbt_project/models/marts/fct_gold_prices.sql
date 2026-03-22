with staging as (
    select * from {{ ref('stg_gold_prices') }}
),
daily_metrics as (
    select
        brand,
        price_date,
        avg(buy_price) as avg_buy_price,
        avg(sell_price) as avg_sell_price,
        min(buy_price) as min_buy_price,
        max(buy_price) as max_buy_price,
        count(*) as data_points
    from staging
    group by 1, 2
)
select * from daily_metrics
