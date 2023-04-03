import os
import UnityPy
import sqlite3
from PIL import Image

game_data_path = os.path.join(os.path.expanduser('~'),'AppData','LocalLow','Cygames','umamusume')

def unpack_all_assets(files:list[str], destination_folder:str, filter_func = None):
    for file in files:
        # load that file via UnityPy.load
        env = UnityPy.load(file)

        # iterate over internal objects
        for obj in env.objects:
            # process specific object types
            if obj.type.name in ["Texture2D", "Sprite"]:
                # parse the object data
                data = obj.read()
                if filter_func and not filter_func(data.name):
                    continue
                # create destination path
                dest = os.path.join(destination_folder, data.name)

                # make sure that the extension is correct
                # you probably only want to do so with images/textures
                dest, ext = os.path.splitext(dest)
                dest = dest + ".png"

                img = data.image
                img.save(dest)

def getIconPath(hex):
    return os.path.join(game_data_path, 'dat', hex[:2], hex)

def getAllPathFromDB(db_path:str, mime_type:str)->list[str]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT h FROM a WHERE m = '{mime_type}'")
    hex_list = c.fetchall()
    c.close()
    return [getIconPath(hex[0]) for hex in hex_list ]

def extract_icon(destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    # unpack all assets
    unpack_all_assets(getAllPathFromDB(os.path.join(game_data_path, 'meta'),'supportcard'), destination_folder, lambda x: x.lower().startswith("support_card_s"))

def create_card_cover(dest_dir, thumb_dir, accesory_dir):
    conn = sqlite3.connect(os.path.join(game_data_path,"master","master.mdb"))
    c = conn.cursor()
    c.execute("SELECT id,rarity,command_id,support_card_type FROM support_card_data")
    info_dict = { row[0]: row[1:] for row in c.fetchall()}
    for root, dirs, files in os.walk(thumb_dir):
        for file in files:
            card_id = int(file.split('.')[0].rsplit('_', 1)[-1])
            if card_id not in info_dict:
                print(f"card_id {card_id} not found")
                continue
            info = info_dict[card_id]
            thumb_image = Image.open(os.path.join(thumb_dir, file))
            rairty_image = Image.open(os.path.join(accesory_dir,f"utx_ico_rarity_{info[0]-1:02}.png"))
            command_id = info[1]
            index = 0
            if command_id == 0:
                if info[2] == 2:
                    index = 5
                elif info[2] == 3:
                    index = 6
            else:
                if command_id == 101:
                    index = 0
                elif command_id == 102:
                    index = 2
                elif command_id == 103:
                    index = 3
                elif command_id == 105:
                    index = 1
                elif command_id == 106:
                    index = 4
            obtain_image = Image.open(os.path.join(accesory_dir,f"utx_ico_obtain_{index:02}.png"))
            thumb_image = thumb_image.resize((512, 682))
            obtain_image = obtain_image.resize((76,76))
            rairty_image = rairty_image.resize((94,94))
            thumb_image.paste(rairty_image, (20, 7), rairty_image)
            thumb_image.paste(obtain_image, (425, 7), obtain_image)
            thumb_image.save(os.path.join(dest_dir, f"support_thumb_{card_id}.png"))
        

def extract_cover(destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    cover_thumb_dir = os.path.join(destination_folder, "thumb")
    accessory_dir = os.path.join(destination_folder, "accessory")
    if not os.path.exists(cover_thumb_dir):
        os.makedirs(cover_thumb_dir)
    if not os.path.exists(accessory_dir):
        os.makedirs(accessory_dir)
    unpack_all_assets(getAllPathFromDB(os.path.join(game_data_path, 'meta'), 'supportcard'), cover_thumb_dir, lambda x: x.lower().startswith("support_thumb"))
    unpack_all_assets(getAllPathFromDB(os.path.join(game_data_path, 'meta'), 'atlas'), accessory_dir, lambda x: x.lower().startswith("utx_ico_rarity_") or x.lower().startswith("utx_ico_obtain_"))
    create_card_cover(destination_folder, cover_thumb_dir, accessory_dir)


if __name__ == "__main__":
    # icon folder
    destination_icon_folder = "tools/images/supportcard/icon"
    extract_icon(destination_icon_folder)
    # cover folder
    destination_cover_folder = "tools/images/supportcard/cover"
    extract_cover(destination_cover_folder)