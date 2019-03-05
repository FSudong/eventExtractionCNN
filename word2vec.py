# coding=utf-8
import numpy as np
from xlrd.timemachine import xrange
from gensim.models import word2vec
import gensim
import logging
"""
从文件中读取词向量
文件格式u：
词数量 向量维度  
词 向量
"""
class word2vec1(object):
    def __init__(self, fname):
        word_vecs = {}
        with open(fname, "rb") as f:
            header = f.readline()
            vocab_size, layer1_size = map(int, header.split())
            binary_len = np.dtype('float32').itemsize * layer1_size
            for line in xrange(vocab_size):
                word = []
                while True:
                    ch = f.read(1)
                    if ch == ' ':
                        word = ''.join(word)
                        break
                    if ch != '\n':
                        word.append(ch)
                word_vecs[word] = np.fromstring(f.read(binary_len), dtype='float32')
        # 词嵌入维数
        self.embedding_size = layer1_size
        self.word2vec = word_vecs
        words, vectors = zip(*word_vecs.items())
        self.words = words  # pretrain文件当中所有的词
        self.word_vec = list(vectors)  # 每一个词的embedding id与word_id words 一致
        word_id = dict(zip(words, range(len(words))))
        # print words[word_id["南京"]]
        # print type(vecs)
        # print np.array(vecs).shape
        self.words = list(words)
        # 矩阵经过归一化处理 L2
        vectors = np.array(vectors)
        # 下面的代码主要是为了计算相似度方便
        vectors_norm = np.linalg.norm(vectors, axis=1)
        vectors_norm = np.reshape(vectors_norm, (vectors.shape[0], 1))
        vectors_norm_div = np.divide(vectors, vectors_norm)
        self.vectors = vectors_norm_div
        self.word_id = word_id


    """
    返回与word最相似的n个词的索引  和 相似度
    """

    def cosine(self, word, n=10):
        word_vec = self.vectors[self.word_id[word]]
        word_norm = np.linalg.norm(word_vec)
        word_norm_div = np.divide(word_vec, word_norm)
        metrics = np.dot(self.vectors, word_norm_div.T)
        best = np.argsort(metrics)[::-1][1:n + 1]
        best_metrics = metrics[best]
        return best, best_metrics

    def close_word(self, word, n=30):
        best, best_metrics = self.cosine(word, n)
        return map(lambda x:self.words[x],best)


class word2vecUsing(object):
    def __init__(self, fname):
        self.model_1 = word2vec.Word2Vec.load(fname)
        self.embedding_size = self.model_1.layer1_size
        word_vecs = {}
        vectors = []
        for word in self.model_1.wv.index2word:
            word_vecs[word] = self.model_1[word]
            vectors.append(self.model_1[word])
        self.word2vec = word_vecs
        self.words = self.model_1.wv.index2word  # pretrain文件当中所有的词
        self.word_vec = list(vectors)  # 每一个词的embedding id与word_id words 一致
        self.vectors = self.word_vec

        word_id = dict(zip(self.words, range(len(self.words))))
        self.word_id = word_id

    """
    返回与word最相似的n个词的索引  和 相似度
    """
    def cosine(self, word1, word2):
        return self.model_1.similarity(word1, word2)

    def close_word(self, word, n=30):
        return self.model_1.most_similar(word, topn=30)


"""
测试程序 john.zhang 2016-11-30
已经验证 正确
"""
# word2vec = word2vec("vectors_100.bin")
# words = word2vec.close_word("上升")
# print ", ".join(words)

# 下降, 攀升, 下滑, 增加, 减少, 回升, 飙升, 上涨, 升高, 提升, 回落, 下调, 缩减, 下跌, 提高, 萎缩, 上扬, 降低, 大增, 上调, 激增, 增长, 猛增, 锐减, 收窄, 骤降, 走低, 缩水, 抬升, 走高
