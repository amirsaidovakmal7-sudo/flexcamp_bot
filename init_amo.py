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




secret_code = 'def502000b362a0bf27bf6248c50a484f7600f376caf47c83eced7c784061d05e2a0fbdc5fd15e47bd5764bc1501efa90da227313f299ae49e5b0268e3756ecc16ea0d65ffd5c05a60a702cf6f156cb5089f60f6cc706eac2aaba4d43d6f935ad3be19f6a41c7705be824c6b195452412d6141767f1a9d35f344c44b2b0f34b39920c0ba62a86cb46167f8f7337629f25084ae1e341ff7357f690c1737718e1f279f2cfb84f0a319699a0a78bbe51ffc345859772c1fd981ea50f9738000e95091a7b8b04f965e4c3e96529ee16b5a611832a96434cb07ae1c5065a03420abf8218fe4951ace7e957367530aa6bd56d209840c17272b41757080fd68ae8a08c7b5767b2f59bb858098cc476d25072bde04a3cdd425e8474d003933270b9a3a0aa79f54ec83b7e49227063d2c9459aea837928ba8a4d121beed3cebefd8d3530b6ca404eb9276afc8ae2b17133d9bcd3e6779bdc56bb3c45a95d039015fed15e27ef9150c5114b3286a5ab55b62cb0b5551e1c86e5af87c22d8cdffb3d67a09bef8545b30828b036c7a32cc06248837fdb439cea85729f453855e1d9a5a6f53d130a1aa1228ac1b0042f71729bed9daa3483e58c0847e62c58e9bd6a646244761310f15be63ea390bfdc74deae392259a5d90d3604a904e82e8fa3ef2513bcb270c1ba036'



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
