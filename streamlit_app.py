import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

x = sp.symbols("x")

st.set_page_config(
    page_title="절댓값 두 개 포함 일차부등식",
    page_icon="📘",
    layout="wide",
)

st.title("📘 절댓값 두 개 포함 일차부등식 탐구")
st.markdown(
    """
이 앱은 고등학교 1학년 수학 수업에서 사용할 수 있는, **절댓값 두 개를 포함한 일차부등식** 학습 도구입니다.

- 왼쪽과 오른쪽 절댓값 식을 버튼과 선택 상자로 쉽게 만들 수 있습니다.
- 부등식의 해를 자동으로 계산하고, 그래프와 수직선으로 결과를 보여줍니다.
"""
)

if "a1" not in st.session_state:
    st.session_state.update(
        {
            "a1": 1,
            "b1": 1,
            "a2": 2,
            "b2": -4,
            "op": "+",
            "ineq": "<=",
            "rhs": 5,
        }
    )


def format_linear(a: int, b: int) -> str:
    if a == 0:
        return f"{b}"

    coeff = "" if abs(a) == 1 else str(abs(a))
    sign = "-" if a < 0 else ""
    term = f"{sign}{coeff}x"

    if b == 0:
        return term

    sign_b = "+" if b > 0 else "-"
    return f"{term} {sign_b} {abs(b)}"


def format_abs(a: int, b: int) -> str:
    return f"|{format_linear(a, b)}|"


def build_expression(a: int, b: int) -> sp.Expr:
    return a * x + b


def solution_intervals(solution):
    if solution == sp.S.EmptySet:
        return []
    if solution == sp.S.Reals:
        return [sp.Interval(-sp.oo, sp.oo)]
    if solution.is_Interval:
        return [solution]
    if solution.is_Union:
        return [arg for arg in solution.args if arg.is_Interval]
    return []


def plot_solution_line(solution, x_min, x_max):
    fig, ax = plt.subplots(figsize=(10, 1.5))
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-1, 1)
    ax.axhline(0, color="black", linewidth=1)
    ax.get_yaxis().set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position("center")

    ax.set_xticks(np.linspace(x_min, x_max, 9))
    ax.set_xticklabels([f"{t:.1f}" for t in np.linspace(x_min, x_max, 9)])
    ax.tick_params(axis="x", length=6)

    intervals = solution_intervals(solution)
    if solution == sp.S.Reals:
        ax.plot([x_min, x_max], [0, 0], color="red", linewidth=8)
        return fig

    if not intervals:
        return fig

    for interval in intervals:
        start = float(interval.start) if interval.start is not sp.S.NegativeInfinity else x_min
        end = float(interval.end) if interval.end is not sp.S.Infinity else x_max
        start = max(start, x_min)
        end = min(end, x_max)
        ax.plot([start, end], [0, 0], color="red", linewidth=8)
        left_marker = "white" if interval.left_open else "red"
        right_marker = "white" if interval.right_open else "red"
        ax.plot(start, 0, marker="o", color=left_marker, markeredgecolor="red", markersize=10)
        ax.plot(end, 0, marker="o", color=right_marker, markeredgecolor="red", markersize=10)

    return fig


st.subheader("1️⃣ 예제와 수식 선택")
with st.expander("빠른 예제 선택", expanded=True):
    c1, c2, c3 = st.columns(3)
    if c1.button("예제 1: |x+1| + |2x-4| <= 5"):
        st.session_state.update({"a1": 1, "b1": 1, "a2": 2, "b2": -4, "op": "+", "ineq": "<=", "rhs": 5})
    if c2.button("예제 2: |2x-3| - |x-2| >= 1"):
        st.session_state.update({"a1": 2, "b1": -3, "a2": 1, "b2": -2, "op": "-", "ineq": ">=", "rhs": 1})
    if c3.button("예제 3: |-x+2| + |x-5| > 4"):
        st.session_state.update({"a1": -1, "b1": 2, "a2": 1, "b2": -5, "op": "+", "ineq": ">", "rhs": 4})

st.markdown(
    "수식을 버튼과 선택 상자로 만들 수 있어요. 절댓값 내부의 계수와 상수를 선택한 뒤, 부등호와 우변 값을 정하세요."
)

st.subheader("2️⃣ 절댓값 부등식 만들기")
col1, col2, col3, col4 = st.columns(4)
with col1:
    a1 = st.selectbox("첫 번째 절댓값 계수 a₁", [-3, -2, -1, 1, 2, 3], index=[-3, -2, -1, 1, 2, 3].index(st.session_state["a1"]))
    b1 = st.slider("첫 번째 절댓값 상수 b₁", -10, 10, st.session_state["b1"], key="b1")
with col2:
    a2 = st.selectbox("두 번째 절댓값 계수 a₂", [-3, -2, -1, 1, 2, 3], index=[-3, -2, -1, 1, 2, 3].index(st.session_state["a2"]))
    b2 = st.slider("두 번째 절댓값 상수 b₂", -10, 10, st.session_state["b2"], key="b2")
with col3:
    op = st.selectbox("연산자", ["+", "-"], index=["+", "-"].index(st.session_state["op"]))
    ineq = st.selectbox("부등호", ["<", "<=", ">", ">="], index=["<", "<=", ">", ">="].index(st.session_state["ineq"]))
with col4:
    rhs = st.slider("우변 상수", -10, 10, st.session_state["rhs"], key="rhs")

st.session_state.update({"a1": a1, "a2": a2, "op": op, "ineq": ineq})

abs1_text = format_abs(a1, b1)
abs2_text = format_abs(a2, b2)
full_expr = f"{abs1_text} {op} {abs2_text} {ineq} {rhs}"

st.markdown("### 📌 현재 선택된 부등식")
st.latex(full_expr)

expr1 = build_expression(a1, b1)
expr2 = build_expression(a2, b2)
left_expr = sp.Abs(expr1) + sp.Abs(expr2) if op == "+" else sp.Abs(expr1) - sp.Abs(expr2)
right_expr = sp.Integer(rhs)

try:
    inequality = {
        "<": left_expr < right_expr,
        "<=": left_expr <= right_expr,
        ">": left_expr > right_expr,
        ">=": left_expr >= right_expr,
    }[ineq]
    solution = sp.solve_univariate_inequality(inequality, x)
except Exception as e:
    st.error(f"부등식 풀이 오류: {e}")
    st.stop()

st.subheader("3️⃣ 풀이 결과")
if solution == sp.S.EmptySet:
    st.write("🔴 해가 없습니다.")
elif solution == sp.S.Reals:
    st.write("🟢 모든 실수가 해입니다.")
    st.latex(r"(-\infty, \infty)")
else:
    st.latex(sp.latex(solution))

roots = []
for expr in [expr1, expr2]:
    roots += [r for r in sp.solve(sp.Eq(expr, 0), x) if r.is_real]
roots = sorted({float(r) for r in roots})

x_min = min(roots + [-10]) - 3
x_max = max(roots + [10]) + 3
x_min, x_max = float(x_min), float(x_max)
xs = np.linspace(x_min, x_max, 1000)

lhs_func = sp.lambdify(x, left_expr, "numpy")
rhs_func = sp.lambdify(x, right_expr, "numpy")
lhs_values = lhs_func(xs)
rhs_values = rhs_func(xs)

st.subheader("4️⃣ 그래프와 해석")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(xs, lhs_values, label=f"왼쪽: {sp.latex(left_expr)}", color="#1f77b4")
ax.plot(xs, rhs_values, label=f"오른쪽: {rhs}", color="#ff7f0e", linestyle="--")
ax.axhline(0, color="black", linewidth=0.8)

for root in roots:
    ax.axvline(root, color="gray", linestyle=":", linewidth=0.8)
    ax.text(root, ax.get_ylim()[1] * 0.9, f"x={root:.1f}", color="gray", ha="center", va="top", fontsize=8)

condition = {
    "<": lhs_values < rhs_values,
    "<=": lhs_values <= rhs_values,
    ">": lhs_values > rhs_values,
    ">=": lhs_values >= rhs_values,
}[ineq]
ax.fill_between(xs, lhs_values, rhs_values, where=condition, color="red", alpha=0.15)

ax.set_xlabel("x")
ax.set_ylabel("값")
ax.set_title("절댓값을 포함한 좌변과 우변의 그래프")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.4)
st.pyplot(fig)

st.markdown("### 5️⃣ 수직선으로 해 표현하기")
line_fig = plot_solution_line(solution, x_min, x_max)
st.pyplot(line_fig)

st.markdown(
    "---\n"
    "### 💡 사용 팁\n"
    "- `a₁` 또는 `a₂`를 음수로 선택하면 `-x` 형태 내부식도 만들 수 있어요.\n"
    "- 해가 나뉘는 구간은 절댓값 내부가 0이 되는 값을 기준으로 자동 계산됩니다.\n"
)
