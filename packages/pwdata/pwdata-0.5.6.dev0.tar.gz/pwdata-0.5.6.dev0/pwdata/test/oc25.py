from pwdata import Config
from tqdm import tqdm 
import json
import numpy as np

if __name__ == "__main__":

    """ 转换脚本
    os.chdir("/a800/wuxingxing/OC25/train")
    file_name = [
                "data0000.aselmdb",
                "data0001.aselmdb",
                "data0002.aselmdb",
                "data0003.aselmdb",
                "data0004.aselmdb",
                "data0005.aselmdb",
                "data0006.aselmdb",
                "data0007.aselmdb",
                "data0008.aselmdb",
                "data0009.aselmdb",
                "data0010.aselmdb",
                "data0011.aselmdb",
                "data0012.aselmdb",
                "data0013.aselmdb",
                "data0014.aselmdb",
                "data0015.aselmdb",
                "data0016.aselmdb",
                "data0017.aselmdb",
                "data0018.aselmdb",
                "data0019.aselmdb"
                ]
    for file in file_name:
        oc_data = Config(format="meta", data_path=file)
        oc_data.to(format='extxyz', data_path=f"{file.split('.')[0]}-extxyz")
        # check file
        try:
            check_data= Config(format="extxyz", data_path=f"{file.split('.')[0]}-extxyz/train.xyz")
        except Exception as e:
            print(e)
            print(f"{file} cvt error!")

        print(f"{file} cvt done!")
    """
    # file_list = [
    #     "/a800/wuxingxing/OC25/train/data0008.aselmdb"
    # ]
    # atom_names = None# ["C", "H"]
    # query = None
    # cpu_nums = 1

    # oc_data = Config(format="meta", data_path=file_list, atom_names=atom_names, query=query, cpu_nums=cpu_nums)
    # oc_data.to(format="extxyz", data_path="/a800/wuxingxing/OC25/tmp")

    oc_data = Config(format="extxyz", data_path="/a800/wuxingxing/OC25/train/train.xyz")
    print(f"read done! image nums: {len(oc_data.images)}")