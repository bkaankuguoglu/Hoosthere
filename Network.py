import requests

class Network:
	def __init__(self, endpoint = 'http://hoo-dev.eu-central-1.elasticbeanstalk.com/hoo/'):
		self.endpoint = endpoint

	def create_visit(self, username, video_id, status=0):
		req = requests.post(self.endpoint + 'create_visit/', json={'username': username, 'video_id': video_id, 'status': status})
		if req.status_code == 200:
			json = req.json()

			if 'result' in json:
				return None
			else:
				return json['id']
		else:
			return None

	def update_visit(self, visit_id, status=0):
		req = requests.post(self.endpoint + 'update_visit/', json={'id': visit_id, 'status': status})
		if req.status_code == 200:
			json = req.json()

			if 'result' in json:
				return True
			else:
				return False
		else:
			return False

	def visit_status(self, visit_id):
		req = requests.get(self.endpoint + 'visit_by_id/', params={'id': visit_id})
		if req.status_code == 200:
			json = req.json()

			if not 'status' in json:
				return None
			else:
				return json['status']
		else:
			return None

	def get_message(self, username):
		req = requests.get(self.endpoint + 'create_message/', params={'username': username})
		if req.status_code == 200:
			json = req.json()

			if 'result' in json:
				return None, None
			else:
				return json['id'], json['message']
		else:
			return None, None
	
	def update_message(self, message_id, status=1):
		req = requests.post(self.endpoint + 'update_message/', json={'id': message_id, 'status': status})

	def get_resident_name(self, username):
		req = requests.get(self.endpoint + 'register_resident/', params={'username': username})
		if req.status_code == 200:
			json = req.json()

			if not 'name' in json:
				return None
			else:
				return json['name']
		else:
			return None

	def get_resident_msID(self, username):
		req = requests.get(self.endpoint + 'register_resident/', params={'username': username})
		if req.status_code == 200:
			json = req.json()

			if not 'microsoft_id' in json:
				return ''
			else:
				return json['microsoft_id']
		else:
			return None

	def microsoft_list(self):
		req = requests.get(self.endpoint + 'microsoft_list/')
		l = ''
		if req.status_code == 200:
			json = req.json()
			for j in json:
				l = l + ',' + (j['microsoft_id'])
		l = l[1:]
		#print(l)
		return l
