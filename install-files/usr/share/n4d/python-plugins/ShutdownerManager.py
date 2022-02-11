#!/usr/bin/python3
import sys
import os
import copy
import time
import n4d.server.core as n4dcore
import n4d.responses

class ShutdownerManager:
	

	def __init__(self):
		
		self.core=n4dcore.Core.get_core()
		self.cron_file="/etc/cron.d/lliurex-shutdowner"
		self.thinclient_cron_file="/etc/cron.d/lliurex-shutdowner-thinclients"
		self.server_cron_file="/etc/cron.d/lliurex-shutdowner-server"
		
		
	#def init

	
	def startup(self,options):
		
		#Old n4d:self.internal_variable=copy.deepcopy(objects["VariablesManager"].get_variable("SHUTDOWNER"))
		check_client=self.core.get_variable("REMOTE_VARIABLES_SERVER").get('return',None)

		if check_client!=None:
			try:
				ret=self.core.delete_variable("SHUTDOWNER")
			except:
				pass
		else:
			self.internal_variable=self.core.get_variable("SHUTDOWNER").get('return',None)
		
			if self.internal_variable==None:
				try:

					self.initialize_variable()
					#Old n4d: objects["VariablesManager"].add_variable("SHUTDOWNER",copy.deepcopy(self.internal_variable),"","Shutdowner internal variable","lliurex-shutdowner")
					self.core.set_variable("SHUTDOWNER",self.internal_variable)
						
				except Exception as e:
					print(str(e))
		
			self.check_server_shutodown()

	#def startup

	
	def initialize_variable(self):
		
		self.internal_variable={}
		self.internal_variable["cron_enabled"]=False
		self.internal_variable["cron_content"]=""
		self.internal_variable["shutdown_signal"]=0.0
		self.internal_variable["cron_values"]={}
		self.internal_variable["cron_values"]["hour"]=0
		self.internal_variable["cron_values"]["minute"]=0
		self.internal_variable["cron_values"]["weekdays"]=[True,True,True,True,True]
		self.internal_variable["cron_values"]["server_shutdown"]=False
		self.internal_variable["server_cron"]={}
		self.internal_variable["server_cron"]["custom_shutdown"]=False
		self.internal_variable["server_cron"]["cron_server_content"]=""
		self.internal_variable["server_cron"]["cron_server_values"]={}
		self.internal_variable["server_cron"]["cron_server_values"]["hour"]=0
		self.internal_variable["server_cron"]["cron_server_values"]["minute"]=0
		self.internal_variable["server_cron"]["cron_server_values"]["weekdays"]=[True,True,True,True,True]

		
	#def initialize_variable


	def check_variable(self,variable):

		try:
			if not type(variable)==dict:
				return False
			if not type(variable["cron_enabled"])==bool:
				return False
			if not type(variable["cron_content"])==str:
				return False
			if not type(variable["shutdown_signal"])==float:
				return False
			if not type(variable["cron_values"])==dict:
				return False
			if not type(variable["cron_values"]["hour"])==int:
				return False
			if not type(variable["cron_values"]["minute"])==int:
				return False
			if not type(variable["cron_values"]["server_shutdown"])==bool:
				return False
			if not type(variable["cron_values"]["weekdays"])==list:
				if len(variable["cron_values"]["weekdays"])!=5:
					return False
			if not type(variable["server_cron"])==dict:
				return False
			if not type(variable["server_cron"]["custom_shutdown"])==bool:
				return False
			if not type(variable["server_cron"]["cron_server_content"])==str:
				return False
			if not type(variable["server_cron"]["cron_server_values"])==dict:
				return False
			if not type(variable["server_cron"]["cron_server_values"]["hour"])==int:
				return False
			if not type(variable["server_cron"]["cron_server_values"]["minute"])==int:
				return False
			if not type(variable["server_cron"]["cron_server_values"]["weekdays"])==list:
				if len(variable["server_cron"]["cron_server_values"]["weekdays"])!=5:
					return False	

		except:
			return False

		return True

	#def check_variable

	
	def manual_client_list_check(self):
		'''
		objects["VariablesManager"].manual_client_list_check()
		return True
		'''
		self.core.check_clients()
		return n4d.responses.build_successful_call_response()
		
	#def manual_client_list_check

	
	def is_cron_enabled(self):
		
		ret={}
		ret["status"]=self.internal_variable["cron_enabled"]
		ret["msg"]=self.internal_variable["cron_content"]
		
		if ret["status"]:
			ret["cli_support"]="enabled"
		else:
			ret["cli_support"]="disabled"
		
		#Old n4d: return ret
		return n4d.responses.build_successful_call_response(ret)
		
		
	#def is_cron_enabled
	
	
	def is_server_shutdown_enabled(self):

				
		ret={}
		ret["status"]=self.internal_variable["cron_values"]["server_shutdown"]
		ret["msg"]=self.internal_variable["server_cron"]["cron_server_content"]
		if ret["status"]:
			ret["cli_support"]="enabled"
		else:
			ret["cli_support"]="disabled"
		
		ret["custom_shutdown"]=self.internal_variable["server_cron"]["custom_shutdown"]	
		#Old n4d: return ret
		return n4d.responses.build_successful_call_response(ret)
		
		
	#def is_server_shutdown_enabled
	

	def update_shutdown_signal(self):
		
		self.internal_variable["shutdown_signal"]=time.time()
		return self.save_variable()
		
	#def update_shutdown_signal

	
	def save_variable(self,variable=None):

		if variable==None:
			variable=copy.deepcopy(self.internal_variable)
		else:
			if not self.check_variable(variable):
				#Old n4d: return {"status":False,"msg":"Variable does not have the expected structure"}
				return n4d.responses.build_failed_call_response('',"Variable does not have the expected structure")
				
			self.internal_variable=copy.deepcopy(variable)
		
		#Old n4d: objects["VariablesManager"].set_variable("SHUTDOWNER",variable)
		
		
		self.check_server_shutodown()
		self.core.set_variable("SHUTDOWNER",variable)
	
		#Old n4: return {"status":True,"msg":""}
		return n4d.responses.build_successful_call_response()
		
		
	#def save_variable

	
	def check_server_shutodown(self):
			
		if self.internal_variable["cron_enabled"] and self.internal_variable["cron_values"]["server_shutdown"]:
			if not self.internal_variable["server_cron"]["custom_shutdown"]:
				f=open(self.cron_file,"w")
				f.write(self.internal_variable["cron_content"])
				f.close()
				if os.path.exists(self.server_cron_file):
					os.remove(self.server_cron_file)	
			else:
				shutdown_cmd="/usr/sbin/shutdown-server-lliurex"
				cron_content="%s %s * * %s root %s >> /var/log/syslog\n"
				minute=self.internal_variable["server_cron"]["cron_server_values"]["minute"]
				hour=self.internal_variable["server_cron"]["cron_server_values"]["hour"]
				days=""
				count=1

				for day in self.internal_variable["server_cron"]["cron_server_values"]["weekdays"]:
					if day:
						days+="%s,"%count
					count+=1
				days=days.rstrip(",")

				server_cron=cron_content%(minute,hour,days,shutdown_cmd)

				f=open(self.server_cron_file,"w")
				f.write(server_cron)
				f.close()
				if os.path.exists(self.cron_file):
					os.remove(self.cron_file)
		else:
			if os.path.exists(self.cron_file):
				os.remove(self.cron_file)
			if os.path.exists(self.server_cron_file):
				os.remove(self.server_cron_file)	
			
		self.build_thinclient_cron()
		
		return True
		
	#def check_server_shutdown
	
	
	def build_thinclient_cron(self):
		
		if self.internal_variable["cron_enabled"] and self.internal_variable["cron_values"]["server_shutdown"]:
			if not self.internal_variable["server_cron"]["custom_shutdown"]:
			# server will handle dialog calls its shutdown
				if os.path.exists(self.thinclient_cron_file):
					os.remove(self.thinclient_cron_file)
				return True
	
		
		if self.internal_variable["cron_enabled"]:
			
			# server will only handle thin clients dialogs
			shutdown_cmd="/usr/sbin/shutdown-lliurex"
			cron_content="%s %s * * %s root %s >> /var/log/syslog\n"
			minute=self.internal_variable["cron_values"]["minute"]
			hour=self.internal_variable["cron_values"]["hour"]
			days=""
			count=1
			
			for day in self.internal_variable["cron_values"]["weekdays"]:
				if day:
					days+="%s,"%count
				count+=1
			days=days.rstrip(",")
			
			thinclient_cron=cron_content%(minute,hour,days,shutdown_cmd)
			
			f=open(self.thinclient_cron_file,"w")
			f.write(thinclient_cron)
			f.close()
			
			return True
			
		else:
			# nothing to do
			if os.path.exists(self.thinclient_cron_file):
				os.remove(self.thinclient_cron_file)
				
			return True
		
		
	#def build_thinclient_cron
