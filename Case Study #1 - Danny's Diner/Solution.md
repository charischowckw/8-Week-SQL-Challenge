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

### 4. What is the most purchased item on the menu and how many times was it purchased by all customers?

````python
merged = sales.merge(menu, on='product_id', how='inner').groupby('product_name')['product_name'].agg('count').to_frame('most_purchased').reset_index().sort_values(['most_purchased'], ascending=False).head(1)
merged 
````

#### Answer:

| product_name | most_purchased |
|--------------|----------------|
| ramen	       | 8              |

### 5. Which item was the most popular for each customer?
````python
merged = sales.merge(menu, on='product_id', how='inner').groupby(['customer_id','product_name'])['product_name'].agg('count').to_frame('count').reset_index()
merged['rnk'] = merged.groupby(['customer_id'])['count'].rank(method='dense', ascending=False)
merged[merged['rnk']==1][['customer_id', 'product_name', 'count']]
````
| customer_id |	product_name | count |
|-------------|--------------|-------|
| A	          | ramen        | 3     |
| B	          | curry        | 2     |
| B	          | ramen        | 2     |
| B	          | sushi        | 2     |
| C	          | ramen        | 3     |

### 6. Which item was purchased first by the customer after they became a member?

````python
merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date >= join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense')
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner')[['customer_id', 'product_name', 'order_date']]
merged2 
````

| customer_id	| product_name | order_date |
|-------------|--------------|------------|
| A           | curry        | 2021-01-07 |
| B           | sushi        | 2021-01-11 |

### 7. Which item was purchased just before the customer became a member?

````python
merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date < join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense', ascending=False)
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner').sort_values(['customer_id'])[['customer_id', 'product_name', 'order_date']]
merged2
````
| customer_id	| product_name | order_date |
|-------------|--------------|------------|
| A          	| sushi        | 2021-01-01 |
| A          	| curry        | 2021-01-01 |
| B          	| sushi        | 2021-01-04 |
