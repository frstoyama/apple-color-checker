import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

# CCごとの基準a*, b*値（表に基づく） ハックナインの論文の値を参考とする　chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.hro.or.jp/upload/16360/75-2.pdf
CC_DATA = {
    1: (-18.1, 30.7),
    2: (-16.9, 27.1),
    3: (-14.6, 22.5),
    4: (-14.7, 18.6),
    5: (-12.1, 15.0),
    6: (-10.8, 13.6),
    7: (-7.9, 8.7),
    8: (-6.2, 5.8),
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    image_base64 = None

    if request.method == 'POST':
        try:
            L = float(request.form['L'])
            a = float(request.form['a'])
            b = float(request.form['b'])

            # もっとも近いCC値をユークリッド距離で判定
            min_dist = float('inf')
            closest_cc = None
            for cc, (cc_a, cc_b) in CC_DATA.items():
                dist = ((a - cc_a)**2 + (b - cc_b)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_cc = cc

            result = f"CC値 {closest_cc}（最も近い基準値）"

            # 散布図生成
            fig, ax = plt.subplots(figsize=(7, 6))
            for cc, (cc_a, cc_b) in CC_DATA.items():
                ax.scatter(cc_a, cc_b, color='blue')
                ax.text(cc_a + 0.3, cc_b, f"CC{cc}", fontsize=10)

            ax.scatter(a, b, color='red', marker='*', s=200, label='測定値')
            ax.annotate(
                f"測定値\nL={L:.1f}\na={a:.1f}\nb={b:.1f}",
                xy=(a, b),
                xytext=(-5, 35),
                textcoords="data",
                arrowprops=dict(arrowstyle="->", color='gray'),
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white", alpha=0.8)
            )

            ax.set_xlabel('a*')
            ax.set_ylabel('b*')
            ax.set_title('a*-b* 平面におけるCC基準と測定値')
            ax.grid(True)
            ax.invert_xaxis()
            plt.tight_layout()

            # 画像をbase64でエンコード
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

        except Exception as e:
            result = f"エラー: {str(e)}"

    return render_template('index.html', result=result, image=image_base64)

if __name__ == '__main__':
    app.run(debug=True)
