import os
import zipfile
import configparser

def zip_folder_to_apk(folder_path, apk_path):
    with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                apk.write(file_path, arcname=os.path.relpath(file_path, folder_path))

if __name__ == "__main__":
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    folder = config['settings']['folder_path']
    output_apk = config['settings'].get('output_apk', 'output_file.apk')
    
    zip_folder_to_apk(folder, output_apk)
    print(f"Packaged contents of {folder} into {output_apk}")
