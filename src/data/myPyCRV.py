#!/usr/bin/env python

import os
import sys
import myPyCommon
from struct import pack, unpack
import myPyCommon as common
import copy

ext_crv = '.crv'
ext_brv = '.brv'

binary16  = 1
binary24  = 2
binary32  = 4
#binary64  = 8
curvefile = 16

binaryID    = 0x02 # first initial version
binaryIDx3  = 0x03 # additional #t line to save columns as strings

blockID   = 0x10

# column data type
COLDATA_NUM    = 0
COLDATA_STRING = 1

def newCrvFile():
    crvout = CRV()
    crvout.addBlock(CRVBlock())
    return crvout

def mergefiles(files, commonColumn, outfile):
    data     = {}
    infoline = ''
    for i,f in enumerate(files):
        inf = CRV(f)[0]
        infoline += inf.getInfoLine() + ' '
        names = inf.getColumnNames()

        if i == 0: # init dataset
            for n in names:
               data[n] = copy.deepcopy(inf.getColumn(name = n))
        else:
            commondata = copy.deepcopy(inf.getColumn(name = commonColumn)) 
            for n in names:
                if n == commonColumn:
                    continue
                if data.has_key(n):
                    common.printErrorAndQuit('Column "%s" already exists, can\'t merge' %n)
                datmerge = copy.deepcopy(inf.getColumn(name = n))

                # merge into it
                data[n]     = copy.deepcopy(datmerge)
                for i in range(len(data[n][-1])): # delete values
                    data[n][-1][i] = 0.
                for pos, el in enumerate(data[commonColumn][-1]):
                    idx = commondata[-1].index(el)
                    data[n][-1][pos] = datmerge[-1][idx]
                    
    # write data to new file
    crvo = newCrvFile()
    crvo[0].addInfoLine(infoline)
    for key in data.keys():
        crvo[0].addColumn(data = data[key])
    crvo.writeCRVFile(outfile)

def getInfoLine(filename, block = 0):
    return common.parseCodedLine(CRV(filename)[block].getInfoLine(), convertToSi = False)

def CRVtoBRV(crvfilename, brvfilename, fileformat = 4):
    crv = CRV()
    crv.readCRVFile(crvfilename)
    crv.writeBinaryCRVFile(brvfilename, fileFormat = fileformat)

def BRVtoCRV(brvfilename, crvfilename):
    crv = CRV()
    crv.readBinaryCRVFile(brvfilename)
    crv.writeCRVFile(crvfilename)

def mergeSingleCRVFiles(inFiles = [], outFile = ''):

    crvOut = CRV()

    for filename in inFiles:
        crvIn = CRV()
        print 'reading ', filename
        crvIn.readCRVFile(filename)
        
        crvOut.addBlock(crvIn.getBlock(0))

    # write merged file
    crvOut.writeCRVFile(outFile)


def mergeSingleBRVFiles(inFiles = [], outFile = ''):

    crvOut = CRV()

    for filename in inFiles:
        crvIn = CRV()
        print 'reading ', filename
        crvIn.readBinaryCRVFile(filename)
        
        crvOut.addBlock(crvIn.getBlock(0))

    # write merged file
    crvOut.writeBinaryCRVFile(outFile)

def getBlockCountFromBinary(brvfile):
    return CRV().readBinaryCRVFile(brvfile, justEvalBlockCount = True)

class CRVBlock:
    _data        = [] # list for data values of type, name = colname
    _tstress     = {} # contains #s
    _comments    = [] # contains comments marked by #c
    _unknownHash = [] # contains all unknown # parameters
    _b           = 32 # binary parameter
    _p           = 1  # p parameter

    def __init__(self):
        self._data     = []
        self._comments = []
        self._tstress  = {}
        self._comments = []
        self._unknownHash = []
        self._b = 0
        self._p = 1

    def __len__(self):
        return self.getColumnCount()
        
    def addComment(self, s):
        self._comments += [s]

    def getComments(self):
        return self._comments

    def addColumn(self, name = '', unit = 'mV', offset = 0.0, scale = 1.0, datatype = 0, vals = [], data = None):
        if len(vals):
            if type(vals[0]) == str and datatype == 0:
                print 'Column \'%s\' is string column, selected automatically' %name
                datatype = 1

        if data != None:
            self._data += [data]
        else:
            self._data += [(name, unit, float(offset), float(scale), datatype, vals)]

    def getColumn(self, name = '', idx = -1):
        if idx != -1:
            return self._data[idx]
        else:
            for (n, u, o, s, t, dat) in self._data:
                if name == n:
                    return (n, u, o, s, t, dat)

    def getColumnNames(self):
        return [n for (n, _, _, _, _, _) in self._data]

    def hasColumn(self, name):
        colNames = self.getColumnNames()
        if not colNames or colNames.count(name) == 0:
            return False
        return True

    def getColumnData(self, name = '', idx = -1):
        if idx == -1:
            colNames = self.getColumnNames()
            if not colNames or colNames.count(name) == 0:
                myPyCommon.printErrorAndQuit('Column "%s" not found in %s' % (name, str(colNames)))

        #print 'x', self.getColumn(name, idx)[0]
        (n, u, o, s, t, dat) = self.getColumn(name, idx)

        if t == 0: # we have numbers
            return [d*s + o for d in dat]
        elif t == 1: # we have strings
            return [d for d in dat]
        else:
            myPyCommon.printErrorAndQuit('Invalid data type')

    def __getitem__(self, b):
        if type(b) == type(''): # check if b is a string
            return self.getColumnData(name = b)
        return self.getColumnData(idx = b)

    def getColumnLinesWithoutNAN(self, name = '', idx = -1):
        (n, u, o, s, t, dat) = self.getColumn(name, idx)
        
        for i in range(len(dat)-1, -1, -1):
            if dat[i] == dat[i]: # is not nan
                return i

        return -1

    def getColumnCount(self):
         return len(self._data)
       
    def __len__(self):
         return len(self._data)

    def getColumnName(self, idx = 0):
        if idx < len(self._data):
            return self._data[idx][0]
        else:
            return ''

    def getColumnUnit(self, idx = 0):
        if idx < len(self._data):
            return self._data[idx][1]
        else:
            return ''

    def setColumnName(self, idx, name):
        while idx >= len(self._data):
            self._data += [('', '', 0, 1, 0, [])]
        self._data[idx] = (name, self._data[idx][1], self._data[idx][2], self._data[idx][3], self._data[idx][4], self._data[idx][5])
      
    def setColumnUnit(self, idx, unit):
        while idx >= len(self._data):
            self._data += [('', '', 0, 1, 0, [])]
        self._data[idx] = (self._data[idx][0], unit, self._data[idx][2], self._data[idx][3], self._data[idx][4], self._data[idx][5])
        
    def setColumnOffset(self, idx, offset):
        while idx >= len(self._data):
            self._data += [('', '', 0, 1, 0, [])]
        self._data[idx] = (self._data[idx][0], self._data[idx][1], float(offset), self._data[idx][3], self._data[idx][4], self._data[idx][5])

    def setColumnScale(self, idx, scale):
        while idx >= len(self._data):
            self._data += [('', '', 0, 1, 0, [])]
        self._data[idx] = (self._data[idx][0], self._data[idx][1], self._data[idx][2], float(scale), self._data[idx][4], self._data[idx][5])

    def setColumnDataType(self, idx, datatype):
        while idx >= len(self._data):
            self._data += [('', '', 0, 1, 0, [])]
        self._data[idx] = (self._data[idx][0], self._data[idx][1], self._data[idx][2], self._data[idx][3], datatype, self._data[idx][5])

    def addValue(self, name = '', icol = -1, val = 0):
        if len(name):
            for icol, (n, _, _, _, t, _,) in enumerate(self._data):
                if n == name:
                    break

        t = self._data[icol][4]
        if t == 0: # if we have numbers
            val = float(val)
        self._data[icol] = (self._data[icol][0], self._data[icol][1], self._data[icol][2], self._data[icol][3], self._data[icol][4], self._data[icol][5]+[val])

    def setColumnData(self, name = '', icol = -1, valarr = []):
        if len(name):
            for icol, (n, _, _, _, _, _) in enumerate(self._data):
                if n == name:
                    break

        self._data[icol] = (self._data[icol][0], self._data[icol][1], self._data[icol][2], self._data[icol][3], self._data[icol][4], valarr) 

    def addTStress(self, name, ts):
        self._tstress[name] = ts
     
    def getTStress(self, name):
        if name in self._tstress:
            return self._tstress[name]
        else:
            return -1

    def setTStress(self, name, ts):
        self._tstress[name] = ts
    
    def addHashMark(self, hashline):
        self._unknownHash += [hashline]

    def addInfoLine(self, info):
        for i in range(len(self._unknownHash)):
            if self._unknownHash[i][0:3] == '#i ':
                del self._unknownHash[i]
                break

        self.addHashMark('#i ' + info)
        
    def getHashMark(self, hashid):
        for s in self._unknownHash:
            if s.find(hashid) != -1:
                return s.partition(' ')[2]
        return ''
    
    def getInfoLine(self):
        return self.getHashMark('#i')

    def extendInfoLine(self, text):
        old = self.getInfoLine()
        new = old + ' ' + text
        self.addInfoLine(new)

    def writeBlock(self, filestream, writeNrDatalines = -1, nrLinesFromColNr = -1, warningAtNAN = False, skipNANColumns = False, fileFormat = curvefile, printWarnings = False, writeHeader = True, enableStringCols = False):        
        if fileFormat != curvefile and fileFormat != binary32:
            myPyCommon.printErrorAndQuit('Invalid output file format')

        # check for cols just containing nans
        skipCols = []
        if skipNANColumns:
            for i, (n, _, _, _, dat) in enumerate(self._data):
                if len(dat):
                    if dat[0] != dat[0]: # column just contains nans
                        skipCols += [n]
            
        outstream = ''

        # binary block start id
        if not fileFormat&0xF0:
            outstream += pack('<I', blockID) # block id
            outstream += pack('<I', 0) # len of block, unknown yet
            outstream += pack('<I', 0) # len of header, unknown yet

        if writeHeader:
            # comments
            if not fileFormat&0xF0:
                outstream += pack('<I', len(self._comments)) # number of comments
            for s in self._comments:
                if not fileFormat&0xF0:
                    outstream += s + '\0'
                else:
                    outstream += '## ' + s + '\n'
            
            # p and b parameter
            self._b = fileFormat
            if not fileFormat&0xF0:
                self._b = fileFormat
                outstream += pack('<I', self._b) # b parameter
                outstream += pack('<I', self._p) # p parameter
            else:
                outstream += '#b %g\n' %self._b
                outstream += '#p %g\n' %self._p
            
            # unknown hashmarks
            if not fileFormat&0xF0:
                outstream += pack('<I', len(self._unknownHash)) # number of unknown hashmarks
            for s in self._unknownHash:
                #print s
                if not fileFormat&0xF0:
                    outstream += '%s\0' %s
                else:
                    outstream += '%s\n' %s

            # stress times
            isDefault = True
            if not fileFormat&0xF0:
                outstream += pack('<I', 0) # number of stresstimes, not known yet
            else:
                # check if ts differs from default value -1
                for name in self._tstress:
                    ts = self._tstress[name]
                    if ts != -1:
                        isDefault = False
                        break
                if not isDefault:
                    outstream += '#s'

            nrWritten = 0
            for (name, unit, offset, scale, _, _) in self._data:
                if name in skipCols:
                    continue
                ts = -1.0
                if name in self._tstress:
                    ts = self._tstress[name]
            
                if not fileFormat&0xF0 and fileFormat == binary32:
                    outstream += pack('<d', ts)
                else:
                    if not isDefault:
                        outstream += ' %e' %ts
                nrWritten += 1
            if not fileFormat&0xF0:
                idx = len(outstream)-8*nrWritten-4
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
            else:
                if not isDefault:
                    outstream += '\n'
            
            # offset
            isDefault = True
            if not fileFormat&0xF0:
                outstream += pack('<I', 0) # number of offset values, not known yet
            else:
                # check if ts differs from default value -1
                for (_, _, offset, _, _, _) in self._data:
                    if offset != 0:
                        isDefault = False
                        break
                if not isDefault:
                    outstream += '#o'

            nrWritten = 0
            for (name, unit, offset, scale, _, _) in self._data:
                if name in skipCols:
                    continue
                if not fileFormat&0xF0 and fileFormat == binary32:
                    outstream += pack('<d', offset)
                else:
                    if not isDefault:
                        outstream += ' %e' %offset
                nrWritten += 1
            if not fileFormat&0xF0:
                idx = len(outstream)-8*nrWritten-4
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
            else:
                if not isDefault:
                    outstream += '\n'
            
            # scale
            isDefault = True
            if not fileFormat&0xF0:
                outstream += pack('<I', 0) # number of scales, not known yet
            else:
                for (_, _, _, scale, _, _) in self._data:
                    if scale != 1:
                        isDefault = False
                        break
                if not isDefault:
                    outstream += '#f'

            nrWritten = 0
            for (name, unit, offset, scale, _, _) in self._data:
                if name in skipCols:
                    continue
                if not fileFormat&0xF0 and fileFormat == binary32:
                    outstream += pack('<d', scale)
                else:
                    if not isDefault:
                        outstream += ' %e' %scale
                nrWritten += 1
            if not fileFormat&0xF0:
                idx = len(outstream)-8*nrWritten-4
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
            else:
                if not isDefault:
                    outstream += '\n'
            
            # names
            if not fileFormat&0xF0:
                outstream += pack('<I', 0) # number of names, not known yet
            else:
                outstream += '#n'
            nrWritten = 0
            bytesWritten = 0
            for (n, _,  _, _, _, _) in self._data:
                if n in skipCols:
                    continue
                if not fileFormat&0xF0:
                    outstream += n + '\0'
                    bytesWritten += len(n) + 1
                else:
                    outstream += '  %s' %n
                nrWritten += 1
            if not fileFormat&0xF0:
                idx = len(outstream)-bytesWritten-4
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
            else:
                outstream += '\n'
            
            # units
            if not fileFormat&0xF0:
                outstream += pack('<I', 0) # number of names, not known yet
            else:
                outstream += '#u'
            nrWritten = 0
            bytesWritten = 0
            for (n, u,  _, _, _, _) in self._data:
                if n in skipCols:
                    continue
                if not fileFormat&0xF0:
                    outstream += u + '\0'
                    bytesWritten += len(u) + 1
                else:
                    outstream += '  %s' %u
                nrWritten += 1
            if not fileFormat&0xF0:
                idx = len(outstream)-bytesWritten-4
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
            else:
                outstream += '\n'
            
            if not fileFormat&0xF0: # write len of header in bytes
                idx = 8
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]

            # column data types
            if enableStringCols:
                if not fileFormat&0xF0:
                    outstream += pack('<I', 0) # number of names, not known yet
                else:
                    outstream += '#t'
                nrWritten = 0
                for (n, _,  _, _, t, _) in self._data:
                    if n in skipCols:
                        continue
                    if not fileFormat&0xF0 and fileFormat == binary32:
                        outstream += pack('<d', t)
                    else:
                        outstream += '  %s' %t
                    nrWritten += 1
                if not fileFormat&0xF0:
                    idx = len(outstream)-8*nrWritten-4
                    outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]
                else:
                    outstream += '\n'


            
            # !!!write len of header in bytes
            if not fileFormat&0xF0: # write len of header in bytes
                idx = 8
                outstream = outstream[0:idx] + pack('<I', nrWritten) + outstream[idx+4:]

        # data values
        nrLinesToWrite = 0
        if nrLinesFromColNr >= 0 and len(self._data) > nrLinesFromColNr:
            for i in range(len(self._data[nrLinesFromColNr][4])-1, -1, -1):
                if self._data[nrLinesFromColNr][4][i] == self._data[nrLinesFromColNr][4][i]: # check if not nan
                    nrLinesToWrite = i + 1
                    break
        elif writeNrDatalines > 0:
            nrLinesToWrite = writeNrDatalines
        else:
            for (_, _,  _, _, _, lst) in self._data:
                if nrLinesToWrite < len(lst):
                    nrLinesToWrite = len(lst)
     
        #if nrLinesToWrite: # hack because last item is not written so far
        #    nrLinesToWrite += 1
        #print "NrLinesToWrite = %d" %nrLinesToWrite

        posstream = len(outstream)
        if not fileFormat&0xF0: # write binary data values
            outstream += pack('<I', 0) # number of data values, not known yet (does not count to head)
        nrWritten = 0
        #print self._data
        for i in range(nrLinesToWrite):
            s = ''
            for (n, _,  _, _, t, lst) in self._data:
                if n in skipCols:
                    continue

                if i < len(lst):
                    if warningAtNAN and lst[i] != lst[i] and printWarnings:
                        myPyCommon.printWarning('NAN found in column %s at line %g' %(n, i))

                    if not fileFormat&0xF0: # write binary data values
                        if t == 0 or not enableStringCols: # we write numbers
                            try:
                                outstream += pack('<f', lst[i]) # data value
                                nrWritten += 1
                            except:
                                myPyCommon.printErrorAndQuit('String column? Use option enableStringCols = True')

                        elif t == 1: # we write strings
                            outstream += lst[i] + '\0' # data value
                            nrWritten += len(lst[i]) + 1
                        else:
                            myPyCommon.printErrorAndQuit('Invalid data type id')
                    else:
                        if t == 0: # we have numbers
                            s += '  %e' %lst[i]
                        elif t == 1: # we have strings
                            s += '  %s' %lst[i]
                        else:
                            myPyCommon.printErrorAndQuit('Invalid column type')
                else:
                    #print 'HELLO', i, len(lst)
                    if not fileFormat&0xF0: # write binary data values
                        outstream += pack('<f', float('nan')) # data value
                        nrWritten += 1
                    else:
                        s += '  nan'
            if fileFormat&0xF0: # write to not binary files
                outstream += s + '\n'

        if not fileFormat&0xF0: # write number of data values and len of block in bytes
            outstream = outstream[0:posstream] + pack('<I', nrWritten) + outstream[posstream+4:]
                              
            idx = 4
            outstream = outstream[0:idx] + pack('<I', len(outstream)) + outstream[idx+4:]

        filestream.write(outstream)

        return len(outstream)

    def stringFromBinaryStream(self, stream):
        s = ''
        while stream[0] != '\0':
            s += stream[0]
            stream = stream[1:]
        stream = stream[1:]

        return (stream, s)

    def readBlockBinary(self, filestream, fileFormat = binary32, binaryVersion = 2):
        # binary block start id
        if not fileFormat&0xF0:
            if unpack('<I', filestream.read(4))[0] != blockID:
                myPyCommon.printError('Unknown blockID of binary curve file')
                return False
            lenBlock       = unpack('<I', filestream.read(4))[0]
            lenBlockHeader = unpack('<I', filestream.read(4))[0]
            instream = filestream.read(lenBlock-12)

        # comments
        if not fileFormat&0xF0:
            numComments = unpack('<I', instream[0:4])[0] # number of comments
            instream = instream[4:]
            for i in range(numComments):
                (instream, s) = self.stringFromBinaryStream(instream)
                self.addComment(s)

        # p and b parameter
        if not fileFormat&0xF0:
            self._b = unpack('<I', instream[0:4])[0] # b parameter
            fileFormat = self._b
            instream = instream[4:]
            self._p = unpack('<I', instream[0:4])[0] # p parameter
            instream = instream[4:]
      
        # unknown hashmarks
        if not fileFormat&0xF0:
            numHashMarks = unpack('<I', instream[0:4])[0] # number of hashes
            instream = instream[4:]
            for i in range(numHashMarks):
                (instream, s) = self.stringFromBinaryStream(instream)
                self._unknownHash += [s]
          
        # stress times
        if not fileFormat&0xF0:
            numTStress = unpack('<I', instream[0:4])[0] # number of stress times
            instream = instream[4:]
            tstressList = []
            for i in range(numTStress):
                tstressList += [unpack('<d', instream[0:8])[0]]
                instream = instream[8:]

        # offset
        if not fileFormat&0xF0:
            numOffset = unpack('<I', instream[0:4])[0] # number of stress times
            instream = instream[4:]
            offsetList = []
            for i in range(numOffset):
                offsetList += [unpack('<d', instream[0:8])[0]]
                instream = instream[8:]

        # scale
        if not fileFormat&0xF0:
            numScales = unpack('<I', instream[0:4])[0] # number of stress times
            instream = instream[4:]
            scalesList = []
            for i in range(numScales):
                scalesList += [unpack('<d', instream[0:8])[0]]
                instream = instream[8:]

        # names
        if not fileFormat&0xF0:
            numNames = unpack('<I', instream[0:4])[0] # number of hashes
            instream = instream[4:]
            namesList = []
            for i in range(numNames):
                (instream, s) = self.stringFromBinaryStream(instream)
                namesList += [s]

        # units
        if not fileFormat&0xF0:
            numUnits = unpack('<I', instream[0:4])[0] # number of hashes
            instream = instream[4:]
            unitsList = []
            for i in range(numUnits):
                (instream, s) = self.stringFromBinaryStream(instream)
                unitsList += [s]
    
        hasStringCols = False
        typesList = []
        if binaryVersion == 3: # column data type
            numtypes = unpack('<I', instream[0:4])[0] # number of column date types
            instream = instream[4:]
            for i in range(numtypes):
                typesList += [unpack('<d', instream[0:8])[0]]
                instream = instream[8:]
            for i in typesList:
                if i:
                   hasStringCols = True
                   break
        else:
            typesList += [0.0 for i in range(len(namesList))] # default we have numbers

        # number of data values
        if not fileFormat&0xF0: # write number of data values and len of block in bytes
            numValues = unpack('<I', instream[0:4])[0]
            instream = instream[4:]
            # create data list
            for k, (n, u, o, s, t) in enumerate(zip(namesList, unitsList, offsetList, scalesList, typesList)):
                self.addColumn(name = n, unit = u, offset = o, scale = s, datatype = t)
                if len(tstressList):
                    self.addTStress(name = n, ts = tstressList[k])

            if fileFormat == binary32:
                if not hasStringCols:
                    valuelst = unpack('<%df' %(numValues), instream)

                    for col in range(len(namesList)):
                        lst = list() # create new list, importand here not to overwrite the previously created one
                        for i in range(col, len(valuelst), len(namesList)):
                            lst += [valuelst[i]]

                        self.setColumnData(icol = col, valarr = lst)
                else:
                    col = 0
                    while len(instream):
                        if typesList[col] == 1: # we have strings
                            s = str()
                            while instream[0] != '\0':
                                s += instream[0]
                                instream = instream[1:]
                            instream = instream[1:] # remove closing NULL
                            self.addValue(icol = col, val = s) 
                        else:
                            self.addValue(icol = col, val = float(unpack('<f', instream[0:4])[0]))

                        col += 1
                        if col >= len(namesList):
                            col = 0
            return True

    def copyBlockHead(self, prev):
        for i in range(len(prev)):
            (n, u, o, s, t, _) = prev.getColumn(idx = i)
            self.addColumn(name = n, unit = u, offset = o, scale = s, vals = [])

    def readBlockCurve(self, filestream, fileFormat = curvefile, previousBlock = None):
        # previous block needed because their are some versions with multiple blocks not containing separate heads
        blockHasData = False
        blockHasHead = False
        for line in filestream:
            if line[0:2].find('##') != -1: # comment
                blockHasData = True
                self._comments += [line.replace('\n', '').partition(' ')[2]]
            elif line[0] == '#': # hashMark
                blockHasData = True
                blockHasHead = True
                els = line.replace('\n', '').replace('\t', ' ').partition(' ')[2].rsplit()
                if line[0:10].find('#n') != -1: # names
                    for i,n in enumerate(els):
                        self.setColumnName(idx = i, name = n)
                elif line[0:10].find('#u') != -1: # units
                    for i,u in enumerate(els):
                        self.setColumnUnit(idx = i, unit = u) 
                elif line[0:10].find('#o') != -1: # offset
                    for i,o in enumerate(els):
                        self.setColumnOffset(idx = i, offset = float(o)) 
                elif line[0:10].find('#f') != -1: # scale
                    for i,s in enumerate(els):
                        self.setColumnScale(idx = i, scale = float(s))
                #elif line[0:10].find('#s') != -1: # stress times
                #    for i, s in enumerate(els):
                #        self.setTStress(idx = i, ts = float(s))
                elif line[0:10].find('#t') != -1: # type, 0 .. float, 1 .. string
                    for i,s in enumerate(els):
                        self.setColumnDataType(idx = i, datatype = int(float(s)))
                elif line[0:10].find('#b') != -1: # b parameter
                    self._b = int(els[0])
                elif line[0:10].find('#p') != -1: # p parameter
                    self._p = int(els[0])
                    if self._p > 10:
                        myPyCommon.printWarning('Strange p - parameter: ', els[0])
                        self._p = 1
                else: # unknown hashMark
                    self.addHashMark(hashline = line.replace('\n', ''))
            elif line[0] != '\n': # data values
                if not blockHasHead: # copy head from previous block
                    myPyCommon.printWarning('Very old crv version without individual block heads -- copy previous head')
                    if previousBlock == None:
                        myPyCommon.printErrorAndQuit('No head found')
                    self.copyBlockHead(previousBlock)
                    blockHasHead = True

                blockHasData = True
                line = ' ' + line # if the first character of the line is no white space insert one
                els = line.replace('\n', '').replace('\t', ' ').partition(' ')[2].rsplit()
                for i,value in enumerate(els):
                    self.addValue(icol = i, val = value)
            else: # end of block reached
                break

        return blockHasData

class CRV:
    _blocks   = [] # single data blocks
    _comments = [] # common header

    def __init__(self, filename = None):
        self._blocks   = []
        self._comments = []
        self.__initialBinaryFile = False

        if filename:
            ext  = ''
            readBinary = False
            if filename.find('.brv') != -1: 
                ext = ''
                readBinary = True
            elif filename.find('.crv') != -1: 
                ext = ''
                readBinary = False
            elif os.path.exists(filename + '.brv'):
                ext = '.brv'
                readBinary = True
            elif os.path.exists(filename + '.crv'):
                ext = '.crv'
                readBinary = False
            else:
                common.printErrorAndQuit('File %s%s not found' %(filename, ext))

            if readBinary:
                self.readBinaryCRVFile(filename, ext)
                self.__initialBinaryFile = True
            else:
                self.readCRVFile(filename, ext)
                self.__initialBinaryFile = False

            self.__initialfilename = filename
            self.__initialext = ext

    def addBlock(self, block):
        self._blocks += [block]

    def getBlockCount(self):
        return len(self._blocks)

    def __len__(self):
        return self.getBlockCount()

    def getBlock(self, idx = -1):
        if idx >= 0 and idx < len(self._blocks):
            return self._blocks[idx]
        else:
            myPyCommon.printErrorAndQuit('Block index out of range')

    def __getitem__(self, idx):
        if idx >= 0 and idx < len(self._blocks):
            return self._blocks[idx]
        else:
            myPyCommon.printErrorAndQuit('Block index out of range')

    def addComment(self, s):
        self._comments += [s]

    def getComments(self):
        return self._comments

    def getInfo(self):
        info = self._blocks[0].getHashMark('#i')
        #print '#i: ', info
        if not info:
            if not len(self.getComments()):
                return ''
            info = self.getComments()[0]
        return info

    def writeCRVFile(self,filename, 
                     append = False,
                     overwrite = 1, writeNrDatalines = -1, nrLinesFromColNr = -1, warningAtNAN = False, skipNANColumns = False, writeHeader = True, withextension = True, enableStringCols = True):

        if not withextension: # used in xcrv
            pass
        else:
            if filename.find(ext_crv) == -1:
                filename += ext_crv

        if not (overwrite or append) and os.path.isfile(filename):
            myPyCommon.printErrorAndQuit('File %s does exist and overwrite/append option is not enabled' % filename)

        if append:
            file = open(filename, 'a')
            file.write('\n')
        else:
            file = open(filename, 'w')

        # write common header
        for s in self._comments:
            file.write('## ' + s + '\n')

        # write single blocks
        for i, block in enumerate(self._blocks):
            block.writeBlock(file, writeNrDatalines = writeNrDatalines, nrLinesFromColNr = nrLinesFromColNr, warningAtNAN = warningAtNAN, skipNANColumns = skipNANColumns, fileFormat = curvefile, writeHeader = writeHeader or i==0, enableStringCols = enableStringCols)
        
            if i < (len(self._blocks)-1): # seperate two blocks
                file.write('\n')

        # finished 
        file.close()

    def readCRVFile(self, filename, ext = '.crv'):
        filename += ext

        if not os.path.isfile(filename):
            myPyCommon.printErrorAndQuit('CRV-File %s does not exist' %filename)

        file = open(filename, 'r')

        # read comments
        while 1 and file:
            line = file.readline() 
            if line.find('##') != -1:
                self._comments += [line.replace('\n', '').partition(' ')[2]]
            else:
                file.seek(-len(line), 1) # go back the last read line from here
                break

        # read blocks, number of blocks 1e5 should be enough
        prevBlock = None
        for i in range(int(1e5)):
            block = CRVBlock()
            if block.readBlockCurve(file, fileFormat = curvefile, previousBlock = prevBlock):
                prevBlock = block
                self._blocks += [block]

        file.close()

    def writeBinaryCRVFile(self, filename, 
                           overwrite = 1, writeNrDatalines = -1, nrLinesFromColNr = -1, fileFormat = binary32, warningAtNAN = False, skipNANColumns = False, enableStringCols = False):
        if filename.find(ext_brv) == -1:
            filename += ext_brv
        
        if not overwrite and os.path.isfile(filename):
            myPyCommon.printErrorAndQuit('File %s does exist and overwrite option is not enabled' %filename)

        file = open(filename, 'w')

        outstream = ''

        if not enableStringCols:
            outstream += pack('<I', binaryID)
        else:
            outstream += pack('<I', binaryIDx3)
        outstream += pack('<I', 0) # len head not known yet
        outstream += pack('<I', len(self._blocks)) # number of blocks
        for i in range(len(self._blocks)):
            outstream += pack('<I', 0) # startposition of the blocks, not known yet
 
        # comments
        outstream += pack('<I', len(self._comments)) # number of comments
        for s in self._comments:
            outstream += s + '\0'

        blocksize = len(outstream) # length of header here
        outstream = outstream[0:4] + pack('<I', blocksize) + outstream[8:]
        
        # write header to file
        file.write(outstream)

        # write single blocks
        for i, block in enumerate(self._blocks):
            outstream = outstream[0:12+i*4] + pack('<I', blocksize) + outstream[12+(i+1)*4:] # start position of this block
            blocksize += block.writeBlock(file, writeNrDatalines = writeNrDatalines, nrLinesFromColNr = nrLinesFromColNr, warningAtNAN = warningAtNAN, skipNANColumns = skipNANColumns, fileFormat = fileFormat, enableStringCols = enableStringCols)

        file.seek(0)
        file.write(outstream) # write head

        # finished 
        file.close()

    def readBinaryCRVFile(self, filename, ext = '.brv', justEvalBlockCount = False):
        if filename.find(ext) == -1:
            filename += ext
       
        if not os.path.isfile(filename):
            myPyCommon.printErrorAndQuit('Binary CRV-File %s does not exist' %filename)

        #print filename
        file = open(filename, 'r')
       
        # check file version
        binaryVersion = 0

        binaryVersion = unpack('<I', file.read(4))[0]
        if binaryVersion == binaryID:
            binaryVersion = 2
        elif binaryVersion == binaryIDx3:
            binaryVersion = 3
        else:
            myPyCommon.printErrorAndQuit('Unknown binary file version')

        lenhead = unpack('<I', file.read(4))[0]

        # read complete file header
        file.seek(0)
        instream = file.read(lenhead)[8:] # skip first two parameters, already analyzed

        # Block information
        numBlocks = unpack('<I', instream[0:4])[0]
        if justEvalBlockCount:
            file.close()
            return numBlocks
            
        instream = instream[4:]
        posBlocks = []
        for i in range(numBlocks):
            posBlocks += [unpack('<I', instream[0:4])[0]]
            instream = instream[4:]

        # Common comments
        numComments = unpack('<I', instream[0:4])[0]
        instream = instream[4:]
        for i in range(numComments):
            s = ''
            while instream[0] != '\0':
                s += instream[0]
                instream = instream[1:]
            instream = instream[1:]
            self.addComment(s)

        # read single blocks
        for i in range(numBlocks):
            block = CRVBlock()
            file.seek(posBlocks[i])
            if not block.readBlockBinary(file, fileFormat = binary32, binaryVersion = binaryVersion):
                print 'Successfully read %d blocks before an invalid block occured' %i
                break
            self._blocks += [block]
#            block.readBlock(file.seek(posBlocks[i]))
#            self.addBlock(block)

        # finished 
        file.close() 

    def isBinaryFile(self, f):
        if not os.path.isfile(f):
            return 0

        file = open(f, 'r')

        binaryVersion = unpack('<I', file.read(4))[0]
        file.close()

        if binaryVersion == binaryID or binaryVersion == binaryIDx3:
            pass
        else:
            return 0

        return 1

    def readfile(self, f):
        ext_crv = '.crv'
        ext_brv = '.brv'

        if f.find(ext_crv) != -1:
            ext_crv = ''
        if f.find(ext_brv) != -1:
            ext_brv = ''

        if os.path.exists(f + ext_brv):
            if self.isBinaryFile(f + ext_brv):
                self.readBinaryCRVFile(f)
        elif os.path.exists(f + ext_crv):
            self.readCRVFile(f)

    def writefile(self, filename = None):
        if filename == None:
            if self.__initialBinaryFile == True:
                self.writeBinaryCRVFile(filename = self.__initialfilename)
            else:
                self.writeCRVFile(filename = self.__initialfilename)
        else:
            if filename[-4:] == '.crv':
                self.writeCRVFile(filename = filename)
            else:
                self.writeBinaryCRVFile(filename = filename)
