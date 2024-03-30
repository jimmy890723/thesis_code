import torch
from transformers import BertTokenizer
from transformers import BertConfig
from transformers import BertForSequenceClassification

def run(my_list):
    if torch.cuda.is_available():
        device = torch.device("cuda")    
        print('There are %d GPU(s) available.' % torch.cuda.device_count())
        print('We will use the GPU:', torch.cuda.get_device_name(0))
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")

    label_dict = {  'INFJ': 0,
                    'ENTP': 1,
                    'INTP': 2,
                    'INTJ': 3,
                    'ENTJ': 4,
                    'ENFJ': 5,
                    'INFP': 6,
                    'ENFP': 7,
                    'ISFP': 8,
                    'ISTP': 9,
                    'ISFJ': 10,
                    'ISTJ': 11,
                    'ESTP': 12,
                    'ESFP': 13,
                    'ESTJ': 14,
                    'ESFJ': 15  }

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', 
                                            do_lower_case=True)

    model = BertForSequenceClassification.from_pretrained("bert-base-uncased",
                                                        num_labels=len(label_dict),
                                                        output_attentions=False,
                                                        output_hidden_states=False)

    model.to(device)

    opt_save_dic = "../data_volume_otos/"
    model.load_state_dict(torch.load(opt_save_dic+'finetuned_BERT_epoch_8.model', map_location=torch.device('cuda')),strict=False)

    # 待分析句子
    sentence_list = my_list
    #sentence_list = ["今天下大雨，我被淋成落湯雞了，你怎麼樣?",
    #                "是說，我明天原本規畫要去爬山，不過我擔心雨會下到明天",
    #                "說得有道理，或許我可以考慮雨備，那如果是參觀博物館的話，你推薦哪一間呢?",
    #                "那你要跟我一起去嗎? 我想應該會很有趣",
    #                "這樣啊，真可惜，希望有一天我們可以一起去",
    #                "雨越下越大了，我沒帶傘該怎麼辦",
    #                "肚子也好餓，你覺得我該叫外送嗎?",
    #                "那你覺得我該吃什麼?我想吃西式餐點的，給我點建議吧",
    #                "好像很不錯欸，那我就直接下訂了，你要一起訂嗎",
    #                "真可惜，等外賣送過來了，我再跟你分享它的味道怎麼樣"]

    EI_type = 0
    SN_type = 0
    TF_type = 0
    JP_type = 0

    new_list = []

    tran_str = ""


    for n in range(len(sentence_list)):
        print(sentence_list[n])

        tran_result = sentence_list[n]
        
        print(tran_result)
        tran_str += tran_result+"\n"
        # 设置待分析的句子
        #sentence = "Hello world!"
        # 对句子进行分词和编码
        encoded_inputs = tokenizer(tran_result, padding=True, truncation=True, return_tensors="pt")
        input_ids = encoded_inputs["input_ids"].to(device)
        attention_mask = encoded_inputs["attention_mask"].to(device)

        # 将模型设置为评估模式
        model.eval()

        # 运行模型的前向传播
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            
        # 获取模型的预测结果
        logits = outputs.logits
        predicted_labels = torch.argmax(logits, dim=1)

        reversed_label_dict = {v: k for k, v in label_dict.items()}

        # 使用预测的标签索引查找相应的类型
        predicted_type = reversed_label_dict[predicted_labels.item()]

        #label_dict
        # 打印预测结果
        print("Predicted type:", predicted_type)

        new_list.append(predicted_type)

        
    opt_save_dic_entire = "../data_volume_0517_Nsoftmax_bert-base_batch_size =12/"
    model.load_state_dict(torch.load(opt_save_dic_entire+'finetuned_BERT_epoch_11.model', map_location=torch.device('cuda')),strict=False)
    #以下為entire
    encoded_inputs = tokenizer(tran_str, padding=True, truncation=True, return_tensors="pt")
    input_ids = encoded_inputs["input_ids"].to(device)
    attention_mask = encoded_inputs["attention_mask"].to(device)

    # 将模型设置为评估模式
    model.eval()

    # 运行模型的前向传播
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        
    # 获取模型的预测结果
    logits = outputs.logits
    predicted_labels = torch.argmax(logits, dim=1)

    reversed_label_dict = {v: k for k, v in label_dict.items()}

    # 使用预测的标签索引查找相应的类型
    predicted_type_entire = reversed_label_dict[predicted_labels.item()]
    print("MBTI(enetire): " + predicted_type_entire)

    return new_list, predicted_type_entire