import streamlit as st

# Set page title and layout configurations
st.set_page_config(page_title="Streamlit Calculator", page_icon="🧮", layout="centered")

st.title("🧮 Web Calculator App")
st.write("A clean math calculator running entirely in your browser via Streamlit.")
st.markdown("---")

# Layout columns for numbers
col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("Enter first number:", value=0.0, format="%f")

with col2:
    num2 = st.number_input("Enter second number:", value=0.0, format="%f")

# Dropdown selection menu for operators
operation = st.selectbox(
    "Choose an operation:",
    ("Addition (+)", "Subtraction (-)", "Multiplication (*)", "Division (/)")
)

st.markdown("### Result:")

# Computation Logic
if st.button("Calculate", type="primary"):
    if operation == "Addition (+)":
        result = num1 + num2
        st.success(f"**Result:** {num1} + {num2} = **{result}**")
        
    elif operation == "Subtraction (-)":
        result = num1 - num2
        st.success(f"**Result:** {num1} - {num2} = **{result}**")
        
    elif operation == "Multiplication (*)":
        result = num1 * num2
        st.success(f"**Result:** {num1} × {num2} = **{result}**")
        
    elif operation == "Division (/)":
        if num2 == 0:
            st.error("Error: Division by zero is not allowed.")
        else:
            result = num1 / num2
            st.success(f"**Result:** {num1} ÷ {num2} = **{result}**")