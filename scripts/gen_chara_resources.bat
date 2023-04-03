cd ..
python tools/extract_chara_icon.py
python tools/upload_image_to_cloudinary.py -i tools/images/chara/icon -o output/chara_icon_mapping.json -s public_id:chara_icon_*
python tools/upload_image_to_cloudinary.py -i tools/images/chara/cover -o output/chara_cover_mapping.json -w 512 -h 512 -s public_id:chara_cover_*