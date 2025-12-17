# -*- coding: utf-8 -*-
import os, sqlite3  # 내장모듈
import pandas as pd

import xy_excel, xy_util  # xython 모듈

class xy_db:
	"""
	database를 사용하기 쉽게 만든것

	파일이름 : xy_db
	코드안에서 사용할때의 이름 : xdb
	객체로 만들었을때의 이름 : db
	"""
	def __history(self):
		"""
		2024-09-08 : 전체적으로 손을 봄
		"""
		pass
	def __init__(self, db_name=""):
		self.db_name = db_name
		self.utilx = xy_util.xy_util()
		self.excelx = xy_excel.xy_excel()

		self.table_name = ""
		self.con = ""  # sqlite db에 연결되는 것

		if self.db_name != "":
			self.con = sqlite3.connect(db_name, isolation_level=None)
			self.cursor = self.con.cursor()
		self.check_db_for_sqlite(db_name)

	def add_new_line_in_listdb(self, input_list_2d, line_data=[]):
		"""
		| listdb에 새로운 줄 하나를 넣는 것입니다
		| listdb의 형태 : [[y_name-1, y_name_2.....],[[a1, a2, a3...], [b1, b2, b3...], ]]

		예제 :
			>>>  소스 예제
			>>> add_new_line_in_listdb(input_list_2d='2차원리스트', line_data='1차원제목리스트')
			...


		:param input_list_2d: 기본 listdb자료
		:param line_data: 추가할 자료 1줄
		:return:
		"""

		temp = []
		new_no = input_list_2d[-1][0] + 1

		if not line_data:
			for one in range(len(input_list_2d[0]) - 1):
				temp.append(None)
			line_data = temp
		elif len(input_list_2d[0]) - 1 > len(line_data):
			for index in range((len(input_list_2d[0]) - 1) - len(line_data)):
				line_data.append(None)

		line_data.insert(0, new_no)
		input_list_2d.append(line_data)
		return input_list_2d

	def append_df1_in_df2(self, df_obj_1, df_obj_2):
		"""
		dataframe의 끝에 dataframe으로 만든 것을 맨끝에 추가하는것

		:param df_obj_1:
		:param df_obj_2:
		:return:
		"""
		df_obj_1 = pd.concat([df_obj_1, df_obj_2])
		return df_obj_1

	def change_any_data_to_dic(self, input_1, input_2=""):
		"""
		입력되는 자료가 어떤 자료형태라도 사전형식으로 만드는 것

		사용예:
			입력형태 1 : [["컬럼이름1","컬럼이름2"],[["값1-1","값1-2"], ["값2-1","값2-2"]]]
			입력형태 2 : [[["컬럼이름1","값1"],["컬럼이름2","값2"]], [["컬럼이름1","값11"],["컬럼이름3","값22"]]]]
			입력형태 3 : ["컬럼이름1","컬럼이름2"],[["값1-1","값1-2"], ["값2-1","값2-2"]]

		:param input_1:
		:param input_2:
		:return: [{"컬럼이름1":"값1", "컬럼이름2": "값2"}, {"컬럼이름3":"값31", "컬럼이름2": "값33"}......]
		"""

		input_type = 0
		if input_2:
			input_type = 3
		else:
			if type(input_1[0][0]) == type([]):
				input_type = 2
			elif type(input_1[0][0]) != type([]) and type(input_1[1][0]) != type([]):
				input_type = 1

			result = []
			if input_type == 1:
				for value_list_1d in input_1[1]:
					one_line_dic = {}
					for index, column in enumerate(input_1[0]):
						one_line_dic[column] = value_list_1d[index]
					result.append(one_line_dic)
			elif input_type == 2:
				for value_list_2d in input_1:
					one_line_dic = {}
					for index, list_1d in enumerate(value_list_2d):
						one_line_dic[list_1d[0]] = list_1d[1]
					result.append(one_line_dic)
			elif input_type == 3:
				one_line_dic = {}
				for index, list_1d in enumerate(input_2):
					one_line_dic[input_1[index]] = list_1d[index]
				result.append(one_line_dic)
		return result

	def change_any_data_to_list_2d(self, input_data):
		"""
		어떤 자료형이 오더라도 2차원 리스트로 만들어 주는 것

		:param input_data:
		:return:
		"""

		if type(input_data) == type([]) or type(input_data) == type(()):
			if type(input_data[0]) == type([]) or type(input_data[0]) == type(()):
				result = input_data
			else:
				result = [input_data]
		elif type(input_data) == type("123") or type(input_data) == type(123):
			result = [[input_data]]
		else:
			result = input_data

		revise_result = []
		for list_1 in result:
			temp = []
			for one in list_1:
				if one:
					pass
				elif type(one) == type(None) or one == [] or one == ():
					one = None
				elif type(one) == type([]) or type(one) == type(()):
					one = str(one)
				else:
					one = ""
				temp.append(one)
			revise_result.append(list(temp))

		return revise_result

	def change_any_range_to_xyxy(self, input_range=""):
		"""
		어떤 형태의 영역표시자료라도 xyxy형태로 만들어 주는 것이다
		모든 :, ~ 의 스타일을 xyxy스타일로 바꾸는것
		기본은 0으로 시작한다
		["2~3:4~5"], ["1~2"],["2~3:~5"] 등의 형태를 바꿔주는 것
		이런 형태의 영역표시를 xyrange라고 하는것은 어떨지

		:param input_range:
		:return:
		"""

		[x1, y1, x2, y2] = [0, 0, 0, 0]
		if type(input_range) == type("abc"):
			if input_range == "all":
				pass
			elif "~" in input_range:
				if ":" in input_range:
					# 2 차원의 자료 요청건 ["2~3:4~5"]
					value1, value2 = input_range.split(":")
					if "~" in value2:
						start2, end2 = value2.split("~")
						if start2 == "" and end2 == "":  # ["2~3:~"]
							pass
						elif start2 == "" and end2:  # ["2~3:~5"]
							y2 = int(end2)
						elif start2 and end2 == "":  # ["2~3:4~"]
							x2 = int(start2) - 1
						elif start2 and end2:  # ["2~3:4~5"]
							x2 = int(start2) - 1
							y2 = int(end2)
						elif value2 == "":  # ["2~3:"]
							pass
						else:
							pass

					if "~" in value1:
						start1, end1 = value1.split("~")
						if start1 == "" and end1 == "":  # ["~:4~5"]
							pass
						elif start1 and end1 == "":  # ["2~:4~5"]
							x1 = int(start1) - 1
						elif start1 == "" and end1:  # ["~3:4~5"]
							y1 = int(end1)
						elif start1 and end1:  # ["2~3:4~5"]
							x1 = int(start1) - 1
							y1 = int(end1)
						elif value1 == "":  # [:"2~3"]
							pass
						else:
							pass
					else:
						pass

				else:  # ["1~2"], ~은 있으나 :이 없을때
					no1, no2 = input_range.split("~")
					if no1 and no2:
						if no1 == no2:  # ["1~1"]
							x1 = int(no1) - 1
							y1 = int(no2)
						else:  # ["1~2"]
							x1 = int(no1) - 1
							y1 = int(no2)
					elif no1 == "":  # ["~2"]
						y1 = int(no2)
					elif no2 == "":  # ["1~"]
						x1 = int(no1) - 1
					else:  # ["~"]
						pass

			elif ":" in input_range:  # ~은 없고 :만 있을때
				no1, no2 = input_range.split(":")
				if no1 == "" and no2 == "":  # [":"]
					pass
				elif no1 == "all":
					pass
				elif no1 == no2:  # ["1:1"]
					x1 = int(no1)
					y1 = int(no2)
				elif no1 == "":  # [":1"]
					y1 = int(no2)
				elif no2 == "":  # ["1:"]
					x1 = int(no1)
				elif no2 == "all":
					pass
				else:  # ["1:2"]
					x1 = int(no1)
					y1 = int(no2)

		return [x1, y1, x2, y2]

	def change_df_to_dic(self, input_df, style="split"):
		"""
		dataframe자료를 사전형식으로 변경하는것

		변경되는 사전형태는 여러가지가 가능하며, 별도로 선택하지 않으면 split형태를 적용한다
		dic의 형태중에서 여러가지중에 하나를 선택해야 한다

		입력형태 : data = {"calory": [123, 456, 789], "기간": [10, 40, 20]}
		출력형태 : dataframe
		dict :    {'제목1': {'가로제목1': 1, '가로제목2': 3}, '제목2': {'가로제목1': 2, '가로제목2': 4}}
		list :    {'제목1': [1, 2], '제목2': [3, 4]}
		series :  {열 : Series, 열 : Series}
		split :   {'index': ['가로제목1', '가로제목2'], 'columns': ['제목1', '제목2'], 'data': [[1, 2], [3, 4]]}
		records : [{'제목1': 1, '제목2': 2}, {'제목1': 3, '제목2': 4}]
		index :   {'가로제목1': {'제목1': 1, '제목2': 2}, '가로제목2': {'제목1': 3, '제목2': 4}}

		:param input_df:
		:param style:
		:return:

		"""

		checked_style = style
		if not style in ["split", "list", 'series', 'records', 'index']:
			checked_style = "split"
		result = input_df.to_dict(checked_style)
		return result

	def change_df_to_listdb(self, input_df):
		"""
		df자료를 커럼과 값을 기준으로 나누어서 결과를 리스트로 돌려주는 것이다
		listdb형태 : [[컬럼이름1, 컬럼이름2,,,,], [자료1], [자료2]....]

		:param input_df: dataframe객체
		:return: [[컬럼이름1, 컬럼이름2,,,,], [자료1], [자료2]....]
		"""

		col_list = input_df.columns.values.tolist()
		value_list = input_df.values.tolist()
		result = [col_list, value_list]
		return result

	def change_dic_to_listdb(self, input_dic):
		"""
		사전의 자료를 sql에 입력이 가능한 형식으로 만드는 것
		listdb형태 : [[컬럼이름1, 컬럼이름2,,,,], [자료1], [자료2]....]

		:param input_dic:
		:return: [[컬럼이름1, 컬럼이름2,,,,], [자료1], [자료2]....]
		"""
		col_list = list(input_dic[0].keys())
		value_list = []
		for one_col in col_list:
			value_list.append(input_dic[one_col])
		result = [col_list, value_list]
		return result

	def change_list_2d_to_listdb(self, input_list_2d):
		"""
		일반적인 input_list_2d와 df용 input_list_2d는 가로와 세로가 반대로 되어야 하기때문에
		listdb로 해야 할것같다

		:param excel_2d:
		:return:
		"""

		input_list_2d = self.utilx.check_data_types_for_list_2d(input_list_2d)  # 2차원이 아닐때 2차원으로 만들러 주는것
		listdb = self.utilx.change_xylist_to_yxlist(input_list_2d)
		return listdb

	def change_list_2d_to_listdb_1(self, input_list_2d, first_is_title=True):
		"""
		2차원리스트를 제목과 listdb스타일의 자료로 만드는 것

		:param input_list_2d:
		:param first_is_title:
		:return:
		"""

		if first_is_title:
			title_list = input_list_2d[0]
			db_list_2d = self.utilx.change_xylist_to_yxlist(input_list_2d[1:])
		else:
			title_list = []
			db_list_2d = self.utilx.change_xylist_to_yxlist(input_list_2d)
		return [title_list, db_list_2d]

	def change_list_db_to_df(self, input_list_db):
		"""
		리스트 db를 dataframe로 바꾸는 것

		:param col_list: 제목리스트
		:param list_db: 리스트로 만든 database, 2차원 값리스트형
		:return: dataframe로 바꾼것
		"""

		input_df = pd.DataFrame(data=input_list_db[1], columns=input_list_db[0])
		return input_df

	def change_list_db_to_df_v2(self, list_db, y_title_list="", x_title_list=""):
		"""
		2차원 리스트 자료를 dataframe형태로 만들어 주는것

		:param list_db: 리스트로 만든 database, 2차원 값리스트형
		:param y_title_list:
		:param x_title_list:
		:return:
		"""

		dic_l1d = self.change_listdb_n_title_list_to_dic(list_db, y_title_list)
		if x_title_list == "":
			df_obj = pd.DataFrame(dic_l1d)
		else:
			df_obj = pd.DataFrame(dic_l1d, index=x_title_list)
		return df_obj

	def change_list_to_listdb(self, input_list):
		"""
		list 자료를 listdb로 만드는 것
		만약 제목에대한 자료가 없으면, 숫자번호를 제목으로 대신해서 넣는다
		listdb의 형태 : [[컬럼이름1, 컬럼이름2,,,,], ,[[a1, a2, a3...], [b1, b2, b3...], ]]

		:param input_list:
		:return:
		"""

		if input_list[0] != type([]):
			# 1차원자료는 2차원으로 만드는 것
			input_list = [input_list]

		if len(input_list) == 1:
			# 자료가 1개란뜻은 제목리스트가 없다는 것이므로, 만드는것이다
			first_no = 0
			len_1line = len(input_list[0][0])
			for one in input_list[0][0]:
				if type(one) == type("abc"):
					first_no = first_no + 1
			if first_no == len_1line:
				print("aaa")
				# 1번째 문자가 전부 텍스트라면, 이것은 제목일 확률이 높으므로 이것을 제목으로 만든다
				input_list = [input_list[0][0], input_list[0][1:]]
			else:
				# 2차원자료중에서 1번째 자료에 제목부분이 안들어있는 것은 1부터 시작하는 번호로 만든다
				print("bbb")
				title_list = []
				for one in range(len(input_list[0])):
					title_list.append(str(one + 1))
				input_list = [title_list, [input_list]]

		return input_list

	def change_listdb_n_title_list_to_dic(self, listdb, col_list=""):
		"""
		dataframe을 만드는 것은 기본으로 1차원의 series와 제목을 가진 사전형태의 자료를 자동으로 바꾼다

		:param listdb: 리스트로 만든 database, 2차원 값리스트형
		:param col_list:
		:return:
		"""

		temp = []
		result = {}
		if type(listdb) == type([]):
			listdb = self.utilx.check_data_types_for_list_2d(listdb)  # 2차원이 아닐때 2차원으로 만들러 주는것
			listdb = self.utilx.change_list_2d_to_list_2d_as_same_len(listdb)  # 길이가 다를때 제일 긴것으로 똑같이 만들어 주는것
			# 별도로 column의 제목이 없다면, 1번부터 시작하는 번호를 넣어준다
			if col_list == "":
				for index, list_1d in enumerate(listdb):
					temp.append(index + 1)
				col_list = temp

			for index, list_1d in enumerate(listdb):
				result[col_list[index]] = listdb[index]
		else:
			result = listdb
		return result

	def change_listdb_to_df(self, input_listdb):
		"""
		리스트 db를 dataframe로 바꾸는 것

		:param col_list: 제목리스트
		:param listdb: 2차원 값리스트형
		:return: dataframe로 바꾼것
		"""

		input_df = pd.DataFrame(data=input_listdb[1], columns=input_listdb[0])
		return input_df

	def change_listdb_to_df_v2(self, listdb, y_title_list="", x_title_list=""):
		"""
		2차원 리스트 자료를 dataframe형태로 만들어 주는것

		:param listdb: 리스트로 만든 database, 2차원 값리스트형
		:param y_title_list:
		:param x_title_list:
		:return:
		"""

		dic_list_1d = self.change_listdb_n_title_list_to_dic(listdb, y_title_list)
		if x_title_list == "":
			df_obj = pd.DataFrame(dic_list_1d)
		else:
			df_obj = pd.DataFrame(dic_list_1d, index=x_title_list)
		return df_obj

	def change_sqlite_table_to_df(self, db_name, table_name):
		"""
		sqlite의 테이블을 df로 변경

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		sql = "SELECT * From {}".format(table_name)
		sql_result = self.cursor.execute(sql)
		cols = []
		for column in sql_result.description:
			cols.append(column[0])
		input_df = pd.DataFrame.from_records(data=sql_result.fetchall(), columns=cols)
		return input_df

	def change_sqlite_table_to_listdb(self, db_name, table_name):
		"""
		sqlite의 테이블 자료를 리스트로 변경

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return: [2차원리스트(제목), 2차원리스트(값들)]
		"""
		self.check_db_for_sqlite(db_name)
		sql_result = self.cursor.execute("SELECT * From {}".format(table_name))
		cols = []
		for column in sql_result.description:
			cols.append(column[0])
		temp = []
		for one in sql_result.fetchall():
			temp.append(list(one))
		result = [cols, temp]
		return result

	def change_table_name_in_sqlite(self, db_name, table_name_old, table_name_new):
		"""
		현재 db에서 테이블 이름 변경

		:param table_name_old:테이블 이름
		:param table_name_new:테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""

		self.check_db_for_sqlite(db_name)
		sql_sentence = "alter table %s rename to %s" % (table_name_old, table_name_new)
		self.cursor.execute(sql_sentence)

	def change_textrange_to_xyxy(self, input_value):
		"""
		| 개인적으로 만든 이용형태를 것으로,
		| check로 시작하는 메소드는 자료형태의 변경이나 맞는지를 확인하는 것이다
		| dataframe의 영역을 나타내는 방법을 dataframe에 맞도록 변경하는 것이다

		Examples:
			>>> change_textrange_to_xyxy("0:2")
			 	결과 ===> [1, 2]
			>>> change_textrange_to_xyxy("1~2")
			 	결과 ===> 1, 2열
			>>> change_textrange_to_xyxy("1,2,3,4")
			 	===> 1,2,3,4열
			>>> change_textrange_to_xyxy("" 또는 "all")
			 	===> 전부

		:param input_value:
		:return:
		"""
		result = input_value
		if type(input_value) == type("abc"):
			if ":" in input_value:
				pass
			elif "~" in input_value:
				temp = input_value.split("~")
				result = "[" + str(int(temp[0]) - 1) + ":" + temp[1] + "]"
			elif "all" in input_value:
				result = "[:]"
			elif "" in input_value:
				result = "[:]"
			elif "," in input_value:
				changed_one = input_value.split(",")
				result = []
				for item in changed_one:
					result.append(int(item))
		return result

	def change_value_in_dicdb(self, main_dic, i_depth_list, i_value):
		"""
		사전형 database

		:param main_dic:
		:param i_depth_list:
		:param i_value:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				i_dic = i_dic[checked_key][1]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_depth_list[-1])
		i_dic[checked_key1][0] = i_value

	def change_value_in_dicdb_at_all_nth_depth(self, i_dic, target_depth, i_key, i_value, current_depth=1):
		"""
		실제 입력값을 넣었을 때, 모든사전을 다 보면서，n번째 차원의 key가 있는것만，value값으로 바꾸는 것

		:param i_dic:
		:param target_depth:
		:param i_key:
		:param i_value:
		:param current_depth:
		:return:
		"""
		if current_depth == target_depth + 1:
			for key in list(i_dic.keys()):
				if key == i_key:
					i_dic[key] = i_value
		else:
			for key, value in i_dic.items():
				if isinstance(value, dict):
					self.change_value_in_dicdb_at_all_nth_depth(value, target_depth, i_key, i_value, current_depth + 1)

	def change_value_in_listdb_at_xy(self, input_listdb, xy, value):
		"""
		listdb의 x,y좌표에 값을 넣는 것

		:param input_list_2d:
		:param x:
		:param y:
		:param value:
		:return:
		"""
		input_listdb[xy[0]][xy[1]] = value
		return input_listdb

	def check_db_for_sqlite(self, db_name=""):
		"""
		기본적으로 test_db.db를 만든다
		memory로 쓰면, sqlite3를 메모리에 넣도록 한다

		:param db_name: 데이터베이스 이름
		:return:
		"""

		if db_name == "" or db_name == "memory":
			self.con = sqlite3.connect(":memory:")
		elif db_name == "" or db_name == "test":  # 데이터베이스를 넣으면 화일로 만든다
			db_name = "test_db.db"
			self.con = sqlite3.connect(db_name, isolation_level=None)
		else:
			self.con = sqlite3.connect(db_name, isolation_level=None)
		self.cursor = self.con.cursor()

	def check_df_range(self, input_range):
		"""
		df의 영역을 나타내는 방법을 df에 맞도록 변경하는 것이다

		:param input_range:
		:return:
		"""

		result = []
		if type(input_range) == type("abc"):
			result = self.change_textrange_to_xyxy(input_range)
		if type(input_range) == type([]):
			for one_value in input_range:
				result.append(self.change_textrange_to_xyxy(one_value))
		return result

	def check_input_data(self, col_list, data_list):
		"""
		컬럼의 이름이 없거나하면 기본적인 이름을 만드는 것이다
		컬럼의 이름이 없으면, 'col+번호'로 컴럼이름을 만드는 것

		:param col_list: y컴럼의 이름들
		:param data_list:
		:return:
		"""

		result = []
		if col_list == "" or col_list == []:
			for num in range(len(data_list)):
				result.append("col" + str(num))
		else:
			result = col_list
		return result

	def check_ix_in_df(self, input_df, input_index):
		"""
		index가 기본 index인 0부터 시작하는 것이 아닌 어떤 특정한 제목이 들어가 있는경우는
		숫자로 사용할수가 없다. 그래서 그서을 확인후에 기본 index가 아닌 경우는 제목으로 변경해 주는
		것을 할려고 한다
		"2~3"  ===>  '인천':'대구'

		:param input_df:
		:param input_index:
		:return:
		"""

		title_list = input_df.index
		result = None
		[ix1, iy1, ix2, iy2] = self.change_any_range_to_xyxy(input_index)
		if ix1 == 0 and ix2 == 0:
			result = "'" + str(title_list[ix1]) + "':'" + str(title_list[- 1]) + ""
		else:
			result = "'" + str(title_list[ix1]) + "':'" + str(title_list[ix2]) + ""
		return result

	def check_ix_in_df_old(self, input_df, input_index):
		"""
		index가 기본 index인 0부터 시작하는 것이 아닌 어떤 특정한 제목이 들어가 있는경우는
		숫자로 사용할수가 없다. 그래서 그서을 확인후에 기본 index가 아닌 경우는 제목으로 변경해 주는
		것을 할려고 한다
		"2~3"  ===>  '인천':'대구'

		:param input_df: dataframe객체
		:param input_index:
		:return:
		"""
		index_list = input_df.index
		two_data = False
		result = input_index
		if ":" == input_index or "all" == input_index or "" == input_index:
			result = ":"
		elif ":" in input_index:
			two_data = input_index.split(":")
		elif "~" in input_index:
			temp = input_index.split("~")
			two_data = [str(int(temp[0]) - 1), temp[1]]

		if two_data:
			if int(two_data[1]) >= len(index_list):
				result = "'" + str(index_list[int(two_data[0])]) + "':"
			else:
				result = "'" + str(index_list[int(two_data[0])]) + "':'" + str(index_list[int(two_data[1]) - 1]) + "'"
		return result

	def check_iy_in_df(self, input_df, input_index):
		"""
		index가 기본 index인 0부터 시작하는 것이 아닌 어떤 특정한 제목이 들어가 있는경우는
		숫자로 사용할수가 없다. 그래서 그것을 확인후에 기본 index가 아닌경우는 제목으로 변경해 주는
		것을 할려고 한다
		"2~3"  ===>  '인천':'대구'

		:param input_df: dataframe객체
		:param input_index:
		:return:
		"""

		index_list = input_df.columns
		result = input_index
		two_data = False
		if ":" == input_index or "all" == input_index or "" == input_index:
			result = ":"
		elif ":" in input_index:
			two_data = input_index.split(":")
		elif "~" in input_index:
			temp = input_index.split("~")
			two_data = [str(int(temp[0]) - 1), temp[1]]
		if two_data:
			if type(int(two_data[0])) == type(1) and type(int(two_data[1])) == type(1):
				if int(two_data[1]) >= len(index_list):
					result = "'" + str(index_list[int(two_data[0])]) + "':"
				else:
					result = "'" + str(index_list[int(two_data[0])]) + "':'" + str(
						index_list[int(two_data[1]) - 1]) + "'"
		return result

	def check_range_in_df(self, input_value):
		"""
		개인적으로 만든 이용형태를 것으로,
		check로 시작하는 메소드는 자료형태의 변경이나 맞는지를 확인하는 것이다
		dataframe의 영역을 나타내는 방법을 dataframe에 맞도록 변경하는 것이다
		x=["0:2"] ===> 1, 2열
		x=["1~2"] ===> 1, 2열
		x=["1,2,3,4"] ===> 1,2,3,4열
		x=[1,2,3,4]  ===> 1,2,3,4열
		x=""또는 "all" ===> 전부

		:param input_value:
		:return:
		"""
		result = self.change_textrange_to_xyxy(input_value)
		return result

	def check_sqlite_db_name_in_folder(self, db_name="", path="."):
		"""
		경로안에 sqlite의 database가 있는지 확인하는 것이다
		database는 파일의 형태이므로 폴더에서 화일이름들을 확인한다

		:param db_name: 데이터베이스 이름
		:param path: 경로
		:return:
		"""
		db_name_all = self.utilx.get_all_filename_in_folder(path)
		if db_name in db_name_all:
			result = db_name
		else:
			result = ""
		return result

	def check_title_name(self, temp_title):
		"""
		각 제목으로 들어가는 글자에 대해서 변경해야 하는것을 변경하는 것이다

		:param temp_title:
		:return:
		"""
		for temp_01 in [[" ", "_"], ["(", "_"], [")", "_"], ["/", "_per_"], ["%", ""], ["'", ""], ['"', ""], ["$", ""],
						["__", "_"], ["__", "_"]]:
			temp_title = temp_title.replace(temp_01[0], temp_01[1])
		if temp_title[-1] == "_": temp_title = temp_title[:-2]
		return temp_title

	def check_y_title(self, y_name):
		"""
		컬럼의 이름으로 쓰이는 것에 이상한 글자들이 들어가지 않도록 확인하는 것이다

		:param y_name: y 컬럼이름
		:return:
		"""
		for data1, data2 in [["'", ""], ["/", ""], ["\\", ""], [".", ""], [" ", "_"]]:
			y_name = y_name.replace(data1, data2)
		return y_name

	def connect_db_for_sqlite(self, db_name=""):
		"""
		database에 연결하기

		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

	def delete_all_empty_y_in_df(self, input_df):
		"""
		dataframe의 빈열을 삭제
		제목이 있는 경우에만 해야 문제가 없을것이다

		:param input_df:
		:return:
		"""
		nan_value = float("NaN")
		input_df.replace(0, nan_value, inplace=True)
		input_df.replace("", nan_value, inplace=True)
		input_df.dropna(how="all", axis=1, inplace=True)
		return input_df

	def delete_empty_y_in_df(self, input_df):
		"""
		dataframe에서 빈 y줄을 삭제하는 것

		:param input_df:
		:return:
		"""
		result = self.delete_all_empty_y_in_df(input_df)
		return result

	def delete_empty_y_in_sqlite_table(self, db_name, table_name):
		"""
		테이블의 컬럼중에서 아무런 값도 없는 컬럼을 삭제한다

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		y_name_all = self.read_all_title_list_in_sqlite(table_name, db_name)

		for y_name in y_name_all:
			sql = ("select COUNT(*) from %s where %s is not null" % (table_name, y_name))
			self.cursor.execute(sql)
			if self.cursor.fetchall()[0][0] == 0:
				# 입력값이 없으면 0개이고, 그러면 삭제를 하는 것이다
				sql = ("ALTER TABLE %s DROP COLUMN %s " % (table_name, y_name))
				self.cursor.execute(sql)

	def delete_sqlite_memory_db(self):
		"""
		memory db는 connection을 close시키면, db가 삭제된다

		:return:
		"""
		self.con.close()

	def delete_sqlite_table(self, db_name, table_name):
		"""
		입력형태 : 테이블이름

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		self.cursor.execute("DROP TABLE " + table_name)

	def delete_value_in_dicdb(self, main_dic, i_depth_list):
		"""
		사전형 db에서 모든 n번째 깊이의 값을 삭제하는 것

		:param main_dic:
		:param i_depth_list:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				i_dic = i_dic[checked_key][1]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_depth_list[-1])
		i_dic[checked_key1][0] = None

	def delete_value_in_dicdb_with_below(self, main_dic, i_depth_list):
		"""
		사전형 db에서 모든 n번째 깊이 이하의 모든 입력값을 삭제하는 것

		:param main_dic:
		:param i_depth_list:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				i_dic = i_dic[checked_key][1]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_depth_list[-1])
		del i_dic[checked_key1]

	def delete_x_line_in_listdb_by_no(self, input_list_2d, input_no):
		"""
		listdb에서 입력으로 들어오는 n번째 x라인을 제거하는것

		:param input_list_2d:
		:param input_no:
		:return:
		"""
		del input_list_2d[input_no]
		return input_list_2d

	def delete_y_in_listdb_by_iy_list(self, input_listdb, input_index_list=[1, 2, 3]):
		"""
		index번호를 기준으로 y라인을 삭제하는것
		listdb의 형태 : [[y_name-1, y_name_2.....],[[a1, a2, a3...], [b1, b2, b3...], ]]

		:param input_listdb:
		:param input_index_list:
		:return:
		"""
		# 맨뒤부터 삭제가 되어야 index가 유지 된다
		checked_input_index_list = input_index_list.reverse()

		for index in checked_input_index_list:
			# y열의 제목을 지우는것
			input_listdb[0].pop(index)

			# 각 항목의 값을 지우는것
			for num in range(len(input_listdb[1])):
				input_listdb[1][num].pop(index)
		return input_listdb

	def delete_y_in_listdb_by_title_list(self, input_listdb, input_name_list=["y_name_1, y_name_2"]):
		"""
		y라인 이름을 기준으로 삭제하는것
		listdb의 형태 : [[y_name-1, y_name_2.....],[[a1, a2, a3...], [b1, b2, b3...], ]]

		:param input_listdb:
		:param input_name_list:
		:return:
		"""

		title_dic = {}
		for index in range(len(input_listdb[0])):
			title_dic[input_listdb[0][index]] = index

		input_index_list = []

		for name in input_name_list:
			index = title_dic[name]
			input_index_list.append(index)

		# 맨뒤부터 삭제가 되어야 index가 유지 된다
		result = self.delete_y_in_listdb_by_iy_list(input_listdb, input_index_list)
		return result

	def delete_y_in_sqlite_table_by_title_list(self, db_name, table_name, y_name_list):
		"""
		컬럼 삭제
		입력형태 : ["col_1","col_2","col_3"]
		y_name : 컬럼이름

		:param table_name: 테이블 이름
		:param y_name_list:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		if y_name_list:
			for y_name in y_name_list:
				sql = ("ALTER TABLE %s DROP COLUMN %s " % (table_name, y_name))
				self.cursor.execute(sql)

	def delete_y_line_in_listdb_by_no(self, input_list_2d, input_no):
		"""
		listdb에서 입력으로 들어오는 n번째 y라인을 제거하는것

		:param input_list_2d: 2차원 리스트
		:param input_no: 번호
		:return:
		"""
		for index in range(len(input_list_2d)):
			del input_list_2d[index][input_no]
		return input_list_2d

	def df_easy_call_by_no(self, df_obj, x="", y=""):
		"""
		사용하기 쉽도록 문법을 만든것. LOC는 않됨
		x="1:2", "1~2" ===> 1~2열
		x="1,2,3,4" ===> 1,2,3,4열
		x=""또는 "all" ===> 전부

		:param df_obj:
		:param x:
		:param y:
		:return:
		"""

		if ":" in x or "~" in x:
			x = x.replace("~", ":")
			x_split = x.split(":")
			temp_x = range(int(x_split[0]), int(x_split[1]) + 1, 1)
		elif x == "":
			temp_x = range(0, len(df_obj))
		else:
			temp_x = []
			x_split = x.split(",")
			for one in x_split:
				temp_x.append(int(one))

		if ":" in y or "~" in y:
			y = y.replace("~", ":")
			y_split = y.split(":")
			temp_y = range(int(y_split[0]), int(y_split[1]) + 1, 1)
		elif y == "":
			temp_y = range(0, len(df_obj.columns))
		else:
			temp_y = []
			y_split = y.split(",")
			for one in y_split:
				temp_y.append(int(one))

		print(temp_x, temp_x)
		result = df_obj.iloc[temp_x, temp_y]
		return result

	def extend_dic1_to_dic2(self, dic1, dic2):
		"""
		사전1에 사전2의 자료를 추가하는 것

		:param dic1:
		:param dic2:
		:return:
		"""
		for one_key in dic2.keys:
			if not one_key in dic1.keys:
				dic1[one_key] = dic2[one_key]
		return dic1

	def extend_list1_to_list2(self, list1, list2):
		"""
		list1의 자료를 list2에 추가하는 것

		:param list1:
		:param list2:
		:return:
		"""
		list1.extend(list2)
		return list1

	def extend_set1_to_set2(self, set1, set2):
		"""
		set1의 자료를 set2에 추가하는 것

		:param set1:
		:param set2:
		:return:
		"""
		set1.update(set2)
		return set1

	def get_all_db_name_in_path(self, path=".\\"):
		"""
		모든 database의 이름을 갖고온다
		모든이 붙은것은 맨뒤에 all을 붙인다

		:param path: 경로
		:return:
		"""
		result = []
		for fname in os.listdir(path):
			if fname[-3:] == ".db":
				result.append(fname)
		return result

	def get_all_table_name_in_sqlite_memory_db(self):
		self.cursor.execute("select name from sqlite_master where type = 'table'; ")
		table_list = self.cursor.fetchall()
		all_table_name = []
		for one in table_list:
			all_table_name.append(one[0])

		return all_table_name

	def get_all_title_in_sqlite_table(self, db_name, table_name):
		"""
		해당하는 테이의 컬럼구조를 갖고온다
		입력형태 : 테이블이름
		출력형태 : 컬럼이름들

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		self.cursor.execute("PRAGMA table_info('%s')" % table_name)
		sql_result = self.cursor.fetchall()
		result = []
		for one_list in sql_result:
			result.append(one_list[1])
		return result

	def get_all_y_property_for_sqlite_table(self, db_name, table_name):
		"""
		해당하는 테이블의 컬럼의 모든 구조를 갖고온다

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		self.cursor.execute("PRAGMA table_info('%s')" % table_name)
		result = []
		for temp_2 in self.cursor.fetchall():
			result.append(temp_2)
		return result

	def get_title_list_from_no1_to_no2_in_sqlite_table(self, db_name, table_name, offset=0, row_count=100):
		"""
		테이블의 자료중 원하는 갯수만 읽어오는 것

		:param table_name: 테이블 이름
		:param offset:
		:param row_count:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		self.cursor.execute(("select * from %s LIMIT %s, %s;") % (table_name, str(offset), str(row_count)))
		result = self.cursor.fetchall()
		return result

	def insert_df1_at_df2(self, df_obj_1, df_obj_2):
		"""
		df_obj_1의 자료에 df_obj_2를 맨끝에 추가하는것

		:param df_obj_1:
		:param df_obj_2:
		:return:
		"""
		df_obj_1 = pd.concat([df_obj_1, df_obj_2])
		return df_obj_1

	def insert_value_in_dicdb_at_nth_depth(self, i_dic, i_depth, i_key, i_value, current_depth=1):
		"""
		i_depth-1 이 있는것중에서 값이 없는 의 모든 값을 새로 만드는것

		:param i_dic:
		:param i_depth:
		:param i_key:
		:param i_value:
		:param current_depth:
		:return:
		"""
		if current_depth == i_depth + 1:
			if not i_key in list(i_dic.keys()):
				i_dic[i_key] = i_value
		else:
			for key, value in i_dic.items():
				if isinstance(value, dict):
					self.insert_value_in_dicdb_at_nth_depth(value, i_depth, i_key, i_value, current_depth + 1)

	def insert_value_in_dicdb_at_nth_depth_with_auto(self, main_dic, i_depth_list, i_key, i_value):
		"""
		i_depth-1 이 있는것중에서 값이 없다면, 그것까지 가는 경로들을 새로 만들어서 마지막에 값을 넣는것
		키값을 1_1, 2_2이런형태로 만들어서 관리하는것

		이것은 reurn값은 최종값이 나타나므로, 그냥 그대로 i_dic을 불러서 사용하여야 합니다

		:param main_dic:
		:param i_depth_list:
		:param i_key:
		:param i_value:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				if not checked_key in list(i_dic.keys()):
					i_dic[checked_key] = [None, {}]
				i_dic = i_dic[checked_key][1]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_key)
		if not checked_key1 in list(i_dic.keys()):
			if type(i_value) != type([]):
				i_value = [i_value, {}]
			i_dic[checked_key1] = i_value

	def insert_value_in_dicdb_at_nth_depth_with_auto_1(self, main_dic, i_depth_list, i_key, i_value):
		"""
		i_depth-1 이 있는것중에서 값이 없다면, 그것까지 가는 경로들을 새로 만들어서 마지막에 값을 넣는것
		키값을 1_1, 2_2이런형태로 만들어서 관리하는것

		이것은 reurn값은 최종값이 나타나므로, 그냥 그대로 i_dic을 불러서 사용하여야 합니다

		:param main_dic:
		:param i_depth_list:
		:param i_key:
		:param i_value:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				if not checked_key in list(i_dic.keys()):
					i_dic[checked_key] = {}
				i_dic = i_dic[checked_key]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_key)
		if not checked_key1 in list(i_dic.keys()):
			i_dic[checked_key1] = i_value

	def insert_value_in_dicdb_with_key_list(self, main_dic, input_key_list, value):
		"""
		사전으로 database를 만든자료에서, key로 찾아가서 마지막에 값을 넣는것

		:param main_dic:
		:param input_key_list:
		:param value:
		:return:
		"""
		current_level = main_dic
		for key in input_key_list[:-1]:
			if key not in current_level:
				current_level[key] = {}
			current_level = current_level[key]
		# 마지막 키에 값을 삽입
		last_key = input_key_list[-1]
		current_level[last_key] = value
		return main_dic

	def insert_y_line_in_listdb(self, input_listdb, input_y_name, input_yline_data):
		"""
		맨끝에, 리스트형태의 자료를 세로열을 하나 추가하는 것

		:param input_listdb:
		:param input_y_name: 세로열의 이름
		:param input_yline_data: 세로열을 위한 자료
		:return:
		"""
		input_listdb[0].append(input_y_name)
		input_listdb[1].append(input_yline_data)
		return input_listdb

	def insert_y_line_in_listdb_by_no(self, input_list_2d, input_no, yline_title="", yline_type=""):
		"""
		n번째 y라인을 추가하는 것입니다

		:param input_list_2d: 기본이되는 listdb
		:param input_no:
		:param yline_title: 새로들어갈 y라인의 컬럼명
		:param yline_type: 새로운 컬럼의 type
		:return:
		"""
		if not yline_type:
			yline_type = "any"
		input_list_2d[0].insert(input_no, [yline_title, yline_type])
		for index in range(1, len(input_list_2d)):
			input_list_2d[index].insert(input_no, None)
		return input_list_2d

	def insert_y_line_in_listdb_with_index_by_title_list(self, input_listdb, input_y_name, input_yline_data, input_index):
		"""
		index번호 위치에, 리스트형태의 자료를 세로열을 하나 추가하는 것

		:param input_listdb:
		:param input_y_name:
		:param input_yline_data:
		:param input_index:
		:return:
		"""
		input_listdb[0].insert(input_index, input_y_name)
		input_listdb[1].insert(input_index, input_yline_data)
		return input_listdb

	def insert_y_line_in_sqlite_memory_db_by_title_list(self, table_name, col_data_list_s):
		"""
		기존의 테이블의 컬럼이름들을 갖고온다
		memory db에 새로운 컬럼을 넣는다

		:param table_name: 테이블 이름
		:param col_data_list_s:
		:return:
		"""

		all_exist_y_name = self.read_all_title_list_in_sqlite(table_name)

		for one_list in col_data_list_s:
			if type(one_list) == type([]):
				y_name = self.check_y_title(one_list[0])
				col_type = one_list[1]
			else:
				y_name = self.check_y_title(one_list)
				col_type = "text"
			if not y_name in all_exist_y_name:
				self.cursor.execute("alter table %s add column '%s' '%s'" % (table_name, y_name, col_type))

	def insert_y_line_in_sqlite_table_by_title_list(self, db_name, table_name, col_data_list_s):
		"""
		(여러줄) 새로운 새로 컬럼을 만든다
		col_data_list_s : [["이름1","int"],["이름2","text"]]
		["이름2",""] => ["이름2","text"]
		1차원리스트가 오면, 전부 text로 만든다

		:param table_name: 테이블 이름
		:param col_data_list_s:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		for one_list in col_data_list_s:
			if type(one_list) == type([]):
				y_name = self.check_y_title(one_list[0])
				col_type = one_list[1]
			else:
				y_name = self.check_y_title(one_list)
				col_type = "text"
			self.cursor.execute("alter table %s add column '%s' '%s'" % (table_name, y_name, col_type))

	def insert_y_title_in_df(self, input_df, input_data):
		"""
		여러가지 형식으로 값을 넣어도 컬럼을 추가하는 방법입니다
		input_df.rename(columns={0: 'TEST', 1: 'ODI', 2: 'T20'}, inplace=True)
		df = df.DataFrame(data, columns=list_1d)

		:param input_df: dataframe객체
		:param input_data:
		:return:
		"""
		checked_changed_data = input_data
		if type(input_data) == type({}):
			# {0: 'TEST', 1: 'ODI', 2: 'T20'}
			checked_changed_data = input_data
		elif type(input_data[0]) == type([]) and len(input_data) == 1:
			# 이자료를 [["기존", "바꿀이름"], ["b", "bb"], ["c", "cc"]]
			checked_changed_data = {}
			for one in input_data:
				checked_changed_data[one[0]] = one[1]
		elif type(input_data[0]) == type([]) and len(input_data) == 2:
			# 이자료를 [["기존1", "기존2", "기존3", "기존3"], ["바꿀이름1", "바꿀이름2", "바꿀이름3", "바꿀이름3"]]
			checked_changed_data = {}
			for index, one in enumerate(input_data):
				checked_changed_data[input_data[index]] = input_data[index]
		elif type(input_data[0]) != type([]) and type(input_data) == type([]):
			# 이자료를 ["바꿀이름1", "바꿀이름2", "바꿀이름3", "바꿀이름3"]
			checked_changed_data = {}
			for index, one in enumerate(input_data):
				checked_changed_data[index] = input_data[index]
		input_df.rename(columns=checked_changed_data, inplace=True)
		return input_df

	def insert_yy_line_in_sqlite_table(self, db_name, table_name, col_data_list_s):
		"""
		(여러줄) 새로운 새로 컬럼을 만든다
		col_data_list_s : [["이름1","int"],["이름2","text"]]
		["이름2",""] => ["이름2","text"]
		1차원리스트가 오면, 전부 text로 만든다

		:param table_name: 테이블 이름
		:param col_data_list_s:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		for one_list in col_data_list_s:
			if type(one_list) == type([]):
				y_name = self.check_y_title(one_list[0])
				col_type = one_list[1]
			else:
				y_name = self.check_y_title(one_list)
				col_type = "text"
			self.cursor.execute("alter table %s add column '%s' '%s'" % (table_name, y_name, col_type))

	def is_y_title_list(self, input_list):
		"""
		입력으로 들어온 1 차원 리스트자료가 컬럼이름으로 사용되는것인지 아닌지 확인하는것

		:param input_list:
		:return:
		"""
		result = 1
		result_empty = 0
		result_date_int = 0
		for one_value in input_list:
			if one_value == None or one_value == "":
				result_empty = result_empty + 1
			if type(one_value) == type(1):
				result_date_int = result_date_int + 1
			if result_empty > 0 or result_date_int > 0:
				result = 0
		return result

	def make_2d_sample_data_in_excel(self):
		"""
		샘플용자료를 만드는 것

		:return:
		"""
		y_title_list = []
		x_len = 10
		y_len = 12

		self.excelx.new_sheet()
		for index in range(1, y_len + 1):
			y_title_list.append("title_" + str(index))

		self.excelx.write_list_1d_from_cell("", [1, 2], y_title_list)
		for no1 in range(1, x_len + 1):
			for no2 in range(1, y_len + 1):
				self.excelx.write_value_in_cell("", [no1 + 1, no2 + 1], no1 * 10 + no2)

		x_title_list = []
		for index in range(1, x_len + 1):
			x_title_list.append("줄_" + str(index))
		self.excelx.write_list_1d_from_cell_as_yline("", [2, 1], x_title_list)

	def make_cursor_for_sqlite_db(self, db_name=""):
		"""
		커서를 만드는 것

		:param db_name:
		:return:
		"""
		self.check_db_for_sqlite(db_name)

	def make_db_for_sqlite(self, db_name=""):
		"""
		(새로운 db 만들기) 새로운 데이터베이스를 만든다
		db_name이 이미 있으면 연결되고, 없으면 새로 만듦
		입력형태 : 이름

		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

	def make_df_by_basic_style(self, dic_list_1d, column_list, index_list):
		"""
		새로운 dataframe을 기본 형태로 만드는 것

		:param dic_list_1d:
		:param column_list:
		:param index_list:
		:return:
		"""
		df_obj = pd.DataFrame(dic_list_1d, columns=column_list, index=index_list)
		return df_obj

	def make_dicdb_as_2d(self, i_dic, input_key_1, input_key_2, input_value_2):
		"""
		사전에 2차원에 값을 넣는데，1차원의 사전이 없으면 만든다
		2 차원자료를 만드는것
		dicdb : 사전형식으로 만들어진 database핸들을 목적으로 만든 자료형태

		:param i_dic:
		:param input_key_1:
		:param input_key_2:
		:param input_value_2:
		:return:
		"""
		if type(i_dic[input_key_1]) != type({}):
			i_dic[input_key_1] = {}
		i_dic[input_key_1][input_key_2] = input_value_2
		return i_dic

	def make_listdb_as_simple(self, line_len, y_len):
		"""
		단순하게 아래와 같은 형태로 만든다
		[[None, None, None, None], [None, None, None, None], [None, None, None, None]]

		:param line_len:
		:param y_len:
		:return:
		"""
		result = []
		for index2 in range(line_len):
			data_one_line = []
			for index in range(y_len):
				data_one_line.append(None)
			result.append(data_one_line)
		return result

	def make_listdb_with_data_type(self, line_len, y_len, title_list=[], type_list=[]):
		"""
		list_2d = [
		["index", "int"],["제목1", "any"],["제목2", "text"],["제목3", "text"],["제목4", "text"],["제목5", "text"],["제목6", "text"],
		[1, None, None, None, None, None, None],
		[1, None, None, None, None, None, None],
		]

		:param line_len: 총 라인수
		:param y_len: 컬럼수
		:param title_list: 제목으로 사용할 부분이 잇을때 사용함
		:param type_list: 각 컬럼에 들어가는 자료형을 위한것
		:return:
		"""
		result = []
		first_line = []

		# 제목에 대한 부분을 만드는 것
		if not title_list:
			title_list = []
			for index in range(y_len):
				title_list.append("제목_" + str(index + 1))
		elif len(title_list) < y_len:
			for index in range(y_len - len(title_list)):
				title_list.append("")

		# 자료형에 대한 부분을 만드는 것
		if not type_list:
			type_list = []
			for one in range(y_len):
				type_list.append("any")
		elif len(type_list) < y_len:
			for index in range(y_len - len(type_list)):
				type_list.append("any")
		first_line.append(["index", "int"])

		# 첫번째 줄을 만드는 것
		for index in range(y_len):
			first_line.append([title_list[index], type_list[index]])
		result.append(first_line)

		# 원하는 자료의 갯수를 None으로 만드는 것
		for index2 in range(line_len):
			data_one_line = [index2 + 1]
			for index in range(y_len):
				data_one_line.append(None)
			result.append(data_one_line)
		return result

	def make_listdb_with_l2d(self, input_l2d):
		"""
		l2d자료로 알아서 listdb를 만드는 것

		:param input_l2d:
		:return:
		"""
		result = []
		line_len = len(input_l2d)
		y_len = self.utilx.get_max_len_for_list_2d(input_l2d)
		title_list = []
		type_list = []
		for no in range(1, y_len + 1):
			title_list.append("title" + str(no))
			type_list.append("any")

		first_line = []
		first_line.append(["index", "int"])

		# 첫번째 줄을 만드는 것
		for index in range(y_len):
			first_line.append([title_list[index], type_list[index]])
		result.append(first_line)

		# 원하는 자료의 갯수를 None으로 만드는 것
		for index2 in range(line_len):
			data_one_line = input_l2d[index2]
			if len(data_one_line) < y_len:
				for index in range(y_len - len(data_one_line)):
					data_one_line.append(None)
			data_one_line.insert(0, index2 + 1)
			result.append(data_one_line)
		return result

	def make_sql_for_insert_by_y_names(self, table_name, col_list):
		"""
		(sql구문 만들기) 컬럼이름을 추가하기 위하여 sql구문 만들기

		:param table_name: 테이블 이름
		:param col_list: y컬럼 이름들
		:return:
		"""
		sql_columns = self.utilx.change_list_1d_to_text_with_chain_word(col_list, ", ")
		sql_values = "?," * len(col_list)
		result = "insert into %s (%s) values (%s)" % (table_name, sql_columns, sql_values[:-1])
		return result

	def make_sql_for_new_column_with_title_list(self, table_name, col_list):
		"""
		컬럼이름으로 새로운 sql을 만드는 것

		:param table_name:
		:param col_list:
		:return:
		"""
		result = self.make_sql_for_insert_by_y_names(table_name, col_list)
		return result

	def make_sql_for_new_table_by_title_list(self, table_name, column_data_list):
		"""
		(새로운 테이블 만들기) 어떤 형태의 자료가 입력이 되어도 테이블을 만드는 sql을 만드는 것
		입력형태 1 : 테이블이름, [['번호1',"text"], ['번호2',"text"],['번호3',"text"],['번호4',"text"]]
		입력형태 2 : 테이블이름, ['번호1','번호2','번호3','번호4']
		입력형태 3 : 테이블이름, [['번호1',"text"], '번호2','번호3','번호4']

		:param table_name:
		:param column_data_list:
		:return:
		"""
		sql_1 = "CREATE TABLE IF NOT EXISTS {}".format(table_name)
		sql_2 = sql_1 + " ("
		for one_list in column_data_list:
			if type(one_list) == type([]):
				if len(one_list) == 2:
					y_name = one_list[0]
					col_type = one_list[1]
				elif len(one_list) == 1:
					y_name = one_list[0]
					col_type = "text"
			elif type(one_list) == type("string"):
				y_name = one_list
				col_type = "text"
			sql_2 = sql_2 + "{} {}, ".format(y_name, col_type)
		sql_2 = sql_2[:-2] + ")"
		return sql_2

	def make_sql_from_dic_data(self, table_name, input_dic):
		"""
		(sql구문 만들기) 사전형의 자료를 기준으로 sql구문 만들기

		:param table_name: 테이블 이름
		:param input_dic: 사전형 자료
		:return:
		"""

		sql_columns = ""
		sql_values = ""
		for one_key in input_dic.keys():
			value = input_dic[one_key]
			sql_columns = sql_columns + str(one_key) + ", "
			if value == None:
				sql_values = sql_values + str(value) + ", "
			elif type(value) == type(123) or type(value) == type(123.4):
				sql_values = sql_values + str(value) + ", "
			else:
				sql_values = sql_values + "'" + str(value) + "', "
		result = "insert into %s (%s) values (%s)" % (table_name, sql_columns[:-2], sql_values[:-2])
		return result

	def make_sqlite_memory_db(self):
		"""
		(새로운 메모리 db만들기)
		self.cursor.execute("CREATE TABLE " + self.table_name + " (auto_no integer primary key AUTOINCREMENT)")
		memory에 생성하는 것은 바로 connection 이 만들어 진다

		:return:
		"""
		self.check_db_for_sqlite(":memory:")

	def make_sqlite_memory_db_table(self, table_name):
		"""
		(새로운 테이블 만들기) 메모리db에 새로운 테이블 만들기

		:param table_name: 테이블 이름
		:return:
		"""
		self.cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + "(number integer)")

		all_table_name = []
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
		sql_results = self.cursor.fetchall()
		for one in sql_results:
			all_table_name.append(one[0])

	def make_sqlite_table(self, db_name, table_name):
		"""
		(새로운 테이블 만들기) database는 먼저 선택해야 한다
		새로운 테이블을 만든다
		입력형태 : 테이블이름

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		# 현재 db안의 테이블에 같은 이름이 없는지 확인 하는 것
		tables = []
		self.cursor.execute("select name from sqlite_master where type = 'table'; ")
		table_list = self.cursor.fetchall()
		all_table_name = []
		for one in table_list:
			all_table_name.append(one[0])

		print(all_table_name)
		if not table_name in all_table_name:
			self.cursor.execute("CREATE TABLE " + table_name + " (Item text)")
		else:
			print("같은 DB에 같은 Table이름이 있읍니다. 확인 바랍니다")

	def make_sqlite_table_with_title_list(self, db_name, table_name, column_data_list):
		"""
		(새로운 테이블 만들기) 어떤 형태의 자료가 입력이 되어도 테이블을 만드는 sql을 만드는 것이다
		입력형태 1 : 테이블이름, [['번호1',"text"], ['번호2',"text"],['번호3',"text"],['번호4',"text"]]
		입력형태 2 : 테이블이름, ['번호1','번호2','번호3','번호4']
		입력형태 3 : 테이블이름, [['번호1',"text"], '번호2','번호3','번호4']

		:param table_name: 테이블 이름
		:param column_data_list:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		sql_2 = self.make_sql_for_new_column_with_title_list(table_name, column_data_list)
		self.cursor.execute(sql_2)
		return sql_2

	def make_table_for_memory_db_with_title_list(self, table_name, title_l1d):
		text1 = " VARIANT,".join(title_l1d)
		self.cursor.execute(f"CREATE TABLE {table_name} ({text1})")

	def make_table_with_title_list_in_sqlite_memory_db(self, table_name, column_data_list):
		sql_columns = self.utilx.change_list_1d_to_text_with_chain_word(column_data_list, "VARIANT, ")
		sql_columns = sql_columns + "VARIANT"
		sql_2 = f"CREATE TABLE {table_name}({sql_columns})"
		self.cursor.execute(sql_2)
		return sql_2

	def minus_dic1_to_dic2(self, dic1, dic2):
		"""
		같은 키가 있으면 삭제하는것

		:param dic1:
		:param dic2:
		:return:
		"""
		for one_key in dic2.keys:
			del dic1[one_key]
		return dic1

	def minus_list1_to_list2(self, list1, list2):
		"""
		같은 키가 있으면 삭제하는것

		:param list1:
		:param list2:
		:return:
		"""
		result = []
		for one_value in list2:
			if not one_value in list1:
				result.append(one_value)
		return result

	def minus_set1_to_set2(self, set1, set2):
		"""
		두개의 set자료에서 같은자료만 삭제하는 것
		빼기기능이다

		:param set1:
		:param set2:
		:return:
		"""
		result = set1 - set2
		return result

	def plus_dic1_to_dic2(self, dic1, dic2):
		"""
		두개의 사전자료를 합치는 것

		:param dic1:
		:param dic2:
		:return:
		"""
		result = self.update_dic1_to_dic2(dic1, dic2)
		return result

	def plus_list1_to_list2(self, list1, list2):
		"""
		두개의 리스트자료를 합치는 것

		:param list1:
		:param list2:
		:return:
		"""

		list1.extend(list2)
		return list1

	def plus_set1_to_set2(self, set1, set2):
		"""
		두개의 set자료를 합치는 것

		:param set1:
		:param set2:
		:return:
		"""
		set1.update(set2)
		return set1

	def print_2d(self, *input_list):
		"""
		2차원 리스트자료를 한줄씩 프린틓주는 것

		:param input_list:
		:return:
		"""

		for input_2d in input_list:
			if type(input_2d) == type([]):
				print("[")
				for one in input_2d:
					print(one, ",")
				print("]")
			elif type(input_2d) == type(()):
				print("(")
				for one in input_2d:
					print(one, ",")
				print(")")
			else:
				print(input_2d)

	def read_all_table_name_in_sqlite(self, db_name=""):
		"""
		대상  : sqlite
		(모든 테이블 이름들) 해당하는 테이의 컬럼구조를 갖고온다
		입력형태 : 데이터베이스 이름
		출력형태 : 테이블이름들

		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
		result = []
		for temp_2 in self.cursor.fetchall():
			result.append(temp_2[0])
		return result

	def read_all_title_list_in_sqlite(self, table_name):
		"""
		(모든 컬럼 이름) 기존의 테이블의 컬럼이름들을 갖고온다

		:param table_name: 테이블 이름
		:return:
		"""
		self.cursor.execute("PRAGMA table_info('%s')" % table_name)
		sql_result = self.cursor.fetchall()
		all_exist_y_name = []
		for one_list in sql_result:
			all_exist_y_name.append(one_list[1])
		return all_exist_y_name

	def read_all_title_list_in_sqlite_memory_db(self, table_name):
		"""
		대상  : sqlite_memory_db
		(모든 컬럼 이름) 모든 컬럼의 이름을 갖고오는 것, 메모리 db

		:param table_name: 테이블 이름
		:return:
		"""
		self.cursor.execute("PRAGMA table_info('%s')" % table_name)
		sql_result = self.cursor.fetchall()
		result = []
		for one_list in sql_result:
			result.append(one_list[1])
		return result

	def read_df_by_name(self, df_obj, x, y):
		"""
		열이나 행의 이름으로 pandas의 dataframe의 일부를 불러오는 것이다
		이것은 리스트를 기본으로 사용한다
		list_x=["가"~"다"] ===> "가"~"다"열
		list_x=["가","나","다","4"] ===> 가,나,다, 4 열
		x=""또는 "all" ===> 전부
		"""

		temp = []
		for one in [x, y]:
			if ":" in one[0]:
				changed_one = one[0]
			elif "~" in one[0]:
				ed_one = one[0].split("~")
				changed_one = "'" + str(ed_one[0]) + "'" + ":" + "'" + str(ed_one[1]) + "'"

			elif "all" in one[0]:
				changed_one = one[0].replace("all", ":")
			else:
				changed_one = one
			temp.append(changed_one)
		# 이것중에 self를 사용하지 않으면 오류가 발생한다
		print(temp)
		exec("self.result = df_obj.loc[{}, {}]".format(temp[0], temp[1]))
		return self.result

	def read_df_by_no(self, df_obj, x, y):
		"""
		dataframe객체를 x,y번호를 기준으로 읽어오는 것

		:param df_obj:
		:param x:
		:param y:
		:return:
		"""
		example = """
			숫자번호로 pandas의 dataframe의 일부를 불러오는 것
			단, 모든것을 문자로 넣어주어야 한다
			x=["1:2", "1~2"] ===> 1, 2열
			x=["1,2,3,4"] ===> 1,2,3,4열
			x=[1,2,3,4]  ===> 1,2,3,4열
			x=""또는 "all" ===> 전부
			"""

		self.manual["df_read_byno"] = {
			"분류1": "pandas, dataframe",
			"설명": "pandas의 dataframe의 자료의 일부를 쉽게 갖고오도록 만든것",
			"입력요소": "df_obj, x, y",
			"기타설명": example
		}
		x_list = self.check_df_range(x)
		y_list = self.check_df_range(y)
		exec("self.result = df_obj.iloc[{}, {}]".format(x_list, y_list))
		return self.result

	def read_df_by_xy(self, df_obj, xy=[0, 0]):
		"""
		위치를 기준으로 값을 읽어오는 것이다
		숫자를 넣으면 된다

		:param df_obj:
		:param xy:
		:return:
		"""
		result = df_obj.iat[int(xy[0]), int(xy[1])]
		return result

	def read_title_in_df_by_iy(self, input_df, y_no=""):
		"""
		컬럼의 y의 컬럼 제목을 읽어오는 것이다

		:param input_df: dataframe객체
		:param y_no:
		:return:
		"""
		result = input_df.columns
		if y_no != "":
			result = result[y_no]
		return result

	def read_value_in_df_by_name(self, input_df, x, y):
		"""
		(dataframe의 1개의 값 읽어오기)
		열이나 행의 이름으로 pandas의 dataframe의 일부를 불러오는 것이다
		이것은 리스트를 기본으로 사용한다
		list_x=["가"~"다"] ===> "가"~"다"열
		list_x=["가","나","다","4"] ===> 가,나,다, 4 열
		x=""또는 "all" ===> 전부

		:param input_df: dataframe객체
		:param x:
		:param y:
		:return:
		"""

		temp = []
		for one in [x, y]:
			if ":" in one[0]:
				changed_one = one[0]
			elif "~" in one[0]:
				ed_one = one[0].split("~")
				changed_one = "'" + str(int(ed_one[0]) - 1) + "'" + ":" + "'" + str(ed_one[1]) + "'"
			elif "all" in one[0]:
				changed_one = "[:]"
			else:
				changed_one = one
			temp.append(changed_one)
		# 이것중에 self를 사용하지 않으면 오류가 발생한다
		exec("self.result = input_df.loc[{}, {}]".format(temp[0], temp[1]))
		return self.result

	def read_value_in_df_by_no(self, input_df, x, y):
		"""
		숫자번호로 pandas의 dataframe의 일부를 불러오는 것
		단, 모든것을 문자로 넣어주어야 한다
		x=["1:2", "1~2"] ===> 1, 2열
		x=["1,2,3,4"] ===> 1,2,3,4열
		x=[1,2,3,4]  ===> 1,2,3,4열
		x=""또는 "all" ===> 전부
		"""

		x_list = self.check_df_range(x)
		y_list = self.check_df_range(y)
		exec("self.result = input_df.iloc[{}, {}]".format(x_list, y_list))
		return self.result

	def read_value_in_df_by_xx(self, input_df, x):
		"""
		x의 라인들을 읽어온다

		:param input_df: dataframe객체
		:param x:
		:return:
		"""

		x_list = self.check_ix_in_df(input_df, x)
		exec("self.result = input_df.loc[{}, {}]".format(x_list, ":"))
		return self.result

	def read_value_in_df_by_xy(self, input_df, xy=[0, 0]):
		"""
		(dataframe의 1개의 값 읽어오기)
		위치를 기준으로 값을 읽어오는 것이다
		숫자를 넣으면 된다

		:param input_df: dataframe객체
		:param xy:
		:return:
		"""
		result = input_df.iat[int(xy[0]), int(xy[1])]
		return result

	def read_value_in_df_by_xyxy(self, input_df, xyxy):
		"""
		4각 영역의 번호위치의 값을 읽어오기

		:param input_df: dataframe객체
		:param xyxy:
		:return:
		"""

		x11, y11, x22, y22 = xyxy

		x1 = min(x11, x22)
		x2 = max(x11, x22)
		y1 = min(y11, y22)
		y2 = max(y11, y22)

		x = str(x1) + ":" + str(x2)
		if x == "0:0":    x = ":"
		y = str(y1) + ":" + str(y2)
		if y == "0:0":    y = ":"

		x_list = self.check_ix_in_df(input_df, x)
		y_list = self.check_iy_in_df(input_df, y)
		# print(x_list, y_list)
		exec("self.result = input_df.loc[{}, {}]".format(x_list, y_list))
		return self.result

	def read_value_in_df_by_yy(self, input_df, y):
		"""
		대상  : dataframe
		여러줄의 y라인들의 값을 읽어온다

		:param input_df: dataframe객체
		:param y:
		:return:
		"""
		y_list = self.check_iy_in_df(input_df, y)
		exec("self.result = input_df.loc[{}, {}]".format(":", y_list))
		return self.result

	def read_value_in_dicdb(self, main_dic, i_depth_list):
		"""
		사전 db에서 n번째 이하의 값을 읽어오는 것

		:param main_dic:
		:param i_depth_list:
		:return:
		"""
		result = self.read_value_in_dicdb_with_below(main_dic, i_depth_list)
		return result

	def read_value_in_dicdb_with_below(self, main_dic, i_depth_list):
		"""
		대상  : dicdb (사전형으로 된 database)
		n번째 깊이 이하의 모든 자료를 읽어오는 것

		:param main_dic:
		:param i_depth_list:
		:return:
		"""
		i_dic = main_dic[0]
		if len(i_depth_list) > 1:
			for index, one_value in enumerate(i_depth_list[:-1]):
				checked_key = str(index + 1) + "_" + str(one_value)
				i_dic = i_dic[checked_key][1]

		checked_key1 = str(len(i_depth_list)) + "_" + str(i_depth_list[-1])
		result = i_dic[checked_key1]
		return result

	def read_value_in_sqlite(self, db_name, table_name):
		"""
		대상  : sqlite
		(테이블의 모든 값) 테이블의 모든 자료를 읽어온다
		입력형태 : 테이블 이름

		:param table_name: 테이블 이름
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		self.cursor.execute(("select * from {}").format(table_name))
		result = self.cursor.fetchall()
		return result

	def read_value_in_sqlite_as_dic_style(self, table_name):
		"""
		대상  : sqlite
		(테이블의 모든 값) 사전형식으로 돌려줌

		:param table_name: 테이블 이름
		:return:
		"""
		sql = f"select * from {table_name}"
		self.cursor.execute(sql)
		names = [description[0] for description in self.cursor.description]

		result = []
		all_lines = self.cursor.fetchall()
		for one_line in all_lines:
			temp = {}
			for index, value in enumerate(one_line):
				temp[names[index]] = value
			result.append(temp)
		return result

	def read_value_in_sqlite_as_dic_style_except_none(self, table_name):
		"""
		대상  : sqlite
		(테이블의 모든 값) 사전형식으로 돌려줌, 단 None값은 제외한다

		:param table_name: 테이블 이름
		:return:
		"""
		sql = f"select * from {table_name}"
		self.cursor.execute(sql)
		names = [description[0] for description in self.cursor.description]
		result = {}
		all_lines = self.cursor.fetchall()
		for one_line in all_lines:
			temp = {}
			for index, value in enumerate(one_line):
				if value:
					temp[names[index]] = value
			if temp["x"] in result.keys():
				result[temp["x"]][temp["y"]] = temp
			else:
				result[temp["x"]] = {}
				result[temp["x"]][temp["y"]] = temp
		return result

	def read_value_in_sqlite_by_title_list(self, db_name, y_title_s="", condition="all"):
		"""
		대상  : sqlite
		컬럼이름으로 테이블 값을 갖고오기, 문자는 컬럼이름으로, 숫자는 몇번째인것으로...

		:param y_title_s:
		:param condition:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		if y_title_s == "":
			sql_columns = "*"
		else:
			sql_columns = self.utilx.change_list_1d_to_text_with_chain_word(y_title_s, ", ")
		if condition == "all":
			lim_no = 100
		else:
			lim_no = condition
		limit_text = "limit {}".format(lim_no)
		sql = "SELECT {} FROM {} ORDER BY auto_no {}".format(sql_columns, self.table_name, limit_text)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		return result

	def read_value_in_sqlite_memory_db_by_xy(self, table_name, x_no, y_no):
		"""
		대상  : sqlite_memory_db
		(한개의 값)메모리db의 x번째, y번째의 값

		:param table_name: 테이블 이름
		:param x_no:
		:param y_no:
		:return:
		"""
		sql = f"select * from {table_name} where x = {x_no} and y = {y_no}"
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		return result

	def read_value_in_sqlite_memory_db_with_y_title_by_xy(self, table_name, x_no, y_no):
		"""
		대상  : sqlite_memory_db
		(한개의 값) 메모리db의 x번째, y번째의 값과 컬럼이름

		:param table_name: 테이블 이름
		:param x_no:
		:param y_no:
		:return:
		"""
		sql = f"select * from {table_name} where x = {x_no} and y = {y_no}"
		self.cursor.execute(sql)
		result = {}
		names = [description[0] for description in self.cursor.description]
		rows = self.cursor.fetchall()
		if rows == []:
			result = {}
		else:
			for row in rows:
				for name, val in zip(names, row):
					result[name] = val
		return result

	def read_value_in_sqlite_memory_db_with_y_title_by_xy_except_none_data(self, table_name, x_no, y_no):
		"""
		대상  : sqlite_memory_db
		메모리db의 x번째, y번째의 값과 컬럼이름, 단 None값은 제외한다

		:param table_name: 테이블 이름
		:param x_no:
		:param y_no:
		:return:
		"""
		sql = f"select * from {table_name} where x = {x_no} and y = {y_no}"
		self.cursor.execute(sql)
		result = {}
		names = [description[0] for description in self.cursor.description]
		rows = self.cursor.fetchall()
		for row in rows:
			for name, val in zip(names, row):
				if val != None:
					result[name] = val
		return result

	def read_x_title_in_df_by_iy(self, input_df, x_no=""):
		"""
		컬럼의 이름을 읽어오기
		x의 index를 기준으로 읽어오기

		:param input_df: dataframe객체
		:param x_no:
		:return:
		"""
		result = input_df.index
		if x_no != "":
			result = result[x_no]
		return result

	def read_xxyy_line_in_df(self, input_df, x, y=""):
		"""
		pandas의 dataframe의 값 읽어오기

		숫자번호로 pandas의 dataframe의 일부를 불러오는 것
		단, 모든것을 문자로 넣어주어야 한다
		x=["1:2", "1~2"] ===> 1, 2열
		x=["1,2,3,4"] ===> 1,2,3,4열
		x=[1,2,3,4]  ===> 1,2,3,4열
		x=""또는 "all" ===> 전부

		:param input_df: dataframe객체
		:param x:
		:param y:
		:return:
		"""

		x_list = self.check_ix_in_df(input_df, x)
		y_list = self.check_iy_in_df(input_df, y)
		exec("self.result = input_df.loc[{}, {}]".format(x_list, y_list))
		return self.result

	def reset_index_no_for_listdb(self, input_listdb):
		"""
		맨앞의 index번호를 새롭게 다시 바꾸는 것

		:param input_listdb:
		:return:
		"""

		for no in range(1, len(input_listdb)):
			input_listdb[no][0] = no
		return input_listdb

	def run_sql_for_sqlite(self, db_name, sql):
		"""
		sqlite의 sql문을 실행하는 것이다

		fetchall는
		첫번째 : (1, '이름1', 1, '값1')
		두번째 : (2, '이름2', 2, '값2')

		:param sql:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		self.con.commit()
		return result

	def run_sql_for_sqlite_memory_db(self, sql):
		"""
		sqlite_memory_db를 대상으로 sql을 실행하는것

		:param sql:
		:return:
		"""
		sql_result = self.cursor.execute(sql)
		result = self.cursor.fetchall()
		column_names = [description[0] for description in self.cursor.description]
		# print(column_names)
		result.insert(0, column_names)
		self.con.commit()
		return result

	def save_sqlite_memory_db_to_disk_db(self, db_name=""):
		"""
		sqlite_memory_db에 저장된 것을 화일로 저장하는것
		python 3.7부터는 backup이 가능

		:param db_name: 데이터베이스 이름
		:return:
		"""
		db_disk = sqlite3.connect(db_name)
		self.con.backup(db_disk)

	def set_database_for_sqlite(self, db_name=""):
		"""
		sqlite용 database를 만드는 것

		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

	def split_list_2d_as_data_x_title_y_title(self, input_list_2d, x_title_len, y_title_len):
		"""
		2줄이상의 제목이 들어갈수있을것같아, 2차원의 자료로 만들었다
		list_2d = self.utilx.check_list_2d(input_list_2d)

		:param input_list_2d:
		:param x_title_len:
		:param y_title_len:
		:return:
		"""
		x_title_list_2d = []
		y_title_list_2d = []
		data_list_2d = []

		total_y_len = len(input_list_2d[0])

		for _ in range(total_y_len - y_title_len):
			y_title_list_2d.append([])

		for list_1d in input_list_2d[y_title_len:]:
			data_list_2d.append(list_1d[x_title_len:])

		if x_title_len:
			for index, list_1d in enumerate(input_list_2d):
				if index >= y_title_len:
					x_title_list_2d.append(list_1d[:x_title_len])

		if y_title_len:
			for index, list_1d in enumerate(input_list_2d):
				if index < y_title_len:
					for index2, one in enumerate(list_1d[x_title_len:]):
						y_title_list_2d[index2].append(one)

		return [data_list_2d, x_title_list_2d, y_title_list_2d]

	def update_dic1_to_dic2(self, dic1, dic2):
		"""
		같은 것이 있으면 update

		:param dic1:
		:param dic2:
		:return:
		"""
		dic1.update(dic2)
		return dic1

	def update_set1_to_set2(self, set1, set2):
		"""
		extend 와 같은 의미이지만, 이해를 돕기위해 만들기

		:param set1:
		:param set2:
		:return:
		"""
		set1.update(set2)
		return set1

	def write_df_to_excel(self, input_df, xy=[1, 1]):
		"""
		df자료를 커럼과 값을 기준으로 나누어서 결과를 돌려주는 것이다

		:param input_df:
		:param xy:
		:return:
		"""
		col_list = input_df.columns.values.tolist()
		value_list = input_df.values.tolist()
		self.excelx.write_list_1d_from_cell_as_yline("", xy, col_list)
		self.excelx.write_value_in_range_as_speedy("", [xy[0] + 1, xy[1]], value_list)

	def write_df_to_sqlite(self, db_name, table_name, input_df):
		"""
		df자료를 sqlite에 새로운 테이블로 만들어서 넣는 것

		:param table_name: 테이블 이름
		:param input_df:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		input_df.to_sql(table_name, self.con)

	def write_dic_to_sqlite(self, db_name, table_name, input_dic):
		"""
		사전형식의 값을 sqlite에 입력하는 것

		:param table_name: 테이블 이름
		:param input_dic:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		for one_col in list(input_dic[0].keys()):
			if not one_col in self.read_all_title_list_in_sqlite(table_name, db_name):
				self.insert_yy_line_in_sqlite_table(table_name, [one_col], db_name)

		sql = self.make_sql_for_insert_by_y_names(table_name, list(input_dic[0].keys()))
		value_list = []
		for one_dic in input_dic:
			value_list.append(list(one_dic.values()))
		self.cursor.executemany(sql, value_list)

	def write_list_1d_to_sqlite(self, db_name, table_name, y_title_s, input_list_1d):
		"""
		리스트의 형태로 넘어오는것중에 y이름과 값을 분리해서 얻는 것이다

		:param table_name: 테이블 이름
		:param y_title_s:
		:param list_1d:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		sql = self.make_sql_for_insert_by_y_names(table_name, y_title_s)
		self.cursor.executemany(sql, input_list_1d)

	def write_list_2d_in_memory_db_with_title_list(self, table_name, title_l1d, list_2d):
		all_table_name = self.get_all_table_name_in_sqlite_memory_db()
		if not table_name in all_table_name:
			self.make_table_for_memory_db_with_title_list(table_name, title_l1d)
		sql_2 = self.make_sql_for_new_column_with_title_list(table_name, title_l1d)
		self.cursor.executemany(sql_2, list_2d)

	def write_list_2d_to_new_sqlite_table_by_data_only(self, db_name, table_name, input_list_2d):
		"""
		input_list_2d의 자료를 새로운 sqlite 테이블로 만드는 것

		:param db_name:
		:param table_name:
		:param input_list_2d:
		:return:
		"""
		title_list = []
		for index, one in enumerate(input_list_2d[0]):
			title_list.append("title_" + str(index + 1))
		sql_text = self.make_sql_for_new_table_by_title_list(table_name, title_list)
		self.run_sql_for_sqlite(db_name, sql_text)

	def write_value_in_df_by_xy(self, df, xy, value):
		"""
		dataframe에 xy스타일의 좌표로 값을 저장하는 것

		:param df: dataframe
		:param xy:
		:param value:
		:return:
		"""
		x_max = df.index.size
		y_max = df.columns.size
		df.iat[int(xy[0]), int(xy[1])] = value

	def write_value_in_sqlite(self, table_name, y_title_s, input_2=""):
		"""
		입력하고 싶은 값을 sqlite에 저장하는것

		:param table_name: 테이블 이름
		:param input_1:
		:param input_2:
		:return:
		"""
		list_1d_dic = self.change_any_data_to_dic(y_title_s, input_2)
		sql_columns = ""
		sql_values = ""
		for one_dic in list_1d_dic:
			for one_key in one_dic.keys():
				sql_columns = sql_columns + one_key + ", "
				sql_values = sql_values + one_dic[one_key] + ", "
			sql = "insert into %s(%s) values (%s)" % (table_name, sql_columns[:-2], sql_values[:-2])
			self.cursor.execute(sql)
		self.con.commit()

	def write_value_in_sqlite_with_data_only(self, db_name, table_name, input_list_2d):
		"""
		sqlite에 값을 추가하는 것 : 제목없이 자료만 갖고 추가를 하는것

		:param db_name:
		:param table_name:
		:param input_list_2d:
		:return:
		"""
		self.check_db_for_sqlite(db_name)

		sql_values = "?," * len(input_list_2d[0])
		sql = f"insert into {table_name} values ({sql_values[:-1]});"
		print(sql)

		for list_1d in input_list_2d:
			self.cursor.execute(sql, list_1d)

	def write_value_to_sqlite_with_title(self, db_name, table_name, y_title_s, col_value_s):
		"""
		sqlite에 값을 추가하는 것 : 제목과 값을 기준으로 추가

		:param table_name: 테이블 이름
		:param y_title_s:
		:param col_value_s:
		:param db_name: 데이터베이스 이름
		:return:
		"""
		self.check_db_for_sqlite(db_name)
		sql_columns = ""
		sql_values = ""
		for column_data in y_title_s:
			sql_columns = sql_columns + column_data + ", "
			sql_values = "?," * len(y_title_s)
		sql = "insert into %s(%s) values (%s)" % (table_name, sql_columns[:-2], sql_values[:-1])
		if type(col_value_s[0]) == type([]):
			self.cursor.executemany(sql, col_value_s)
		else:
			self.cursor.execute(sql, col_value_s)
		self.con.commit()



