from __future__ import absolute_import, division, print_function
__metaclass__ = type

import unittest
from unittest.mock import patch

from ansible_collections.takebishi.dgw.tests.unit.unit_test_util import UnitTestUtil, basic
from ansible_collections.takebishi.dgw.plugins.modules.dgw_export_config_file import is_different_setting, DgwCompareError


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
    def test_dgw_export_config_file_is_different_setting(self):
        test_dir = "./tests/unit/export_test_files/"

        # 同じ設定
        file1 = test_dir + "normal2.dxg"
        file2 = test_dir + "normal2.dxg"
        ret = is_different_setting(file1, file2)
        self.assertFalse(ret)

        # 同じ設定(改行あり・なし)
        file1 = test_dir + "normal2.dxg"
        file2 = test_dir + "LineFeed2.dxg"
        ret = is_different_setting(file1, file2)
        self.assertFalse(ret)

        # 同じ設定(オブジェクトの並びが違う)
        file1 = test_dir + "LineFeed2.dxg"
        file2 = test_dir + "LineFeed2_obj.dxg"
        ret = is_different_setting(file1, file2)
        self.assertFalse(ret)

        # 同じ設定(リスト内の並びが違う)
        file1 = test_dir + "LineFeed2.dxg"
        file2 = test_dir + "LineFeed2_list.dxg"
        ret = is_different_setting(file1, file2)
        self.assertFalse(ret)

        # 異なる設定(valueが異なる)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "normal2.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(keyが異なる)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "DefferentKey1.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(keyが異なる)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "DefferentKey2.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(リストが多い)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "LineFeed1_listadd.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(リストが少ない)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "LineFeed1_listdel.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(オブジェクトが多い)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "LineFeed1_objadd.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

        # 異なる設定(オブジェクトが少ない)
        file1 = test_dir + "normal1.dxg"
        file2 = test_dir + "LineFeed1_objdel.dxg"
        ret = is_different_setting(file1, file2)
        self.assertTrue(ret)

    def test_dgw_export_config_file_is_different_setting_abnormal(self):
        test_dir = "./tests/unit/export_test_files/"

        # 存在しないファイル(file1)
        file1 = test_dir + "aaa.dxg"
        file2 = test_dir + "normal2.dxg"
        with self.assertRaises(DgwCompareError):
            is_different_setting(file1, file2)

        # 存在しないファイル(file2)
        file1 = test_dir + "normal2.dxg"
        file2 = test_dir + "bbb.dxg"
        with self.assertRaises(DgwCompareError):
            is_different_setting(file1, file2)

        # Jsonではないファイル(file1)
        file1 = test_dir + "NotJson.dxg"
        file2 = test_dir + "normal2.dxg"
        with self.assertRaises(DgwCompareError):
            is_different_setting(file1, file2)

        # Jsonではないファイル(file2)
        file1 = test_dir + "normal2.dxg"
        file2 = test_dir + "NotJson.dxg"
        with self.assertRaises(DgwCompareError):
            is_different_setting(file1, file2)
