# -*- coding: utf-8 -*-
from copy import deepcopy
import xy_re


class xy_list(object):
	"""
	그냥 한번 만들고 싶어서 만들어 보았다
	1부터 시작하고, 1~2처럼 사용이 가능한 리스트를 만들고 싶었다
	맨처음은 기존 리스트의 기능은 무시하고 그냥 만들어 보았는데,
	하다보니, 기존 리스트의 기능은 똑같아야 할것 같아서 변경 하였다
	그래서, 문자형태를 이용하여 사용하는 방법을 한다
	즉 abc라는 리스트가 있다면
	abc[0] = abc["1"] = abc["1~1"]



	새로운 리스트의 최종(?) 버전을 만들었다
	처음으로 만든것으로 아직 최종버전은이라고 할수는 없고, 점점 사용해 보면서 보완하기로 한다

	1. index로 하는 기능은 기존의 리스트와 동일하게 하였다 (다음에는 완전히 1로 시작하는 것을 만들어 보도록 하는데, 2차원 이상의 index에서 1로 시작하는 것을 만들지 못했다)
	2. 리스트에서 자주 사용하는 함수를 xy_list의 객체로 만들었다
	3. 맨 처음 이 클래스의 이름을 xy_list 로 만들었는데, 1차원 셀주소의 리스트 묶음으로 사용하고 있어서, 1로 시작하는 리스트 기능을 만들었기때문에, xy_list라고 만듦
	4. for문을 사용해서 나타나는 각 객체를 xy_list의 객체로 만듦
	5. i로 시작하는 것은 index의 의미로 기존의 리스트인 0부터 시작하는 의미
	6. pcell에서 리스트 값을 돌려주는 기본 객체를 xy_list로 적용
	7. to라는 단어로 시작되는 것은 기본 자료는 그대로 두고, 변경한 결과만 돌려주는 것이다
	8. change라는 단어가 된 것은 기본 자료 자체를 변경하는 것이다
	9. 이 모듈의 가장큰 장점은 추가적인 메소드를 만들어서 자주 사용하는 객체형을 바꿔서 사용이 가능하다는 것이다
	10. 물론 시간이 좀더 들어가겠지만, 더 효용성이 있어 보인다


	기존의 리스트에 추가적이 기능이 가능하도록 만들었다
	다음에는 아예 1로부터만 시작하는 것을 만들어 보도록 하겠다

	기본 기능에서 숫자는 기본 리스트의 기능
	문자일때는 1부터 시작하는 기능이며
	메소드를 실행하는 부분에서
	"""

	def __history(self):
		"""
		2025-03-30 : 전체적으로 이름을 변경
		"""
		pass

	def __add__(self, other):
		"""
		+ 기 뒷부분이 오면 실행 되는 것
		"""
		other = self.to_general_list(other)
		self.main_list = self.main_list + other
		return xy_list(self.main_list)

	def __call__(self, input_data):
		"""
		이 객체가 불릴때 실행되는 것

		:param input_data:
		:return:
		"""
		xy_list(input_data)

	def __check_all_tuple_n_set_to_list(self, input_any_data):
		"""
		입력으로 들어오는 자료중에서 안의 모든 자료를 list로 변경

		return을 사용해서 재귀함수를 사용하기때문에, 별도로 불러오는 함수를 사용해서, 결과를 돌려주는 형태로 나눈 것이다
		:param input_any_data:
		:return:
		"""
		if isinstance(input_any_data, (list, tuple)):
			return [self.change_all_tuple_n_set_to_list(x) for x in input_any_data]
		elif isinstance(input_any_data, set):
			return set(self.change_all_tuple_n_set_to_list(x) for x in input_any_data)
		else:
			return input_any_data

	def __delitem__(self, key=""):
		"""
		del(x)를 하면 실행되는 코드
		getitem과 다르게 2차원인경우는 2차원자료를 먼저 삭제하고 1차원자료를 삭제한다
		"""
		if isinstance(key, slice):
			# :가 있는 형태가 들어갈때 slice 함수로 바뀌면서 이루어 지는 것이다
			del self.main_list[key.start:key.stop:key.step]

		elif type(key) == type(123):
			# 숫자가 들어올때 실행 되는 것
			del self.main_list[key]

		elif key == None:
			pass
		elif type(key) == type("abc"):
			if "~" in key:
				if ":" in key:
					# 2 차원의 자료 요청건 ["2~3:4~5"]
					value1, value2 = key.split(":")

					if "~" in value2:
						start, end = value2.split("~")
						if start == "" and end == "": #["2~3:~"]
							pass
						elif start == "" and end:#["2~3:~5"]
							for index in range(len(self.main_list)):
								del self.main_list[index][:int(end)]
						elif start and end == "": #["2~3:4~"]
							for index in range(len(self.main_list)):
								del self.main_list[index][int(start) - 1:]
						elif start and end: #["2~3:4~5"]
							for index in range(len(self.main_list)):
								del self.main_list[index][int(start) - 1:int(end)]
						elif value2 == "":  # ["2~3:"]
							pass
						else:
							pass

					if "~" in value1:
						start, end = value1.split("~")
						if start == "" and end == "": #["~:4~5"]
							pass
						elif start and end == "": #["2~:4~5"]
							del self.main_list[int(start) - 1:]
						elif start == "" and end: #["~3:4~5"]
							del self.main_list[:int(end)]
						elif start and end: #["2~3:4~5"]
							del self.main_list[int(start) - 1:int(end)]
					else:
						pass

				else: #["1~2"], ~은 있으나 :이 없을때
					no1, no2 = key.split("~")
					if no1 and no2:
						if no1 == no2: #["1~1"]
							del self.main_list[int(no1) - 1]
						else :  # ["1~2"]
							del self.main_list[int(no1) - 1:int(no2)]
					elif no1 == "": #["~2"]
						del self.main_list[:int(no2)]
					elif no2 == "": #["1~"]
						del self.main_list[int(no1) - 1:]
					else: #["~"]
						self.main_list = []

			elif ":" in key: # ~은 없고 :만 있을때
				no1, no2 = key.split(":")
				if no1 == "" and no2 == "": # [":"]
					pass
				elif no1 == no2: # ["1:1"]
					del self.main_list[int(no1) - 1]
				elif no1 == "": # [":1"]
					del self.main_list[:int(no2)]
				elif no2 == "": # ["1:"]
					del self.main_list[int(no1) - 1:]
				else: # ["1:2"]
					del self.main_list[int(no1) - 1:int(no2)]

		return xy_list(self.main_list)

	def __getitem__(self, key=""):
		"""
		xtlist[2:3]이 실행될때 되는 것
		값을 불러올때 실행되는 부분이다
		이부분의 입력값으로 문자가 가능하다, 다른것은 모두 숫자로만 입력되어져야 한다
		:param key:
		:return:
		"""

		if isinstance(key, slice):
			# :가 있는 형태가 들어갈때 slice 함수로 바뀌면서 이루어 지는 것이다
			return self.main_list[key.start:key.stop:key.step]

		elif type(key) == type(123):
			# 숫자가 들어올때 실행 되는 것
			value = self.main_list[key]
			if type(value) == type([]) or type(value) == type(()):
				return xy_list(value)
			else:
				return value
		elif key == None:
			return None
		elif type(key) == type("abc"):
			if "~" in key:
				if ":" in key:
					# 2 차원의 자료 요청건
					value1, value2 = key.split(":")
					if "~" in value1:
						start, end = value1.split("~")
						if not start and not start:
							temp1 = self.main_list
						elif start and not start:
							temp1 = self.main_list[int(start) - 1:]
						elif not start and start:
							temp1 = self.main_list[:int(end)]
						elif start and start:
							temp1 = self.main_list[int(start) - 1:int(end)]
					elif value1 == "":
						temp1 = self.main_list
					else:
						temp1 = [self.main_list[int(value1) - 1]]

					if "~" in value2:
						start, end = value2.split("~")
						if not start and not end:
							return temp1
						elif start and not end:
							result = []
							for one in temp1:
								result.append(one[int(start) - 1:])
							return xy_list(result)
						elif not start and end:
							result = []
							for one in temp1:
								result.append(one[:int(end)])
							return xy_list(result)
						elif start and end:
							result = []

							for one in temp1:
								result.append(one[int(start) - 1:int(end)])
							return xy_list(result)
					elif value2 == "":
						return temp1
					else:
						result = []
						for one in temp1:
							result.append(one[int(value2) - 1])
						return xy_list(result)
				else:
					# ~은 있으나 :이 없을때
					no1, no2 = key.split("~")
					if no1 == no2 and no1 != "" and no2 != "":
						return xy_list(self.main_list[int(no1) - 1])
					else:
						if no1 == "":
							no1 = None
						else:
							no1 = int(no1) - 1
						if no2 == "":
							no2 = None
						else:
							no2 = int(no2)
						return xy_list(self.main_list[no1:no2])
			elif ":" in key:
				# ~은 없고 :만 있을때
				no1, no2 = key.split(":")
				if no1 == "" and no2 == "":
					return xy_list(self.main_list)
				elif no1 == no2:
					return xy_list(self.main_list[int(no1) - 1])
				elif no1 == "":
					return xy_list(self.main_list[:int(no2)])
				elif no2 == "":
					return xy_list(self.main_list[int(no1) - 1:])
				else:
					return xy_list(self.main_list[int(no1) - 1:int(no2)])
			else:
				value = self.main_list[int(key.strip()) - 1]
				if type(value) == type([]) or type(value) == type(()):
					return xy_list(list(value))
				else:
					return value

	def __init__(self, input_data=None):
		"""
		어떤 입력자료가 오더라도 리스트로 만들어 주는 것
		xy_list의 내부적으로는 일반 list와 같은 형태로 계산이 된다

		만약 xy_list가 들어오면 그 자료형으로 되는 것

		:param input_data:
		:return:
		"""
		self.main_list = []

		if type(input_data) == type(()):  # 듀플일때
			self.main_list = list(input_data)
		elif type(input_data) == type([]):  # list일때
			self.main_list = input_data
		elif type(input_data) == type(xy_list):  # xy_list일때
			self.main_list = input_data
		elif type(input_data) == type(set()):  # set일때
			self.main_list = list(input_data)
		elif type(input_data) == type({}):  # 사전일때
			self.main_list = list(input_data.items())
		elif input_data == None:
			self.main_list = []
		else:
			self.main_list = [input_data]

	def __iter__(self):
		"""
		for문과 같이 반복을 할때 시작되는 부분
		아마도 레지스터에 들어가는 부분인것 같다
		:return:
		"""
		self.current_index = 0
		return self

	def __len__(self):
		"""
		len(x)를 하면 실행되는 부분
		"""
		return len(self.main_list)

	def __next__(self):
		"""
		iter부분을 한번 실행이 된 이후에 Stopiteration이 될때 까지 계속 반복이 된다
		for문이 실행될때 iter과 연동해서 일이 일어난다
		"""
		if self.current_index < len(self.main_list):
			# 갯수만큼 반복이 되는 것
			value = self.main_list[self.current_index]
			if type(value) == type([]):
				x = xy_list(value)
			else:
				x = value
			self.current_index += 1
			return x
		raise StopIteration

	def __setitem__(self, input_no, input_data):
		"""
		xy_list[2] ="abc"와같이 값을 집어 넣을때 실행되는 것
		값을 입력할때 사용되는 부분
		"""
		input_data = self.check_input_data(input_data)
		if type(input_no) == type("abc"):
			input_no = int(input_no) - 1
		else:
			self.check_no(input_no)
		self.main_list[input_no] = input_data

	def __str__(self):
		"""
		print(xy_list_obj)하면 실행되는 코드
		리스트 객체를 프린트하면 나오는것은 객체가 아니라, 그모양의 문자열일뿐이다
		"""

		result = ""
		if len(self.main_list) > 20:
			for one in self.main_list[:5]:
				result = result + str(one) + "\n"
				result = result + "\n ======== head(5 lines) : tail(5 lines) ============	\n\n"
			for one in self.main_list[-5:]:
				result = result + str(one) + "\n"
		else:
			result = str(self.main_list)
		return result

	def __sub__(self, other):
		#print("빼기")
		other = self.to_general_list(other)
		for one in other:
			if one in self.main_list:
				self.main_list.remove(one)
		return xy_list(self.main_list)

	def all(self):
		"""
		모든 객체를 문자열로 돌려주는 것
		이것은 객체이름을 print하면 나타나는 것이다
		"""
		return self.main_list

	def append(self, input_data):
		"""
		기본기능과 동일
		
		:param input_data: 입력으로 들어오는 자료
		:return: 
		"""
		input_data = self.check_input_data(input_data)
		#print("append용 자료 => ", input_data)
		self.main_list.append(input_data)
		return xy_list(self.main_list)

	def append_with_unique(self, input_data):
		"""
		기존자료에 없는 새로운 것만 추가하게 하는것

		:param input_data: 입력으로 들어오는 자료
		:return: 
		"""
		input_data = self.check_input_data(input_data) #어떤 자료라도 리스트로 만드는 것
		for one_value in input_data:
			if not one_value in self.main_list:
				self.main_list.append(one_value)
		return xy_list(self.main_list)

	def change(self, input_no, value):
		"""
		값을 변경하는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param value:
		:return:
		"""
		dic_data = self.check_input_no(input_no)
		no = dic_data["start"]
		self.main_list[no-1]= value

	def change_all_tuple_n_set_to_list(self, input_any_data):
		result = self.__check_all_tuple_n_set_to_list(input_any_data)
		return result

	def change_value_by_index(self, input_index, input_data):
		"""
		n번째 값을 바꾸는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_data:
		:return:
		"""
		self.main_list[input_index] = input_data
		return xy_list(self.main_list)

	def change_value_by_no(self, input_no, input_data):
		"""
		기본자료가 1차원자료라고 생각을 하는 것이다
		n번째 값을 바꾸는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_data:
		:return:
		"""
		self.main_list[input_no - 1] = input_data
		return xy_list(self.main_list)

	def check_index(self, input_index):
		if input_index < 0:
			raise IndexError("0이상의 숫자를 입력하세요")

	def check_input_data(self, input_data):
		"""
		입력으로 들어오는 자료를 확인하는 것이다
		:param input_data:
		:return:
		"""
		if type(input_data) == type(()):  # 듀플일때
			result = list(input_data)
		elif type(input_data) == type([]):  # list일때
			result = input_data
		elif type(input_data) == type(xy_list):  # xy_list일때
			result = input_data
		elif type(input_data) == type(set()):  # set일때
			result = list(input_data)
		elif type(input_data) == type({}):  # 사전일때
			result = list(input_data.items())
		elif type(input_data) == type(123):  # 숫자일때
			result = input_data
		elif type(input_data) == type("abc"):  # 문자일때
			result = input_data
		elif input_data == None:
			result = []
		else:
			result = [input_data]
		return result

	def check_input_index(self, input_index):
		"""
		입력번호를 확인하는 것이다 (index : 0 1부터 시작되는 것)
		"""
		if input_index != type(123):
			raise IndexError("숫자를 입력하세요")

	def check_input_no(self, input_no):
		"""
		입력번호를 확인하는 것이다 (no : 1부터 시작되는 것)
		입력값으로 들어오는 경우그 정수와 문자가 가증한데,
		두 경우에 따라서 어떤 것이 있는지 확인하는 것이다

		input_list["start~7"]
		input_list["~end"]
		input_list["3~4"]

		"""
		result = {}
		if type(input_no) == type("abc"):
			if "~" in input_no:
				start, end = str(input_no).split("~")
				if start == "":
					result["start"] = 1
				else:
					result["start"] = int(start)
				if end == "":
					result["end"] = None
				else:
					result["end"] = int(end) + 1
			else:
				result["start"] = int(input_no)
		elif type(input_no) == type(123):
			result["start"] = int(input_no)

		return result

	def check_list_style(self, input_data=""):
		"""
		입력값의 형태를 알아 내는 것
		어떤 자료가 오더라도 형태를 알아야 다른것으로 변경하거나 바꿀수가 있다

		:param input_data:
		:return:
		"""
		if input_data == "":
			input_data = self.main_list
		input_data = self.to_general_list(input_data)
		temp = ""
		temp_set = set()
		temp_no = set()
		if type(input_data) == type([]) or type(input_data) == type(()):
			for one in input_data:
				if type(one) == type([]) or type(one) == type(()):
					temp_set.add("list")
					temp_no.add(len(one))
				elif type(one) == type("abc") or one == None or type(one) == type(123):
					temp_set.add("str")
			if len(temp_set) == 1 and "list" in temp_set:
				if len(temp_no) == 1:
					temp = "l2d_same_len"
				else:
					temp = "l2d"
			elif len(temp_set) == 1 and "str" in temp_set:
				temp = "l1d"
			else:
				temp = "list_str_mix"
		elif type(input_data) == type({}):
			temp = "dic"
		elif type(input_data) == type("abc"):
			temp = "str"
		elif type(input_data) == type(123):
			temp = "int"
		elif input_data == None:
			temp = "none"
		return temp

	def check_max_len(self, input_data_2d):
		"""
		2차원자료에서 가장 긴것을 확인한다
		"""
		temp = 0
		for l1d in input_data_2d:
			temp = max(temp, len(l1d))
		return temp

	def check_no(self, input_no):
		"""
		입력으로 들어오는 숫자가 0이 아닌것을 확인 하는 것
		"""
		if input_no == 0 and type(input_no) != type(123):
			raise IndexError("0이 아닌 숫자를 입력하세요")

	def clear(self):
		"""
		모든값을 삭제하는 것
		"""
		return self.main_list.clear()

	def copy(self):
		"""
		일반적인 copy는 아니다
		"""
		return deepcopy(self.main_list)

	def count(self, input_data=None):
		"""
		len과 같은 의미이다

		:param input_data:
		:return:
		"""
		if input_data == None:
			return len(self.main_list)
		else:
			return self.main_list.count(input_data)

	def deepcopy(self):
		"""
		deepcopy기능을 만든 것이다
		"""
		return deepcopy(self.main_list)

	def delete_by_value(self, input_data, option=""):
		"""
		값을 넣으면 제일 먼저 만나는 같은 값을 삭제한다
		"""
		for index, one in enumerate(self.main_list):
			if one == input_data:
				del self.main_list[index]
				if option == "":
					break
				else:
					pass

	def delete_all_by_value(self, input_data):
		"""
		값을 넣으면 모든 같은 값을 삭제한다

		:param input_data:
		:return:
		"""
		for index, one in enumerate(self.main_list):
			if one == input_data:
				del self.main_list[index]

	def delete_by_x(self, input_no):
		"""
		n번째의 값을 삭제하는 것
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		del self.main_list[input_no - 1]
		return xy_list(self.main_list)

	def extend(self, input_data):
		"""
		기존자료의 뒷부분에 연결하는 것

		:param input_data:
		:return:
		"""
		input_data = self.to_general_list(input_data)
		self.main_list.extend(input_data)
		return xy_list(self.main_list)

	def fromto(self, start, end):
		"""
		자료의 일부를 갖고오는 것입니다

		:param start:
		:param end:
		:return:
		"""
		self.check_no(start)
		self.check_no(end)
		return self.main_list[min(start, end) - 1:max(start, end)]

	def filter_by_nth_style(self, input_list, nth_style, nth_only=""):
		"""
		리스트자료를 쉽게 갖고오는 방법을 해보는것
		css를 공부하다, 2n+1과같은 형식이 좋을것 같아서 만들어 봄
		sample = [
		"3~5",
		"3+5, 2n+1", #=> 3에서 5개를
		"-3-5, 2n+1",# => 3에서 5개를
		"3~5,4~5, 2n+1",
		"3,5,7,9",
		"2n+1",
		"even",
		"odd",
		]
		:param input_list:
		:param nth_style:
		:param nth_only:
		:return:
		"""
		rex = xy_re.xy_re()

		if type(input_list) == type(xy_list):
			print("xy_list 입니다")
			input_list = input_list.to_list()
			print(input_list)
		result = []

		# 2n+1의 형식이 아닌 단어가 들어간 경우 (짝수, 홀수등의 표현이 가능하도록)
		# 현재 가능한 단어 : even, odd
		if nth_style == "even":
			result = input_list[0::2]
		elif nth_style == "odd":
			result = input_list[1::2]
		elif nth_style.startswith("not"):
			pass
		else:
			c_list = nth_style.split(",")
			for one in c_list:
				aaa = rex.search_all_by_xsql("[+-:0~1][숫자:1~][~:1~1][+-:0~1][숫자:1~]", one)  # 3~5
				bbb = rex.search_all_by_xsql("[+-:0~1][숫자:1~][+-:1~1][숫자:1~]", one)  # 3+5,-3-5
				ccc = rex.search_all_by_xsql("[+-:0~1][숫자:1~]", one)  # 숫자만 분리

				# 문자열안에 ~이 들어가 있는가?
				if aaa:
					if len(ccc) == 1 and int(ccc[0][0]) >= 0:  # 0 보다 큰수
						result.extend(input_list[int(ccc[0][0]) - 1:])
					elif len(ccc) == 1 and int(ccc[0][0]) < 0:  # 0 보다 작은수
						result.extend(input_list[int(ccc[0][0]):])
					elif len(ccc) == 2:
						num1 = int(ccc[0][0])
						num2 = int(ccc[1][0])
						if num1 >= 0 and num2 >= 0:
							result.extend(input_list[num1 - 1:num2])
						elif num1 >= 0 and num2 < 0:
							result.extend(input_list[num1 - 1:num2])
						elif num1 < 0 and num2 >= 0:
							result.extend(input_list[num1: num2])
						elif num1 < 0 and num2 < 0:
							result.extend(input_list[num1:num2])

				# ~ 이없는 숫자들만 있는지...
				elif bbb:
					# 기준점에서 양의수는 오른쪽으로 몇번째까지, 음의수는 왼쪽으로 몇번째까지의 의미
					if len(ccc) == 1 and int(ccc[0][0]) >= 0:  # 0 보다 큰수
						result.extend(input_list[int(ccc[0][0]) - 1:])
					elif len(ccc) == 1 and int(ccc[0][0]) < 0:  # 0 보다 작은수
						result.extend(input_list[int(ccc[0][0]):])
					elif len(ccc) == 2:
						num1 = int(ccc[0][0])
						num2 = int(ccc[1][0])
						if num1 >= 0 and num2 >= 0:
							result.extend(input_list[num1 - 1:num1 - 1 + num2])
						elif num1 >= 0 and num2 < 0:
							result.extend(input_list[num1 - 1 + num2:num1 - 1])
						elif num1 < 0 and num2 >= 0:
							result.extend(input_list[num1: num1 + num2])
						elif num1 < 0 and num2 < 0:
							result.extend(input_list[num1 + num2:num1])

				elif not "n" in one and not aaa and not bbb:
					for a1 in ccc:
						num1 = int(a1[0])
						if num1 >= 0:
							result.append(input_list[num1 - 1])
						elif num1 < 0:
							result.append(input_list[num1])
		print(result)

		# 2n+1과같은 형식이 있는지 확인 하는 것
		nth_jf = None
		nth_full = rex.search_all_by_xsql("[+-:0~1][숫자:1~]n[+-:0~1][숫자:1~]", nth_style)
		if nth_full:
			nth_jf = nth_full[0][0]
			nth_style = nth_style.replace(nth_jf, "")

		nth_style = str(nth_style).strip()
		if nth_style.endswith(","):
			nth_style = nth_style[:-1]

		if nth_only:
			nth_jf = nth_only

		if nth_jf:
			print("nth_jf ==> ", nth_jf)
			if result == []:
				result = input_list
			final_result = []
			# 2n+1과 같은 형태의 자료를 갖고오는 것
			nth_list = nth_jf.split("n")
			print("nth_list", nth_list)
			num2 = 0
			num1 = int(nth_list[0])
			if len(nth_list) == 2:
				if nth_list[1] == "":
					num2 = 0
				else:
					num2 = int(nth_list[1])

			len_start = 0
			len_end = len(result)

			len_start = len_start - num2
			len_end = len_end - num2

			len_start = int(len_start / num1)
			len_end = int(len_end / num1)

			for num in range(len_start, len_end + 1):
				new_num = num1 * num + num2
				final_result.append(result[new_num - 1])
			result = final_result
		return result

	def get_dimension_for_input_data(self, input_any_data=""):
		"""
		입력으로 들어온 자료의 차원을 알아내는 함수

		2d : 2차원자료
		1d : 1차원자료
		0d : 문자, 숫자, None과같은 자료

		:param input_any_data:
		:return:
		"""
		if input_any_data == "":
			input_any_data = self.main_list

		data_style = self.check_list_style(input_any_data)
		if data_style == "l2d_same_len" or data_style == "l2d":
			result = "2d"
		elif data_style == "l1d" or data_style == "list_str_mix":
			result = "1d"
		else:
			result = "0d"
		return result

	def index(self, value):
		"""
		값의 index번호를 돌려준다
		:param value:
		:return:
		"""
		return self.main_list.index(value)

	def insert(self, index, value):
		"""
		값을 추가하는 것

		:param index:
		:param value:
		:return:
		"""
		#self.check_no(index)
		return self.main_list.insert(index, value)

	def insert_value_by_ix(self, index, input_data):
		"""
		index번호를 기준으로 값을 넣는 것
		"""
		input_data = self.to_general_list(input_data)
		self.main_list.insert(index, input_data)

		return xy_list(self.main_list)

	def insert_value_by_x(self, x_no, input_data=None):
		"""
		자료하나를 추가하는 것
		"""
		input_data = self.to_general_list(input_data)
		self.main_list.insert(x_no - 1, input_data)
		return xy_list(self.main_list)

	def insert_value_by_y(self, y_no, input_data=None):
		input_data = self.to_general_list(input_data)
		list_style = self.check_list_style(self.main_list)

		if list_style in ["l2d_same_len", "l2d"]:
			for ix in range(len(self.main_list)):
				self.main_list[ix].insert(y_no - 1, input_data)
		elif list_style in ["l1d", "list_str_mix"]:
			self.main_list.insert(y_no - 1, input_data)

		return xy_list(self.main_list)

	def insert_x(self, x_no, input_value=None):
		main_list_status = True
		list_style = self.check_list_style(self.main_list)
		if list_style in ["l2d_same_len", "l2d"]:
			self.main_list.insert(x_no-1, input_value)
		elif list_style in ["l1d", "list_str_mix"]:
			self.main_list.insert(x_no-1, input_value)
		else:
			main_list_status = False
		return main_list_status

	def insert_y(self, y_no, input_value=None):
		"""

		:param y_no:
		:param input_value:
		:return:
		"""

		main_list_status = True
		list_style = self.check_list_style(self.main_list)
		if list_style in ["l2d_same_len", "l2d"]:
			for ix in range(len(self.main_list)):
				self.main_list[ix].insert(y_no-1, input_value)
		elif list_style in ["l1d", "list_str_mix"]:
			self.main_list.insert(y_no-1, input_value)
		else:
			main_list_status= False
		return main_list_status

	def ix(self, x1):
		"""
		ix : 무조건 숫자여야 한다
		"""
		self.check_index(x1)
		return self.main_list[x1]

	def ixy(self, *xy):
		"""
		ixy : 무조건 숫자여야 한다
		"""
		if type(xy) == type([]):
			x,y=xy
		else:
			x, y = xy[0], xy[1]
		return self.main_list[x][y]

	def ixyxy(self, xyxy):
		"""
		ixyxy : 무조건 숫자여야 한다
		"""
		x1, y1, x2, y2 = [min(xyxy[0], xyxy[2]), min(xyxy[1], xyxy[3]), max(xyxy[0], xyxy[2]),	max(xyxy[1], xyxy[3])]
		temp=[]
		for x in range(x1, x2+1):
			temp.append(self.main_list[x][y1:y2+1])
		return temp

	def iy(self, y1):
		"""
		iy : 무조건 숫자여야 한다
		"""
		self.check_index(y1)
		temp=[]
		for one in self.main_list:
			temp.append(one[y1])
		return temp

	def pop(self):
		"""
		일반적인 pop은 제일 뒷것을 하는 것
		"""
		return self.main_list.pop()

	def pop_by_no(self, input_no):
		"""
		no번째의 값을 돌력주고, 그것을 삭제하는것과 같다
		
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return: 
		"""
		self.check_no(input_no)
		temp = self.main_list[input_no-1]
		del self.main_list[input_no-1]
		return temp

	def pop_by_x(self, input_no):
		"""
		일반적인 pop은 제일 뒷것을 하는 데, 이것은 n번째의값을 pop하는것
		
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return: 
		"""
		self.check_no(input_no)
		temp = self.main_list[input_no - 1]
		del self.main_list[input_no - 1]
		return temp

	def pop_first(self):
		"""
		일반적인 pop은 제일 뒷것을 하는 데, 이것은 맨앞의 값을 pop하는것
		"""
		temp = self.main_list[0]
		del self.main_list[0]
		return temp

	def print(self):
		print(self.main_list)

	def pprint(self, input_data=""):
		"""
		각 요소들을 하나씩 출력하는 것

		:param input_data:
		:return:
		"""
		if input_data == "":
			input_data = self.main_list
		else:
			input_data = self.to_general_list(input_data)
		#print(input_data)

		data_style = self.check_list_style(input_data)
		#print(data_style)
		if data_style == "l2d_same_len" or data_style == "l2d":
			for l1d in input_data:
				print(l1d)
		elif data_style == "l1d" or data_style == "list_str_mix":
			for l0d in input_data:
				print(l0d)
		else:
			print(input_data)

	def read(self, input_no):
		"""
		값읽기 : n번째의 값을 읽어오기
		
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return: 
		"""
		dic_data = self.check_input_no(input_no)
		no = dic_data["start"]
		return self.main_list[no-1]

	def read_by_ix(self, x1):
		"""
		i : index의 값 (index : 0부터 시작하는 값)
		ix : 무조건 숫자여야 한다
		"""
		self.check_input_index(x1)
		return self.main_list[x1]

	def read_by_ixy(self, ixy):
		"""
		i : index의 값 (index : 0부터 시작하는 값)
		ixy : 무조건 숫자여야 한다
		"""
		if type(ixy) == type([]):
			x, y = ixy
		else:
			x, y = ixy, ixy
		return self.main_list[x][y]

	def read_by_ixyxy(self, xyxy):
		"""
		i : index의 값 (index : 0부터 시작하는 값)
		ixyxy : 무조건 숫자여야 한다
		"""
		x1, y1, x2, y2 = [min(xyxy[0], xyxy[2]), min(xyxy[1], xyxy[3]), max(xyxy[0], xyxy[2]), max(xyxy[1], xyxy[3])]
		result = []
		for x in range(x1, x2 + 1):
			result.append(self.main_list[x][y1:y2 + 1])
		return result

	def read_by_iy(self, y1):
		"""
		1차원의 리스트위 값을 index번호로 읽어오기
		i : index의 값을 의미 (index : 0부터 시작하는 값)
		
		:param y1: 
		:return: 
		"""
		self.check_input_index(y1)
		result = []
		for one in self.main_list:
			result.append(one[y1])
		return result

	def read_by_x(self, x1):
		"""
		x1 : 무조건 숫자여야 한다
		n번째의 자료를 갖고오는것과 같지만, x, y의 동일성을 위해서 만든것이다
		"""
		self.check_no(x1)
		return self.main_list[x1 - 1]

	def read_by_xyxy(self, xyxy):
		"""
		xyxy : 무조건 숫자여야 한다
		"""
		x1, y1, x2, y2 = [min(xyxy[0], xyxy[2]), min(xyxy[1], xyxy[3]), max(xyxy[0], xyxy[2]), max(xyxy[1], xyxy[3])]
		result = []
		for x in range(x1 - 1, x2):
			result.append(self.main_list[x][y1 - 1:y2])
		return result

	def read_by_y(self, y1):
		"""
		y1 : 무조건 숫자여야 한다
		만약 2차원의 자료라면 각 n번째의 자료를 따로 갖고오는 것이다
		만약 1차원의 자료라면 x와 같은 효과를 나타낸다
		"""
		self.check_no(y1)

		temp = self.check_list_style(self.main_list)
		if "l2d" in temp:
			result = []
			for one in self.main_list:
				result.append(one[y1 - 1])
		elif "l1d" in temp:
			result = self.main_list[y1 - 1]
		return result

	def read_by_yy(self, y1, y2):
		"""
		2차원자료에서 세로영역들만 갖고오는 것이다
		"""
		self.check_no(y1)
		self.check_no(y2)

		temp = self.check_list_style(self.main_list)
		if "l2d" in temp:
			result = []
			for one in self.main_list:
				result.append(one[y1 - 1:y2])
		elif "l1d" in temp:
			result = self.main_list[y1 - 1:y2]
		return result

	def read_from_no1_to_no2(self, start, end):
		"""
		(1,2)의 형식으로 사용하고, 1~2와 같은 의미이다
		"""
		self.check_no(start)
		self.check_no(end)
		return self.main_list[min(start, end) - 1:max(start, end)]

	def read_by_xx(self, x1, x2):
		"""
		그냥 [2:3]과같은 형태를 사용해도 되지만,
		yy와의 형평성을 위해선 만든것이다
		:param x1:
		:param x2:
		:return:
		"""
		self.check_no(x1)
		self.check_no(x2)
		return self.main_list[x1 - 1:x2]

	def replace_by_step(self, input_value, step=1):
		"""
		매 n번째의 값을 바꾸고 싶을때

		:param input_value:
		:param step:
		:return:
		"""
		for num in range(0, len(self.main_list), step):
			self.main_list[num] = input_value
		return self.main_list

	def remove(self, value):
		return self.main_list.remove(value)

	def reverse(self):
		"""
		반대로 정렬하는 것
		:return:
		"""
		return self.main_list.reverse()

	def sort(self, *arg_list, **arg_dic):
		"""
		일반적인 장렬 방법
		"""
		return self.main_list.sort(*arg_list, **arg_dic)

	def sort_by_len(self):
		"""
		문자의 길이를 기준으로 정렬하는 것
		:return:
		"""

		self.main_list.sort(key=lambda x: len(str(x)))
		return self.main_list

	def sort_2d_by_index(self, index_no):
		"""
		2차원자료의 i번째를 기준으로 정렬하는 것입니다

		:param index_no:
		:return:
		"""
		none_temp = []
		str_temp = []
		int_temp = []

		for l1d in self.main_list:

			if type(l1d[index_no]) == type(None):
				none_temp.append(l1d)
			elif type(l1d[index_no]) == type("str"):
				str_temp.append(l1d)
			else:
				int_temp.append(l1d)

		result_int = sorted(int_temp, key=lambda x: x[index_no])
		result_str = sorted(str_temp, key=lambda x: x[index_no])
		self.main_list = none_temp + result_int + result_str
		return self.main_list

	def to_general_list(self, input_data=""):
		"""
		입력되는 모든 자료는 일반 list나 xy_list만 가능
		이것은 일반적인 list로 만들어 주는 것

		:param input_data:
		:return:
		"""
		if input_data == "":
			input_data = self.main_list

		if type(xy_list) == type(input_data):
			result = list(input_data)
		elif type(input_data) == type([]):
			result = input_data
		else:
			result = list(input_data)
		return result

	def to_list(self):
		"""
		기본의 자료를 돌려주는 것이다
		xy_list가 아닌 일반 list형으로 만들어서 돌려주는 것

		:return:
		"""
		return self.main_list

	def to_l1d(self):
		"""
		모든 것을 1차원자료로 만드는 것이다
		:return:
		"""
		list_style = self.check_list_style(self.main_list)
		if list_style in ["l2d_same_len", "l2d"]:
			result = []
			for l1d in self.main_list:
				result.extend(l1d)
		elif list_style in ["l1d", "list_str_mix"]:
			result = self.main_list
		elif list_style in ["str", "int"]:
			result = [self.main_list]
		return result

	def to_l2d(self):
		"""
		어떤 자료라도 2차원자료로 만드는 것
		"""
		list_style = self.check_list_style(self.main_list)
		if list_style in ["l2d_same_len", "l2d"]:
			pass
		elif list_style in ["l1d", "list_str_mix"]:
			self.main_list = [self.main_list]
		elif list_style in ["str", "int"]:
			self.main_list = [[self.main_list]]
		return self.main_list

	def to_l2d_with_same_len(self):
		"""
		2차원자료의 y의갯수를 가장 큰것을 기준으로 같은 갯수로 만들기 위해서
		부족한 부분은 None을 추가하는 것이다

		:return:
		"""
		l2d = self.to_l2d()
		max_len = self.check_max_len(l2d)
		new_list_obj = []
		for l1d in l2d:
			differ_no = max_len - len(l1d)
			if differ_no > 0:
				l1d.extend([None] + differ_no)
			new_list_obj.append(l1d)
		return new_list_obj

	def to_unique(self):
		"""
		현재 자료중 고유한것만 갖고오는 것이다
		:return:
		"""
		result = set()
		l2d = self.to_l2d()
		for l1d in l2d:
			for one in l1d:
				result.add(one)
		return list(result)

	def to_set(self):
		"""
		현재 자료중 고유한것만 갖고오는 것이다
		set자료형으로 바꾸는 것이다

		:return:
		"""
		result = set()
		for one in self.main_list:
			result.add(one)
		return result

	def to_unique_with_order(self):
		"""
		현재 자료중 고유한것만 갖고오는 것이다 + 순서도 유지

		:return:
		"""
		new_main_list = []
		for one in self.main_list:
			if not one in new_main_list:
				new_main_list.append(one)
		return new_main_list

	def update(self, input_data):
		"""
		기본자료형에 없는것을 추가한 것입니다

		:param input_data:
		:return:
		"""
		input_data = self.check_input_data(input_data) #append_with_unique와 동일한 코드입니다
		for one_value in input_data:
			if not one_value in self.main_list:
				self.main_list.append(one_value)
		return xy_list(self.main_list)

	def write(self, value, input_no=-1):
		"""
		값을 쓰는것으로 n번째에 값을 쓰는 것이다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param value:
		:return:
		"""
		dic_data = self.check_input_no(input_no)
		no = dic_data["start"]
		self.main_list[no-1] = value

	def write_by_index(self, input_no, input_data):
		"""
		n번째에 값을 넣는 것이다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_data:
		:return:
		"""
		input_data = self.to_general_list(input_data)
		self.main_list[input_no] = input_data

	def write_by_no(self, input_no, input_data):
		"""
		n번째의 값을 바꾸는것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_data:
		:return:
		"""
		input_data = self.to_general_list(input_data)
		self.main_list[input_no - 1] = input_data

	def write_by_xy(self, xy, input_data=None):
		"""
		2차원 리스트 자료의 값을 바꾸는것

		:param xy:
		:param input_data:
		:return:
		"""

		input_data = self.to_general_list(input_data)
		if type(xy) == type([]) and len(xy) == 2:
			if len(xy) == 1 and input_data is None:
				return self.main_list[xy[0] - 1]
			elif len(xy) == 1 and not input_data is None:
				self.main_list[xy[0] - 1] = input_data
			elif len(xy) == 2 and input_data is None:
				return self.main_list[xy[0] - 1][xy[1] - 1]
			elif len(xy) == 1 and not input_data is None:
				self.main_list[xy[0] - 1][xy[1] - 1] = input_data
		elif type(xy) == type(123):
			if input_data is None:
				return self.main_list[xy - 1]
			else:
				self.main_list[xy - 1] = input_data

	def x(self, x1):
		"""
		x1 : 무조건 숫자여야 한다
		n번째의 자료를 갖고오는것과 같지만, x, y의 동일성을 위해서 만든것이다

		:param x1:
		:return:
		"""
		self.check_no(x1)
		return self.main_list[x1-1]

	def xy(self, xy, value=None):
		"""
		2차원의 자료에서 x,y의 값을 갖고오는 것이다

		:param xy:
		:param value:
		:return:
		"""
		if type(xy) == type([]) and len(xy) == 2:
			if len(xy) == 1 and value is None:
				return self.main_list[xy[0] - 1]
			elif len(xy) == 1 and not value is None:
				self.main_list[xy[0] - 1] = value
			elif len(xy) == 2 and value is None:
				return self.main_list[xy[0] - 1][xy[1] - 1]
			elif len(xy) == 1 and not value is None:
				self.main_list[xy[0] - 1][xy[1] - 1] = value
		elif type(xy) == type(123):
			if value is None:
				return self.main_list[xy - 1]
			else:
				self.main_list[xy - 1] = value

	def xyxy(self, xyxy):
		"""
		2차원의 자료를 기준으로 일정 영역의 자료를 갖고노는 것이다
		xyxy : 무조건 숫자여야 한다
		앞에 i가 없으면 일반 숫자이다

		:param xyxy:
		:return:
		"""
		x1, y1, x2, y2 = [min(xyxy[0], xyxy[2]), min(xyxy[1], xyxy[3]), max(xyxy[0], xyxy[2]), max(xyxy[1], xyxy[3])]
		temp = []
		for x in range(x1-1, x2):
			temp.append(self.main_list[x][y1-1:y2])
		return temp

	def y(self, input_y):
		"""
		현재 리스트의 y번째 열들의 값을 돌려주는데, 만약 2차원이면, 
		y번째들을 1차원으로 만들어서 돌려준다
		앞에 i가 없으면 일반 숫자이다
		
		y1 : 무조건 숫자여야 한다
		만약 2차원의 자료라면 각 n번째의 자료를 따로 갖고오는 것이다
		만약 1차원의 자료라면 x와 같은 효과를 나타낸다

		:param input_y:
		:return:
		"""
		self.check_no(input_y)

		temp = self.check_list_style(self.main_list)
		if "l2d" in temp:
			result=[]
			for one in self.main_list:
				result.append(one[input_y-1])
		elif "l1d" in temp:
			result = self.main_list[input_y-1]
		return result


