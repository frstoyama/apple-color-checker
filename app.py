from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances

app = Flask(__name__)

# カラーチャート読み込み
df = pd.read_excel("ColorReaderPro_Apple_CC.xlsx")
lab_values = df[['L', 'a', 'b']].values
cc_numbers = df['CC_No'].values

def classify_lab(L, a, b):
    input_color = np.array([[L, a, b]])
    distances = pairwise_distances(input_color, lab_values, metric='euclidean')
    idx = np.argmin(distances)
    return int(cc_numbers[idx]), round(float(distances[0, idx]), 2), lab_values[idx]

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            L = float(request.form["L"])
            a = float(request.form["a"])
            b = float(request.form["b"])
            level, deltaE, matched = classify_lab(L, a, b)
            result = {
                "level": level,
                "deltaE": deltaE,
                "matched": matched,
                "input": (L, a, b)
            }
        except ValueError:
            result = "入力が正しくありません。数値を入力してください。"
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
