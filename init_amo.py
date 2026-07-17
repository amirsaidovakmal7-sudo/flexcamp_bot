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




secret_code = 'def502001b6b8bae5c3345cad44955ce091ebcf38317e90b928d79d0e30c97da3b60d9cc8622baf5e43775ca9c2190464e1824c67d040bc9f974bd95422ae5e6dfda25229a8b1719abd92096c851a2c059bffe21ad01845022d6f7c4dc92ddc2a970a7b179d222f977a9bae1154df44df950088f5baae866a19f57c6d1a5a0ca680b58218848b044f933236615e1834ce5e2378c22494274457259f2fcc384aeefb16dc1684a4fbbc25b3705500d8ae7fb5a3788fd8c3edbb4112bcc717b5e9f656f6f57012e39b99970a7444a5ea69e860f36bd9b044f3616799e15bd461a4e40eda9e47b95d5054ac16f8f731ed54c89c69c8dfd514fea1ae4e4f4650eb5f6f3f73026e1dbe774c99303939b7bb84c0f515c15ccfd3e4f9780d459d394cad089e4d33a76416964e5aad0f596e1fe1cea7e0142169fc4f02290c800177a0d93de37df5a1bb56361194e032c1b47d9142d3cf17b7bcf23ae40dfbc834dac322b9bd5bb89f9f3f5230a337c2ef84e018d43dc6c747c5060c89808592d85fbea455d9d8bf9818d15a0a93adda2855ce94156dc2e88eb86492a4b19a4386bc7bb099565d8cfa0650bb4b0283788b49932c4b50e27c38cf6f4a48bc0bd04d7ef096af2bf070598bd5316fad3ace066188c43a4b497f3d34e5d5c1184a7c6bf8a862515fcd45d'



def _is_expire(token):
    if isinstance(token, str):
        token = token.encode('utf-8')
    token_data = jwt.decode(token, options={"verify_signature": False})
    exp = datetime.utcfromtimestamp(token_data['exp'])
    now = datetime.utcnow()

    return now >= exp


def save_tokens(access_token, refresh_token):
    try:
        create_access_token(access_token)
        create_refresh_token(refresh_token)
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

amocrmwrapper = AmoCRMWrapper()

amocrmwrapper.init_oauth2()
