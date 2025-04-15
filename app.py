import streamlit as st
import random
import os
from PIL import Image, ImageDraw
import math
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# 設定音符圖庫路徑
PICS_DIR = "pics"

# 難度對應的音符範圍
DIFFICULTY_NOTES = {
    "beginner": [0, 1, 2],
    "beginner+": [0, 1, 2, 3],
    "intermediate": [0, 1, 4, 5, 6, 7, 15],
    "intermediate+": [0, 1, 2, 3, 4, 5, 6, 7, 15],
    "advanced": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15],
    "professional": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
}

# 難度對應的小節數範圍
MEASURE_RANGES = {
    "beginner": (1, 27),
    "beginner+": (1, 27),
    "intermediate": (1, 18),
    "intermediate+": (1, 18),
    "advanced": (1, 18),
    "professional": (1, 18)
}

# 每行小節數
MEASURES_PER_ROW = {
    "beginner": 3,
    "beginner+": 3,
    "intermediate": 2,
    "intermediate+": 2,
    "advanced": 2,
    "professional": 2
}

# 平板直立尺寸（假設 10 吋平板，解析度約 1200x1920，單位 pixel）
TABLET_WIDTH = 1200
TABLET_HEIGHT = 1920
NOTE_HEIGHT = 265
NOTE_WIDTH_RANGE = (180, 250)
MEASURE_BEATS = 4
BARLINE_WIDTH = 5
MARGIN = 50

def generate_score(difficulty, num_measures):
    # 根據難度選擇音符
    note_choices = DIFFICULTY_NOTES[difficulty]
    measures_per_row = MEASURES_PER_ROW[difficulty]
    
    # 計算每小節寬度（隨機音符寬度）
    measure_width = sum(random.randint(*NOTE_WIDTH_RANGE) for _ in range(MEASURE_BEATS)) + BARLINE_WIDTH
    row_width = measure_width * measures_per_row + BARLINE_WIDTH
    num_rows = math.ceil(num_measures / measures_per_row)
    
    # 計算總圖片尺寸
    total_width = max(row_width, measure_width * min(num_measures, measures_per_row)) + 2 * MARGIN
    total_height = (NOTE_HEIGHT + 50) * num_rows + 2 * MARGIN
    
    # 確保圖片不超過平板尺寸
    scale = min(TABLET_WIDTH / total_width, TABLET_HEIGHT / total_height)
    if scale < 1:
        total_width = int(total_width * scale)
        total_height = int(total_height * scale)
        measure_width = int(measure_width * scale)
        note_width_range = (int(NOTE_WIDTH_RANGE[0] * scale), int(NOTE_WIDTH_RANGE[1] * scale))
        note_height = int(NOTE_HEIGHT * scale)
    else:
        note_width_range = NOTE_WIDTH_RANGE
        note_height = NOTE_HEIGHT
    
    # 創建空白樂譜圖片
    score_image = Image.new("RGB", (int(total_width), int(total_height)), "white")
    draw = ImageDraw.Draw(score_image)
    
    # 繪製樂譜
    for row in range(num_rows):
        measures_in_row = min(measures_per_row, num_measures - row * measures_per_row)
        x_offset = MARGIN
        y_offset = MARGIN + row * (note_height + 50)
        
        # 繪製左邊界線
        draw.line([(x_offset, y_offset), (x_offset, y_offset + note_height)], fill="black", width=BARLINE_WIDTH)
        x_offset += BARLINE_WIDTH
        
        for measure_idx in range(measures_in_row):
            for beat in range(MEASURE_BEATS):
                # 隨機選擇音符
                note_idx = random.choice(note_choices)
                note_path = os.path.join(PICS_DIR, f"{note_idx}.png")
                if os.path.exists(note_path):
                    note_img = Image.open(note_path)
                    note_width = random.randint(*note_width_range)
                    note_img = note_img.resize((note_width, note_height), Image.LANCZOS)
                    score_image.paste(note_img, (int(x_offset), int(y_offset)))
                    x_offset += note_width
                else:
                    st.error(f"音符圖片 {note_path} 不存在！")
                    return None
            # 繪製小節線
            draw.line([(x_offset, y_offset), (x_offset, y_offset + note_height)], fill="black", width=BARLINE_WIDTH)
            x_offset += BARLINE_WIDTH
        
        # 繪製右邊界線（如果行未滿）
        if measures_in_row < measures_per_row:
            draw.line([(x_offset, y_offset), (x_offset, y_offset + note_height)], fill="black", width=BARLINE_WIDTH)
    
    return score_image

def save_as_pdf(score_image, filename):
    # 將圖片轉為 A4 PDF
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # A4 尺寸（像素，假設 72 dpi）
    a4_width, a4_height = A4
    img_width, img_height = score_image.size
    scale = min(a4_width / img_width, a4_height / img_height)
    new_width = img_width * scale
    new_height = img_height * scale
    
    # 將 PIL 圖片保存為臨時文件
    temp_img_path = "temp_score.png"
    score_image.save(temp_img_path)
    pdf.drawImage(temp_img_path, (a4_width - new_width) / 2, (a4_height - new_height) / 2, new_width, new_height)
    pdf.save()
    
    pdf_buffer.seek(0)
    with open(filename, "wb") as f:
        f.write(pdf_buffer.read())
    os.remove(temp_img_path)

# Streamlit 界面
st.title("節奏樂譜產生器")

# 難度選擇
difficulty = st.selectbox("選擇難度", ["beginner", "beginner+", "intermediate", "intermediate+", "advanced", "professional"])

# 小節數選擇
min_measures, max_measures = MEASURE_RANGES[difficulty]
num_measures = st.slider("選擇小節數", min_measures, max_measures, min_measures)

# 產生按鈕
if st.button("產生樂譜"):
    score_image = generate_score(difficulty, num_measures)
    if score_image:
        # 顯示樂譜
        st.image(score_image, caption="生成的節奏樂譜")
        
        # 提供下載選項
        img_buffer = io.BytesIO()
        score_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        st.download_button(
            label="下載 PNG",
            data=img_buffer,
            file_name="rhythm_score.png",
            mime="image/png"
        )
        
        # 生成並提供 PDF 下載
        pdf_filename = "rhythm_score.pdf"
        save_as_pdf(score_image, pdf_filename)
        with open(pdf_filename, "rb") as f:
            st.download_button(
                label="下載 PDF",
                data=f,
                file_name=pdf_filename,
                mime="application/pdf"
            )
