cd ..
python tools/extract_skill_icon.py
python tools/upload_image_to_cloudinary.py -i tools/images/skill_icon -o output/skill_icon_mapping.json -s public_id:utx_ico_skill_*