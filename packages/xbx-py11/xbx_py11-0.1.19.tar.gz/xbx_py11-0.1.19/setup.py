from setuptools import setup


package_data = {
    'xtquant': ['xtquant/*', 'xtquant/xtbson/*', 'xtquant/xtbson/bson36/*', 'xtquant/xtbson/bson37/*', 'xtquant/qmttools/*'],# ['xtquant/*']代表移动文件的路径，如果有其他类似情况按这个格式往下加就行
    'xbxdata': ['xbxdata/*'],
}

setup(
    name='xbx-py11',
    version='0.1.19',# 版本号
    description='xbx-py11',
    author='xbx-py11',
    packages=['xtquant', 'xbxdata'], # package_data的key
    package_data=package_data, # 不用改了
    include_package_data=True,
   
    
    install_requires=[  # 用到的库，有需要的往下加
        'ccxt==4.5.22',
        'dataframe_image==0.2.4',
        'DrissionPage==4.1.0.14',
        'lxml==5.3.0',
        'ntplib==0.4.0',
        'httpx==0.27.2',
        'bs4==0.0.2',
        'scipy==1.14.1',
        'tabulate==0.9.0',
        'dash==2.18.1',
        'dash-iconify==0.1.2',
        'dash-mantine-components==0.14.5',
        'scikit-learn==1.5.2',
        'py-mini-racer==0.6.0',
        'psutil ==6.0.0',
        'py7zr==0.22.0',
        'rarfile==4.2',
        'matplotlib==3.9.2',
        'joblib==1.4.2',
        'numpy==2.0.2',
        'pandas==2.2.3',
        'requests==2.32.3',
        'PyExecJS==1.5.1',
        'tqdm==4.66.5',
        'plotly==5.24.1',
        'pyarrow==17.0.0',
        'retrying==1.3.4',
        'colorama==0.4.6',
        'seaborn==0.13.2',
        'numba==0.60.0',
        'openpyxl==3.1.5',
        'unlock_joblib_tasks==1.3',
        'zstandard==0.23.0',
        'unlock-processpool-win==2.1.0',
        'schedule==1.2.2',
        'xlrd==2.0.1',
        'fastapi==0.115.12',
        'uvicorn==0.34.2',
        'python-jose==3.5.0',
        'python-multipart==0.0.20',
        'pyotp==2.9.0',
        'sqlalchemy==2.0.41',
        'pycryptodome==3.21.0',
    ],
)
