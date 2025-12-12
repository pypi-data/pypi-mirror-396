import os

root_dir = os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0]

if __name__ == '__main__':
    print(root_dir)
