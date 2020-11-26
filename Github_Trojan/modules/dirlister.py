# importing packages
import os

def run(**args):
    'function returing a string of list of files in directory.'
    print('In Directory lister')
    files = os.listdir('.')

    return str(files)