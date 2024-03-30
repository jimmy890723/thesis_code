import torch
import pandas as pd
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.nn.utils.rnn import pad_sequence
from sklearn.model_selection import train_test_split
import torch.nn.functional as F
from sklearn import svm
import joblib 

def run(my_list):
    print(type(my_list))
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

    # 資料載入和轉換 

    mbti_counts = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0}
    mbti_per_count = []

    dialogue_ids = [label_dict[personality] for personality in my_list]
        
    for personality_id in dialogue_ids:
        mbti_counts[personality_id] += 1
        
    for i in range(len(label_dict)):
        mbti_per_count.append(round(mbti_counts[i]/len(dialogue_ids), 2))

    # 轉換為張量   
    input_data = torch.tensor(mbti_per_count, dtype=torch.float32)    

    #只有一個樣本（sample），但被解釋為1D陣列，因此要轉為2D
    input_data = input_data.reshape(1, -1)
    
    model_filename_SVM = 'C:/Users/JenMing/Desktop/MBTI/SVM/svm_model.pkl'
    #model_filename_SVM = 'C:/Users/JenMing/Desktop/MBTI/SVM/kernel=rbf C=0.5/svm_model.pkl'
    #model_filename_SVM = 'C:/Users/JenMing/Desktop/MBTI/SVM/train_by1/svm_model.pkl'

    # 加载SVM模型
    loaded_svm_model = joblib.load(model_filename_SVM)

    # 使用加载的模型进行预测
    loaded_predicted_labels = loaded_svm_model.predict(input_data)

    # 创建反向映射
    reverse_personality_mapping = {v: k for k, v in label_dict.items()}

    # 使用反向映射将数字转换为对应的个性
    personality_SVM = reverse_personality_mapping.get(int(loaded_predicted_labels), "Unknown")

    print("By SVM MBTI: " + personality_SVM)
    
    #--- ELM ---
    # 定義 sigmoid 函數
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
        
    # 保存ELM模型
    model_filename_ELM = 'C:/Users/JenMing/Desktop/MBTI/ELM/elm_model.pkl'
    #model_filename_ELM = 'C:/Users/JenMing/Desktop/MBTI/ELM/n_del_hidden_size = 25/elm_model.pkl'

    # 載入 ELM 模型
    loaded_elm_model = joblib.load(model_filename_ELM)
    
    # 使用載入的模型進行預測
    input_data_np = input_data.numpy()
    hidden_activations_test = sigmoid(np.dot(input_data_np, loaded_elm_model['input_weights']) + loaded_elm_model['biases'])
    y_pred = np.dot(hidden_activations_test, loaded_elm_model['output_weights'])
    predicted_labels = np.argmax(y_pred, axis=1)
    # 使用反向映射将数字转换为对应的个性
    personality_ELM = reverse_personality_mapping.get(int(predicted_labels), "Unknown")

    print("By ELM MBTI: " + personality_ELM)

    #---Random Forest---
    # 保存Random Forest參數
    model_filename_RF = 'C:/Users/JenMing/Desktop/MBTI/random_forest/RF_model.pkl'
    #model_filename_RF = 'C:/Users/JenMing/Desktop/MBTI/random_forest/RF_1/RF_model.pkl'
    
    # 從文件載入模型
    loaded_model_RF = joblib.load(model_filename_RF)

    # 使用載入的模型進行預測
    personality_RF_list = loaded_model_RF.predict(input_data_np)
     # 使用反向映射将数字转换为对应的个性
    personality_RF = reverse_personality_mapping.get(int(personality_RF_list), "Unknown")

    print("By Random Forest MBTI: " + personality_RF)

    personality = ""
    # 确保三个字符串长度相同，如果不同可以根据需求进行适当处理
    if len(personality_SVM) != len(personality_ELM) or len(personality_ELM) != len(personality_RF):
        print("MBTI字串長度不相同\n")
    else:
        for i in range(len(personality_ELM)):
            if personality_SVM[i] == personality_ELM[i] or personality_RF[i] == personality_ELM[i]:
                personality += personality_ELM[i]
            else:
                personality += personality_SVM[i]

    print("\nFinal MBTI: " + personality)

    return personality