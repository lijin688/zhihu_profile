import json
import re
from crawl_zhihu.zhihu.items import ZhihuFolloweeItem, ZhihuDynamicItem
from scrapy import Spider,Request


class ZhihuSpider(Spider):
    name='zhihu_spider'
    allowed_domains = ["www.zhihu.com"]
    start_urls = ["https://www.zhihu.com/"]
    target_user_token = "reseted1502783493"
    user_include = 'locations'

    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include=data[*].answer_count,articles_count,gender,' \
                    'follower_count,is_followed,is_following,badge[?(type=best_answerer)].' \
                    'topics&offset={offset}&limit=20'.format(user=target_user_token, offset=0)
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'.format(user=target_user_token, include=user_include)
    #可选内容：locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics
    # dynamic_url = 'https://www.zhihu.com/api/v4/members/' + target_user_token + '/activities?limit=10&desktop=True'

    def start_requests(self):
        yield Request(self.followees_url, callback=self.parse_fo)
        yield Request(self.user_url, callback=self.parse_user)
        # yield Request(self.dynamic_url, callback=self.parse_user)


    def parse_user(self, response):
        result = json.loads(response.text)
        print(result)
        item = ZhihuFolloweeItem()
        item['user_name'] = result['name']
        item['sex'] = result['gender']  # gender为1是男，0是女，-1是未设置
        item['user_sign'] = result['headline']
        item['user_avatar'] = result['avatar_url_template'].format(size='xl')
        item['user_url'] = 'https://www.zhihu.com/people/' + result['url_token']
        if len(result['locations']):
            item['user_add'] = result['locations'][0]['name']
        else:
            item['user_add'] = ''
        yield item

    def parse_dynamic(self, response):
        result = json.loads(response.text)

        for d in result['data']:
            print(d['verb'])
            if d['verb'] == 'ANSWER_CREATE':
                content = re.sub('<.*?>', '', d['target']['content'])
                title = d['target']['question']['title']

        item = ZhihuFolloweeItem()
        item['user_name'] = result['name']
        item['sex'] = result['gender']  # gender为1是男，0是女，-1是未设置
        item['user_sign'] = result['headline']
        item['user_avatar'] = result['avatar_url_template'].format(size='xl')
        item['user_url'] = 'https://www.zhihu.com/people/' + result['url_token']
        if len(result['locations']):
            item['user_add'] = result['locations'][0]['name']
        else:
            item['user_add'] = ''
        yield item

    def parse_fo(self, response):
        results = json.loads(response.text)
        for result in results['data']:
            yield Request(self.user_url.format(user=result['url_token'], include=self.user_include),callback=self.parse_user)
            if result['url_token'] != self.target_user_token:
                yield Request(self.followees_url.format(user=result['url_token'], offset=0),callback=self.parse_fo)  # 对关注者的关注者进行遍历，爬取深度depth+=1
            else:
                pass
        if results['paging']['is_end'] is False: #关注列表页是否为尾页
            next_url = results['paging']['next'].replace('http','https')
            yield Request(next_url,callback=self.parse_fo)
        else:
            pass

