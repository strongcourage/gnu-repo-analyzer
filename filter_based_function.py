#!/usr/bin/env python3

import os
import difflib
import re
from git import Repo

count = 0

# projects = ['grep', 'make', 'gzip', 'bash', 'tar', 'coreutils']
projects = ['coreutils']

functions = [
        # 'sort','cut','test'
        # 'cat','yes','cp','chmod','chown','ls','paste','mv'


        'acpid','addgroup','adduser','adjtimex','ar','arp','arping','ash','awk'
        ,'basename','beep','blkid','brctl','bunzip2','bzcat','bzip2','cal','cat'
        ,'catv','chat','chattr','chgrp','chmod','chown','chpasswd','chpst','chroot'
        ,'chrt','chvt','cksum','clear','cmp','comm','cp','cpio','crond','crontab'
        ,'cryptpw','cut','date','dc','dd','deallocvt','delgroup','deluser','depmod'
        ,'devmem','df','dhcprelay','diff','dirname','dmesg','dnsd','dnsdomainname'
        ,'dos2unix','dpkg','du','dumpkmap','dumpleases','echo','ed','egrep','eject'
        ,'env','envdir','envuidgid','expand','expr','fakeidentd','false','fbset'
        ,'fbsplash','fdflush','fdformat','fdisk','fgrep','find','findfs','flash_lock'
        ,'flash_unlock','fold','free','freeramdisk','fsck','fsck.minix','fsync'
        ,'ftpd','ftpget','ftpput','fuser','getopt','getty','grep','gunzip','gzip','hd'
        ,'hdparm','head','hexdump','hostid','hostname','httpd','hush','hwclock','id'
        ,'ifconfig','ifdown','ifenslave','ifplugd','ifup','inetd','init','inotifyd'
        ,'insmod','install','ionice','ip','ipaddr','ipcalc','ipcrm','ipcs','iplink'
        ,'iproute','iprule','iptunnel','kbd_mode','kill','killall','killall5','klogd'
        ,'last','length','less','linux32','linux64','linuxrc','ln','loadfont'
        ,'loadkmap','logger','login','logname','logread','losetup','lpd','lpq','lpr'
        ,'ls','lsattr','lsmod','lzmacat','lzop','lzopcat','makemime','man','md5sum'
        ,'mdev','mesg','microcom','mkdir','mkdosfs','mkfifo','mkfs.minix','mkfs.vfat'
        ,'mknod','mkpasswd','mkswap','mktemp','modprobe','more','mount','mountpoint'
        ,'mt','mv','nameif','nc','netstat','nice','nmeter','nohup','nslookup','od'
        ,'openvt','passwd','patch','pgrep','pidof','ping','ping6','pipe_progress'
        ,'pivot_root','pkill','popmaildir','printenv','printf','ps','pscan','pwd'
        ,'raidautorun','rdate','rdev','readlink','readprofile','realpath'
        ,'reformime','renice','reset','resize','rm','rmdir','rmmod','route','rpm'
        ,'rpm2cpio','rtcwake','run-parts','runlevel','runsv','runsvdir','rx','script'
        ,'scriptreplay','sed','sendmail','seq','setarch','setconsole','setfont'
        ,'setkeycodes','setlogcons','setsid','setuidgid','sh','sha1sum','sha256sum'
        ,'sha512sum','showkey','slattach','sleep','softlimit','sort','split'
        ,'start-stop-daemon','stat','strings','stty','su','sulogin','sum','sv'
        ,'svlogd','swapoff','swapon','switch_root','sync','sysctl','syslogd','tac'
        ,'tail','tar','taskset','tcpsvd','tee','telnet','telnetd','test','tftp','tftpd'
        ,'time','timeout','top','touch','tr','traceroute','true','tty','ttysize'
        ,'udhcpc','udhcpd','udpsvd','umount','uname','uncompress','unexpand','uniq'
        ,'unix2dos','unlzma','unlzop','unzip','uptime','usleep','uudecode','uuencode'
        ,'vconfig','vi','vlock','volname','watch','watchdog','wc','wget','which','who'
        ,'whoami','xargs','yes','zcat','zcip'
        ]

for project in projects:

    repo = Repo(project)

    f2commits={}
    for f in functions:
        f2commits[f] = []
    
    for commit in repo.iter_commits("master"):
        if len(commit.parents) == 0:
            continue
        diffIndex = commit.diff(commit.parents[0])
        
        changed_tests = False

        for diff in diffIndex.iter_change_type('A'):
            # print(diff.b_path)
            if re.match('.*test.*', diff.b_path):
                changed_tests = True

        changed_function = False
        modified_source = []
        for diff in diffIndex.iter_change_type('M'):
            # print(diff.a_path)               
            # if re.match(find_f, diff.b_path):
            #     changed_function = True
                
            if re.match('.*test.*', diff.b_path):
                changed_tests = True

            _, extension = os.path.splitext(diff.a_path)
            if extension == '.c':
                modified_source.append(diff)
        if len(modified_source) == 0 or len(modified_source) > 2:
            continue

        too_long = False
        has_array = False
        has_struct = False
        has_pointer = False

        for diff in modified_source:
            b = diff.b_blob.data_stream.read()
            if not isinstance(b, str):
                b = b.decode("latin-1")
            a = diff.a_blob.data_stream.read()
            if not isinstance(a, str):
                a = a.decode("latin-1")
            ud = difflib.unified_diff(b.splitlines(keepends=True),
                                      a.splitlines(keepends=True), n=0)
            plus_count = 0
            minus_count = 0
            for line in ud:
                if line.startswith('-'):
                    if re.match('.*\[.*\].*', line):
                        has_array = True
                    if re.match('.*memset.*', line):
                        has_array = True
                    if re.match('.*memcpy.*', line):
                        has_array = True
                    if re.match('.*->.*', line):
                        has_struct = True
                    if re.match('.*\*.*', line):
                        has_pointer = True
                    minus_count = minus_count + 1
                if line.startswith('+'):
                    if re.match('.*\[.*\].*', line):
                        has_array = True
                    if re.match('.*memset.*', line):
                        has_array = True
                    if re.match('.*memcpy.*', line):
                        has_array = True
                    if re.match('.*->.*', line):
                        has_struct = True
                    if re.match('.*\*.*', line):
                        has_pointer = True
                    plus_count = plus_count + 1
            if plus_count + minus_count > 10:
                too_long = True

        if too_long or not changed_tests or not (has_array or has_pointer or has_struct):# or not changed_function:
            continue

        # if has_array:
        #     print("ARRAY")
        # if has_pointer:
        #     print("POINTER")
        # if has_struct:
        #     print("STRUCT")

        count = count + 1
        # print("http://git.savannah.gnu.org/cgit/{}.git/commit/?id={}".format(project, commit.hexsha))
        
        for f in functions:
            find_f = '.*src/' + f + '.c*'
            for diff in diffIndex.iter_change_type('M'):
                # print(diff.b_path)
                if re.match(find_f, diff.a_path):
                    print("http://git.savannah.gnu.org/cgit/{}.git/commit/?id={}".format(project, commit.hexsha))
                    f2commits[f].append("http://git.savannah.gnu.org/cgit/{}.git/commit/?id={}".format(project, commit.hexsha))
                
    for f in f2commits:
        print("--------------------------------------------------------------------------------------")
        print(f)
        for com in f2commits[f]:
            print(com)

    # print("Total: {}".format(count))
