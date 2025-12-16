import numpy as np,pandas as pd
from mille import *
'''
   pd_mille
   converte la colonna col del datframe df diviso mille
'''
def pd_mille(df,nome_col):  
    df.loc[:,nome_col] = df.apply(lambda row: mille(row[nome_col]), axis=1)
    return (df)


def main():
    print("function pd_mille")
    data = {'Name.': ['Tom', 'nick', 'krish', 'jack'],
            'Age': [20000, 21000, 19000, 180]}
    df = pd.DataFrame(data)
    df = pd_mille(df,'Age')
    print(df)
  
if __name__== "__main__":    
   main()
