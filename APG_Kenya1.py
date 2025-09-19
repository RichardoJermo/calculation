import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# Helper Functions
# ======================

def calc_costs(value, rate, duration_years):
    """Calculate annual and total costs based on value, bank rate and duration."""
    annual = value * rate
    total = annual * duration_years
    return annual, total

def format_currency(num):
    return f"${num:,.0f}"

# ======================
# Page Setup
# ======================
st.set_page_config(page_title="Insurance Guarantee Cost Calculator", layout="wide")
st.title("📊 Insurance Guarantee Cost Calculator")
st.markdown("Compare costs between original single-project and recommended phased structures")

# ======================
# Input Section
# ======================
st.header("Project Parameters")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Structure Parameters")
    total_contract_value = st.number_input("Total Contract Value ($)", min_value=0.0, value=320_000_000.0, step=1_000_000.0)
    advance_payment_percent_orig = st.slider("Advance Payment Percentage (%)", 0.0, 100.0, 40.0) / 100
    pg_percent_orig = st.slider("Performance Guarantee Percentage (%)", 0.0, 100.0, 30.0) / 100
    construction_duration_orig = st.number_input("Construction Duration (months)", 1, 24)
    dlp_duration_orig = st.number_input("Defects Liability Period (months)", 0, 12)

with col2:
    st.subheader("Phased Structure Parameters")
    num_phases = st.number_input("Number of Phases", 1, 5)
    pg_percent_phased = st.slider("Phased PG Percentage (%)", 0.0, 100.0, 10.0) / 100
    construction_duration_phased = st.number_input("Phase Construction Duration (months)", 1, 6)
    dlp_duration_phased = st.number_input("Phase DLP Duration (months)", 0, 12)
    bank_fee_rate = st.slider("Bank Fee Rate (% annually)", 0.1, 10.0, 1.0) / 100

# ======================
# Calculations
# ======================
# Values
apg_value_orig = total_contract_value * advance_payment_percent_orig
pg_value_orig = total_contract_value * pg_percent_orig

phase_contract_value = total_contract_value / num_phases
apg_value_phased = phase_contract_value * advance_payment_percent_orig
pg_value_phased = phase_contract_value * pg_percent_phased

# Durations (years)
apg_duration_orig = construction_duration_orig / 12
pg_duration_orig = (construction_duration_orig + dlp_duration_orig) / 12
apg_duration_phased = construction_duration_phased / 12
pg_duration_phased = (construction_duration_phased + dlp_duration_phased) / 12

# Costs
apg_annual_cost_orig, apg_total_cost_orig = calc_costs(apg_value_orig, bank_fee_rate, apg_duration_orig)
pg_annual_cost_orig, pg_total_cost_orig = calc_costs(pg_value_orig, bank_fee_rate, pg_duration_orig)
total_cost_orig = apg_total_cost_orig + pg_total_cost_orig

apg_annual_cost_phased, apg_cost_per_phase = calc_costs(apg_value_phased, bank_fee_rate, apg_duration_phased)
pg_annual_cost_phased, pg_cost_per_phase = calc_costs(pg_value_phased, bank_fee_rate, pg_duration_phased)

apg_total_cost_phased = apg_cost_per_phase * num_phases
pg_total_cost_phased = pg_cost_per_phase * num_phases
total_cost_phased = apg_total_cost_phased + pg_total_cost_phased

# Savings
apg_savings = apg_total_cost_orig - apg_total_cost_phased
pg_savings = pg_total_cost_orig - pg_total_cost_phased
total_savings = total_cost_orig - total_cost_phased

# Credit line
credit_line_orig = apg_value_orig
credit_line_phased = apg_value_phased + pg_value_phased
credit_line_savings = credit_line_orig - credit_line_phased

# ======================
# Results - Summary Table
# ======================
st.header("Results")

summary_data = {
    "Metric": [
        "APG Value", 
        "PG Value", 
        "APG Duration (years)", 
        "PG Duration (years)",
        "APG Annual Cost",
        "PG Annual Cost",
        "APG Total Cost",
        "PG Total Cost",
        "Total Cost",
        "Credit Line Required"
    ],
    "Original Structure": [
        format_currency(apg_value_orig),
        format_currency(pg_value_orig),
        f"{apg_duration_orig:.1f}",
        f"{pg_duration_orig:.1f}",
        format_currency(apg_annual_cost_orig),
        format_currency(pg_annual_cost_orig),
        format_currency(apg_total_cost_orig),
        format_currency(pg_total_cost_orig),
        format_currency(total_cost_orig),
        format_currency(credit_line_orig)
    ],
    "Phased Structure": [
        f"{format_currency(apg_value_phased)} per phase",
        f"{format_currency(pg_value_phased)} per phase",
        f"{apg_duration_phased:.1f} per phase",
        f"{pg_duration_phased:.1f} per phase",
        f"{format_currency(apg_annual_cost_phased)} per phase",
        f"{format_currency(pg_annual_cost_phased)} per phase",
        format_currency(apg_total_cost_phased),
        format_currency(pg_total_cost_phased),
        format_currency(total_cost_phased),
        f"{format_currency(credit_line_phased)} at any time"
    ],
    "Savings/Improvement": [
        "", "", "", "", "", "",
        format_currency(apg_savings),
        format_currency(pg_savings),
        format_currency(total_savings),
        f"{format_currency(credit_line_savings)} freed"
    ]
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ======================
# Charts
# ======================
# Cost comparison
cost_df = pd.DataFrame({
    "Cost Type": ["APG", "PG", "Total"],
    "Original Structure": [apg_total_cost_orig, pg_total_cost_orig, total_cost_orig],
    "Phased Structure": [apg_total_cost_phased, pg_total_cost_phased, total_cost_phased]
})
fig = px.bar(cost_df.melt(id_vars="Cost Type", var_name="Structure", value_name="Cost"),
             x="Cost Type", y="Cost", color="Structure", barmode="group",
             title="Cost Comparison: Original vs Phased")
st.plotly_chart(fig, use_container_width=True)

# Savings chart
savings_df = pd.DataFrame({
    "Savings Type": ["APG Savings", "PG Savings", "Total Savings"],
    "Amount": [apg_savings, pg_savings, total_savings]
})
fig2 = px.bar(savings_df, x="Savings Type", y="Amount", title="Savings from Phased Structure")
st.plotly_chart(fig2, use_container_width=True)

# Credit line
credit_df = pd.DataFrame({
    "Structure": ["Original", "Phased"],
    "Credit Line Required": [credit_line_orig, credit_line_phased]
})
fig3 = px.bar(credit_df, x="Structure", y="Credit Line Required", title="Credit Line Requirements")
st.plotly_chart(fig3, use_container_width=True)

# ======================
# Detailed Calculations
# ======================
st.header("Detailed Calculations")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Original Structure")
    st.markdown(f"""
- APG Value: {format_currency(total_contract_value)} × {advance_payment_percent_orig*100:.1f}% = **{format_currency(apg_value_orig)}**  
- PG Value: {format_currency(total_contract_value)} × {pg_percent_orig*100:.1f}% = **{format_currency(pg_value_orig)}**  
- APG Duration: {construction_duration_orig} ÷ 12 = **{apg_duration_orig:.1f} years**  
- PG Duration: ({construction_duration_orig}+{dlp_duration_orig}) ÷ 12 = **{pg_duration_orig:.1f} years**  
- APG Total Cost: {format_currency(apg_value_orig)} × {bank_fee_rate*100:.1f}% × {apg_duration_orig:.1f} = **{format_currency(apg_total_cost_orig)}**  
- PG Total Cost: {format_currency(pg_value_orig)} × {bank_fee_rate*100:.1f}% × {pg_duration_orig:.1f} = **{format_currency(pg_total_cost_orig)}**
""")

with col4:
    st.subheader("Phased Structure")
    st.markdown(f"""
- Phase Contract Value: {format_currency(total_contract_value)} ÷ {num_phases} = **{format_currency(phase_contract_value)}**  
- APG per Phase: {format_currency(phase_contract_value)} × {advance_payment_percent_orig*100:.1f}% = **{format_currency(apg_value_phased)}**  
- PG per Phase: {format_currency(phase_contract_value)} × {pg_percent_phased*100:.1f}% = **{format_currency(pg_value_phased)}**  
- APG Total Cost: {format_currency(apg_value_phased)} × {bank_fee_rate*100:.1f}% × {apg_duration_phased:.1f} × {num_phases} = **{format_currency(apg_total_cost_phased)}**  
- PG Total Cost: {format_currency(pg_value_phased)} × {bank_fee_rate*100:.1f}% × {pg_duration_phased:.1f} × {num_phases} = **{format_currency(pg_total_cost_phased)}**
""")

# ======================
# Conclusion
# ======================
st.header("Conclusion")
st.success(f"""
**Direct Cost Savings: {format_currency(total_savings)}**  
**Credit Line Reduction: {format_currency(credit_line_savings)}** (from {format_currency(credit_line_orig)} to {format_currency(credit_line_phased)})  
**Improved cash flow** by requiring only {format_currency(credit_line_phased)} at any time instead of {format_currency(credit_line_orig)}
""")

# ======================
# Download CSV
# ======================
csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Results as CSV", csv, "guarantee_cost_calculator_results.csv", "text/csv")
