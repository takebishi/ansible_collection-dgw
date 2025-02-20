import json
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils import basic


# ansibleモジュールから戻りステータスを取得するためのクラスと関数
class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


class UnitTestUtil:
    # ansibleモジュールに引数を渡すための関数
    @staticmethod
    def set_module_args(args):
        """prepare arguments so that they will be picked up during module creation"""
        args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
        basic._ANSIBLE_ARGS = to_bytes(args)

    @staticmethod
    def exit_json(*args, **kwargs):
        """function to patch over exit_json; package return data into an exception"""
        if 'changed' not in kwargs:
            kwargs['changed'] = False
        raise AnsibleExitJson(kwargs)

    @staticmethod
    def fail_json(*args, **kwargs):
        """function to patch over fail_json; package return data into an exception"""
        kwargs['failed'] = True
        raise AnsibleFailJson(kwargs)
