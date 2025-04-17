#!/usr/bin/python
"""
Title: get the valid 23andMe file
Date:2025-04-10
Author: Tongrui Zhang

Description:
    This script will check the input file is valid 23andMe file and make the 23andMe file has uniform format:
    1.header: "#    rsid    chromosome  position    genotype"
    2.tab as a delimiter
    3.4 columns containing details for rsid, chromosome, position and genotype
    4."--" refering to no genotype information
    
List of functions:
    1.valid_chromosome(): check the chromosome detail is only 'X', 'Y', 'XY', 'MT' or number between 0-26
    2.valid_position(): check the position detail is integer
    3.valid_genotype(): check the characters in genotype details only include 'A','C','T','G','D','I','-', or '0'
            
Procedure:
    1. Check the input arguments are valid and pass them as input file path and output file path.
    2. Detect the input file's delimiter and header is valid
    3. Check the content and format of the input file is valid and convert the different types of input files into files with uniform format 

Usage:
    python valid_23am.py input_file output_file
"""
############################################################################################################################################

import sys
from pathlib import Path
import re
import csv

#check the chromosome detail is only 'X', 'Y', 'XY', 'MT' or integer number between 0-26
def valid_chromosome(chrom):
    try:
        if chrom.upper() in ['X', 'Y', 'XY','MT'] or 0 <= int(chrom) <= 26:
                return True
        else:
            print("chromosome should be either X, Y, XY, MT or 0-26")
            return False
    except ValueError:
        return False

#check the position detail is integer
def valid_position(pos):
    try:
        int(pos)
        return True
    except ValueError:
        print("position should be an integer")
        return False

#check the characters in genotype details only include 'A','C','T','G','D','I','-', or '0'
def valid_genotype(geno):
    geno_accepted = set('ACTGDI-0')
    if all([i in geno_accepted for i in geno]):
        return True
    else:
        print("genotype should be one of A, C, T, G, D, I, -, 0")
        return False

if __name__ == "__main__":
    #check the input arguments have correct number and the input file exists and it's a file
    if len(sys.argv) != 3:
        print("wrong parameter number. Usage: python valid_23am.py input_file output_file")
        sys.exit(1)
    if not Path(sys.argv[1]).exists() or not Path(sys.argv[1]).is_file():
        print(f"check INPUT FILE exists and it's a file")
        raise FileNotFoundError

    input_file = sys.argv[1] #input_file
    output_file = sys.argv[2] #output_file

    try:
        with open(input_file, 'r') as inputf, open(output_file, 'w') as outf:
            first_line = inputf.readline().strip() #extract the first line to detect the delimiter of the input file
            if "\t" in first_line:
                dialect = 'excel-tab'
            elif "," in first_line:
                dialect = 'excel'
            else:
                print("file requires tab or comma delimiter")
                raise ValueError           
            
            if "chromosome" in first_line.lower() or "position" in first_line.lower(): #if the first line is header, pass
                pass
            elif not re.search(r'[^#a-zA-Z0-9\s,-]', first_line): #if the first line is not header, check if it is valid information line
                inputf.seek(0)
            else: #if the first line is not header and not valid information line, raise error
                print("file first line should be either valid header or valid information line")
                raise ValueError
                
            reader = csv.reader(inputf, dialect=dialect) #read the input file with the detected delimiter
            writer = csv.writer(outf, delimiter='\t') #write the output file with tab delimiter
            writer.writerow(["# rsid", "chromosome", "position", "genotype"]) #write the header to the output file
            #use for loop to read the input file line by line
            #check the content and format of the input file is valid: correct number of columns, valid chromosome, position and genotype
            #convert the different types of input files into files with uniform format: the genotype is 2 characters in 1 column, and the genotype is "--" if no genotype information
            for line in reader:
                if not line:
                    continue
                if len(line) != 4 and len(line) !=5:
                    print("expect 4 or 5 columns")
                    raise ValueError
                elif len(line) == 5:
                    rsid, chrom, pos, a1,a2 = line
                    geno = a1+a2
                else:
                    rsid, chrom, pos, geno = line

                if not valid_chromosome(chrom) or not valid_position(pos) or not valid_genotype(geno):
                    print(f"line {line} is invalid")
                    raise ValueError(f"Invalid data found: {line}")
                if geno == "00":
                    geno = "--"
                writer.writerow([rsid, chrom, pos, geno])

    except FileNotFoundError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)
