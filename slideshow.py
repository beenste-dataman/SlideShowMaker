import os
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip
from datetime import datetime
import random
import concurrent.futures

def get_max_size(image_files):
    max_width = max_height = 0
    for img_file in image_files:
        with Image.open(img_file) as img:
            width, height = img.size
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height
    # Ensure the dimensions are divisible by 2
    max_width = max_width if max_width % 2 == 0 else max_width + 1
    max_height = max_height if max_height % 2 == 0 else max_height + 1
    return max_width, max_height


def pad_img(img_path, size=(1920, 1080), color=(0, 0, 0)):
    with Image.open(img_path) as img:
        width, height = img.size
        new_img = Image.new("RGB", size, color)
        new_img.paste(img, ((size[0] - width) // 2, (size[1] - height) // 2))
        new_path = "/content/padded/" + os.path.basename(img_path) # you can adjust new_path as needed, this is intended to work with an ftp destination and irregularly sized images
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        new_img.save(new_path)
        return new_path

def process_images_concurrently(image_files):
    size = get_max_size(image_files)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return list(executor.map(pad_img, image_files, [size]*len(image_files)))

date_string = datetime.now().strftime("%m-%d")

# Define your image duration and path to images here
img_duration = 0.6  # Each image will display for 0.6 seconds
img_folder = "/content/out"  # Replace with your folder path

# Get list of all image files in the folder
image_files = []
for root, dirs, files in os.walk(img_folder):
    for file in files:
        if file.endswith((".png", ".jpg", ".jpeg")):
            image_files.append(os.path.join(root, file))

# Sort the images by name
image_files.sort()

# Process images concurrently
padded_images = process_images_concurrently(image_files)

random.shuffle(padded_images)



# Create a moviepy clip
clip = ImageSequenceClip(padded_images, durations=[img_duration] * len(padded_images))

# Write the result to a file, this is specifically set to make a video that can play on MacOS and iOS. Can be adjusted. 
clip.write_videofile(
    f"filename-{date_string}.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="8000k",  # Specify bitrate to be high enough for good quality
    ffmpeg_params=["-pix_fmt", "yuv420p"]  # Specify pixel format
)
