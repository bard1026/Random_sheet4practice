# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 23:34:49 2025

@author: bard1
"""

import streamlit as st
from PIL import Image, ImageDraw
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
    
    # 限制小節數
    if difficulty in ["beginner", "beginner+"]:
        num_measures = min(num_measures, 27)  # 最多27小節
        measures_per_line = 3
    else:
        num_measures = min(num_measures, 18)  # 最多18小節
        measures_per_line = 2
    
    measure_images = []
    for _ in range(num_measures):
        measure = []
        for _ in range(4):  # 每小節四拍
            note_id = random.choice(note_ids)
            img_path = os.path.join(IMAGE_FOLDER, f"{note_id}.png")
            img = Image.open(img_path)
            measure.append(img)
        measure_images.append(measure)

    notes_per_measure = 4
    notes_per_line = measures_per_line * notes_per_measure

    sheet_width = 2600
    left_margin = 100
    right_margin = 2500
    usable_width = right_margin - left_margin

    max_height = 265
    line_height = max_height + 55  # 留白空間

    img_lines = []
    y = 30

    for line_start in range(0, len(measure_images), measures_per_line):
        current_line = Image.new('RGB', (sheet_width, line_height), 'white')
        draw = ImageDraw.Draw(current_line)

        this_line_measures = measure_images[line_start:line_start+measures_per_line]
        flat_images = [img for measure in this_line_measures for img in measure]

        # 動態調整圖片大小以避免太寬（針對 intermediate 到 professional）
        total_image_width = sum(img.width for img in flat_images)
        if difficulty in ["intermediate", "intermediate+", "advanced", "professional"]:
            scale_factor = min(1.0, usable_width / total_image_width) if total_image_width > usable_width else 1.0
            flat_images = [
                img.resize((int(img.width * scale_factor), int(img.height * scale_factor)), resample=Image.LANCZOS)
                for img in flat_images
            ]
            total_image_width = sum(img.width for img in flat_images)

        spacing = 0
        full_line = len(this_line_measures) == measures_per_line
        if full_line:
            spacing = (usable_width - total_image_width) // (notes_per_line - 1) if notes_per_line > 1 else 0

        x = left_margin
        count = 0
        for img in flat_images:
            current_line.paste(img, (x, y))
            x += img.width
            if count < len(flat_images) - 1:
                x += spacing
            count += 1
            # 畫小節線（每 4 張圖片後）
            if count % notes_per_measure == 0:
                sep_x = x - spacing // 2 if full_line else x
                draw.line([(sep_x, y), (sep_x, y + max_height)], fill='black', width=3)

        img_lines.append(current_line)

    # 合併所有行
    full_height = line_height * len(img_lines)
    sheet_img = Image.new('RGB', (sheet_width, full_height), 'white')
    for i, line_img in enumerate(img_lines):
        sheet_img.paste(line_img, (0, i * line_height))

    return sheet_img

def export_to_pdf(image, filename="sheet_music.pdf"):
    try:
        pdf = FPDF(unit="pt", format="A4")
        pdf.add_page()
        
        # A4尺寸：595 x 842 pt（1英寸 = 72 pt）
        margin_top_bottom_right = 0.5 * 72  # 0.5英寸 = 36 pt
        margin_left = 0.74653 * 72  # 0.74653英寸 ≈ 53.75 pt
        
        # 計算可用寬度
        img_width = 595 - margin_left - margin_top_bottom_right  # 595 - 53.75 - 36 ≈ 505.25 pt
        img_height = image.size[1] * (img_width / image.size[0])  # 按比例縮放
        
        temp_path = "temp_sheet.png"
        image.save(temp_path)
        
        # 檢查臨時檔案是否存在
        if not os.path.exists(temp_path):
            st.error(f"臨時圖片檔案 {temp_path} 生成失敗！")
            return False
        
        pdf.image(temp_path, x=margin_left, y=margin_top_bottom_right, w=img_width)
        pdf.output(filename)
        
        # 檢查 PDF 檔案是否存在
        if not os.path.exists(filename):
            st.error(f"PDF 檔案 {filename} 生成失敗！")
            return False
        
        st.success(f"PDF 檔案 {filename} 已生成！")
        return True
    
    except Exception as e:
        st.error(f"匯出 PDF 時發生錯誤：{str(e)}")
        return False
    finally:
        # 清理臨時檔案（即使發生錯誤）
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                st.warning(f"無法刪除臨時檔案 {temp_path}：{str(e)}")

# Streamlit 介面
st.title("節奏樂譜產生器")

difficulty = st.selectbox("選擇難度：", list(DIFFICULTY_MAP.keys()))
# 根據難度設置小節數上限
max_measures = 27 if difficulty in ["beginner", "beginner+"] else 18
num_measures = st.slider("選擇小節數：", min_value=1, max_value=max_measures, value=8)

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

    # 將 PDF 匯出和下載邏輯合併，確保按鈕點擊後立即處理
    if st.button("匯出成 A4 PDF"):
        success = export_to_pdf(sheet_img)
        if success:
            try:
                with open("sheet_music.pdf", "rb") as file:
                    st.download_button(
                        label="下載 PDF 樂譜",
                        data=file,
                        file_name="sheet_music.pdf",
                        mime="application/pdf",
                        key="pdf_download"  # 添加唯一鍵避免衝突
                    )
            except FileNotFoundError:
                st.error("PDF 檔案未找到，無法提供下載！")
            except Exception as e:
                st.error(f"下載 PDF 時發生錯誤：{str(e)}")
