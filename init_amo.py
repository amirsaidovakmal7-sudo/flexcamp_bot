from config import *
import requests
import os
from datetime import datetime
import time
from requests.exceptions import JSONDecodeError
import jwt
import dotenv
from dotenv import load_dotenv
from database.access_token_service import *
from database.refresh_token_service import *



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(BASE_DIR, ".env")


TG_USERNAME_ID = 1897829
RESPONSIBLE_USER_ID = 33083426




secret_code = 'def502009bf47712257ec69a809758f420c713ff8052c18b6f3ae79497dc89404e442f0e0f90f785584ed52215a00f3eb1336d0b02757fecf209bd3a550b6d89ecbb01b163050ec9e1146a230db7878f6d79d0852b68f981f728fb2bb74443dca44f9988cae0cd9171d9da9cf454717fb20ed87501ff786deb9e1adf323ce1170d80d6471ee1de391cd584895821dc507064da41c46eeeeafe687fc3917d8b2ed65bb59941f257e2b3ce58cb8e6b8d6d6320b94077b09419e58687e3004a7e2c49ad29976281acf47690ebc30e7e3757de61981a8668549db6ce077db7e5b50bc840f7a6af669fabc301e968332433ab6a4ec5e769a07f9e5b0e964ded87c6cb2fef7c2d04ddb696fa6f86048ee8bc12733430f967d76b058ebf047dd69346a4116ca1cee472e6836b3c909204d163d8d92c8e21932a3a8a2c99c089339b61830352c2b5c27ff7dc2a04ae4cc62588726e5d31dd407838d34c3e6e201f0f6179a422f55b71fb0aa3af28e1fe411d9a55149bdeffd4a14fd356288b769aa5059bc41f0d2d1a9d19218d93f05384cf9a4efb800e6dee4f7df1d06f5ad2d2431cf1411e335cd6088249c476f4e778a7330214b453d12b8dfb2973f7306d91b1b16d6eca73615309c8c47291b121db644c5ff4a5cac9e0b466304ec9bfcf209ff8ac4a23351e'



def _is_expire(token):
    if isinstance(token, str):
        token = token.encode('utf-8')
    token_data = jwt.decode(token, options={"verify_signature": False})
    exp = datetime.utcfromtimestamp(token_data['exp'])
    now = datetime.utcnow()

    return now >= exp


def save_tokens(access_token, refresh_token):
    try:
        update_access_token_bd(access_token)
        update_refresh_token_bd(refresh_token)
        return True
    except Exception as e:
        return e





def get_access_token():
    return get_access_token_bd()


def get_refresh_token():
    return get_refresh_token_bd()


def get_new_tokens():
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': get_refresh_token(),
        'redirect_uri': REDIRECT_URI,

    }
    response = requests.post('https://{}.amocrm.ru/oauth2/access_token'.format(SUBDOMAIN),
                             json=data).json()
    print(response)
    access_token = response['access_token']
    refresh_token = response['refresh_token']

    save_tokens(access_token, refresh_token)


class AmoCRMWrapper:
    def init_oauth2(self):
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': "authorization_code",
            'code': secret_code,
            'redirect_uri': REDIRECT_URI
        }
        response = requests.post('https://{}.amocrm.ru/oauth2/access_token'.format(SUBDOMAIN),
                                 json=data).json()

        print(response)
        access_token = response['access_token']
        refresh_token = response['refresh_token']

        result = save_tokens(access_token, refresh_token)

        print(f'РЕЗУЛЬТАТ: {result}, {type(result)}')




    def base_request(self, **kwargs):
        if _is_expire(get_access_token()):
            get_new_tokens()
        access_token = f"Bearer {get_access_token()}"

        headers = {
            "Authorization": access_token
        }
        req_type = kwargs.get('type')
        response = ""
        if req_type == "get":
            try:
                response = requests.get("https://{}.amocrm.ru{}".format(
                    SUBDOMAIN, kwargs.get("endpoint")), headers=headers).json()
            except JSONDecodeError as e:
                return e

        elif req_type == "get_param":
            url = "https://{}.amocrm.ru{}?{}".format(
                SUBDOMAIN,
                kwargs.get("endpoint"), kwargs.get("parameters"))
            response = requests.get(str(url), headers=headers).json()
        elif req_type == "post":
            response = requests.post("https://{}.amocrm.ru{}".format(
                SUBDOMAIN,
                kwargs.get("endpoint")), headers=headers, json=kwargs.get("data")).json()
        return response



def add_complex_lead(name, phone_number, username):
    data = [
        {
            "source_name": "Сайт Flex Camp",
            "source_uid": "Форма запипси flex camp",
            "metadata": {
                "ip": "82.115.50.124",
                "form_id": "new lead",
                "form_sent_at": int(time.time()),
                "form_name": "Форма записи в лагерь",
                "form_page": "https://flexcamp.uz",
                "referer": "https://flexcamp.uz"
            },
            "_embedded": {
                "leads": [{

                    "name": 'Новая сделка с бота',
                }

                          ],
                "contacts": [
                    {
                        "name": name,
                        "updated_by": 0,
                        "custom_fields_values": [
                            {
                                "field_id": TG_USERNAME_ID,
                                "values": [
                                    {
                                        "value": username
                                    }
                                ]
                            },
                            {
                                "field_code": "PHONE",
                                "values": [
                                    {
                                        "enum_code": "WORK",
                                        "value": phone_number
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    ]
    amocrm_wrapper = AmoCRMWrapper()
    response = amocrm_wrapper.base_request(endpoint='/api/v4/leads/unsorted/forms', type='post', data=data)

    lead_id = response['_embedded']['unsorted'][0]['_embedded']['leads'][0]['id']
    return lead_id


