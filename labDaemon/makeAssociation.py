#!/bin/python3

import iptc,sys

def associate(from_ip, to_ip):
    table_filter = iptc.Table(iptc.Table.FILTER)
    table_filter.Autocommit = False
    table_nat = iptc.Table(iptc.Table.NAT)
    table_nat.Autocommit = False

    chain_filter_FORWARD = iptc.Chain(table_filter, "VPN_FW")
    chain_nat_PREROUTING = iptc.Chain(table_nat, "PREROUTING")
    #"Create iptables rules for relaying vxlan traffic from host A to B. Unidirectional."
    nb_associations = 0

    for rule in chain_filter_FORWARD.rules:
        if rule.src.split('/') == from_ip:
            return False
            #There is already a rule with this address!!

    #Allow traffic from from_ip to to_ip in table filter, chain FORWARD
    rule_fw = iptc.Rule()
    rule_fw.src = from_ip
    rule_fw.dst = to_ip
    rule_fw.protocol = "udp"
    match_fw= rule_fw.create_match('udp')
    match_fw.dport = '4789'
    target_fw = rule_fw.create_target("ACCEPT")
    chain_filter_FORWARD.insert_rule(rule_fw)
    #Searches for associations with A

    #traffic must go through DNAT for each destination association it has
    rule_nat_dnat = iptc.Rule()
    rule_nat_dnat.src = from_ip
    rule_nat_dnat.protocol = "udp"
    match_nat_dnat = rule_nat_dnat.create_match("udp")
    match_nat_dnat.dport = "4789"
    target_nat_dnat = rule_nat_dnat.create_target("DNAT")
    target_nat_dnat.to_destination = to_ip
    chain_nat_PREROUTING.insert_rule(rule_nat_dnat)
    table_filter.commit()
    table_nat.commit()
    table_filter.autocommit = True
    table_nat.autocommit = True
    return True

def delete_association(virt_ip):
    print("deleting association of", virt_ip)
    
    table_filter = iptc.Table(iptc.Table.FILTER)
    chain_filter_VPNFORWARD = iptc.Chain(table_filter, "VPN_FW")
    
    table_filter.refresh()
    table_filter.Autocommit = False
    deleted = True
    while deleted:
        deleted = False
        for fwrule in chain_filter_VPNFORWARD.rules:
            if fwrule.src.split('/')[0]  == virt_ip or fwrule.dst.split('/')[0] == virt_ip:
                chain_filter_VPNFORWARD.delete_rule(fwrule)
                print("FW:putting", str(fwrule), "aside")
                deleted = True
                break
    table_filter.commit()
    table_filter.autocommit = True
    
    table_nat = iptc.Table(iptc.Table.NAT)
    chain_nat_PREROUTING = iptc.Chain(table_nat, "PREROUTING")
    table_nat.refresh() 
    table_nat.Autocommit = False
    
    deleted = True
    while deleted:
        deleted = False
        for natrule in chain_nat_PREROUTING.rules:
            if natrule.src.split("/")[0] == virt_ip \
            or natrule.target.parameters.get("to_destination", "") == virt_ip:
                chain_nat_PREROUTING.delete_rule(natrule)
                print("NAT:putting", str(natrule), "aside")
                deleted = True
                break
    #for rule in nat_to_delete:
    #    chain_nat_PREROUTING.delete_rule(rule)
    table_nat.commit()
    table_nat.autocommit = True
    return True

if __name__ == "__main__":
    nb_args = len(sys.argv)
    if nb_args != 3:
        sys.exit('wrong number of args\nUsage = python3 make_association.py x.x.x.x y.y.y.y')
    ip_A = sys.argv[1]
    ip_B = sys.argv[2]


    if associate(ip_A, ip_B) == False:
        print("Association déjà existante")
    if associate(ip_B, ip_A) == False:
        print("Association déjà existante")
