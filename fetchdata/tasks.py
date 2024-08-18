import requests
import hashlib
import base64
import random
import string
import urllib.parse
import phpserialize
from django.utils import timezone
from .models import SlaveServer, VpsInfo

class VirtualizorAdminAPI:
    def __init__(self, ip, key, passw, port=4084):
        self.key = key
        self.passw = passw
        self.ip = ip
        self.port = port
        self.protocol = 'http'
    
    def make_apikey(self, key, passw):
        return key + hashlib.md5((passw + key).encode('utf-8')).hexdigest()

    def generateRandStr(self, length):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length)).lower()
    
    def call(self, path, data=None, post=None, cookies=None):
        key = self.generateRandStr(8)
        apikey = self.make_apikey(key, self.passw)
        
        url = f'{self.protocol}://{self.ip}:{self.port}/{path}'
        url += f'&adminapikey={urllib.parse.quote(self.key)}&adminapipass={urllib.parse.quote(self.passw)}'
        url += f'&api=serialize&apikey={urllib.parse.quote(apikey)}'

        if data:
            url += f'&apidata={urllib.parse.quote(base64.b64encode(data.encode("utf-8")).decode("utf-8"))}'

        headers = {
            'User-Agent': 'Softaculous'
        }

        if cookies:
            cookies = {k: v for k, v in cookies.items()}

        if post:
            response = requests.post(url, headers=headers, data=post, cookies=cookies, verify=False)
        else:
            response = requests.get(url, headers=headers, cookies=cookies, verify=False)
        
        if response.status_code != 200:
            return None
        
        return response.text
    
    def list_vs(self):
        path = 'index.php?act=vs'
        result = self.call(path)
        
        if result:
            try:
                deserialized_result = phpserialize.loads(result.encode('utf-8'))
                return deserialized_result.get(b'vs', {})
            except Exception as e:
                print(f"Deserialization failed: {e}")
                return {}
        else:
            return {}

def fetch_and_save_vps_info(slave_server):
    api = VirtualizorAdminAPI(slave_server.ip_address, slave_server.api_key, slave_server.api_pass)
    vps_list = api.list_vs()

    for vps_data in vps_list.values():
        vps_id = vps_data.get(b'vpsid').decode('utf-8')
        limit_bandwidth = int(vps_data.get(b'bandwidth', b'0').decode('utf-8'))
        used_bandwidth = int(vps_data.get(b'used_bandwidth', b'0').decode('utf-8'))

        for ip_key, ip_address in vps_data[b'ips'].items():
            ip = ip_address.decode('utf-8')

            # Create or update VpsInfo
            vps_info, created = VpsInfo.objects.update_or_create(
                vps_id=vps_id,
                ip=ip,
                datacenter=slave_server.datacenter,
                defaults={
                    'limit_bandwidth': limit_bandwidth,
                    'used_bandwidth': used_bandwidth,
                    'start_date': timezone.now(),
                    'end_date': timezone.now(),  # Adjust this based on your logic
                    'username': 'default_username',  # Replace with actual logic if necessary
                    'telegram_id': 'default_telegram_id',  # Replace with actual logic if necessary
                    'is_active': True,
                }
            )

            if created:
                print(f"Created new VPS Info: {vps_info}")
            else:
                print(f"Updated VPS Info: {vps_info}")

# Example usage for all slave servers
def fetch_all_vps_info():
    for slave_server in SlaveServer.objects.all():
        fetch_and_save_vps_info(slave_server)
