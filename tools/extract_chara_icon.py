import os
import UnityPy
import sqlite3
import re

game_data_path = os.path.join(os.path.expanduser('~'),'AppData','LocalLow','Cygames','umamusume')

def unpack_all_assets(files:dict[int, str], destination_folder:str, prefix:str=""):
    for id, file in files.items():
        # load that file via UnityPy.load
        env = UnityPy.load(file)

        # iterate over internal objects
        for obj in env.objects:
            # process specific object types
            if obj.type.name in ["Texture2D", "Sprite"]:
                # parse the object data
                data = obj.read()

                name = f"{prefix}_{id}"
                # create destination path
                dest = os.path.join(destination_folder, name)

                # make sure that the extension is correct
                # you probably only want to do so with images/textures
                dest, ext = os.path.splitext(dest)
                dest = dest + ".png"

                img = data.image
                img.save(dest)

def getFilePath(hex):
    return os.path.join(game_data_path, 'dat', hex[:2], hex)

def getCoverAndIconPathFromDB(master_db_path, meta_db_path):
    conn = sqlite3.connect(master_db_path)
    c = conn.cursor()
    c.execute("SELECT card_id,get_dress_id_2 FROM card_rarity_data")
    id_dress_dict = {row[0]:row[1] for row in c.fetchall() if row[1] > 0}
    c.close()
    conn = sqlite3.connect(meta_db_path)
    c = conn.cursor()
    c.execute("SELECT n,h FROM a WHERE n like 'chara/chr%' AND m='chara'")
    hex_dict = { row[0]:row[1] for row in c.fetchall()}
    c.close()
    cover_dict = {}
    icon_dict = {}
    for id,dress_id in id_dress_dict.items():
        str_id = str(id)
        cover_path_key = f'chara/chr{str_id[:4]}/chara_stand_{str_id[:4]}_{dress_id}'
        icon_path_key = f'chara/chr{str_id[:4]}/chr_icon_{str_id[:4]}_{dress_id}_02'
        if cover_path_key in hex_dict:
            cover_dict[id] = getFilePath(hex_dict[cover_path_key])
        else:
            print(f'cover_path_key {cover_path_key} not found')
        if icon_path_key in hex_dict:
            icon_dict[id] = getFilePath(hex_dict[icon_path_key])
        else:
            print(f'icon_path_key {icon_path_key} not found')
    return (cover_dict, icon_dict)

if __name__ == "__main__":
    # destination folder
    destination_icon_folder = "tools/images/chara/icon"
    destination_cover_folder = "tools/images/chara/cover"
    if not os.path.exists(destination_icon_folder):
        os.makedirs(destination_icon_folder)
    if not os.path.exists(destination_cover_folder):
        os.makedirs(destination_cover_folder)
    # unpack all assets
    cover_dict, icon_dict = getCoverAndIconPathFromDB(os.path.join(game_data_path, 'master', 'master.mdb'), os.path.join(game_data_path, 'meta'))
    unpack_all_assets(cover_dict, destination_cover_folder, prefix="chara_cover")
    unpack_all_assets(icon_dict, destination_icon_folder, prefix="chara_icon")