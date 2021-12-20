import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from instaparser.items import InstaparserItem
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'it.bokolyar'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1639925421:AYNQAIfEN2+sT/oi0d8feL98BgR9CEerQU0l7fOV0/c25+12MIRIkAJMM7TRrlPDzFfO46VOGx2+fxtaNck8R+bIunQsqEBxNe8axFaCodsbCvxwk0jOFNi9NgVxzlWT8HX6MVRfrxjgOYSCK4Sp'
    users = ['eborzik', 'bokolyarkonstantin', 'siurprizansambl', '__.lm.nastya.__']
    #users = ['bokolyarkonstantin', 'tennisclub_volghanin', 'hulia_bokolyar']

    inst_friendship_link = 'https://i.instagram.com/api/v1/friendships/'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pwd},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(
                    f'/{user}/',
                    callback=self.user_friendships,
                    cb_kwargs={'username': user}
                )

    def user_friendships(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        params_followers = {'count': 12, 'search_surface': 'follow_list_page'}
        params_followings = {'count': 12}
        variables_followers = f'{user_id}/followers/?{urlencode(params_followers)}'
        variables_followings = f'{user_id}/following/?{urlencode(params_followings)}'
        url_followers = f'{self.inst_friendship_link}{variables_followers}'
        url_followings = f'{self.inst_friendship_link}{variables_followings}'

        headers = {'User-Agent': 'Instagram 155.0.0.37.107'}

        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            headers=headers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'params': deepcopy(params_followers)}
        )

        yield response.follow(
            url_followings,
            callback=self.user_followings_parse,
            headers=headers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'params': deepcopy(params_followings)}
        )

    def user_followers_parse(self, response: HtmlResponse, username, user_id, params):
        j_data = response.json()
        next_max_id = j_data.get('next_max_id')
        if next_max_id:
            params['max_id'] = next_max_id
            variables_followers = f'{user_id}/followers/?{urlencode(params)}'
            headers = {'User-Agent': 'Instagram 155.0.0.37.107'}
            url_followers = f'{self.inst_friendship_link}{variables_followers}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                headers=headers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'params': deepcopy(params)}
            )
        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                type='follower',
                username=username,
                user_id=user_id,
                f_username=user.get('username'),
                f_user_id=user.get('pk'),
                f_user_photo=user.get('profile_pic_url')
            )
            yield item

    def user_followings_parse(self, response: HtmlResponse, username, user_id, params):
        j_data = response.json()
        next_max_id = j_data.get('next_max_id')
        if next_max_id:
            params['max_id'] = next_max_id
            variables_followings = f'{user_id}/following/?{urlencode(params)}'
            headers = {'User-Agent': 'Instagram 155.0.0.37.107'}
            url_followings = f'{self.inst_friendship_link}{variables_followings}'
            yield response.follow(
                url_followings,
                callback=self.user_followings_parse,
                headers=headers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'params': deepcopy(params)}
            )
        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                type='following',
                username=username,
                user_id=user_id,
                f_username=user.get('username'),
                f_user_id=user.get('pk'),
                f_user_photo=user.get('profile_pic_url')
            )
            yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')
