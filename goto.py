#!/usr/bin/env python
# coding=utf-8
# -------------------------------------------------------------
#       LB2 GoTo - SSH Automation
#
#       Autor: Tiago M Reichert
#       Data Inicio:  27/12/2016
#       Data Release: 27/12/2016
#       email: tiago.miguel@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
# --------------------------------------------------------------

import sys
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.constants import load_config_file
import os

def load_ssh_args():
    """
    Read ansible.cfg and get only the the ssh_args parameter
    if defined
    :return: Output of ansible ssh_args
    """
    config, _ = load_config_file()
    # It's easier to ask for forgiveness than permission
    try:
        ssh_section = config._sections['ssh_connection']
        return ssh_section['ssh_args']
    except KeyError:
        return None

class SSHInventory:

    def __init__(self):

        variable_manager = VariableManager()
        loader = DataLoader()
        self.inventory = Inventory(loader=loader, variable_manager=variable_manager)


    def get_host(self, host):
        return self.inventory.get_host(host)

    def get_ssh_cmd(self, host):
        port = "22"
        user = "root"
        options = ""

        if 'ansible_port' in host.vars:
            port = host.vars['ansible_port']

        if 'ansible_ssh_port' in host.vars:
            port = host.vars['ansible_ssh_port']

        if 'ansible_user' in host.vars:
            user = host.vars['ansible_user']

        if 'ansible_ssh_user' in host.vars:
            user = host.vars['ansible_ssh_user']

        ssh_args = load_ssh_args()
        if ssh_args:
            options += ssh_args

        if 'ansible_ssh_private_key_file' in host.vars:
            options += " -i %s" % host.vars['ansible_ssh_private_key_file']

        return "{}@{} {} {}".format(user, host.address, port, options)

def lerEntrada():
    try:
        return input("Choose an option: ")
    except:
        return lerEntrada()

def listarOpcoes(hosts, inv):
    count = 0
    print '0 - SAIR'
    for host in hosts:
        count += 1
        print str(count)+" - %s" % host.name
    escolha = lerEntrada()
    if escolha == 0:
        sys.exit(0)
    try:
        h = hosts[escolha-1]
        v = inv.get_ssh_cmd(h).split(' ')
        try:
            os.execlp('ssh', 'ssh ', v[0], '-p ' + v[1],'-F' + v[3], '-i ' + v[5])
        except:
            os.execlp('ssh', 'ssh', '-i /root/.ssh/id_rsa', v[0], '-p ' + v[1], '-F' + v[3])

    except:
        print 'Favor selecione uma opcao valida'
        listarOpcoes(hosts, inv)

def main(args=None):
    pattern = ''
    if args:
        pattern = args[0]
    inv = SSHInventory()
    hosts = inv.inventory.get_hosts(pattern)
    listarOpcoes(hosts,inv)

if __name__ == '__main__':
    try:
        var = sys.argv[1:]
    except:
        var = None
    main(var)

