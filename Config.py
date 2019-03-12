word_embedding_size = 20

labels_event_size = 2
# convert_event = {0: "非事件", 1: "会谈", 2: "股票降低类事件", 3: "股票异动类事件", 4: "股票交易类事件",
#                          5: "业绩上升类事件", 6: "业绩下滑类事件", 7: "产品涨价类事件", 8: "产品跌价类事件"
#                          }  # 事件类型准换
# eval_num = -721#训练时 使用前300条训练
eval_num = -1477#训练时 使用前300条训练
# eval_num = -1637#测试时使用所有的数据 共计549条

max_sequence_length = 100
labels_role_size = 6
# convert_role = {0: "其它角色", 1: "施事角色", 2: "受事角色", 3: "时间角色", 4: "地点角色", 5: "数字角色"}  # 角色类型转换
saveEvalFile = "train_eval_data\\testpool20190122-select-bz-jianshaoledingyu.xls"
txtfile_totrain = "train_eval_data\\datas_ace.txt"
Save_predicateMode_path = ".\\ace_cnn_model_02\modelnew\model.ckpt"