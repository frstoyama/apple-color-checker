from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie1976
import os

app = Flask(__name__)

# CC値とLab値の対応表（1〜8）
standard_lab_values = {
    1: (51.8, -18.1, 30.7),
    2: (47.8, -16.9, 27.1),
    3: (43.3, -14.6, 22.5),
    4: (39.9, -14.7, 18.6),
    5: (38.0, -12.1, 15.0),
    6: (35.5, -10.8, 13.6),
    7: (32.2, -7.9, 8.7),
    8: (30.5, -6.2, 5.8),
}

# ExcelファイルからLab値を読み込む関数
def load_excel_lab_values(filepath):
    df = pd.read_excel(filepath)
    lab_dict = {}
    for _, row in df.iterrows():
        level = int(row['CC'])
        lab_dict[level] = (row['L'], row['a'], row['b'])
    return lab_dict

@app.route('/', methods=['GET', 'POST'])
def index():
    cc_value = None
    cc_value_excel = None
    input_lab = (None, None, None)

    if request.method == 'POST':
        try:
            L = float(request.form['L'])
            a = float(request.form['a'])
            b = float(request.form['b'])
            input_lab = (L, a, b)
            input_color = LabColor(L, a, b)

            # 通常のCC値計算
            deltas_std = {}
            for level, (l, a_, b_) in standard_lab_values.items():
                std_color = LabColor(l, a_, b_)
                delta = delta_e_cie1976(input_color, std_color)
                deltas_std[level] = delta

            sorted_std = sorted(deltas_std.items(), key=lambda x: x[1])
            cc_low, d_low = sorted_std[0]
            cc_high, d_high = sorted_std[1]
            if d_low + d_high > 0:
                ratio = d_high / (d_low + d_high)
                interpolated_cc = cc_low * ratio + cc_high * (1 - ratio)
            else:
                interpolated_cc = float(cc_low)
            cc_value = round(interpolated_cc, 1)

            # Excelに基づくCC値計算
            excel_path = os.path.join(os.path.dirname(__file__), 'ColorReaderPro_Apple_CC.xlsx')
            if os.path.exists(excel_path):
                excel_lab_values = load_excel_lab_values(excel_path)
                deltas_excel = {}
                for level, (l, a_, b_) in excel_lab_values.items():
                    std_color = LabColor(l, a_, b_)
                    delta = delta_e_cie1976(input_color, std_color)
                    deltas_excel[level] = delta

                sorted_excel = sorted(deltas_excel.items(), key=lambda x: x[1])
                cc_low, d_low = sorted_excel[0]
                cc_high, d_high = sorted_excel[1]
                if d_low + d_high > 0:
                    ratio = d_high / (d_low + d_high)
                    interpolated_cc_excel = cc_low * ratio + cc_high * (1 - ratio)
                else:
                    interpolated_cc_excel = float(cc_low)
                cc_value_excel = round(interpolated_cc_excel, 1)
            else:
                cc_value_excel = 'Excelファイルが見つかりません'

        except ValueError:
            cc_value = '入力エラー'
            cc_value_excel = '入力エラー'

    return render_template('index.html', cc_value=cc_value, cc_value_excel=cc_value_excel, input_lab=input_lab)

if __name__ == '__main__':
    app.run(debug=True)
