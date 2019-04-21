import requests
import json

nsqdipaddr = 'http://192.168.2.60:4151'


def publishnsqmessage(topicname, message):
    url = '%s/pub?topic=%s' % (nsqdipaddr, topicname)
    return requests.post(url, data=json.dumps(message))


if __name__ == '__main__':
    import sys
    topicname = 'crawlunvisitedalbum'
    uid = int(sys.argv[1])
    message = {'uid': uid}
    print publishnsqmessage(topicname, message)
