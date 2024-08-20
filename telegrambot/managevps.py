import requests
import hashlib
import base64
import random
import string
import urllib.parse
import phpserialize
from django.core.exceptions import ObjectDoesNotExist
from fetchdata.models import SlaveServer, VpsInfo

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
        
        return phpserialize.loads(response.text.encode('utf-8'))

    def list_vs(self):
        path = 'index.php?act=vs'
        result = self.call(path)
        
        if result:
            try:
                deserialized_result = result
                return deserialized_result.get(b'vs', {})
            except Exception as e:
                print(f"Deserialization failed: {e}")
                return {}
        else:
            return {}

    def manage_vps(self, post):
        post['theme_edit'] = 1
        post['editvps'] = 1
        path = f'index.php?act=managevps&vpsid={post["vpsid"]}'
        result = self.call(path, post=post)
        
        if result:
            return {
                'title': result.get(b'title').decode('utf-8'),
                'done': result.get(b'done', False),
                'error': [err.decode('utf-8') for err in result.get(b'error', [])],
                'vs_info': result.get(b'vps'),
                'vps_data': result.get(b'vps_data')
            }
        else:
            return None

def add_bandwidth_to_vps(datacenter, ip_address, additional_bandwidth):
    try:
        # Find the SlaveServer instance associated with the datacenter
        slave_server = SlaveServer.objects.get(datacenter=datacenter)

        # Initialize the API
        api = VirtualizorAdminAPI(slave_server.ip_address, slave_server.api_key, slave_server.api_pass)

        # Fetch VPS info to find the correct VPS by IP address
        vps_list = api.list_vs()
        
        target_vps = None

        for vps_data in vps_list.values():
            vps_ips = [ip.decode('utf-8') for ip in vps_data[b'ips'].values()]
            if ip_address in vps_ips:
                target_vps = vps_data
                break

        if not target_vps:
            return {"success": False, "error": "VPS with the specified IP address not found"}

        # Extract current bandwidth and calculate the new bandwidth
        current_bandwidth = float(target_vps.get(b'bandwidth', b'0').decode('utf-8'))
        new_bandwidth = current_bandwidth + additional_bandwidth

        # Prepare data for API call to update the bandwidth
        post_data = {
            "vpsid": target_vps[b'vpsid'].decode('utf-8'),
            "bandwidth": new_bandwidth
        }

        # Use the manage_vps method to send the updated bandwidth
        response = api.manage_vps(post_data)

        if response and response.get('error'):
            return {"success": False, "error": response['error']}

        # Update the VpsInfo in the database
        try:
            vps_info = VpsInfo.objects.get(vps_id=post_data['vpsid'], ip=ip_address)
            vps_info.limit_bandwidth = int(new_bandwidth)
            vps_info.save()
        except ObjectDoesNotExist:
            return {"success": False, "error": "VPS Info record not found in the database"}

        return {"success": True, "message": "Bandwidth updated successfully"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
