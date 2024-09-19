import subprocess
import os
import shutil
import sys

def build_apk(project_directory):
    """
    在指定的 Android 项目目录中运行 ./gradlew assembleDebug 生成 APK，并输出生成的 APK 文件路径。

    :param project_directory: Android 项目根目录的路径
    """
    # 保存当前工作目录
    current_dir = os.getcwd()

    try:
        # 切换到 Android 项目目录
        os.chdir(project_directory)
        print(project_directory)

        result = subprocess.run(
            ['./gradlew', 'assembleDebug'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 检查命令是否成功执行
        if result.returncode == 0:
            print("APK build succeeded!")
            # 查找生成的 APK 文件
            apk_files = []
            for root, dirs, files in os.walk(project_directory):
                for file in files:
                    if file.endswith('.apk') and str(file).__contains__('v8a'):
                    # if file.endswith('.apk'):
                        apk_files.append(os.path.join(root, file))

            if apk_files:
                for apk_path in apk_files:
                    print(f"Generated APK path: {apk_path}")
                return apk_files[0]
            else:
                print("APK file not found.")
        else:
            print("APK build failed!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 切换回原来的工作目录
        os.chdir(current_dir)


def get_layout_files_as_r_layout(project_directory):
    """
    获取指定 Android 项目 res 文件夹下所有 layout 文件，以 R.layout 形式返回。

    :param project_directory: Android 项目根目录的路径
    :return: R.layout 形式的 layout 文件名列表
    """
    r_layout_files = []
    res_directory = ''

    # for dirpath, dirnames, _ in os.walk(project_directory):
    #     for dirname in dirnames:
    #         print(os.path.join(dirpath, dirname))

    # 在指定目录中找到 res 文件夹
    for root, dirs, files in os.walk(project_directory):
        for dir in dirs:
            dirname = os.path.join(root, dir)
            if dirname.endswith('/res') and dirname.__contains__('main') and \
                    res_directory.__contains__("/generated/") == False:
                res_directory = dirname
                for root, dirs, files in os.walk(res_directory):
                    for dir_name in dirs:
                        if dir_name.startswith('layout') and dir_name.__contains__("menu") == False:
                            layout_directory = os.path.join(root, dir_name)

                            print(layout_directory)
                            for file in os.listdir(layout_directory):
                                if file.endswith('.xml'):
                                    layout_name = os.path.splitext(file)[0]
                                    r_layout_files.append(f"R.layout.{layout_name}")

    return r_layout_files


def find_file(project_directory, filename):
    """
    在指定的 Android 项目目录中查找特定文件。

    :param project_directory: Android 项目根目录的路径
    :param filename: 要查找的文件名
    :return: 文件的完整路径，如果未找到则返回 None
    """
    for root, dirs, files in os.walk(project_directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def replace_set_content_view_line(file_path, new_set_content_view_line):
    """
    在指定文件中查找包含 setContentView 的那一行，并用新的 setContentView 替换它。

    :param file_path: 文件的完整路径
    :param new_set_content_view_line: 新的 setContentView 字符串
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                if 'setContentView' in line:
                    file.write(f"{new_set_content_view_line}\n")
                else:
                    file.write(line)

        print(f"Replaced setContentView lines in {file_path}.")
        file.close()

    except Exception as e:
        print(f"An error occurred while modifying {file_path}: {e}")


def rename_and_move_apk(apk_path, project_name, layout_name):
    """
    重命名 APK 文件为项目名称和 layout 名称的组合，并将其移动到 Python 根目录下的 temp 文件夹。

    :param apk_path: 原始 APK 文件路径
    :param project_name: 项目名称
    :param layout_name: layout 名称
    """
    try:
        # 获取项目名称
        project_name = os.path.basename(os.path.normpath(project_dir))

        # 获取 Python 根目录
        python_root_directory = os.path.dirname(os.path.abspath(__file__))

        # temp 文件夹路径
        temp_directory = os.path.join(python_root_directory, 'temp')

        # 新的 APK 文件名和路径
        new_apk_name = f"{project_name}_{layout_name}.apk"
        new_apk_path = os.path.join(temp_directory, new_apk_name)

        # 移动并重命名 APK 文件
        os.rename(apk_path, new_apk_path)

        print(f"APK renamed and moved to: {new_apk_path}")
    except Exception as e:
        print(f"An error occurred while renaming and moving APK: {e}")

if __name__ == "__main__":
    project_dir = "/Users/h/Documents/GitHub/setdiff_dataset/LibreTube"

    # 获取项目名称
    project_name = os.path.basename(os.path.normpath(project_dir))
    # 获取 Python 根目录
    python_root_directory = os.path.dirname(os.path.abspath(__file__))

    # temp 文件夹路径
    temp_directory = os.path.join(python_root_directory, 'temp')

    # # 如果 temp 文件夹存在，先删除它
    # if os.path.exists(temp_directory):
    #     shutil.rmtree(temp_directory)
    #
    # # 重新创建 temp 文件夹
    # os.makedirs(temp_directory, exist_ok=True)

    # 获取 layout 文件并转换成 R.layout 形式
    r_layout_files = get_layout_files_as_r_layout(project_dir)
    set_content_view_lines = [f"setContentView({r_layout_file});" for r_layout_file in r_layout_files]
    print("Generated setContentView lines:")
    for line in set_content_view_lines:
        print(line)

    # 查找 SetDiffActivity.java 文件
    target_file = "SetDiffActivity.java"
    file_path = find_file(project_dir, target_file)
    if file_path:
        # 替换 setContentView 的那一行
        for set_content_view_line in set_content_view_lines:
            layout_name = set_content_view_line.split('(')[1].split(')')[0].split('.')[-1]
            replace_set_content_view_line(file_path, set_content_view_line)
            print(f"Found {target_file} at: {file_path}")
            # 生成 APK
            apk_path = build_apk(project_dir)
            if apk_path:
                # 重命名 APK 文件
                rename_and_move_apk(apk_path, project_name, layout_name)
                # exit(0)
    else:
        print(f"{target_file} not found in the project.")