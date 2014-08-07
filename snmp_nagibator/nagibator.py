#!/usr/bin/env python3
# coding: cp1251


#----------------------------------------------------------------------
# Description: An Scaner SMB-shares account via SNMP in Kyocera printers
# Author:  Artyom Breus <Artyom.Breus@gmail.com>
# Created at: Thu Jul 17 17:02:07 VLAT 2014
# Computer: vostok-ws060.slavyanka.local
#
# Copyright (c) 2014 Artyom Breus  All rights reserved.
#
#----------------------------------------------------------------------




"""
*  This program is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""



from time import time
from pysnmp.entity.rfc3413.oneliner import cmdgen
#from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import ipaddress
# OptParser import Block
from optparse import OptionParser
import socket
import sys
from multiprocessing.dummy import Pool as ThreadPool

# Globals
printers_list 	= []
network 		= []
threads 		= 20
tcp_timeout     = 1
udp_timeout		= 1
retries         = 2
mode 			= 'collect'


def tcpping(host = "127.0.0.1"):
	global tcp_timeout
	port=9103
	rs=True
	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(tcp_timeout)
	try:
		s.connect((host,port))
		s.close()
	except socket.timeout:
		rs=False
	except socket.error:
		rs=False
	except:
		rs=False
		print("INFO:",str(sys.exc_info()))
	return rs

# SNMP requests Block
def get_snmp_mean(address, snmp_oid, proto):
	global timeout, retries
	community='public'
	generator = cmdgen.CommandGenerator().getCmd
	comm_data = cmdgen.CommunityData('public', mpModel = proto) # 0 - v1,1 means version SNMP v2c
	#transport = cmdgen.UdpTransportTarget((address, 161))
	transport = cmdgen.UdpTransportTarget((address, 161),  timeout=udp_timeout, retries=retries )
	#value     = cmdgen.MibVariable(snmp_oid)
	value     =  snmp_oid

	res = (errorIndication, errorStatus, errorIndex, varBinds) = generator(comm_data, transport, value)

	if not errorIndication is None  or errorStatus is True:
	       print("Error: %s %s %s %s" % res)
	       return False
	#print("----- %s" % str(varBinds[0][1]))	
	return str(varBinds[0][1])


def create_printers_list():		
	pl = []
	pool = ThreadPool(threads)
	#print(str(network))
	res = pool.map(tcpping, network)
	pool.close()
	pool.join()
	#print(str(res))
	for x in range(len(res)):
		if res[x]:
			pl.append(network[x])
	return pl


def get_account(printer_host):
	#print('host %s'%printer_host)
	login = ""
	passw = ""	
	cnt = 1
	proto = 0 				# 0 = SNMP v1; 1 = SNMP v2c	
	cnt = 1
	res = []
	while cnt < 10:
		#print('cnt = %d'%cnt)
		#print('v1')		
		login = get_snmp_mean(printer_host,'1.3.6.1.4.1.1347.42.23.2.4.1.1.5.%d.1'%cnt, proto)		
		if not login:	
			#print('v2')			
			login = get_snmp_mean(printer_host,'1.3.6.1.4.1.1347.42.23.2.4.1.1.5.%d.1'%cnt, 1)
		if login:
			#print('OK')		
			passw = get_snmp_mean(printer_host,'1.3.6.1.4.1.1347.42.23.2.4.1.1.6.%d.1'%cnt,proto)		
		else:
			#print('False')
			break
		#print("%s : %s"%(login,passw))
		res.append((printer_host,login,passw))
		cnt += 1		
	return res



def collect_accounts2():
	global printers_list, mode
	accounts = []
	pool = ThreadPool(threads)	
	res = pool.map(get_account, printers_list)
	#res = map(get_account, printers_list)
	pool.close()
	pool.join()
	#print("RES = ",str(res))
	if mode == 'collect':
		for account_list in res:		
			for account in account_list:
				if account[1:] not in accounts:
					accounts.append(account[1:])
	elif mode == 'full':
		for account_list in res:
			for account in account_list:
				if account not in accounts:		
					accounts.append(account)
	return accounts
		

def main():
	global printers_list, mode, network, threads, tcp_timeout, udp_timeout, retries
	parser = OptionParser()
	parser.add_option("-R", "--ip_range", dest="ip_range",
                    help="E.g: 172.21.0.0/24 or 172.21.0.1-172.21.0.254,", metavar="NETWORK")
	parser.add_option("-I", "--ip", dest="ip",
                    help="E.g: 172.21.0.212", metavar="NETADDRESS")
	parser.add_option("-T", "--threads", dest="threads",
                    help="E.g: 20", metavar="THREADS_AMOUNT", default = 20)
	parser.add_option("", "--tcp-timeout", dest="tcp_timeout",
                    help="Timeout for tcp connection (while Kyoceras seek proccess)", metavar="SEC", default = 2)
	parser.add_option("", "--udp-timeout", dest="udp_timeout",	
                    help="Timeout for answer snmp udp request ", metavar="SEC", default = 1.5)
	parser.add_option("", "--retries", dest="retries",
                    help="Retries snmp answer per device", metavar="TIMES", default = 2)
	parser.add_option("-M", "--mode", dest="mode",
                    help="Switch modes: 'collect' - Show all unique accounts in network range ; 'full' - Show all collected info ",
                     metavar="MODE", default = 'collect')


	args = None
	(option, args) = parser.parse_args(args)

	if option.ip_range and option.ip:
		print("Variables -R and -I are not compatabled")
		sys.exit(1)

	if (not option.ip_range and not option.ip):
		parser.print_help()
		sys.exit(0)


	if option.ip_range:
		network = [str(ipaddr) for ipaddr in ipaddress.IPv4Network(option.ip_range)]	
	else:
		network = [option.ip]
	


	threads = int(option.threads)	
	tcp_timeout = float(option.tcp_timeout)
	udp_timeout = float(option.udp_timeout)
	retries     = int(option.retries)
	mode       = option.mode
	if mode not in ('collect','full'):
		print('ERROR: Incorrect MODE')
		sys.exit(1)


	#print(network)
	t1 = time()			
	print('[ MODE: '+ mode + ' ]')
	printers_list = create_printers_list()
	#print("create printers_list ",str(printers_list))	
	accounts = collect_accounts2()
	print(" === [ ACCOUNTS ] ===")
	last_pr = None
	if mode == 'collect':
		for login, passw in accounts:
			print(login,":",passw)
		print("\n\n [ %d RECORDS ]"%len(accounts))
	elif mode == 'full':
		for printer_host, login, passw in accounts:
			if last_pr == printer_host:
				printer_host = "              "
			print(printer_host,"\t\t\t",login,":",passw)
			last_pr = printer_host
		print("\n\n [ %d RECORDS ]"%len(accounts))
	print("\n\n\n\n",time() - t1, " sec")
	return

if __name__ == '__main__':
	main()