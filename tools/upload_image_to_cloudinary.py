# Import
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import cloudinary
from dotenv import load_dotenv
import os
import json
import getopt
import sys

load_dotenv()

# Config
cloudinary.config(
    cloud_name="djdwogbsk",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def upload_to_cloudinary(source_dir:str, output:str, width:int, height:int, crop:str):
    mapping = {}
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            public_id = file.split(".")[0]
            print(f"Uploading {file}...")
            upload(os.path.join(source_dir, file), public_id=public_id)
            url, options = cloudinary_url(
                public_id, width=width, height=height, crop=crop)
            mapping[public_id] = url

    with open(output, "w") as f:
        json.dump(mapping, f, indent=4)


if __name__ == "__main__":
    try:
      opts,args = getopt.getopt(sys.argv[1:],"i:o:w:h:c:")
    except getopt.GetoptError:
        print("upload_skill_icon_to_cloudinary.py -i <input_dir> -o <output_file> -w <width> -h <height> -c <crop>")
        sys.exit(2)
    input_dir = ""
    output_file = ""
    width = 280
    height = 280
    crop = "fill"
    for opt, arg in opts:
        if opt == "-i":
            input_dir = arg
        elif opt == "-o":
            output_file = arg
        elif opt == "-w":
            width = int(arg)
        elif opt == "-h":
            height = int(arg)
        elif opt == "-c":
            crop = arg
    if input_dir == "" or output_file == "":
        print("upload_skill_icon_to_cloudinary.py -i <input_dir> -o <output_file> -w <width> -h <height> -c <crop>")
        sys.exit(2)
    upload_to_cloudinary(input_dir, output_file, width, height, crop)

