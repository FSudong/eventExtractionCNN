"""
1、word2vec模型训练得到所有的word embedding
2、分类模型训练集构造
    分词 词性标注
    argument candidate & trigger position
    事件类型 candidate角色
    空格
3、训练模型
4、处理实际的一个句子
    句子分词

3、
"""
import re


from excelTools import excelTools
from generate_word2vec_resource import *
from multi_task_test_w2c import trainEval
from LtpToolFast import LtpToolFast

def extractBysentence():
    pass

def evaluate():

    pass

"""
读取excel中信息
"""
def excelFile2train():
    ltp = LtpToolFast()
    triggers = ["会见", "访问", "会晤", "对话", "谈判", "交流", "出席", "签署", "访谈", "采访", "问答", "座谈", "沟通", "交谈", "谈话", "出席", "邀请", "峰会"]
    excelfile = "train_eval_data\\testpool20190122-select-bz-jianshaoledingyu.xls"
    txtfile = "train_eval_data\\datas_ace.txt"
    etl = excelTools()
    etl.setExcelFilePath(excelfile)
    alldata = etl.readExcelTrainData()
    save2txt = []
    save_sentence = 0
    for data in alldata:
        # 分词 词性 命名实体
        words = ltp.segment(data["text"])
        tags = ltp.tag(words)
        ners = ltp.ner(words, tags)
        arcs = ltp.dependency(words, tags)
        print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
        tri_word = ""
        for i in range(len(arcs)):
            if arcs[i].relation == "HED":
                tri_word = words[i]
        assert (tri_word != "")
        roles = ltp.labelRole(words, tags, arcs)
        role_dict = ltp.structureRole(words, roles)
        words,tags,ners = ltp.structureWTER(words,tags,ners)
        trigger_index = 0
        for i in range(len(words)):
            if words[i].find(tri_word) != -1:
                trigger_index = i
                break
        # 触发词 index
        eventType = int(data["chatEvent"])
        wt = []
        wt = [words[i] + "/" + tags[i] for i in range(len(words))]
        for i in range(len(words)):
            if words[i] in triggers:
                trigger_index = i
                break


        bt = []
        old_old_size = len(save2txt)
        for i in range(len(words)):
            if ners[i] != "O" or (words[i] in role_dict["A0"]) or (words[i] in role_dict["A1"]) or (words[i] in role_dict["LOC"]) or (words[i] in role_dict["TMP"]):
                bt_tag = ["A" for i in range(len(words))]

                bt_tag[trigger_index] = "T"
                bt_tag[i] = "B"
                bt = [words[i]+"/"+bt_tag[i] for i in range(len(words))]

                if data["act"] != "" and data["act"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt)+"\n"+", ".join(bt)+"\n"+str(int(eventType))+"-"+"1"+"\n\n")
                if data["accept"] != "" and data["accept"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "2"+"\n\n")
                if data["time"] != "" and (data["time"].find(words[i]) != -1 or words[i].find(data["time"]) != -1):
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "3"+"\n\n")
                if data["location"] != "" and data["location"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "4"+"\n\n")
        if len(save2txt) <= old_old_size:
            for i in range(len(words)):
                if ners[i] != "O" or (words[i] in role_dict["A0"]) or (words[i] in role_dict["A1"]) or (
                        words[i] in role_dict["LOC"]) or (words[i] in role_dict["TMP"]):
                    bt_tag = ["A" for i in range(len(words))]
                    bt_tag[trigger_index] = "T"
                    bt_tag[i] = "B"
                    bt = [words[i] + "/" + bt_tag[i] for i in range(len(words))]
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n" + str(int(eventType)) + "-" + "0"+"\n\n")
                    break
        assert (len(save2txt)>old_old_size)
        print("正处理excel中第x条数据：", save_sentence)
        if len(save2txt) > old_old_size:
            save_sentence += 1
        pass
    print("共有语句数目：",save_sentence)
    with open(txtfile,"w", encoding="utf-8") as f:
        for _ in save2txt:
            f.write(_)

'''
正则表达式
'''

def excelFile2trainZheze():
    ltp = LtpToolFast()
    triggers = ["会见", "访问", "会晤", "对话", "谈判", "交流", "出席", "签署", "访谈", "采访", "问答", "座谈", "沟通", "交谈", "谈话", "出席", "邀请", "峰会"]
    excelfile = Config.saveEvalFile
    txtfile = Config.txtfile_totrain
    etl = excelTools()
    etl.setExcelFilePath(excelfile)
    alldata = etl.readExcelTrainData()
    save2txt = []
    for data in alldata:
        # 分词 词性 命名实体
        old_words = ltp.segment(data["text"])
        tags = ltp.tag(old_words)
        old_ners = ltp.ner(old_words, tags)
        words = []
        ners = []
        i = 0
        while i < len(old_words):
            if ners[i] == "B-Ni":
                sub_words = ""
                while ners[i]!="E-Ni":
                    sub_words += old_words[i]
                    i += 1
                sub_words += old_words[i]
                i += 1
                words.append(sub_words)
                ners.append("S")
            elif ners[i] == "S-Ni":
                words.append(old_words[i])
                i += 1
                ners.append("S")
            elif ners[i] == "O":
                words.append(old_words[i])
                i += 1
                ners[i].append("O")
        tags = ["n" for _ in range(len(words))]


        # 触发词 index
        eventType = int(data["chatEvent"])
        trigger_index = -1
        wt = [words[i] + "/" + tags[i] for i in range(len(words))]
        for i in range(len(words)):
            if words[i] in triggers:
                trigger_index = i
                break

        for i in range(len(words)):
            # print(ners[i],len(re.compile(r'((\d+年)|(\d+月)|(\d+日))+').findall(ners[i])) > 0)
            if ners[i] != "O" or len(re.compile(r'((\d+年)|(\d+月)|(\d+日))+').findall(words[i])) > 0:
                bt_tag = ["A" for i in range(len(words))]
                bt_tag[trigger_index] = "T"
                bt_tag[i] = "B"
                bt = [words[i]+"/"+bt_tag[i] for i in range(len(words))]
                if data["act"] != "" and data["act"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt)+"\n"+", ".join(bt)+"\n"+str(int(eventType))+"-"+"1"+"\n\n")
                if data["accept"] != "" and data["accept"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "2"+"\n\n")
                if data["time"] != "" and (data["time"].find(words[i]) != -1 or words[i].find(data["time"]) != -1):
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "3"+"\n\n")
                if data["location"] != "" and data["location"].find(words[i]) != -1:
                    save2txt.append(", ".join(wt) + "\n" + ", ".join(bt) +"\n"+ str(int(eventType)) + "-" + "4"+"\n\n")
        pass
    with open(txtfile,"w", encoding="utf-8") as f:
        for _ in save2txt:
            f.write(_)
    ltp.__del__()


def generateWord2vec():
    from gensim.models import word2vec
    import os
    import gensim

    cut_file = '.\\word2vecModel\\word2vec_train.txt'
    # if not os.path.exists(cut_file ):    # 判断文件是否存在，参考：https://www.cnblogs.com/jhao/p/7243043.html
    cut_txt(cut_file)  # 须注意文件必须先另存为utf-8编码格式

    save_model_name = 'word2vecModel\\vectors.model'

    # if not os.path.exists(save_model_name):     # 判断文件是否存在
    model_train(cut_file, save_model_name)
    # else:
    #     print('此训练模型已经存在，不用再次训练')

    # 加载已训练好的模型
    model_1 = word2vec.Word2Vec.load(save_model_name)
    # 计算两个词的相似度/相关程度
    print(model_1.wv.index2word)

    y1 = model_1.similarity("习近平", "李克强")
    # print("词嵌入维度：{}\n词典：{}\n".format(model_1.layer1_size,model_1.wv.vocab))
    print(u"习近平和李克强的相似度为：", y1)
    print("-------------------------------\n")

    # 计算某个词的相关词列表
    y2 = model_1.most_similar("李克强", topn=10)  # 10个最相关的
    print(u"和李克强最相关的词有：\n")
    for item in y2:
        print(item[0], item[1])
    print("-------------------------------\n")
    pass





def main_entrance():
    excelFile2train()
    # 得到规范的训练和测试数据
    # excelFile2trainZheze()
    # word2vec更新
    # print("word2vec更新...")
    # generateWord2vec()
    # print("generateWord2vec")
    # 开始训练并输出
    # trainEval()


if __name__ == '__main__':
    main_entrance()