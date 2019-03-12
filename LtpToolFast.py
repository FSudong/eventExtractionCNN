import os
import platform
from pyltp import *

class LtpToolFast:
    def __init__(self, lexicon_filepath='', display=False):
        fsd_computer = platform.node() != 'DESKTOP-OJ37RMB'
        ltp_data_dir = r'F:\Coding\ltp_data' if fsd_computer else r'C:\Users\ll\Downloads\ltp\3.4'

        self.lexicon = "F:\Coding\ltp_data\lexicon"
        # 成员函数是否直接展示结果
        self.display = display
        self.lexicon_filepath = os.path.join(ltp_data_dir, "lexicon")
        # 分词
        self.segmentor = Segmentor()
        cws_model_path = os.path.join(ltp_data_dir, 'cws.model')
        if self.lexicon_filepath != "":
            self.segmentor.load_with_lexicon(cws_model_path, self.lexicon_filepath)
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

    def structureWTER(self,old_words,old_tags,old_ners):
        words = []
        ners = []
        i = 0
        while i < len(old_words):
            if old_ners[i].find("B-N") != -1:
                sub_words = ""
                while old_ners[i].find("E-N") == -1:
                    sub_words += old_words[i]
                    i += 1
                sub_words += old_words[i]
                i += 1
                words.append(sub_words)
                ners.append("S")
            elif old_ners[i].find("S-N") != -1:
                words.append(old_words[i])
                i += 1
                ners.append("S")
            elif old_ners[i] == "O":
                words.append(old_words[i])
                i += 1
                ners.append("O")
        tags = ["n" for _ in range(len(words))]
        return words,tags,ners

    '''
    返回角色的字典形式 rolename : [1,2,3]
    '''
    def structureRole(self, words,roles):
        role_dict = {}
        role_dict["A0"] = []
        role_dict["A1"] = []
        role_dict["LOC"] = []
        role_dict["TMP"] = []
        for role in roles:
            for arg in role.arguments:
                role_dict[arg.name] = list(map(lambda x : words[x], range(arg.range.start,arg.range.end+1)))
        return role_dict
