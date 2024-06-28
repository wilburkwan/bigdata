
import os
import json
import gradio as gr
import PyPDF2
import google.generativeai as genai


# 提示用戶輸入 API Key
api_key = "AIzaSyBCjcuoP7Oh5eK5Dh2nk9urYVeFjsPcLjw"

# 設定 API Key 環境變量
os.environ['GIMINI_API_KEY'] = api_key

# 定義函數讀取 PDF 檔案
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# 設定 generative ai 的 API Key
genai.configure(api_key=os.environ['GIMINI_API_KEY'])

# 初始化模型
model = genai.GenerativeModel('gemini-pro')

# 定義 Gradio 的處理函數
def analyze_pdf(file_path, prompt):
    # 讀取 PDF 檔案
    pdf_text = read_pdf(file_path)

    # 設定分析的 prompt
    final_prompt = prompt + " " + pdf_text

    # 發送生成請求
    response = model.generate_content(final_prompt)

    # 檢查回應結構並提取生成的文本內容
    if response and 'candidates' in response:
        if response['candidates']:
            generated_text = response['candidates'][0]['content']['parts'][0]['text']
            return generated_text
        else:
            return "No candidates found in response."
    else:
        # 假設 response 是一個 GenerateContentResponse 物件，這裡直接將其轉換為字串
        response_str = str(response)  # 將 response 轉換為字串

        # 提取 JSON 部分的字串（此步驟根據實際 response 的格式可能需要調整）
        start_index = response_str.find("{")
        end_index = response_str.rfind("}") + 1
        json_str = response_str[start_index:end_index]

        # 解析 JSON 資料
        data = json.loads(json_str)
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return text

# 定義 Gradio 的界面
with gr.Blocks() as demo:
    gr.Markdown("# PDF 內容分析")
    pdf_input = gr.File(label="上傳 PDF 檔案")
    prompt_input = gr.Textbox(label="輸入分析 Prompt")
    output = gr.Textbox(label="分析結果")
    analyze_button = gr.Button("開始分析")
    analyze_button.click(fn=analyze_pdf, inputs=[pdf_input, prompt_input], outputs=output)

# 啟動 Gradio 界面
demo.launch(share=True)
