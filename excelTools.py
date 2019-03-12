
import json
import operator
import os
import re

import xlrd as xlrd
import xlwt as xlwt

# writebook = xlwt.Workbook()#打开一个excel
# sheet = writebook.add_sheet('test')#在打开的excel中添加一个sheet
#
# dir = "."
# row = 1
# for root,dirs,files in os.walk(dir):
#     if files and "接见会见.json" in files:
#         with open(root+"\接见会见.json", 'r', encoding='utf-8') as f:
#             eventinfo_list = json.load(f)
#             for i,event in enumerate(eventinfo_list):
#                 row += 1
#                 sheet.write(row, 1, i)  # 写入excel，i行0列
#                 sheet.write(row, 2, event['title'])#写入excel，i行0列
#                 sheet.write(row, 3, event['abstract'])  # 写入excel，i行0列
#                 sheet.write(row, 4, event['text'])  # 写入excel，i行0列
#     pass
# # with open('leaders_activity', 'r', encoding='utf-8') as f:
# #     event_type = json.load(f)
#
# # sheet.write(i,0,result[0])#写入excel，i行0列
# # sheet.write(i,1,result[1])
from xlutils.copy import copy

from stringutils import getSimilar


class excelTools:
    '''
    读取excel内容
    '''
    def __init__(self):
        self.excelfile='./已标注事件.xls'
        self.testfile = './testpool20190121.xls'

    def setExcelFilePath(self, filepath):
        self.excelfile = filepath

    def setTestFilePath(self, filepath):
        self.testfile = filepath

    """
    将excel中的数据转化为cnn的训练数据
   """
    def readExcelTrainData(self):
        event_list = []
        wb = xlrd.open_workbook(filename=self.excelfile)
        shheet1 = wb.sheet_by_index(0)
        for row in range(shheet1.nrows):
            if row == 0:
                continue
            a = shheet1.cell(row, 0)
            event_info = {
                'text': shheet1.cell(row, 0).value,
                'chatEvent': shheet1.cell(row, 1).value,
                'act': shheet1.cell(row, 4).value,
                'accept': shheet1.cell(row, 7).value,
                'time': str(shheet1.cell(row, 10).value),
                'location': shheet1.cell(row, 13).value,
            }
            event_list.append(event_info)
        return event_list

    def readExcel2list(self):
        event_list = []
        wb = xlrd.open_workbook(filename=self.excelfile)
        shheet1 = wb.sheet_by_index(0)
        print(shheet1.name, shheet1.nrows, shheet1.ncols)
        for row in range(shheet1.nrows):
            if row == 0:
                continue
            a = shheet1.cell(row, 0)
            event_info = {
                'title': shheet1.cell(row, 0).value,
                'abstract': shheet1.cell(row, 1).value,
                'text': shheet1.cell(row, 2).value,
            }
            event_list.append(event_info)
        return event_list

    def readExcel2yied(self):
        event_list = []
        wb = xlrd.open_workbook(filename=self.excelfile)
        shheet1 = wb.sheet_by_index(0)
        print(shheet1.name, shheet1.nrows, shheet1.ncols)
        for row in range(shheet1.nrows):
            if row == 0:
                continue
            yield shheet1.cell(row, 0).value, "url", "date", shheet1.cell(row, 1).value+"。"+shheet1.cell(row, 2).value

    def readTestExcel2yied(self):
        event_list = []
        wb = xlrd.open_workbook(filename=self.testfile)
        shheet1 = wb.sheet_by_index(0)
        print(shheet1.name, shheet1.nrows, shheet1.ncols, os.path.basename(__file__))
        for row in range(shheet1.nrows):
            if row == 0:
                continue
            yield shheet1.cell(row, 0).value, "url", "date", ""

    # 保存title abstract text
    def write2ExistedExcel(self, result, start, end):
        rb = xlrd.open_workbook(self.excelfile)
        wb = copy(rb)
        sheet = wb.get_sheet(0)
        cols = len(result[0])
        rowNum = start
        while rowNum < end:
            # sheet.write(rowNum, 5, result[rowNum - 1][0].replace(",","\n"))
            # sheet.write(rowNum, 6, result[rowNum - 1][1].replace(",","\n"))
            # sheet.write(rowNum, 7, result[rowNum - 1][2].replace(",","\n"))
            # print(rowNum, result[rowNum-start])
            sheet.write(rowNum, 5, str(result[rowNum - start][0]).replace(",","\n"))
            sheet.write(rowNum, 6, str(result[rowNum - start][1]).replace(",","\n"))
            sheet.write(rowNum, 7, str(result[rowNum - start][2]).replace(",","\n"))
            rowNum += 1
        os.remove(self.excelfile)
        wb.save(self.excelfile)

    # 新闻文本分句，一句一行存入
    def create_test_pool(self, title, url, date, text):
        # 测试数据 分句 然后按行填入excel中
        s = title + "。" + text
        s_list = re.split(r'[;。]', s)
        if len(s_list) > 8:
            s_list = s_list[0:8]
        s_list = [x.strip() for x in s_list if x.strip(' ')!=""]
        s_list_len = len(s_list)
        #处理要放入数据的excel
        rb = xlrd.open_workbook(self.testfile)
        nrows = rb.sheet_by_index(0).nrows
        wb = copy(rb)
        sheet1 = wb.get_sheet(0)
        for row in range(s_list_len):
            print("excelTools.py line143 ",row + nrows, os.path.basename(__file__))
            sheet1.write(row + nrows, 0, s_list[row])
        os.remove(self.testfile)
        wb.save(self.testfile)

    # 抽取结果的字典形式转入 excel文件中
    def extractResult2excel(self, extract_list):
        extract_list_len = len(extract_list)
        rb = xlrd.open_workbook(self.excelfile)
        wb = copy(rb)
        sheet1 = wb.get_sheet(0)
        for row in range(extract_list_len):
            print(row + 1, os.path.basename(__file__))
            sheet1.write(row + 1, 2, 1 if extract_list[row]["事件类型"] == "会谈" else 0)
            sheet1.write(row + 1, 3, extract_list[row]["匹配模板"] if extract_list[row]["匹配模板"] else "")
            sheet1.write(row + 1, 5, extract_list[row]["抽取结果"]["会谈方1"])
            sheet1.write(row + 1, 8, extract_list[row]["抽取结果"]["会谈方2"])
            sheet1.write(row + 1, 11, extract_list[row]["抽取结果"]["时间"])
            sheet1.write(row + 1, 14, extract_list[row]["抽取结果"]["地点"])
            sheet1.write(row + 1, 17, extract_list[row]["抽取结果"]["会谈内容"])
            sheet1.write(row + 1, 20, extract_list[row]["抽取结果"]["会谈结果"])
        os.remove(self.excelfile)
        wb.save(self.excelfile)


    # 抽取结果的字典形式转入 excel文件中
    def extractCNNResult2excel(self, extract_list):
        extract_list_len = len(extract_list)
        rb = xlrd.open_workbook(self.excelfile)
        wb = copy(rb)
        sheet1 = wb.get_sheet(0)

        for row in range(extract_list_len):
            print(row + 1, os.path.basename(__file__))
            sheet1.write(row + 1, 2, extract_list[row]["event_type"])
            sheet1.write(row + 1, 5, extract_list[row]["act_role"])
            sheet1.write(row + 1, 8, extract_list[row]["accept_role"])
            sheet1.write(row + 1, 11, extract_list[row]["time"])
            sheet1.write(row + 1, 14, extract_list[row]["loc"])
        os.remove(self.excelfile)
        wb.save(self.excelfile)

    # 计算事件类型评测值
    def evaluateEventType(self, colum):
        rb = xlrd.open_workbook(self.excelfile)
        sheet1 = rb.sheet_by_index(0)
        x1, x2, y1, y2 = 0,0,0,0
        zheng = 0
        fan = 0
        for row in range(sheet1.nrows):
            if row == 0:
                continue
            # print(row , sheet1.nrows,os.path.basename(__file__))
            realevent = int(sheet1.cell(row , 1).value)
            jevent = int(sheet1.cell(row , colum).value)
            if realevent == 1:
                if jevent == 1:
                    x1 = x1+1
                elif jevent == 0:
                    x2 = x2 + 1
                zheng = zheng + 1
            elif realevent == 0:
                if jevent == 1:
                    y1 = y1+1
                elif jevent == 0:
                  y2 = y2 + 1
                fan = fan + 1
        P = float(x1)/(x1+y1)
        R = float(x1)/(x1+x2)
        F = 2 * P * R /(P+R)
        print(colum, ":", "precision",float(x1)/(x1+y1),"precall",float(x1)/(x1+x2),"F：",F,"zheng:",zheng,"fan:",fan,"x1",x1,"x2",x2,"y1",y1,"y2",y2)

    #计算事件元素
    def evaluateEventArgument(self, colum):
        rb = xlrd.open_workbook(self.excelfile)
        sheet1 = rb.sheet_by_index(0)
        x1, x2, x3, y1, y2, y3 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for row in range(sheet1.nrows):
            if row == 0:
                continue
            # print(row , sheet1.nrows,os.path.basename(__file__))
            labelEvent = sheet1.cell(row , colum - 2).value
            judgeEvent = sheet1.cell(row, colum - 1).value
            match = sheet1.cell(row , colum).value

            if labelEvent :
                if judgeEvent:
                    if match == 1.0:
                        x1 = x1 + 1
                    else:
                        x2 = x2 + 1
                else:
                    x3 = x3 + 1
            else:
                if judgeEvent:
                    y2 = y2 + 1
                else:
                    y3 = y3 + 1

        print(colum, ":", "precision",float(x1)/(x1+x2+y2),"precall",float(x1)/(x1+y2+x3))


    # 计算事件类型评测值
    def evaluateCNNEventType(self, colum):
        rb = xlrd.open_workbook(self.excelfile)
        sheet1 = rb.sheet_by_index(0)
        x1, x2, y1, y2 = 0,0,0,0
        for row in range(sheet1.nrows):
            if row == 0:
                continue
            # print(row , sheet1.nrows,os.path.basename(__file__))
            realevent = sheet1.cell(row , 1).value
            jevent = sheet1.cell(row , colum).value
            if realevent == 1.0:
                if jevent == 1.0:
                    x1 = x1+1
                elif jevent == 0.0:
                    x2 = x2 + 1
            elif realevent == 0.0:
                if jevent == 1.0:
                    y1 = y1+1
                elif jevent == 0.0:
                  y2 = y2 + 1
        print(colum, ":", "precision",float(x1)/(x1+x2),"precall",float(x1)/(x1+y1))

    #计算事件元素
    def evaluateCNNEventArgument(self, colum):
        rb = xlrd.open_workbook(self.excelfile)
        sheet1 = rb.sheet_by_index(0)
        x1, x2, y1, y2 = 0.0, 0.0, 0.0, 0.0
        zheng = 0
        fan = 0
        for row in range(sheet1.nrows):
            if row == 0:
                continue
            # print(row , sheet1.nrows,os.path.basename(__file__))
            labelRole = str(sheet1.cell(row , colum - 2).value)
            judgeRole = str(sheet1.cell(row, colum - 1).value)

            if labelRole != "":
                if getSimilar(labelRole,judgeRole):
                    x1 += 1
                else:
                    x2 += 1
                zheng = zheng + 1
            else:
                if judgeRole == "":
                    y1 += 1
                else:
                    y2 += 1
                fan = fan + 1
        P = float(x1) / (x1 + y1)
        R = float(x1) / (x1 + x2)
        if P+R != 0:
            F = 2 * P * R / (P + R)
        else:
            F = -1
        print(colum, ":", "precision",float(x1)/(x1+y1),"precall",float(x1)/(x1+x2),"F：",F,"zheng:",zheng,"fan:",fan,"x1",x1,"x2",x2,"y1",y1,"y2",y2)

if __name__ == "__main__":
    etool = excelTools()
    etool.readExcel2yied()
    pass