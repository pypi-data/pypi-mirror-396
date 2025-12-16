###############################################################################################################
# Required Python modules and libraries
import os.path
import sys

# Comment the following line to execute the code from the installed library. Otherwise, Python executes the local files.
sys.path.insert(1, os.path.dirname(sys.path[0]))

from icdr_class import icdr

from sys import platform

import pandas as pd

if __name__ == '__main__':
    base_path = ''
    if platform == "linux" or platform == "linux2":
        base_path = '/media/leo/7CE54B377BB9B18B/datasets/EntityResolution/ProductMatching/pricerunner/'
        output_path = '/home/leo/Desktop/dev/Python/FastDynamicRecordLinkage/runs/'
    elif platform == "win32":
        base_path = 'D:/datasets/EntityResolution/ProductMatching/pricerunner/'
        output_path = 'D:/dev/Python/FastDynamicRecordLinkage/runs/'
    else:
        exit(1)

    entities_file = base_path + 'coffee_makers_2.csv'
    input_dataframe = pd.read_csv(entities_file)
    input_dataframe.head(10)

    index = icdr()
    index.build(input_file=entities_file)

    records = index.retrieve(q="bosch coffee maker", num_results=20)
    print("Results:\n", records)


    #index.display_index()
    #index.write(output_path)

    index.destroy()

    #index2 = icdr()
    #index2.read(output_path)
    #index2.display_index()
    #index2.display_entities()
    #index2.destroy()
