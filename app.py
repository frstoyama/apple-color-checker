from flask import Flask, render_template, request
import pandas as pd
import math

app = Flask(__name__)

# ExcelからCC基準値を読み込み（Excelが存在する場合）
try:
    df_excel = pd.read_excel("ColorReaderPro_Apple_CC.xlsx")
    excel_lab_values = df_excel[["L", "a", "b"]].values.tolist()
except Exception:
    excel_lab_values = []

# app.py に直接定義された基準CC値
fixed_cc_values = [
    [51.8, -18.1, 30.7],
    [47.8, -16.9, 27.1],
    [43.3, -14.6, 22.5],
    [39.9, -14.7, 18.6],
    [38.0, -12.1, 15.0],
    [35.5, -10.8, 13.6],
    [32.2, -7.9, 8.7],
    [30.5, -6.2, 5.8]
]

def delta_e_cie1976_manual(lab1, lab2):
    return round(math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2))), 2)

@app.route("/", methods=["GET", "POST"])
def index():
    cc_value = None
    input_lab = None
    fixed_deltas = []
    excel_deltas = []

    if request.method == "POST":
        L = float(request.form["L"])
        a = float(request.form["a"])
        b = float(request.form["b"])
        input_lab = [L, a, b]

        # ΔE計算（固定）
        fixed_deltas = [delta_e_cie1976_manual(input_lab, std_lab) for std_lab in fixed_cc_values]
        min_fixed_index = fixed_deltas.index(min(fixed_deltas))
        cc_value = round(min_fixed_index + 1 + (1 - (min(fixed_deltas) / 10)), 1)  # 小数点第一位まで表示

        # ΔE計算（Excel）
        if excel_lab_values:
            excel_deltas = [delta_e_cie1976_manual(input_lab, std_lab) for std_lab in excel_lab_values]

    return render_template("index.html", cc_value=cc_value, input_lab=input_lab,
                           fixed_deltas=fixed_deltas, excel_deltas=excel_deltas)

if __name__ == "__main__":
    app.run(debug=True)
