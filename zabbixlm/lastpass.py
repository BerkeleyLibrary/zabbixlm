import subprocess

class LastPass:
    @classmethod
    def get_password(cls, itemname):
        return subprocess.check_output(['lpass', 'show', '--password', itemname, '--sync', 'no']).strip().decode('utf-8')
