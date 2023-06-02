import os
import UnityPy
import sqlite3

game_data_path = os.path.join(os.path.expanduser('~'),'AppData','LocalLow','Cygames','umamusume')

def unpack_all_assets(files:list[str], destination_folder:str):
    for file in files:
        # load that file via UnityPy.load
        env = UnityPy.load(file)

        # iterate over internal objects
        for obj in env.objects:
            # process specific object types
            if obj.type.name in ["Texture2D", "Sprite"]:
                # parse the object data
                data = obj.read()

                # create destination path
                dest = os.path.join(destination_folder, data.name)

                # make sure that the extension is correct
                # you probably only want to do so with images/textures
                dest, ext = os.path.splitext(dest)
                dest = dest + ".png"

                img = data.image
                img.save(dest)

def getPath(hex):
    return os.path.join(game_data_path, 'dat', hex[:2], hex)

def getAllPathFromDB(db_path:str)->list[str]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT h FROM a WHERE m = 'chara'")
    hex_list = c.fetchall()
    c.close()
    return [getPath(hex[0]) for hex in hex_list ]

if __name__ == "__main__":
    # destination folder
    destination_folder = "tools/images/chara"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    # unpack all assets
    unpack_all_assets(getAllPathFromDB(os.path.join(game_data_path, 'meta')), destination_folder)