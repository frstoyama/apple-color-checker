from flask import Flask, render_template, request, redirect, url_for, session
from math import sqrt

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # セッションを有効にするためのキー

# 標準CCのLab値リスト
standard_lab_list = [
    {'cc': 1, 'lab': [45.11, -14.68, 21.59]},
    {'cc': 2, 'lab': [42.70, -13.08, 18.31]},
    {'cc': 3, 'lab': [36.82, -11.04, 15.37]},
    {'cc': 4, 'lab': [33.40, -11.36, 13.37]},
    {'cc': 5, 'lab': [31.06, -9.49, 11.18]},
    {'cc': 6, 'lab': [28.95, -8.03, 9.26]},
    {'cc': 7, 'lab': [24.68, -5.71, 6.22]},
    {'cc': 8, 'lab': [22.86, -4.58, 4.17]},
]

# ΔE（CIE76）を計算する関数
def delta_e_cie76(lab1, lab2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))

@app.route("/", methods=["GET", "POST"])
def index():
    input_lab = None
    estimated_cc = None
    delta_list_direct = []

    # 履歴を取得（なければ初期化）
    history = session.get('history', [])
    average_lab = session.get('average_lab')
    average_cc = session.get('average_cc')

    if request.method == "POST":
        try:
            L = float(request.form["L"])
            a = float(request.form["a"])
            b = float(request.form["b"])
            input_lab = [L, a, b]

            # ΔE計算
            delta_list_direct = []
            for ref in standard_lab_list:
                delta = delta_e_cie76(input_lab, ref["lab"])
                delta_list_direct.append({"cc": ref["cc"], "delta": delta})

            # ΔE最小のCC値を推定
            min_item = min(delta_list_direct, key=lambda x: x["delta"])
            estimated_cc = min_item["cc"]
            delta_value = round(min_item["delta"], 2)

            # 履歴追加
            history.append({
                "L": round(L, 2),
                "a": round(a, 2),
                "b": round(b, 2),
                "delta": delta_value,
                "estimated_cc": estimated_cc
            })
            session['history'] = history
            session.pop('average_lab', None)
            session.pop('average_cc', None)

        except ValueError:
            pass  # 入力エラーなどは無視（必要に応じてエラー表示可）

    return render_template(
        "index.html",
        input_lab=input_lab,
        estimated_cc=estimated_cc,
        delta_list_direct=delta_list_direct,
        history=history,
        average_lab=average_lab,
        average_cc=average_cc
    )

@app.route("/clear", methods=["POST"])
def clear():
    session.pop('history', None)
    session.pop('average_lab', None)
    session.pop('average_cc', None)
    return redirect(url_for('index'))

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    history = session.get('history', [])
    if 0 <= index < len(history):
        history.pop(index)
        session['history'] = history
    return redirect(url_for('index'))

@app.route("/average_cc", methods=["POST"])
def average_cc():
    history = session.get('history', [])
    if not history:
        return redirect(url_for('index'))

    # Lab平均
    L_avg = sum(h["L"] for h in history) / len(history)
    a_avg = sum(h["a"] for h in history) / len(history)
    b_avg = sum(h["b"] for h in history) / len(history)
    session['average_lab'] = [round(L_avg, 2), round(a_avg, 2), round(b_avg, 2)]

    # 推定CC値の平均
    cc_avg = sum(h["estimated_cc"] for h in history) / len(history)
    session['average_cc'] = round(cc_avg, 2)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
