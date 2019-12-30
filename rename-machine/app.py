#!/usr/bin/env python3.6

import maas.client
from maas.client.enum import NodeStatus
from xml.etree import ElementTree
import re
import logging
from pprint import pprint

# Rename the machine in MAAS with: switchName-portNumber

# Logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)


# Replace … with an API key previously obtained by hand from
# http://$host:$port/MAAS/account/prefs/.
# client = maas.client.connect(
#     "http://localhost:5240/MAAS/", apikey="…")

maas_host = "http://xx.xx.xx"
maas_port = "5240"
RENAMING = False

# TODO: Timeout connection
# TODO: Connexion Exception
client = maas.client.login(maas_host + ":" + maas_port + "/MAAS/", username="XXX", password="XXX", )

# Get a reference to self.
myself = client.users.whoami()
assert myself.is_admin, "%s is not an admin" % myself.username
message = "Connected as " + myself.username
logging.info(message)

# Check for a MAAS server capability.
version = client.version.get()
assert "devices-management" in version.capabilities

# Check the default OS and distro series for deployments.
# print("Default OS: " + client.maas.get_default_os())
# print("Default OS version: " + client.maas.get_default_distro_series())

# print("Machines:")
all_machines = client.machines.list()

new_machines = [
    machine
    for machine in all_machines
    if machine.status == NodeStatus.NEW
]

print("All machines (", len(all_machines), "):")
for machine in all_machines:
    # print(machine.hostname, machine.fqdn, machine.status, machine.status_action, machine.status_message,
    #       machine.status_name, machine.ip_addresses, sep='__')
    print("-", machine.fqdn, ":", machine.status_name)
    data = machine.get_details()

    try:
        lldp = ElementTree.fromstring(data["lldp"])
        switch = lldp[0][0][1].text.split(".")[0]
        port_name = lldp[0][1][0].text
        port = ''.join(re.findall(r'\d+', port_name))
        new_hostname = switch.lower() + "-" + port

        if machine.hostname != new_hostname and RENAMING is True:
            machine.hostname = new_hostname
            machine.save()
            message = "Renamed" + machine.hostname + "to" + new_hostname
            logging.info(message)
        else:
            message = machine.fqdn + " - nothing to do"
            logging.info(message)
    except TypeError:
        pass
