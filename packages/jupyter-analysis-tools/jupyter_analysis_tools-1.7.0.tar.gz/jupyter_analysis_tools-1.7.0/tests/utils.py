# -*- coding: utf-8 -*-
# tests/utils.py


import os
from pathlib import Path

from jupyter_analysis_tools.utils import (
    appendToPATH,
    isWindows,
    makeNetworkdriveAbsolute,
    naturalKey,
    networkdriveMapping,
)

# output of 'net use' command on Windows
outNetUse = r"""Neue Verbindungen werden gespeichert.


Status       Lokal     Remote                    Netzwerk

-------------------------------------------------------------------------------
OK           G:        \\ALPHA\BETA              Microsoft Windows Network
OK           K:        \\GAM\MMA                 Microsoft Windows Network
OK           M:        \\user\drive\uname        Microsoft Windows Network
OK           T:        \\test\foldername         Microsoft Windows Network
OK                     \\psi\folder              Microsoft Windows Network
Der Befehl wurde erfolgreich ausgeführt.
"""

# sample output of 'mount' command on Linux
outMount = (
    "sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)\n"
    "proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)\n"
    "tmpfs on /run type tmpfs (rw,nosuid,nodev,noexec,relatime,size=13148680k,mode=755,inode64)\n"
    "//abc02.def.ault.de/X23/somename on /mnt/some (ugly) on type name type cifs "
    "(rw,nosuid,nodev,relatime,vers=3.0,cache=strict,upcall_target=app,username=dhdhfh,"
    "uid=1000,forceuid,gid=1000,forcegid,addr=10.0.1.2,file_mode=0660,dir_mode=0770,soft,nounix,"
    "mapposix,rsize=4194304,wsize=4194304,bsize=1048576,retrans=1,echo_interval=60,actimeo=1,"
    "closetimeo=1)\n"
    "udev on /dev type devtmpfs (rw,nosuid,relatime,size=65700820k,nr_inodes=16425205,mode=755,"
    "inode64)\n"
    "//xyz04.fgsd.asd.com/G2S/GH31 on /mnt/gh 12 type cifs (rw,nosuid,nodev,relatime,vers=3.0,"
    "cache=strict,upcall_target=app,username=dhdhfh,uid=1000,forceuid,gid=1000,forcegid,"
    "addr=10.6.1.5,file_mode=0660,dir_mode=0770,soft,nounix,mapposix,rsize=4194304,wsize=4194304,"
    "bsize=1048576,retrans=1,echo_interval=60,actimeo=1,closetimeo=1)\n"
    "devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)"
)


def test_appendToPATH(capsys):
    # Setting up a PATH for testing first (platform dependent).
    testpath = "/usr/local/sbin:/usr/local/bin:/sbin:/usr/games:/usr/local/games:/snap/bin"
    if isWindows():
        testpath = "something else"
    os.environ["PATH"] = testpath
    assert os.environ["PATH"] == testpath

    if not isWindows():  # Linux edition
        appendToPATH("/tmp", ("one", "two"), verbose=True)
        captured = capsys.readouterr()
        assert (
            captured.out
            == """\
     /tmp/one [exists: False]
     /tmp/two [exists: False]
"""
        )
        assert os.environ["PATH"] == testpath + ":/tmp/one:/tmp/two"

    else:  # Windows edition
        appendToPATH(r"C:\Windows", ("one", "two"), verbose=True)
        captured = capsys.readouterr()
        assert (
            captured.out
            == """\
     C:\\Windows\\one [exists: False]
     C:\\Windows\\two [exists: False]
"""
        )
        assert os.environ["PATH"] == testpath + r";C:\Windows\one;C:\Windows\two"


def test_networkdriveMapping():
    if isWindows():
        map = networkdriveMapping(cmdOutput=outNetUse, resolveNames=False)
        assert map == {
            "G:": "\\\\ALPHA\\BETA",
            "K:": "\\\\GAM\\MMA",
            "M:": "\\\\user\\drive\\uname",
            "T:": "\\\\test\\foldername",
        }
    else:  # Linux or macOS
        map = networkdriveMapping(cmdOutput=outMount, resolveNames=False)
        assert map == {
            "/mnt/gh 12": "//xyz04.fgsd.asd.com/G2S/GH31",
            "/mnt/some (ugly) on type name": "//abc02.def.ault.de/X23/somename",
        }


def test_makeNetworkdriveAbsolute():
    if isWindows():
        filepath = Path(r"M:\some\folders\a file name.ext")
        newpath = makeNetworkdriveAbsolute(filepath, cmdOutput=outNetUse, resolveNames=False)
        assert filepath != newpath
        assert newpath == Path(r"\\user\drive\uname\some\folders\a file name.ext")
    else:  # Linux or macOS
        filepath = Path("/mnt/some (ugly) on type name/some/folders/a file name.ext")
        newpath = makeNetworkdriveAbsolute(filepath, cmdOutput=outMount, resolveNames=False)
        assert filepath != newpath
        assert newpath == Path("//abc02.def.ault.de/X23/somename/some/folders/a file name.ext")


def test_naturalKey():
    filelist = ["test2.ext", "test100.ext", "test1.ext", "test05.ext"]
    lstSorted = sorted(filelist, key=naturalKey)
    assert lstSorted == ["test1.ext", "test2.ext", "test05.ext", "test100.ext"]
