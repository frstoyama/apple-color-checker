from flask import Flask, render_template, request
import pandas as pd
import math

app = Flask(__name__)

# ─────────────────────────────
# ExcelからのCC基準値の読み込み
# ─────────────────────────────
excel_df = pd.read_excel("ColorReaderPro_Apple_CC.xlsx")
cc_lab_excel = []
for i, row in excel_df.iterrows():
    cc_lab_excel.append({
        "cc": i + 1,
        "L": row["L"],
        "a": row["a"],
        "b": row["b"]
    })

# ─────────────────────────────
# 手入力で与えた基準値
# ─────────────────────────────
standard_lab_list = [
    {"cc": 1, "L": 80.2, "a": -16.3, "b": 30.3},
    {"cc": 2, "L": 73.5, "a": -14.3, "b": 29.3},
    {"cc": 3, "L": 65.5, "a": -13.3, "b": 27.4},
    {"cc": 4, "L": 59.3, "a": -12.1, "b": 24.5},
    {"cc": 5, "L": 51.8, "a": -11.2, "b": 21.8},
    {"cc": 6, "L": 45.9, "a": -10.7, "b": 18.8},
    {"cc": 7, "L": 40.7, "a": -10.5, "b": 16.9},
    {"cc": 8, "L": 36.3, "a": -10.5, "b": 14.8},
]

# ΔE計算関数（CIE1976）
def delta_e_cie1976_manual(lab1, lab2):
    return round(math.sqrt(
        (lab1[0] - lab2[0]) ** 2 +
        (lab1[1] - lab2[1]) ** 2 +
        (lab1[2] - lab2[2]) ** 2
    ), 1)

@app.route("/", methods=["GET", "POST"])
def index():
    cc_value_manual = None
    cc_value_excel = None
    delta_e_manual_list = []
    delta_e_excel_list = []
    input_lab = None

    if request.method == "POST":
        L = float(request.form["L"])
        a = float(request.form["a"])
        b = float(request.form["b"])
        input_lab = (L, a, b)

        # 手入力のCC値群とのΔE計算
        for entry in standard_lab_list:
            delta = delta_e_cie1976_manual(input_lab, (entry["L"], entry["a"], entry["b"]))
            delta_e_manual_list.append({"cc": entry["cc"], "delta": delta})

        # Excel由来のCC値群とのΔE計算
        for entry in cc_lab_excel:
            delta = delta_e_cie1976_manual(input_lab, (entry["L"], entry["a"], entry["b"]))
            delta_e_excel_list.append({"cc": entry["cc"], "delta": delta})

        # ΔEが最小のCCを取得
        cc_value_manual = min(delta_e_manual_list, key=lambda x: x["delta"])["cc"]
        cc_value_excel = min(delta_e_excel_list, key=lambda x: x["delta"])["cc"]

    return render_template(
        "index.html",
        input_lab=input_lab,
        cc_value_manual=cc_value_manual,
        cc_value_excel=cc_value_excel,
        delta_e_manual_list=delta_e_manual_list,
        delta_e_excel_list=delta_e_excel_list
    )

if __name__ == "__main__":
    app.run(debug=True)
