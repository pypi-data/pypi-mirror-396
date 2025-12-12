import os, sys
from pwdata import Config

import argparse

def run_convert_configs(cmd_list:list[str]):
    # parser = argparse.ArgumentParser(description='This command is used for transferring structural files between different apps. For extxyz format, all configs will save to one file, \nFor pwmlff/npy, configs with same atom types and atom nums in each type will save to one dir.\n')

    # parser.add_argument('-i', '--input',         type=str, required=True,  help="The directory or file path of the datas.\nYou can also use JSON file to list all file paths in 'datapath': [], such as 'pwdata/test/meta_data.json'")
    # parser.add_argument('-s', '--savepath',      type=str, required=False, default="MOVEMENT", help="The output dir path, if not provided, the current dir will be used")
    # args = parser.parse_args(cmd_list)
    args_input = "/share/public/wuxingxing/SandboxAQ/train_id_v2/data.0021.aselmdb"
    args_savepath = "~/tmp/"
    image = Config(data_path=args_input, format="meta")
    image.to(format="extxyz", data_path=args_savepath)
    print("covert extxyz done!")

if __name__=="__main__":
    print(sys.argv)
    run_convert_configs([])# cmd_list = sys.argv[1:]