from pwdata import META_OMol, Molecule, read_oMol_data
from tqdm import tqdm 
import json
import numpy as np

if __name__ == "__main__":
    file_list = [
        "/a800/wuxingxing/omol25-test.aselmdb"
    ]
    atom_names = None# ["C", "H"]
    query = None
    cpu_nums = 3

    omol_data = read_oMol_data(file_list, atom_names, query, cpu_nums)
    print(len(omol_data.image_list))
    save_path = "/a800/wuxingxing/omol25-test.json"
    out_put = {}
    for idx, image in tqdm(enumerate(omol_data.image_list), total=len(omol_data.image_list), desc="Convert to json file:"):
        tmp = {}
        for var_name, var_value in vars(image).items():
            if var_name != "data":
                tmp[var_name] = var_value
            for key in image.data.keys():
                tmp[key] = image.data[key]
            for key in tmp.keys():
                if isinstance(tmp[key], np.ndarray):
                    tmp[key] = tmp[key].flatten().tolist()
        out_put[idx] = tmp
    json.dump(out_put, open(save_path, "w"), indent=4)
