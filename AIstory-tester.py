from transformers import GPTJForCausalLM, AlbertTokenizer
import torch
import re
import regex
import time
import datetime
from tqdm import tqdm
import json
import argparse
from peft import PeftModel


# 生成関数本体
def b(prompt):
    input_ids = tokenizer.encode(
        prompt,
        add_special_tokens=False,
        return_tensors="pt"
    ).cuda()
    tokens = model.generate(
        input_ids=input_ids.to(device=model.device),
        max_new_tokens=d["max_new_tokens"],
        temperature=d["temperature"],
        top_p=d["top_p"],
        repetition_penalty=d["repetition_penalty"],
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    out = tokenizer.decode(tokens[0], skip_special_tokens=True)
    return out


# 設定に基づいて生成関数を呼び出す
def story(begin, prompt):
    s = b(begin + prompt)
    ptr = r'文章:(.*)'
    m = re.search(ptr, s)
    return (m.group())


# 指定文字で文字列を分割する
def conv_lf(pstr, s):
    for p in pstr:
        ptr = '(' + p + ')'
        s = regex.sub(ptr, r'\1\n', s)
    return s


# 生成結果と設定を出力する
def save_file(fname, buffer, dic):
    # ファイル名へタイムスタンプを追加して保存する
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    wfile = fname + now.strftime('%Y%m%d-%H%M%S') + ".txt"
    with open(wfile, "w", encoding="utf8", newline='\n') as f:
        f.write(buffer)
    jwfile = fname + now.strftime('%Y%m%d-%H%M%S') + ".json"
    with open(jwfile, "w", encoding="utf8") as jf:
        json.dump(dic, jf, indent=2, ensure_ascii=False)

    print("Saved", wfile, jwfile)


# メイン処理
# 引数の評価
parser = argparse.ArgumentParser()
parser.add_argument("--configfile", type=str,
                    help="Config file name", default="./sample.json")
args = parser.parse_args()

# AImodelの初期化
tokenizer = AlbertTokenizer.from_pretrained(
    "AIBunCho/japanese-novel-gpt-j-6b",
    keep_accents=True,
    remove_space=False)

model = GPTJForCausalLM.from_pretrained(
    "AIBunCho/japanese-novel-gpt-j-6b",
    load_in_4bit=True,
    device_map='auto',
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True)

# model.half()
model.eval()

# if torch.cuda.is_available():
#     model = model.to("cuda")

endless = True
eval_flag = False

while endless:
    try:
        # 設定ファイルの読み込みを行う
        with open(args.configfile, "r", encoding="utf8") as f:
            d = json.load(f)

        # 設定ファイルから読み込んだ生成プロンプトを準備する
        config_prompt = d["指示"] + "設定：" + d["設定"] + "あらすじ：" + d["あらすじ"]
        seed_prompt = "文章：" + d["文章"]
        first_seed = d["シード"]
        if first_seed == -1:
            first_seed = int(time.time())
            d["シード"] = first_seed
        torch.manual_seed(first_seed)

        if eval_flag is False:
            if d.get("loratest") is not None:
                if d["loratest"] is True:
                    # LoRAモデルの準備
                    model = PeftModel.from_pretrained(
                        model,
                        "sehiro/akanetalk-lora",
                        load_in_4bit=True,
                        device_map='auto',
                        torch_dtype=torch.float32,
                    )
                    print("LoRA test enable.")
            model.eval()
            eval_flag = True

        # 指定文字数を超えるか、または指定回数を超えるまでまで生成を続ける
        print("Making start.")

        output = seed_prompt

        maxloop = d["maxloop"]
        maxlength = d["maxlength"]
        for i in tqdm(range(maxloop), desc="Generate"):
            output = story(config_prompt, output)
            seed = int(time.time())
            torch.manual_seed(seed)

            # GPU負荷調整のためのwait時間（秒）
            # 生成速度が落ちるため、可能なら設定時間を短くすること
            # 0以下ならsleepしない
            maxwait = d["maxwait"]
            if maxwait > 0:
                time.sleep(maxwait)
        print("Done, loop=", i)

    finally:
        # 生成された文章に改行を追加して成形する（簡易版）
        ptr = r'。」）'
        m = conv_lf(ptr, output)

        ptr = r'文章:'
        m = re.sub(ptr, '', m)

        d["文章"] = re.sub(ptr, '', output)
        save_file("output-story-", m, d)

    time.sleep(10)
