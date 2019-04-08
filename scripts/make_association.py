#!/bin/python3

import iptc,sys

nb_args = len(sys.argv)
if nb_args != 3:
    sys.exit('wrong number of args\nUsage = python3 make_association.py x.x.x.x y.y.y.y')
ip_A = sys.argv[1]
ip_B = sys.argv[2]

table_filter = iptc.Table(iptc.Table.FILTER)
table_filter.Autocommit = False
table_mangle = iptc.Table(iptc.Table.MANGLE)
table_mangle.Autocommit = False
table_nat = iptc.Table(iptc.Table.NAT)
table_nat.Autocommit = False

chain_filter_FORWARD = iptc.Chain(table_filter, "VPN_FW")
chain_mangle_PREROUTING = iptc.Chain(table_mangle, "PREROUTING")
chain_nat_PREROUTING = iptc.Chain(table_nat, "PREROUTING")

def associate(from_ip, to_ip):
    "Create iptables rules for relaying vxlan traffic from host A to B. Unidirectional."
    nb_associations = 0

    for rule in chain_filter_FORWARD.rules:
        if rule.src[:len(from_ip)] == from_ip:
            nb_associations = nb_associations + 1
    print("Associations with " + from_ip + " = " + str(nb_associations))
            
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

    #if from_ip has more than one association traffic must be duplicated
    if nb_associations >= 1:
        rule_mangle_tee = iptc.Rule()
        rule_mangle_tee.src = from_ip
        rule_mangle_tee.protocol = "udp"
        match_mangle_tee = rule_mangle_tee.create_match("udp")
        match_mangle_tee.dport = "4789"
        target_mangle_tee = rule_mangle_tee.create_target("TEE")
        target_mangle_tee.gateway = to_ip
        chain_mangle_PREROUTING.insert_rule(rule_mangle_tee)
    
    #traffic must go through DNAT for each destination association it has
    rule_nat_dnat = iptc.Rule()
    rule_nat_dnat.src = from_ip
    rule_nat_dnat.protocol = "udp"
    match_nat_dnat = rule_nat_dnat.create_match("udp")
    match_nat_dnat.dport = "4789"
    if nb_associations >=1:
        match_nat_dnat_stat = rule_nat_dnat.create_match("statistic")
        match_nat_dnat_stat.mode = "nth"
        match_nat_dnat_stat.every = str(nb_associations + 1)
    target_nat_dnat = rule_nat_dnat.create_target("DNAT")
    target_nat_dnat.to_destination = to_ip
    chain_nat_PREROUTING.insert_rule(rule_nat_dnat)
    return





associate(ip_A, ip_B)
associate(ip_B, ip_A)
table_filter.commit()
table_mangle.commit()
table_nat.commit()
