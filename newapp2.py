import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# Set page title and layout
st.set_page_config(page_title="Superstore Analytics", layout="wide", page_icon="📊")

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv("superstore.csv")  # Replace with your file path
    data["Order Date"] = pd.to_datetime(data["Order Date"])  # Convert to datetime
    return data

df = load_data()

# Sidebar for global filters
st.sidebar.header("Global Filters")
region = st.sidebar.multiselect("Select Region", df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Select Category", df["Category"].unique(), default=df["Category"].unique())
segment = st.sidebar.multiselect("Select Customer Segment", df["Segment"].unique(), default=df["Segment"].unique())

# Date range filter
st.sidebar.header("Date Range Filter")
min_date = df["Order Date"].min()
max_date = df["Order Date"].max()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Convert date inputs to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Apply filters
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Segment"].isin(segment)) &
    (df["Order Date"] >= start_date) &
    (df["Order Date"] <= end_date)
]

# Top N slider
st.sidebar.header("Top N Analysis")
top_n = st.sidebar.slider("Select Top N", 5, 20, 10)

# Multi-page layout
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Sales Analysis", "Profit Analysis", "Geographical Analysis", "Sales Rep Analysis", "Send Notifications"])

# Page 1: Overview
if page == "Overview":
    st.title("📊 Superstore Analytics - Overview")
    st.markdown("Welcome to the Superstore Analytics Dashboard! Explore insights across sales, profit, and customer segments.")

    # KPIs
    st.subheader("Key Performance Indicators (KPIs)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"SAR {filtered_df['Sales'].sum():,.2f}")
    with col2:
        st.metric("Total Profit", f"SAR {filtered_df['Profit'].sum():,.2f}")
    with col3:
        st.metric("Average Discount", f"{filtered_df['Discount'].mean():.2%}")

    # Sales and Profit Trends
    st.subheader("Sales and Profit Trends Over Time")
    trend_data = filtered_df.groupby("Order Date")[["Sales", "Profit"]].sum().reset_index()
    fig1 = px.line(
        trend_data,
        x="Order Date",
        y=["Sales", "Profit"],
        title="Sales and Profit Over Time",
        labels={"value": "Amount", "variable": "Metric"},
        color_discrete_sequence=["#636EFA", "#EF553B"],
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Top Products by Sales
    st.subheader(f"Top {top_n} Products by Sales")
    top_products = filtered_df.groupby("Product Name")["Sales"].sum().nlargest(top_n).reset_index()
    fig2 = px.bar(
        top_products,
        x="Product Name",
        y="Sales",
        title=f"Top {top_n} Products by Sales",
        color="Sales",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig2, use_container_width=True)

# Page 2: Sales Analysis
elif page == "Sales Analysis":
    st.title("📈 Sales Analysis")
    st.markdown("Explore sales trends and performance across categories, sub-categories, and regions.")

    # Sales by Category (Bar Chart)
    st.subheader("Sales by Category")
    sales_by_category = filtered_df.groupby("Category")["Sales"].sum().reset_index()
    fig3 = px.bar(
        sales_by_category,
        x="Category",
        y="Sales",
        title="Sales by Category",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Sales by Sub-Category (Treemap)
    st.subheader("Sales by Sub-Category (Treemap)")
    fig4 = px.treemap(
        filtered_df,
        path=["Category", "Sub-Category"],
        values="Sales",
        color="Sales",
        color_continuous_scale="Viridis",
        title="Sales Distribution by Sub-Category",
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Sales by State (Bar Chart)
    st.subheader(f"Top {top_n} States by Sales")
    sales_by_state = filtered_df.groupby("State")["Sales"].sum().nlargest(top_n).reset_index()
    fig5 = px.bar(
        sales_by_state,
        x="State",
        y="Sales",
        title=f"Top {top_n} States by Sales",
        color="Sales",
        color_continuous_scale="Plasma",
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Sales by City (Bar Chart)
    st.subheader(f"Top {top_n} Cities by Sales")
    sales_by_city = filtered_df.groupby("City")["Sales"].sum().nlargest(top_n).reset_index()
    fig6 = px.bar(
        sales_by_city,
        x="City",
        y="Sales",
        title=f"Top {top_n} Cities by Sales",
        color="Sales",
        color_continuous_scale="Inferno",
    )
    st.plotly_chart(fig6, use_container_width=True)

# Page 3: Profit Analysis
elif page == "Profit Analysis":
    st.title("💰 Profit Analysis")
    st.markdown("Analyze profit trends and performance across categories, regions, and customer segments.")

    # Profit by Region (Bar Chart)
    st.subheader("Profit by Region")
    profit_by_region = filtered_df.groupby("Region")["Profit"].sum().reset_index()
    fig7 = px.bar(
        profit_by_region,
        x="Region",
        y="Profit",
        title="Profit by Region",
        color="Region",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    st.plotly_chart(fig7, use_container_width=True)

    # Profit vs Sales (Scatter Plot)
    st.subheader("Profit vs Sales")
    fig8 = px.scatter(
        filtered_df,
        x="Sales",
        y="Profit",
        color="Category",
        size="Quantity",
        hover_name="Sub-Category",
        title="Profit vs Sales by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig8, use_container_width=True)

# Page 4: Geographical Analysis
elif page == "Geographical Analysis":
    st.title("🌍 Geographical Analysis")
    st.markdown("Explore sales and profit performance across regions and states.")

    # Sales by State (Choropleth Map)
    st.subheader("Sales by State (Choropleth Map)")
    sales_by_state = filtered_df.groupby("State")["Sales"].sum().reset_index()
    fig9 = px.choropleth(
        sales_by_state,
        locations="State",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        title="Sales by State (USA)",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig9, use_container_width=True)

    # Profit by State (Choropleth Map)
    st.subheader("Profit by State (Choropleth Map)")
    profit_by_state = filtered_df.groupby("State")["Profit"].sum().reset_index()
    fig10 = px.choropleth(
        profit_by_state,
        locations="State",
        locationmode="USA-states",
        color="Profit",
        scope="usa",
        title="Profit by State (USA)",
        color_continuous_scale="Greens",
    )
    st.plotly_chart(fig10, use_container_width=True)

# Page 5: Sales Representative Analysis
elif page == "Sales Rep Analysis":
    st.title("🧑‍💼 Sales Representative Analysis")
    st.markdown("Analyze individual performance of sales representatives.")

    # Check if Sales Rep column exists
    if "SalesRep" in df.columns:
        # Sidebar filter for Sales Rep
        sales_reps = st.sidebar.multiselect("Select Sales Rep", df["SalesRep"].unique(), default=df["SalesRep"].unique())

        # Apply Sales Rep filter
        sales_rep_df = filtered_df[filtered_df["SalesRep"].isin(sales_reps)]

        # KPIs for Sales Reps
        st.subheader("Key Metrics for Sales Reps")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sales", f"SAR {sales_rep_df['Sales'].sum():,.2f}")
        with col2:
            st.metric("Total Profit", f"SAR {sales_rep_df['Profit'].sum():,.2f}")
        with col3:
            st.metric("Average Discount", f"{sales_rep_df['Discount'].mean():.2%}")

        # Top Sales Reps by Sales
        st.subheader(f"Top {top_n} Sales Representatives by Sales")
        top_sales_reps = sales_rep_df.groupby("SalesRep")["Sales"].sum().nlargest(top_n).reset_index()
        fig_sr1 = px.bar(
            top_sales_reps,
            x="SalesRep",
            y="Sales",
            title=f"Top {top_n} Sales Reps by Sales",
            color="Sales",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_sr1, use_container_width=True)

        # Top Sales Reps by Profit
        st.subheader(f"Top {top_n} Sales Representatives by Profit")
        top_profit_reps = sales_rep_df.groupby("SalesRep")["Profit"].sum().nlargest(top_n).reset_index()
        fig_sr2 = px.bar(
            top_profit_reps,
            x="SalesRep",
            y="Profit",
            title=f"Top {top_n} Sales Reps by Profit",
            color="Profit",
            color_continuous_scale="Plasma",
        )
        st.plotly_chart(fig_sr2, use_container_width=True)

        # Top Sales Reps by Bonus
        st.subheader(f"Top {top_n} Sales Representatives by Bonus")
        top_bonus_reps = sales_rep_df.groupby("SalesRep")["Bonus"].sum().nlargest(top_n).reset_index()
        fig_sr3 = px.bar(
            top_bonus_reps,
            x="SalesRep",
            y="Bonus",
            title=f"Top {top_n} Sales Reps by Bonus",
            color="Bonus",
            color_continuous_scale="Inferno",
        )
        st.plotly_chart(fig_sr3, use_container_width=True)
    else:
        st.warning("No 'Sales Rep' column found in the dataset.")

# Page 6: Send Notifications
elif page == "Send Notifications":
    st.title("📨 Send Notifications")
    st.markdown("Send SMS or email notifications to customers with their bonus and other information.")

    # Check if Mobile and email columns exist
    if "Mobile" not in df.columns:
        st.error("The dataset must contain 'Mobile' and 'email' columns to send notifications.")
    else:
        # Select notification type
        notification_type = st.radio("Select Notification Type", ["SMS", "Email"])

        # Customize message
        st.subheader("Customize Message")
        message = st.text_area("Enter your message", "Dear Customer, your bonus for this month is SAR {bonus}. Thank you for your continued support!")

        # Send SMS via Twilio
        if notification_type == "SMS":
            st.subheader("Send SMS")
            twilio_account_sid = st.text_input("Twilio Account SID")
            twilio_auth_token = st.text_input("Twilio Auth Token", type="password")
            twilio_phone_number = st.text_input("Twilio Phone Number")

            if st.button("Send SMS"):
                if not twilio_account_sid or not twilio_auth_token or not twilio_phone_number:
                    st.error("Please provide Twilio credentials.")
                else:
                    client = Client(twilio_account_sid, twilio_auth_token)
                    for index, row in filtered_df.iterrows():
                        try:
                            bonus = row["Bonus"]
                            Mobile = row["Mobile"]
                            personalized_message = message.format(bonus=bonus)
                            message = client.messages.create(
                                body=personalized_message,
                                from_=twilio_phone_number,
                                to=Mobile
                            )
                            st.success(f"SMS sent to {Mobile} successfully!")
                        except Exception as e:
                            st.error(f"Failed to send SMS to {Mobile}: {e}")

        # Send Email via SMTP
        elif notification_type == "Email":
            st.subheader("Send Email")
            smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", 587)
            smtp_username = st.text_input("SMTP Username")
            smtp_password = st.text_input("SMTP Password", type="password")

            if st.button("Send Email"):
                if not smtp_username or not smtp_password:
                    st.error("Please provide SMTP credentials.")
                else:
                    for index, row in filtered_df.iterrows():
                        try:
                            bonus = row["Bonus"]
                            email = row["email"]
                            personalized_message = message.format(bonus=bonus)

                            msg = MIMEMultipart()
                            msg["From"] = smtp_username
                            msg["To"] = email
                            msg["Subject"] = "Your Bonus Information"
                            msg.attach(MIMEText(personalized_message, "plain"))

                            server = smtplib.SMTP(smtp_server, smtp_port)
                            server.starttls()
                            server.login(smtp_username, smtp_password)
                            server.sendmail(smtp_username, email, msg.as_string())
                            server.quit()
                            st.success(f"Email sent to {email} successfully!")
                        except Exception as e:
                            st.error(f"Failed to send email to {email}: {e}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Plotly.")