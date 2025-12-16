import numpy as np
import pandas as pd
import argparse
from .post import files_to_dfs
import sys

def quantile_normalize_edges(infile: str, filetype: str, outfile: str):    
    '''
    Quantile normalizes the edges of the lioness network and saves the output in a pickle file
     
    Parameters:
    -----------
        - infile: str, lioness data frame in pickle or csv format
        - filetype: str, the format of the infile
        - outfile: str, Path to output file 
        
    Returns:
    -----------
        - Nothing
    '''

    if filetype == "pickle":
        lion = pd.read_pickle(infile, index_col = 0)   
    elif filetype == "csv":
        lion = pd.read_csv(infile, index_col = 0)

    print(lion.head())  