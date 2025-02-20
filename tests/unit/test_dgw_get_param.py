from __future__ import absolute_import, division, print_function
__metaclass__ = type

import unittest
from unittest.mock import patch

from ansible_collections.takebishi.dgw.tests.unit.unit_test_util import UnitTestUtil, AnsibleExitJson, AnsibleFailJson, basic
from ansible_collections.takebishi.dgw.plugins.modules.dgw_get_param import main


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
    # dgw_get_param normal
    def test_dgw_get_param_normal(self):
        test_dir = "./tests/unit/export_test_files/"
        src_path = test_dir + 'unit_check.dxg'

        # 正常
        param_path = 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value'
        out = 'bbb_tag'
        UnitTestUtil.set_module_args({'src': src_path, 'param_path': param_path})
        with self.assertRaises(AnsibleExitJson) as result:
            main()
        self.assertEqual(result.exception.args[0]['param'], out)

        # 正常
        param_path = 'Event.Item.event1.action.action1.setting.sleeptime.value'
        out = '800'
        UnitTestUtil.set_module_args({'src': src_path, 'param_path': param_path})
        with self.assertRaises(AnsibleExitJson) as result:
            main()
        self.assertEqual(result.exception.args[0]['param'], out)

        UnitTestUtil.set_module_args({'src': src_path, 'param_path': 'DataSource.Device.AB1.name'})
        out = 'AB1'
        with self.assertRaises(AnsibleExitJson) as result:
            main()
        self.assertEqual(result.exception.args[0]['param'], out)

    # dgw_change_param abnormal
    def test_dgw_get_param_abnormal(self):
        test_dir = "./tests/unit/export_test_files/"
        src_path = test_dir + 'unit_check.dxg'
        param_path = 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value'

        # ファイルパスが空
        UnitTestUtil.set_module_args({'src': '', 'param_path': param_path})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("not found", result.exception.args[0]['errmsg'])

        # ファイルパスがnone
        UnitTestUtil.set_module_args({'src': None, 'param_path': param_path})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # パラメータパスが空
        UnitTestUtil.set_module_args({'src': src_path, 'param_path': ''})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("DgwUtilError", result.exception.args[0]['errmsg'])

        # パラメータパスがnone
        UnitTestUtil.set_module_args({'src': src_path, 'param_path': None})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("'None' is not a string and conversion is not allowed", result.exception.args[0]['msg'])

        # ファイルが存在しない
        UnitTestUtil.set_module_args({'src': test_dir + 'export_12345_.dxg', 'param_path': param_path})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("not found", result.exception.args[0]['errmsg'])

        # Jsonフォーマット異常(Jsonでないファイル)
        UnitTestUtil.set_module_args({'src': test_dir + 'NotJson.dxg', 'param_path': param_path})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("JSONDecodeError", result.exception.args[0]['errmsg'])

        # 最後のキーがない
        UnitTestUtil.set_module_args({'src': src_path, 'param_path': 'DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.vvvv'})
        with self.assertRaises(AnsibleFailJson) as result:
            main()
        self.assertIn("DgwUtilError", result.exception.args[0]['errmsg'])
