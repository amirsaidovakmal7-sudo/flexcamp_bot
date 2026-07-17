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




secret_code = 'def5020006f84ac7a58783d39793053f843fc48053874f154b882c497c5e5ca9e85bf8bc660f7ef39daff12ed89487ac8d129a470ab694fae0be1560b0dcb202ad3c7c30ef08b4dfc78b5833b79cddb56fc88d8b6f80f0c6204089efacf0c6f4712e1e7603fbe6748f4ba266717dfa683e9601ce13e019e81d5779a329e3866bad206c976b241a74d881f4280539a04180c4efbefae6847d266c3ec64fc1821262153180f010c37667eb6cb3d3aecf8b6e71c5048f7d34097db0bfeda462f131d96b3215381b4e450ab30fce8e3945d626eb9a1e078a8a27be991f58dcf196a2041f6a8403214c298617027f75244d5141f724917ed86c43797b13df58ea78d4532ffc5e5d8366454313fcf396fc8942b3771c2c08d19f209a1daa1c74aae9ac38faba76aa93161fee51485ddead7f26eac4c731d6a77691e1f7aa5489652d3a86f2dcb88693e643388c9ff3cb2d3c822c851c4c4db729de113b94101464ea3f170a82dd85064bed1242a691e7268b36e605a6eb287ae024bc9c788b250df61ce3a8153096bf4282cfbe34de1d1f0022e9d7c353105840eb0620cabd7888b603c7742fc1a0506f2a9b6bf01ddbe7144205889f9e7a3203f47965edc39f646d29642498498895ac6e0c59ce9503df4dd5bd74888f1ce1d77e6548daa906348ae15e7a4673'



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


