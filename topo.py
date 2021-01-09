# Copyright 2020 Lin Wang

# This code is part of the Advanced Computer Networks (2020) course at Vrije 
# Universiteit Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import random
import queue
import math

# Class for an edge in the graph
class Edge:
	def __init__(self):
		self.lnode = None
		self.rnode = None
	
	def remove(self):
		self.lnode.edges.remove(self)
		self.rnode.edges.remove(self)
		self.lnode = None
		self.rnode = None

# Class for a node in the graph
class Node:
	def __init__(self, id, type):
		self.edges = []
		self.id = id
		self.type = type

	# Add an edge connected to another node
	def add_edge(self, node):
		edge = Edge()
		edge.lnode = self
		edge.rnode = node
		self.edges.append(edge)
		node.edges.append(edge)
		return edge

	# Remove an edge from the node
	def remove_edge(self, edge):
		self.edges.remove(edge)

	# Decide if another node is a neighbor
	def is_neighbor(self, node):
		for edge in self.edges:
			if edge.lnode == node or edge.rnode == node:
				return True
		return False

class Jellyfish:

	def __init__(self, num_servers, num_switches, num_ports):
		self.servers = []
		self.switches = []
		self.num_servers=num_servers
		self.num_switches=num_switches
		self.num_ports=num_ports
		self.generate()

	#method to generate servers
	def generateServers(self):
		serv_to_conn=[]
		for i in range(0, self.num_servers):
			server = Node(str(i), "server")
			self.servers.append(server)
			serv_to_conn.append(server)
		return serv_to_conn

	#method to generate switches
	def generateSwitches(self,s):
		sw_to_conn=[]
		free_p=[]
		for i in range(0, self.num_switches):
			switch = Node(str(i), "switch")
			self.switches.append(switch)
			sw_to_conn.append(switch)
			free_p.append(s)

		return sw_to_conn,free_p

	#method for incorporate a link
	def remover(self,r,free_p, ind_A,sw_A):
		ind_C = random.randint(0, self.num_switches - 1)
		sw_C = self.switches[ind_C]
		rand_conn = random.randint(0, r - 1)
		edge_to_remove = sw_C.edges[rand_conn]
		sw_A.add_edge(edge_to_remove.lnode)
		sw_A.add_edge(edge_to_remove.rnode)
		free_p[ind_A] = free_p[ind_A] - 2
		sw_C.remove_edge(edge_to_remove)
		return free_p

	#method to connect servers to switches
	def connectServer(self,remaining_servers,r,servers_to_conn):
		for i in range(0, self.num_switches):
			for n in range(0, r):
				if(remaining_servers == 0):
					ind_A = random.randint(0, self.num_servers - 1)
					to_conn = self.servers[ind_A]
				elif(remaining_servers > 0):
					ind_A = random.randint(0, remaining_servers - 1)
					remaining_servers = remaining_servers - 1
					to_conn = servers_to_conn[ind_A]
					servers_to_conn.pop(ind_A)
				if(not self.switches[i].is_neighbor(to_conn)):
					self.switches[i].add_edge(to_conn)

	#generation of the topology
	def generate(self):
		# TODO: code for generating the jellyfish topology

		#Calculate number of ports used to connect servers
		r = math.ceil(self.num_servers / self.num_switches)

		#calculate number of ports for switches
		s = self.num_ports - r

		remaining = self.num_switches
		remaining_servers = self.num_servers

		serv_to_conn=[]
		switches_to_conn=[]
		free_p=[]

		serv_to_conn=self.generateServers()
		sw_to_conn,free_p = self.generateSwitches(s)

	
		while sw_to_conn:
			
			ind_A = random.randint(0, remaining - 1)

			if ((remaining == 1) and (free_p[ind_A] == 1)):
				break
			
			if ((remaining == 1) and (free_p[ind_A] >= 2)):

				free_p=self.remover(r,free_p, ind_A,sw_A)
				break

			if(free_p[ind_A] == 0):
				free_p.pop(ind_A)
				sw_to_conn.pop(ind_A)
				remaining = remaining - 1
				continue

			ind_B = random.randint(0, remaining - 1)
			if ind_A == ind_B:
				continue

			if(free_p[ind_B] == 0):
				free_p.pop(ind_B)
				sw_to_conn.pop(ind_B)
				remaining = remaining - 1
				continue
			
			sw_A = sw_to_conn[ind_A]
			sw_B = sw_to_conn[ind_B]

			if(not sw_A.is_neighbor(sw_B)):
				sw_A.add_edge(sw_B)
				free_p[ind_A] = free_p[ind_A] - 1
				free_p[ind_B] = free_p[ind_B] - 1
			elif sw_A.is_neighbor(sw_B) and remaining == 2:
				break


		self.connectServer(remaining_servers,r,serv_to_conn)

		return

	#method to calculare the path length between server pairs
	def get_server_pairs(self):
		
		count=[0]*5
		for i in range(0,len(self.servers)):
			
			sw_i=self.server_switch(self.servers[i])
			dst_arr=self.shortest_path(sw_i)
			for k in range(i+1,len(self.servers)):

				sw_k=self.server_switch(self.servers[k])
				hop=dst_arr[int(sw_k.id)]+2
				if hop==6:
					count[4]+=1
				elif hop==5:
					count[3]+=1
				elif hop==4:
					count[2]+=1
				elif hop==3:
					count[1]+=1
				elif hop==2:
					count[0]+=1

		return count
	
	#method to get the switch which a server is connected to
	def server_switch(self,server):
		if server.edges[0].lnode==server:
			return server.edges[0].rnode
		else:
			return server.edges[0].lnode
	
	def shortest_path(self,src):
		dst=[-1]*len(self.switches)
		explored=[]
		queue=[]
		dst[int(src.id)]=0
		queue.append(src)
		queue.append(0)
		while queue:
			node=queue.pop(0)
			dist=queue.pop(0)

			if node not in explored:
				for edge in node.edges:

					if edge.lnode==node:
						to_node=edge.rnode
					else:
						to_node=edge.lnode
					
					if to_node.type=="switch":
						if to_node not in explored and dst[int(to_node.id)]==-1:
							dst[int(to_node.id)]=dist+1				
							queue.append(to_node)
							queue.append(dist+1)
					
				explored.append(node)
			
		return dst	

	#returns also the path
	def shortest_path2(self,src):
		dst=[-1]*len(self.switches)
		prec=[None]*len(self.switches)
		explored=[]
		queue=[]
		dst[int(src.id)]=0
		queue.append(src)
		queue.append(0)
		while queue :
			node=queue.pop(0)
			dist=queue.pop(0)

			if node not in explored:
				for edge in node.edges:

					if edge.lnode==node:
						to_node=edge.rnode
					else:
						to_node=edge.lnode
					
					if to_node.type=="switch":
						if dst[int(to_node.id)]==-1:
							dst[int(to_node.id)]=dist+1
							prec[int(to_node.id)]=node.id				
							queue.append(to_node)
							queue.append(dist+1)
					
				explored.append(node)

		return dst,prec	
	

class Fattree:

	def __init__(self, num_ports):
		self.servers = []
		self.switches = []
		self.core_switches=0
		self.num_switches=0
		self.num_servers=0
		self.server_pod=0
		self.num_pod=num_ports
		self.switches_pod=0
		self.generate(num_ports)

	def to_node(self,sw, edge):

		if edge.rnode==sw:
			return edge.lnode
		else:
			return edge.rnode


	def generateSwitches(self):

		#Core switches
		for i in range(0,int(self.core_switches)):
			id="10.1."+str(self.num_pod)+"."+str(i)
			node=Node(id,type="core_switch")
			self.switches.append(node)

		#aggregation and edge switches for pod
		for p in range(0,int(self.num_pod)):					#pod
			base_id="10."+str(p)+"."			
			for s in range(0,int(self.num_pod)):				#switch
				id=base_id+str(s)+".1"
				node=Node(id,type="switch")
				self.switches.append(node)

	def generateServers(self):
		
		for p in range(0,self.num_pod):					#pod
			base_id="10."+str(p)+"."
			for s in range(0,int(self.num_pod/2)):				#switch
				base_id_=base_id+str(s)+"."
				for i in range(2,2+int(self.num_pod/2)):
					id=base_id_+str(i)
					#print(id)
					node=Node(id,type="server")
					self.servers.append(node)

	def connect_network(self):
		#connect edge switches to servers
		for p in range(0,self.num_pod):
			
			for s in range(0,int(self.switches_pod/2)):
				offset=self.core_switches+(self.num_pod*p)+s #offset to find switch         
				
				for i in range(0,int(self.switches_pod/2)):
					os=p*self.core_switches+s*int(self.switches_pod/2)+i		#offset to find server
					switch=self.switches[int(offset)]
					self.servers[int(os)].add_edge(switch)

		#connect edge switches to aggregation switches
		for p in range(0,self.num_pod):

			for s in range(0,int(self.switches_pod/2)):
				offset=self.core_switches+(self.num_pod*p)+s #offset to find switch
				switch=self.switches[int(offset)]

				for i in range(int(self.switches_pod/2),int(self.switches_pod)):
					os=self.core_switches+(self.num_pod*p)+i
					ag_switch=self.switches[int(os)]
					switch.add_edge(ag_switch)

		#connect aggregation to core
		for p in range(0,self.num_pod):
			core=0
			for s in range(int(self.num_pod/2),int(self.num_pod)):
				offset=self.core_switches+(self.num_pod*p)+s #offset to find switch
				switch=self.switches[int(offset)]
				for i in range(core,core+int(self.num_pod/2)):
					switch.add_edge(self.switches[i])
				
				core=core+int(self.num_pod/2)
					
	def generate(self, num_ports):
				
		# TODO: code for generating the fat-tree topology
		# switches
		k2=math.pow(num_ports,2)
		self.num_switches=int(5*k2/4)
		self.core_switches=math.pow(num_ports/2,2)

		#servers
		k3=math.pow(num_ports,3)
		self.num_servers=int(k3/4)
		self.server_pod=math.pow(num_ports/2,2)

		
		self.switches_pod=(self.num_switches-self.core_switches)/self.num_pod

		self.generateSwitches()
		self.generateServers()
		self.connect_network()

	#method which return the path length between all possible server pairs
	def get_server_pairs(self):

		count=[0]*3
		for i in range(0,len(self.servers)):
			
			s=self.servers[i]
			#recover pod
			id=s.id
			splitted=id.split(".")
			pod_n_s=splitted[1]
			switch_n_s=splitted[2]

			for j in range(i+1,len(self.servers)):
				s2=self.servers[j]
				id=s2.id
				splitted=id.split(".")
				pod_n_s2=splitted[1]
				switch_n_s2=splitted[2]
				if (switch_n_s==switch_n_s2) and (pod_n_s==pod_n_s2):
					count[0]+=1
				elif (pod_n_s==pod_n_s2):
					count[1]+=1
				else:
					count[2]+=1
		return count
