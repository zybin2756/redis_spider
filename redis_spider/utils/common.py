import hashlib


def get_md5(url):
    url = url.encode(encoding="gb2312")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()