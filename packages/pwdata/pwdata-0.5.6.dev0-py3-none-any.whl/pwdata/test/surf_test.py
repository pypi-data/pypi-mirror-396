import numpy as np
from pwdata.image import Image
from pwdata.config import Config
from pwdata.build.supercells import make_supercell
from pwdata.pertub.perturbation import perturb_structure
from pwdata.pertub.scale import scale_cell

def test_super_cell(input_format, config_file, super_cell_matrix, pbc, save_path, save_name, save_format, direct = True, sort = False, wrap = False):
    config = Config(format=input_format, data_path=config_file, atom_names=None)
    # Make a supercell     
    supercell = make_supercell(config, super_cell_matrix, pbc)
    # Write out the structure
    supercell.to(data_path = save_path,
                data_name  = save_name,
                format     = save_format,
                direct = True, 
                sort   = False,
                wrap   = False)
    
def test_scale():
    pass

def test_pertub():
    pass


if __name__=="__main__":
    test_super_cell()