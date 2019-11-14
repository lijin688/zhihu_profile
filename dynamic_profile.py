import requests
import re
import json
import jieba
import matplotlib.pyplot as plt
from scipy.misc import imread
from wordcloud import WordCloud,ImageColorGenerator
from collections import Counter
import urllib.parse

class Profile:
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        # 'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
        "Cookie": '_zap=74789ddd-d211-40fa-9603-6be4eb6acf27; d_c0="APApdRSBjQ-PTmc7mHk2QB0qxpiVOlyzgTM=|1559974225"; __gads=ID=39c4019f328d13e3:T=1561860512:S=ALNI_MZxdbK8H3NM9ZG5wPCKXb8LxqzPxg; _xsrf=a05a473b-5fb0-4b1a-af5d-7954dbcf8395; capsion_ticket="2|1:0|10:1571792460|14:capsion_ticket|44:OTkyMzE2NGViNzRhNGM5ODgwODIwNmNiMTA1NDVhYzc=|61619374d97c214c0d78c84cc1e111cbd12a5e5d0ba577439145e089d3950052"; z_c0="2|1:0|10:1571792507|4:z_c0|92:Mi4xNDJPQUF3QUFBQUFBOENsMUZJR05EeVlBQUFCZ0FsVk5lX1NjWGdBQ0tBRG9kQ2x3NFliNEM5QU5UTDdyVlZCaF93|fcdd0200ce5a89b5ecce4e608220310e350e7802b475c210038ba4db18b5c46c"; q_c1=22c596ec323a4e41838fd1b7796b1130|1571798584000|1559974226000; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1572589288,1572589695,1572590046,1572593679; tst=f; tgw_l7_route=060f637cd101836814f6c53316f73463; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1572830596'
    }
    def __init__(self, user_token):
        self.user_token = user_token
        self.followee_token_list = []
        self.answer_list = []  # 回答列表
        self.article_list = []  # 发表文章列表
        self.vote_list = []  # 赞同回答+赞同文章列表
        self.column_follow = []  # 关注专栏列表
        self.question_list = []  # 创建问题列表
        self.question_list_number = 0
        self.question_follow = []  # 关注问题列表
        self.question_follow_number = 0
        self.topic_follow = []  # 关注话题列表
        self.topic_follow_number = 0
        self.collect_follow = []  # 关注收藏夹列表
        self.collect_follow_number = 0
        self.livejoin_list = []  # 参加的live列表

    def get_followee_user_token(self):
        followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include=data[*].answer_count,articles_count,gender,' \
                        'follower_count,is_followed,is_following,badge[?(type=best_answerer)].' \
                        'topics&offset={offset}&limit=20'
        url = followees_url.format(user=self.user_token, offset=0)
        r = requests.get(url, headers=self.header)
        results = json.loads(r.text)
        print(results)
        total = results['paging']['totals']
        page = total // 20
        for p in range(page):
            url = followees_url.format(user=self.user_token, offset=p*20)
            r = requests.get(url, headers=self.header)
            results = json.loads(r.text)
            # print(results)
            for result in results['data']:
                self.followee_token_list.append(result['url_token'])
        # print(self.followee_token_list)
        return self.followee_token_list

    def get_content(self, url=None, token_list=None, limit=5):
        for token in token_list:
            url = 'https://www.zhihu.com/api/v4/members/{user_token}/activities?limit=10&desktop=True'.format(
                user_token=token) if url is None else url
            i = 1
            while True:
                r = requests.get(url, headers=self.header)
                content = json.loads(r.text)
                self.parse_content(content)
                if content['paging']['is_end'] is False:
                    url = content['paging']['next']
                else:
                    break
                i += 1
                if limit is not None and i > limit:
                    break

    def parse_content(self, result):
        for d in result['data']:
            print(d['verb'])
            if d['verb'] == 'ANSWER_CREATE':
                content = re.sub('<.*?>', '', d['target']['content'])
                # print(content)
                self.answer_list.append([d['target']['question']['title'], content])
            elif d['verb'] == 'MEMBER_CREATE_ARTICLE':
                content = re.sub('<.*?>', '', d['target']['content'])
                # print(content)
                self.article_list.append([d['target']['title'], content])
            elif d['verb'] == 'QUESTION_CREATE':
                print(d['target']['title'])
                self.question_list.append(d['target']['title'])
                self.question_list_number += 1
            elif d['verb'] == 'ANSWER_VOTE_UP':
                content = re.sub('<.*?>', '', d['target']['content'])
                print(d['target']['question']['title'])
                # print(content)
                self.vote_list.append([d['target']['question']['title'], content])
            elif d['verb'] == 'QUESTION_FOLLOW':
                print(d['target']['title'])
                self.question_follow.append(d['target']['title'])
                self.question_follow_number += 1
            elif d['verb'] == 'TOPIC_FOLLOW':
                print(d['target']['name'])
                self.topic_follow.append(d['target']['name'])
                self.topic_follow_number += 1
            elif d['verb'] == 'MEMBER_VOTEUP_ARTICLE':
                content = re.sub('<.*?>', '', d['target']['content'])
                print(d['target']['title'])
                # print(content)
                self.vote_list.append([d['target']['title'], content])
            elif d['verb'] == 'MEMBER_FOLLOW_COLUMN':
                print(d['target']['title'])
                self.column_follow.append(d['target']['title'])
            elif d['verb'] == 'MEMBER_FOLLOW_COLLECTION':
                print(d['target']['title'])
                self.collect_follow.append(d['target']['title'])
                self.collect_follow_number += 1
            elif d['verb'] == 'LIVE_JOIN':
                print(d['target']['subject'])
                self.livejoin_list.append(d['target']['subject'])

    def predict(self, info_type, content_list):
        if len(content_list):
            wordlist = []
            back_coloring = imread("mybg.jpg")
            stopwords = {}.fromkeys([line.rstrip() for line in open('stopwords.txt', 'r', encoding='utf-8')])  # 停用词词表
            cloud = WordCloud(font_path='font.ttf',  # 若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
                              background_color="white",  # 背景颜色
                              # max_words=2000,  # 词云显示的最大词数
                              mask=back_coloring,  # 设置背景图片
                              max_font_size=100,  # 字体最大值
                              random_state=42,
                              width=1000, height=860, margin=2,
                              # 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                              )
            for content in content_list:
                if type(content) is list:
                    for c in content:
                        wordlist += jieba.cut(c, cut_all=False)
                else:
                    wordlist += jieba.cut(content, cut_all=False)
            word_list_new = [w for w in wordlist if w not in stopwords]
            wordstr = (',').join(word_list_new)
            wc = cloud.generate(wordstr)
            image_colors = ImageColorGenerator(back_coloring)
            plt.figure("wordc")
            plt.imshow(wc.recolor(color_func=image_colors))
            wc.to_file('{}的{}词云.png'.format(self.user_token, info_type))
            worddict = Counter(word_list_new)
            print('{}的{}词频：\n{}'.format(self.user_token, info_type, worddict.most_common(20)))


if __name__ == '__main__':
    user = Profile('reseted1502783493')  # 指定分析对象
    user_token_list = user.get_followee_user_token()  # 获取所有的关联用户
    user.get_content(token_list=user_token_list[:7])  # 可限定关联用户的数量
    user.predict('回答问题', user.answer_list)
    # user.predict('创建问题', user.question_list)
