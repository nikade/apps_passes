import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests import Response
from PassReportItem import PassReportItem
from exceptions import LoginException, UnknownResponseException


class AppsWebClient:

    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._ssss = requests.Session()
        self.childs = {}

        self.do_login()


        self.get_childrens()

    def do_login(self):
        logging.info("Логин начало")
        auth_response = self._ssss.post(url="https://apps-inform.ru/Account/Login",
                                        data={'login': self._login, 'password': self._password, 'rememberme': 'false'})
        if auth_response.status_code != 200:
            return LoginException(f"Неверный status_code={auth_response.status_code}")
        login_result = json.loads(auth_response.text.replace('\\\"', '"')[1:-1])
        succeed = login_result.get('succeed') or None
        if succeed != 'True':
            raise LoginException(json)
        logging.info("Логин успешно")

    def get_childrens(self):
        logging.info("Получение детей")
        profile_response = self._ssss.get("https://apps-inform.ru/profile")
        if profile_response.status_code != 200:
            raise UnknownResponseException
        profile = BeautifulSoup(profile_response.text,features="lxml")
        child_elements = profile.find('select', id='ChildrenListForm').find_all('option')
        self.childs = dict((x.attrs['value'], x.text) for x in child_elements)
        if len(self.childs) != 0:
            logging.info("Получение детей успешно")
            return
        raise Exception("Детей нет")

    def do_authed_get_request(self, url: str, data: dict):
        res: Response = self._ssss.get(url=url, data=data)
        if res.status_code != 200 or res.text == '':
            if not self.do_login():
                raise LoginException
            res = self._ssss.get(url=url, data=data)
        if res.status_code != 200 or res.text == '':
            raise UnknownResponseException
        return res.text

    def get_passing(self, child_id: int, date_begin: datetime, date_end: datetime):
        logging.info("Получение отчета")
        text = self.do_authed_get_request(url="https://apps-inform.ru/Profile/GetPassing",
                                          data={'PersonalID': child_id,
                                                'datestart': date_begin.strftime('%d-%m-%Y'),
                                                'dateend': date_end.strftime('%d-%m-%Y')})
        all_img = BeautifulSoup(text[7::],features="lxml").find_all('img')
        last_year = date_end.year
        logging.info("Получение отчета успшено")
        return list(
            PassReportItem(
                datetime.strptime(
                    r.parent.parent.find('td', style='text-align: center;')
                      .text +'.'+str(last_year) + ' ' + str(r.next_sibling).rstrip(),
            '%d.%m.%Y %H:%M:%S'),
                r.attrs['src'].endswith('in.png')
            )
            for r in all_img)


# https://apps-inform.ru/Profile/GetPassing?PersonalID=3802811&datestart=09-10-2024&dateend=09-10-2024
