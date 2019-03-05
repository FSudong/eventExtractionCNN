import os
import platform
from pprint import pprint

from pyltp import *

import Config


class LtpToolFast:
    def __init__(self, lexicon_filepath='', display=False):
        fsd_computer = platform.node() != 'DESKTOP-OJ37RMB'
        ltp_data_dir = r'F:\Coding\ltp_data' if fsd_computer else r'C:\Users\ll\Downloads\ltp\3.4'

        self.lexicon = "F:\Coding\ltp_data\lexicon"
        # 成员函数是否直接展示结果
        self.display = display
        self.lexicon_filepath = lexicon_filepath
        # 分词
        self.segmentor = Segmentor()
        cws_model_path = os.path.join(ltp_data_dir, 'cws.model')
        if lexicon_filepath:
            self.segmentor.load_with_lexicon(cws_model_path, lexicon_filepath)
        else:
            self.segmentor.load(cws_model_path)
        # 词性标注
        self.postagger = Postagger()
        pos_model_path = os.path.join(ltp_data_dir, 'pos.model')
        if lexicon_filepath:
            self.postagger.load_with_lexicon(pos_model_path, lexicon_filepath)
        else:
            self.postagger.load(pos_model_path)
        # 命名实体识别
        self.recognizer = NamedEntityRecognizer()
        ner_model_path = os.path.join(ltp_data_dir, 'ner.model')
        self.recognizer.load(ner_model_path)
        # 依存句法
        self.parser = Parser()
        parser_model_path = os.path.join(ltp_data_dir, 'parser.model')
        self.parser.load(parser_model_path)
        # 语义分析
        self.labeller = SementicRoleLabeller()
        pisrl_model_path = os.path.join(ltp_data_dir, 'pisrl_win.model')
        self.labeller.load(pisrl_model_path)

    def __del__(self):
        self.segmentor.release()
        self.postagger.release()
        self.recognizer.release()
        self.parser.release()
        self.labeller.release()


    """
    一波在ltp接口上直接封装的函数
    函数不会进行嵌套调用
    """
    def segment(self, sentence):
        return list(self.segmentor.segment(sentence))

    def tag(self, words):
        return list(self.postagger.postag(words))

    def dependency(self, words, tags):
        return self.parser.parse(words, tags)

    def ner(self, words, tags):
        netags = self.recognizer.recognize(words, tags)  # 命名实体识别
        if self.display:
            print('命名实体识别:', list(netags))
        return list(netags)

    def labelRole(self, words, tags, arcs):
        roles = self.labeller.label(words, tags, arcs)  # 语义角色标注
        if self.display:
            print('\n', '-' * 8, "语言角色", '-' * 8)
            for role in roles:
                print(role.index, "".join(
                    ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
        return roles



# 此函数作用是对初始语料进行分词处理后，作为训练模型的语料
def cut_txt(old_file):
    ltp = LtpToolFast()
    global cut_file     # 分词之后保存的文件名
    cut_file = old_file + '_cut.txt'

    try:
        fi = open(old_file, 'r', encoding='utf-8')
    except BaseException as e:  # 因BaseException是所有错误的基类，用它可以获得所有错误类型
        print(Exception, ":", e)    # 追踪错误详细信息
    text = fi.read()  # 获取文本内容
    new_text = ltp.segment(text)
    str_out = ' '.join(new_text).replace('，', '').replace('。', '').replace('？', '').replace('！', '') \
        .replace('“', '').replace('”', '').replace('：', '').replace('…', '').replace('（', '').replace('）', '') \
        .replace('—', '').replace('《', '').replace('》', '').replace('、', '').replace('‘', '') \
        .replace('’', '')     # 去掉标点符号
    fo = open(cut_file, 'w', encoding='utf-8')
    fo.write(str_out)

def model_train(train_file_name, save_model_file):  # model_file_name为训练语料的路径,save_model为保存模型名
    from gensim.models import word2vec
    import gensim
    import logging
    # 模型训练，生成词向量
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(train_file_name)  # 加载语料
    model = gensim.models.Word2Vec(sentences, size=Config.word_embedding_size)  # 训练skip-gram模型; 默认window=5
    model.save(save_model_file)
    model.wv.save_word2vec_format(save_model_name + ".bin", binary=True)   # 以二进制类型保存模型以便重用


from gensim.models import word2vec
import os
import gensim

cut_file = 'word2vecModel\word2vec_train.txt'
if not os.path.exists(cut_file ):    # 判断文件是否存在，参考：https://www.cnblogs.com/jhao/p/7243043.html
    cut_txt(cut_file)  # 须注意文件必须先另存为utf-8编码格式

save_model_name = 'word2vecModel\\vectors.model'

if not os.path.exists(save_model_name):     # 判断文件是否存在
    model_train(cut_file, save_model_name)
else:
    print('此训练模型已经存在，不用再次训练')

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
