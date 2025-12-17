import os
import sys
import re
import netrc
import logging
import requests
import json
import pprint
import traceback
import urllib.parse
import hashlib
import datetime

#~ class NotFoundError(Exception):    
	#~ def __init__(self, message):
		#~ super().__init__(message)

#~ class InvalidArgumentError(Exception):    
	#~ def __init__(self, message):
		#~ super().__init__(message)
		
#~ class ArgumentNotFoundError(Exception):    
	#~ def __init__(self, message):
		#~ super().__init__(message)
	
#~ class InternalServerError(Exception):    
	#~ def __init__(self, message):
		#~ super().__init__(message)

#~ class PermissionDeniedError(Exception):    
	#~ def __init__(self, message):
		#~ super().__init__(message)

class Response:
				
	status_code = None
	text = None
	
	def __init__(self, status_code, text):
		self.status_code = status_code
		self.text = text
					
class API:
	
	' init logger '
	logger = logging.getLogger(__qualname__)	
	logger.propagate = False  
	if not logger.handlers:
		handler = logging.StreamHandler()
		formatter = logging.Formatter(
			"%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",datefmt='%Y-%m-%d %H:%M:%S',
		)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
				
	api_url = "https://edc.dgfi.tum.de/api/v3/"
	
	def __init__(self, **kwargs,):
		
		log_level = kwargs.get('log_level',logging.INFO)
		debug = kwargs.get('debug',0)	
		self.username = None
		self.api_key = kwargs.get('api_key',None)
		
		' set log level '
		self.logger.setLevel(log_level)
		
		if debug == 1:
			self.api_url = "https://edc.dgfi.tum.de:8001/api/v3/"
			self.logger.warning("Debug-API enabled ("+str(self.api_url)+")!")
				
		if self.api_key == None:
			' read credential from ~/.netrc '		
			n = netrc.netrc()
			credentials = n.authenticators('edc.dgfi.tum.de')
			if credentials == None:
				self.logger.error('No credentials found in ~/.netrc')
				sys.exit(0)
			
			self.username = credentials[0]
			self.api_key = credentials[2]
			
		self.logger.info('API-Key: '+str(self.api_key))

	def send_api_request(self, url, args):
		
		
		response = requests.post(url, json=args)							
		if response.status_code == 400:	
			json_response = json.loads(response.text)			
			self.logger.error('400 - OpenADB-API url not found!')
			raise ArgumentNotFoundError(json_response['message'])
		elif response.status_code == 403:	
			json_response = json.loads(response.text)
			self.logger.error('403 - Permission denied!')
			raise PermissionDeniedError(json_response['message'])
		elif response.status_code == 471:	
			json_response = json.loads(response.text)
			self.logger.error('471 - Invalid Argument')
			raise InvalidArgumentError(json_response['message'])
		elif response.status_code == 500:
			json_response = json.loads(response.text)
			self.logger.error('500 - Internal Server Error')			
			raise InternalServerError(json_response['message'])	
					
		return response
	
	def get_file_md5(self,path_file):
		
		md5_hash = hashlib.md5()

		with open(path_file, 'rb') as file:
			chunk_size = 8192
			while chunk := file.read(chunk_size):
				md5_hash.update(chunk)

		return md5_hash.hexdigest()

	def upload(self, file_path):
			
		if not os.path.isfile:
			print (file_path,'does not exist!')
			sys.exit(0)
		
		headers = {
			"Authorization": f"ApiKey {self.api_key}",			
		}

		files = {
		    "file": open(file_path, "rb"),
		}
		s = requests.Session()
		s.trust_env = False
		response = s.post(self.api_url+"upload/", headers=headers, files=files)
		if response.status_code != 200 and response.status_code != 201:
			self.logger.info('Uploading `'+file_path+'` ... FAILED!')
			self.logger.error("Status: "+str(response.status_code))
			self.logger.error("Response: "+str(response.text))
		else:
			self.logger.info('Uploading `'+file_path+'` ... OK')
			
		return response
	
	def download(self, path_url, **kwargs):
			
		headers = {
			"Authorization": f"ApiKey {self.api_key}",			
		}

		filename = os.path.basename(path_url)			
		
		args = {}
		args['path_url'] = path_url
		args['path_output'] = kwargs.get('output_path',"")
		args['overwrite'] = kwargs.get('overwrite',False)
		args['preserve_timestamp'] = kwargs.get('preserve_timestamp',False)
		args['update_only'] = kwargs.get('update_only',False)
		args['file_pattern'] = kwargs.get('file_pattern',None)
		args['log_path'] = kwargs.get('log_path',None)
		
				
		if args['log_path'] != None:
			output_log = open(args['log_path'],'w')
		
		summary = {}
		summary['num_uptodate'] = 0
		summary['num_downloaded'] = 0
		summary['num_failed'] = 0
		summary['files_failed'] = []
		summary['files_downloaded'] = []
		
		' get listing of files on server '
		s = requests.Session()
		s.trust_env = False
		response_listing = s.post(self.api_url+"listing/", headers=headers, data=args)					
		if response_listing.status_code == 200:
			file_listing = json.loads(response_listing.text)['listing']
			source = json.loads(response_listing.text)['source']
			self.logger.info('Found '+str(len(file_listing))+' files to download!')			
			for url_path, url_md5, url_timestamp in file_listing:
				
				' create local path '
				if source == "file":
					file_local = os.path.basename(url_path)
					path_local = os.path.abspath(args['path_output'])+'/'+file_local
					
				elif source == "directory":					
					file_local = os.path.basename(url_path)
					path_local = os.path.abspath(args['path_output'])+'/'+os.path.abspath(url_path).replace(path_url,'')
					
				' create local directory if not exist '
				if not os.path.isdir(os.path.dirname(path_local)):
					os.mkdir(os.path.dirname(path_local))
								
				do_download = 1
				if args['update_only'] == True and url_md5 != None and os.path.isfile(path_local):
					md5_local = self.get_file_md5(path_local)
					if url_md5 == md5_local:
						do_download = 0
						
				if do_download == 1:
					
					args_download = {}
					args_download['path_url'] = url_path
					
					response_download = s.post(self.api_url+"download/", headers=headers, data=args_download)	
					if response_listing.status_code == 200:

						' Download file '
						with open(path_local, 'wb') as f:
							for chunk in response_download.iter_content(chunk_size=1024): 
								if chunk:
									f.write(chunk)						
						
						' Update modification timestamp '						
						if args['preserve_timestamp'] == True and url_timestamp != None:								
							if url_timestamp != None:						
								os.utime(path_local, (int(float(url_timestamp)), int(float(url_timestamp))))
								
						' Check if download was successful '
						if os.path.isfile(path_local):
							self.logger.info(path_local+' -> Download successful!')
							if args['log_path'] != None:
								output_log.write(str(datetime.datetime.now())+' '+path_local+' NEW\n')
							summary['num_downloaded'] += 1
							summary['files_downloaded'].append(path_local)
						else:
							self.logger.info(path_local+' -> Download FAILED!')
							if args['log_path'] != None:
								output_log.write(str(datetime.datetime.now())+' '+path_local+' FAILED\n')
							summary['num_failed'] += 1
							summary['files_failed'].append(path_local)
						
					else:
						self.logger.info(path_local+' -> Download FAILED!')
						if args['log_path'] != None:
							output_log.write(str(datetime.datetime.now())+' '+path_local+' FAILED\n')
						summary['num_failed'] += 1		
				else:
					self.logger.info(path_local+' -> up-to-date!')
					summary['num_uptodate']+= 1 
			
			self.logger.info(str(summary['num_downloaded'])+' file(s) downloaded!')
			self.logger.info(str(summary['num_failed'])+' file(s) failed!')
			self.logger.info(str(summary['num_uptodate'])+' file(s) up-to-date!')
			if args['log_path'] != None:
				self.logger.info('Log-File: '+str(args['log_path']))
				output_log.close()
		else:
			self.logger.warning('File or directory `'+path_url+'` not found on server!')
			
		return summary
		
	def browse(self, dataset, query, format='json',path=None):
					
		headers = {
			"Authorization": f"ApiKey {self.api_key}",			
		}
		
		if format not in ['json','list','ascii']:
			self.logger.error('Invalid value for `format`! Allowed values: `json`,`list`,`ascii`')
			sys.exit(0)
		
		args = {}
		args['dataset'] = dataset
		args['query'] = urllib.parse.quote(json.dumps(query))
		
		s = requests.Session()
		s.trust_env = False
		response = s.post(self.api_url+"browse/", headers=headers, data=args)
		if response.status_code != 200 and response.status_code != 201:			
			self.logger.error("Status: "+str(response.status_code))
			self.logger.error("Response: "+str(response.text))
		else:			
			data = json.loads(response.text)						
			self.logger.info(str(len(data))+" entries found!")
			if format == "json":
				response_text = []
				for entry in data:
					if 'incoming_date' in entry and entry['incoming_date'] != None:
						entry['incoming_date'] = entry['incoming_date']+"Z"
					if 'start_data_date' in entry and entry['start_data_date'] != None:
						entry['start_data_date'] = entry['start_data_date']+"Z"
					if 'end_data_date' in entry and entry['end_data_date'] != None:
						entry['end_data_date'] = entry['end_data_date']+"Z"
					if 'creation_date' in entry and entry['creation_date'] != None:
						entry['creation_date'] = entry['creation_date']+"Z"
					response_text.append(entry)
			elif format == "list":
				response_text = []
				for entry in data:
					if dataset == 'CPF':
						response_text.append([entry['id'],entry['incoming_date']+"Z",entry['provider'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['eph_seq'],entry['status'],entry['errors']])						
					elif dataset == 'CPF_v2':
						response_text.append([entry['id'],entry['incoming_date']+"Z",entry['provider'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['eph_seq'],entry['eph_seq_daily'],entry['status'],entry['errors']])						
					else:
						response_text.append([entry['id'],entry['incoming_date']+"Z",entry['station'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['creation_date']+"Z",entry['observations'],entry['version'],entry['status'],entry['errors']])
			elif format == "ascii":
				response_text = ""
				for entry in data:
					if dataset == 'CPF':
						row = ("%d %s %s %s %s %s %s %s %s\n" % (entry['id'],entry['incoming_date']+"Z",entry['provider'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['eph_seq'],entry['status'],entry['errors']))					
					elif dataset == 'CPF_v2':
						row = ("%d %s %s %s %s %s %s %s %s %s\n" % (entry['id'],entry['incoming_date']+"Z",entry['provider'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['eph_seq'],entry['eph_seq_daily'],entry['status'],entry['errors']))					
					else:
						row = ("%d %s %s %s %s %s %s %s %s %s %s\n" % (entry['id'],entry['incoming_date']+"Z",entry['station'],entry['satellite'],entry['start_data_date']+"Z",entry['end_data_date']+"Z",entry['creation_date']+"Z",entry['observations'],entry['version'],entry['status'],entry['errors']))					
					response_text += row
			
			if path != None:
				self.logger.info("Writing "+str(path)+" ...")
				output = open(path,'w')
				output.write(str(response_text))
				output.close()
						
			response = Response(response.status_code,response_text)
			
		return response
		