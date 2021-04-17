"""
Dedupes images

root/
├──2019-04-16
│  ├──IMG_1003.jpg
│  ├──IMG_1004.jpg
├──2019-05-03
│  ├──IMG_1004.jpg
│  ├──IMG_1005.jpg

In the directory structure above the file IMG_1004.jpg appears to be a duplicate.
This script will
    - compare both files bit by bit to determine if they are the same 
    - provide a resolution strategy to remove the deplicate e.g. keeping the oldest copy
"""
import filecmp
import os

import click


@click.command()
@click.argument('path')
def dedupe(path: str):
    print(f'Deduping path {path}')
    file_list = {}
    # TODO check if path exists
    for dirpath, dirs, files in os.walk(path):     
        # TODO check file extensions
        
        if dirpath == path:
            continue  # skip base directory

        for ff in files:
            full_path = os.path.join(dirpath, ff)
            if ff in file_list:
                first_path = file_list[ff]['paths'][0]
                matched = filecmp.cmp(full_path, first_path, shallow=False)
                if matched:
                    num_matches = len(file_list[ff]['paths'])
                    print(f'{full_path} has matched with {first_path} and has {num_matches} matches')
                else:
                    print(f'{full_path} and {first_path} have the same filename but do not match')
            else:
                file_list[ff] = {'paths': [full_path]}

if __name__ == '__main__':
    dedupe()
