from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import shutil
import stat
import json
import unittest
from unittest.mock import patch
from datetime import datetime

from ansible_collections.takebishi.dgw.tests.unit.unit_test_util import UnitTestUtil, AnsibleExitJson, AnsibleFailJson, basic
from ansible_collections.takebishi.dgw.plugins.modules.dgw_change_param import main


class TestDgwModule(unittest.TestCase):
    # unittest用の初期設定
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=UnitTestUtil.exit_json,
                                                 fail_json=UnitTestUtil.fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    # -----------------------
    # テストケース   test_...で始まるメソッドを追加する
    # -----------------------
    # dgw_change_param normal
    def test_dgw_change_param_normal(self):
        src_path = './tests/unit/export_test_files/unit_check.dxg'
        dest_dir = '/tmp/unittest' + datetime.now().strftime("%Y%m%d%H%M%S%f")
        dest_path = dest_dir + '/change_test.dxg'

        os.makedirs(dest_dir)

        # 正常
        param_path = 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value'
        param = 'aabbcc'
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleExitJson):
            main()
        self.assertTrue(os.path.exists(dest_path))

        # JSON解析
        file = open(dest_path, 'r', encoding="utf-8")
        obj = json.load(file)
        file.close()
        self.assertEqual(obj['DataSource']['Device'][0]['group'][0]['group'][0]['setting'][0]['value'], param)
        os.remove(dest_path)

        # 正常
        param_path = 'Event.Item.event1.action.action1.setting.sleeptime.value'
        param = '1234'
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleExitJson):
            main()
        self.assertTrue(os.path.exists(dest_path))

        # JSON解析
        file = open(dest_path, 'r', encoding="utf-8")
        obj = json.load(file)
        file.close()
        self.assertEqual(obj['Event']['Item'][0]['action'][0]['setting'][1]['value'], param)
		
        shutil.rmtree(dest_dir)

    # dgw_change_param abnormal
    def test_dgw_change_param_abnormal(self):
        src_dir = './tests/unit/export_test_files'
        src_path = src_dir + '/unit_check.dxg'
        dest_dir = '/tmp/unittest' + datetime.now().strftime("%Y%m%d%H%M%S%f")
        dest_path = dest_dir + '/change_test.dxg'
        param_path = 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value'
        param = 'aabbcc'

        dest_dir = '/tmp/unittest' + datetime.now().strftime("%Y%m%d%H%M%S%f")
        dest_path = dest_dir + '/change_test.dxg'

        os.makedirs(dest_dir)
		
        # ファイルパスが空
        UnitTestUtil.set_module_args({'src': '', 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("not found", result.exception.args[0]['errmsg'])

        # ファイルパスがNone
        UnitTestUtil.set_module_args({'src': None, 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        # 引数の型違いエラーとなる
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # 出力ファイルパスが空
        UnitTestUtil.set_module_args({'src': src_path, 'dest': '', 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("No such file or directory", result.exception.args[0]['errmsg'])

        # 出力ファイルパスがNone
        UnitTestUtil.set_module_args({'src': src_path, 'dest': None, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        # 引数の型違いエラーとなる
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # パラメータパスが空
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': '', 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("Cannot find parameter key", result.exception.args[0]['errmsg'])

        # パラメータパスがNone
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': None, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        # 引数の型違いエラーとなる
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # パラメータがnone
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': param_path, 'param': None})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        # 引数の型違いエラーとなる
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # ファイルが存在しない
        UnitTestUtil.set_module_args({'src': src_dir + '/export_12345_.dxg', 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("not found", result.exception.args[0]['errmsg'])

        # Jsonフォーマット異常(Jsonでないファイル)
        UnitTestUtil.set_module_args({'src': src_dir + '/NotJson.dxg', 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("JSONDecodeError", result.exception.args[0]['errmsg'])

        # 最後のキーがない
        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path,
                                      'param_path': 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.vvvv', 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertFalse(os.path.exists(dest_path))
        self.assertIn("Cannot find parameter key", result.exception.args[0]['errmsg'])

        # ファイルが書込めない
        write_file = open(dest_path, 'w', encoding="utf-8")
        write_file.close()
        if os.getuid() == 0:
            os.system(f'chattr +a {dest_path}')
        else:
            os.chmod(dest_path, stat.S_IREAD)

        UnitTestUtil.set_module_args({'src': src_path, 'dest': dest_path, 'param_path': param_path, 'param': param})
        with self.assertRaises(AnsibleFailJson) as result:
            main()

        if os.getuid() == 0:
            os.system(f'chattr -a {dest_path}')
            self.assertIn("Operation not permitted", result.exception.args[0]['errmsg'])
        else:
            os.chmod(dest_path, stat.S_IREAD | stat.S_IWUSR)
            self.assertIn("Permission denied", result.exception.args[0]['errmsg'])

        shutil.rmtree(dest_dir)
