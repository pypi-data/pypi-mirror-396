from user_agent import generate_user_agent
from SignerPy import *
import requests, SignerPy, json, secrets, uuid, binascii, os, time, random,re
class TikTok:
    @staticmethod
    
    def xor(string):
          return "".join([hex(ord(c) ^ 5)[2:] for c in string])
    def GetUser(self,es):
        secret = secrets.token_hex(16)
        xor_email=self.xor(es)
        params = {
            "request_tag_from": "h5",
            "fixed_mix_mode": "1",
            "mix_mode": "1",
            "account_param": xor_email,
            "scene": "1",
            "device_platform": "android",
            "os": "android",
            "ssmix": "a",
            "type": "3736",
            "_rticket": str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632",
            "cdid": str(uuid.uuid4()),
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "370805",
            "version_name": "37.8.5",
            "manifest_version_code": "2023708050",
            "update_version_code": "2023708050",
            "ab_version": "37.8.5",
            "resolution": "1600*900",
            "dpi": "240",
            "device_type": "SM-G998B",
            "device_brand": "samsung",
            "language": "en",
            "os_api": "28",
            "os_version": "9",
            "ac": "wifi",
            "is_pad": "0",
            "current_region": "TW",
            "app_type": "normal",
            "sys_region": "US",
            "last_install_time": "1754073240",
            "mcc_mnc": "46692",
            "timezone_name": "Asia/Baghdad",
            "carrier_region_v2": "466",
            "residence": "TW",
            "app_language": "en",
            "carrier_region": "TW",
            "timezone_offset": "10800",
            "host_abi": "arm64-v8a",
            "locale": "en-GB",
            "ac2": "wifi",
            "uoo": "1",
            "op_region": "TW",
            "build_number": "37.8.5",
            "region": "GB",
            "ts":str(round(random.uniform(1.2, 1.6) * 100000000) * -1),
            "iid": str(random.randint(1, 10**19)),
            "device_id": str(random.randint(1, 10**19)),
            "openudid": str(binascii.hexlify(os.urandom(8)).decode()),
            "support_webview": "1",
            "okhttp_version": "4.2.210.6-tiktok",
            "use_store_region_cookie": "1",
            "app_version":"37.8.5"}
        cookies = {
            "passport_csrf_token": secret,
            "passport_csrf_token_default": secret,
            "install_id": params["iid"],
        }
        
        
        
        
        s=requests.session()
        cookies = {
            '_ga_3DVKZSPS3D': 'GS2.1.s1754435486$o1$g0$t1754435486$j60$l0$h0',
            '_ga': 'GA1.1.504663773.1754435486',
            '__gads': 'ID=0cfb694765742032:T=1754435487:RT=1754435487:S=ALNI_MbIZNqLgouoeIxOQ2-N-0-cjxxS1A',
            '__gpi': 'UID=00001120bc366066:T=1754435487:RT=1754435487:S=ALNI_MaWgWYrKEmStGHPiLiBa1zlQOicuA',
            '__eoi': 'ID=22d520639150e74a:T=1754435487:RT=1754435487:S=AA-AfjZKI_lD2VnwMipZE8ienmGW',
            'FCNEC': '%5B%5B%22AKsRol8AtTXetHU2kYbWNbhPJd-c3l8flgQb4i54HStVK8CCEYhbcA3kEFqWYrBZaXKWuO9YYJN53FddyHbDf05q1qY12AeNafjxm2SPp7mhXZaop_3YiUwuo_WHJkehVcl5z4VyD7GHJ_D8nI2DfTX5RfrQWIHNMA%3D%3D%22%5D%5D',
        }
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en,ar;q=0.9,en-US;q=0.8',
            'application-name': 'web',
            'application-version': '4.0.0',
            'content-type': 'application/json',
            'origin': 'https://temp-mail.io',
            'priority': 'u=1, i',
            'referer': 'https://temp-mail.io/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-cors-header': 'iaWg3pchvFx48fY',
        }
        
        json_data = {
            'min_name_length': 10,
            'max_name_length': 10,
        }
        
        response = requests.post('https://api.internal.temp-mail.io/api/v3/email/new', cookies=cookies, headers=headers, json=json_data)
        name=response.json()["email"]
        url = "https://api16-normal-c-alisg.tiktokv.com/passport/account_lookup/email/"
        s.cookies.update(cookies)
        m=SignerPy.sign(params=params,cookie=cookies)
        
        headers = {
          'User-Agent': "com.zhiliaoapp.musically/2023708050 (Linux; U; Android 9; en_GB; SM-G998B; Build/SP1A.210812.016;tt-ok/3.12.13.16)",
          'x-ss-stub':m['x-ss-stub'],
          'x-tt-dm-status': "login=1;ct=1;rt=1",
          'x-ss-req-ticket':m['x-ss-req-ticket'],
          'x-ladon': m['x-ladon'],
          'x-khronos': m['x-khronos'],
          'x-argus': m['x-argus'],
          'x-gorgon': m['x-gorgon'],
          'content-type': "application/x-www-form-urlencoded",        
        }
        
        response = requests.post(url, headers=headers,params=params,cookies=cookies)
        
        if 'data' in response.json():
            try:passport_ticket=response.json()["data"]["accounts"][0]["passport_ticket"]
            except Exception as e:return {'status':e,'username':None}
        else:
            return {'status':'Bad','username':None}           
        
        name_xor=self.xor(name)
        url = "https://api16-normal-c-alisg.tiktokv.com/passport/email/send_code/"
        params.update({"not_login_ticket":passport_ticket,"email":name_xor})
        m = SignerPy.sign(params=params, cookie=cookies)
        headers = {
            'User-Agent': "com.zhiliaoapp.musically/2023708050 (Linux; U; Android 9; en_GB; SM-G998B; Build/SP1A.210812.016;tt-ok/3.12.13.16)",
            'Accept-Encoding': "gzip",
            'x-ss-stub': m['x-ss-stub'],
            'x-ss-req-ticket': m['x-ss-req-ticket'],
            'x-ladon': m['x-ladon'],
            'x-khronos': m['x-khronos'],
            'x-argus': m['x-argus'],
            'x-gorgon': m['x-gorgon'],
        }
        response = s.post(url, headers=headers, params=params, cookies=cookies)
        
        time.sleep(5)
        cookies = {
            '_ga': 'GA1.1.504663773.1754435486',
            '__gads': 'ID=0cfb694765742032:T=1754435487:RT=1754435487:S=ALNI_MbIZNqLgouoeIxOQ2-N-0-cjxxS1A',
            '__gpi': 'UID=00001120bc366066:T=1754435487:RT=1754435487:S=ALNI_MaWgWYrKEmStGHPiLiBa1zlQOicuA',
            '__eoi': 'ID=22d520639150e74a:T=1754435487:RT=1754435487:S=AA-AfjZKI_lD2VnwMipZE8ienmGW',
            'FCNEC': '%5B%5B%22AKsRol8AtTXetHU2kYbWNbhPJd-c3l8flgQb4i54HStVK8CCEYhbcA3kEFqWYrBZaXKWuO9YYJN53FddyHbDf05q1qY12AeNafjxm2SPp7mhXZaop_3YiUwuo_WHJkehVcl5z4VyD7GHJ_D8nI2DfTX5RfrQWIHNMA%3D%3D%22%5D%5D',
            '_ga_3DVKZSPS3D': 'GS2.1.s1754435486$o1$g0$t1754435503$j43$l0$h0',
        }
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en,ar;q=0.9,en-US;q=0.8',
            'application-name': 'web',
            'application-version': '4.0.0',
            'content-type': 'application/json',
            'origin': 'https://temp-mail.io',
            'priority': 'u=1, i',
            'referer': 'https://temp-mail.io/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-cors-header': 'iaWg3pchvFx48fY'
        }
        
        response = requests.get(
            'https://api.internal.temp-mail.io/api/v3/email/{}/messages'.format(name),
            cookies=cookies,
            headers=headers,
        )
        import re
        try:
            exEm = response.json()[0]
            match = re.search(r"This email was generated for ([\w.]+)\.", exEm["body_text"])
            if match:
                username = match.group(1)
                print(username)
                return {'status':'Good','username':username,'Dev':'Mustafa','Telegram':'@PPH9P'}
        except Exception as e:return {'status':'Bad','username':None,'Info':e,'Dev':'Mustafa','Telegram':'@PPH9P'}    
        #@staticmethod
 

#
    def __init__(self):
        self.REAL_DEVICES = [
            "Samsung Galaxy A10", "Samsung Galaxy A11", "Samsung Galaxy A12",
            "Samsung Galaxy A20", "Samsung Galaxy A21", "Samsung Galaxy A22",
            "Samsung Galaxy A30", "Samsung Galaxy A31", "Samsung Galaxy A32",
            "Samsung Galaxy A33", "Samsung Galaxy A50", "Samsung Galaxy A51",
            "Samsung Galaxy A52", "Samsung Galaxy A53", "Samsung Galaxy A54",
            "Samsung Galaxy M11", "Samsung Galaxy M12", "Samsung Galaxy M21",
            "Samsung Galaxy M22", "Samsung Galaxy M31", "Samsung Galaxy M32",
            "Samsung Galaxy M33", "Samsung Galaxy M51",
            "Samsung Galaxy S8", "Samsung Galaxy S9", "Samsung Galaxy S10",
            "Samsung Galaxy S20", "Samsung Galaxy S21", "Samsung Galaxy S22",
            "Samsung Galaxy S23",
            "Xiaomi Redmi 9", "Xiaomi Redmi 9A", "Xiaomi Redmi 10",
            "Xiaomi Redmi 10A", "Xiaomi Redmi Note 8", "Xiaomi Redmi Note 9",
            "Xiaomi Redmi Note 10", "Xiaomi Redmi Note 10 Pro",
            "Xiaomi Redmi Note 11", "Xiaomi Redmi Note 12",
            "Xiaomi Poco X3", "Xiaomi Poco X3 Pro", "Xiaomi Poco F3", "Xiaomi Poco F4",

            "OPPO A15", "OPPO A16", "OPPO A31", "OPPO A53",
            "OPPO Reno 5", "OPPO Reno 6",

  
            "Vivo Y12", "Vivo Y15", "Vivo Y20", "Vivo Y21",
            "Vivo Y33", "Vivo V20", "Vivo V21",

  
            "Huawei Y7 Prime", "Huawei Y9 2019", "Huawei Nova 3i",
            "Huawei Nova 7i", "Huawei Mate 20 Lite", "Huawei P30 Lite",

            "Infinix Hot 9", "Infinix Hot 10", "Infinix Hot 11",
            "Infinix Hot 12", "Infinix Note 7", "Infinix Note 8",
            "Infinix Note 10", "Infinix Note 11",

            
            "Tecno Spark 6", "Tecno Spark 7", "Tecno Spark 8",
            "Tecno Camon 15", "Tecno Camon 16",

            
            "Motorola Moto G7", "Motorola Moto G8", "Motorola Moto G9",
            "Motorola Moto G10", "Motorola Moto G30", "Motorola Moto E7",

           
            "Nokia 3.4", "Nokia 5.3", "Nokia 5.4", "Nokia X10", "Nokia X20"
        ]


        self.DEVICES_300 = random.sample(self.REAL_DEVICES * 10, 300)

    def generate_build(self):
        return f"SP1A.{random.randint(200000,299999)}.{random.randint(100,999)}"

    def generate_android(self):
        return random.choice(["10","11","12","13","14",'15'])

    def generate_user_agent(self, device, android_version, build_number):
        return (
            f"Mozilla/5.0 (Linux; Android {android_version}; {device}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Version/4.0 Chrome/112.0.5615.48 Mobile Safari/537.36 "
            f"Build/{build_number}"
        )

    def GetDevices(self):
        devices_list = []
        for _ in range(len(self.DEVICES_300)):
            device = random.choice(self.DEVICES_300)
            brand = device.split()[0]
            android = self.generate_android()
            build = self.generate_build()
            ts = str(round(random.uniform(1.2, 1.6) * 100000000) * -1)
            rticket = ts + "4632"
            device_id = str(random.randint(1, 10**19))
            ua = self.generate_user_agent(device, android, build)

            return {
                'type': device,
                'brand': brand,
                'version': android,
                "build": build,
                "user_agent": ua,
                "ts": ts,
                "_rticket": rticket,
                "device_id": device_id
            }
    def GetLevel(self, username):
        username = username.strip().lstrip('@')
        url = f'https://www.tiktok.com/@{username}'
        headers = {'User-Agent': str(generate_user_agent())}

        try:  
            response = requests.get(url, headers=headers)  
            if '{"userInfo":{' in response.text:  
         
                match = re.search(r'"userInfo":\{.*?"id":"([^"]+)"', response.text)  
                if match:  
                    user_id = match.group(1)  
            elif '"user":{"id":"' in response.text:  
                match = re.search(r'"user":{"id":"([^"]+)"', response.text)  
                if match:  
                    user_id = match.group(1)  
            else:
                user_id = None

            if not user_id:
                api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"  
                api_response = requests.get(api_url)  
                if api_response.status_code == 200:  
                    data = api_response.json()  
                    if data.get("code") == 0 and "data" in data:  
                        user_id = data["data"]["user"]["id"]  

            if not user_id:
                return {'status':'Bad','Level':None}
            
            user_details, raw_response = self.get_tiktok_user_details(user_id)

            if user_details and user_details.get('status_code') == 0:  
                data = user_details.get('data', {})  
                badge_list = data.get('badge_list', [])  
                for badge in badge_list:  
                    combine = badge.get('combine', {})  
                    if combine and 'text' in combine:  
                        text_data = combine.get('text', {})  
                        if 'default_pattern' in text_data:  
                            aa = text_data.get('default_pattern')  
                            return {'status':'Good','Level':text_data['default_pattern'],'Dev':'Mustafa','Telegram':'@PPH9P'}
                return user_id, user_details  
            else:
                return {'status':'Bad','Level':None,'Dev':'Mustafa','Telegram':'@PPH9P'}
                
                return user_id, None  

        except Exception as e:  
            return e
            return {'status':'Bad','Level':None,'Info':e,'Dev':'Mustafa','Telegram':'@PPH9P'}  
            return None, None

    def get_tiktok_user_details(self, user_id, custom_headers=None, custom_params=None):

        url = "https://webcast22-normal-c-alisg.tiktokv.com/webcast/user/"

        headers = {  
            "Host": "webcast22-normal-c-alisg.tiktokv.com",  
            "cookie": "store-idc=alisg; passport_csrf_token=20e9da8b0e16abaa45d4ce2ad75a1325; passport_csrf_token_default=20e9da8b0e16abaa45d4ce2ad75a1325; d_ticket=913261767c3f16148c133796e661c1d83cf5d; multi_sids=7464926696447099909%3A686e699e8bbbc4e9f5e08d31c038c8e4; odin_tt=e2d5cd703c2e155d572ad323d28759943540088ddc6806aa9a9b48895713be4b585e78bf3eb17d28fd84247c4198ab58fab17488026468d3dde38335f4ab928ad1b9bd82a2fb5ff55da00e3368b4d215; cmpl_token=AgQQAPMsF-RPsLemUeAYPZ08_KeO5HxUv5IsYN75Vg; sid_guard=686e699e8bbbc4e9f5e08d31c038c8e4%7C1751310846%7C15552000%7CSat%2C+27-Dec-2025+19%3A14%3A06+GMT; uid_tt=683a0288ad058879bbc16d3b696fa815e1d72c050bdb2d14b824141806068417; uid_tt_ss=683a0288ad058879bbc16d3b696fa815e1d72c050bdb2d14b824141806068417; sid_tt=686e699e8bbbc4e9f5e08d31c038c8e4; sessionid=686e699e8bbbc4e9f5e08d31c038c8e4; sessionid_ss=686e699e8bbbc4e9f5e08d31c038c8e4; store-country-code=eg; store-country-code-src=uid; tt-target-idc=alisg; ttwid=1%7Cmdx9QyT3L35S3CFNpZ_6a1mG2Q3hbfWvwQh6gY5hjhw%7C1751310949%7C253ef523ddc8960c5f52b286d8ce0afc2623ec081a777dac3ba5606ecdc1bd40; store-country-sign=MEIEDPH3p6xlgJXYVovbBgQgMf22gnCf0op7iOSSy6oKKB7paF60OVLAsxbGkh6BUGAEEF0aMxzItZZ03IrkjedsuYY; msToken=Srtgt7p6ncYXI8gph0ecExfl9DpgLtzOynFNZjVGLkKUjqV0J1JI8aBoE8ERmO5f43HQhtJxcU2FeJweSbFIlIOADOHP_z75VvNeA2hp5LN1JZsKgj-wymAdEVJt",  
            "x-tt-pba-enable": "1",  
            "x-bd-kmsv": "0",  
            "x-tt-dm-status": "login=1;ct=1;rt=1",  
            "live-trace-tag": "profileDialog_batchRequest",  
            "sdk-version": "2",  
            "x-tt-token": "034865285659c6477b777dec3ab5cd0aa70363599c1acde0cd4e911a51fed831bdb2ec80a9a379e8e66493471e519ccf05287299287a55f0599a72988865752a3668a1a459177026096896cf8d50b6e8b5f4cec607bdcdee5a5ce407e70ce91d52933--0a4e0a20da4087f3b0e52a48822384ac63e937da36e5b0ca771f669a719cf633d66f8aed12206a38feb1f115b80781d5cead8068600b779eb2bba6c09d8ae1e6a7bc44b46b931801220674696b746f6b-3.0.0",  
            "passport-sdk-version": "6031490",  
            "x-vc-bdturing-sdk-version": "2.3.8.i18n",  
            "x-tt-request-tag": "n=0;nr=011;bg=0",  
            "x-tt-store-region": "eg",  
            "x-tt-store-region-src": "uid",  
            "rpc-persist-pyxis-policy-v-tnc": "1",  
            "x-ss-dp": "1233",  
            "x-tt-trace-id": "00-c24dca7d1066c617d7d3cb86105004d1-c24dca7d1066c617-01",  
            "user-agent": "com.zhiliaoapp.musically/2023700010 (Linux; U; Android 11; ar; SM-A105F; Build/RP1A.200720.012; Cronet/TTNetVersion:f6248591 2024-09-11 QuicVersion:182d68c8 2024-05-28)",  
            "accept-encoding": "gzip, deflate, br",  
            "x-tt-dataflow-id": "671088640"  
        }  

        if custom_headers:
            headers.update(custom_headers)  
  
        params = {  
            "user_role": '{"7464926696447099909":1,"7486259459669820432":1}',  
            "request_from": "profile_card_v2",  
            "sec_anchor_id": "MS4wLjABAAAAiwBH59yM2i_loS11vwxZsudy4Bsv5L_EYIkYDmxgf-lv3oZL4YhQCF5oHQReiuUV",  
            "request_from_scene": "1",  
            "need_preload_room": "false",  
            "target_uid": user_id,  
            "anchor_id": "246047577136308224",  
            "packed_level": "2",  
            "need_block_status": "true",  
            "current_room_id": "7521794357553400594",  
            "device_platform": "android",  
            "os": "android",  
            "ssmix": "a",  
            "_rticket": "1751311566864",  
            "cdid": "808876f8-7328-4885-857d-8f15dd427861",  
            "channel": "googleplay",  
            "aid": "1233",  
            "app_name": "musical_ly",  
            "version_code": "370001",  
            "version_name": "37.0.1",  
            "manifest_version_code": "2023700010",  
            "update_version_code": "2023700010",  
            "ab_version": "37.0.1",  
            "resolution": "720*1382",  
            "dpi": "280",  
            "device_type": "SM-A105F",  
            "device_brand": "samsung",  
            "language": "ar",  
            "os_api": "30",  
            "os_version": "11",  
            "ac": "wifi",  
            "is_pad": "0",  
            "current_region": "IQ",  
            "app_type": "normal",  
            "sys_region": "IQ",  
            "last_install_time": "1751308971",  
            "timezone_name": "Asia/Baghdad",  
            "residence": "IQ",  
            "app_language": "ar",  
            "timezone_offset": "10800",  
            "host_abi": "armeabi-v7a",  
            "locale": "ar",  
            "content_language": "ar,",  
            "ac2": "wifi",  
            "uoo": "1",  
            "op_region": "IQ",  
            "build_number": "37.0.1",  
            "region": "IQ",  
            "ts": "1751311566",  
            "iid": "7521814657976928001",  
            "device_id": "7405632852996097552",  
            "openudid": "c79c40b21606bf59",  
            "webcast_sdk_version": "3610",  
            "webcast_language": "ar",  
            "webcast_locale": "ar_IQ",  
            "es_version": "3",  
            "effect_sdk_version": "17.6.0",  
            "current_network_quality_info": '{"tcp_rtt":16,"quic_rtt":16,"http_rtt":584,"downstream_throughput_kbps":1400,"quic_send_loss_rate":-1,"quic_receive_loss_rate":-1,"net_effective_connection_type":3,"video_download_speed":1341}'  
        }  

        if custom_params: 
            params.update(custom_params)  

        try:  
            up = get(params=params)  
            def parse_cookie_string(cookie_string):  
                cookie_dict = {}  
                for item in cookie_string.split(';'):  
                    if item.strip():  
                        try:  
                            key, value = item.strip().split('=', 1)  
                            cookie_dict[key.strip()] = value.strip()  
                        except ValueError:  
                            cookie_dict[item.strip()] = ''  
                return cookie_dict  
            cookie_dict = parse_cookie_string(headers["cookie"])  
            sg = sign(params=up, cookie=cookie_dict)  

            headers.update({  
                'x-ss-req-ticket': sg['x-ss-req-ticket'],  
                'x-ss-stub': sg['x-ss-stub'],  
                'x-argus': sg["x-argus"],  
                'x-gorgon': sg["x-gorgon"],  
                'x-khronos': sg["x-khronos"],  
                'x-ladon': sg["x-ladon"],  
            })  
            headers["accept-encoding"] = "identity"  
            response = requests.get(url, headers=headers, params=params)  

            try:  
                json_data = response.json()  
                if json_data.get('status_code') != 0:  
                    return {'status':'Bad','Level':None}
                streamed_content = ""  
                for line in response.iter_lines():  
                    if line:  
                        decoded_line = line.decode('utf-8')  
                        if decoded_line.startswith('data: '):  
                            json_part = decoded_line[6:]  
                            try:  
                                data_part = json.loads(json_part)  
                                if 'choices' in data_part and len(data_part['choices']) > 0:  
                                    delta = data_part['choices'][0].get('delta', {})  
                                    if 'content' in delta and delta['content']:  
                                        streamed_content += delta['content']  
                            except json.JSONDecodeError:  
                                continue  
                if streamed_content:  
                    return {'status':'Bad','Level':None}

                return json_data, response  
            except json.JSONDecodeError:  
                return False
                return None, response  
            except Exception as e:  
                #print(f"حدث خطأ أثناء معالجة الاستجابة: {e}")  
                return {'status':'Bad','Level':None}

        except Exception as e:  
            return e
    def GetInfo(self,username):
        
        try:
            level=TikTok().GetLevel(username).get('Level')
            headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    };url = f"https://www.tiktok.com/@{username}";response = requests.get(url, headers=headers,timeout=10).text;data = response.split('''"userInfo":{"user":{''')[1].split('''</sc''')[0];followers = data.split('"followerCount":')[1].split(',')[0];id = data.split('"id":"')[1].split('"')[0];nickname = data.split('"nickname":"')[1].split('"')[0];following = data.split('"followingCount":')[1].split(',')[0];likes = data.split('"heart":')[1].split(',')[0]
            ff = {
    "🔥 HIT TIKTOK 🔥": {
        "User": username,
        'Level':level,
        "Name": nickname,
        "Id": id,
        "Followers": followers,
        "Following": following,
        "Likes": likes
    },
    "By": "@D_B_HH",
    "Channel": "@k_1_cc"
}
        except Exception as e:return {'status':'Bad','Dev':'Mustafa','Telegram':'@PPH9P'}
import aiohttp
import asyncio
import re
from urllib.parse import urlparse, parse_qs, quote

class Gmail:
	@staticmethod
	def CheckGmail(email):
		import random , requests
		try:
			N = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(random.randrange(5,10)))
			b = random.randrange(1980,2010),random.randrange(1,12),random.randrange(1,28)
			sis = requests.Session()
			headers = {
	                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	                'accept-language': 'en-US,en;q=0.9',
	                'referer': 'https://accounts.google.com/',
	                'upgrade-insecure-requests': '1',
	                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
	                'x-browser-channel': 'stable',
	                'x-browser-copyright': 'Copyright 2024 Google LLC. All rights reserved.',
	                'x-browser-year': '2024',
	            }
	
			params = {
	                'biz': 'false',
	                'continue': 'https://mail.google.com/mail/u/0/',
	                'ddm': '1',
	                'emr': '1',
	                'flowEntry': 'SignUp',
	                'flowName': 'GlifWebSignIn',
	                'followup': 'https://mail.google.com/mail/u/0/',
	                'osid': '1',
	                'service': 'mail',
	            }
	
			response = sis.get('https://accounts.google.com/lifecycle/flows/signup', params=params, headers=headers)
			tl=response.url.split('TL=')[1]
			s1= response.text.split('"Qzxixc":"')[1].split('"')[0]
			at = response.text.split('"SNlM0e":"')[1].split('"')[0]
			headers = {
	                'accept': '*/*',
	                'accept-language': 'en-US,en;q=0.9',
	                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	                'origin': 'https://accounts.google.com',
	                'referer': 'https://accounts.google.com/',
	                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
	                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
	                'x-same-domain': '1',
	            }
	
			params = {
	                'rpcids': 'E815hb',
	                'source-path': '/lifecycle/steps/signup/name',
	                'hl': 'en-US',
	                'TL': tl,
	                'rt': 'c',
	            }
	
			data = 'f.req=%5B%5B%5B%22E815hb%22%2C%22%5B%5C%22{}%5C%22%2C%5C%22%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5D%2C%5B%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2C%5C%22mail%5C%22%5D%2C1%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(N,at)
	
			response = sis.post(
	                'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	                params=params,
	                headers=headers,
	                data=data,
	            ).text
	
	
	
			headers = {
	                'accept': '*/*',
	                'accept-language': 'en-US,en;q=0.9',
	                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	                'origin': 'https://accounts.google.com',
	                'referer': 'https://accounts.google.com/',
	                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
	                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
	                'x-same-domain': '1',
	            }
	
			params = {
	                'rpcids': 'eOY7Bb',
	                'source-path': '/lifecycle/steps/signup/birthdaygender',
	                'hl': 'en-US',
	                'TL': tl,
	                'rt': 'c',
	            }
	
			data = 'f.req=%5B%5B%5B%22eOY7Bb%22%2C%22%5B%5B{}%2C{}%2C{}%5D%2C1%2Cnull%2Cnull%2Cnull%2C%5C%22%3Cf7Nqs-sCAAZfiOnPf4iN_32KOpLfQKL0ADQBEArZ1IBDTUyai2FYax3ViMI2wqBpWShhe-OPRhpMjnm9s14Yu65MknXEBWcyTyF3Jx0pzQAAAeGdAAAAC6cBB7EATZAxrowFF7vQ68oKqx7_sdcR_u8t8CJys-8G4opCIVySwUYaUnm-BovA8aThYLISPNMc8Pl3_B0GnkQJ_W4SIed6l6EcM7QLJ8AXVNAaVgbhsnD7q4lyQnlvR14HRW10oP85EU_bwG1E4QJH1V0KnVS4mIeoqB7zHOuxMuGifv6MB3GghUGTewh0tMN1jaf8yvX804tntlrlxm3OZgCZ2UxgDjUVOKFMv1Y3Txr16jJEJ56-T7qrPCtt6H1kmUvCIl_RDZzbt_sj5OLnbX1UvVA-VgG8-X9AJdvGhCKVhkf3iSkjy6_ZKsZSbsOsMjrm7ggnLdMStIf4AzbJIyMC7q4JMCaDaW_UI9SgquR8mHMpHGRmP7zY-WE47l7uRSpkI6oV93XJZ1zskJsxaDz7sDYHpzEL1RGPnkZU45XkIkwuc1ptU_AiM6SQyoZK7wFnhYxYfDQjSwaC7lOfngr6F2e4pDWkiC96QY4xLr6m2oUoDbyKR3ykccKEECEakFKzS-wSxIt9hK6nw-a9PEpVzhf6uIywZofNCs0KJOhhtv_ReG24DOC6NHX-FweCOkiYtT2sISrm6H8Wr4E89oU_mMWtpnXmhs8PB28SXw42-EdhRPsdcQkgKycOVT_IXwCc4Td9-t7715HP-L2XLk5i05aUrk-sHPPEz8SyL3odOb1SkwQ69bRQHfbPZr858iTDD0UaYWE_Jmb4wlGxYOSsvQ3EIljWDtj69cq3slKqMQu0ZC9bdqEh0p_T9zvsVwFiZThf19JL8PtqlXH5bgoEnPqdSfYbnJviQdUTAhuBPE-O8wgmdwl22wqkndacytncjwGR9cuXqAXUk_PbS-0fJGxIwI6-b7bhD7tS2DUAJk708UK5zFDLyqN6hFtj8AAjNM-XGIEqgTavCRhPnVT0u0l7p3iwtwKmRyAn42m3SwWhOQ6LDv-K2DyLl2OKfFu9Y-fPBh-2K2hIn2tKoGMgVbBR8AsVsYL7L6Bh5JIW7LCHaXNk3oDyHDx5QFaPtMmnIxcfFG90YSEPIgWV2nb67zDDacvvCkiPEQMXHJUcz1tuivaAgCTgW68wNYkUt89KJDhJTSWY2jcPsDIyCnS-SGESyR7mvbkvC3Robo0zVQm6q3Z73si9uqJiPmUGgBLycxUq2A_L3B-Hz35vBm5Oc5Hbe8hJToB03ilQzLa8Kld5BY8_kmmh6kfrOvi07uwfusHv3mKfijE2vaK3v2O2He41hCaOv3ExSfdPKb2V5nPPTw8ryyC5ZwlM_DLCU_k5xONsh4uplpRmydmJcit4aj5Ig0qLVF9MxIWU5xoDlvhKL9jHh-HVgIe-CPp4RMM5BfTxDgtESiF97RWjwrNeKn6Fc4311AdCrfZMcZ0F2JnQsfKAz4H-hoWbrOEVBkPcBt5umJ_iaCm0cQ2XTQMjzAtfWbRe6EGSxbkK-DXBl4EQM-6cnH1139MIHLzNou_Tltbl2HaomCS044CwhRNpe95KuYhM4Fz0Z_8rRjqy48tS_L4kQMX1CtxjBNfd4eUoaAIwAcz3LaL5BwL0DAYcV3xruTTuy6X8zFHe8fAIB9pJ_Pw0YJm3Ye28_tTg5xk0R4EU7_IPIHk6RrtSsG0Rfst3Qi5NRfWFg5h9LlmlHO_EUhdw1wbCICTqbS2A94aIBSCQzn7RmqOTTSIXwgFwnSBRKvoo0v9tKQ2rnMZsXRhzQgxwfmYOq29EUbuHmmWQjpRhfzX1Z6-5gXRPr4-PjrInsTiAi36xDyc8a1yTAhKMwnvf3GNqcK8lqx80VCASvcpYxGIAFl4QghroZbIJXlhccCWVF_xrzsw83QUdoZ5ExWi5f_cLvEXeZssdtan1orOaPJuWXT_0ryzpS9fOGtT68pL4HMAPLPpfwhiZ-wtZQU0oVy6T2L6oP1SIHQDU_QDaMR0MkStXNDj69r5cTDdYZiIbFkvWYeL1afTEljx1i2n2KKnDmpJfx2HeGCSZBMKZey24z_LDLA7MyJ2VBo4Zvmm23dwhWHOly56w9ul4sWzpHqgsqmKynRoaq9SXKrrmbR3f2GKBHSvy3Jm0Ln52zwIQfFSXpOjGXq5pkOXlvQc6MPuV3zADVmcUZs6ywI-ER3PkAaA-f-zG-ke_6jvOzGp6WF8UxnIk5tq3tus_R5pUjVQFjk6qZtWOP8VZd1TeJ54Oo_ywj8YAYCphkDtFYRMZSubmnI-F9LLlAfOiDwQ7r-iNvp8psduy9xrWdIpE_l23Y_qYJPHwvtopL3lB7juqEiFkhUts7NEugyWY-m6-9oEgsOY0lM4746V-XUxSeS7UkZkQZZM19g7GkWjJ61D98i0m2u_UYLnyDFQEaIxVhFcmS1Zq7OMsKm_gYpMt4LuD1F3N__Vj05QNyI59QNQADODveiHpfVva9Cd2AzBm9AKGwU4xDS_FyX3XRsRbfQFtqNzPf1LAERHlnHFn%5C%22%2C%5Bnull%2Cnull%2C%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22mail%5C%22%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(b[0],b[1],b[2],at)
	
			response = sis.post(
	                'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	                params=params,
	                headers=headers,
	                data=data,
	            ).text
			headers = {
	                'accept': '*/*',
	                'accept-language': 'en-US,en;q=0.9',
	                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	                'origin': 'https://accounts.google.com',
	                'referer': 'https://accounts.google.com/',
	                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
	                'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	                'x-goog-ext-391502476-jspb': '["'+s1+'"]',
	                'x-same-domain': '1',
	            }
			params = {
	                'rpcids': 'NHJMOd',
	                'source-path': '/lifecycle/steps/signup/username',
	                'hl': 'en-US',
	                'TL': tl,
	                'rt': 'c',
	            }
			data = 'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{}%5C%22%2C0%2C0%2Cnull%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C152855%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(email,at)
	
			response = sis.post(
	                'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	                params=params,
	                headers=headers,
	                data=data,
	            ).text
			if 'password' in response:
				return {'status': 'Good', 'Dev': 'Mustafa', 'Telegram': '@D_B_HH'}
			else:
				return {'status': 'Bad', 'Dev': 'Mustafa', 'Telegram': '@D_B_HH'}
		except Exception as e:
			return e


class Facebook:
    def GetIDs(self):
        try:
            n = int(input("كم رابط تريد؟ "))
        except Exception:
            print("اكتب رقم بابا")
            return None

        urls = []
        for i in range(1, n + 1):
            u = input(f"link{i}: ").strip()
            urls.append(u)

        ids = []
        for urll in urls:
            if not urll:
                ids.append("ماكو")
                continue
            try:
                r = requests.get(urll, timeout=10).text
                match = re.search(r'"userID":"(\d+)"', r)
                if match:
                    ids.append(match.group(1))
                else:
                    return {'status':'Bad','IDs':'ماكو' , 'Dev': 'Mustafa', 'Telegram': '@D_B_HH'}
            except Exception as e:
                return {'status':'Good','Info': e, 'Dev': 'Mustafa', 'Telegram': '@D_B_HH'}

        ids_str = ",".join(ids)
        return {'status':'Good','IDs': ids_str, 'Dev': 'Mustafa', 'Telegram': '@D_B_HH'}


    def GetApps(self,cok):
	    try:
	     	
		    cookies = {}
		    session=requests.session()
		    for part in cok.split(';'):
		        if '=' in part:
		            key, val = part.strip().split('=', 1)
		            cookies[key] = val
		
		    headers = {
		        'user-agent': 'NokiaX2-01/5.0 (08.35) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 (Linux; Android 9; SH-03J) AppleWebKit/937.36 (KHTML, like Gecko) Safari/420+'
		    }
		
		    active_html = session.get('https://m.facebook.com/settings/apps/tabbed/?tab=active', cookies=cookies, headers=headers).text
		    expired_html = session.get('https://m.facebook.com/settings/apps/tabbed/?tab=inactive', cookies=cookies, headers=headers).text
		
		    lines = []  
		    lines.append("activities:")
		    apps = re.findall(r'data-testid="app_info_text">([^<]+)</span>', active_html)
		    dates = re.findall(r'(?:تمت الإضافة في|Added on|Ditambahkan pada|Ajouté le|Dodano dnia)\s*([^<]+)</p>', active_html)
		    if apps:
		        for i, app in enumerate(apps):
		            date = dates[i].strip() if i < len(dates) else "غير معروف"
		            lines.append(f"{i+1}. {app.strip()} - {date}")
		    else:
		        lines.append("No active apps")
		
		    lines.append("\nexpires:")
		    apps2 = re.findall(r'data-testid="app_info_text">([^<]+)</span>', expired_html)
		    dates2 = re.findall(r'(?:Kedaluwarsa pada|انتهت الصلاحية في)\s*([^<]+)</p>', expired_html)
		    if apps2:
		        for i, app in enumerate(apps2):
		            date = dates2[i].strip() if i < len(dates2) else "غير معروف"
		            lines.append(f"{i+1}. {app.strip()} - {date}")
		    else:
		        lines.append("No expired apps")
		
		    return "\n Dev : Mustafa | Tele : @D_B_HH \n".join(lines)
	    except:
	    	return 'problem'
	    	pass
