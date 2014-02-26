#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Mejorando.la - www.mejorando.la
# Yohan Graterol - <y@mejorando.la>

'''boupy

Usage:
  boupy up <folder> [--encrypt=<encrypt>]
  boupy down <url> <output_folder> [--isencrypt=<isencrypt>]
  boupy -h | --help
  boupy --version

Options:
  -h --help                Show this screen.
  --version                Show version.
  --compress=<compress>    Compress the folder.
  --encrypt=<encrypt>      Encrypt the output compressed file Possible values = Y or N.
  --isencrypt=<encrypt>    Is encrypted the target file?.
'''

from __future__ import unicode_literals, print_function
import os
import json
import tarfile
import datetime
import requests
from docopt import docopt
from functools import wraps
from zoort.zoort import encrypt_file, decrypt_file, factory_uploader

__version__ = "0.1.0"
__author__ = "Yohan Graterol"
__license__ = "MIT"

YES = ['y', 'Y']
PASSWORD_FILE = None
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None
AWS_BUCKET_NAME = None
AWS_VAULT_NAME = None
AWS_KEY_NAME = None


def load_config(func):
    '''
    @Decorator
    Load config from JSON file.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = None
        try:
            config = open('/etc/boupy/config.json')
        except IOError:
            try:
                config = open(
                    os.path.join(
                        os.path.expanduser('~'),
                        '.boupy/config.json'))
            except IOError:
                raise SystemExit('Error #00: Can\'t load config.')
        config_data = json.load(config)

        global AWS_ACCESS_KEY
        global AWS_SECRET_KEY
        global AWS_BUCKET_NAME
        global AWS_VAULT_NAME
        global AWS_KEY_NAME
        global PASSWORD_FILE
        PASSWORD_FILE = config_data.get('password_file')
        AWS_ACCESS_KEY = config_data.get('aws').get('aws_access_key')
        AWS_SECRET_KEY = config_data.get('aws').get('aws_secret_key')
        AWS_BUCKET_NAME = config_data.get('aws').get('aws_bucket_name')
        AWS_VAULT_NAME = config_data.get('aws').get('aws_vault_name')
        AWS_KEY_NAME = config_data.get('aws').get('aws_key_name')
        return func(*args, **kwargs)
    return wrapper


def normalize_path(path):
    '''
    Add slash to path end
    '''
    if path[-1] != '/':
        return path + '/'
    return path


def extract_name_folder(folder):
    folder_split = folder.split('/')
    return folder_split[-2]


@load_config
def main():
    '''Main entry point for the boupy CLI.'''
    args = docopt(__doc__, version=__version__)
    print(args)
    if args.get("up"):
        pass


def boupy_up(args):
    folder = args.get('<folder>')
    encrypt = args.get('--encrypt') or 'N'

    if not folder:
        raise SystemExit('Error #01: Folder is not defined.')

    folder = normalize_path(folder)
    name_out_file = '-'.join((extract_name_folder(folder),
                              datetime.datetime.now().strftime(
                                  '%Y-%m-%d-%H-%M-%S')))
    folder_out_file = '/tmp/' + name_out_file
    tar = tarfile.open(folder_out_file + '.tar.gz', 'w:gz')
    tar.add(folder, arcname=name_out_file)
    tar.close()
    if encrypt in YES:
        encrypt_file(folder_out_file + '.tar.gz',
                     folder_out_file, PASSWORD_FILE)
        factory_uploader(name_backup=folder_out_file,
                         vault_name=AWS_VAULT_NAME,
                         path=os.path.join(os.path.expanduser('~'),
                                           '.boupy.db'))
    else:
        factory_uploader(name_backup=folder_out_file + '.tar.gz',
                         vault_name=AWS_VAULT_NAME,
                         path=os.path.join(os.path.expanduser('~'),
                                           '.boupy.db'))
    try:
        os.remove(folder_out_file + '.tar.gz')
        os.remove(folder_out_file)
    except OSError:
        pass


def boupy_down(args):
    url = args.get('<url>')
    output_folder = args.get('<output_folder>')
    isencrypt = args.get('--isencrypt')

    if not url:
        raise SystemExit('Error #02: URL is not defined.')
    if not output_folder:
        raise SystemExit('Error #03: Output folder is not defined.')

    output = 'restore.tar.gz' if not isencrypt in YES else 'restore'
    output = '/tmp/' + output

    data = requests.get(url)
    with open(output, 'wb') as restore:
        restore.write(data.content)

    if isencrypt in YES:
        decrypt_file(output, output + '.tar.gz')


if __name__ == '__main__':
    main()
