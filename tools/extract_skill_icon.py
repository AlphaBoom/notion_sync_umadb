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

def getIconPath(hex):
    return os.path.join(game_data_path, 'dat', hex[:2], hex)

def getAllIconsPathFromDB(db_path:str)->list[str]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT h FROM a WHERE n like 'outgame/skillicon/utx_ico_skill_%'")
    hex_list = c.fetchall()
    c.close()
    return [getIconPath(hex[0]) for hex in hex_list ]

if __name__ == "__main__":
    # destination folder
    destination_folder = "tools/images/"
    # unpack all assets
    unpack_all_assets(getAllIconsPathFromDB(os.path.join(game_data_path, 'meta')), destination_folder)