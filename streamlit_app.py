import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

x = sp.symbols("x")

st.set_page_config(
    page_title="절댓값을 포함한 일차부등식 탐구",
    page_icon="📘",
    layout="wide"
)

st.title("📘 절댓값을 포함한 일차부등식 탐구")

st.markdown(
    """
### 🎯 학습목표
**절댓값을 포함한 일차부등식을 풀 수 있다!**
"""
)

st.divider()


def parse_expr_safe(expr_text: str) -> sp.Expr:
    expr_text = expr_text.strip()
    if expr_text == "":
        raise ValueError("빈 입력")
    return sp.sympify(expr_text)


def is_linear(expr: sp.Expr) -> bool:
    expr = sp.expand(expr)
    poly = sp.Poly(expr, x)
    return poly.degree() <= 1


def validate_linear(expr_text: str) -> sp.Expr:
    expr = parse_expr_safe(expr_text)
    if not is_linear(expr):
        raise ValueError("절댓값 내부에는 일차식만 입력 가능합니다.")
    return expr


def interval_label(left, right):
    if left is sp.S.NegativeInfinity:
        return f"x < {sp.latex(right)}"
    if right is sp.S.Infinity:
        return f"x \\ge {sp.latex(left)}"
    return f"{sp.latex(left)} \\le x < {sp.latex(right)}"


def pick_test_point(left, right):
    if left is sp.S.NegativeInfinity and right is not sp.S.Infinity:
        return float(right) - 1.0
    if right is sp.S.Infinity and left is not sp.S.NegativeInfinity:
        return float(left) + 1.0
    if left is sp.S.NegativeInfinity and right is sp.S.Infinity:
        return 0.0
    return (float(left) + float(right)) / 2.0


def to_interval(expr):
    if expr.is_Interval:
        return [expr]
    if expr.is_Union:
        return [arg for arg in expr.args if arg.is_Interval]
    return []


def plot_number_line(solution, x_min, x_max):
    fig, ax = plt.subplots(figsize=(8, 1.5))
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-1, 1)
    ax.get_yaxis().set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position("center")

    ticks = np.linspace(x_min, x_max, 9)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.1f}" for t in ticks])
    ax.tick_params(axis="x", which="both", length=6)

    intervals = to_interval(solution)
    for interval in intervals:
        start = -1e6 if interval.start is sp.S.NegativeInfinity else float(interval.start)
        end = 1e6 if interval.end is sp.S.Infinity else float(interval.end)
        start = max(start, x_min)
        end = min(end, x_max)
        if start >= end:
            continue
        ax.plot([start, end], [0, 0], color="red", linewidth=6)
        if interval.left_open:
            ax.plot(start, 0, marker="o", color="white", markeredgecolor="red", markersize=8)
        else:
            ax.plot(start, 0, marker="o", color="red", markersize=8)
        if interval.right_open:
            ax.plot(end, 0, marker="o", color="white", markeredgecolor="red", markersize=8)
        else:
            ax.plot(end, 0, marker="o", color="red", markersize=8)

    return fig


st.subheader("📝 부등식 입력")
col1, col2, col3, col4, col5 = st.columns([3, 1, 3, 2, 3])

with col1:
    abs1_text = st.text_input("첫 번째 절댓값 내부", value="x+1")
with col2:
    plus_minus = st.selectbox("연산", ["+", "-"])
with col3:
    abs2_text = st.text_input("두 번째 절댓값 내부", value="2*x-4")
with col4:
    inequality = st.selectbox("부등호", [">", ">=", "<", "<="]) 
with col5:
    rhs_text = st.text_input("우변", value="5")

st.caption("곱셈 기호를 포함하여 작성해주세요! 예시: 2x는 '2*x' 로 입력합니다.")
st.divider()

if st.button("🚀 풀이 시작", use_container_width=True):
    try:
        abs1 = validate_linear(abs1_text)
        abs2 = validate_linear(abs2_text)
        rhs = parse_expr_safe(rhs_text)
    except Exception as e:
        st.error(f"입력 오류: {e}")
        st.stop()

    st.success("입력 확인 완료")

    roots = []
    try:
        r1 = sp.solve(sp.Eq(abs1, 0), x)
        r2 = sp.solve(sp.Eq(abs2, 0), x)
        for r in r1 + r2:
            if r.is_real:
                roots.append(sp.simplify(r))
    except Exception as e:
        st.error(f"근 계산 오류: {e}")
        st.stop()

    roots = sorted(list(set(roots)), key=lambda v: float(v))

    st.subheader("📌 절댓값이 0이 되는 값")
    if len(roots) == 0:
        st.write("절댓값 내부가 0이 되는 실수가 없습니다.")
        st.stop()

    for r in roots:
        st.latex(f"x = {sp.latex(r)}")

    st.divider()

    intervals = []
    if len(roots) == 1:
        a = roots[0]
        intervals = [
            (interval_label(sp.S.NegativeInfinity, a), sp.S.NegativeInfinity, a),
            (interval_label(a, sp.S.Infinity), a, sp.S.Infinity),
        ]
    elif len(roots) == 2:
        a, b = roots
        intervals = [
            (interval_label(sp.S.NegativeInfinity, a), sp.S.NegativeInfinity, a),
            (interval_label(a, b), a, b),
            (interval_label(b, sp.S.Infinity), b, sp.S.Infinity),
        ]
    else:
        st.error("절댓값 0이 되는 값이 2개 이하여야 합니다.")
        st.stop()

    lhs_original = sp.Abs(abs1) + sp.Abs(abs2) if plus_minus == "+" else sp.Abs(abs1) - sp.Abs(abs2)

    st.subheader("📖 구간별 풀이")
    solution_parts = []
    graph_segments = []

    for idx, (label, left, right) in enumerate(intervals, start=1):
        st.markdown(f"#### {idx}. 구간: {label}")
        test_point = pick_test_point(left, right)

        sign1 = 1 if abs1.subs(x, test_point) >= 0 else -1
        sign2 = 1 if abs2.subs(x, test_point) >= 0 else -1
        expr1 = abs1 if sign1 == 1 else -abs1
        expr2 = abs2 if sign2 == 1 else -abs2
        linear_expr = expr1 + expr2 if plus_minus == "+" else expr1 - expr2
        linear_expr = sp.simplify(linear_expr)

        sign_desc1 = "+" if sign1 == 1 else "-"
        sign_desc2 = "+" if sign2 == 1 else "-"
        expr1_str = f"{sign_desc1}{sp.latex(abs1)}" if sign1 == -1 else sp.latex(abs1)
        expr2_str = f"{sign_desc2}{sp.latex(abs2)}" if sign2 == -1 else sp.latex(abs2)
        if plus_minus == "+":
            piece_str = f"{expr1_str} + {expr2_str}"
        else:
            piece_str = f"{expr1_str} - {expr2_str}"

        st.markdown("- 선형식:")
        st.latex(sp.latex(linear_expr))

        interval_relation = sp.And(x >= left, x < right) if right is not sp.S.Infinity and left is not sp.S.NegativeInfinity else (
            (x < right) if left is sp.S.NegativeInfinity else (x >= left)
        )
        inequality_expr = None
        if inequality == ">":
            inequality_expr = linear_expr > rhs
        elif inequality == ">=":
            inequality_expr = linear_expr >= rhs
        elif inequality == "<":
            inequality_expr = linear_expr < rhs
        else:
            inequality_expr = linear_expr <= rhs

        st.markdown("- 구간에서의 부등식:")
        st.latex(f"{sp.latex(linear_expr)} {inequality} {sp.latex(rhs)}")

        try:
            sol = sp.solve_univariate_inequality(inequality_expr, x)
        except Exception as e:
            st.error(f"구간 부등식 풀이 오류: {e}")
            continue

        if left is not sp.S.NegativeInfinity or right is not sp.S.Infinity:
            if left is sp.S.NegativeInfinity:
                domain_interval = sp.Interval.open(-sp.oo, right) if right is not sp.S.Infinity else sp.Interval(-sp.oo, sp.oo)
            elif right is sp.S.Infinity:
                domain_interval = sp.Interval(left, sp.oo)
            else:
                domain_interval = sp.Interval(left, right, left_open=False, right_open=True)
            sol = sol.intersect(domain_interval)

        graph_segments.append((left, right, linear_expr))
        solution_parts.append(sol)

        st.markdown("- 이 구간의 해:")
        if sol is sp.EmptySet:
            st.write("해가 없습니다.")
        else:
            st.latex(sp.latex(sol))

        st.divider()

    if not solution_parts:
        st.warning("해를 구할 수 없습니다.")
        st.stop()

    total_solution = solution_parts[0]
    for part in solution_parts[1:]:
        total_solution = total_solution.union(part)

    st.subheader("✅ 최종 해")
    if total_solution is sp.EmptySet:
        st.write("해가 존재하지 않습니다.")
    else:
        st.latex(sp.latex(total_solution))

    all_x = []
    for left, right, _ in graph_segments:
        if left is not sp.S.NegativeInfinity:
            all_x.append(float(left))
        if right is not sp.S.Infinity:
            all_x.append(float(right))
    if all_x:
        x_min = min(all_x) - 3
        x_max = max(all_x) + 3
    else:
        x_min, x_max = -10, 10
    x_min, x_max = float(x_min), float(x_max)
    xs = np.linspace(x_min, x_max, 800)

    lhs_func = sp.lambdify(x, lhs_original, "numpy")
    rhs_func = sp.lambdify(x, rhs, "numpy")
    lhs_values = lhs_func(xs)
    rhs_values = rhs_func(xs)

    st.subheader("📈 구간별 그래프")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, rhs_values, label=f"우변: {sp.latex(rhs)}", color="black", linestyle="--")

    colors = ["tab:blue", "tab:orange", "tab:green"]
    for idx, (left, right, linear_expr) in enumerate(graph_segments):
        mask = np.ones_like(xs, dtype=bool)
        if left is not sp.S.NegativeInfinity:
            mask &= xs >= float(left)
        if right is not sp.S.Infinity:
            mask &= xs < float(right)
        if not np.any(mask):
            continue
        segment_y = sp.lambdify(x, linear_expr, "numpy")(xs[mask])
        ax.plot(xs[mask], segment_y, color=colors[idx % len(colors)], label=f"구간 {idx+1}: {sp.latex(linear_expr)}")
        if left is not sp.S.NegativeInfinity:
            ax.axvline(float(left), color=colors[idx % len(colors)], linewidth=0.8, linestyle=":")
        if right is not sp.S.Infinity:
            ax.axvline(float(right), color=colors[idx % len(colors)], linewidth=0.8, linestyle=":")

    ax.set_xlabel("x")
    ax.set_ylabel("좌변 값")
    ax.legend(loc="upper left", fontsize="small")
    ax.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig)

    st.subheader("🧭 수직선으로 표현된 최종 해")
    solution_fig = plot_number_line(total_solution, x_min, x_max)
    st.pyplot(solution_fig)

    if plus_minus == "+":
        lhs_original = Abs(abs1) + Abs(abs2)
    else:
        lhs_original = Abs(abs1) - Abs(abs2)

    st.subheader("📖 구간별 풀이")

    solution_parts = []

    graph_data = []
for idx, (label, left, right) in enumerate(intervals, start=1):

    section_labels = ["①", "②", "③"]

    if idx <= 3:
        st.markdown(f"### {section_labels[idx-1]}")
    else:
        st.markdown(f"### {idx}")

    st.latex(label)

    # ----------------------------
    # 테스트점 선택
    # ----------------------------

    if left is S.NegativeInfinity:

        test_x = float(right) - 1

    elif right is S.Infinity:

        test_x = float(left) + 1

    else:

        test_x = (float(left) + float(right)) / 2
        expanded_expr = simplify(expanded_expr)

        st.latex(
            sp.latex(expanded_expr)
            + inequality
            + sp.latex(rhs)
        )

        # 이후 3/4에서 실제 부등식 풀이 진행
        graph_data.append(
            (
                label,
                expanded_expr
            )
        )

        # ----------------------------
        # 구간 조건
        # ----------------------------

        if left is S.NegativeInfinity:

            interval_condition = (x < right)

        elif right is S.Infinity:

            interval_condition = (x >= left)

        else:

            interval_condition = sp.And(
                x >= left,
                x < right
            )

        # ----------------------------
        # 부등식 생성
        # ----------------------------

        if inequality == ">":

            inequality_expr = (
                expanded_expr > rhs
            )

        elif inequality == ">=":

            inequality_expr = (
                expanded_expr >= rhs
            )

        elif inequality == "<":

            inequality_expr = (
                expanded_expr < rhs
            )

        else:

            inequality_expr = (
                expanded_expr <= rhs
            )

        # ----------------------------
        # 부등식 풀이
        # ----------------------------

        try:

            inequality_solution = (
                solveset(
                    inequality_expr,
                    x,
                    domain=S.Reals
                )
            )

        except Exception as e:

            st.error(
                f"부등식 풀이 오류: {e}"
            )

            continue

        # ----------------------------
        # 구간과 교집합
        # ----------------------------

        if left is S.NegativeInfinity:

            current_interval = Interval.open(
                -sp.oo,
                right
            )

        elif right is S.Infinity:

            current_interval = Interval(
                left,
                sp.oo
            )

        else:

            current_interval = Interval(
                left,
                right,
                left_open=False,
                right_open=True
            )

        try:

            final_piece = (
                inequality_solution.intersect(
                    current_interval
                )
            )

        except Exception:

            final_piece = inequality_solution

        solution_parts.append(final_piece)

        # ----------------------------
        # 결과 표시
        # ----------------------------

        st.markdown("**구간에서 얻은 해**")

        st.latex(
            sp.latex(final_piece)
        )

        st.divider()

    # --------------------------------------------------
    # 최종 해
    # --------------------------------------------------

    st.subheader("✅ 최종 해")

    if len(solution_parts) == 0:

        st.write("해가 존재하지 않습니다.")

        st.stop()

    total_solution = solution_parts[0]

    for s in solution_parts[1:]:

        try:
            total_solution = (
                total_solution.union(s)
            )

        except Exception:
            pass

    st.latex(
        sp.latex(total_solution)
    )

    # --------------------------------------------------
    # 그래프용 함수
    # --------------------------------------------------

    if plus_minus == "+":

        lhs_function = (
            Abs(abs1)
            + Abs(abs2)
        )

    else:

        lhs_function = (
            Abs(abs1)
            - Abs(abs2)
        )

    rhs_function = rhs

    st.subheader("📈 함수 그래프")

    graph_points = roots.copy()

    if len(graph_points) == 1:

        xmin = float(graph_points[0]) - 5
        xmax = float(graph_points[0]) + 5

    else:

        xmin = float(min(graph_points)) - 5
        xmax = float(max(graph_points)) + 5

    xs = np.linspace(
        xmin,
        xmax,
        1000
    )

    lhs_func = sp.lambdify(
        x,
        lhs_function,
        "numpy"
    )

    rhs_func = sp.lambdify(
        x,
        rhs_function,
        "numpy"
    )

    lhs_y = lhs_func(xs)
    rhs_y = rhs_func(xs)

    # 4/4에서 그래프 출력

        # --------------------------------------------------
    # 함수 그래프 출력
    # --------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        xs,
        lhs_y,
        linewidth=2,
        label="좌변"
    )

    ax.plot(
        xs,
        rhs_y,
        linewidth=2,
        linestyle="--",
        label="우변"
    )

    # 절댓값이 0이 되는 점 표시
    for r in roots:

        ax.axvline(
            float(r),
            linestyle=":",
            alpha=0.7
        )

        ax.text(
            float(r),
            ax.get_ylim()[0],
            f"x={sp.latex(r)}",
            fontsize=9
        )

    ax.set_title("좌변과 우변의 그래프")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

    st.divider()

    # --------------------------------------------------
    # 수직선 그래프
    # --------------------------------------------------

    st.subheader("📍 해의 수직선 표현")

    fig2, ax2 = plt.subplots(
        figsize=(10, 2)
    )

    ax2.axhline(
        y=0,
        linewidth=2
    )

    ax2.set_yticks([])

    ax2.set_xlim(
        xmin,
        xmax
    )

    # ----------------------------------------------
    # 해집합 표시
    # ----------------------------------------------

    try:

        if isinstance(
            total_solution,
            Interval
        ):

            intervals_to_draw = [
                total_solution
            ]

        else:

            intervals_to_draw = list(
                total_solution.args
            )

    except Exception:

        intervals_to_draw = []

    for item in intervals_to_draw:

        if not isinstance(
            item,
            Interval
        ):
            continue

        left = (
            xmin
            if item.start is -sp.oo
            else float(item.start)
        )

        right = (
            xmax
            if item.end is sp.oo
            else float(item.end)
        )

        ax2.plot(
            [left, right],
            [0, 0],
            linewidth=8
        )

        # 왼쪽 끝점

        if item.start is not -sp.oo:

            if item.left_open:

                ax2.plot(
                    left,
                    0,
                    marker="o",
                    markersize=10,
                    fillstyle="none"
                )

            else:

                ax2.plot(
                    left,
                    0,
                    marker="o",
                    markersize=10
                )

        # 오른쪽 끝점

        if item.end is not sp.oo:

            if item.right_open:

                ax2.plot(
                    right,
                    0,
                    marker="o",
                    markersize=10,
                    fillstyle="none"
                )

            else:

                ax2.plot(
                    right,
                    0,
                    marker="o",
                    markersize=10
                )

    ax2.set_title("해의 수직선 그래프")

    st.pyplot(fig2)

    st.divider()

    # --------------------------------------------------
    # 정리
    # --------------------------------------------------

    st.success(
        "풀이가 완료되었습니다!"
    )

    st.info(
        """
절댓값이 0이 되는 값을 기준으로
구간을 나누어 풀이했습니다.

그래프를 통해 각 구간의 의미를
시각적으로 확인해 보세요.
"""
    )

