# Import
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import cloudinary
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Config
cloudinary.config(
  cloud_name = "djdwogbsk",
  api_key = os.getenv("CLOUDINARY_API_KEY"),
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

mapping = {}

for root, dirs, files in os.walk("tools/images"):
    for file in files:
        public_id = file.split(".")[0]
        print(f"Uploading {file}...")
        upload("tools/images/"+file, public_id=public_id)
        url,options = cloudinary_url(public_id, width=280, height=280, crop="fill")
        mapping[public_id] = url

with open("output/skill_icon_mapping.json", "w") as f:
    json.dump(mapping, f, indent=4)

