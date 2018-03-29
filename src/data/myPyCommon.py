#!/usr/bin/env python
import sys
from time import localtime, strftime
import time
import os
import commands
import pickle
import subprocess
from subprocess import Popen, list2cmdline
import zlib

#
kb   = 1.38066e-23 # J/K
q0   = 1.60218e-19 # C

###############################################################################
class MyException(Exception):
    pass

###############################################################################
def getEnvironmentVariable(name):
    try:
        return os.environ[name]
    except:
        printWarning('Enviroment variable %s does not exist' %name)
        return ''

###############################################################################
def getTimeString(toffset = 0, timepoint = None):
    currenttime = time.time()
    if timepoint != None:
        currenttime = timepoint
    return strftime("%a, %d %b %Y %H:%M:%S", localtime(currenttime + toffset))

def getCurrentTimeString2():
    return getTimeString2(timepoint = time.time())

def getTimeString2(toffset = 0, timepoint = None):
    currenttime = time.time()
    if timepoint != None:
        currenttime = timepoint
    return strftime("%02d.%02m.%Y@%02H:%02M:%02S", localtime(currenttime + toffset))

def secondsToTimestring(s):
    return time.strftime("%H:%M:%S", time.gmtime(s))

###############################################################################
def stripString(source):
    dest = ''
    for c in source:
        if ord(c) == 0:
            return dest
        dest += c

###############################################################################
def timeout(twait):
    out = time.time() + twait
    while out > time.time():
        pass

###############################################################################
def bashExe(cmd, parallel = False, maxThreads = 4):
    if parallel == False:
        print 'BashExe: Start job ' + italic(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        return process.communicate()[0]
    else:
        bashExeParallel(cmd, maxThreads = maxThreads)

def bashExeParallel(cmd, maxThreads = 4):
    if not cmd: 
        return

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)

    processes = []
    jobsstarted = 0
    while True:
        while jobsstarted < len(cmd) and len(processes) < maxThreads:
            printInfo('Start job %d of %d (max. %d parallel jobs)' %(jobsstarted+1, len(cmd), maxThreads))
            task = cmd[jobsstarted] #.pop() # don not remove items from list
            print 'BashExeParallel: Start job ' + italic(task)
            processes.append(Popen(task, shell=True))
            jobsstarted += 1

        for p in processes:
            if done(p):
                if success(p):
                    processes.remove(p)
                else:
                    fail()

        if not processes and not cmd:
            break
        else:
            time.sleep(0.5)

###############################################################################
def italic(txt):
    return '\x1B[3m' + txt + '\x1B[23m'
def red(txt):
    return '\033[01;31m' + txt + '\033[0m'
def blue(txt):
    return '\033[01;34m' + txt + '\033[0m'
def green(txt):
    return '\033[01;32m' + txt + '\033[0m'
def orange(txt):
    return '\033[01;36m' + txt + '\033[0m'
def yellow(txt):
    return '\033[01;33m' + txt + '\033[0m'

###############################################################################
def printInfo(text, bw = 0):
    if bw:
        print '# %s ### INFO:  ' %getTimeString() + text
    else:
        print blue('# %s ### INFO:  ' %getTimeString() + text)

###############################################################################
def printInfo2(text, bw = 0):
    if bw:
        print '# %s ### INFO:  ' %getTimeString() + text
    else:
        print green('# %s ### INFO:  ' %getTimeString() + text)

###############################################################################
def printFinished(text, bw = 0):
    if bw:
        print '# %s ### FINISHED:  ' %getTimeString() + text
    else:
        print green('# %s ### FINISHED:  ' %getTimeString() + text)

###############################################################################
def printWarning(text):
    msg = '# %s ### WARNING:  ' %getTimeString() + text
    print yellow(msg)
    return msg

###############################################################################
def printDevice(text):
    print yellow('# %s ### DEVICE:  ' %getTimeString() + text)

###############################################################################
def printMeasurement(text):
    print orange('# %s ### MEASUREMENT:  ' %getTimeString() + text)

###############################################################################
def printProcessInfo(text):
    print yellow('# %s ### PROCESSINFO:  ' %getTimeString() + text)

###############################################################################
def printError(text):
    print red('# %s ### ERROR: ' %getTimeString() + text)

###############################################################################
def printErrorAndQuit(text):
    print red('# %s ### ERROR: ' %getTimeString() + text)
    raise MyException({"message": text})

###############################################################################
def printDebug(text):
    print yellow('# %s ### DEBUG:  ' %getTimeString() + text)

###############################################################################
def printState(text):
    print blue('# %s ### STATE:  ' %getTimeString() + text)

###############################################################################
def valueToSi(value, forceUnit = None):
    if value == 0:
        return '0'

    if value < 0:
        s = '-'
        value *= -1
    else:
        s = ' '
        
    if forceUnit != None:
        units      = [ 'f', 'p', 'n', 'u', 'm' , ' ', 'k', 'M', 'G', 'T', 'P' ]
        multiplier = [ 1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1, 1e3, 1e6, 1e9, 1e12, 1e15 ]
        factor = multiplier[units.index(forceUnit)]
        
        s += '%3.3f%s' %(value / factor, forceUnit)
    else:
        if value >= 1.0e15:
            s += '%3.3fP' %(value / 1.0e15)
        elif value >= 1.0e12:
            s += '%3.3fT' %(value / 1.0e12)
        elif value >= 1.0e9:
            s += '%3.3fG' %(value / 1.0e9)
        elif value >= 1.0e6:
            s += '%3.3fM' %(value / 1.0e6)
        elif value >= 1.0e3:
            s += '%3.3fk' %(value / 1.0e3)
        elif value >= 1:
            s += '%3.3f ' %(value / 1.0)
        elif value >= 1.0e-3:
            s += '%3.3fm' %(value / 1.0e-3)
        elif value >= 1.0e-6:
            s += '%3.3fu' %(value / 1.0e-6)
        elif value >= 1.0e-9:
            s += '%3.3fn' %(value / 1.0e-9)
        elif value >= 1.0e-12:
            s += '%3.3fp' %(value / 1.0e-12)
        elif value >= 1.0e-15:
            s += '%3.3ff' %(value / 1.0e-15)
        elif value >= 1.0e-18:
            s += '%3.3fa' %(value / 1.0e-18)
        else:
            s += '%e ' %(value)

    # remove zeroes after '.'
    for k in range(len(s)-2, 0, -1):
        if s[k] == ' ':
            continue
        if s[k] == '0':
            s = '%s%s' %(s[0:k], s[k+1:]) # put k+1 to have empty space between value and Si unit
        elif s[k] == '.':
            s = '%s%s' %(s[0:k], s[k+1:])
            break
        else:
            break

    return s

###############################################################################
def valueToSiBytes(value):
    unit = ''

    if value < 1024:
        unit = ''
    else:
        value /= 1024

        if value < 1024:
            unit = 'k'
        else:
            value /= 1024

            if value < 1024:
                unit = 'M'
            else:
                value /= 1024
                unit = 'G'


    s = '%3.3lf%s' %(value, unit)
  
    # remove zeroes after '.'
    for k in range(len(s)-2, 0, -1):
        if s[k] == ' ':
            continue
        if s[k] == '0':
            s = '%s%s' %(s[0:k], s[k+1:]) # put k+1 to have empty space between value and Si unit
        elif s[k] == '.':
            s = '%s%s' %(s[0:k], s[k+1:])
            break
        else:
            break

    return s
###############################################################################
def parseCodedLine(line, convertToSi = True):
    params = {}

    for sub in line.rsplit():
        if len(sub) < 5: # units, don't care I always use Si units
            if convertToSi:
                params[key] = params[key] + sub
            continue
        
        els = sub.split('=')

        if len(els) != 2: # i just consider tuples
            continue

        key   = els[0]
        value = els[1]
        
        # convert value to an Si like string if is numerical
        try:
            if value.find(';') != -1: # new version
                value = value.split(';')[0]

            if convertToSi:
                value = valueToSi(float(value))
            else:
                value = float(value)
        except :
            value = value.replace(' ', '') # remove all white spaces

        params[key] = value
        
    return params

def getKeyValueFromLine(line, key):
    p1 = line.find(key) + len(key) + 1
    p2 = line.find(' ', p1)
    return (key, line[p1:p2])

def stringToUnitValue(s):
    vs = '' # value string
    us = '' # unit string

    print s
    done  = False
    value = True
 
    for c in s:
        if value:
            vs += c
            print vs
            if vs[-1] == '.' or vs[-1] == ' ':
                continue

            try:
                val  = float(c)
                #done = True
            except:
                us += c
                vs = vs[:-1]

                done = True
                #if len(vs) > 1:
                #    val = float(vs[:-1])
                #    done = True

            if done:
                value = False
        else:
            us += c

    print 'vs = ', vs
    print 'us = ', us

###############################################################################
def createCodedLine(infodict, ignoreKeys = [ ]):
    line = ''
    for key in infodict.keys():
        if key in ignoreKeys:
            continue
        line += '%s=%s ' %(key, str(infodict[key]))

    return line
       
###############################################################################
def dictToBinaryStream(infodict):
    return pickle.dumps(infodict)

def binaryStreamToDict(stream):
    return pickle.loads(stream)

###############################################################################
def checkFileExists(d):
    if os.path.isfile(d):
        return 1
    return 0

###############################################################################
def checkDirExists(d):
    return os.path.isdir(d)

###############################################################################
def checkFileExistsSSH(d, host):
    cmd = 'ssh %s \'ls %s\'' %(host, d)
    status, output = commands.getstatusoutput(cmd)
    if output.find('No such file') != -1:
        return 0
    return 1

###############################################################################
def checkAndMakeDir(d):
    if not os.path.isdir(d):
        os.makedirs(d)

###############################################################################
def checkAndMakeDirSSH(host, d):
    cmd = 'ssh %s \'ls %s\'' %(host, d)
    status, output = commands.getstatusoutput(cmd)
    if output.find('No such file'):
        cmd = 'ssh %s \'mkdir -p %s\'' %(host, d)
        status, output = commands.getstatusoutput(cmd)

###############################################################################
def fileCopySSHtoHost(host, src, dest):
    checkAndMakeDirSSH(host, dest[:dest.rfind('/')])
    cmd = 'scp -C %s %s:%s' %(src, host, dest)
    status, output = commands.getstatusoutput(cmd)

###############################################################################
def fileCopy(src, dest):
    checkAndMakeDir(dest[:dest.rfind('/')])
    cmd = 'cp %s %s' %(src, dest)
    status, output = commands.getstatusoutput(cmd)

###############################################################################
def fileCopySSHFromHost(host, src, dest):
    checkAndMakeDir(dest[:dest.rfind('/')])
    cmd = 'scp -C %s:%s %s' %(host, src, dest)
    status, output = commands.getstatusoutput(cmd)

###############################################################################
def parseCmdLineArgs(s):
    s = s[1:] # skip first, is programm name
    d = dict()
    i = 0
    while i < len(s):
        if (i+1) < len(s) and s[i+1][0] != '-':
            d[s[i]] = s[i+1]
            i += 2
        else:
            d[s[i]] = '1' 
            i += 1

    return d

###############################################################################
def getKey(config, key, tp):
    try:
        value = config[key]

        if tp == 'string':
            return str(value)
        elif tp == 'int':
            return int(value)
        elif tp == 'float':
            return float(value)
        else:
            printErrorAndQuit('invalid data type')
    except:
        printErrorAndQuit('wrong key or conversion failed')

###############################################################################
def checkAllKeysAvailable(config, keys):
    for key in keys:
        if not config.has_key(key):
            raise Exception("Key %s missing" %key)

def checkInvalidKeys(config, keys):
    keyConfig = []
    for key in config.keys():
        keyConfig += [key]

    print keyConfig

def checkInRange(value, lower, upper, comment = '', abort = False):
    if value < lower or value > upper:
        msg = 'Value for %s out of range (%e, %e)!' %(comment, lower, upper)
        if abort:
            printErrorAndQuit(msg)
        else:
            printError(msg)

def inrange(value, lower, upper):
    checkvalue = None
    if type(value) != type(list()):
        checkvalue = [ value ]
    else:
        checkvalue = value
    
    for val in checkvalue:
        if lower <= val and val <= upper:
            return True
    return False

###############################################################################
def save_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

###############################################################################
def load_obj(name):
    try:
        with open(name, 'rb') as f:
            return pickle.load(f)
    except:
        return None

###############################################################################
def convertDataType(configuration, key, finaltype):
    if finaltype == '2d-tuple':
        if type(configuration[key]) == type((0, 0)):
            if len(configuration[key]) == 2:
                configuration[key] = (float(configuration[key][0]), float(configuration[key][1]))
            else:
                printErrorAndQuit('Tuple has invalid length for %s' %key)
        else:
            try:
                configuration[key] = (float(configuration[key]), float(configuration[key]))
            except:
                printErrorAndQuit('Invalid data for convertDataType with finaltype = %s' %finaltype)
    if finaltype == 'floatlist':
        try:
            if type(configuration[key]) != type(list()):
                configuration[key] = [ configuration[key] ]
            for i in range(len(configuration[key])):
                configuration[key][i] = float(configuration[key][i])
        except:
            printErrorAndQuit('Could not convert data to list of floats: %s' %str(configuration[key]))
    if finaltype == 'intlist':
        try:
            if type(configuration[key]) != type(list()):
                configuration[key] = [ configuration[key] ]
            for i in range(len(configuration[key])):
                configuration[key][i] = int(configuration[key][i])
        except:
            printErrorAndQuit('Could not convert data to list of floats: %s' %str(configuration[key]))

    return configuration

###############################################################################
def checkKeyExists(configuration, key, default):
    if not configuration.has_key(key):
        configuration[key] = default
        printWarning('Configuration key %s is set to %s' %(key, default))
    return configuration

###############################################################################
def getConfigurationChecksum(configuration):
    data = pickle.dumps(configuration)
    return zlib.crc32(data)%2**32

###############################################################################
def factorization(n):
        primes = [ ]
        for i in range(2, n+1):
            while n%i == 0:
                primes += [ i ]
                n /= i
        return primes
