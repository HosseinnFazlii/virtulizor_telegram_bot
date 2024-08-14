import requests
import hashlib
import base64
import re
import pickle

class c:
    def __init__(self, ip, key, password, port=4085):
        self.key = key
        self.password = password
        self.ip = ip
        self.port = port
        self.protocol = 'https' if port == 4085 else 'http'
        self.error = []

    def r(self, data):
        print(data)

    def _unserialize(self, string):
        try:
            var = pickle.loads(string)
        except:
            var = None
        if not var:
            matches = re.findall(r's:(\d+):"(.*?)";', string)
            for mk, mv in matches:
                tmp_str = f's:{len(mv)}:"{mv}";'
                string = string.replace(matches[0][mk], tmp_str)
            try:
                var = pickle.loads(string)
            except:
                var = None
        return var

    def make_apikey(self, key, password):
        return key + hashlib.md5((password + key).encode()).hexdigest()

    def generate_rand_str(self, length):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(chars[i % len(chars)] for i in range(length)).lower()

    def call(self, path, data=None, post=None, cookies=None):
        key = self.generate_rand_str(8)
        apikey = self.make_apikey(key, self.password)
        url = f"{self.protocol}://{self.ip}:{self.port}/{path}"
        url += '&adminapikey=' + requests.utils.quote(self.key)
        url += '&adminapipass=' + requests.utils.quote(self.password)
        url += '&api=serialize&apikey=' + requests.utils.quote(apikey)
        if data:
            url += '&apidata=' + requests.utils.quote(base64.b64encode(pickle.dumps(data)).decode())
        headers = {'User-Agent': 'Softaculous'}
        if post:
            response = requests.post(url, data=post, cookies=cookies, headers=headers, verify=False)
        else:
            response = requests.get(url, cookies=cookies, headers=headers, verify=False)
        if response.status_code != 200:
            return False
        resp = response.content.strip()
        result = self._unserialize(resp)
        return result if result else False

    def add_ip_pool(self, post):
        post['addippool'] = 1
        path = 'index.php?act=addippool'
        return self.call(path, post=post)

    def add_ips(self, post):
        post['submitip'] = 1
        path = 'index.php?act=addips'
        return self.call(path, post=post)

    def add_iso(self, post):
        post['addiso'] = 1
        path = 'index.php?act=addiso'
        return self.call(path, post=post)

    def delete_iso(self, post):
        path = 'index.php?act=iso'
        return self.call(path, post=post)

    def add_plan(self, post):
        post['addplan'] = 1
        path = 'index.php?act=addplan'
        return self.call(path, post=post)

    def media_groups(self, page=1, reslen=50, post=None):
        if not post:
            path = 'index.php?act=mediagroups'
            return self.call(path)
        else:
            path = f'index.php?act=mediagroups&mgid={post["mgid"]}&mg_name={post["mg_name"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def add_server(self, post):
        post['addserver'] = 1
        path = 'index.php?act=addserver'
        return self.call(path, post=post)

    def server_groups(self, post=None):
        path = 'index.php?act=servergroups'
        return self.call(path, post=post)

    def add_template(self, post):
        post['addtemplate'] = 1
        path = 'index.php?act=addtemplate'
        return self.call(path, post=post)

    def add_user(self, post=None):
        path = 'index.php?act=adduser'
        return self.call(path, post=post)

    def add_vs(self, post, cookies=None):
        path = 'index.php?act=addvs'
        post = self.clean_post(post)
        result = self.call(path, post=post, cookies=cookies)
        return {
            'title': result['title'],
            'error': result.get('error', []),
            'vs_info': result['newvs'],
            'globals': result['globals']
        }

    def add_vs_v2(self, post, cookies=None):
        path = 'index.php?act=addvs'
        post['addvps'] = 1
        post['node_select'] = 1
        result = self.call(path, post=post, cookies=cookies)
        return {
            'title': result['title'],
            'error': result.get('error', []),
            'vs_info': result['newvs'],
            'globals': result['globals'],
            'done': result['done']
        }

    def add_ip_range(self, post):
        path = 'index.php?act=addiprange'
        return self.call(path, post=post)

    def edit_ip_range(self, post):
        path = f'index.php?act=editiprange&ipid={post["ipid"]}'
        return self.call(path, post=post)

    def ip_range(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=ipranges&page={page}&reslen={reslen}'
            return self.call(path)
        elif 'delete' in post:
            path = 'index.php?act=ipranges'
            return self.call(path, post=post)
        else:
            path = f'index.php?act=ipranges&ipsearch={post["ipsearch"]}&ippoolsearch={post["ippoolsearch"]}&lockedsearch={post["lockedsearch"]}&ippid={post["ippid"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def add_sg(self, post):
        post['addsg'] = 1
        path = 'index.php?act=addsg'
        return self.call(path, post=post)

    def edit_sg(self, post):
        post['editsg'] = 1
        path = f'index.php?act=editsg&sgid={post["sgid"]}'
        return self.call(path, post=post)

    def delete_sg(self, post):
        path = 'index.php?act=servergroups'
        return self.call(path, post=post)

    def list_backup_plans(self, page=1, reslen=50, post=None):
        path = f'index.php?act=backup_plans&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def add_backup_plan(self, post):
        post['addbackup_plan'] = 1
        path = 'index.php?act=addbackup_plan'
        return self.call(path, post=post)

    def edit_backup_plan(self, post):
        post['editbackup_plan'] = 1
        path = 'index.php?act=editbackup_plan'
        return self.call(path, post=post)

    def delete_backup_plan(self, post):
        path = 'index.php?act=backup_plans'
        result = self.call(path, post=post)
        del result['backup_plans']
        return result

    def backup_servers(self, page=1, reslen=50, post=None):
        path = f'index.php?act=backupservers&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def delete_backup_servers(self, post):
        path = 'index.php?act=backupservers'
        return self.call(path, post=post)

    def test_backup_servers(self, post):
        path = 'index.php?act=backupservers'
        return self.call(path, post=post)

    def add_backup_server(self, post):
        post['addbackupserver'] = 1
        path = 'index.php?act=addbackupserver'
        return self.call(path, post=post)

    def edit_backup_server(self, post):
        post['editbackupserver'] = 1
        path = f'index.php?act=editbackupserver&id={post["id"]}'
        return self.call(path, post=post)

    def add_storage(self, post):
        post['addstorage'] = 1
        path = 'index.php?act=addstorage'
        return self.call(path, post=post)

    def storages(self, post=None, page=1, reslen=50):
        path = f'index.php?act=storage&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def edit_storage(self, post):
        post['editstorage'] = 1
        path = f'index.php?act=editstorage&stid={post["stid"]}'
        return self.call(path, post=post)

    def orphaned_disks(self, post=None):
        path = 'index.php?act=orphaneddisks'
        return self.call(path, post=post)

    def add_dns_plan(self, post):
        post['adddnsplan'] = 1
        path = 'index.php?act=adddnsplan'
        return self.call(path, post=post)

    def list_dns_plans(self, page=1, reslen=50, post=None):
        if not post or 'planname' not in post:
            path = 'index.php?act=dnsplans'
        else:
            path = f'index.php?act=dnsplans&planname={requests.utils.quote(post["planname"])}&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def edit_dns_plans(self, post):
        post['editdnsplan'] = 1
        path = f'index.php?act=editdnsplan&dnsplid={post["dnsplid"]}'
        return self.call(path, post=post)

    def delete_dns_plans(self, post):
        path = 'index.php?act=dnsplans'
        return self.call(path, post=post)

    def add_admin_acl(self, post):
        path = 'index.php?act=add_admin_acl'
        return self.call(path, post=post)

    def admin_acl(self, post=None):
        path = 'index.php?act=admin_acl'
        return self.call(path, post=post)

    def edit_admin_acl(self, post):
        path = f'index.php?act=edit_admin_acl&aclid={post["aclid"]}'
        return self.call(path, post=post)

    def add_mg(self, post):
        post['addmg'] = 1
        path = 'index.php?act=addmg'
        return self.call(path, post=post)

    def edit_mg(self, post):
        post['editmg'] = 1
        path = f'index.php?act=editmg&mgid={post["mgid"]}'
        return self.call(path, post=post)

    def delete_mg(self, post):
        path = f'index.php?act=mediagroups&delete={post["delete"]}'
        return self.call(path, post=post)

    def add_distro(self, post):
        post['add_distro'] = 1
        path = 'index.php?act=add_distro'
        return self.call(path, post=post)

    def edit_distro(self, post):
        post['add_distro'] = 1
        path = f'index.php?act=add_distro&edit={post["edit"]}'
        return self.call(path, post=post)

    def list_distros(self, post=None):
        if not post:
            path = 'index.php?act=list_distros'
        else:
            path = f'index.php?act=list_distros&delete={post["delete"]}'
        return self.call(path, post=post)

    def list_eu_iso(self, page=1, reslen=50, post=None):
        path = f'index.php?act=euiso&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def delete_eu_iso(self, post):
        path = 'index.php?act=euiso'
        return self.call(path, post=post)

    def list_recipes(self, page=1, reslen=50, post=None):
        if 'rid' not in post:
            path = f'index.php?act=recipes&page={page}&reslen={reslen}'
        else:
            path = f'index.php?act=recipes&rid={post["rid"]}&rname={post["rname"]}&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def add_recipes(self, post):
        post['addrecipe'] = 1
        path = 'index.php?act=addrecipe'
        return self.call(path, post=post)

    def edit_recipe(self, post):
        post['editrecipe'] = 1
        path = f'index.php?act=editrecipe&rid={post["rid"]}'
        return self.call(path, post=post)

    def recipes(self, post):
        path = 'index.php?act=recipes'
        return self.call(path, post=post)

    def tasks(self, page=1, reslen=50, post=None):
        if not post or 'show_logs' in post:
            path = f'index.php?act=tasks&page={page}&reslen={reslen}'
        else:
            path = f'index.php?act=tasks&actid={post["actid"]}&vpsid={post["vpsid"]}&username={post["username"]}&action={post["action"]}&status={post["status"]}&order={post["order"]}&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def add_pdns(self, post):
        post['addpdns'] = 1
        path = 'index.php?act=addpdns'
        return self.call(path, post=post)

    def admin_index(self):
        path = 'index.php?act=adminindex'
        return self.call(path)

    def api_doings(self):
        pass

    def backup(self, post):
        path = 'index.php?act=backup'
        return self.call(path, post=post)

    def bandwidth(self, post=None):
        if not post:
            path = 'index.php?act=bandwidth'
            return self.call(path)
        else:
            path = f'index.php?act=bandwidth&show={post["show"]}'
            return self.call(path, post=post)

    def clean_post(self, post, edit=0):
        post['serid'] = int(post.get('serid', 0))
        post['uid'] = int(post.get('uid', 0))
        post['plid'] = int(post.get('plid', 0))
        post['osid'] = int(post.get('osid', 0))
        post['iso'] = int(post.get('iso', 0))
        post['space'] = post.get('space', 10)
        post['ram'] = int(post.get('ram', 512))
        post['swapram'] = int(post.get('swapram', 1024))
        post['bandwidth'] = int(post.get('bandwidth', 0))
        post['network_speed'] = int(post.get('network_speed', 0))
        post['cpu'] = int(post.get('cpu', 1000))
        post['cores'] = int(post.get('cores', 4))
        post['cpu_percent'] = int(post.get('cpu_percent', 100))
        post['vnc'] = int(post.get('vnc', 1))
        post['vncpass'] = post.get('vncpass', 'test')
        post['sec_iso'] = int(post.get('sec_iso', 0))
        post['kvm_cache'] = int(post.get('kvm_cache', 0))
        post['io_mode'] = int(post.get('io_mode', 0))
        post['vnc_keymap'] = post.get('vnc_keymap', 'en-us')
        post['nic_type'] = post.get('nic_type', 'default')
        post['osreinstall_limit'] = int(post.get('osreinstall_limit', 0))
        post['mgs'] = post.get('mgs', 0)
        post['tuntap'] = post.get('tuntap', 0)
        post['virtio'] = post.get('virtio', 0)
        post['noemail'] = int(post.get('noemail', 0))
        post['boot'] = post.get('boot', 'dca')
        post['band_suspend'] = int(post.get('band_suspend', 0))
        post['vif_type'] = post.get('vif_type', 'netfront')
        if edit == 0:
            post['addvps'] = int(post.get('addvps', 1))
        else:
            post['editvps'] = int(post.get('editvps', 1))
            post['acpi'] = post.get('acpi', 1)
            post['apic'] = post.get('apic', 1)
            post['pae'] = post.get('pae', 1)
            post['dns'] = post.get('dns', ['4.2.2.1', '4.2.2.2'])
            post['editvps'] = int(post.get('editvps', 1))
        return post

    def cluster(self):
        pass

    def config(self, post=None):
        path = 'index.php?act=config'
        return self.call(path, post=post)

    def config_slave(self, post=None):
        path = 'index.php?act=config_slave'
        if post and 'serid' in post:
            path += f'&changeserid={post["serid"]}'
        return self.call(path, post=post)

    def cpu(self, serverid=0):
        path = f'index.php?act=manageserver&changeserid={serverid}'
        result = self.call(path)
        return result['usage']['cpu']

    def server_loads(self, post=None):
        path = 'index.php?act=serverloads'
        return self.call(path, post=post)

    def create_ssl(self, post):
        path = 'index.php?act=createssl'
        return self.call(path, post=post)

    def lets_encrypt(self, post):
        path = 'index.php?act=letsencrypt'
        return self.call(path, post=post)

    def create_template(self, post):
        path = 'index.php?act=createtemplate'
        post['createtemp'] = 1
        return self.call(path, post=post)

    def server_stats(self, post=None):
        path = f'index.php?act=server_stats'
        if post and 'serid' in post:
            path += f'&changeserid={post["serid"]}'
        return self.call(path, post=post)

    def vps_stats(self, post=None):
        path = f'index.php?act=vps_stats'
        if post and 'serid' in post:
            path += f'&changeserid={post["serid"]}'
        if post and 'page' in post and 'reslen' in post:
            path += f'&page={post["page"]}&reslen={post["reslen"]}'
        result = self.call(path, post=post)
        if 'vps_data' in result and isinstance(result['vps_data'], dict):
            tmp_vpsdata = {k.replace('K_', ''): v for k, v in result['vps_data'].items()}
            result['vps_data'] = tmp_vpsdata
        return result

    def data_backup(self, post):
        path = 'index.php?act=databackup'
        return self.call(path, post=post)

    def list_db_back_files(self):
        path = 'index.php?act=databackup'
        return self.call(path)

    def create_vps_backup(self, post):
        path = 'index.php?act=editbackup_plan'
        if 'vpsid' in post:
            path = f'index.php?act=managevps&vpsid={post["vpsid"]}'
            post = {}
            post['cbackup'] = 1
        return self.call(path, post=post)

    def vps_backup_list(self, post):
        path = f'index.php?act=vpsrestore&op=get_vps&vpsid={post["vpsid"]}'
        if 'serid' in post:
            path += f'&changeserid={post["serid"]}'
        return self.call(path, post=post)

    def vps_restore(self, post):
        post['restore'] = 1
        path = 'index.php?act=vpsrestore'
        if 'serid' in post:
            path += f'&changeserid={post["serid"]}'
        result = self.call(path, post=post)
        del result['restore_details']
        return result

    def delete_vps_backup(self, post):
        path = 'index.php?act=vpsrestore'
        return self.call(path, post=post)

    def pdns(self, page, reslen, post=None):
        if not post:
            path = f'index.php?act=pdns&page={page}&reslen={reslen}'
            return self.call(path)
        elif 'test' in post:
            path = f'index.php?act=pdns&test={post["test"]}'
            return self.call(path)
        elif 'delete' in post:
            path = 'index.php?act=pdns'
            return self.call(path, post=post)
        else:
            path = f'index.php?act=pdns&pdns_name={requests.utils.quote(post["pdns_name"])}&pdns_ipaddress={post["pdns_ipaddress"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def rdns(self, post=None):
        path = 'index.php?act=rdns'
        return self.call(path, post=post)

    def domains(self, page=1, reslen=50, post=None):
        path = f'index.php?act=domains&pdnsid={post["pdnsid"]}&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def delete_dns_records(self, post):
        path = f'index.php?act=dnsrecords&pdnsid={post["pdnsid"]}'
        return self.call(path, post=post)

    def dns_records(self, page=1, reslen=50, post=None):
        if 'del' not in post:
            path = f'index.php?act=dnsrecords&pdnsid={post["pdnsid"]}&domain_id={post["domain_id"]}&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=dnsrecords&pdnsid={post["pdnsid"]}&domain_id={post["domain_id"]}'
            return self.call(path, post=post)

    def search_dns_records(self, page=1, reslen=50, post=None):
        path = f'index.php?act=dnsrecords&pdnsid={post["pdnsid"]}&domain_id={post["domain_id"]}&dns_name={post["dns_name"]}&dns_domain={post["dns_domain"]}&record_type={post["record_type"]}&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def add_dns_record(self, post):
        post['add_dnsrecord'] = 1
        path = f'index.php?act=add_dnsrecord&pdnsid={post["pdnsid"]}'
        return self.call(path, post=post)

    def edit_dns_record(self, post):
        post['add_dnsrecord'] = 1
        path = f'index.php?act=add_dnsrecord&pdnsid={post["pdnsid"]}&edit={post["edit"]}'
        return self.call(path, post=post)

    def edit_pdns(self, post):
        post['editpdns'] = 1
        path = f'index.php?act=editpdns&pdnsid={post["pdnsid"]}'
        return self.call(path, post=post)

    def default_vs_conf(self, post):
        path = 'index.php?act=defaultvsconf'
        return self.call(path, post=post)

    def delete_vs(self, vid):
        path = f'index.php?act=vs&delete={vid}'
        return self.call(path)

    def sso(self):
        result = self.call('index.php?act=sso')
        url = f'https://{self.ip}:{self.port}/{result["token_key"]}/?as={result["sid"]}'
        return url if result['token_key'] and result['sid'] else False

    def disk(self, serverid=0):
        path = f'index.php?act=manageserver&changeserid={serverid}'
        result = self.call(path)
        return result['usage']['disk']

    def webuzo(self, post):
        post['webuzo'] = 1
        path = 'index.php?act=webuzo'
        return self.call(path, post=post)

    def webuzo_scripts(self):
        path = 'index.php?act=webuzo'
        return self.call(path)

    def edit_email_temp(self, post):
        path = f'index.php?act=editemailtemp&temp={post["temp"]}'
        return self.call(path, post=post)

    def reset_email_temp(self, post):
        path = f'index.php?act=editemailtemp&temp={post["temp"]}&reset={post["reset"]}'
        return self.call(path)

    def billing_settings(self, post):
        post['editsettings'] = 1
        path = 'index.php?act=billing'
        return self.call(path, post=post)

    def resource_pricing(self, post):
        post['editsettings'] = 1
        path = 'index.php?act=resource_pricing'
        return self.call(path, post=post)

    def add_invoice(self, post):
        post['addinvoice'] = 1
        path = 'index.php?act=addinvoice'
        return self.call(path, post=post)

    def edit_invoice(self, post):
        post['editinvoice'] = 1
        path = f'index.php?act=editinvoice&invoid={post["invoid"]}'
        return self.call(path, post=post)

    def list_invoice(self, page=1, reslen=50, post=None):
        path = f'index.php?act=invoices&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def delete_invoice(self, post):
        path = 'index.php?act=invoices'
        return self.call(path, post=post)

    def add_transaction(self, post):
        post['addtransaction'] = 1
        path = 'index.php?act=addtransaction'
        return self.call(path, post=post)

    def edit_transaction(self, post):
        post['edittransaction'] = 1
        path = f'index.php?act=edittransaction&trid={post["trid"]}'
        return self.call(path, post=post)

    def list_transaction(self, page=1, reslen=50, post=None):
        path = f'index.php?act=transactions&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def delete_transactions(self, post):
        path = 'index.php?act=transactions'
        return self.call(path, post=post)

    def edit_ip_pool(self, post):
        post['editippool'] = 1
        path = f'index.php?act=editippool&ippid={post["ippid"]}'
        return self.call(path, post=post)

    def delete_ip_pool(self, ippid):
        path = 'index.php?act=ippool'
        return self.call(path, post=ippid)

    def edit_ips(self, post):
        path = 'index.php?act=editips'
        return self.call(path, post=post)

    def delete_ips(self, post):
        path = 'index.php?act=ips'
        return self.call(path, post=post)

    def edit_plan(self, post):
        post['editplan'] = 1
        path = f'index.php?act=editplan&plid={post["plid"]}'
        return self.call(path, post=post)

    def edit_server(self, post):
        post['editserver'] = 1
        path = f'index.php?act=editserver&serid={post["serid"]}'
        return self.call(path, post=post)

    def edit_template(self, post):
        path = f'index.php?act=edittemplate&osid={post["osid"]}'
        post['edittemplate'] = 1
        return self.call(path, post=post)

    def edit_user(self, post):
        path = f'index.php?act=edituser&uid={post["uid"]}'
        return self.call(path, post=post)

    def sync_os_template(self, post):
        path = 'index.php?act=ostemplates'
        return self.call(path, post=post)

    def edit_vs(self, post, cookies=None):
        post['editvps'] = 1
        path = f'index.php?act=editvs&vpsid={post["vpsid"]}'
        result = self.call(path, post=post, cookies=cookies)
        return {
            'title': result['title'],
            'done': result['done'],
            'error': result.get('error', []),
            'vs_info': result['vps']
        }

    def manage_vps(self, post):
        post['theme_edit'] = 1
        post['editvps'] = 1
        path = f'index.php?act=managevps&vpsid={post["vpsid"]}'
        result = self.call(path, post=post)
        return {
            'title': result['title'],
            'done': result['done'],
            'error': result.get('error', []),
            'vs_info': result['vps'],
            'vps_data': result['vps_data']
        }

    def create_single_vps_backup(self, vpsid):
        path = f'index.php?act=managevps&cbackup=1&vpsid={vpsid}'
        return self.call(path)

    def email_config(self, post):
        path = 'index.php?act=emailconfig'
        return self.call(path, post=post)

    def email_temp(self, post=None):
        path = 'index.php?act=emailtemp'
        return self.call(path, post=post)

    def file_manager(self, post):
        path = 'index.php?act=filemanager'
        return self.call(path, post=post)

    def firewall(self, post):
        path = 'index.php?act=firewall'
        return self.call(path, post=post)

    def give_os(self):
        pass

    def health(self):
        pass

    def hostname(self, post):
        path = 'index.php?act=hostname'
        return self.call(path, post=post)

    def import_data(self, post):
        path = f'index.php?act=import&sa={post["sa"]}'
        if 'ta' in post:
            path += f'&ta={post["ta"]}'
        path += f'&changeserid={post["changeserid"]}'
        return self.call(path, post=post)

    def import_solusvm(self, post):
        valid_ta = ['nodes', 'nodegroups', 'plans', 'users', 'ips', 'os', 'vps']
        if 'ta' not in post or post['ta'] not in valid_ta:
            return False
        post['sa'] = 'solusvm'
        result = self.import_data(post)
        ta_map = {'ips': 'ipblock', 'os': 'templates'}
        for k, v in result.items():
            if k in ['title', 'error', 'done', 'timenow', 'time_taken']:
                continue
            if (not ta_map.get(post['ta']) and not re.search(post['ta'], k)) or not re.search(ta_map[post['ta']], k):
                del result[k]
        return result

    def import_proxmox(self, post):
        valid_ta = ['nodes', 'users', 'storages', 'vps']
        if 'ta' not in post or post['ta'] not in valid_ta:
            return False
        post['sa'] = 'proxmox'
        result = self.import_data(post)
        ta_map = {'ips': 'ipblock', 'os': 'templates'}
        for k, v in result.items():
            if k in ['title', 'error', 'done', 'timenow', 'time_taken']:
                continue
            if (not ta_map.get(post['ta']) and not re.search(post['ta'], k)) or not re.search(ta_map[post['ta']], k):
                del result[k]
        return result

    def import_feathur(self, post):
        valid_ta = ['nodes', 'users', 'ips', 'os', 'vps']
        if 'ta' not in post or post['ta'] not in valid_ta:
            return False
        post['sa'] = 'feathur'
        result = self.import_data(post)
        ta_map = {'ips': 'ipblock', 'os': 'templates'}
        for k, v in result.items():
            if k in ['title', 'error', 'done', 'timenow', 'time_taken']:
                continue
            if (not ta_map.get(post['ta']) and not re.search(post['ta'], k)) or not re.search(ta_map[post['ta']], k):
                del result[k]
        return result

    def import_hypervm(self, post):
        valid_ta = ['nodes', 'plans', 'users', 'ips', 'os', 'vps']
        if 'ta' not in post or post['ta'] not in valid_ta:
            return False
        post['sa'] = 'hypervm'
        result = self.import_data(post)
        ta_map = {'ips': 'ipblock', 'os': 'templates'}
        for k, v in result.items():
            if k in ['title', 'error', 'done', 'timenow', 'time_taken']:
                continue
            if (not ta_map.get(post['ta']) and not re.search(post['ta'], k)) or not re.search(ta_map[post['ta']], k):
                del result[k]
        return result

    def import_openvz(self, post):
        post['sa'] = 'openvz'
        return self.import_data(post)

    def import_kvm(self, post):
        post['sa'] = 'kvm'
        return self.import_data(post)

    def import_xen(self, post):
        post['sa'] = 'xen'
        return self.import_data(post)

    def import_xcp(self, post):
        post['sa'] = 'xcp'
        return self.import_data(post)

    def import_openvz7(self, post):
        post['sa'] = 'openvz7'
        return self.import_data(post)

    def ip_pool(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=ippool&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            if 'servers_search' not in post or post['servers_search'] == '':
                post['servers_search'] = -1
            path = f'index.php?act=ippool&poolname={requests.utils.quote(post["poolname"])}&poolgateway={post["poolgateway"]}&netmask={post["netmask"]}&nameserver={post["nameserver"]}&servers_search={post["servers_search"]}&page={page}&reslen={reslen}'
            return self.call(path)

    def ips(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=ips&page={page}&reslen={reslen}'
        else:
            if 'servers_search' not in post or post['servers_search'] == '':
                post['servers_search'] = -1
            path = f'index.php?act=ips&ipsearch={post["ipsearch"]}&ippoolsearch={post["ippoolsearch"]}&macsearch={post["macsearch"]}&vps_search={post["vps_search"]}&servers_search={post["servers_search"]}&lockedsearch={post["lockedsearch"]}&ippid={post["ippid"]}&page={page}&reslen={reslen}'
        result = self.call(path)
        tmp_ippool = {}
        if 'ips' in result:
            for ip in result['ips']:
                if 'ippid' in ip:
                    tmp_ippool[ip['ippid']] = result['ippools'][ip['ippid']]
        result['ippools'] = tmp_ippool
        return result

    def iso(self):
        path = 'index.php?act=iso'
        return self.call(path)

    def kernel_conf(self, post=None):
        path = 'index.php?act=kernelconf'
        return self.call(path, post=post)

    def license(self):
        path = 'index.php?act=license'
        return self.call(path)

    def list_vs(self, page=1, reslen=50, search=None):
        if not search:
            path = f'index.php?act=vs&page={page}&reslen={reslen}'
        else:
            path = f'index.php?act=vs&search=1&page={page}&reslen={reslen}'
            for k, v in search.items():
                path += f'&{k}={v}'
        result = self.call(path)
        return result['vs']

    def update_vps_net_rules(self, vpsid):
        if vpsid:
            path = f'index.php?act=vs&action=vs_netrestrict&vpsid={vpsid}'
            return self.call(path)

    def login(self):
        pass

    def login_logs(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=loginlogs&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=loginlogs&username={post["username"]}&ip={post["ip"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def logs(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=logs&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=logs&id={post["id"]}&email={post["email"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def maintenance(self, post):
        path = 'index.php?act=maintenance'
        return self.call(path, post=post)

    def make_slave(self):
        pass

    def os(self, post=None):
        if not post:
            path = 'index.php?act=os'
        else:
            path = f'index.php?act=os&getos={post["osids"][0]}'
        return self.call(path, post=post)

    def os_templates(self, page=1, reslen=50):
        path = f'index.php?act=ostemplates&page={page}&reslen={reslen}'
        return self.call(path)

    def delete_os_templates(self, post):
        path = f'index.php?act=ostemplates&delete={post["delete"]}'
        result = self.call(path)
        return {
            'title': result['title'],
            'done': result['done'],
            'ostemplates': result['ostemplates']
        }

    def performance(self, serid, option=""):
        path = f'index.php?act=performance&changeserid={serid}'
        if option == 'network_stats':
            path += '&network_stats=1'
        elif option == 'live_stats':
            path += '&ajax=true'
        return self.call(path)

    def php_my_admin(self):
        pass

    def plans(self, page=1, reslen=50, search=None):
        if not search:
            path = f'index.php?act=plans&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=plans&planname={requests.utils.quote(search["planname"])}&ptype={search["ptype"]}&page={page}&reslen={reslen}'
            return self.call(path)

    def sort_plans(self, page=1, reslen=50, sort=None):
        path = f'index.php?act=plans&sortcolumn={sort["sortcolumn"]}&sortby={sort["sortby"]}&page={page}&reslen={reslen}'
        return self.call(path)

    def delete_plans(self, post):
        path = f'index.php?act=plans&delete={post["delete"]}'
        return self.call(path)

    def list_user_plans(self, post=None, page=1, reslen=50):
        path = f'index.php?act=user_plans&page={page}&reslen={reslen}'
        return self.call(path, post=post)

    def add_user_plans(self, post):
        post['adduser_plans'] = 1
        path = 'index.php?act=adduser_plans'
        return self.call(path, post=post)

    def edit_user_plans(self, post):
        post['edituser_plans'] = 1
        path = f'index.php?act=edituser_plans&uplid={post["uplid"]}'
        return self.call(path, post=post)

    def delete_user_plans(self, post):
        path = 'index.php?act=user_plans'
        return self.call(path, post=post)

    def power_off(self, vid):
        path = f'index.php?act=vs&action=poweroff&serid=0&vpsid={vid}'
        return self.call(path)

    def processes(self, post=None):
        path = 'index.php?act=processes'
        return self.call(path, post=post)

    def ram(self, serverid=0):
        path = f'index.php?act=manageserver&changeserid={serverid}'
        result = self.call(path)
        return result['usage']['ram']

    def rebuild(self, post):
        post['reos'] = 1
        vps = self.list_vs(1, 1, {'vpsid': post['vpsid']})
        post['serid'] = vps[post['vpsid']]['serid']
        path = f'index.php?act=rebuild&changeserid={post["serid"]}'
        return self.call(path, post=post)

    def restart(self, vid):
        path = f'index.php?act=vs&action=restart&serid=0&vpsid={vid}'
        return self.call(path)

    def restart_services(self, post):
        post['do'] = 1
        path = f'index.php?act=restartservices&service={post["service"]}&do={post["do"]}'
        return self.call(path, post=post)

    def server_info(self, serid=0):
        path = 'index.php?act=serverinfo'
        if serid:
            path += f'&changeserid={serid}'
        result = self.call(path)
        return {
            'title': result['title'],
            'info': {
                'masterkey': result['info']['masterkey'],
                'path': result['info']['path'],
                'key': result['info']['key'],
                'pass': result['info']['pass'],
                'kernel': result['info']['kernel'],
                'num_vs': result['info']['num_vs'],
                'version': result['info']['version'],
                'patch': result['info']['patch']
            }
        }

    def servers(self, search=None, del_serid=0):
        if del_serid == 0:
            path = 'index.php?act=servers'
            if search:
                path += f'&servername={requests.utils.quote(search["servername"])}&serverip={search["serverip"]}&ptype={search["ptype"]}&search=Search'
        else:
            path = f'index.php?act=servers&delete={del_serid}'
        return self.call(path)

    def server_force_delete(self, del_serid=0):
        if del_serid == 0:
            path = 'index.php?act=servers'
        else:
            path = f'index.php?act=servers&force={del_serid}'
        return self.call(path)

    def list_servers(self):
        path = 'index.php?act=servers'
        return self.call(path)

    def services(self, post=None):
        path = 'index.php?act=services'
        return self.call(path, post=post)

    def ssh(self):
        pass

    def ssl(self, post=None):
        path = 'index.php?act=ssl'
        return self.call(path, post=post)

    def ssl_cert(self):
        pass

    def start(self, vid):
        path = f'index.php?act=vs&action=start&serid=0&vpsid={vid}'
        return self.call(path)

    def stop(self, vid):
        path = f'index.php?act=vs&action=stop&serid=0&vpsid={vid}'
        return self.call(path)

    def status(self, vids):
        path = f'index.php?act=vs&vs_status={",".join(map(str, vids))}'
        result = self.call(path)
        return result['status']

    def suspend(self, vid, post=None):
        path = f'index.php?act=vs&suspend={vid}'
        return self.call(path, post=post)

    def unsuspend(self, vid):
        path = f'index.php?act=vs&unsuspend={vid}'
        return self.call(path)

    def suspend_net(self, vid):
        path = f'index.php?act=vs&suspend_net={vid}'
        return self.call(path)

    def unsuspend_net(self, vid):
        path = f'index.php?act=vs&unsuspend_net={vid}'
        return self.call(path)

    def lock(self, vid, reason=''):
        path = f'index.php?act=vs&action=lock&vpsid={vid}'
        return self.call(path, post={'reason': reason})

    def unlock(self, vid):
        path = f'index.php?act=vs&action=unlock&vpsid={vid}'
        return self.call(path)

    def tools(self):
        pass

    def ubc(self, post):
        path = 'index.php?act=ubc'
        return self.call(path, post=post)

    def updates(self, post):
        path = 'index.php?act=updates'
        return self.call(path, post=post)

    def user_logs(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=userlogs&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=userlogs&vpsid={post["vpsid"]}&email={post["email"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def ip_logs(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=iplogs&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=iplogs&vpsid={post["vpsid"]}&ip={post["ip"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def delete_ip_logs(self, post):
        if post:
            path = 'index.php?act=iplogs'
            return self.call(path, post=post)

    def users(self, page=1, reslen=50, post=None):
        if not post:
            path = f'index.php?act=users&page={page}&reslen={reslen}'
            return self.call(path, post=post)
        else:
            path = f'index.php?act=users&uid={post["uid"]}&email={post["email"]}&type={post["type"]}&page={page}&reslen={reslen}'
            return self.call(path, post=post)

    def delete_users(self, del_userid):
        path = 'index.php?act=users'
        return self.call(path, post=del_userid)

    def vnc(self, post):
        path = f'index.php?act=vnc&novnc={post["novnc"]}'
        return self.call(path, post=post)

    def vs(self, page=1, reslen=50):
        path = f'index.php?act=vs&page={page}&reslen={reslen}'
        return self.call(path)

    def vs_bandwidth(self):
        path = 'index.php?act=vsbandwidth'
        return self.call(path)

    def vs_cpu(self):
        path = 'index.php?act=vscpu'
        return self.call(path)

    def vs_ram(self):
        path = 'index.php?act=vsram'
        return self.call(path)

    def clone_vps(self, post):
        path = 'index.php?act=clone'
        post['migrate'] = 1
        post['migrate_but'] = 1
        return self.call(path, post=post)

    def migrate(self, post):
        path = 'index.php?act=migrate'
        return self.call(path, post=post)

    def haproxy(self, post):
        path = 'index.php?act=haproxy'
        return self.call(path, post=post)

    def list_haproxy(self, search=None, page=1, reslen=50):
        if not search:
            path = f'index.php?act=haproxy&page={page}&reslen={reslen}'
        else:
            path = (f'index.php?act=haproxy&s_id={search["s_id"]}&s_serid={search["s_serid"] or "-1"}&s_vpsid={search["s_vpsid"]}&s_protocol={search["s_protocol"] or "-1"}'
                    f'&s_src_hostname={search["s_src_hostname"]}&s_src_port={search["s_src_port"]}&s_dest_ip={search["s_dest_ip"]}&s_dest_port={search["s_dest_port"]}&haproxysearch={search["haproxysearch"]}')
        result = self.call(path)
        return result['haproxydata']

    def ha(self, sgid=0):
        path = 'index.php?act=ha'
        if sgid:
            path += f'&get_ha_stats={sgid}'
        return self.call(path)

    def reset_bandwidth(self, vpsid):
        path = f'index.php?act=vs&bwreset={vpsid}'
        return self.call(path)

    def generate_keys(self):
        result = self.call('index.php?act=addvs&generate_keys=1')
        return result['new_keys']

    def list_ssh_keys(self, uid):
        if not uid:
            return False
        post = {'uid': uid}
        result = self.call('index.php?act=users&list_ssh_keys=1', post=post)
        return {
            'ssh_keys': result['ssh_keys'],
            'error': result.get('error')
        }

    def add_ssh_keys(self, post):
        if not post['vpsid']:
            return False
        result = self.call(f'index.php?act=managevps&vpsid={post["vpsid"]}&add_ssh_keys=1', post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }

    def list_volumes(self, search=None, page=1, reslen=50):
        if not search:
            path = f'index.php?act=volumes&page={page}&reslen={reslen}'
        else:
            path = f'index.php?act=volumes&search=Search&page={page}&reslen={reslen}'
            if 'disk_name' in search:
                search['disk_name'] = requests.utils.quote(search['disk_name'])
            for k, v in search.items():
                path += f'&{k}={v}'
        result = self.call(path)
        return result['storage_disk']

    def add_volumes(self, post):
        if not post['vpsid']:
            return False
        path = 'index.php?act=volumes'
        result = self.call(path, post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }

    def perform_volumes_actions(self, post):
        if not post['disk_did_action']:
            return False
        path = 'index.php?act=volumes'
        result = self.call(path, post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }

    def delete_volumes(self, post):
        path = 'index.php?act=volumes'
        result = self.call(path, post=post)
        return {
            'done': result.get('done'),
            'error': result.get('error')
        }

    def get_load_balancer(self, page=1, reslen=50, post=None):
        path = f'index.php?act=load_balancer&page={page}&reslen={reslen}'
        if post and 'search' in post:
            path += '&search=1'
            if 'uid' in post:
                path += f'&uid={post["uid"]}'
            if 'hostname' in post:
                path += f'&hostname={post["hostname"]}'
            if 'sgid' in post:
                path += f'&sgid={post["sgid"]}'
        return self.call(path, post=post)

    def delete_load_balancer(self, lb_uuid, delete_added_vm=0):
        path = 'index.php?act=load_balancer'
        post = {'delete_lb': lb_uuid}
        if delete_added_vm:
            post['delete_added_vm'] = delete_added_vm
        return self.call(path, post=post)

    def add_to_load_balancer(self, lb_uuid, vpsid):
        path = 'index.php?act=load_balancer'
        post = {'select_lb': lb_uuid, 'vpsid': vpsid}
        return self.call(path, post=post)

    def manage_load_balancer(self, lb_uuid, post=None):
        path = f'index.php?act=manage_load_balancer&lb_uuid={lb_uuid}'
        return self.call(path, post=post)

    def passthrough_pool(self, search=None, page=1, reslen=50):
        if not search:
            path = f'index.php?act=passthrough&page={page}&reslen={reslen}'
            return self.call(path)
        else:
            path = f'index.php?act=passthrough&pid={search["pid"]}&pname={requests.utils.quote(search["pname"])}&page={page}&reslen={reslen}'
            return self.call(path)

    def get_node_pcis(self):
        path = 'index.php?act=addpassthrough&get_nodePCIs=1'
        return self.call(path)

    def get_node_usbs(self):
        path = 'index.php?act=addpassthrough&get_nodeUSBs=1'
        return self.call(path)

    def add_passthrough(self, post):
        if 'passthrough_type' not in post or (post['passthrough_type'] == 0 and post['usb_key'] < 0):
            return False
        result = self.call('index.php?act=addpassthrough', post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }

    def edit_passthrough(self, post):
        if not post['pid']:
            return False
        result = self.call(f'index.php?act=editpassthrough&pid={post["pid"]}', post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }

    def delete_passthrough(self, post):
        if not post['delete']:
            return False
        result = self.call(f'index.php?act=passthrough&delete={post["delete"]}', post=post)
        return {
            'done': result['done'],
            'error': result.get('error')
        }
