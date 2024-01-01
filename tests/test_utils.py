#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import os
import sys
import typing
import unittest.mock
from utils import parse_arguments, update_arguments_common, str2bool, get_base_type, contains_list_type, \
    is_argument_defined, generate_message_id, create_temporary_empty_file, get_valid_filename


class TestUtils(unittest.TestCase):

    def test_parse_arguments(self):
        # Test with default args
        with unittest.mock.patch.object(sys, 'argv', ['test_utils.py']):
            args = parse_arguments()
            self.assertFalse(args.debug)
            self.assertEqual(args.level, 'ERROR')

        # Test with custom args
        test_args = ['test_utils.py', '--debug', '--level', 'DEBUG']
        with unittest.mock.patch.object(sys, 'argv', test_args):
            args = parse_arguments()
            self.assertTrue(args.debug)
            self.assertEqual(args.level, 'DEBUG')

    def test_update_arguments_common(self):
        with unittest.mock.patch.object(sys, 'argv', ['test_utils.py', '--model', 'mixtral']):
            args = parse_arguments()
            self.assertEqual(args.model, 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf')
            args.model = 'mistral'
            update_arguments_common(args)
            self.assertEqual(args.model, 'mistral-7b-instruct-v0.1.Q4_K_M.gguf')

    def test_str2bool(self):
        self.assertTrue(str2bool('True'))
        self.assertFalse(str2bool('False'))
        self.assertRaises(argparse.ArgumentTypeError, str2bool, 'invalid')

    def test_get_base_type(self):
        self.assertEqual(get_base_type(int), int)
        self.assertEqual(get_base_type(str), str)
        self.assertEqual(get_base_type(list), list)
        self.assertEqual(get_base_type(typing.List[int]), int)

    def test_contains_list_type(self):
        self.assertTrue(contains_list_type(typing.List))
        self.assertFalse(contains_list_type(str))
        self.assertFalse(contains_list_type(int))

    def test_is_argument_defined(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--test')
        self.assertTrue(is_argument_defined(parser, 'test'))
        self.assertFalse(is_argument_defined(parser, 'foo'))
        parser = argparse.ArgumentParser()
        self.assertFalse(is_argument_defined(parser, 'test'))
        parser = argparse.ArgumentParser()
        parser.add_argument('--long-arg')
        self.assertTrue(is_argument_defined(parser, 'long-arg'))

    def test_generate_message_id(self):
        message_id = generate_message_id()
        self.assertIsInstance(message_id, str)
        self.assertTrue('cmpl-' in message_id)

    def test_create_temporary_empty_file(self):
        temp_file_path = create_temporary_empty_file()
        self.assertIsInstance(temp_file_path, str)
        self.assertTrue(os.path.exists(temp_file_path))
        os.remove(temp_file_path)
        self.assertFalse(os.path.exists(temp_file_path))

    def test_get_valid_filename(self):
        url = 'https://example.com/path/to/file.txt'
        filename = get_valid_filename(url)
        self.assertEqual(filename, 'file.txt')

        url = 'https://example.com/odd_chars/?%^*'
        filename = get_valid_filename(url)
        self.assertRegex(filename, r'example.com.download')
