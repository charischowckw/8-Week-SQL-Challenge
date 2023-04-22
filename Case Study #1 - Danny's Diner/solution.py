import pandas as pd
import numpy as np
import datetime as dt

sales = pd.read_excel('danny_dinner.xlsx', sheet_name = 'sales')
menu = pd.read_excel('danny_dinner.xlsx', sheet_name = 'menu')
members = pd.read_excel('/danny_dinner.xlsx', sheet_name = 'members')

"""1. What is the total amount each customer spent at the restaurant?"""

merged = sales.merge(menu, on='product_id', how='inner').groupby('customer_id')['price'].sum().reset_index().rename(columns={'price':'total_sales'})
merged

"""2. How many days has each customer visited the restaurant?"""

merged = sales.merge(menu, on='product_id', how='inner').groupby('customer_id')['order_date'].nunique().reset_index().rename(columns={'order_date':'time_visited'})
merged

"""3. What was the first item from the menu purchased by each customer?"""

first_item = sales.sort_values(['customer_id', 'order_date'])
first_item['rnk'] = first_item.groupby('customer_id')['order_date'].rank(method='dense')
first_item = first_item[first_item['rnk']==1].drop_duplicates(keep='first')
merged = first_item.merge(menu, on='product_id', how='inner')[['customer_id', 'product_name']]
merged

"""4. What is the most purchased item on the menu and how many times was it purchased by all customers?"""

merged = sales.merge(menu, on='product_id', how='inner').groupby('product_name')['product_name'].agg('count').to_frame('most_purchased').reset_index().sort_values(['most_purchased'], ascending=False).head(1)
merged

"""5. Which item was the most popular for each customer?"""

merged = sales.merge(menu, on='product_id', how='inner').groupby(['customer_id','product_name'])['product_name'].agg('count').to_frame('count').reset_index()
merged['rnk'] = merged.groupby(['customer_id'])['count'].rank(method='dense', ascending=False)
merged[merged['rnk']==1][['customer_id', 'product_name', 'count']]

"""6. Which item was purchased first by the customer after they became a member?"""

merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date >= join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense')
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner')[['customer_id', 'product_name', 'order_date']]
merged2

"""7. Which item was purchased just before the customer became a member?"""

merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date < join_date')
merged['rnk'] = merged.groupby(['customer_id'])['order_date'].rank(method='dense', ascending=False)
merged = merged.query('rnk == 1')
merged2 = merged.merge(menu, on='product_id', how = 'inner').sort_values(['customer_id'])[['customer_id', 'product_name', 'order_date']]
merged2

"""8. What is the total items and amount spent for each member before they became a member?"""

merged = sales.merge(members, on='customer_id', how = 'inner').query('order_date < join_date').merge(menu, on='product_id', how='inner')
merged.groupby(['customer_id']).agg({"product_name":np.size, 'price':np.sum}).reset_index().rename(columns={'product_name':'product_count', 'price':'amount_spent'})

"""9. If each $1 spent equates to 10 points and sushi has a 2x points multiplier — how many points would each customer have?"""

menu['points'] = menu.apply(lambda x: x['price']*20 if x['product_name']=='sushi' else x['price']*10, axis=1)
merged = sales.merge(menu, on='product_id', how='inner').groupby(['customer_id'])['points'].sum().reset_index()
merged

"""10. In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi — how many points do customer A and B have at the end of January?"""

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

"""Recreate the table with: customer_id, order_date, product_name, price, member (Y/N)"""

merged = sales.merge(menu, on='product_id', how='inner').merge(members, on='customer_id', how='outer')
merged['member'] = merged.apply(lambda x:'Y' if x['order_date'] >= x['join_date'] else 'N', axis=1)
