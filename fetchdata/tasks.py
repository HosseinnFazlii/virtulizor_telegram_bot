from .models import VpsInfo , SlaveServer
from .virtulizorAdmin1 import c as VirtualizorAdmin1



class FetchVPSDetailsView():
    def get(self, request):
        vps = VpsInfo.objects.all()
        
        slaveserver=SlaveServer.objects.all()

        for slaveserver in slaveserver:
            virtualizor = VirtualizorAdmin1(slaveserver.ip_address, slaveserver.api_key, slaveserver.api_pass)
            vps_list = virtualizor.list_vs()
            
            for vps_data in vps_list:
                vps_id = vps_data.get('vpsid')
                ip_address = vps_data.get('ip')
                bandwidth_limit = vps_data.get('bandwidth')
                used_bandwidth = vps_data.get('used_bandwidth')

                vps.objects.update_or_create(
                    vps_id=vps_id,
                    
                    defaults={
                        'datacenter':slaveserver.datacenter,
                        'ipaddress': ip_address,
                        'bandwidth_limit': bandwidth_limit,
                        'used_bandwidth': used_bandwidth,
                    }
                )

        # return Response({"status": "success"})