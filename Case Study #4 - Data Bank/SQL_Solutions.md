# Case Study 4: Data Bank

## Solution

***
### A. Customer Nodes Exploration

#### 1. How many unique nodes are there on the Data Bank system?

````sql 
select
count(distinct node_id) as unique_nodes
from data_bank.customer_nodes;
````

##### Answer:
<img width="766" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/e258cd8b-7e80-4481-af3f-705058c3b807">

#### 2. What is the average total historical deposit counts and amounts for all customers?

````sql 
select
r.region_id,
r.region_name, 
count(cn.node_id) as cnt_nodes
from data_bank.customer_nodes cn
join data_bank.regions r on r.region_id = cn.region_id
group by r.region_id, r.region_name
order by r.region_id;
````

##### Answer:
<img width="938" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/70350e99-47c2-4f8f-9bcb-338ee020a443">

#### 3. How many customers are allocated to each region?

````sql 
select
r.region_id,
r.region_name, 
count(distinct cn.customer_id) as cnt_customers
from data_bank.customer_nodes cn
join data_bank.regions r on r.region_id = cn.region_id
group by r.region_id, r.region_name
order by r.region_id;
````

##### Answer:
<img width="947" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/8b364ed8-da95-4955-9905-496c21942c4f">

#### 4. How many days on average are customers reallocated to a different node?

````sql 
select
round(avg(end_date - start_date),2) as avg_reallocation_days
from data_bank.customer_nodes
where end_date != '9999-12-31';
````

##### Answer:
<img width="763" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/c3f6deb4-0c02-4e5b-8526-d6f8d7044518">

#### 5. What is the median, 80th and 95th percentile for this same reallocation days metric for each region?

````sql 
select
r.*,
percentile_cont(0.5) within group (order by cn.end_date - cn.start_date) as median,
percentile_cont(0.8) within group (order by cn.end_date - cn.start_date) as percentile_80th,
percentile_cont(0.95) within group (order by cn.end_date - cn.start_date) as percentile_95th
from data_bank.customer_nodes cn
left join data_bank.regions r on r.region_id = cn.region_id
where cn.end_date != '9999-12-31'
group by r.region_id, r.region_name;
````

##### Answer:
<img width="935" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/2e42dc40-9ffb-4080-9544-4be5c1a75d20">

***
###  B. Customer Transactions

#### 1. What is the unique count and total amount for each transaction type?

````sql 
select
txn_type,
count(*) as cnt,
sum(txn_amount) as total_amount
from data_bank.customer_transactions
group by txn_type
````

##### Answer:
<img width="775" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/04d0946d-4874-495a-bf7d-1a7ef026dc68">

#### 2. What is the average total historical deposit counts and amounts for all customers?

````sql 
with deposits as (
select
customer_id, 
txn_type,
count(*) as cnt,
avg(txn_amount) as avg_amounts
from data_bank.customer_transactions
group by customer_id, txn_type
order by customer_id, txn_type)

select
round(avg(cnt),0) as avg_count,
round(avg(avg_amounts),2) as avg_amounts
from deposits
where txn_type = 'deposit';
````

##### Answer:
<img width="766" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/8485b93e-8ecd-4ce8-ba9a-5cee4c5663d7">

#### 3. For each month - how many Data Bank customers make more than 1 deposit and either 1 purchase or 1 withdrawal in a single month?

````sql 
with txn_monthly as (select
customer_id, 
extract (month from txn_date) as txn_month, 
sum(case when txn_type = 'deposit' then 1 else 0 end) as deposit_count,
sum(case when txn_type = 'purchase' then 1 else 0 end) as purchase_count,
sum(case when txn_type = 'withdrawal' then 1 else 0 end) as withdrawal_count
from data_bank.customer_transactions
group by customer_id, txn_month 
order by customer_id, txn_month)

select 
txn_month,
count (distinct customer_id) as customer_count
from txn_monthly
where deposit_count > 1 and (purchase_count >= 1 OR withdrawal_count >= 1)
group by txn_month
order by txn_month;
````

##### Answer:
<img width="942" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/a9d9086b-dfb0-452e-a843-0b0690744463">

#### 4. What is the closing balance for each customer at the end of the month?

````sql 
with monthy_balance as (select
customer_id,
extract (month from txn_date) as txn_month,
sum (case when txn_type = 'deposit' then txn_amount else -txn_amount end) as net_amount
from data_bank.customer_transactions
group by customer_id, txn_month
order by customer_id, txn_month)

select 
customer_id,
txn_month, 
sum(net_amount) over (partition by customer_id order by txn_month rows between unbounded preceding and current row) as closing_balance
from monthy_balance;
````

##### Answer: 
(Limiting to the first 9 results)
<img width="932" alt="image" src="https://github.com/chrischowckw/8weekCodingChallenge/assets/104264881/c92cf232-0b73-45d6-af20-7e470fd06a55">

