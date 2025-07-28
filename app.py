import streamlit as st

def str_to_bits(s):
    return [int(c) for c in s.zfill(4)]

def invert_bits(bits):
    return [1 - b for b in bits]

def render_inversion(a_bits, b_bits):
    not_a = invert_bits(a_bits)
    not_b = invert_bits(b_bits)

    output = []
    output.append(f"Inverted A: {''.join(str(b) for b in not_a)}")
    output.append(f"Inverted B: {''.join(str(b) for b in not_b)}")
    return output

# Streamlit layout
st.title("4-bit KALI Simulator (Brent-Kung)")

a_input = st.text_input("Enter A (4-bit binary)", "1011")
b_input = st.text_input("Enter B (4-bit binary)", "1001")

if st.button("Run Simulation"):
    if len(a_input) > 4 or len(b_input) > 4 or not a_input.isdigit() or not b_input.isdigit():
        st.error("Please enter valid 4-bit binary values.")
    else:
        a_bits = str_to_bits(a_input)
        b_bits = str_to_bits(b_input)
        stage_output = render_inversion(a_bits, b_bits)
        for line in stage_output:
            st.text(line)
