# %%
from collections import Counter

import pymongo as mo
import re
import pandas as pd
import pandas as pd
import jieba
import jieba.posseg as psg
from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# %%
client = mo.MongoClient("mongodb://localhost:27017/")
db = client["eastmoneys_news"]
collection = db["shuzi_new"]


# %%
def clear_str(str_raw:str):
    for pat in ['\\n', ' ', ' ', '\r', '\\xa0', '\n\r\n','\n','查看详情>>\n\n\n','\t','$','\\\u3000','主力资金加仓名单实时更新，APP内免费看>>','（文章来源：([\u4e00-\u9fa5]+·[\u4e00-\u9fa5]+)）']:
        str_raw.replace(pat,'')
        str_raw = re.sub(fr'{pat}','',str_raw)
    # str_raw.replace('查看详情>>\\n\\n\\n','')
    return str_raw

def concatenate_columns(row, column1, column2):
    
        return row[column1] + row[column2]

# %%
datas = collection.find()
title_set = set()
finaldata_list = []
for data in datas:
    if data['title'] not in title_set:
        title_set.add(data['title'])
        try:
            if '惠博普' not in data['title']:
                data['body'] = clear_str(data['body'])
                finaldata_list.append(data)
        except:continue
        # print(data['title'])
    else:
        print(data['title'])
        

# %%
# 数据清洗函数
stop_file = 'E:\财经新闻爬虫\cn_stopwords.txt'
stopword_list = open(stop_file,encoding ='utf-8')
stop_list = []
other_stop = ['普惠','数字','金融']
for line in stopword_list:
    line = re.sub(u'\n|\\r', '', line)
    stop_list.append(line)
stop_list.extend(other_stop)

# %%
# 数据准备
data_frame = pd.DataFrame(finaldata_list)
data_frame = data_frame.dropna(how='any')
data_frame['total_content'] = data_frame.apply(lambda row: concatenate_columns(row, 'title', 'body'), axis=1)

# %%
# 总的词云生成函数
from PIL import Image
import numpy as np
def generate_wordcloud_gernel(words):
    word_counter = Counter(words)
    mask_path = 'E:\财经新闻爬虫\cloud.png'
    mask = np.array(Image.open(mask_path))
    plt.figure(figsize=(10, 6))
    font_path = 'E:\财经新闻爬虫\shangshouqingbaiti.ttf'
    wordcloud = WordCloud(font_path=font_path,background_color='white',mask=mask,max_words=100)
    wordcloud.generate_from_frequencies(word_counter)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('wordcloud.png', dpi=600)
    plt.show()

# %%
import jieba.posseg as pseg
test = '需要'
a = pseg.cut(test)
for c,d in a:
    print(c,d)

# %%
def chinese_word_cut(sentence):
    word_list = []
    #jieba分词
    seg_list = jieba.lcut(sentence)
    for seg_word in seg_list:
        # word = re.sub(u'[^\u4e00-\u9fa5]','')
        if seg_word not in stopword_list and len(seg_word)>1:
            word_list.append(seg_word)
       
    return (" ").join(word_list)

# def chinese_word_cut2(sentence):
#     words = pseg.cut(sentence)
#     for seg_word,pos in words:
#         if pos in ['n','v','adj']
#             if seg_word not in stopword_list and len(seg_word)>1:
            


# %%
data_frame['content_cutted'] = data_frame['total_content'].apply(chinese_word_cut)
tf_vectorizer = CountVectorizer(strip_accents = 'unicode',
                                # max_features=n_features,
                                stop_words='english',
                                max_df = 0.5,
                                min_df = 10)
tf = tf_vectorizer.fit_transform(data_frame.content_cutted)

# %%
n_topics = 8
lda = LatentDirichletAllocation(n_components=n_topics, max_iter=50,
                                learning_method='batch',
                                learning_offset=50,
#                                 doc_topic_prior=0.1,
#                                 topic_word_prior=0.01,
                               random_state=0)
lda.fit(tf)
vec_lda = lda.transform(tf)

# %%
import os 
path_result = 'E:\财经新闻爬虫\lda_result2'

# %%
def print_top_words(model, feature_names, n_top_words):
    tword = []
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        topic_w = " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        tword.append(topic_w)
        
        print(topic_w)
    return tword

# %%
def generate_wordcloud(words, importance,path,topic_number):
    wordcloud_data = {word: importance[idx] for idx, word in enumerate(words)}
    font_path = 'D:\\texlive\\2022\\texmf-dist\\fonts\\truetype\public\\arvo\Arvo-Bold.ttf'
    font_path = 'E:\财经新闻爬虫\shangshouqingbaiti.ttf'
    
    wordcloud = WordCloud(font_path=font_path,background_color='white',max_words=50)
    wordcloud.generate_from_frequencies(wordcloud_data)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    final_path = os.path.join(path,f'topic{topic_number}.png')
    plt.savefig(final_path,dpi=300)
    plt.show()
    plt.close()

# %%
tf_feature_names = tf_vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    print(topic_idx)
    generate_wordcloud(list(tf_feature_names),list(topic))

# %%
def write_list_to_txt(lst, filename):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, 'w') as file:
        i = 0
        for item in lst:
            file.write(f'#topic{i}'+ '\n')
            file.write(str(item) + '\n')
            i+=1
    print(f"Data written to {filename} successfully.")

# %%
for  n_topics  in range(3,15):
    topic_path = os.path.join(path_result,str(n_topics))
    if not os.path.exists(topic_path):
            os.makedirs(topic_path)
    lda = LatentDirichletAllocation(n_components=n_topics, max_iter=50,
                                    learning_method='batch',
                                    learning_offset=50,
    #                                 doc_topic_prior=0.1,
    #                                 topic_word_prior=0.01,
                                random_state=0)
    lda.fit(tf)
    vec_lda = lda.transform(tf)

    n_top_words = 25
    tf_feature_names = tf_vectorizer.get_feature_names_out()
    topic_word = print_top_words(lda, tf_feature_names, n_top_words)
    topic_text_path = os.path.join(topic_path,'topic.txt')
    write_list_to_txt(topic_word,topic_text_path)

    topics=lda.transform(tf)
    topic = []
    for t in topics:
        topic.append("Topic #"+str(list(t).index(np.max(t))))

    data_frame['概率最大的主题序号']=topic
    data_frame['每个主题对应概率']=list(topics)
    excel_path = os.path.join(topic_path,'data_topic.xlsx')
    data_frame.to_excel(excel_path,index=False)

    for topic_idx, topic in enumerate(lda.components_):
        
        generate_wordcloud(list(tf_feature_names),list(topic),path=topic_path,topic_number=topic_idx)
    

# %%
topic_word

# %%
# 全部词云生成
total_word_list = []
for index,row in data_frame.iterrows():
    seg_list = jieba.lcut(row['total_content'])
    for seg_word in seg_list:
        if (seg_word not in stop_list) and len(seg_word)>1 :
            total_word_list.append(seg_word)
generate_wordcloud_gernel(total_word_list)

# %%
lda.components_.shape

# %%
plexs = []
scores = []
n_max_topics = 16
for i in range(1,n_max_topics):
    print(i)
    lda = LatentDirichletAllocation(n_components=i, max_iter=50,
                                    learning_method='batch',
                                    learning_offset=50,random_state=0)
    lda.fit(tf)
    plexs.append(lda.perplexity(tf))
    scores.append(lda.score(tf))

# %%
n_t=15#区间最右侧的值。注意：不能大于n_max_topics
x=list(range(1,n_t+1))
plt.plot(x,plexs[0:n_t])
plt.xlabel("number of topics")
plt.ylabel("perplexity")
plt.show()

# %%
topics=lda.transform(tf)
topic = []
for t in topics:
    topic.append("Topic #"+str(list(t).index(np.max(t))))
data_frame['概率最大的主题序号']=topic
data_frame['每个主题对应概率']=list(topics)
data_frame.to_excel("data_topic.xlsx",index=False)

# %%
from collections import Counter
def plot_proj(embedding, lbs):
    """
    Plot UMAP embeddings
    :param embedding: UMAP (or other) embeddings
    :param lbs: labels
    """
    n = len(embedding)
    counter = Counter(lbs)
    for i in range(len(np.unique(lbs))):
        plt.plot(embedding[:, 0][lbs == i], embedding[:, 1][lbs == i], '.', alpha=0.5,
                 label='cluster {}: {:.2f}%'.format(i, counter[i] / n * 100))
    plt.legend()

def visualize(final_vec,culster_model):
    """
    Visualize the result for the topic model by 2D embedding (UMAP)
    :param model: Topic_Model object
    """

    reducer = umap.UMAP()
    print('Calculating UMAP projection ...')
    vec_umap = reducer.fit_transform(final_vec)
    # vec_umap = pca_2d(final_vec)
    # print('Calculating UMAP projection. Done!')
    plot_proj(vec_umap,culster_model.labels_)
    # dr = '/contextual_topic_identification/docs/images/{}/{}'.format(model.method, model.id)
    # if not os.path.exists(dr):
    #     os.makedirs(dr)
    # plt.savefig(dr + '/2D_vis')

# %%
def plot_proj(embedding, lbs):
    """
    Plot UMAP embeddings
    :param embedding: UMAP (or other) embeddings
    :param lbs: labels
    """
    n = len(embedding)
    counter = Counter(lbs)
    for i in range(len(np.unique(lbs))):
        plt.plot(embedding[:, 0][lbs == i], embedding[:, 1][lbs == i], '.', alpha=0.5,
                 label='cluster {}: {:.2f}%'.format(i, counter[i] / n * 100))
    plt.legend()

def visualize(final_vec,bert_name,cluster_method,gamma):
    """
    Visualize the result for the topic model by 2D embedding (UMAP)
    :param model: Topic_Model object
    """

    reducer = umap.UMAP()
    print('Calculating UMAP projection ...')
    vec_umap = reducer.fit_transform(final_vec)
    for num_group in range(3,10):
    # for num_group in[5]:    
        clu_model = AE2cluster(final_vec,num_group=num_group,method=cluster_method)   
        plot_proj(vec_umap,clu_model.labels_)
        dr = os.path.join(culster_result_path,bert_name[4:],cluster_method.__name__)
        if not os.path.exists(dr):
            os.makedirs(dr)
        plt.savefig(os.path.join(dr,f'{gamma}_{num_group}.png'))
        plt.savefig(os.path.join(dr,f'bert.png'))
        plt.close()


