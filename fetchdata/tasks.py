import requests
import hashlib
import base64
import random
import string
import urllib.parse
import phpserialize
from django.utils import timezone
from .models import SlaveServer, VpsInfo
from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings
from calendar import monthrange


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
    
    def list_vs(self, reslen=50):
        path = f'index.php?act=vs&reslen={reslen}'
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

def adjust_end_date(original_start_date):
    today = datetime.now()
    adjusted_day = min(original_start_date.day, monthrange(today.year, today.month)[1])  # Ensure day is valid for the new month
    adjusted_start_date = original_start_date.replace(year=today.year, month=today.month, day=adjusted_day)
    return adjusted_start_date + timedelta(days=30)

def fetch_and_save_vps_info(slave_server):
    api = VirtualizorAdminAPI(slave_server.ip_address, slave_server.api_key, slave_server.api_pass)
    vps_list = api.list_vs(reslen=1000)  # Fetch 1000 records instead of the default 50

    for vps_data in vps_list.values():
        vps_id = vps_data.get(b'vpsid').decode('utf-8')
        hostname = vps_data.get(b'hostname').decode('utf-8')

        start_time_unix = int(vps_data.get(b'time').decode('utf-8'))
        start_date = datetime.utcfromtimestamp(start_time_unix)
        new_end_date = adjust_end_date(start_date)

        limit_bandwidth = float(vps_data.get(b'bandwidth', b'0').decode('utf-8'))
        used_bandwidth = float(vps_data.get(b'used_bandwidth', b'0').decode('utf-8'))

        limit_bandwidth = int(limit_bandwidth)
        used_bandwidth = int(used_bandwidth)

        for ip_key, ip_address in vps_data[b'ips'].items():
            ip = ip_address.decode('utf-8')

            vps_info, created = VpsInfo.objects.get_or_create(
                vps_id=vps_id,
                ip=ip,
                datacenter=slave_server.datacenter,
                defaults={
                    'hostname': hostname,
                    'start_date': start_date,
                    'end_date': new_end_date,
                    'limit_bandwidth': limit_bandwidth,
                    'used_bandwidth': used_bandwidth,
                    'username': 'default_username',
                    'telegram_id': 'default_telegram_id',
                    'is_active': True,
                }
            )

            if not created:
                vps_info.hostname = hostname
                vps_info.limit_bandwidth = limit_bandwidth
                vps_info.used_bandwidth = used_bandwidth
                vps_info.save()
                print(f"Updated VPS Info: {vps_info}")
            else:
                print(f"Created new VPS Info: {vps_info}")

@shared_task
def fetch_all_vps_info_task():
    fetch_all_vps_info()

def fetch_all_vps_info():
    for slave_server in SlaveServer.objects.all():
        fetch_and_save_vps_info(slave_server)

@shared_task
def check_vps_expiration_warning_task():
    three_days_from_now = timezone.now() + timedelta(days=3)
    expiring_soon_vps = VpsInfo.objects.filter(end_date__date=three_days_from_now.date(), is_active=True)

    for vps in expiring_soon_vps:
        message = (
            f"⚠️ Your VPS with hostname {vps.hostname} and IP address {vps.ip} "
            f"is going to expire in 3 days. Please take necessary action."
        )
        send_telegram_message(vps.telegram_id, message)

@shared_task
def check_vps_expiration_task():
    today = timezone.now().date()
    expiring_vps = VpsInfo.objects.filter(end_date__date=today, is_active=True)

    for vps in expiring_vps:
        message = (
            f"⚠️ Your VPS with hostname {vps.hostname} and IP address {vps.ip} "
            f"will expire today. Please contact support."
        )
        send_telegram_message(vps.telegram_id, message)

@shared_task
def check_vps_bandwidth_task():
    vps_with_low_bandwidth = VpsInfo.objects.filter(is_active=True)

    for vps in vps_with_low_bandwidth:
        free_bandwidth = vps.limit_bandwidth - vps.used_bandwidth
        if free_bandwidth < 200:  # If less than 200 GB remaining
            message = (
                f"⚠️ Your VPS with hostname {vps.hostname} and IP address {vps.ip} "
                f"is running low on bandwidth. Only {free_bandwidth} GB remaining."
            )
            send_telegram_message(vps.telegram_id, message)

@shared_task
def notify_superadmins_of_expired_vps_task():
    now = timezone.now()
    expired_vps_list = VpsInfo.objects.filter(end_date__lt=now, is_active=True)

    if expired_vps_list.exists():
        message = "The following VPSs have expired:\n"
        for vps in expired_vps_list:
            message += f"Hostname: {vps.hostname}, IP: {vps.ip}, End Date: {vps.end_date.strftime('%Y-%m-%d')}\n"
            vps.is_active = False
            vps.save()

        for telegram_id in settings.SUPERADMIN_TELEGRAM_IDS:
            send_telegram_message(telegram_id, message)

def send_telegram_message(telegram_id, message):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": message
    }
    requests.post(url, data=data)
