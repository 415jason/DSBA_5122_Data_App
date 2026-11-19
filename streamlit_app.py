import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, on July 14th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum(numeric_only=True))
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(numeric_only=True), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq=pd.offsets.MonthEnd())).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")

# Limit the sub-category choices to the selected category
category = st.selectbox("Category", sorted(df["Category"].unique()))
category_df = df[df["Category"] == category]
sub_categories = sorted(category_df["Sub_Category"].unique())
selected_items = st.multiselect("Sub_Category", sub_categories, default=sub_categories, key=category)
selected_df = category_df[category_df["Sub_Category"].isin(selected_items)]

if selected_df.empty:
    st.info("Select at least one sub-category to see monthly sales and profit metrics.")
else:
    st.write("### Monthly sales for the selected items")
    selected_sales_by_month = selected_df["Sales"].groupby(pd.Grouper(freq=pd.offsets.MonthEnd())).sum()
    st.line_chart(selected_sales_by_month)

    # Calculate both margins from total profit and total sales so each dollar has equal weight
    total_sales = selected_df["Sales"].sum()
    total_profit = selected_df["Profit"].sum()
    overall_margin = 100 * df["Profit"].sum() / df["Sales"].sum()

    st.write("### Sales and profit for the selected items")
    sales_col, profit_col, margin_col = st.columns(3)
    sales_col.metric("Total sales", f"${total_sales:,.2f}")
    profit_col.metric("Total profit", f"${total_profit:,.2f}")
    if total_sales:
        selected_margin = 100 * total_profit / total_sales
        margin_col.metric("Overall profit margin", f"{selected_margin:.2f}%",
                          delta=f"{selected_margin - overall_margin:+.2f} pp")
    else:
        margin_col.metric("Overall profit margin", "N/A")
    st.caption(f"The delta shows the percentage-point difference from the all-products margin ({overall_margin:.2f}%).")
