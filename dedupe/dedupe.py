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
import re

import click


def resolve(*paths):
    """Decide which path to delete
    Returns path to keep
    """

    def date_from_path(path):
        date_re = re.compile(r'\d{4}-\d{2}-\d{2}')
        parts = path.split('/')
        date = None
        for part in parts:
            match = date_re.match(part)
            if match:
                if date:
                    raise ValueError('Multiple dates in path')
                date = part
        if not date:
            raise ValueError(f'Could not find date in {path}')
        return date
    
    sorted_paths = sorted(paths, key=date_from_path)
    return sorted_paths[0], sorted_paths[1:]


@click.command()
@click.argument('path')
def dedupe(path: str):
    print(f'Deduping path {path}')
    file_list = {}
    total_size = 0
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
                    file_list[ff]['paths'].append(full_path)
                    total_size += os.path.getsize(full_path)
                else:
                    print(f'{full_path} and {first_path} have the same filename but do not match')
            else:
                file_list[ff] = {'paths': [full_path]}

    for file_path in file_list:
        if len(file_list[file_path]['paths']) > 1:
            try:
                keep, delete = resolve(*file_list[file_path]['paths'])
                print('Resolving ' + ', '.join(file_list[file_path]['paths']) + ' decided to keep ' + keep)

                for path in delete:
                    print(f'Deleting {path}')
                    #os.remove(path)
            except ValueError as err:
                print(err)

    size_in_mbs = int(total_size / 1024 / 1024)
    print('Total size of dupes ' + str(size_in_mbs))

if __name__ == '__main__':
    dedupe()
