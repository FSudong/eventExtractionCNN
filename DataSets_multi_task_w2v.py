# coding=utf-8
"""
john.zhang 2016-12-22
中文的关系分类数据集 这里能用到的数据如下
1 整个句子词的id
2 整个句子词的word2vec
3 整个句子的词性
4 触发词位置向量
5 候选词的位置向量
6 触发词及其上下文词id
7 触发词及其上下文词word2vec
8 触发词及其上下文词性
9 候选词及其上下文词id
10 候选词及其上下文词word2vec
11 候选词及其上下文词性
"""
from collections import namedtuple
import numpy as np
import _pickle as cPickle
import os

import Config
from word2vec import *


def find_candidates(items1, items2):
    """
    找出满足条件的元素的下标
    """
    result = []
    for i in range(len(items1)):
        if items1[i] in items2:
            result.append(i)
    return result


def one_hot(labels, label_num):
    """
    将输入数据转换为one-hot类型
    :param labels: 一个二维的list 这里要注意因为没有加入限定条件 很容易出错
    :param label_num: 标签数目
    :return:
    """
    result = []
    for i in range(len(labels)):
        one_hot_vec = [0] * label_num
        one_hot_vec[labels[i][0]] = 1
        result.append(one_hot_vec)
    return result


"""
测试程序 已验证
"""
"""
one_hot([[0],[1],[1]], 3)
"""


# 生成具有context信息的setence特征
def get_context_features(x, epos_id=113, windows=3):
    """
    :param x: 原始输入的整个句子
    :param epos_id: 用于句子开头和结尾的填充部分
    :param windows: 窗口的大小
    :return:
    """
    context = (windows - 1) // 2  # 上下文长度
    x_pad = list(x)
    x_pad = [epos_id] * context + x_pad
    x_pad = x_pad + [epos_id] * context
    # 依据x_pad生成多少个context
    context_w_num = len(x_pad) - windows + 1
    sentence_fatures = []
    # return map(lambda i:x_pad[i:i+windows] , range(context_w_num))
    for i in range(context_w_num):
        sentence_fatures.append(x_pad[i:i + windows])
    return sentence_fatures


class datasets(object):
    def __init__(self, file='datas_ace.txt', store_path="ace_data_cl", batch_size=5,
                 max_sequence_length=20, windows=3, eval_num=50, word2vec_bin_file="word2vecModel\\vectors.model"):
        """
        file： 数据集
        store_path: 生成的数据存储的位置
        batch_size: 匹次训练样本数目
        max_sequence_length: 最大的长度 长度超出剔除 长度不够填充
        windows: 上下文窗口的大小
        eval_num: 用于测试的数据集
        word2vec_bin_file: 预先训练得到的word2vec文件
        """
        # 预先训练得到的word2vec
        word2vec_c = word2vecUsing(word2vec_bin_file)
        self.embedding_size = word2vec_c.embedding_size
        self.word2vec = word2vec_c.word2vec
        all_words = set()  # 训练集中出现的所有的词
        all_pos_taggings = set()  # 训练集中出现的所有词性
        all_labels_event = set()  # 事件类型
        all_labels_role = set()  # 角色类型
        all_marks = set()  # 人工标注词的事件标记
        data_model = namedtuple(("data"),
                                ['words', 'pos_taggings', 'marks', 'label_event', 'label_role'])  # 词 词性 标记 事件类别
        instances = []  # 实例
        words = []  # 词
        pos_taggings = []  # 词性
        marks = []  # 标签
        label_event = []  # 事件类型
        label_role = []  # 事件角色
        with open(file, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        id = 1
        for line in lines:
            if id == 1:
                words_natures_line = line.strip().split(', ')
                for word_nature in words_natures_line:
                    # "//wp" 这种情况比较特殊
                    if "//wp" == word_nature:
                        word_nature = ["/", "wp"]
                        words.append(word_nature[0])  # 记录当前实例的词
                        pos_taggings.append(word_nature[1])  # 记录当前实例的词性
                        all_words.add(word_nature[0])  # 记录训练集当中出现的所有词
                        all_pos_taggings.add(word_nature[1])  # 记录训练集当中出现的所有词性
                    else:
                        word_nature = word_nature.split("/")
                        words.append(word_nature[0])  # 记录当前实例的词
                        pos_taggings.append(word_nature[1])  # 记录当前实例的词性
                        all_words.add(word_nature[0])  # 记录训练集当中出现的所有词
                        all_pos_taggings.add(word_nature[1])  # 记录训练集当中出现的所有词性
            if id == 2:
                words_marks_line = line.strip().split(', ')
                for word_mark in words_marks_line:
                    # if word_mark.__contains__('O'):
                    #     print(line
                    # "//A" 这种情况比较特殊
                    if "//A" == word_mark:
                        word_mark = ["/", "A"]
                        marks.append(word_mark[1])  # 记录当前实例的标注信息
                        all_marks.add(word_mark[1])  # 记录训练集中所有标注信息
                    else:
                        word_mark = word_mark.split("/")
                        # print("/".join(word_mark)
                        marks.append(word_mark[1])  # 记录当前实例的标注信息
                        all_marks.add(word_mark[1])  # 记录训练集中所有标注信息
            if id == 3:
                label_line = line.strip().split("-")
                all_labels_event.add(int(label_line[0]))  # 事件类别
                label_event.append(int(label_line[0]))  # 记录当前实例的事件类型
                all_labels_role.add(int(label_line[1]))  # 角色类型

                # 记录当前实例的角色类型
                label_role.append(int(label_line[1]))
            if id == 4:
                # 置零
                id = 1
                #                 print("words_length:{}, pos_length:{}, marks_length:{}".format(len(words),len(pos_taggings),len(marks))
                assert len(words) == len(pos_taggings) == len(marks)  # 判定数目相等
                # 长度超出最大距离
                if len(words) <= max_sequence_length:  # 超出最大长度的不记录
                    instances.append(
                        data_model(words=words, pos_taggings=pos_taggings, marks=marks, label_event=label_event,
                                   label_role=label_role))
                # 清空
                words = []  # 词
                pos_taggings = []  # 词性
                marks = []  # 人工标注
                label_event = []  # 事件类型
                label_role = []  # 角色类型
                continue
            id += 1
        all_words.add('<eos>')  # 添加一个填充无效字符
        all_pos_taggings.add('*')  # 添加一个特殊的词性
        words_size = len(all_words)  # 数据集中词的数目
        word_id = dict(zip(all_words, range(words_size)))  # 词_id 词典
        #         for t in word_id.items():
        #             print("{},{}".format(t[0],t[1])
        pos_taggings_size = len(all_pos_taggings)  # 数据集中词的词性数目
        #         print(", ".join(all_pos_taggings)
        #         print(all_labels_event
        #         print(all_labels_role
        pos_taggings_id = dict(zip(all_pos_taggings, range(pos_taggings_size)))  # 词性_id

        labels_event_size = len(all_labels_event)  # 数据集中事件的所有事件类别数目
        labels_role_size = len(all_labels_role)  # 数据集中角色类别数目

        mark_size = len(all_marks)  # 数据集中出现过的人工标记数目
        mark_id = dict(zip(all_marks, range(mark_size)))  # 人工标注_id 这个用不到

        self.windows = windows  # 上下文窗口
        self.batch_size = batch_size  # 匹次训练的实例数目
        self.max_sequence_length = max_sequence_length  # 序列最大的长度

        self.all_words = list(all_words)  # 训练集中出现的所有词
        self.all_pos_taggings = list(all_pos_taggings)  # 训练集中出现的所有词性
        self.all_marks = list(all_marks)  # 训练集中出现的所有人工标记
        self.all_labels_event = list(all_labels_event)  # 训练集中出现的所有事件标签
        self.all_labels_role = list(all_labels_role)
        self.words_size = words_size  # 词数目
        self.pos_taggings_size = pos_taggings_size  # 词性数目
        self.labels_event_size = labels_event_size  # 事件数目
        self.labels_role_size = labels_role_size  # 角色数目

        self.mark_size = mark_size  # 人工标识数目

        self.word_id = word_id  # 词_id 词典
        self.pos_taggings_id = pos_taggings_id  # 词性_id
        self.mark_id = mark_id  # 标记_id

        # 留出一部分样本用于测试集  将instance一分为二
        self.eval_num = eval_num
        self.eval_instances = instances[-eval_num:]

        instances = instances[0:-eval_num]
        self.instances_size = len(instances)  # 实例数目
        self.instances = instances  # 实例
        self.batch_nums = self.instances_size // self.batch_size  # 每一次epoch需要的batch_nums
        self.index = np.arange(self.instances_size)  # 每一个instance对应的id
        self.point = 0  # 用于记录当前实例位置

        # 判断文件是否存在
        if not os.path.exists(store_path):
            os.mkdir(store_path)
        # 将生成的数据存储到本地文件
        with open("{}/words".format(store_path), 'wb') as f:
            cPickle.dump(self.all_words, f)
        with open("{}/all_pos_taggings".format(store_path), 'wb') as f:
            cPickle.dump(self.all_pos_taggings, f)
        with open("{}/all_labels_event".format(store_path), 'wb') as f:
            cPickle.dump(self.all_labels_event, f)
        with open("{}/all_labels_role".format(store_path), 'wb') as f:
            cPickle.dump(self.all_labels_role, f)
        with open("{}/word_id".format(store_path), 'wb') as f:
            cPickle.dump(self.word_id, f)
        with open("{}/pos_taggings_id".format(store_path), 'wb') as f:
            cPickle.dump(self.pos_taggings_id, f)
        with open("{}/mark_id".format(store_path), 'wb') as f:
            cPickle.dump(self.mark_id, f)

    # 对数据集进行shuffle操作
    def shuffle(self):
        np.random.shuffle(self.index)
        self.point = 0

    # 获取匹次数据
    def next_batch(self):
        start = self.point  # 本次batch
        self.point = self.point + self.batch_size
        if self.point > self.instances_size:  # 一次epoch完成 实例重新shuffle
            self.shuffle()
            start = 0
            self.point = self.point + self.batch_size
        end = self.point
        batch_instances = map(lambda x: self.instances[x], self.index[start:end])
        return batch_instances

    # 转换成神经网络能够识别的
    def next_cnn_data(self):
        batch_instances = self.next_batch()
        y_event = []  # 事件标签
        y_role = []  # 角色标签
        x = []  # 事件句 id
        t = []  # 触发词 id
        c = []  # 候选词 id

        pos_tag = []  # 词性标注
        t_pos_tag = []  # 触发词的词性
        c_pos_tag = []  # 候选词的词性

        x_w2v = []  # 事件句的 word2vec
        t_w2v = []  # 触发词的 word2vec
        c_w2v = []  # 候选词的 word2vec

        pos_c = []  # 候选词位置向量
        pos_t = []  # 触发词位置向量
        eos_id = self.word_id['<eos>']  # 获取填充词的id
        pos_eos_id = self.pos_taggings_id['*']  # 获取填充词性的id
        # 候选词上下文窗口
        c_context = []
        # 触发词上下文窗口
        t_context = []
        # 根据当前词选出具有context的上下文信息 统一用词的id表示
        # 更多信息请关注：Relation Classification via Convolutional Deep Neural Network 论文当中叫做 sentence features
        sentences_fatures = []
        # 生成数据 标记0和1 将词用词id表示 'words', 'pos_taggings', 'marks', 'label'
        for instance in batch_instances:
            words = instance.words
            pos_taggings = instance.pos_taggings
            marks = instance.marks
            # 'label_event', 'label_role'
            label_event = instance.label_event
            label_role = instance.label_role
            # print(", ".join(words)
            # 找出当前句子的候选词下标 这里强制规定一个句子只能有一个候选词
            index_candidates = find_candidates(marks, ['B'])
            #             print("index_candidate:{}".format(index_candidates)
            #             print(", ".join(words)
            assert (len(index_candidates)) == 1
            # 找出当前句子的触发词下标 这里强制规定一个句子只能有一个触发词
            index_triggers = find_candidates(marks, ['T'])  # 找出当前句子的触发词的下标id
            #             print("index_triggers:{}".format(index_triggers)
            assert (len(index_triggers)) == 1
            # print(index_triggers
            y_event.append(label_event)  # 事件类别
            y_role.append(label_role)
            # 长度不够 人工标注标签填充
            marks = marks + ['A'] * (self.max_sequence_length - len(marks))
            #             print(marks
            # 长度不够 单词填充
            words = words + ['<eos>'] * (self.max_sequence_length - len(words))
            #             print(", ".join(words)
            # 长度不够 词性填充
            pos_taggings = pos_taggings + ['*'] * (self.max_sequence_length - len(pos_taggings))
            # 添加预先训练的word2vec数据 生成sentence features
            # 这里采用的是事先创建一个向量 然后在相应位置插入合适的数据
            x_w2c_s = np.zeros(shape=(self.max_sequence_length, self.embedding_size))
            for i in range(self.max_sequence_length):
                w_s = words[i]  # 当前词
                if w_s in self.word2vec:  # word2vec训练集中存在该词
                    x_w2c_s[i] = self.word2vec[w_s]
                else:
                    continue  # 如果不存在就直接用0表示
            x_w2v.append(x_w2c_s)
            # 词性转换为词性id
            pos_taggings = list(map(lambda x: self.pos_taggings_id[x], pos_taggings))
            pos_tag.append(pos_taggings)
            sentence_fatures_pos_tags = get_context_features(pos_taggings, epos_id=pos_eos_id, windows=self.windows)
            # 触发词及其上下文的词性id
            t_pos_tag.append(sentence_fatures_pos_tags[index_triggers[0]])
            # 候选词及其上下文的词性id
            c_pos_tag.append(sentence_fatures_pos_tags[index_candidates[0]])
            # 将当前句子的词转换为词的id
            index_words = list(map(lambda x: self.word_id[x], words))
            # x 就是词向量组成的句子特征
            x.append(index_words)
            sentence_fatures = get_context_features(index_words, epos_id=eos_id, windows=self.windows)
            # 由每一个句子当中的词的上下文组成的词组成
            sentences_fatures.append(sentence_fatures)
            # 依据候选词在句子当中的位置 选取候选词的context
            c_context.append(sentence_fatures[index_candidates[0]])
            c_contexe_s_ws = list(map(lambda x: self.all_words[x], sentence_fatures[index_candidates[0]]))
            #             print(", ".join(c_contexe_s_ws)
            # 根据候选词 选取候选词的context的word2vec特征
            c_w2v_s = np.zeros(shape=(self.windows, self.embedding_size))
            for i in range(self.windows):
                w_s = c_contexe_s_ws[i]  # 当前词
                if w_s in self.word2vec:  # word2vec训练集中存在该词
                    c_w2v_s[i] = self.word2vec[w_s]
                else:
                    continue  # 如果不存在就直接用0表示
            c_w2v.append(c_w2v_s)
            # 依据触发词在句子当中的位置 选取触发词的context
            t_context.append(sentence_fatures[index_triggers[0]])
            # 根据触发词 选取触发词的context的word2vec特征
            t_contexe_s_ws = list(map(lambda x: self.all_words[x], sentence_fatures[index_triggers[0]]))
            #             print("|".join(t_contexe_s_ws)
            t_w2v_s = np.zeros(shape=(self.windows, self.embedding_size))
            for i in range(self.windows):
                w_s = t_contexe_s_ws[i]
                if w_s in self.word2vec:
                    t_w2v_s[i] = self.word2vec[w_s]
                else:
                    continue
            t_w2v.append(t_w2v_s)
            # 候选词位置向量
            pos_candidate = list(range(-index_candidates[0], 0)) + list(range(0, self.max_sequence_length - index_candidates[0]))
            pos_c.append(pos_candidate)
            # 触发词位置向量
            pos_trigger = list(range(-index_triggers[0], 0)) + list(range(0, self.max_sequence_length - index_triggers[0]))
            pos_t.append(pos_trigger)
            # 根据句子当中触发词的下标id找出其在词表当中的位置 并进行填充
            t.append([index_words[index_triggers[0]]] * self.max_sequence_length)
            # 根据句子当中候选词的下标id找出其在词表当中的位置 并进行填充
            c.append([index_words[index_candidates[0]]] * self.max_sequence_length)
            # 确定长度是否一致
            assert len(words) == len(marks) == len(pos_taggings) == len(index_words) == len(sentence_fatures) == len(
                pos_candidate) == len(pos_trigger)
        assert len(sentences_fatures) == len(y_event) == len(y_role) == len(x) == len(t) == len(c) == len(pos_c) == len(
            pos_t) == len(
            pos_tag) == len(x_w2v) == len(c_w2v) == len(t_w2v) == len(t_pos_tag) == len(c_pos_tag)
        # 记录触发词和候选词所在句子当中的位置 并且生成触发词位置矩阵和候选词位置矩阵
        # x:(词的id) t:触发词(词的id) c:候选词(词的id) y_event:事件的类别(类别id) y_role:角色的类别 pos_c:候选词位置向量 pos_t: 触发词位置向量
        # c_context 候选词的上下文信息 t_context 触发词的上下文信息  pos_tag 句子的词性 x_w2v 句子的word2vec特征 t_w2v 触发词的word2vec特征 c_w2v 候选词的word2vec特征
        # t_pos_tag 触发词词性   c_pos_tag 候选词词性
        return x, t, c, one_hot(y_event, Config.labels_event_size), one_hot(y_role, Config.labels_role_size), pos_c, pos_t, sentences_fatures, c_context, t_context, pos_tag, \
               np.array(x_w2v), np.array(t_w2v), np.array(c_w2v), t_pos_tag, c_pos_tag

    # 用于测试的部分数据集
    def eval_cnn_data(self):
        batch_instances = self.eval_instances
        y_event = []  # 事件标签
        y_role = []  # 角色标签
        x = []  # 事件句 id
        t = []  # 触发词 id
        c = []  # 候选词 id

        pos_tag = []  # 词性标注
        t_pos_tag = []  # 触发词的词性
        c_pos_tag = []  # 候选词的词性

        x_w2v = []  # 事件句的 word2vec
        t_w2v = []  # 触发词的 word2vec
        c_w2v = []  # 候选词的 word2vec



        pos_c = []  # 候选词位置向量
        pos_t = []  # 触发词位置向量
        eos_id = self.word_id['<eos>']  # 获取填充词的id
        pos_eos_id = self.pos_taggings_id['*']  # 获取填充词性的id
        # 候选词上下文窗口
        c_context = []
        # 触发词上下文窗口
        t_context = []
        # 根据当前词选出具有context的上下文信息 统一用词的id表示
        # 更多信息请关注：Relation Classification via Convolutional Deep Neural Network 论文当中叫做 sentence features
        sentences_fatures = []
        # 生成数据 标记0和1 将词用词id表示 'words', 'pos_taggings', 'marks', 'label'
        for instance in batch_instances:
            words = instance.words
            pos_taggings = instance.pos_taggings
            marks = instance.marks
            # 'label_event', 'label_role'
            label_event = instance.label_event
            label_role = instance.label_role
            # print(", ".join(words)
            # 找出当前句子的候选词下标 这里强制规定一个句子只能有一个候选词
            index_candidates = find_candidates(marks, ['B'])
            #             print("index_candidate:{}".format(index_candidates)
            #             print(", ".join(words)
            assert (len(index_candidates)) == 1
            # 找出当前句子的触发词下标 这里强制规定一个句子只能有一个触发词
            index_triggers = find_candidates(marks, ['T'])  # 找出当前句子的触发词的下标id
            #             print("index_triggers:{}".format(index_triggers)
            assert (len(index_triggers)) == 1
            # print(index_triggers
            y_event.append(label_event)  # 事件类别
            y_role.append(label_role)
            # 长度不够 人工标注标签填充
            marks = marks + ['A'] * (self.max_sequence_length - len(marks))
            #             print(marks
            # 长度不够 单词填充
            words = words + ['<eos>'] * (self.max_sequence_length - len(words))
            #             print(", ".join(words)
            # 长度不够 词性填充
            pos_taggings = pos_taggings + ['*'] * (self.max_sequence_length - len(pos_taggings))
            # 添加预先训练的word2vec数据 生成sentence features
            # 这里采用的是事先创建一个向量 然后在相应位置插入合适的数据
            x_w2c_s = np.zeros(shape=(self.max_sequence_length, self.embedding_size))
            for i in range(self.max_sequence_length):
                w_s = words[i]  # 当前词
                if w_s in self.word2vec:  # word2vec训练集中存在该词
                    x_w2c_s[i] = self.word2vec[w_s]
                else:
                    continue  # 如果不存在就直接用0表示
            x_w2v.append(x_w2c_s)
            # 词性转换为词性id
            pos_taggings = list(map(lambda x: self.pos_taggings_id[x], pos_taggings))
            pos_tag.append(pos_taggings)
            sentence_fatures_pos_tags = get_context_features(pos_taggings, epos_id=pos_eos_id, windows=self.windows)
            # 触发词及其上下文的词性id
            t_pos_tag.append(sentence_fatures_pos_tags[index_triggers[0]])
            # 候选词及其上下文的词性id
            c_pos_tag.append(sentence_fatures_pos_tags[index_candidates[0]])
            # 将当前句子的词转换为词的id
            index_words = list(map(lambda x: self.word_id[x], words))
            # x 就是词向量组成的句子特征
            x.append(index_words)
            sentence_fatures = get_context_features(index_words, epos_id=eos_id, windows=self.windows)
            # 由每一个句子当中的词的上下文组成的词组成
            sentences_fatures.append(sentence_fatures)
            # 依据候选词在句子当中的位置 选取候选词的context
            c_context.append(sentence_fatures[index_candidates[0]])
            c_contexe_s_ws = list(map(lambda x: self.all_words[x], sentence_fatures[index_candidates[0]]))
            #             print(", ".join(c_contexe_s_ws)
            # 根据候选词 选取候选词的context的word2vec特征
            c_w2v_s = np.zeros(shape=(self.windows, self.embedding_size))
            for i in range(self.windows):
                w_s = c_contexe_s_ws[i]  # 当前词
                if w_s in self.word2vec:  # word2vec训练集中存在该词
                    c_w2v_s[i] = self.word2vec[w_s]
                else:
                    continue  # 如果不存在就直接用0表示
            c_w2v.append(c_w2v_s)
            # 依据触发词在句子当中的位置 选取触发词的context
            t_context.append(sentence_fatures[index_triggers[0]])
            # 根据触发词 选取触发词的context的word2vec特征
            t_contexe_s_ws = list(map(lambda x: self.all_words[x], sentence_fatures[index_triggers[0]]))
            #             print("|".join(t_contexe_s_ws)
            t_w2v_s = np.zeros(shape=(self.windows, self.embedding_size))
            for i in range(self.windows):
                w_s = t_contexe_s_ws[i]
                if w_s in self.word2vec:
                    t_w2v_s[i] = self.word2vec[w_s]
                else:
                    continue
            t_w2v.append(t_w2v_s)
            # 候选词位置向量
            pos_candidate = list(range(-index_candidates[0], 0)) + list(range(0, self.max_sequence_length - index_candidates[0]))
            pos_c.append(pos_candidate)
            # 触发词位置向量
            pos_trigger = list(range(-index_triggers[0], 0)) + list(range(0, self.max_sequence_length - index_triggers[0]))
            pos_t.append(pos_trigger)
            # 根据句子当中触发词的下标id找出其在词表当中的位置 并进行填充
            t.append([index_words[index_triggers[0]]] * self.max_sequence_length)
            # 根据句子当中候选词的下标id找出其在词表当中的位置 并进行填充
            c.append([index_words[index_candidates[0]]] * self.max_sequence_length)
            # 确定长度是否一致
            assert len(words) == len(marks) == len(pos_taggings) == len(index_words) == len(sentence_fatures) == len(
                pos_candidate) == len(pos_trigger)
        assert len(sentences_fatures) == len(y_event) == len(y_role) == len(x) == len(t) == len(c) == len(pos_c) == len(
            pos_t) == len(
            pos_tag) == len(x_w2v) == len(c_w2v) == len(t_w2v) == len(t_pos_tag) == len(c_pos_tag)
        # 记录触发词和候选词所在句子当中的位置 并且生成触发词位置矩阵和候选词位置矩阵
        # x:(词的id) t:触发词(词的id) c:候选词(词的id) y_event:事件的类别(类别id) y_role:角色的类别 pos_c:候选词位置向量 pos_t: 触发词位置向量
        # c_context 候选词的上下文信息 t_context 触发词的上下文信息  pos_tag 句子的词性 x_w2v 句子的word2vec特征 t_w2v 触发词的word2vec特征 c_w2v 候选词的word2vec特征
        # t_pos_tag 触发词词性   c_pos_tag 候选词词性
        return x, t, c, one_hot(y_event, Config.labels_event_size), one_hot(y_role, \
                                                                          Config.labels_role_size), pos_c, pos_t, sentences_fatures, c_context, t_context, pos_tag, \
               np.array(x_w2v), np.array(t_w2v), np.array(c_w2v), t_pos_tag, c_pos_tag


"""
测试代码 john.zhang 2016-12-22 已验证 正确
"""
datas = datasets()
print(datas.all_marks)
x, t, c, y_event, y_role, pos_c, pos_t, sentences_fatures, c_context, t_context, pos_tag, x_w2c, t_w2v, c_w2v,\
    t_pos_t, c_pos_t = datas.eval_cnn_data()
for i in range(len(x)):
    print("原始句子:{}".format(", ".join(map(lambda x: datas.all_words[x], x[i]))))
    print("词性:{}".format(", ".join(map(lambda x: datas.all_pos_taggings[x], pos_tag[i]))))
    print("触发词:{}".format(", ".join(map(lambda x: datas.all_words[x], t[i]))))
    print("候选词:{}".format(", ".join(map(lambda x: datas.all_words[x], c[i]))))
    print("事件类型：{}".format(y_event[i]))
    print("角色类别:{}".format(y_role[i]))
    print("候选词位置向量：{}".format(pos_c[i]))
    print("触发词位置向量:{}".format(pos_t[i]))
    print("候选词的上下文：{}".format(", ".join(map(lambda x: datas.all_words[x], c_context[i]))))
    print("触发词上下文词性:{}".format(", ".join(map(lambda x: datas.all_pos_taggings[x], t_pos_t[i]))))
    print("候选词上下文词性:{}".format(", ".join(map(lambda x:datas.all_pos_taggings[x], c_pos_t[i]))))
    print("触发词的上下文：{}".format(", ".join(map(lambda x: datas.all_words[x], t_context[i]))))

    context_words = map(lambda contexts: map(lambda x: datas.all_words[x], contexts), sentences_fatures[i])
    for context_word in context_words:
        print("上下文特征：{}".format(", ".join(context_word)))