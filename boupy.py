#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Mejorando.la - www.mejorando.la
# Yohan Graterol - <y@mejorando.la>

'''boupy

Usage:
  boupy up <folder> [--encrypt=<encrypt>] [--upload_s3=<upload_s3>]
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
import zoort
from zoort import encrypt_file, decrypt_file, factory_uploader

__version__ = "0.1.2"
__author__ = "Yohan Graterol"
__license__ = "MIT"

YES = ['y', 'Y']
zoort.PASSWORD_FILE = None
zoort.AWS_ACCESS_KEY = None
zoort.AWS_SECRET_KEY = None
zoort.AWS_BUCKET_NAME = None
zoort.AWS_VAULT_NAME = None
zoort.AWS_KEY_NAME = None
zoort.DELETE_WEEKS = None

_error_codes = {
    100: u'Error #00: Can\'t load config.',
    101: u'Error #01: Folder is not defined.',
    102: u'Error #02: URL is not defined.',
    103: u'Error #03: Output folder is not defined.'
}


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
                raise SystemExit(_error_codes.get(100))
        config_data = json.load(config)

        zoort.PASSWORD_FILE = config_data.get('password_file')
        zoort.DELETE_WEEKS = config_data.get('delete_weeks')
        zoort.AWS_ACCESS_KEY = config_data.get('aws').get('aws_access_key')
        zoort.AWS_SECRET_KEY = config_data.get('aws').get('aws_secret_key')
        zoort.AWS_BUCKET_NAME = config_data.get('aws').get('aws_bucket_name')
        zoort.AWS_VAULT_NAME = config_data.get('aws').get('aws_vault_name')
        zoort.AWS_KEY_NAME = config_data.get('aws').get('aws_key_name')
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
    if args.get("up"):
        boupy_up(args)
    if args.get("down"):
        boupy_down(args)


def boupy_up(args):
    folder = args.get('<folder>')
    encrypt = args.get('--encrypt') or 'N'
    s3 = args.get('--upload_s3') or 'N'
    uploader = 'S3' if s3 in YES else 'Glacier'

    if not folder:
        raise SystemExit(101)

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
                     folder_out_file, zoort.PASSWORD_FILE)

        factory_uploader(uploader,
                         action='upload',
                         name_backup=folder_out_file,
                         bucket_name=zoort.AWS_BUCKET_NAME,
                         path=os.path.join(os.path.expanduser('~'),
                                           '.boupy.db'))
    else:
        factory_uploader(uploader,
                         action='upload',
                         name_backup=folder_out_file + '.tar.gz',
                         bucket_name=zoort.AWS_BUCKET_NAME,
                         path=os.path.join(os.path.expanduser('~'),
                                           '.boupy.db'))
    if os.path.isfile(folder_out_file + '.tar.gz'):
        os.remove(folder_out_file + '.tar.gz')
    if os.path.isfile(folder_out_file):
        os.remove(folder_out_file)


def boupy_down(args):
    url = args.get('<url>')
    output_folder = args.get('<output_folder>')
    isencrypt = args.get('--isencrypt')

    if not url:
        raise SystemExit(102)
    if not output_folder:
        raise SystemExit(103)

    file_name = url.split('/')[-1]

    output = file_name + 'tar.gz' if not isencrypt in YES else file_name
    output = '/tmp/' + output

    data = requests.get(url)
    with open(output, 'wb') as restore:
        restore.write(data.content)

    if isencrypt in YES:
        decrypt_file(output, output + '.tar.gz')


if __name__ == '__main__':
    main()
