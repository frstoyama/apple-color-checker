from flask import Flask, render_template, request
import pandas as pd
import math

app = Flask(__name__)

# ΔE（CIE76）を計算する関数
def calculate_delta_e(lab1, lab2):
    return round(math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2))), 1)

# 直接定義された基準Lab値（CC値1～8）
standard_lab_list = [
    {'cc': 1, 'lab': [66.3, -18.0, 26.9]},
    {'cc': 2, 'lab': [62.5, -14.9, 27.4]},
    {'cc': 3, 'lab': [58.4, -11.9, 27.4]},
    {'cc': 4, 'lab': [54.4, -10.7, 26.2]},
    {'cc': 5, 'lab': [50.4, -8.5, 24.8]},
    {'cc': 6, 'lab': [46.6, -7.3, 23.7]},
    {'cc': 7, 'lab': [42.9, -6.2, 22.1]},
    {'cc': 8, 'lab': [39.0, -5.2, 21.5]},
]

# Excelファイルから基準値を読み込む（ColorReaderPro_Apple_CC.xlsx）
excel_path = "ColorReaderPro_Apple_CC.xlsx"
df_excel = pd.read_excel(excel_path)
cc_lab_excel = []
for _, row in df_excel.iterrows():
    try:
        cc = int(row['CC値'])
        lab = [float(row['L']), float(row['a']), float(row['b'])]
        cc_lab_excel.append({'cc': cc, 'lab': lab})
    except (ValueError, KeyError):
        continue

# 最も近いCCとΔE一覧を返す関数
def find_closest_cc(input_lab, cc_lab_list):
    delta_list = []
    for item in cc_lab_list:
        delta = calculate_delta_e(input_lab, item['lab'])
        delta_list.append({'cc': item['cc'], 'delta': delta})
    closest = min(delta_list, key=lambda x: x['delta'])
    return round(closest['cc'], 1), closest, delta_list

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            L = float(request.form["L"])
            a = float(request.form["a"])
            b = float(request.form["b"])
            input_lab = [L, a, b]

            cc_value_direct, closest_direct, delta_list_direct = find_closest_cc(input_lab, standard_lab_list)
            cc_value_excel, closest_excel, delta_list_excel = find_closest_cc(input_lab, cc_lab_excel)

            return render_template(
                "index.html",
                input_lab=input_lab,
                cc_value_direct=cc_value_direct,
                closest_direct=closest_direct,
                delta_list_direct=delta_list_direct,
                cc_value_excel=cc_value_excel,
                closest_excel=closest_excel,
                delta_list_excel=delta_list_excel
            )
        except ValueError:
            return render_template("index.html", input_lab=None, error="入力値に誤りがあります。")

    # GET時に必ずHTMLを返す
    return render_template("index.html", input_lab=None)

if __name__ == "__main__":
    app.run(debug=True)
