# COEN498 PP: Cloud Computing
# Javier E. Fajardo - 26487602

# common.py: some data and definitions necessary for both client and server
import animal_pb2
import q_and_a_pb2
import json

from binascii import hexlify, unhexlify
from hashlib import md5


# common port to use
PORT = 4981

CLIENT_ID = "COEN498PP-CLIENT1"
SERVER_ID = "COEN498PP-SERVER1"
# hex string used for challenge. We don't want to get hung up in other connections that aren't approved
CHALLENGE = hexlify(md5('h'.encode()).digest()).decode()

class serializable():
	"""
	Interface/Abstract class for serialization in this assignment.
	Not common in Python, but makes sure that we have both the protobuf and the json
	"""
	def serialize(self,mode=None):
		if mode == 'json':
			return self.serializeJSON().encode()
		elif 'protobuf' in mode:
			return self.serializeProto()
		else:
			raise ValueError
	#end
	
	def deserialize(self,mode=None,raw_data=None):
		# check the data.
		assert(raw_data is not None and len(raw_data)>1)
	
		if mode == 'json':
			self.deserializeJSON(raw_data.decode())  # JSON data is a string
		elif 'protobuf' in mode:
			return self.deserializeProto(raw_data)
		else:
			raise ValueError
	#end 
	
	def serializeJSON(self):
		"""Makes a valid json string of 'most' objects. Subclasses may not be easily transformed into dicts"""
		return json.dumps(self.__dict__)
	
	def serializeProto(self):
		raise NotImplementedError
		
	def deserializeJSON(self, json_data):
		raise NotImplementedError
	
	def deserializeProto(self, proto_data):
		raise NotImplementedError
#end class serializable

class Animal(serializable):
	"""Common animal class"""
	
	# These sets are general items animals can have and this is shared among all animal classes
	# This is just to keep track of which features can be asked and are valid
	_qualities = set(['carnivore', 'herbivore', 'omnivore', 'predator', 'prey', 'mammal', 'reptile', 'large', 'small', 'aquatic', 'domesticated'])  # e.g 'is it large?', 'is it herbivore?'
	_abilities = set(['run','walk','fly','swim','lay eggs','mate'])  # 'can it walk?', 'can it lay egss?'
	_features = set(['fur','tail', 'teeth', 'paws', 'bones','scales'])  # 'does it have fur/tail/teeth?'
	_colors =  set(['beige', 'black', 'blue', 'brown', 'gold', 'gray', 'green', 'magenta', 'maroon', 'navy', 'orange', 'pink', 'purple', 'red', 'silver', 'tan', 'violet', 'white', 'yellow'])

	def __init__(self):
		"""Constructor"""
		self.name = type(self).__name__
		self.qualities = []
		self.abilities = []
		self.features = []
		self.colors = []
	#end 
	
	def __str__(self):
		ch = ", "
		return "{}\n   -Abilities: {}\n   -Qualities: {}\n   -Features: {}\n   -Known colors: {}\n".format(self.name,ch.join(self.abilities),ch.join(self.qualities),ch.join(self.features),ch.join(self.colors))

	def serializeProto(self):
		proto_data = animal_pb2.Animal()
		proto_data.name = self.name
		proto_data.qualities.extend(self.qualities)
		proto_data.abilities.extend(self.abilities)
		proto_data.features.extend(self.features)
		proto_data.colors.extend(self.colors)
		return proto_data.SerializeToString()
	#end 
		
	def deserializeJSON(self, json_data):
		self_obj = json.loads(json_data)
		self.name = self_obj['name']
		self.abilities = self_obj['abilities']
		self.qualities = self_obj['qualities']
		self.features = self_obj['features']
		self.colors = self_obj['colors']
	
	def deserializeProto(self, proto_data):
		self_obj = animal_pb2.Animal()
		self_obj.ParseFromString(proto_data)
		self.name = self_obj.name
		self.abilities = self_obj.abilities
		self.qualities = self_obj.qualities
		self.features = self_obj.features
		self.colors = self_obj.colors
	
#end class animal

class Question(serializable):
	"""Class for wrapping the question being sent between client and server"""
	
	readableString = {'qualities':'is it {}?','abilities':'can it {}?','features':'does it have {}?','colors':'is it {} in color?', 'name': 'is it a {}?'}
	
	def __init__(self, q_type=None, q_guess=None):
		self.inquiry = q_type
		self.guess = q_guess
	#end 
	
	def __str__(self):
		"""Make this question human readable"""
		return Question.readableString[self.inquiry].format(self.guess)
		
	def __repr__(self):
		return self.__str__()
	
	def serializeProto(self):
		proto_data = q_and_a_pb2.Question()
		proto_data.inquiry = self.inquiry
		proto_data.guess = self.guess
		return proto_data.SerializeToString()
		
	def deserializeJSON(self, json_data):
		self_obj = json.loads(json_data)
		self.inquiry = self_obj['inquiry']
		self.guess = self_obj['guess']
	
	def deserializeProto(self, proto_data):
		self_obj = q_and_a_pb2.Question()
		self_obj.ParseFromString(proto_data)
		self.inquiry = self_obj.inquiry
		self.guess = self_obj.guess
#end class

class Answer(serializable):
	"""Class for wrapping the answer being sent between client and server"""
	def __init__(self, question=None, value=None):
		self.question = question
		self.response = value
		self.game_over = False
	#end
	
	def readable(self):
		"""Make this Answer readable instead of just true and false"""
		if self.response:
			return "Yes"
		else:
			return "No"
	#end
	
	def serializeJSON(self):
		"""Makes a valid json string of this object"""
		question_dict = self.question.__dict__
		this_dict = self.__dict__
		this_dict['question'] = question_dict
		return json.dumps(this_dict)
	
	def serializeProto(self):
		proto_data = q_and_a_pb2.Answer()
		proto_data.response = self.response
		proto_data.game_over = self.game_over
		
		proto_data.question.inquiry = self.question.inquiry
		proto_data.question.guess = self.question.guess
		return proto_data.SerializeToString()
		
	def deserializeJSON(self, json_data):
		self_obj = json.loads(json_data)		
		self.response = self_obj['response']
		self.game_over = self_obj['game_over']
		self.question = Question()  # need to make a new object here
		self.question.__dict__.update(self_obj['question'])
	
	def deserializeProto(self, proto_data):
		self_obj = q_and_a_pb2.Answer()
		self_obj.ParseFromString(proto_data)
		self.response = self_obj.response
		self.game_over = self_obj.game_over
		
		self.question = Question()  # need to make a new object here
		self.question.inquiry = self_obj.question.inquiry
		self.question.guess = self_obj.question.guess
#end class