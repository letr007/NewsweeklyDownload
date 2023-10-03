import shutil, os

print("复制文件...")
shutil.copytree("./ffmpeg/", "C:/ffmpeg")
ffmpeg_path = 'C:\\ffmpeg\\bin'
print("添加环境变量...")
os.environ["PATH"] = ffmpeg_path + ";" + os.environ["PATH"]
