<img src="./locopod.png" alt="locopod" width="256">
=======

LOcal COPy On Demand - a convenient wrapper for rsync

Rsync is a brilliant tool to synchronize files between multiple machines. Though it is sometimes a hassle to use in a consistent way. Locopod allows to define settings (e.g. the local directory for files copied from external machines) that should be used uniformly and should be hidden from scripts that need to process files from other machines. Locopod allows to pull and push files or complete directories from/to other machines. The maximum available space for local copies can be configured, locopod takes care of this deleting older files automatically. Various authentification mechanisms are available: username:password for SSH and rsyncdemon, and pre-shared SSH-key.

## Configuration

The default configuration can be set up in the file locopod.config
```
# This is an example config file.
[config]
USERNAME = rsyncclient
CACHE_DIR = /path/to/cache_dir
PASSWORD_FILE = ./rsync.password
# 20 GB
MEMORY_QUOTA = 20480
```

### rsyncdemon

In case you decide for rsyncdemon username:password authentification put the secret password in the PASSWORD_FILE (default, can be overwritten with -k option). rsyncdemon needs to be configured as follows.

The main config (/etc/rsyncd.conf) should contain:
```
# Locopod uses the Folder [root]
[root]
    path = /
    comment = Root
    uid = rsync_user
    gid = rsync_group
    read only = no
    list = yes
    auth users = rsyncclient
    secrets file = /etc/rsyncd.secrets
    use chroot = no
```

Set rsync\_user and rsync\_group according your access policy. rsync\_user will be the owner of synced files. Put the secret password in /etc/rsyncd.secrets.

Start the rsync demon.

## Usage

```
USAGE: locopod.py [-q] [-u <uri> | -p <uri> | -b <uri> | -s | -f <amount> | -d <directory>] [-c <cacheDir>] [-l <user>] [-k <password_file>] [-w]
    -u - Pull a resource from the remote URI.
    -p - Push a local resource to the remote URI.
    -s - Query the available space on the cache directory's file system (in bytes).
    -f - Free the specified amount of space (in bytes).
    -d - List the contents of <directory> (can be an URI or local directory).
    -c - Specify the cache directory to use.
    -q - Run the program in quiet mode.
    -l - Specify the username on the remote host.
    -k - Specify a password file for authentication.
    -w - Use the faster but potentially weaker blowfish cipher for data encryption.
    -b - Return local base path.
```
