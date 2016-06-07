#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import csv
import os
import sys


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Digital preservation utilities.')
    subparsers = parser.add_subparsers(help='sub-command help')
    count_parser = subparsers.add_parser('count', 
        help='count files and sizes in bytes')
    checksum_parser = subparsers.add_parser('check', 
        help='create inventory of files and checksums')
    compare_parser = subparsers.add_parser('comp', 
        help='compare and verify inventories')


#    parser.add_argument('-c', '--config', required=True,
#        help='relative or absolute path to the YAML config file')

    args = parser.parse_args()


if __name__ == "__main__":
    main()
