## 来源
基本都为以下项目中代码，请移步至原作者项目
[https://github.com/zhangluoyang/cnn-for-auto-event-extract.git](https://github.com/zhangluoyang/cnn-for-auto-event-extract.git)

## Suggestions  

Sorry, the data was in my last compute. However, the computer's disk was destroyed. So the paths below are recommended.  
1、Read the part which loads data, and you will finally inference what the data should be like.  
2、Ask the author for help. His github link was given in Readme.md  
3、Give up. according to my experience, this code does not preform well .   

## 运行环境  
python 3.6 + pyltp

## 运行过程
1、需修改 multi_task_test_w2v.py 中327 349 if 语句 和 Config中训练数据条数。以切换训练及测试模式


## TODO
- [ ] 语句分词结果影响训练结果，直接决定了哪些是candidate
- [ ] 语句最大长度
- [ ] 训练集 非目标事件类型，触发词默认为 依存关系的head
- [ ] 中文词向量使用方法 ：加载至模型
- [ ] 词性嵌入：目前是随机的向量
