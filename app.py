from flask import Flask, render_template, request, send_file
import pandas as pd
from sklearn.metrics import pairwise_distances
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# 基準Lab値（葉色インデックス1〜8）
ref_data = pd.DataFrame({
    'level': [1, 2, 3, 4, 5, 6, 7, 8],
    'L': [51.8, 47.8, 43.3, 39.9, 38.0, 35.5, 32.2, 30.5],
    'a': [-18.1, -16.9, -14.6, -14.7, -12.1, -10.8, -7.9, -6.2],
    'b': [30.7, 27.1, 22.5, 18.6, 15.0, 13.6, 8.7, 5.8]
})

# グローバル変数で測定値を保持
last_input = {'L': None, 'a': None, 'b': None}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            L = float(request.form['L'])
            a = float(request.form['a'])
            b = float(request.form['b'])
            last_input['L'] = L
            last_input['a'] = a
            last_input['b'] = b

            # 距離（ΔE）を計算
            input_lab = [[L, a, b]]
            ref_lab = ref_data[['L', 'a', 'b']].values
            distances = pairwise_distances(input_lab, ref_lab)[0]
            min_index = distances.argmin()

            result = {
                'level': int(ref_data.loc[min_index, 'level']),
                'delta_e': round(distances[min_index], 2),
                'ref_lab': tuple(round(x, 2) for x in ref_lab[min_index])
            }
        except:
            result = None

    return render_template('index.html', result=result)


@app.route('/plot.png')
def plot_png():
    fig, ax = plt.subplots()
    # 散布図（基準）
    ax.scatter(ref_data['a'], ref_data['b'], c='blue', label='基準値')

    # 測定値（赤）
    if all(v is not None for v in last_input.values()):
        ax.scatter(last_input['a'], last_input['b'], c='red', marker='*', s=200, label='測定値')
        ax.annotate(f"L={last_input['L']:.1f}, a={last_input['a']:.1f}, b={last_input['b']:.1f}",
                    (last_input['a'], last_input['b']),
                    textcoords="offset points", xytext=(30, 0), ha='left', fontsize=10, color='black')

    ax.set_xlabel('a*')
    ax.set_ylabel('b*')
    ax.set_title('a*-b* 散布図')
    ax.legend()
    ax.grid(True)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)