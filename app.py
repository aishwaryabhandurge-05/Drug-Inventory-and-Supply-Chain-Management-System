import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Pharma Supply Chain System",
    layout="wide"
)

# --------------------------------------------------
# LOGIN CREDENTIALS
# --------------------------------------------------

USERNAME = "admin"
PASSWORD = "pharma123"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("final_pharma_supply_chain_dataset.csv")

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

def login_page():

    st.markdown("""
    <style>

    .stApp {
        background-image: url("https://images.unsplash.com/photo-1603398938378-e54eab446dde");
        background-size: cover;
        background-position: center;
    }

    .login-container {
        background: rgba(0,0,0,0.80);
        padding: 45px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0px 0px 30px rgba(0,0,0,0.6);
    }

    .title {
        font-size: 42px; 
        font-weight: bold; 
        color: #ffffff;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8); 
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 20px;
        color: #f1f1f1;
        margin-bottom: 25px;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.7);
    }
    
    /* Username & Password labels */ 
    label { 
        font-size: 22px !important; 
        color: black !important;
        font-weight: bold !important; 
    }
    
    /* Input fields */ 
    div[data-baseweb="input"] input { 
        height: 50px !important; 
        font-size: 18px !important; 
    } 
                
    div[data-baseweb="base-input"] input { 
        height: 50px !important; 
        font-size: 18px !important; 
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown('<div class="login-box">', unsafe_allow_html=True) 
        
        st.markdown('<div class="title">💊 Pharma SCM</div>', unsafe_allow_html=True) 
        st.markdown('<div class="subtitle">Inventory & Supply Chain Dashboard</div>', unsafe_allow_html=True) 
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password") 
        
        if st.button("Login", use_container_width=True): 
            
            if username == USERNAME and password == PASSWORD: 
                st.session_state.logged_in = True 
                st.rerun() 
            else: 
                st.error("Invalid username or password") 
                
        st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------

def main_app():

    df = load_data()

    st.sidebar.title("💊 Pharma SCM")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard Overview",
            "Inventory Management",
            "Supply Chain Tracking",
            "Cold Chain Monitoring"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ======================================================
# PAGE 1: DASHBOARD OVERVIEW
# ======================================================

    if page == "Dashboard Overview":

        st.title("📊 System Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Medicines", df["product_name"].nunique())
        col2.metric("Total Shipments", df["shipment_id"].nunique())
        col3.metric("Avg Stock Level", int(df["stock_level"].mean()))
        col4.metric("Risk Records", df[df["anomaly_flag"] == 1].shape[0])

        st.markdown("---")

        st.subheader("High-Level Description")

        st.write(
        """
        This system monitors pharmaceutical inventory and supply chain operations.
        It integrates inventory tracking, demand forecasting, shipment monitoring,
        cold-chain compliance, and operational risk detection.
        """
        )

        st.subheader("📈 Inventory & Risk Insights")

        colA, colB = st.columns(2)

        with colA:

            st.markdown("**Top 10 Medicines by Stock Level**")

            top_stock = (
                df.groupby("product_name")["stock_level"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_stock)

        with colB:

            st.markdown("**Risk vs Normal Records**")

            risk_counts = df["anomaly_flag"].value_counts()
            risk_counts = risk_counts.rename({0: "Normal", 1: "Risk"})

            fig, ax = plt.subplots()

            ax.bar(
                risk_counts.index,
                risk_counts.values,
                color=["#2ca02c", "#d62728"]
            )

            ax.set_ylabel("Number of Records")
            ax.set_xlabel("Status")
            ax.set_title("Operational Risk Distribution")

            st.pyplot(fig)

# ======================================================
# PAGE 2: INVENTORY MANAGEMENT
# ======================================================

    elif page == "Inventory Management":

        st.title("📦 Inventory Management")

        col1, col2 = st.columns(2)

        with col1:
            pharmacy_filter = st.selectbox(
                "Select Pharmacy",
                ["All"] + sorted(df["pharmacy_name"].unique())
            )

        with col2:
            category_filter = st.selectbox(
                "Select Product Category",
                ["All"] + sorted(df["product_category"].unique())
            )

        filtered_df = df.copy()

        if pharmacy_filter != "All":
            filtered_df = filtered_df[
                filtered_df["pharmacy_name"] == pharmacy_filter
            ]

        if category_filter != "All":
            filtered_df = filtered_df[
                filtered_df["product_category"] == category_filter
            ]

        st.markdown("---")

        st.subheader("🔍 Search Medicines by Name or Use")

        search_query = st.text_input(
            "Search medicine (e.g. painkiller,antacid, thyroid, antihistamine)"
        )

        if search_query:

            search_query = search_query.lower()

            search_df = filtered_df[
                filtered_df["product_name"].str.lower().str.contains(search_query, na=False)
                |
                filtered_df["product_category"].str.lower().str.contains(search_query, na=False)
            ]

            if search_df.empty:
                st.warning("No medicines found for this search.")
            else:
                st.dataframe(search_df, use_container_width=True)

        st.markdown("---")

        st.subheader("📊 Inventory Status Summary")

        summary_data = {
            "Low Stock": (
                filtered_df["stock_level"] < filtered_df["stock_threshold_min"]
            ).sum(),
            "Normal Stock": (
                (filtered_df["stock_level"] >= filtered_df["stock_threshold_min"]) &
                (filtered_df["stock_level"] <= filtered_df["stock_threshold_max"])
            ).sum(),
            "Excess Stock": (
                filtered_df["stock_level"] > filtered_df["stock_threshold_max"]
            ).sum()
        }

        st.bar_chart(summary_data)

        # LOW STOCK TABLE

        st.subheader("⚠️ Low Stock Medicines")

        low_stock_df = filtered_df[
            filtered_df["stock_level"] < filtered_df["stock_threshold_min"]
        ][[
            "product_name",
            "pharmacy_name",
            "stock_level",
            "stock_threshold_min",
            "reorder_quantity_suggested"
        ]]

        st.dataframe(low_stock_df, use_container_width=True)

        # EXCESS STOCK TABLE

        st.subheader("📦 Excess Stock Medicines")

        excess_stock_df = filtered_df[
            filtered_df["stock_level"] > filtered_df["stock_threshold_max"]
        ][[
            "product_name",
            "pharmacy_name",
            "stock_level",
            "stock_threshold_max"
        ]]

        st.dataframe(excess_stock_df, use_container_width=True)

# ======================================================
# PAGE 3: SUPPLY CHAIN TRACKING
# ======================================================

    elif page == "Supply Chain Tracking":

        st.title("🚚 Supply Chain Tracking")

        st.subheader("Shipment Delay Overview")

        delayed_shipments = df[df["delivery_delay_days"] > 0]

        if delayed_shipments.empty:
            st.success("No delayed shipments found.")
        else:
            st.dataframe(delayed_shipments, use_container_width=True)

        st.markdown("---")

        st.subheader("📊 Delivery Delay Trend")

        delay_counts = (
            df[df["delivery_delay_days"] > 0]["delivery_delay_days"]
            .value_counts()
            .sort_index()
        )

        if not delay_counts.empty:

            fig, ax = plt.subplots()

            ax.plot(
                delay_counts.index,
                delay_counts.values,
                marker="o",
                color="#1f77b4"
            )

            ax.set_xlabel("Delivery Delay (Days)")
            ax.set_ylabel("Number of Shipments")

            st.pyplot(fig)

        st.markdown("---")

        st.subheader("✅ On-Time vs Delayed Shipment Performance")

        on_time_count = int((df["delivery_delay_days"] <= 0).sum())
        delayed_count = int((df["delivery_delay_days"] > 0).sum())

        fig, ax = plt.subplots()

        ax.pie(
            [on_time_count, delayed_count],
            labels=["On-Time", "Delayed"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#2ca02c", "#d62728"],
            wedgeprops=dict(width=0.4)
        )

        st.pyplot(fig)

        st.markdown("---")

        st.subheader("⏱️ Delay Severity Analysis")

        def delay_severity(days):
            if days <= 0:
                return "On-Time"
            elif days <= 2:
                return "Minor(1–2days)"
            elif days <= 5:
                return "Moderate(3–5days)"
            else:
                return "Severe(>5days)"

        severity_df = df.copy()
        severity_df["delay_severity"] = severity_df["delivery_delay_days"].apply(delay_severity)

        severity_counts = severity_df["delay_severity"].value_counts()

        fig, ax = plt.subplots()

        ax.bar(severity_counts.index, severity_counts.values)

        st.pyplot(fig)

  # Delay vs Transport Loss (HEATMAP)
    # --------------------------------------------------
        st.subheader("🔥 Delay vs Transport Loss Heatmap")

        heatmap_df = df[df["quantity_lost"] > 0][
            ["delivery_delay_days", "quantity_lost"]
    ]

        if heatmap_df.empty:
            st.info("Not enough data to generate heatmap.")
        else:
            heatmap_data = pd.crosstab(
                heatmap_df["delivery_delay_days"],
                heatmap_df["quantity_lost"]
            )

            fig, ax = plt.subplots(figsize=(8, 5))
            im = ax.imshow(
                heatmap_data,
                cmap="Reds",
                aspect="auto"
            )

            ax.set_xlabel("Quantity Lost")
            ax.set_ylabel("Delivery Delay (Days)")
            ax.set_title("Heatmap: Delivery Delay vs Transport Loss")

            plt.colorbar(im, ax=ax, label="Frequency")
        st.pyplot(fig)

# ======================================================
# PAGE 4: COLD CHAIN MONITORING
# ======================================================

    elif page == "Cold Chain Monitoring":

        st.title("❄️ Cold Chain Monitoring")

        cold_chain_df = df[df["is_temperature_sensitive"] == "Yes"]

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Cold-Chain Drugs", cold_chain_df.shape[0])

        col2.metric(
            "Temperature Violations",
            cold_chain_df[
                cold_chain_df["temperature_violation_flag"] == 1
            ].shape[0]
        )

        col3.metric(
            "Violation Rate (%)",
            round(
                cold_chain_df["temperature_violation_flag"].mean()*100,
                2
            )
        )

        st.subheader("🌡️ Transport Temperature Distribution")

        st.bar_chart(
            cold_chain_df["avg_transport_temp_c"]
            .round()
            .value_counts()
            .sort_index()
        )

# --------------------------------------------------
# RUN APP
# --------------------------------------------------

if st.session_state.logged_in:
    main_app()
else:
    login_page()
