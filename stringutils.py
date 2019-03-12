def getMaxCommonSubstr(s1, s2):
    # 求两个字符串的最长公共子串
    # 思想：建立一个二维数组，保存连续位相同与否的状态

    len_s1 = len(s1)
    len_s2 = len(s2)

    # 生成0矩阵，为方便后续计算，多加了1行1列
    # 行: (len_s1+1)
    # 列: (len_s2+1)
    record = [[0 for i in range(len_s2 + 1)] for j in range(len_s1 + 1)]

    maxNum = 0  # 最长匹配长度
    p = 0  # 字符串匹配的终止下标

    for i in range(len_s1):
        for j in range(len_s2):
            if s1[i] == s2[j]:
                # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1

                if record[i + 1][j + 1] > maxNum:
                    maxNum = record[i + 1][j + 1]
                    p = i  # 匹配到下标i

    # 返回 子串长度，子串
    return maxNum, s1[p + 1 - maxNum: p + 1]


def printMatrixList(li):
    # 打印多维list
    row = len(li)
    col = len(li[0])

    for i in range(row):
        for j in range(col):
            print(li[i][j], end=' ')
        print('')

def getSimilar(s1,s2):
    [lenMatch, strMatch] = getMaxCommonSubstr(s1, s2)
    lenth = len(s2) if len(s1) > len(s2) else len(s1)
    if lenth == 0:
        return False
    sim = lenMatch / lenth
    if sim > 0.4:
        return True
    else:
        return False

if __name__ == "__main__":

    # s1="黑猫英语名著3级 02 Alic's Adventures In Wonderland 艾丽丝漫游奇境记.pdf"
    # s2="艾丽丝漫游奇境记 Alic_s Adventures In Wonderland 01.mp3"
    s1='abcdef'
    s2='bcxdef'
    [lenMatch,strMatch] = getMaxCommonSubstr(s1,s2)
    print('子串: ', strMatch)
    print('子串长度: ', lenMatch)
