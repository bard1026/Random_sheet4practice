import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random

# Function to create a random beat
def create_beat():
    beats = [
        "𝅘𝅥",               # 四分音符
        "𝄾  𝅘𝅥𝅮",             # 八分休止符 + 八分音符
        "𝅘𝅥𝅮  𝄾",
        "♫"              # 八分音符 + 八分音符
    ]
    return random.choice(beats)

# Function to create a measure with four beats
def create_measure():
    return [create_beat() for _ in range(4)]

# Function to create sheet music with specified number of measures
def create_sheet_music(num_measures):
    sheet_music = [create_measure() for _ in range(num_measures)]
    return sheet_music

# Function to draw sheet music
def draw_sheet_music(sheet_music):
    # A4 size in points (100 PPI)
    img_width = 210 * 100 / 25.4  # A4 width in points
    img_height = 297 * 100 / 25.4  # A4 height in points
    
    img_width = int(img_width) # 826 in 100 PPI
    img_height = int(img_height) #1169 in 100 PPI

    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Bravura.otf", 40)  # Update with the path to your font
    
    y = 60
    x = 10
    J = 0
    # Draw 打擊譜號 line
    draw.line([(x, y + 50), (x, y + 90)], fill='black', width=6)
    x += 10
    draw.line([(x, y + 50), (x, y + 90)], fill='black', width=6)
    x += 10
    for measure in sheet_music:
        for beat in measure:
            draw.text((x, y), beat, font=font, fill='black')
            x += 45  # Adjust spacing as needed
        # Draw measure line
        x += 10
        draw.line([(x, y + 40), (x, y + 80)], fill='black', width=2)
        J += 1
        x += 10
        if J == 4:  # Check if it exceeds width
            J = 0
            x = 10
            y += 80  # Adjust line height as needed
            # 換行再 Draw 打擊譜號 line
            draw.line([(x, y + 40), (x, y + 80)], fill='black', width=6)
            x += 10
            draw.line([(x, y + 40), (x, y + 80)], fill='black', width=6)
            x += 10
        if y > img_height:  # Check if it exceeds height
            break

    return img
    
def save_as_pdf(image, path):
    image.save(path, "PDF", resolution=100.0)

# Streamlit app code
st.title("Random Sheet Music Generator")

num_measures = st.slider("Select number of measures:", min_value=1, max_value=40, value=8)
sheet_music = create_sheet_music(num_measures)
sheet_music_img = draw_sheet_music(sheet_music)

pdf_path = "sheet_music.pdf"
save_as_pdf(sheet_music_img, pdf_path)

st.image(sheet_music_img, caption="Generated Sheet Music")

# Download link for PDF
with open(pdf_path, "rb") as file:
    btn = st.download_button(
        label="Download PDF",
        data=file,
        file_name="sheet_music.pdf",
        mime="application/pdf"
    )
