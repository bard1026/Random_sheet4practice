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
    # A4 size in points (1 point = 1/72 inch)
    img_width = 210 * 72 / 25.4  # A4 width in points
    img_height = 297 * 72 / 25.4  # A4 height in points
    
    img_width = int(img_width)
    img_height = int(img_height)

    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Bravura.otf", 40)  # Update with the path to your font
    
    y = 50
    x = 50
    for measure in sheet_music:
        for beat in measure:
            draw.text((x, y), beat, font=font, fill='black')
            x += 100  # Adjust spacing as needed
        # Draw measure line
        draw.line([(x, y + 40), (x, y + 90)], fill='black', width=2)
        x += 50
        if x > img_width - 200:  # Check if it exceeds width
            x = 50
            y += 100  # Adjust line height as needed
        if y > img_height - 100:  # Check if it exceeds height
            break

    return img
    
def save_as_pdf(image, path):
    image.save(path, "PDF", resolution=300.0)
