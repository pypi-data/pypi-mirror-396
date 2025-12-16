#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 17:43:26 2023

@author: nikos, vf
"""

import sys
from .__master__ import main as atlas_master
from .helper_functions.parse_caller_args import call_parser
from .helper_functions.caller_utils import prepare_master_args, export_report
from .helper_functions.__parse_init_file__ import parse_call_atlas_ini
from .helper_functions.save_ini_files import copy_ini_files

def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]
        
    # Get the input .ini file path of the ATLAS caller
    cmd_args = call_parser()
    
    # Parse the fields from the initialization file
    parser_args = parse_call_atlas_ini(filepath = cmd_args['ini_file'])

    # Prepare the ATLAS arguments
    mst_args = prepare_master_args(parser_args)

    # Call ATLAS
    atlas_master(mst_args)

    # Export to an html draft QA report file
    export_report(parser_args)
    
    #Save ini files along with input data in the parent folder
    copy_ini_files(parser_args, cmd_args['ini_file'])

if __name__ == "__main__":
    
    main()