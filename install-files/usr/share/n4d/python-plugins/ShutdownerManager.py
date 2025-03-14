#!/usr/bin/python3
import sys
import os
import subprocess
import copy
import time
import n4d.server.core as n4dcore
import n4d.responses
import xmlrpc.client as n4dclient
import ssl

class ShutdownerManager:
	
	def __init__(self):
		
		self.core=n4dcore.Core.get_core()
		self.cron_file="/etc/cron.d/lliurex-shutdowner"
		self.desktop_cron_file="/etc/cron.d/lliurex-shutdowner-desktop"
		self.adi_cron_file="/etc/cron.d/lliurex-shutdowner-adi"
		self.adi_client="/usr/bin/natfree-client"
		self.is_clientized_desktop=False
		self.keep_cron_file=False
		self.is_adi=False
		self.version_reference=["adi","desktop"]
		
	#def init

	def startup(self,options):
		
		set_internal_variable=False
		is_client=self._is_client_mode()
		
		
		if is_client:
			try:
				ret=self.core.delete_variable("SHUTDOWNER")
			except:
				pass
		else:
			if self.is_adi:
				if os.path.exists(self.desktop_cron_file):
					os.remove(self.desktop_cron_file)
			else:
				if os.path.exists(self.adi_cron_file):
					os.remove(self.adi_cron_file)
							
			self.internal_variable=self.core.get_variable("SHUTDOWNER").get('return',None)
		
			if self.internal_variable==None:
				try:

					self.initialize_variable()
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
		try:
			ret["status"]=self.internal_variable["cron_enabled"]
			ret["msg"]=self.internal_variable["cron_content"]
			
			if ret["status"]:
				ret["cli_support"]="enabled"
			else:
				ret["cli_support"]="disabled"
		except:
			pass
		
		return n4d.responses.build_successful_call_response(ret)
		
	#def is_cron_enabled
	
	def is_server_shutdown_enabled(self):

		ret={}
		try:
			ret["status"]=self.internal_variable["cron_values"]["server_shutdown"]
			ret["msg"]=self.internal_variable["server_cron"]["cron_server_content"]
			if ret["status"]:
				ret["cli_support"]="enabled"
			else:
				ret["cli_support"]="disabled"
			
			ret["custom_shutdown"]=self.internal_variable["server_cron"]["custom_shutdown"]	
		except:
			pass
		
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
				return n4d.responses.build_failed_call_response('',"Variable does not have the expected structure")
				
			variable["cron_content"]=variable["cron_content"].replace("&gt;&gt;",">>")
			variable["server_cron"]["cron_server_content"]=variable["server_cron"]["cron_server_content"].replace("&gt;&gt;",">>")
			self.internal_variable=copy.deepcopy(variable)
		
		self.keep_cron_file=False
		self.check_server_shutodown()
		self.core.set_variable("SHUTDOWNER",variable)
	
		return n4d.responses.build_successful_call_response()
		
	#def save_variable

	def check_server_shutodown(self):
			
		if self.internal_variable["cron_enabled"] and self.internal_variable["cron_values"]["server_shutdown"]:
			if not self.internal_variable["server_cron"]["custom_shutdown"]:
				tmp_cron_content=self.internal_variable["cron_content"].replace("&gt;&gt;",">>")
				f=open(self.cron_file,"w")
				f.write(tmp_cron_content)
				f.close()
				if os.path.exists(self.adi_cron_file):
					os.remove(self.adi_cron_file)	
			else:
				if self.is_adi:
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
					server_cron=server_cron.replace("&gt;&gt;",">>")

					f=open(self.adi_cron_file,"w")
					f.write(server_cron)
					f.close()
					if os.path.exists(self.cron_file):
						os.remove(self.cron_file)
		else:
			if os.path.exists(self.cron_file):
				if self.is_clientized_desktop:
					self.keep_cron_file=True
					os.rename(self.cron_file,self.desktop_cron_file)
					self._update_internal_variable()
				else:
					os.remove(self.cron_file)
			
			if os.path.exists(self.adi_cron_file):
				os.remove(self.adi_cron_file)	
			
		if not self.is_adi:
			self.build_thinclient_cron()

		return True
		
	#def check_server_shutdown
	
	def build_thinclient_cron(self):
		
		if self.internal_variable["cron_enabled"] and self.internal_variable["cron_values"]["server_shutdown"]:
			if not self.internal_variable["server_cron"]["custom_shutdown"]:
			# server will handle dialog calls its shutdown
				if os.path.exists(self.desktop_cron_file):
					os.remove(self.desktop_cron_file)
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
			thinclient_cron=thinclient_cron.replace("&gt;&gt;",">>")
			f=open(self.desktop_cron_file,"w")
			f.write(thinclient_cron)
			f.close()
			
			return True
			
		else:
			# nothing to do
			if os.path.exists(self.desktop_cron_file):
				if not self.keep_cron_file:
					os.remove(self.desktop_cron_file)

			return True
		
	def _is_client_mode(self):

		is_client=False
		self.is_desktop=True
		flavours=[]
	
		try:
			cmd='lliurex-version -v'
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
			result=p.communicate()[0]

			if type(result) is bytes:
				result=result.decode()

			for x in result.split(","):
				if x.strip() in self.version_reference:
					flavours.append(x.strip())

			for item in flavours:
				if 'adi' in item:
					self.is_desktop=False
					self.is_adi=True
				break
		
			if self.is_desktop:
				if os.path.exists(self.adi_client):
					if self._check_connection_with_adi():
						is_client=True
						self.is_clientized_desktop=False
					else:
						self.is_clientized_desktop=True
			
			return is_client
			
		except Exception as e:
			return False
	
	#def _is_client_mode

	def _check_connection_with_adi(self):

		try:
			context=ssl._create_unverified_context()
			client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
			test=client.is_cron_enabled('','ShutdownerManager')
			return True
		except Exception as e:
			return False

	#def _check_connection_with_server

	def _update_internal_variable(self):

		if os.path.exists(self.desktop_cron_file):
			with open(self.desktop_cron_file,'r') as fd:
				content=fd.readline()
		try:
			parse_content=content.split(" ")
			self.internal_variable["cron_enabled"]=True
			self.internal_variable["cron_content"]=content.replace("&gt;&gt;",">>")
			self.internal_variable["cron_values"]["hour"]=parse_content[1]
			self.internal_variable["cron_values"]["minute"]=parse_content[0]
			tmp_weekdays=[False,False,False,False,False]
			for item in parse_content[4].split(","):
				if item=="1":
					tmp_weekdays[0]=True
				elif item=="2":
					tmp_weekdays[1]=True
				elif item=="3":
					tmp_weekdays[2]=True
				elif item=="4":
					tmp_weekdays[3]=True
				elif item=="5":
					tmp_weekdays[4]=True
			self.internal_variable["cron_values"]["weekdays"]=tmp_weekdays
			self.core.set_variable("SHUTDOWNER",self.internal_variable)
		except:
			pass

	#def _update_internal_variable

	def cancel_shutdown(self):
		
		command="shutdown -c"
		os.system(command)
		
	#def cancel_shutdown
	
#class ShutdownerManager
