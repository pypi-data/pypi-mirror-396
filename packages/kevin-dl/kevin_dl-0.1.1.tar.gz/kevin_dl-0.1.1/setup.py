from setuptools import setup, find_packages

setup(
    packages=find_packages(),

    # # 默认只添加 .py 文件，如果需要添加其他文件则需要令 include_package_data 为 True
    # include_package_data=True,
    # # 需要添加的额外文件列表，比如这里就表示将添加 images/raw 下的所有 .png 文件和 images/2k 下的所有 .jpg 文件
    # package_data={
    #     "images": ['raw/*.png', '2k/*.jpg'],
    # },
    # # 需要排除的文件
    # exclude_package_data={
    #     "images": ['raw/233.png'],
    # },
    # 或者参考 https://towardsdatascience.com/the-complete-guide-for-creating-a-good-pypi-package-acb5420a03f8
    # 使用 MANIFEST.in 指定需要额外添加的文件
)
