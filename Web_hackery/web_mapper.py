# importing packages
import time
import os
import queue
import threading
import urllib.error
import urllib.parse
import urllib.request

threads = 10
target = "http://www.blackhatpython.com"
directory = "/home/anonymous/Virtual Home/CyberStuffs/Vulnerable systems/Joomla_3.9.22"
filters = [".jpg", ".gif", "png", ".css"]

os.chdir(directory)
web_paths = queue.Queue()

for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s%s" % (target, path)
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            print("[%d] => %s" % (response.code, path))
            response.close()
            time.sleep(5)
        except urllib.error.HTTPError as error:
            print("Failed %s" % error.code)
            pass


for i in range(threads):
    print("Spawning thread: %d" % i)
    t = threading.Thread(target=test_remote)
    t.start()