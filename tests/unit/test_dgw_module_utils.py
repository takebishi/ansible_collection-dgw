from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import unittest
from unittest.mock import patch

from ansible_collections.takebishi.dgw.tests.unit.unit_test_util import UnitTestUtil, basic
from ansible_collections.takebishi.dgw.plugins.module_utils.dgw_util import find_object, DgwUtilError


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
    # find object case normal
    def test_find_object_normal(self):
        test_path = "./tests/unit/export_test_files/unit_check.dxg"
        file = open(test_path, 'r', encoding="utf-8")
        inobj = json.load(file)

        param_path = "DataSource.Device.AB1.setting.name.value"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "AB1")

        param_path = "DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "bbb_tag")

        param_path = "Event.Item.event1.action.action1.setting.sleeptime.value"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "800")

        param_path = "Event.Item.event1.action.action2.setting.httpMethod.value"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "GET")

        param_path = "CommInterface.Mqtt.mqtt1.setting.clientId.value"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "my_client3")

        param_path = "DataSource.Device.AB1.group.folder1.group.bbb_tag.name"
        keys = param_path.split('.')
        outobj = find_object(keys, inobj)
        self.assertEqual(outobj, "bbb_tag")

    # find object case abnormal
    def test_find_object_abnormal1(self):
        test_path = "./tests/unit/export_test_files/unit_check.dxg"
        file = open(test_path, 'r', encoding="utf-8")
        inobj = json.load(file)

        # 空
        param_path = ""
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # ccc_tagがない
        param_path = "DataSource.Device.AB1.group.folder1.group.ccc_tag.name"
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # name1がない
        param_path = "DataSource.Device.AB1.group.folder1.group.bbb_tag.name1"
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # setting1がない
        param_path = "Event.Item.event1.action.action2.setting1.httpMethod.value"
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # action3がない
        param_path = "Event.Item.event1.action.action3.setting.httpMethod.value"
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # value1がない
        param_path = "DataSource.Device.AB1.group.folder1.group.bbb_tag1.setting.name.value1"
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

    def test_find_object_abnormal2(self):
        param_path = "DataSource.Device.json1.setting.name.value"
        # inobj = json.loads('{ "DataSource": { "Device": [ { "name": "json1", "setting": [ { "name": "name", "value": "json1" }, '\
        #                   '{ "name": "adapterIPAddress", "value": "localhost" }, { "name": "adapterPortNo", "value": "52230" },  '\
        #                   '{ "name": "simulationType", "value": "0" }, { "name": "readCycle", "value": "100" }, { "name": "timeoutMsec", "value": "0" } ], '\
        #                   ' "type": "JsonUdp" } ] } }')

        # Jsonが空
        inobj = json.loads('{}')
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # Jsonに "name": <設定名>のキー＆値がない
        # setting内のname設定もない
        inobj = json.loads('{ "DataSource": { "Device": [ { "setting": [ { "name": "adapterIPAddress", "value": "localhost" }, '
                           '{ "name": "adapterPortNo", "value": "52230" }, { "name": "simulationType", "value": "0" },  '
                           '{ "name": "readCycle", "value": "100" }, { "name": "timeoutMsec", "value": "0" } ],  '
                           '"type": "JsonUdp" } ] } }')
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # Jsonに "name": <設定名>のキー＆値がない
        # setting内のname設定のvalueもない
        inobj = json.loads('{ "DataSource": { "Device": [ { "setting": [ { "name": "name" }, { "name": "adapterIPAddress", "value": "localhost" }, '
                           '{ "name": "adapterPortNo", "value": "52230" }, { "name": "simulationType", "value": "0" },  '
                           '{ "name": "readCycle", "value": "100" }, { "name": "timeoutMsec", "value": "0" } ], "type": "JsonUdp" } ] } }')
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)

        # Jsonに "name": <設定名>のキー＆値がない
        # setting内のname設定のnameもない
        inobj = json.loads('{ "DataSource": { "Device": [ { "setting": [ { "value": "json1" }, { "name": "adapterIPAddress", "value": "localhost" }, '
                           '{ "name": "adapterPortNo", "value": "52230" }, { "name": "simulationType", "value": "0" }, '
                           '{ "name": "readCycle", "value": "100" }, { "name": "timeoutMsec", "value": "0" } ], "type": "JsonUdp" } ] } }')
        keys = param_path.split('.')
        with self.assertRaises(DgwUtilError):
            find_object(keys, inobj)
