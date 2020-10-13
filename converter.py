# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 12:42:25 2020

@author:
"""

import os 
from glob import glob
from bs4 import BeautifulSoup
import re
import time
import calendar
from datetime import datetime
from tkinter import filedialog
from tkinter import *
import shutil 
import html2markdown


start_time = time.time()
TAG_REMOVAL_REGEX = re.compile(r'<[^>]+>')
body_regex =re.compile(r'</?body[^>]*>')
div_regex =re.compile(r'</?div[^>]*>')
span_regex =re.compile(r'</?span[^>]*>')
img_regex =re.compile(r'<img></img>*?>')
atag_regex =re.compile(r'<a></a>*?>')
atag2_regex = re.compile(r'<a\sname=\"*\d*\">[^>]/a>')
loading = "..............................."


def generated_time():
    geneerated_time = time.strftime("%Y_%m_%d_%H_%M_%S")
    return geneerated_time



def ask_file_directory():
    root = Tk()
    root.withdraw()
    dataSet_file_directory = filedialog.askdirectory()
    return dataSet_file_directory
  


def read_html_file(file):
    HtmlFile = open(file, 'r', encoding='utf-8')
    html_source_code = HtmlFile.read() 
    return html_source_code



    
def remove_html_tags(html_source_code):
    """
     Remove head and CSS and scrtipt tags
     return everything within
     the html body
    """
    soup = BeautifulSoup(html_source_code,'html.parser')
    body = soup.findAll("body")
   
    remove_body = body_regex.sub("", str(body[0]))
    remove_div = div_regex.sub("", remove_body)
    removed_span = span_regex.sub("", remove_div)
    
    #remoong empty elements
    removed_a_tags = re.sub(atag_regex, '', removed_span) 
    removed_atag2_regex =  re.sub(atag2_regex, '', removed_a_tags) 
    removed_imgs_tags =re.sub(img_regex, '', removed_atag2_regex)  
 
    html_body_content = removed_imgs_tags
    
    return html_body_content


    
def filter_html_body(html_body_content): 
    """
     Filters the html content wrap text 
     in p tags return a parsed html
    """
    soup = BeautifulSoup(html_body_content,'html.parser')
    content_data = []
    filtered_list = []
    for data in soup:
        content_data.append(str(data))
        
    filtered_content = [ele for ele in content_data if ele.strip()] 
    index = 0 
    for element in filtered_content:
        if(element.startswith('<')==False):
            filtered_content[index] = "<p>"+element+"</p>"
        index = index + 1
    return filtered_content


def create_uncoverted_directory(dataset_name,timestr):
   
     cwd = os.getcwd()
     unconverted_directory = str(str(dataset_name) +"_UnconvertedHTML_Generated_On_"+str(timestr))
     unconverted_directory = os.path.join(cwd,unconverted_directory);
     while not os.path.exists(unconverted_directory):
         os.mkdir(unconverted_directory)
         
     return unconverted_directory
    
def save_unconverted_file(unconverted_file,source_code,html_file_name):
     unconverted_file = os.path.join(unconverted_file,html_file_name)
     unconverted_file = open(unconverted_file ,"w",encoding="utf-8")
     unconverted_file.write("%s\n" % source_code)
     unconverted_file.close()

def open_directory_and_process_html(file_path): 
    timestr = generated_time()
    dataset_name = os.path.basename((file_path))                   
    targetPath = str(str(dataset_name) +"_MDConverted_Generated_On_"+str(timestr))
    
    
    attachments = [os.path.abspath(x) for x in glob(file_path +'\\*/')]  
    html_files_path= glob(file_path +'\\*.html')
    html_files = [os.path.basename(x) for x in glob(file_path +'\\*.html')]
    Total_html_files = len(html_files_path)    

    failded_conversion = []
    uncoverted_source_codes =[]
    if(Total_html_files == 0):
        print("No Html Files Found in the provided directory",file_path)
        print("Try Again ! Restart the program")
        exit
       
    else:
        print("File Dataset Name: ", dataset_name)
        print("Total Html Files Found In Selected Dataset '"+dataset_name+"' : "+ str(Total_html_files))
        print("Html Files With File Attachment In Selected Dataset '"+dataset_name+"' : "+str(len(attachments)))
        
        print("Click and Enter 'Y' to continue the conversion process ===> ",end="")
        confirmation =  str(input()).strip()
        if(confirmation == "Y" ):
            cwd = os.getcwd()
            targetPath = os.path.join(cwd,targetPath);
            while not os.path.exists(targetPath):
                os.mkdir(targetPath)
            
            for file_number in range(0,Total_html_files):
                
                file_name = os.path.basename(html_files_path[file_number]) 
                print("Reading Html File "+ file_name)
                html_source_code = read_html_file(html_files_path[file_number])
               
                html_body_content = remove_html_tags(html_source_code)
                try:
                    
                    body= html2markdown.convert(html_body_content)
               
                    md_file_name = file_name.strip()+".md"
                    
                    targetFile = os.path.join(targetPath, md_file_name)
    
                    targetFile = open(targetFile ,"w",encoding="utf-8")
                    
                    targetFile.write("%s\n" % body)
                    targetFile.close()
                    print("Converted MD File "+ file_name)
                except:
                    uncoverted_source_codes.append(html_source_code)
                    failded_conversion.append(file_name)
                    print(file_name," Html File could not be converted ! Moving to Convert Next File")
                  
            
            total_converted_files = str(Total_html_files - len(failded_conversion))
            print("=======================================================================")
            print("=======================================================================\n")   
            if(len(failded_conversion)!= 0):
                message = "NOTE: YOU ARE SEEING THIS MESSAGE AS THE "
                print("\n\n"+message+"FOLLOWING HTML FILES WERE NOT CONVERTED, DUE TO BADLY WRITTEN HTML FORMAT\n")
                print("Following artilces are badly written, please convert them manually ")
                unconverted_directory = create_uncoverted_directory(dataset_name,timestr)
                for file in range(len(failded_conversion)):
                    corrupted_file = failded_conversion[file]
                    save_unconverted_file(unconverted_directory,uncoverted_source_codes[file],corrupted_file)
                    print(str(file+1)+". "+corrupted_file)
                    
           
          
            
            print("HTML Files has been Converted Sucessfully.\nPlease refer to the following directory to check the converted md\n\nDirectory==>"+targetPath)
            print("Conversion Summary:\n"+"Total HTML Files Converted: "+str(total_converted_files))
            print("Total Unconverted Html Files: "+ str(len(failded_conversion)))
            print("\nTotal Time took to convert entire dataSet:", ("{0:.6g} Seconds".format(time.time() - start_time) )) 
            print("Click and Enter 'q' to quit the program or Enter 'N' to convert another dataSet: ",end="")
            exit_confirmation =  str(input()).strip()
            if(exit_confirmation =='q'):
                print("Thank you for using the program ! Goodbye")
                exit
            elif(exit_confirmation =='N'):
                main()
            else:
                 print("You did not enter 'q' or 'N', closing the  programme ",end="")
                 print("\nThank you for using the program ! Goodbye")
                 exit
            
        else:
             print("Confrimation Failed Closing the program !")
             exit
             
def main():
    print("===========================================")
    print("*********************************")
    print("*********************************")
    print("     HTML TO MD CONVERTER        ")      
    print("*********************************")
    print("*********************************")
    print("===========================================\n\n")
    
    print("File Dialogbox Gui is being loaded:\n\n ")
    dataset_path = ask_file_directory()
    print("Selected File Path:", dataset_path)
    open_directory_and_process_html(dataset_path) 
  
    
    
if __name__ == '__main__':
    main()