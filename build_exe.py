import PyInstaller.__main__
import os
import sys

def build():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    
    # 查找 akshare 的数据文件目录
    try:
        import akshare
        akshare_path = os.path.dirname(akshare.__file__)
        akshare_data_path = os.path.join(akshare_path, "file_fold")
        
        if not os.path.exists(akshare_data_path):
            print(f"警告: 未找到 AkShare 数据文件夹 {akshare_data_path}")
            print("由于已优化为使用腾讯/新浪接口，可忽略此警告。")
    except Exception as e:
        print(f"无法定位 AkShare 路径: {e}")
        akshare_data_path = None
    
    # PyInstaller 参数
    params = [
        main_script,
        "--name=StockMonitor",
        "--onefile",        # 打包成一个 exe 文件
        "--noconsole",     # 运行时不显示控制台窗口
        "--clean",         # 清理临时文件
        f"--workpath={os.path.join(current_dir, 'build')}",
        f"--distpath={os.path.join(current_dir, 'dist')}",
        # 添加隐藏导入，防止某些模块丢失
        "--hidden-import=requests",
        "--hidden-import=pandas",
        "--hidden-import=akshare",
        # 如果有图标，可以加上 --icon=youricon.ico
    ]
    
    # 如果找到了 akshare 数据文件夹，添加到打包
    if akshare_data_path and os.path.exists(akshare_data_path):
        params.append(f"--add-data={akshare_data_path}{os.pathsep}akshare/file_fold")
        print(f"已添加 AkShare 数据文件: {akshare_data_path}")
    
    print("正在启动打包流程，请稍候...")
    PyInstaller.__main__.run(params)
    print("\n打包完成！EXE 文件位于 dist 目录下。")
    print("注意：程序已优化为优先使用腾讯/新浪接口，即使 AkShare 数据文件缺失也能正常运行。")

if __name__ == "__main__":
    build()
