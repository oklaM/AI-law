import pdfplumber
import pandas as pd
import os

folder_txt = os.path.join(os.getcwd(), 'txt')
folder_json = os.path.join(os.getcwd(), 'json')

if not os.path.exists(folder_txt):
    os.mkdir(folder_txt)

if not os.path.exists(folder_json):
    os.mkdir(folder_json)

path = os.path.join(os.getcwd(), 'pdf')

pdfs = os.listdir(path)

# for pdf in pdfs:
#     path_pdf = os.path.join(path, pdf)
#     path_txt = os.path.join(folder_txt, pdf.replace('.pdf', '.txt'))
#     if os.path.exists(path_txt):
#         os.unlink(path_txt)
#     f_pdf = pdfplumber.open(path_pdf)  ## open pdf
#     f_txt = open(path_txt, 'a', encoding='utf-8')  ## open txt
#     for page in f_pdf.pages:
#         # for word in page.extract_words():
#         #     f_txt.write(word)
#         # f_txt.write(page.extract_words())
#         f_txt.write(page.extract_text())
#         # print(page.extract_text())
#     # for table in page.extract_tables(): 
#     #     df = pd.DataFrame(table) 
#     #     #第一列当成表头： df = pd.DataFrame(table[1:],columns=table[0])
#     #     print(df)
#     f_txt.close() ## close txt
#     f_pdf.close() ## close pdf
#     break
path = os.path.join(os.getcwd(), 'pdfs.txt')
with open(path, 'w', encoding="utf-8") as f:
    for pdf in pdfs:
        f.write(pdf + '\n')
