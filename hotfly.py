#!/usr/bin/env python

import os
import sys
import argparse
from datetime import datetime
import Sybase
from fitscard import fitscard

VERSION = '2.0'

BLOCKSIZE = 2880
CARDSIZE = 80
SIMPLE   = 'SIMPLE  ='
PCOUNT   = 'PCOUNT  ='
GCOUNT   = 'GCOUNT  ='
XTENSION = 'XTENSION='
ARCFILE  = 'ARCFILE ='
END = 'END'.ljust(80)

KEYWORDS_FROM_FILE = [
    "SIMPLE","XTENSION","BITPIX","NAXIS","NAXIS1","NAXIS2","NAXIS3","NAXIS4", 
    "NAXIS5","NAXIS6","NAXIS7","NAXIS8","NAXIS9","EXTEND","PCOUNT","GCOUNT",
    "TFIELDS","TTYPE1","TFORM1","ZIMAGE","ZCMPTYPE","ZBITPIX","ZNAXIS","ZNAXIS1","ZNAXIS2",
    "ZNAXIS3","ZNAXIS4","ZNAXIS5","ZNAXIS6","ZNAXIS7","ZNAXIS8","ZNAXIS9",
    "ZTILE1","ZTILE2","ZTILE3","ZTILE4","ZTILE5","ZTILE6","ZTILE7","ZTILE8","ZTILE9",
    "ZVAL1","ZVAL2","ZVAL3","ZVAL4","ZVAL5","ZVAL6","ZVAL7","ZVAL8","ZVAL9",
    "ZNAME1","ZNAME2","ZNAME3","ZNAME4","ZNAME5","ZNAME6","ZNAME7","ZNAME8","ZNAME9",
    "ZMASKCMP","ZSIMPLE","ZTENSION","ZEXTEND","ZBLOCKED","ZPCOUNT","ZGCOUNT","DATASUM","ZDATASUM"]

NOT_KEYWORDS_FROM_DB = KEYWORDS_FROM_FILE + ["HDRVER","CHECKSUM","ZHECKSUM","END"," "]

def log(msg):
    if debug:
        print >> sys.stderr, msg

def error(msg):
    print >> sys.stderr, msg

def dbrcGet(alias):
    dbrcLines = open(os.getenv('HOME') + '/.dbrc').readlines()
    for line in dbrcLines:
        items = line.split()
        if len(items) == 5 and items[0][0] != '#' and items[4] == alias:
            return (items[0], items[2], items[3])
    raise Exception(alias + ' not found in $HOME/.dbrc')

def connect():
    global dbcon
    server, user, password = dbrcGet('HEADONFLY')
    log('connecting to %s as user %s' % (server, user))
    dbcon = Sybase.connect(server, user, password)

def disconnect():
    if dbcon:
        dbcon.close()

def getHdrver(fileId):
    global hdrver
    
    cur = dbcon.cursor()
    query = """select convert(char(10), last_mod_date, 'yyyy-mm-dd')
    from dbcm.dp_tracking where dp_id = '%s'""" % fileId
    cur.execute(query, select=False)
    res = cur.fetchall()
    cur.close()
    if res:
        hdrver = res[0][0]
    else:
        raise Exception('%s not found in repository' % fileId)
    
def makeHdrverCard():
    fitsCard = fitscard(keyword='HDRVER', value=hdrver, type='T', comment='ESO Archive header timetag')
    return fitsCard.format()

def makeProcessedByHotflyCard():
    comment = 'processed by hotfly version %s on %s UT' % (VERSION, datetime.utcnow().isoformat()[:23])
    fitsCard = fitscard(keyword='COMMENT', value=comment)
    return fitsCard.format()

def getHeaderFromDB(fileId):
    cur = dbcon.cursor()
    query = """select kw_name, kw_value, kw_type, kw_comment
    from dbcm.keywords_repository
    where dp_id = '%s' order by ext_id, kw_ind""" % fileId
    cur.execute(query, select=False)
    res = cur.fetchall()
    cur.close()
    currentHeader = []
    headers = []
    for kwName, kwValue, kwType, kwComment in res:
        if kwName == 'END':
            currentHeader.append(END)
            headers.append(currentHeader)
            currentHeader = []
        elif kwName == 'ESO-LOG':
            kwName = 'HISTORY ' + kwName
        elif kwName not in NOT_KEYWORDS_FROM_DB:
            fitsCard = fitscard(keyword=kwName, value=kwValue, type=kwType, comment=kwComment)
            currentHeader.append(fitsCard.format())
        else:
            pass
    return headers

def readBlock(inputFile):
    data = inputFile.read(BLOCKSIZE)
    size = len(data)
    if size > 0 and size != BLOCKSIZE:
        raise Exception('read %d bytes, expected %d' % (size, BLOCKSIZE))
    return data

def copyData(inputFile, outputFile):
    while True:
        data = readBlock(inputFile)
        if not data or data[:len(XTENSION)] == XTENSION:
            return data
        else:
            outputFile.write(data)

def readHeader(inputFile, block):
    header = []
    while block:
        for i in range(0, BLOCKSIZE, CARDSIZE):
            card = block[i:i+CARDSIZE]
            header.append(card)
            if card == END:
                return header
        block = readBlock(inputFile)
    raise Exception('END not found')

def skipFirstHdu(header):
    for card in header:
        if card[:len(ARCFILE)] == ARCFILE:
            return False
    return True

def writeHeader(outputFile, header, dbHeader, hduNum):
    numCards = 0
    if hduNum == 0 and skipFirstHdu(header):
        log('skipping first hdu')
        hduNum = -1
        for card in header:
            kwd = card[:8].strip()
            if kwd != 'CHECKSUM':
                outputFile.write(card)
                numCards += 1
    else:
        for card in header:
            kwd = card[:8].strip()
            # PCOUNT and GCOUNT must not be in primary HDU
            pgCountInPrimaryHdu = (kwd in ['PCOUNT','GCOUNT'] and hduNum == 0)
            if kwd in KEYWORDS_FROM_FILE and not pgCountInPrimaryHdu:
                fitsCard = fitscard(image = card)
                outputFile.write(fitsCard.format())
                numCards += 1
            if card == END:
                for dbCard in dbHeader:
                    if hduNum == 0 and dbCard == END:
                        outputFile.write(makeHdrverCard())
                        outputFile.write(makeProcessedByHotflyCard())
                        numCards += 2
                    outputFile.write(dbCard)
                    numCards += 1
    numSpaces = BLOCKSIZE - ((numCards * CARDSIZE) % BLOCKSIZE)
    outputFile.write(' ' * numSpaces)
    return (hduNum + 1)

def run(inputFile, outputFile, fileId):
    hduNum = 0
    
    block = readBlock(inputFile)
    if not block:
        raise Exception('empty file')
    if block[:len(SIMPLE)] != SIMPLE:
        raise Exception('not a fits file')
    
    dbHeaders = getHeaderFromDB(fileId)
    
    while True:
        log('hdu %d/%d' % (hduNum, len(dbHeaders)))
        header = readHeader(inputFile, block)
        hduNum = writeHeader(outputFile, header, dbHeaders[hduNum], hduNum)
        block = copyData(inputFile, outputFile)
        if not block:
            log('end of file')
            break

def main():
    global debug
    
    parser = argparse.ArgumentParser()
    parser.add_argument("file_id")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--inputfile")
    parser.add_argument("-o", "--outputfile")
    args = parser.parse_args()
    debug = args.debug
    
    try:
        if args.outputfile and os.path.exists(args.outputfile):
            error('file exists: %s' % args.outputfile)
            sys.exit(1)
        infile = open(args.inputfile, 'rb') if args.inputfile else sys.stdin
        outfile = open(args.outputfile, 'wb') if args.outputfile else sys.stdout
        connect()
        getHdrver(args.file_id)
        run(infile, outfile, args.file_id)
        disconnect()
    except Exception as e:
        error(str(e))
        if args.outputfile:
            try: os.remove(args.outputfile)
            except: pass
        sys.exit(1)

if __name__ == '__main__':
    main()
