# Case Study 1: Danny's Diner

## Solution

***

### 1. What is the total amount each customer spent at the restaurant?

````sql
select s.customer_id, sum(m.price) as total_sales
from sales s
join menu m on s.product_id = m.product_id
group by s.customer_id;
````

#### Answer:

| customer_id | total_sales |
| ----------- | ----------- |
| A           | 76          |
| B           | 74          |
| C           | 36          |

***

### 2. How many days has each customer visited the restaurant?

````sql
select customer_id, count(distinct(order_date)) as visit_days
from sales
group by customer_id;
 
````

#### Answer:

| customer_id	| visit_days  |
|-------------|-------------|
| A	          | 4           |
| B	          | 6           |
|	C	          | 2           |

***

### 3. What was the first item from the menu purchased by each customer?

````sql
with first_item_eaten as (
  select s.customer_id, s.product_id, m.product_name,
  dense_rank() over (order by order_date) as first_item
  from sales s
  join menu m on m.product_id = s.product_id)

select customer_id, product_name
from first_item_eaten
where first_item = 1
group by customer_id, product_name;
````

#### Answer:

| customer_id	| product_name|
|-------------|-------------|
| A	          | curry       |
| A	          | shshi       |
| B	          | curry       |
| C	          | ramen       |

***

### 4. What is the most purchased item on the menu and how many times was it purchased by all customers?

````sql
select m.product_name, count(s.product_id) as most_purchased
from menu m
join sales s on s.product_id = m.product_id
group by s.product_id
order by most_purchased desc
limit 1;
````

#### Answer:

| product_name | most_purchased |
|--------------|----------------|
| ramen	       | 8              |

***

### 5. Which item was the most popular for each customer?

````sql
with popular_item as (select 
  s.customer_id, s.product_id, m.product_name, count(s.product_id) as item_count,
  dense_rank() over (partition by customer_id order by count(s.product_id) desc) as item_rank
  from sales s 
  join menu m on m.product_id = s.product_id
  group by s.customer_id, s.product_id)

select customer_id, product_name, item_count
from popular_item
where item_rank =1;
````

#### Answer:

| customer_id |	product_name | item_count |
|-------------|--------------|-------|
| A	          | ramen        | 3     |
| B	          | curry        | 2     |
| B	          | ramen        | 2     |
| B	          | sushi        | 2     |
| C	          | ramen        | 3     |

***

### 6. Which item was purchased first by the customer after they became a member?

````sql
with first_purchased as (select *,
  dense_rank() over (partition by s.customer_id order by s.order_date) as rank
  from sales s 
  join members mb on mb.customer_id = s.customer_id
  join menu m on m.product_id = s.product_id
  where s.order_date >= mb.join_date)

select customer_id, order_date, product_name
from first_purchased
where rank = 1;
````

#### Answer:

| customer_id	| order_date | product_name |
|-------------|------------|--------------|
| A           | 2021-01-07 | curry        |
| B           | 2021-01-11 | sushi        |

***

### 7. Which item was purchased just before the customer became a member?

````sql
with rank as (
  select s.customer_id, s.order_date, m.product_id, m.product_name,
  dense_rank() over (partition by s.customer_id order by s.order_date desc) as rk
  from sales s
  join members mb on mb.customer_id = s.customer_id
  join menu m on m.product_id = s.product_id
  where s.order_date < mb.join_date)
 
select customer_id, order_date, product_name
from rank
where rk =1;
````

#### Answer:

| customer_id	| order_date | product_name | 
|-------------|------------|--------------|
| A          	| 2021-01-01 | sushi        | 
| A          	| 2021-01-01 | curry        |
| B          	| 2021-01-04 | sushi        |

***

### 8. What is the total items and amount spent for each member before they became a member?

````sql
select 
s.customer_id,
count(s.product_id) as quantity,
sum(m.price)  as total_sales
from sales s 
join menu m on m.product_id = s.product_id
join members mb on mb.customer_id = s.customer_id
where s.order_date < mb.join_date
group by s.customer_id;
````

#### Answer:

| customer_id | quantity | total_sales |
|-------------|----------|-------------|
| A	          | 2	       | 25          |
|	B	          | 3	       | 40          |

***

### 9. If each $1 spent equates to 10 points and sushi has a 2x points multiplier — how many points would each customer have?

````sql
select 
s.customer_id,
sum(case when m.product_name ="sushi" then price*20 else price*10 end) as points
from sales s
join menu m on m.product_id = s.product_id
group by s.customer_id;
````

#### Answer:

| customer_id | points | 
| ----------- | -------|
| A           | 860    |
| B           | 940    |
| C           | 360    |

***

### 10. In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi — how many points do customer A and B have at the end of January?

````sql
Select 
customer_id, 
sum(points)
from (
  select s.customer_id,
  sum(case when m.product_name = "sushi" then m.price*20 else m.price*10 end) as points
  from sales s 
  join members mb on mb.customer_id = s.customer_id 
  join menu m on m.product_id = s.product_id
  where s.order_date < mb.join_date or s.order_date > date(mb.join_date, "+6 days") and s.order_date != '2021-02-01'
  group by s.customer_id
  union 
  select s.customer_id,
  sum(m.price*20) as points
  from sales s 
  join members mb on mb.customer_id = s.customer_id 
  join menu m on m.product_id = s.product_id
  where s.order_date >= mb.join_date and s.order_date <= date(mb.join_date, '+6 days')
  group by s.customer_id)
group by customer_id;
````

#### Answer:

| customer_id | sum(points) | 
| ----------- | -------|
| A           | 1370   |
| B           | 820    |

***

## Bonus Questions

### Join All The Things - Recreate the table with: customer_id, order_date, product_name, price, member (Y/N)

````sql
select
s.customer_id,
s.order_date,
m.product_name,
m.price,
(case when s.order_date >= mb.join_date then "Y" else "N" end) as member
from sales s
left join members mb on mb.customer_id = s.customer_id
left join menu m on m.product_id = s.product_id;
````

#### Answer:

| customer_id |	order_date | product_name |	price |	member|
|-------------|------------|--------------|-------|-------|
| A           |	2021-01-01 | sushi        |	10	  | N     |
| A           |	2021-01-01 | curry        |	15	  | N     |
| A           |	2021-01-07 | curry        |	15	  | Y     |
| A           |	2021-01-10 | ramen        |	12	  | Y     |
| A           |	2021-01-11 | ramen        |	12	  | Y     |
| A           |	2021-01-11 | ramen        |	12	  | Y     |
| B           |	2021-01-04 | sushi        |	10	  | N     |
| B           |	2021-01-11 | sushi        |	10	  | Y     |
| B           |	2021-01-01 | curry        |	15	  | N     |
| B           |	2021-01-02 | curry        |	15	  | N     |
| B           |	2021-01-16 | ramen        |	12	  | Y     |
|	B           |	2021-02-01 | ramen        |	12	  | Y     |
| C           |	2021-01-01 | ramen        |	12	  | N     |
| C           |	2021-01-01 | ramen        |	12	  | N     |
| C           |	2021-01-07 | ramen        |	12	  | N     |

### Rank All The Things

````sql
with summary as (select
s.customer_id,
s.order_date,
m.product_name,
m.price,
(case when s.order_date >= mb.join_date then "Y" else "N" end) as member
from sales s
left join members mb on mb.customer_id = s.customer_id
left join menu m on m.product_id = s.product_id)
select *,
case when member = "N" then NULL else dense_rank() over(partition by customer_id, member order by order_date) end as ranking
from summary;
````

#### Answer:

| customer_id	| order_date | product_name	| price| member	| ranking|
|-------------|------------|--------------|-------|-------|--------|
| A           |	2021-01-01 | sushi        |	10	  | N     |	       |
| A           |	2021-01-01 | curry        |	15	  | N	    |	       |
| A           |	2021-01-07 | curry        |	15	  | Y	    |	1      |
| A           |	2021-01-10 | ramen        |	12	  | Y	    | 2      |
| A           |	2021-01-11 | ramen        |	12	  | Y	    | 3      |
| A           |	2021-01-11 | ramen        |	12	  | Y	    | 3      |
| B           |	2021-01-01 | curry        |	15	  | N		  |	       |
| B           |	2021-01-02 | curry        |	15	  | N		  |	       |
| B           |	2021-01-04 | sushi        |	10	  | N		  |	       |
| B           |	2021-01-11 | sushi        |	10	  | Y		  |	1      |
| B           |	2021-01-16 | ramen        |	12	  | Y		  |	2      |
| B           |	2021-02-01 | ramen        |	12	  | Y		  |	3      |
| C           |	2021-01-01 | ramen        |	12	  | N		  |		     |
| C           |	2021-01-01 | ramen        |	12	  | N		  |	       |
| C           |	2021-01-07 | ramen        |	12	  | N		  |	       |
