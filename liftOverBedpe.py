from __future__ import print_function
import argparse
import os

try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict
########################################################################################
#                                                                                      #
#                                            Functions                                 #
#                                                                                      #
########################################################################################

""" Define a function that splits up bedpe files into 2 temp files """
def splitBedpe(bedpe, tmp1="tmp1.bed", tmp2="tmp2.bed", tmp_annot="tmp_annot.txt",
               header="F", verbose="F"):

    t1 = open(tmp1, 'w')
    t2 = open(tmp2, 'w')
    bedpein = open(bedpe, 'r')
    annotations = open(tmp_annot, 'w')

    if header == "T":
        headerline = bedpein.readline()

    for n, l in enumerate(bedpein):
        n = str(n)
        e = l.strip().split("\t")
        print("\t".join(e[0:3] + [n]), file=t1)
        print("\t".join(e[3:6] + [n]), file=t2)
        print("\t".join(e[6:] + [n]), file=annotations)

    t1.close()
    t2.close()
    bedpein.close()
    annotations.close()


""" Define a function that implements liftOver """
def doliftOver(liftOver,chain,infile,verbose="F"):

    cmd = " ".join([liftOver,infile,chain,infile + ".success",infile + ".failure"])
    if verbose == "T":
        print(cmd)
    os.system(cmd)


""" Define a function that merges liftOver """
def mergeliftOver(f1, f2, annotations, outputfile, verbose="F"):

    o = open(outputfile,'w')


    # read in file 1 and make dictionary
    readdict = OrderedDict()
    f = open(f1, 'r')
    for l in f:
        e = l.strip().split('\t')
        readdict[e[3]] = e[:3]
    f.close()

    # read in file2 and print out matches
    f = open(f2,'r')
    for l in f:
        e = l.strip().split('\t')
        if e[3] in readdict:
            readdict[e[3]] += e[:3]

    f = open(annotations,'r')
    for l in f:
        e = l.strip().split('\t')
        if e[-1] in readdict:
            readdict[e[-1]] += e[:-1]

    for i, val in readdict.items():
        print("\t".join(val), file=o)
    f.close()
    o.close()


########################################################################################
#                                                                                      #
#                                        Parse arguments                               #
#                                                                                      #
########################################################################################


parser = argparse.ArgumentParser(description='wrapper for liftOver to accomodate bedpe files')

# required arguments
parser.add_argument('--lift',        dest='liftOver',     help='path to liftOver')
parser.add_argument('--chain',          dest='chain',         help='(e.g. hg19ToHg18.over.chain)')
parser.add_argument('--i',              dest='infile',         help='input file in bedpe format')
parser.add_argument('--o',              dest='outfile',         help='output file')
parser.add_argument('--v',              dest='verbose',         help='verbose' , default = "F")
parser.add_argument('--h',              dest='header',         help='T /  F if there is a header line', default = "F")

# parse arguments
args = parser.parse_args()

# read in args
LO       = args.liftOver
chain    = args.chain
bedpeIN  = args.infile
bedpeOUT = args.outfile
tmp1     = "tmp1.bed"
tmp2     = "tmp2.bed"
tmp_annot= "tmp_annot.txt"
header     = args.header
verbose     = args.verbose

#####################################################################################################
#                                                                                                    #
#                                        Run the Code                                                  #
#                                                                                                    #
#####################################################################################################

# break up the files
splitBedpe(bedpeIN, tmp1, tmp2, tmp_annot, header, verbose)

# perform liftOver
doliftOver(LO, chain, tmp1, verbose)
doliftOver(LO, chain, tmp2, verbose)

# merge liftOvered files
mergeliftOver(tmp1+".success", tmp2+".success", tmp_annot, bedpeOUT, verbose)

# remove tmp files
os.remove(tmp1)
os.remove(tmp2)
os.remove(tmp_annot)
os.remove(tmp1+".success")
os.remove(tmp1+".failure")
os.remove(tmp2+".success")
os.remove(tmp2+".failure")
