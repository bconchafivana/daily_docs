daily_query = """SELECT dd.*, 
dd.fecha_ejecucion - 1 as fecha_vision, 
dd.fecha_ejecucion - dd.vencimiento - 1 as mora_days,
case when dd.fecha_ejecucion - dd.vencimiento - 1 <= 0 then '1. No Mora'
	when dd.fecha_ejecucion - dd.vencimiento - 1 >= 0 and dd.fecha_ejecucion - dd.vencimiento - 1 < 30 then '2. 30 Mora'
	when dd.fecha_ejecucion - dd.vencimiento - 1 >= 30 and dd.fecha_ejecucion - dd.vencimiento - 1 < 60 then '3. 60 Mora'
	when dd.fecha_ejecucion - dd.vencimiento - 1 >= 60 and dd.fecha_ejecucion - dd.vencimiento - 1 < 90 then '4. 90 Mora'
	when dd.fecha_ejecucion - dd.vencimiento - 1 >= 90  then '5. +90 Mora' end as mora_cluster
FROM daily_delay_payments_status dd
WHERE dd.fecha_ejecucion IN (SELECT MIN(ddps.fecha_ejecucion)
                             FROM daily_delay_payments_status ddps
                             GROUP BY EXTRACT(MONTH FROM ddps.fecha_ejecucion))
OR dd.fecha_ejecucion > now() - INTERVAL '30 days' """


query_mem = """
 select d.document_id , json_extract_string(d.operation, 'no_reception') as n_op, 
json_extract_string(d.operation, 'price_dif') as price_dif,
json_extract_string(d.operation, 'base_rate') as base_rate,
round(30*100*(round((o.comissions + o.expenses)*d.finance_amount/o.finance_amount) + json_extract_string(d.operation, 'price_dif'))/(json_extract_string(d.operation, 'expiration_days')*d.finance_amount), 2) as rate_all_in,
json_extract_string(d.operation, 'expiration_days') as expiration_days,
json_extract_string(d.operation, 'financing_factoring') as financing_factoring, 
coms.comission, 
round((o.comissions + o.expenses)*d.finance_amount/o.finance_amount) as com_exps,
d.debtor_category
from fc_documents d
left join (
select dp.document_id,
case when dp.proportion_valid_payed = 1 and dp.revenue_executive > 0  and dp.mora_days_executive < 61 then round(0.085*dp.revenue_executive)
	when dp.proportion_valid_payed < 1 and dp.revenue_executive > 0 and dp.mora_days_executive < 61 then round(0.5*dp.proportion_valid_payed*0.085*dp.revenue_executive)
	else 0 end as comission
	from ds_perceived2 dp
) coms on coms.document_id = d.document_id 
left join fc_rf_operation_documents od on od.document_id = d.document_id 
left join fc_operations o on o.operation_id = od.operation_id 
where d.status in (2,3) and o.status_description <> 'Rechazada' and d.document_id in 
"""