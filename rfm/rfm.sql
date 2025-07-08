create or replace temporary table dbt_ike.rfm_model as (with spine as (
    select
        cust.id                                         as customer_id
      , datediff('month', initial_date, current_date()) as cust_age_months
      , subs.annual_recurring_services                  as annual_recurring_services
    from clean_pest_routes_customers               as cust
         left join clean_pest_routes_subscriptions as subs on subs.id = cust.primary_subscription_id
    where
        subs.is_active = 1
    and cust.has_completed_service = 1
    and cust.is_subscriber = 1
    )

   , monetary as (
    select
        customer_id
      , sum(case
                when source_id ilike ('I-%')
                    then amount * -1
                    else 0
                end) as total_invoiced
      , sum(case
                when source_id ilike ('P-%')
                    then amount
                    else 0
                end) as total_paid
    from model_customer_ledger
    where
          customer_id in (
              select
                  customer_id
              from spine
              )
      and ledger_date between current_date - interval '1 year' and current_date
    group by
        1
    )
   , frequency as (
    select
        customer_id
      , service_type_text
      , count(id) as appointment_count
    from clean_pest_routes_appointments
    where
          customer_id in (
              select
                  customer_id
              from spine
              )
      and status_id = 1
      and service_type_text in ('Standard', 'Reservice')
      and appointment_date between current_date - interval '1 year' and current_date
    group by
        1, 2
    )


select
    spine.customer_id
  , total_invoiced
  , total_paid
  , ntile(4) over (order by total_paid)                           as arr_quartile
  , div0(total_paid, total_invoiced)                              as ar_paid_ratio
  , ntile(4) over (order by ar_paid_ratio)                        as ar_paid_ratio_quartile
  , standard.appointment_count                                    as ar_standard_services
  , reservice.appointment_count                                   as ar_reservice_services
  , div0(standard.appointment_count, reservice.appointment_count) as ar_service_type_ratio
  , ntile(4) over (order by ar_service_type_ratio)                as ar_service_type_ratio_quartile
  , spine.annual_recurring_services
  , spine.cust_age_months

from spine
     left join monetary  as arr on spine.customer_id = arr.customer_id
     left join frequency as standard on spine.customer_id = standard.customer_id and standard.service_type_text = 'Standard'
     left join frequency as reservice on spine.customer_id = reservice.customer_id and reservice.service_type_text = 'Reservice')