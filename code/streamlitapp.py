import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import os 
import warnings
import plotly.figure_factory as ff
import seaborn as sns

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

# Add decorative elements
st.markdown("<h1 style='text-align: center; color: #4285f4;'>SuperStore EDA Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #4285f4;'>", unsafe_allow_html=True)



logo_url = './img/sale.jpg'
st.sidebar.image(logo_url)

# File Upload

st.sidebar.header("Upload Data")
f1 = st.sidebar.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

# Default Data Loading
if f1 is not None:
    filename = f1.name
    st.sidebar.success(f"File upload successful: {filename}")
    df = pd.read_csv(filename, encoding="UTF-8")  # Use the file-like object directly
else:
    st.sidebar.info("No file selected. Using default data.")
    df = pd.read_csv("Superstore.csv", encoding="UTF-8")

# Date Range Selector
st.sidebar.header("Select Date Range")
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()
date1 = st.sidebar.date_input("Start Date", startDate)
date2 = st.sidebar.date_input("End Date", endDate)

# Convert 'Order Date' column to datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Apply Filters
df = df[(df["Order Date"] >= pd.to_datetime(date1)) & (df["Order Date"] <= pd.to_datetime(date2))].copy()



# Region Filter
st.sidebar.header("Filter Data")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
state = st.sidebar.multiselect("Pick the State", df["State"].unique())
city = st.sidebar.multiselect("Pick the City", df["City"].unique())

# Apply Filters
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df[df["State"].isin(state) & df["City"].isin(city)]
elif region and city:
    filtered_df = df[df["Region"].isin(region) & df["City"].isin(city)]
elif region and state:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state)]
elif city:
    filtered_df = df[df["City"].isin(city)]
else:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state) & df["City"].isin(city)]

# Charts and Visualizations

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()



col1, col2 = st.columns(2)
with col1:
    # st.subheader("Sales per Region")
    st.markdown(
        "<p style='text-align: center; font-size: 30px; font-weight: bold; color: blue;'>Sales per Region</p>",
        unsafe_allow_html=True,
    )
    regions = filtered_df["Region"]
    sales = filtered_df["Sales"]
    # Create a bar chart using Seaborn
    plt.figure(figsize=(8, 5))
    sns.barplot(x=regions, y=sales, palette="viridis")
    plt.xlabel('Regions')
    plt.ylabel('Sales')
    plt.title('Sales by Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    st.pyplot(plt)
    
    
with col2:
    # st.subheader("Region wise Sales")
    st.markdown(
        "<p style='text-align: center; font-size: 30px; font-weight: bold; color: blue;'>Region wise Sales</p>",
        unsafe_allow_html=True,
    )
    fig = px.pie(category_df, values = "Sales", names = "Category", hole = 0.5)
    fig.update_traces(text = category_df["Category"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
    
    
   

# Expanders
col21, col22 = st.columns(2)
with col21.expander("Explore the Data 📊"):
    st.dataframe(filtered_df)

with col22.expander("Explore the Data 📊"):
    st.dataframe(category_df)

    
# Custom dashed line or space
st.markdown("<hr style='border: 1px dashed #4285f4;'>", unsafe_allow_html=True)    
    

st.subheader("Sales per State")
states = filtered_df["State"]
sales = filtered_df["Sales"]
plt.figure(figsize=(8, 4))
sns.barplot(x=states, y=sales, palette="viridis")
plt.xlabel('States')
plt.ylabel('Sales')
plt.title('Sales by State')
plt.xticks(rotation=90,fontsize=8,  ha='right')


plt.tight_layout()
plt.show()
st.pyplot(plt) 
with st.expander("Explore the Data 📊"):
    st.dataframe(filtered_df)        
  
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        # st.write(region.style.background_gradient(cmap="Oranges"))
        st.write(region.style.background_gradient(axis=0, cmap='YlOrRd'))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
 
# Create a treemap based on State, Category, Sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color_discrete_sequence=px.colors.sequential.Plasma)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)



# Time Series Analysis of Sales

filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"])
time_series_df = filtered_df.resample('M', on='Order Date').sum()

st.subheader("Time Series Analysis of Sales")
fig_time_series = px.line(time_series_df, x=time_series_df.index, y='Sales', labels={'y': 'Total Sales'},
                          line_shape='linear', markers=True, color_discrete_sequence=['green'])
st.plotly_chart(fig_time_series, use_container_width=True)


# Top Products by Sales
top_products_df = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)

st.subheader("Top Products by Sales")
fig_top_products = px.bar(top_products_df, x='Sales', y=top_products_df.index, orientation='h', labels={'y': 'Product'})
st.plotly_chart(fig_top_products, use_container_width=True)

# Profit vs. Discount Scatter Plot
st.subheader("Profit vs. Discount")
fig_scatter = px.scatter(filtered_df, x='Discount', y='Profit', color='Category', size='Sales', hover_data=['Product Name'])
st.plotly_chart(fig_scatter, use_container_width=True)


cl11, cl21 = st.columns((2))
with cl11:

    # Sales Distribution by Ship Mode
    ship_mode_sales_df = filtered_df.groupby('Ship Mode')['Sales'].sum().sort_values(ascending=False)

    st.subheader("Sales Distribution by Ship Mode")
    fig_ship_mode_sales = px.pie(ship_mode_sales_df, values='Sales', names=ship_mode_sales_df.index, title='Sales Distribution by Ship Mode')
    st.plotly_chart(fig_ship_mode_sales, use_container_width=True)

with cl21:
    # Customer Segment Distribution
    segment_distribution_df = filtered_df['Segment'].value_counts()

    st.subheader("Customer Segment Distribution")
    fig_segment_distribution = px.pie(segment_distribution_df, values=segment_distribution_df.values, names=segment_distribution_df.index, title='Customer Segment Distribution')
    st.plotly_chart(fig_segment_distribution, use_container_width=True)
    
    
# Download filtered DataSet
st.info('Download the Filetered Data', icon="ℹ️")
csv = filtered_df.to_csv(index = False).encode('utf-8')
st.download_button('Download Filtered Data', data = csv, file_name = "Filtered_Data.csv",mime = "text/csv")
