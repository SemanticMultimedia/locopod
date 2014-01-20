#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a ...

### Example Use Case: ###

"""

import sys, os, getopt, subprocess, socket
from functools import partial
from ConfigParser import RawConfigParser

# Default values of global variables
CACHE_DIR = "./"
USERNAME = ""
PASSWORD_FILE = ""
QUIET = False
HOST_IP = socket.gethostbyname(socket.getfqdn())
WEAK_ENCRYPTION = False
MEMORY_QUOTA = 0 # in MB. 0 means: no limit.

# Only variables in this list can be configured via locopod.config.
# They must have a default value specified above.
GLOBAL_VARS = ["CACHE_DIR", "USERNAME", "PASSWORD_FILE", "QUIET", "HOST_IP", "WEAK_ENCRYPTION", "MEMORY_QUOTA"]

def print_usage():
	print 'USAGE: locopod.py [-q] [-u <uri> | -p <uri> | -b <uri> | -s | -f <amount>]'
	print '\t\t[-c <cacheDir>] [-l <user>] [-k <password_file>] [-w]\n'
	print '\t-u\t-\tPull a resource from the remote URI.'
	print '\t-p\t-\tPush a local resource to the remote URI.'	
	print '\t-s\t-\tQuery the available space on the cache directory\'s file system (in bytes).'
	print '\t-f\t-\tFree the specified amount of space (in bytes).'
	print '\t-c\t-\tSpecify the cache directory to use.'
	print '\t-q\t-\tRun the program in quiet mode.'
	print '\t-l\t-\tSpecify the username on the remote host.'
	print '\t-k\t-\tSpecify a password file for authentication.'
	print '\t-w\t-\tUse the faster but potentially weaker blowfish cipher for data encryption.'
	print '\t-b\t-\tReturn local base path.'

def print_debug(*messages):
	if not QUIET:
		for msg in messages:
			print msg,
		print "" # for the newline


def read_config():
	# config file should be placed in same directory as the script
	config_file_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "locopod.config")
	parser = RawConfigParser()

	try:
		parser.readfp(open(config_file_path))
	except IOError:		
		return

	for name, value in parser.items("config"):
		name = name.upper()
		if name in GLOBAL_VARS:
			default = globals()[name]
			if type(default) == type(1):
				value = parser.getint("config", name)
			elif type(default) == type(1.0):
				value = parser.getfloat("config", name)
			elif type(default) == type(True):
				value = parser.getboolean("config", name)
			globals()[name] = value


# Set configuration variables from command line options.
def set_config(opts):
	global CACHE_DIR
	global USERNAME
	global QUIET
	global PASSWORD_FILE
	global WEAK_ENCRYPTION

	if "-c" in opts or "--cacheDir" in opts:
		CACHE_DIR = opts.get("-c", opts.get("--cacheDir"))
		if not CACHE_DIR[-1] == "/":
			CACHE_DIR += "/"

	if "-l" in opts:		
		USERNAME = opts["-l"]

	if "-q" in opts:
		QUIET = True

	if "-k" in opts:
		PASSWORD_FILE = opts["-k"]

	if "-w" in opts:
		WEAK_ENCRYPTION = True

	PASSWORD_FILE = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), PASSWORD_FILE))

# opts should be a dictionary of (option -> argument)
def choose_operation(opts):
	operation = None
	params = []

	for opt in opts:
		if opt == '-h':
			print_usage()
			sys.exit()
	  	elif opt in ("-u", "--uri"):
			operation = pull
			params = [opts[opt]]
		elif opt in ("-b", "--basePath"):
			operation = base_path
			params = [opts[opt]]
	  	elif opt in ("-s", "--space"):
			operation = query_free_space
			params = [CACHE_DIR]
		elif opt in ("-p", "--push"):
			operation = push
			params = [opts[opt]]
		elif opt in ("-f", "--free"):
			operation = free_space
			params = [CACHE_DIR, int(opts[opt])]
	
	return operation, params


def main(argv):
	if not argv:
		print_usage()
		sys.exit(1)

	try:
		opts, _ = getopt.getopt(argv,"qhp:sf:u:b:c:l:k:w",["push=", "space", "free=", "uri=", "cacheDir=", "basePath="])
	except getopt.GetoptError:
	  	print_usage()
	  	sys.exit(2)

	read_config()

	opts = dict(opts)
	set_config(opts)
	operation, params = choose_operation(opts)

	if operation:
		print operation(*params)
	else:
		print_usage()
		sys.exit(1)


def query_free_space(d):
	"""Returns the amount of free space available to non-super users (in bytes). (UNIX-specific?)"""	

	stats = os.statvfs(d)
   	return stats.f_bavail * stats.f_bsize


def directory_size(path):
	"""Return the size of the given directory in bytes."""
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


def free_space(path, amount):
	remaining = free_space_rec(path, amount)
	return amount - remaining


def free_space_rec(path, amount):
	"""In the given directory, free space equal to or greater than the given amount in bytes."""

	print_debug(path, amount)

	if os.path.isfile(path):
		size = os.lstat(path).st_size
		os.remove(path)
		return amount - size

	# sort directory entries by modification time (oldest first)
	# TODO: It's still somewhat random, which files get deleted first.
	# E.g., files will always be deleted prior to any directory on the same level.
	# Also, deleting files in a directory changes it's mtime, so it won't be considered
	# first the next time this function is called, although it is still the
	# oldest directory.
   	entries = sorted(os.listdir(path), key=partial(modification_time, path))

	for name in entries:
		if name == "." or name == "..":
			continue
		amount = free_space_rec(os.path.join(path, name), amount)
		
		if amount <= 0:
			break

	# Remove directory, if it is empty now.
	if not os.listdir(path) and path != CACHE_DIR:
		size = os.lstat(path).st_size
		os.rmdir(path)
		amount -= size

	return amount


def enforce_memory_quota():
	if MEMORY_QUOTA <= 0:
		return

	conversion = 1048576.0 # = 1024 * 1024
	# used disk space in MB. 
	used = directory_size(CACHE_DIR) / conversion
	if used >= MEMORY_QUOTA:
		# Free at least 10 percent of the maximum available memory,
		# plus whatever we are currently using above the threshold.
		free = used - MEMORY_QUOTA + (MEMORY_QUOTA * 0.1)
		free_space(CACHE_DIR, free * conversion)
	

def push(remote):
	"""
	Pushes changed resources from the local cache to the remote resource.

	Expects remote to be a URI of the form 'host:/absolute/path/' and
	will synchronize the directory 'CACHE_DIR/host_ip/absolute/path' if it exists.
	"""	

	# handle request locally?
	if is_local_request(remote):
		# assumption: files have been changed locally and
		# don't need to be pushed into another directory
		return True

	local = get_cache_dir(remote)

	if not os.path.isdir(local):
		print_debug("There is no cached directory.")
		return False

	# this is needed in case the remote URI doesn't contain a trialing slash
	local += os.path.basename(remote)

	if USERNAME:
		remote = "%s@%s" % (USERNAME, remote)

	return (not sync_files(local, remote))


def pull(remote):
   	"""
	Retrieves a resource from the master to the local workspace

	Expects remote to be a URI of the form 'host::root/absolute/path/' and
	will save the resources in the directory 'CACHE_DIR/host_ip/absolute/path/'.
	"""

	# Cases: URI on remote host, URI on local host
	remote_path = split_url(remote)[1]

	# handle request locally?
	if is_local_request(remote):
		# return the path portion of the URI
		return remote_path
	
	filename = os.path.basename(remote_path)
	cache_dir = get_cache_dir(remote)

	print_debug("Copy from %s to %s" % (remote, cache_dir))
	
	if not os.path.isdir(cache_dir):
		os.makedirs(cache_dir)

	#print "USER: " + USERNAME
	if USERNAME:
		remote = "%s@%s" % (USERNAME, remote)

	result = sync_files(remote, cache_dir)

	if result != 0:		
		return False

	touch_directories(cache_dir)
	enforce_memory_quota()
	return cache_dir + filename


def base_path(remote):
	"""Returns the local base path within the cache dir for the given uri."""

	# Cases: URI on remote host, URI on local host
	remote_path = split_url(remote)[1]

	# handle request locally?
	if is_local_request(remote):
		# return the path portion of the URI
		return remote_path

	filename = os.path.basename(remote_path)
	cache_dir = get_cache_dir(remote)

	return cache_dir + filename


def sync_files(src, dest):
	
	if PASSWORD_FILE:
		# Private-Key authentication
		cmd  = ["rsync", "-OrLptgoDz", "--password-file=%s" % PASSWORD_FILE, src, dest]
	else:
		# Username and password authentication
		cmd  = ["rsync", "-OrLptgoDz", src, dest]
	
	if QUIET:
		cmd.insert(1, "-q")

	print_debug(cmd)
	return execute( cmd )


def touch_directories(path):
	print_debug("Touching: " + path)

	if path == CACHE_DIR or path == CACHE_DIR + "/":
		return
	elif os.path.isdir(path):
		os.utime(path, None)

	touch_directories(path.rsplit("/", 2)[0] + "/")

def split_url(remote):
	components = remote.split("::root", 1)
	if len(components) == 2:
		host, remote_path = components
	else: # URL reference a module other than the 'root' module
		try:
			host, remote_path = remote.split("::")
		except ValueError:
			print "Currently, only URLs in rsync's archive syntax are supported."
			raise
	return (host, remote_path)


def is_local_request(remote):
	host = split_url(remote)[0]
	remote_host_ip = socket.gethostbyname(host)	
	return (remote_host_ip == HOST_IP or remote_host_ip == "127.0.0.1")
	#return not ("::" in remote)


def get_cache_dir(remote):
	host, remote_path = split_url(remote)
	if remote_path[0] == "/":
		remote_path = remote_path[1:]
	return os.path.join(CACHE_DIR, host, os.path.dirname(remote_path) + "/")


def modification_time(directory, f):
	return os.lstat(os.path.join(directory, f)).st_mtime


def execute(cmd):
	proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE);
	return proc.wait()

if __name__ == "__main__":
   	main(sys.argv[1:])
