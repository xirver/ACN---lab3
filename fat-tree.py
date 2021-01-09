# Copyright 2020 Lin Wang

# This code is part of the Advanced Computer Networks (ACN) course at VU 
# Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

#!/usr/bin/env python3

# A dirty workaround to import topo.py from lab2

import os
import subprocess
import time
import mininet
import mininet.clean
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.link import TCLink
from mininet.node import Node, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.util import waitListening, custom

import topo

class FattreeNet(Topo):

	def __init__(self, k):
		self.pod=k
		self.core_switches=(k/2)**2
		self.agg_switches=k*k/2
		self.edge_switches=k*k/2
		self.host=k**3/4
		self.host_pod=self.host/self.edge_switches
		self.core_list=[]
		self.agg_list=[]
		self.edge_list=[]
		self.server_list=[]

		Topo.__init__(self)


	def create_switches(self):
		self.create_core_switches(self.core_switches)
		self.create_agg_switches(self.agg_switches)
		self.create_edge_switches(self.edge_switches)

	def create_servers(self):


		pod=0
		switch=0
		cont_switch=0
		cont_pod=0
		cont_server=1

		for i in range(0,int(self.host)):
			
			if(cont_switch==2):
				switch+=1
				cont_switch=0

			if(cont_pod==4):
				switch=0
				pod+=1
				cont_pod=0

			if(cont_server==3):
				cont_server=1


			ip="10."+str(pod)+"."+str(switch)+"."+str(cont_server)
			self.server_list.append(self.addHost("server"+str(i),ip=ip))

			cont_pod+=1
			cont_server+=1
			cont_switch+=1
	
	def create_core_switches(self, PREFIX):
		self.add_switch(int(self.core_switches), "1", self.core_list)

	def create_agg_switches(self, NUMBER):
		self.add_switch(int(self.agg_switches), "2", self.agg_list)

	def create_edge_switches(self, NUMBER):
		self.add_switch(int(self.edge_switches), "3", self.edge_list)
		 

	def add_switch(self, number, prefix, switch_list):

		if prefix=="1":
			ip_base="10."+str(self.pod)

			for i in range(0, int(number/2)):
				ip=ip_base+".1."+str(i+1)
				switch_list.append(self.addSwitch(prefix + str(i), cls=OVSKernelSwitch,ip=ip))

			for i in range(int(number/2),number):
				ip=ip_base+".1."+str(number/2+i)
				switch_list.append(self.addSwitch(prefix + str(i), cls=OVSKernelSwitch,ip=ip))

		
		elif prefix=="2":

			for i in range(0,number):
				switch_list.append(self.addSwitch(prefix + str(i), cls=OVSKernelSwitch))
		
		elif prefix=="3":
			for i in range(0,number):
				switch_list.append(self.addSwitch(prefix + str(i), cls=OVSKernelSwitch))
		
		else:
			return

	def connect_network(self):
		#core-agg
		print("CORE AGG")
		end = int(self.pod/2)
		for x in range(0, int(self.agg_switches), end):
			for i in range(0, end):
				for j in range(0, end):
					print("Connecting core ",(i*end+j)," to agg", (x+i))
					self.addLink(
						self.core_list[i*end+j],
						self.agg_list[x+i],
						bw=15,
						delay='5ms'
						)   # use_htb=False

		# Agg to Edge
		for x in range(0, int(self.agg_switches),end):
			for i in range(0, end):
				for j in range(0, end):
					self.addLink(
						self.agg_list[x+i], self.edge_list[x+j], bw=15, delay='5ms')   

		# Edge to Host
		for x in range(0, int(self.edge_switches)):
			for i in range(0, int(self.host_pod)):
				self.addLink(
					self.edge_list[x],
					self.server_list[int(self.host_pod) * x + i],
					bw=15,
					delay='5ms')  


	def is_core(self, dpid):
		if dpid in self.core_list:
			return True
		else:
			return False

	def is_pod(self, dpid):

		if dpid in self.agg_list:
			return True
		elif dpid in self.edge_list:
			return True
		else:
			return False

def make_mininet_instance(graph_topo):

	net_topo = FattreeNet(graph_topo)
	net_topo.create_switches()
	net_topo.create_servers()
	net_topo.connect_network()
	print(net_topo.is_pod("34"))
	net = Mininet(topo=net_topo, controller=None, autoSetMacs=True)
	
	net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6653)
	return net

def run(graph_topo):
	
	# Run the Mininet CLI with a given topology
	lg.setLogLevel('info')
	mininet.clean.cleanup()
	net = make_mininet_instance(graph_topo)

	info('*** Starting network ***\n')
	net.start()
	info('*** Running CLI ***\n')
	CLI(net)
	info('*** Stopping network ***\n')
	net.stop()



#ft_topo = topo.Fattree(4)
run(4)