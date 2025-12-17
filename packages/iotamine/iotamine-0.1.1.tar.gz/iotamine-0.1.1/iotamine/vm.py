class VM:
    def __init__(self, client):
        self.client = client

    def create(self, hostname: str, password: str, operating_system: int, pop: int, cores: int, ram: int, disk: int, traffic=5):
        return self.client.request("POST", "/vps/", json={
                                                                "hostname":hostname,
                                                                "password":password,
                                                                "operating_system": operating_system,
                                                                "pop": pop,
                                                                "cores": cores,
                                                                "ram": ram,
                                                                "disk": disk,
                                                                "traffic": traffic
                                                            })

    def list(self):
        return self.client.request("GET", "/vps/")

    def details(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/")

    def start(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/start/")

    def stop(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/stop/")

    def restart(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/restart/")

    def poweroff(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/poweroff/")

    def rebuild(self, vps_id, operating_system, password):
        return self.client.request("POST", f"/vps/{vps_id}/rebuild/", json={
            "osid": operating_system,
            "new_pass": password,
            "conf_pass": password
        })
    
    def stats(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/stats/")
    
    def vnc(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/vnc/")
    
    def list_disk(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/list_disk/")
    
    def add_disk(self, vps_id, size: int):
        return self.client.request("POST", f"/vps/{vps_id}/add_disk/", json={
            "size": size
        })
    
    def delete_disk(self, vps_id, disk_uuid):
        return self.client.request("DELETE", f"/vps/{vps_id}/delete_disk/{disk_uuid}/")
    
    def add_ip(self, vps_id):
        return self.client.request("POST", f"/vps/{vps_id}/add_ip/")
    
    def delete_ip(self, vps_id, ip_addr):
        return self.client.request("DELETE", f"/vps/{vps_id}/delete_ip/{ip_addr}/")
    
    def add_rdns(self, vps_id, ip_addr, rdns):
        return self.client.request("PUT", f"/vps/{vps_id}/ip_address/{ip_addr}/", json={"rdns":rdns})
    
    def list_snapshots(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/listbackup/")
    
    def create_snapshot(self, vps_id):
        return self.client.request("POST", f"/vps/{vps_id}/createbackup/")
    
    def restore_snapshot(self, vps_id, snapshot_id):
        return self.client.request("POST", f"/vps/{vps_id}/restorebackup/", json={"backup_id":snapshot_id})
    
    def delete_snapshot(self, vps_id, snapshot_id):
        return self.client.request("POST", f"/vps/{vps_id}/deletebackup/", json={"backup_id":snapshot_id})
    
    def list_firewall_rules(self, vps_id):
        return self.client.request("GET", f"/vps/{vps_id}/firewall_rules/")
    
    def update_firewall_rules(self, vps_id, rules: dict):
        return self.client.request("POST", f"/vps/{vps_id}/firewall_rules/updateRules/", json=rules)

    def destroy(self, vm_id: str):
        return self.client.request("DELETE", f"/vps/{vm_id}/")
