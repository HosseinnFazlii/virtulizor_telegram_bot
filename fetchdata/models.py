from django.db import models

# Model for Datacenter
class Datacenter(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Model for SlaveServer
class SlaveServer(models.Model):
    api_key = models.CharField(max_length=255)
    api_pass = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    datacenter = models.ForeignKey(Datacenter, on_delete=models.CASCADE, related_name='slave_servers')

    def __str__(self):
        return f"{self.ip_address} - {self.datacenter.name}"

    class Meta:
        verbose_name = "Slave Server"
        verbose_name_plural = "Slave Servers"


class VpsInfo(models.Model):
    vps_id = models.CharField(max_length=255, unique=True)
    datacenter = models.ForeignKey(Datacenter, on_delete=models.CASCADE, related_name='vps_info')
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    limit_bandwidth = models.BigIntegerField(help_text="Limit bandwidth in MB or GB")
    used_bandwidth = models.BigIntegerField(help_text="Used bandwidth in MB or GB")
    username = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"VPS {self.vps_id} - {self.datacenter.name}"

    class Meta:
        verbose_name = "VPS Info"
        verbose_name_plural = "VPS Info"