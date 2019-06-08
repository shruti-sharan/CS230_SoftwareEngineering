# -*- coding: utf-8 -*-
"""Scraper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wspLwlU9PRuuSiFBLR1fm_754k0pJHRP
"""

from bs4 import BeautifulSoup
import urllib.request
import re
import pandas as pd
import numpy as np
import ssl
from tkinter.filedialog import askopenfilename

ssl._create_default_https_context = ssl._create_unverified_context
PATH_TO_FILE = askopenfilename()

# from google.colab import files
# uploaded = files.upload()


# Methods to extract lines
def ext_current_line(soup, line_number):
    current_line = soup.find(id="newcode" + str(line_number)) 
    return current_line.text if current_line else ""


# upper context
def ext_upper(soup, line_number, number_of_lines):
    context = ""
    for line in np.arange(line_number-number_of_lines, line_number):
        extracted_line = soup.find(id="newcode" + str(line))
        if(extracted_line is None):
            extracted_line = soup.find(id="oldcode" + str(line))
        context += extracted_line.text if extracted_line and 'udiffremove' not in extracted_line['class'][1] else ""
    return context


# lower context
def ext_lower(soup, line_number, number_of_lines):
    context = ""
    for line in np.arange(line_number + 1, line_number + number_of_lines + 1):
        extracted_line = soup.find(id="newcode" + str(line))
        if(extracted_line is None):
            extracted_line = soup.find(id="oldcode" + str(line))
        context += extracted_line.text if extracted_line and 'udiffremove' not in extracted_line['class'][1] else ""
    print(context)
    return context


def ext_context(soup, line_number, number_of_lines):
    regex_id = re.compile("...code*")
    # regex_class = re.compile("udiff udiffadd|udiff ")
    list_of_tags = soup.findAll("td", attrs={"id": regex_id})
    index = [idx for idx, s in enumerate(list_of_tags) if s['id']=="newcode" + str(line_number)][0]
    list_of_lines = [line_tag.text.strip('\n') for line_tag in list_of_tags]
    for line in list_of_lines:
        print(line)
    upper = list_of_lines[:index]
    lower = list_of_lines[index+1:]
    return (upper, lower)

def ext_diff_full(soup):
    regex_id = re.compile("...code*")
    # regex_class = re.compile("udiff udiffadd|udiff ")
    list_of_tags = soup.findAll("td", attrs={"id": regex_id})
    list_of_lines = [line_tag.text.strip('\n') for line_tag in list_of_tags]
    return list_of_lines


def clean_context_line(line):
    if len(line.strip()) == 0:
        return line
    if (line.strip()[0] == '+'):
        return line.replace('+', " ", 1)
    if (line.strip()[0] == '-'):
        return None
    return line

# we are extracting 10 lines just for now
data = pd.read_csv(PATH_TO_FILE)
current_lines = []
upper = []
lower = []


#filter only columns we want
filtered_data = data.filter(['review_id','patchset_id','patch_id'], axis=1)
for index, row in filtered_data.iterrows():

    url = 'https://codereview.chromium.org/' + str(row['review_id']) + '/patch/' + str(row['patchset_id']) + '/' + str(row['patch_id'])
    print(url)

    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    current_line = ext_current_line(soup, row['line_number'])
    #current_lines.append(ext_current_line(soup, row['line_number']))
    #upper.append(ext_upper(soup, row['line_number'],5)) #extract upper context
    #lower.append(ext_lower(soup, row['line_number'],5))
    #print("An error occured.")
    
    try:
        saved_file_name = str(row['review_id']) + '' + str(row['patchset_id']) + '' + str(row['patch_id']) + str(row['line_number']) + '.txt'
        f = open(saved_file_name, mode='w', encoding='utf-8')
        
        clean_line = clean_context_line(current_line)
        if (clean_line is not None):
            f.write(clean_line + '\n')
    finally:
        f.close()