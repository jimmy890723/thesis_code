import torch
from googletrans import Translator
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

    opt_save_dic = "data_volume_0517_Nsoftmax_bert-base_batch_size =12/"
    model.load_state_dict(torch.load(opt_save_dic+'finetuned_BERT_epoch_11.model', map_location=torch.device('cuda')),strict=False)

    # 待分析句子
    sentence_list = my_list
    #sentence_list = ["你覺得進擊的巨人",
    #                "我可以明年就畢業嗎",
    #                "碩班好累，好想休",
    #                "我的積分什麼時候才能爬上去",
    #                "幫我推一支股票，好想賺錢",
    #                "今天練完球晚餐要吃甚麼",
    #                "宵夜要吃什麼",
    #                "張小P什麼時候要放過我 痾合"]

    tran_str = ""
    #中轉英
    translator = Translator(service_urls=['translate.google.com'])
    for n in range(len(sentence_list)):
        print(sentence_list[n])

        
        translation = translator.translate(sentence_list[n], dest='en')
        tran_result = translation.text
    
        print(tran_result)
        tran_str += tran_result+"\n"
        # 设置待分析的句子
        #sentence = "Hello world!"
        # 对句子进行分词和编码
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
    predicted_type = reversed_label_dict[predicted_labels.item()]

    #label_dict
    # 打印预测结果
    print("Predicted type (entire):", predicted_type)
    
    return predicted_type

run()