import ipaddress


def verify_ip_in_subnet(ip, subnet):
    ip = ipaddress.ip_address(ip)
    subnet = ipaddress.ip_network(subnet)
    return ip in subnet


def generate_ip(subnet, last_index):
    network = ipaddress.ip_network(subnet)
    new_ip = network.network_address + last_index
    return str(new_ip)