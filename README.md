# AIstory-tester

AIbuncho 様が公開された文章特化型 LLM モデルをあれこれ試すためのテストコードです。  
Windows ＆ CUDA 環境が必要です。

https://huggingface.co/AIBunCho/japanese-novel-gpt-j-6b

# インストール手順

Python の実行環境と CUDA ドライバは事前に導入しておいてください。

1.適当なフォルダを作成し、PowerShell 等から次のコマンドを実行してください。

```
pip install -r requirements.txt
```

# 実行

```
python.exe .\AIstory-tester.py
```

しばらくすると「output-story-20230815-235959.txt」みたいのが同じフォルダ内に生成されます。実行するたびに生成内容はランダムに変化しますので、まずはお楽しみください。

# ヒント

現状で各種設定は「sample.json」に格納しています。

```json:sample.json
{
  "指示": "",
  "設定": "",
  "状況": "",
  "あらすじ": "",
  "文章": "",
  "シード": -1,
  "modelsize": 4,
  "max_new_tokens": 65535,
  "temperature": 0.7,
  "top_p": 0.9,
  "repetition_penalty": 1.2,
  "maxloop": 10,
  "maxlength": 1500,
  "maxwait": 5,
  "end": 0
}
```

このうち
"指示",
"設定",
"状況",
"あらすじ",
"文章",
にそれぞれ適当な編集を行い実行すると出力結果が変化します。残念ながら作者にも最適な指示はわからないので、もしおもしろい指示や設定を見つけた方は共有して頂けるとうれしいです。
