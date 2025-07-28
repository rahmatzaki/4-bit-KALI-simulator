import streamlit as st

def create_partition(rows=7, cols=3):
    return [["" for _ in range(cols)] for _ in range(rows)]

def init_partitions():
    partitions = {}
    for r in range(2):
        for c in range(15):
            if c == 0:
                partitions[(r, c)] = create_partition(7, 5)
            else:
                partitions[(r, c)] = create_partition(7, 3)
    return partitions

# All core simulation functions go here...
# [PLACEHOLDER]

def render_partition_table(partitions, stage_name):
    st.subheader(stage_name)
    for r in range(2):
        cols = st.columns(15)
        for c in range(15):
            with cols[c]:
                cell_data = partitions.get((r, c), [["." for _ in range(3)] for _ in range(7)])
                cell_str = "\n".join(
                    " ".join(str(cell) if cell else "." for cell in row)
                    for row in cell_data
                )
                st.text(cell_str)

def run_simulation(a_str, b_str):
    a_bits = [int(c) for c in a_str.zfill(4)]
    b_bits = [int(c) for c in b_str.zfill(4)]
    partitions = init_partitions()

    # STAGES - call each one and render results
   def init_partitions():
    partitions = {}
    for r in range(2):
        for c in range(15):
            if c == 0:
                partitions[(r, c)] = create_partition(7, 5)
            else:
                partitions[(r, c)] = create_partition(7, 3)
    return partitions


def str_to_bits(s):
    return [int(c) for c in s.zfill(4)]


def invert_bits(bits):
    return [1 - b for b in bits]


def stage_inversion(a_bits, b_bits, partitions):
    not_a = invert_bits(a_bits)
    not_b = invert_bits(b_bits)

    # Correct mapping: a3 in col1, a2 in col2, a1 in col3, a0 in col4
    partitions[(0, 0)][0][1] = str(not_a[0])
    partitions[(0, 0)][1][1] = str(not_a[0])
    partitions[(0, 0)][2][1] = str(not_a[0])
    partitions[(1, 0)][0][1] = str(not_a[0])

    partitions[(0, 0)][0][2] = str(not_a[1])
    partitions[(0, 0)][1][2] = str(not_a[1])
    partitions[(0, 0)][2][2] = str(not_a[1])
    partitions[(1, 0)][0][2] = str(not_a[1])

    partitions[(0, 0)][0][3] = str(not_a[2])
    partitions[(0, 0)][1][3] = str(not_a[2])
    partitions[(0, 0)][2][3] = str(not_a[2])
    partitions[(1, 0)][0][3] = str(not_a[2])

    partitions[(0, 0)][0][4] = str(not_a[3])
    partitions[(0, 0)][1][4] = str(not_a[3])
    partitions[(0, 0)][2][4] = str(not_a[3])
    partitions[(1, 0)][0][4] = str(not_a[3])

    for idx, nb in enumerate(not_b[::-1]):
        if idx < 3:
            partitions[(0, 0)][idx][0] = str(nb)
        else:
            partitions[(1, 0)][0][0] = str(nb)


def get_bit(partitions, r, c, row, col):
    try:
        return int(partitions[(r, c)][row][col])
    except:
        return 0


def stage_partial_product(partitions):
    a_locs = {
        0: (0, 0, 0, 4),
        1: (0, 0, 0, 3),
        2: (0, 0, 0, 2),
        3: (0, 0, 0, 1),
    }
    b_locs = {
        0: (0, 0, 0, 0),
        1: (0, 0, 1, 0),
        2: (0, 0, 2, 0),
        3: (1, 0, 0, 0),
    }
    for i in range(4):
        for j in range(4):
            a_val = get_bit(partitions, *a_locs[i])
            b_val = get_bit(partitions, *b_locs[j])
            pp = 1 if (a_val | b_val) == 0 else 0

            row = j if j < 3 else 0
            pr = 0 if j < 3 else 1
            col_base = 1 + 2 * (3 - i)

            for offset in range(2):
                partitions[(pr, col_base + offset)][row][0] = str(pp)


def shift_stage(partitions, stage):
    def shift_cell(pr, pc, row, col, new_pc):
        val = partitions[(pr, pc)][row][col]
        if val != "":
            partitions[(pr, pc)][row][col] = ""
            partitions[(pr, new_pc)][row][col] = val

    for pr in range(1):
        for i in range(12, 0, -1):
            if stage == 2:
                for row in [0, 1, 2]:
                    shift_cell(pr, i, row, 0, i + 2)
            elif stage == 4:
                for row in [0, 1]:
                    shift_cell(pr, i, row, 0, i + 2)
            elif stage == 6:
                row = 0
                shift_cell(pr, i, row, 0, i + 2)

def stage_fa(partitions):
    def xor3(a, b, c):
        return a ^ b ^ c

    def nor(a, b):
        return int(not (a or b))

    def compute_fa(a, b, cin):
        s = xor3(a, b, cin)
        cout = nor(nor(a, b), nor(b, cin) or nor(a, cin))
        return s, cout

    for pr in range(2):
        for pc in range(1, 15):
            a = get_bit(partitions, pr, pc, 0, 0)
            b = get_bit(partitions, pr, pc, 1, 0)
            cin = get_bit(partitions, pr, pc, 2, 0)
            s, cout = compute_fa(a, b, cin)

            partitions[(pr, pc)] = create_partition(7, 3)

            if pc % 2 == 0:
                partitions[(pr, pc)][4][0] = str(s)
            else:
                partitions[(pr, pc)][6][0] = str(cout)

def relocate_for_next_fa(partitions):
    for pc in range(1, 15):
        val = partitions[(0, pc)][4][0]
        if val:
            partitions[(0, pc - 1)][4][0] = val

    for pc in range(2, 15):
        val = partitions[(0, pc)][6][0]
        if val:
            partitions[(0, pc)][6][0] = ""
            partitions[(0, pc - 1)][6][0] = val
            partitions[(0, pc - 2)][6][0] = val

    for pc in range(15):
        val = partitions[(1, pc)][4][0]
        if val:
            partitions[(0, pc)][0][0] = val
            if pc > 0:
                partitions[(0, pc - 1)][0][0] = val
            partitions[(1, pc)][4][0] = ""

    for pc in range(15):
        partitions[(1, pc)][6][0] = ""

def second_fa_stage(partitions):
    def nor(x, y):
        return int(not (x or y))

    def compute_fa(a, b, cin):
        s = a ^ b ^ cin
        cout = nor(nor(a, b), nor(b, cin) or nor(a, cin))
        return s, cout

    for pc in range(1, 15):
        a = int(partitions[(0, pc)][0][0]) if partitions[(0, pc)][0][0] else 0
        b = int(partitions[(0, pc)][4][0]) if partitions[(0, pc)][4][0] else 0
        cin = int(partitions[(0, pc)][6][0]) if partitions[(0, pc)][6][0] else 0

        s, cout = compute_fa(a, b, cin)

        # Clear all input cells
        partitions[(0, pc)] = [["" for _ in range(3)] for _ in range(7)]

        if pc % 2 == 0:
            partitions[(0, pc)][0][0] = str(s)
        else:
            partitions[(0, pc)][1][0] = str(cout)

def brent_kung_stage0(partitions):
    def xor(a, b):
        return a ^ b

    def and_gate(a, b):
        return a & b

    for i in range(7):
        even_pc = i * 2 + 2

        if even_pc == 14:
            partitions[(0, 14)][1][2] = "0"
            a = get_bit(partitions, 0, even_pc, 0, 0)
            partitions[(0, even_pc)][0][2] = str(a)
            partitions[(0, even_pc)][0][0] = ""
            continue

        odd_pc = i * 2 + 3
        output_pc = even_pc 

        a = get_bit(partitions, 0, even_pc, 0, 0)
        b = get_bit(partitions, 0, odd_pc, 1, 0)

        p = xor(a, b)
        g = and_gate(a, b)

        partitions[(0, output_pc)][0][2] = str(p)
        partitions[(0, output_pc)][1][2] = str(g)

        # Clear original input bits
        partitions[(0, even_pc)][0][0] = ""
        partitions[(0, odd_pc)][1][0] = ""

def brent_kung_stage1(partitions):
    def and_gate(a, b):
        return a & b

    def or_gate(a, b):
        return a | b

    pairs = [
        (14, 12),  # Bit 0 and Bit 1
        (10, 8),   # Bit 2 and Bit 3
        (6, 4),    # Bit 4 and Bit 5
    ]

    for hi, lo in pairs:
        # Get p and g from appropriate cells
        p_lo = get_bit(partitions, 0, hi, 0, 2)
        p_hi = get_bit(partitions, 0, lo, 0, 2)

        g_lo = get_bit(partitions, 0, hi, 1, 2)
        g_hi = get_bit(partitions, 0, lo, 1, 2)

        # Compute new combined p and g
        p_out = and_gate(p_hi, p_lo)
        g_out = or_gate(g_hi, and_gate(p_hi, g_lo))

        # Store results into hi partition (same column)
        partitions[(0, lo)][2][1] = str(p_out)  # new p
        partitions[(0, lo)][3][1] = str(g_out)  # new g

def brent_kung_stage2(partitions):
    def and_gate(a, b):
        return a & b

    def or_gate(a, b):
        return a | b

    # Pair 1: column 2 (low), column 4 (high)
    p_hi = get_bit(partitions, 0, 2, 0, 2)
    g_hi = get_bit(partitions, 0, 2, 1, 2)
    p_lo = get_bit(partitions, 0, 4, 2, 1)
    g_lo = get_bit(partitions, 0, 4, 3, 1)

    p_out = and_gate(p_hi, p_lo)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))

    partitions[(0, 2)][4][0] = str(p_out)
    partitions[(0, 2)][5][0] = str(g_out)

    # Pair 2: column 8 (low), column 12 (high)
    p_hi = get_bit(partitions, 0, 8, 2, 1)
    g_hi = get_bit(partitions, 0, 8, 3, 1)
    p_lo = get_bit(partitions, 0, 12, 2, 1)
    g_lo = get_bit(partitions, 0, 12, 3, 1)

    p_out = and_gate(p_hi, p_lo)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))

    partitions[(0, 8)][4][0] = str(p_out)
    partitions[(0, 8)][5][0] = str(g_out)

def brent_kung_final_propagation(partitions):
    def and_gate(a, b):
        return a & b

    def or_gate(a, b):
        return a | b

    # Stage 3: col 2 + col 8 → result to col 1
    p_hi = get_bit(partitions, 0, 2, 4, 0)
    g_hi = get_bit(partitions, 0, 2, 5, 0)
    p_lo = get_bit(partitions, 0, 8, 4, 0)
    g_lo = get_bit(partitions, 0, 8, 5, 0)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))
    partitions[(0, 1)][2][2] = str(g_out)

    # Stage 4: col 4 + col 8 → result to col 3
    p_hi = get_bit(partitions, 0, 4, 2, 1)
    g_hi = get_bit(partitions, 0, 4, 3, 1)
    p_lo = get_bit(partitions, 0, 8, 4, 0)
    g_lo = get_bit(partitions, 0, 8, 5, 0)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))
    partitions[(0, 3)][2][2] = str(g_out)

    # Stage 5a: col 6 + col 8 → result to col 6
    p_hi = get_bit(partitions, 0, 6, 0, 2)
    g_hi = get_bit(partitions, 0, 6, 1, 2)
    p_lo = get_bit(partitions, 0, 8, 4, 0)
    g_lo = get_bit(partitions, 0, 8, 5, 0)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))
    partitions[(0, 5)][2][2] = str(g_out)

    # Stage 5b: col 10 + col 12 → result to col 9
    p_hi = get_bit(partitions, 0, 10, 0, 2)
    g_hi = get_bit(partitions, 0, 10, 1, 2)
    p_lo = get_bit(partitions, 0, 12, 2, 1)
    g_lo = get_bit(partitions, 0, 12, 3, 1)
    g_out = or_gate(g_hi, and_gate(p_hi, g_lo))
    partitions[(0, 9)][2][2] = str(g_out)

def final_adder(partitions):
    def xor(a, b):
        return a ^ b

    # r0
    r0 = get_bit(partitions, 0, 14, 0, 2)
    partitions[(1, 14)][0][0] = str(r0)

    # r1
    a = get_bit(partitions, 0, 12, 0, 2)
    b = get_bit(partitions, 0, 14, 1, 2)
    partitions[(1, 12)][0][0] = str(xor(a, b))

    # r2
    a = get_bit(partitions, 0, 10, 0, 2)
    b = get_bit(partitions, 0, 12, 3, 1)
    partitions[(1, 10)][0][0] = str(xor(a, b))

    # r3
    a = get_bit(partitions, 0, 8, 0, 2)
    b = get_bit(partitions, 0, 9, 2, 2)
    partitions[(1, 8)][0][0] = str(xor(a, b))

    # r4
    a = get_bit(partitions, 0, 6, 0, 2)
    b = get_bit(partitions, 0, 8, 5, 0)
    partitions[(1, 6)][0][0] = str(xor(a, b))

    # r5
    a = get_bit(partitions, 0, 4, 0, 2)
    b = get_bit(partitions, 0, 5, 2, 2)
    partitions[(1, 4)][0][0] = str(xor(a, b))

    # r6
    a = get_bit(partitions, 0, 2, 0, 2)
    b = get_bit(partitions, 0, 3, 2, 2)
    partitions[(1, 2)][0][0] = str(xor(a, b))

    # r7
    r7 = get_bit(partitions, 0, 1, 2, 2)
    partitions[(1, 1)][0][0] = str(r7)

# Streamlit UI
st.title("4-bit KALI Brent-Kung Simulation (Web Version)")
a = st.text_input("Input A (4-bit binary)", "1011")
b = st.text_input("Input B (4-bit binary)", "1001")

if st.button("Run Simulation"):
    run_simulation(a, b)
