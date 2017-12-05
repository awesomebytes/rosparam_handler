#!/usr/bin/env python

# Copyright (c) 2017, Sammy Pfeiffer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Sammy Pfeiffer
#
# Utilities to import from another package .params file
#

from imp import load_source
from rospkg import RosPack, ResourceNotFound
from tempfile import NamedTemporaryFile
import cStringIO
import tokenize
import re


def remove_comments(source):
    """
    Returns 'source' minus comments, based on
    https://stackoverflow.com/a/2962727
    :param source: string with Python source code
    :return: source code without comments
    """
    io_obj = cStringIO.StringIO(source)
    out = ""
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        else:
            out += token_string
        last_col = end_col
        last_lineno = end_line
    return out


def load_generator(package_name, params_file_name, relative_path='/cfg/'):
    """
    Returns the generator created in another .params file from another package.
    Python does not allow to import from files without the extension .py
    so we need to hack a bit to be able to import from .params file.
    Also the .params file was never thought to be imported, so we need
    to do some extra tricks.
    :param package_name: ROS package name
    :param params_file_name: .params file name
    :param relative_path: path in between package_name and params_file_name, defaults to /cfg/
    :return:
    """
    # Get the file path
    rp = RosPack()
    try:
        pkg_path = rp.get_path(package_name)
    except ResourceNotFound:
        return None
    full_file_path = pkg_path + '/cfg/' + params_file_name
    # print("Loading rosparam_handler params from file: " + full_file_path)

    # Read the file and check for exit() calls
    # Look for line with exit function to not use it or we will get an error
    with open(full_file_path, 'r') as f:
        file_str = f.read()
    # Remove all comment lines first
    clean_file = remove_comments(file_str)
    # Find exit( calls
    exit_finds = [m.start() for m in re.finditer('exit\(', clean_file)]
    # If there are, get the last one
    if exit_finds:
        last_exit_idx = exit_finds[-1]
        clean_file = clean_file[:last_exit_idx]
        with NamedTemporaryFile() as f:
            f.file.write(clean_file)
            f.file.close()
            tmp_module = load_source('tmp_module', f.name)
    else:
        # Looks like the exit call is not there
        # or it's surrounded by if __name__ == '__main__'
        # so we can just load the source
        tmp_module = load_source('tmp_module', full_file_path)

    for var in dir(tmp_module):
        if not var.startswith('_'):
            module_element = getattr(tmp_module, var)
            type_str = str(type(module_element))
            # Looks like:
            # <class 'PACKAGE_NAME.parameter_generator_catkin.ParameterGenerator'>
            if 'parameter_generator_catkin.ParameterGenerator' in type_str:
                return module_element

    return None
