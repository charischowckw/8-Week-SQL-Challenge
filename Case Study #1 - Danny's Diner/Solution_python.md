# Case Study 1: Danny's Diner

## Solution

***

### Import Packages

````python
import pandas as pd
import numpy as np
import datetime as dt
````

### Import datasets

````python
sales = pd.read_excel('danny_dinner.xlsx', sheet_name = 'sales')
menu = pd.read_excel('danny_dinner.xlsx', sheet_name = 'menu')
members = pd.read_excel('danny_dinner.xlsx', sheet_name = 'members')
````

***

### 1. What is the total amount each customer spent at the restaurant?

````python
merged = sales.merge(menu, on='product_id', how='inner').groupby('customer_id')['price'].sum().reset_index().rename(columns={'price':'total_sales'})
merged
````

#### Answer:

| Customer_id | total_sales |
| ----------- | ----------- |
| A           | 76          |
| B           | 74          |
| C           | 36          |

***

### 2. How many days has each customer visited the restaurant?

````python
merged = sales.merge(menu, on='product_id', how='inner').groupby('customer_id')['order_date'].nunique().reset_index().rename(columns={'order_date':'time_visited'})
merged 
````

#### Answer:

| customer_id	| time_visited|
|-------------|-------------|
| A	          | 4           |
| B	          | 6           |
|	C	          | 2           |

***

### 3. What was the first item from the menu purchased by each customer?

````python
first_item = sales.sort_values(['customer_id', 'order_date'])
first_item['rnk'] = first_item.groupby('customer_id')['order_date'].rank(method='dense')
first_item = first_item[first_item['rnk']==1].drop_duplicates(keep='first')
merged = first_item.merge(menu, on='product_id', how='inner')[['customer_id', 'product_name']]
merged
````

#### Answer:

| customer_id	| product_name|
|-------------|-------------|
| A	          | sushi       |
| A	          | curry       |
| B	          | curry       |
| C	          | ramen       |

***

### 4. What is the most purchased item on the menu and how many times was it purchased by all customers?

````python
merged = sales.merge(menu, on='product_id', how='inner').groupby('product_name')['product_name'].agg('count').to_frame('most_purchased').reset_index().sort_values(['most_purchased'], ascending=False).head(1)
merged 
````

#### Answer:

| product_name | most_purchased |
|--------------|----------------|
| ramen	       | 8              |

***

### 5. Which item was the most popular for each customer?

````python
merged = sales.merge(menu, on='product_id', how='inner').groupby(['customer_id','product_name'])['product_name'].agg('count').to_frame('count').reset_index()
merged['rnk'] = merged.groupby(['customer_id'])['count'].rank(method='dense', ascending=False)
merged[merged['rnk']==1][['customer_id', 'product_name', 'count']]
````

#### Answer:

| customer_id |	product_name | count |
|-------------|--------------|-------|
| A	          | ramen        | 3     |
| B	          | curry        | 2     |
| B	          | ramen        | 2     |
| B	          | sushi        | 2     |
| C	          | ramen        | 3     |

***

### 6. Which item was purchased first by the customer after they became a member?

````python
merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date >= join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense')
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner')[['customer_id', 'product_name', 'order_date']]
merged2 
````

#### Answer:

| customer_id	| product_name | order_date |
|-------------|--------------|------------|
| A           | curry        | 2021-01-07 |
| B           | sushi        | 2021-01-11 |

***

### 7. Which item was purchased just before the customer became a member?

````python
merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date < join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense', ascending=False)
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner').sort_values(['customer_id'])[['customer_id', 'product_name', 'order_date']]
merged2
````

#### Answer:

| customer_id	| product_name | order_date |
|-------------|--------------|------------|
| A          	| sushi        | 2021-01-01 |
| A          	| curry        | 2021-01-01 |
| B          	| sushi        | 2021-01-04 |

***

### 8. What is the total items and amount spent for each member before they became a member?

````python
merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date < join_date').merge(menu, on='product_id', how='inner')
merged.groupby(['customer_id']).agg({"product_name":np.size, 'price':np.sum}).reset_index().rename(columns={'product_name':'product_count', 'price':'amount_spent'})
````

#### Answer:

| customer_id | product_count | amount_spent|
|-------------|---------------|-------------|
| A	          | 2	            | 25          |
|	B	          | 3	            | 40          |

***

### 9. If each $1 spent equates to 10 points and sushi has a 2x points multiplier — how many points would each customer have?

````python
menu['points'] = menu.apply(lambda x: x['price']*20 if x['product_name']=='sushi' else x['price']*10, axis=1)
merged = sales.merge(menu, on='product_id', how='inner').groupby(['customer_id'])['points'].sum().reset_index()
merged 
````

#### Answer:

| customer_id | points | 
| ----------- | -------|
| A           | 860    |
| B           | 940    |
| C           | 360    |

***

### 10. In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi — how many points do customer A and B have at the end of January?

````python
members['last_date'] = members['join_date'] + dt.timedelta(days=7)
menu['points'] = menu.apply(lambda x: x['price']*20 if x['product_name']=='sushi' else x['price']*10, axis=1)

merged = sales.merge(members, on='customer_id', how='inner').query('order_date < 20210201')
first_week_join_points =  merged.query('order_date >= join_date and order_date < last_date')
first_week_join_points = first_week_join_points.merge(menu, on='product_id', how='inner')
first_week_join_points['points'] = first_week_join_points['price']*20

normal_points = merged[~merged.order_date.isin(first_week_join_points.order_date)]
normal_points = normal_points.merge(menu, on='product_id', how='inner')
normal_points['points'] = normal_points.apply(lambda x: x['price']*20 if x['product_name']=='sushi' else x['price']*10, axis=1)

result = pd.concat([first_week_join_points, normal_points]).groupby('customer_id')['points'].sum().reset_index()

result
````

#### Answer:

| Customer_id | points | 
| ----------- | -------|
| A           | 1370   |
| B           | 820    |

***

## Bonus Questions

### Join All The Things - Recreate the table with: customer_id, order_date, product_name, price, member (Y/N)

````python
merged = sales.merge(menu, on='product_id', how='inner').merge(members, on='customer_id', how='outer')
merged['member'] = merged.apply(lambda x:'Y' if x['order_date'] >= x['join_date'] else 'N', axis=1)
merged[['customer_id', 'order_date','product_name', 'price', 'member']]
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
