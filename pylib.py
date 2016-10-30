# -*- python -*-
# author: krozin@gmail.com
# pylib: created 2014/03/01.
# copyright

def get_random_mac():
    import random
    return ':'.join(map(lambda x: "%02x" % x, [0x00,0x16,0x3e,random.randint(0x00, 0x7f),random.randint(0x00, 0xff),random.randint(0x00, 0xff)]))

def get_random_ip4():
    import random
    return ".".join(map(lambda x: str(random.randint(0,256)), [i for i in range(0,4)]))

def get_random_ip4net():
    import random
    return get_random_ip4()+"/"+str(random.choice([16,24]))

def get_random_uuid():
    import uuid
    import hashlib
    import os
    l = os.urandom(30).encode('base64')[:-1]
    return hashlib.sha256(l).hexdigest()

def get_sha(s):
    import uuid
    import hashlib
    import os
    return hashlib.sha256(s).hexdigest()

def generate_tmp_files(targetdict="/tmp/files/"):
    import os
    import random
    import time
    import threading

    if not os.path.exists(targetdict):
        os.makedirs(targetdict)
    class FileThread(threading.Thread):
        def run(self):
            print "run"
            while(True):
                filenames = []
                countf = (random.choice([1,2,3]))
                for i in xrange(0, countf):
                    filenames.append(os.path.join(targetdict, get_random_uuid()))
                for i in filenames:
                    with (open(i, 'w')) as nfile:
                        nfile.write(get_random_ip4())
                time.sleep(1)
    mythread = FileThread()
    mythread.start()

def generate_file_name():
    from datetime import datetime
    import random
    filename = "_".join([datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"), str(random.randint(1,100))])
    return filename


def check_new_files(directory):
    import os
    new_files = []
    for root, _, files in os.walk(directory):
        if files:
            abs_root = os.path.abspath(root)
            for fd in files:
                new_files.append(os.path.join(abs_root, fd))
        break
    return new_files

def get_base64_from_file(filepath):
    import base64
    import os
    encoded_string = ""
    if os.path.exists(filepath):
        with open(filepath, "rb") as ifile:
            encoded_string = base64.b64encode(ifile.read())
    return encoded_string

def make_cleanup(s):
    """clean up string: remove IP/IP6/Mac/etc... by using regexp

    :param s: str - input string
    :return: s after regexp and clean up
    """

    # let's try to find all IP, IP6, MAC
    ip4re = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ip6re = re.compile(r'\b(?:[a-fA-F0-9]{4}[:|\-]?){8}\b')
    macre = re.compile(r'\b[a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:]'
                       r'[a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:]'
                       r'[a-fA-F0-9]{2}[:][a-fA-F0-9]{2}\b')
    punctuation = re.compile(r'["\'!,?.:;\(\)\{\}\[\]\/\\]+')

    def ismatch(match):
        value = match.group()
        return " " if value else value
    s = ip4re.sub(ismatch, s)
    s = ip6re.sub(ismatch, s)
    s = macre.sub(ismatch, s)
    s = punctuation.sub(ismatch, s)
    return s

def image2text(filepath, lang='rus'):
    import os
    from PIL import Image
    import pytesseract
    if os.path.exists(filepath):
        print pytesseract.image_to_string(Image.open(filepath), lang=lang)
        return pytesseract.image_to_string(Image.open(filepath), lang=lang)

def distance(astr, bstr):
    """Calculates the Levenshtein distance between a and b

    :param astr: str - input string
    :param bstr: str - input string
    :return: distance: int - distance between astr and bstr
    """

    alen, blen = len(astr), len(bstr)
    if alen > blen:
        astr, bstr = bstr, astr
        alen, blen = blen, alen
    row = list(range(alen + 1))  # Keep current row
    for i in range(1, blen + 1):
        change = i-1
        row[0] = i
        for j in range(1, alen + 1):
            if astr[j - 1] != bstr[i - 1]:
               change += 1  
            add = row[j] + 1
            delete = row[j - 1] + 1
            row[j] = min(add, delete, change)
            change = add - 1 #previous value of row[j]
    return row[alen]

# decorator which print how many time were spend on fucntion
def benchmark(func):
    import time
    def wrapper(*args, **kwargs):
        t = time.clock()
        res = func(*args, **kwargs)
        #print func.__name__
        print(time.clock() - t)
        return res
    return wrapper

# decorator which counting call of function
def counter(func):
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        res = func(*args, **kwargs)
        print("{0} invoked: {1}x times".format(func.__name__, wrapper.count))
        return res
    wrapper.count = 0
    return wrapper

