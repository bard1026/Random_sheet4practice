# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 23:34:49 2025

@author: bard1
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
from fpdf import FPDF

# 圖片資料夾路徑
IMAGE_FOLDER = "pics"  # 圖片需命名為 0.png ~ 15.png

# 難度對應圖庫索引
DIFFICULTY_MAP = {
    "beginner": [0, 1, 2],
    "beginner+": [0, 1, 2, 3],
    "intermediate": [0, 1, 4, 5, 6, 7, 15],
    "intermediate+": [0, 1, 2, 3, 4, 5, 6, 7, 15],
    "advanced": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15],
    "professional": list(range(0, 16))
}

# 產生一張樂譜圖片
def generate_sheet_music(difficulty, num_measures):
    note_ids = DIFFICULTY_MAP[difficulty]
    measure_images = []
    for _ in range(num_measures):
        measure = []
        for _ in range(4):  # 每小節四拍
            note_id = random.choice(note_ids)
            img_path = os.path.join(IMAGE_FOLDER, f"{note_id}.png")
            img = Image.open(img_path)
            measure.append(img)
        measure_images.append(measure)

    # 配置參數
    measures_per_line = 3
    notes_per_measure = 4
    notes_per_line = measures_per_line * notes_per_measure  # 12
    sheet_width = 2600
    left_margin = 100
    right_margin = 2500
    usable_width = right_margin - left_margin  # 2400
    spacing_slots = notes_per_line + (measures_per_line - 2)  # 11 + 2 = 13
    spacing = usable_width // spacing_slots
    max_height = 265
    line_height = max_height + 55  # 留一點空隙

    # 圖片行初始化
    img_lines = []
    current_line = Image.new('RGB', (sheet_width, line_height), 'white')
    draw = ImageDraw.Draw(current_line)
    x = left_margin
    y = 30
    count = 0

    for measure in measure_images:
        for idx, img in enumerate(measure):
            current_line.paste(img, (x, y))
            x += img.width + spacing
            count += 1
            # 插入分隔線（在每小節之後，但不要在最後一個小節）
            if count % 4 == 0 and (count // 4) % 3 != 0:
                draw.line([(x - spacing // 2, y), (x - spacing // 2, y + max_height)], fill='black', width=3)

        # 換行邏輯：每 3 小節（12 張圖）換行
        if count % (notes_per_measure * measures_per_line) == 0:
            img_lines.append(current_line)
            current_line = Image.new('RGB', (sheet_width, line_height), 'white')
            draw = ImageDraw.Draw(current_line)
            x = left_margin

    # 收尾行
    if count % notes_per_line != 0:
        img_lines.append(current_line)

    # 組合所有行成一張長圖
    full_height = line_height * len(img_lines)
    sheet_img = Image.new('RGB', (sheet_width, full_height), 'white')
    for idx, line_img in enumerate(img_lines):
        sheet_img.paste(line_img, (0, idx * line_height))

    return sheet_img

# 匯出成 A4 PDF
def export_to_pdf(image, filename="sheet_music.pdf"):
    pdf = FPDF(unit="pt", format="A4")
    pdf.add_page()
    temp_path = "temp_sheet.png"
    image.save(temp_path)
    pdf.image(temp_path, x=20, y=20, w=555)  # A4寬度約595pt，留邊界
    pdf.output(filename)
    os.remove(temp_path)

# Streamlit 介面
st.title("節奏樂譜產生器")

difficulty = st.selectbox("選擇難度：", list(DIFFICULTY_MAP.keys()))
num_measures = st.slider("選擇小節數：", min_value=1, max_value=40, value=8)

if st.button("產生樂譜"):
    sheet_img = generate_sheet_music(difficulty, num_measures)
    sheet_img_path = "sheet_music.png"
    sheet_img.save(sheet_img_path)
    # 預覽用縮圖（等比例）
    preview_width = 800
    w_percent = (preview_width / float(sheet_img.size[0]))
    h_size = int((float(sheet_img.size[1]) * float(w_percent)))
    preview_img = sheet_img.resize((preview_width, h_size), resample=Image.LANCZOS)
    st.image(preview_img, caption="產生的樂譜", width=800)

    with open(sheet_img_path, "rb") as file:
        st.download_button(
            label="下載 PNG 圖片",
            data=file,
            file_name="sheet_music.png",
            mime="image/png"
        )

    if st.button("匯出成 A4 PDF"):
        export_to_pdf(sheet_img)
        with open("sheet_music.pdf", "rb") as file:
            st.download_button(
                label="下載 PDF 樂譜",
                data=file,
                file_name="sheet_music.pdf",
                mime="application/pdf"
            )
