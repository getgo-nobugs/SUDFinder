import subprocess
import time
import os
import csv

def list_devices():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.strip().split('\n')[1:]  # Remove the first line 'List of devices attached'

        device_list = []
        for device in devices:
            if device.strip():
                device_list.append(device.split('\t')[0])

        return device_list
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def adb_root(device_id):
    try:
        root_cmd = ['adb', '-s', device_id, 'root']
        print(f"Executing command: {' '.join(root_cmd)}")
        result = subprocess.run(root_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        if 'adbd is already running as root' in result.stdout or 'restarting adbd as root' in result.stdout:
            return True
        else:
            print(f"Failed to elevate device {device_id} to root.")
            return False
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_uninstall(device_id, package_name):
    try:
        uninstall_cmd = ['adb', '-s', device_id, 'uninstall', package_name]
        print(f"Executing command: {' '.join(uninstall_cmd)}")
        result = subprocess.run(uninstall_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        if 'Success' in result.stdout:
            print(f"Successfully uninstalled {package_name} on device {device_id}.")
            return True
        else:
            print(f"Failed to uninstall {package_name} or it was not installed on device {device_id}.")
            return False
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_install(device_id, apk_path):
    try:
        install_cmd = ['adb', '-s', device_id, 'install', apk_path]
        print(f"Executing command: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        if 'Success' in result.stdout:
            print(f"Successfully installed {apk_path} on device {device_id}.")
            return True
        else:
            print(f"Failed to install {apk_path} on device {device_id}.")
            return False
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_pull(device_id, remote_path, local_path):
    try:
        cmd = ['adb', '-s', device_id, 'pull', remote_path, local_path]
        print(f"Executing command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        if result.returncode == 0:
            print(f"Successfully pulled file from {device_id}:{remote_path} to {local_path}")
            return True
        else:
            print(f"Failed to pull {remote_path} from device {device_id}.")
            return False
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_start_app(device_id, package_name, activity_name):
    try:
        start_cmd = ['adb', '-s', device_id, 'shell', 'am', 'start', '-n', f"{package_name}/{activity_name}"]
        print(f"Executing command: {' '.join(start_cmd)}")
        result = subprocess.run(start_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")

        if 'Starting' in result.stdout:
            print(f"Successfully started app {package_name} on device {device_id}.")
            return True
        else:
            print(f"Failed to start app {package_name} on device {device_id}.")
            return False
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_set_text_scale(device_id, scale):
    try:
        # Set text scale
        scale_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'system', 'font_scale', str(scale)]
        print(f"Executing command: {' '.join(scale_cmd)}")
        scale_result = subprocess.run(scale_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{scale_result.stdout}")
        print(f"Stderr:\n{scale_result.stderr}")

        if scale_result.returncode != 0:
            print(f"Failed to set text scale on device {device_id}.")
            return False

        # Disable night mode
        night_mode_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'secure', 'ui_night_mode', '1']
        print(f"Executing command: {' '.join(night_mode_cmd)}")
        night_mode_result = subprocess.run(night_mode_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{night_mode_result.stdout}")
        print(f"Stderr:\n{night_mode_result.stderr}")

        if night_mode_result.returncode != 0:
            print(f"Failed to disable night mode on device {device_id}.")
            return False

        # Disable auto-rotation
        rotation_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'system', 'user_rotation', '0']
        print(f"Executing command: {' '.join(rotation_cmd)}")
        rotation_result = subprocess.run(rotation_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{rotation_result.stdout}")
        print(f"Stderr:\n{rotation_result.stderr}")

        if rotation_result.returncode != 0:
            print(f"Failed to disable auto-rotation on device {device_id}.")
            return False

        print(f"Successfully set text scale to {scale}, disabled night mode, and disabled screen rotation on device {device_id}.")
        return True
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def adb_set_landscape_mode(device_id):
    try:
        # Set device to landscape mode
        landscape_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'system', 'user_rotation', '1']
        print(f"Executing command: {' '.join(landscape_cmd)}")
        landscape_result = subprocess.run(landscape_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{landscape_result.stdout}")
        print(f"Stderr:\n{landscape_result.stderr}")

        if landscape_result.returncode != 0:
            print(f"Failed to set landscape mode on device {device_id}.")
            return False

        # Disable night mode
        night_mode_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'secure', 'ui_night_mode', '1']
        print(f"Executing command: {' '.join(night_mode_cmd)}")
        night_mode_result = subprocess.run(night_mode_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{night_mode_result.stdout}")
        print(f"Stderr:\n{night_mode_result.stderr}")

        if night_mode_result.returncode != 0:
            print(f"Failed to disable night mode on device {device_id}.")
            return False

        # Set text scale to 1.0
        scale_cmd = ['adb', '-s', device_id, 'shell', 'cmd', 'settings', 'put', 'system', 'font_scale', '1.0']
        print(f"Executing command: {' '.join(scale_cmd)}")
        scale_result = subprocess.run(scale_cmd, capture_output=True, text=True)
        print(f"Stdout:\n{scale_result.stdout}")
        print(f"Stderr:\n{scale_result.stderr}")

        if scale_result.returncode != 0:
            print(f"Failed to set text scale on device {device_id}.")
            return False

        print(f"Successfully set landscape mode, disabled night mode, and set text scale to 1.0 on device {device_id}.")
        return True
    except Exception as e:
        print(f"Exception occurred on device {device_id}: {e}")
        return False

def read_app_info(csv_file):
    try:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            app_info = [row for row in reader]
        return app_info
    except Exception as e:
        print(f"Exception occurred while reading CSV file: {e}")
        return []

def main():
    # modes = ["1", "2.5", "rot"]  # Modes to run in sequence
    modes = ["ara"]  # Modes to run in sequence
    devices = list_devices()
    if not devices:
        print("No devices found.")
        return

    apk_directory = '/Users/huanghuaxun/PycharmProjects/setdiff/v2/apk_utils/temp/'
    csv_file = 'app_info.csv'  # CSV file containing package_name, activity_name, and app_name
    generated_data_dir = './generated_data/'

    app_info_list = read_app_info(csv_file)
    if not app_info_list:
        print("No app information found in the CSV file.")
        return

    # Get all .apk files in the directory
    apk_files = [f for f in os.listdir(apk_directory) if f.endswith('.apk')]

    if not apk_files:
        print("No APK files found in the directory.")
        return

    for device_id in devices:
        if adb_root(device_id):
            for mode in modes:
                if mode == "1":
                    adb_set_text_scale(device_id, 1.0)
                elif mode == "2.5":
                    adb_set_text_scale(device_id, 2.0)
                elif mode == "rot":
                    adb_set_landscape_mode(device_id)

                for apk_file in apk_files:
                    apk_path = os.path.join(apk_directory, apk_file)
                    apk_name = os.path.splitext(apk_file)[0]

                    # Check if any file in generated_data_dir starts with {mode}_{apk_name}
                    if any(f.startswith(f"{mode}_{apk_name}") for f in os.listdir(generated_data_dir)):
                        print(f"Skipping {apk_file} as data already exists.")
                        continue

                    for app_info in app_info_list:
                        package_name = app_info['package_name']
                        activity_name = app_info['activity_name']
                        app_name = app_info['app_name']

                        # Skip APK files that do not contain the app_name
                        if app_name not in apk_name:
                            continue

                        adb_uninstall(device_id, package_name)
                        time.sleep(4)
                        if adb_install(device_id, apk_path):
                            if adb_start_app(device_id, package_name, activity_name):
                                # Wait for 15 seconds to let the app run
                                time.sleep(10)
                                remote_paths = [
                                    f'/data/data/{package_name}/files/view_tree.txt',
                                    f'/data/data/{package_name}/files/font.txt',
                                    f'/data/data/{package_name}/files/screenshot.png'
                                ]
                                for remote_path in remote_paths:
                                    filename = remote_path.split('/')[-1]
                                    local_path = os.path.join(generated_data_dir, f"{mode}_{apk_name}_{device_id}_{filename}")
                                    adb_pull(device_id, remote_path, local_path)

if __name__ == "__main__":
    main()