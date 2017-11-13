import os
from click.testing import CliRunner
from subprocess import call, Popen, check_output

from twindb_backup.cli import main


def test_restore(instance1, config_content_ssh, tmpdir):

    my_cnf = tmpdir.join('.my.cnf')
    my_cnf.write("""
[client]
user=dba
password=qwerty
""")
    config = tmpdir.join('twindb-backup.cfg')
    id_rsa = tmpdir.join('id_rsa')
    id_rsa.write("""-----BEGIN RSA PRIVATE KEY-----
MIIEoAIBAAKCAQEAyXxAjPShNGAedbaEtltFI6A7RlsyI+4evxTq6uQrgbJ6Hm+p
HBXshXQYXDyVjvytaM+6GKF+r+6+C+6Wc5Xz4lLO/ZiSCdPbyEgqw1JoHrgPNpc6
wmCtjJExxjzvpwSVgbZg3xOdqW1y+TyqeUkXEg/Lm4VZhN1Q/KyGCgBlWuAXoOYR
GhaNWqcnr/Wn5YzVHAx2yJNrurtKLVYVMIkGcN/6OUaPpWqKZLaXiK/28PSZ5GdT
DmxRg4W0pdyGEYQndpPlpLF4w5gNUEhVZM8hWVE29+DIW3XXVYGYchxmkhU7wrGx
xZR+k5AT+7g8VspVS8zNMXM9Z27w55EQuluNMQIBIwKCAQAzz35QIaXLo7APo/Y9
hS8JKTPQQ1YJPTsbMUO4vlRUjPrUoF6vc1oTsCOFbqoddCyXS1u9MNdvEYFThn51
flSn6WhtGJqU0BPxrChA2q0PNqTThfkqqyVQCBQdCFrhzfqPEaPhl1RtZUlzSh01
IWxVGgEn/bfu9xTTQk5aV9+MZQ2XKe4BGzpOZMI/B7ivRCcthEwMTx92opr52bre
4t7DahVLN/2Wu4lxajDzCaKXpjMuL76lFov0mZZN7S8whH5xSx1tpapHqsCAwfLL
k49lDdR8aN6oqoeK0e9w//McIaKxN2FVxD4bcuXiQTjihx+QwQOLmlHSRDKhTsYg
4Q5bAoGBAOgVZM2eqC8hNl5UH//uuxOeBKqwz7L/FtGemNr9m0XG8N9yE/K7A5iX
6EDvDyVI51IlIXdxfK8re5yxfbJ4YevenwdEZZ2O8YRrVByJ53PV9CcVeWL4p6f/
I56sYyDfXcnDTEOVYY0mCfYUfUcSb1ExpuIU4RvuQJg6tvbdxD9FAoGBAN4/pVCT
krRd6PJmt6Dbc2IF6N09OrAnLB3fivGztF5cp+RpyqZK4ve+akLoe1laTg7vNtnF
l/PZtM9v/VT45hb70MFEHO+sKvGa5Yimxkb6YCriJOcLxTysSgFHKz7v+8BqqoHi
qY4fORGwPVDv28I8jKRvcuNHendV/Rdcuk79AoGAd1t1q5NscAJzu3u4r4IXEWc1
mZzClpHROJq1AujTgviZInUu1JqxZGthgHrx2KkmggR3nIOB86/2bdefut7TRhq4
L5+Et24VzxKgSTD6sJnrR0zfV3iQvMxbdizFRBsaSoGyMWLEdHn2fo4xzMem9o6Q
VwNsdMOsMQhA1rsxuiMCgYBr8wcnIxte68jqxC1OIXKOsmnKi3RG7nSDidXF2vE1
JbCiJMGD+Hzeu5KyyLDw4rgzI7uOWKjkJ+obnMuBCy3t6AZPPlcylXPxsaKwFn2Q
MHfaUJWUyzPqRQ4AnukekdINAJv18cAR1Kaw0fHle9Ej1ERP3lxfw6HiMRSHsLJD
nwKBgCIXVhXCDaXOOn8M4ky6k27bnGJrTkrRjHaq4qWiQhzizOBTb+7MjCrJIV28
8knW8+YtEOfl5R053SKQgVsmRjjDfvCirGgqC4kSAN4A6MD+GNVXZVUUjAUBVUbU
8Wt4BxW6kFA7+Su7n8o4DxCqhZYmK9ZUhNjE+uUhxJCJaGr4
-----END RSA PRIVATE KEY-----
""")
    content = config_content_ssh.format(
        PRIVATE_KEY=str(id_rsa),
        BACKUP_DIR="/etc",
        HOST_IP=instance1['ip']
    )
    config.write(content)
    cmd = ['sudo', 'twindb-backup', '--debug',
           '--config', str(config),
           'backup', 'hourly']
    assert call(cmd) == 0

    cmd = ["sudo", "twindb-backup", '--debug', '--config', str(config), "ls", "| grep etc", "| grep tmp",
           "| awk -F/ '{ print $NF}'", "| sort", "| tail -1"]
    basename = check_output(args=cmd)
    cmd = ["sudo", "twindb-backup", '--debug', '--config', str(config), "ls", "| grep %s" % basename, "| head -1"]

    url = check_output(cmd)
    runner = CliRunner()
    print('Url:')
    print(url)
    result = runner.invoke(main,
                           ['--config', str(config),
                            'restore', 'file', url, "--dst", "/tmp/test_dir"]
                           )
    if result.exit_code != 0:
        print('Command output:')
        print(result.output)
        print(result.exception)
        print(result.exc_info)
    assert result.exit_code == 0
    assert os.listdir("/tmp/test_dir") is not None
