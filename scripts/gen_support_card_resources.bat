cd ..
python tools/extract_support_card_icon.py
python tools/upload_image_to_cloudinary.py -i tools/images/supportcard/icon -o output/supportcard_icon_mapping.json -s public_id:support_card_s_*
python tools/upload_image_to_cloudinary.py -i tools/images/supportcard/cover -o output/supportcard_cover_mapping.json -w 512 -h 682 -s public_id:support_thumb_*