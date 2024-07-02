import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random

# Function to create a random beat
def create_beat():
    beats = [
        "𝅘𝅥 ",               # 四分音符
        "𝄾  𝅘𝅥𝅮",             # 八分休止符 + 八分音符
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
    img_width = 1000
    img_height = 200 + len(sheet_music)*50 # (4各一列 列高200)
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Bravura.otf", 40)  # Update with the path to your font
    
    y = 20
    j = 0
    x = 20
    for measure in sheet_music:
        for beat in measure:
            draw.text((x, y), beat, font=font, fill='black')
            x += 50
        # Draw measure line
        draw.line([(x, y + 40), (x, y + 90)], fill='black', width=2)
        x += 25
        j = j + 1
        if j % 4 == 0:
            x = 20
            y = y + 200

    return img

st.title("Random Sheet Music Generator")

num_measures = st.slider("Select number of measures:", min_value=1, max_value=40, value=8)
sheet_music = create_sheet_music(num_measures)
sheet_music_img = draw_sheet_music(sheet_music)

sheet_music_img_path = "sheet_music.png"
sheet_music_img.save(sheet_music_img_path)

st.image(sheet_music_img, caption="Generated Sheet Music")

# Download link
with open(sheet_music_img_path, "rb") as file:
    btn = st.download_button(
        label="Download Image",
        data=file,
        file_name="sheet_music.png",
        mime="image/png"
    )
