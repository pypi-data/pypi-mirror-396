# -*- coding: utf-8 -*-
import re, time, calendar, arrow, datetime, random
import pywintypes
from korean_lunar_calendar import KoreanLunarCalendar

import xy_re, xy_util, xy_common  # xython 모듈


class xy_time():
	"""
	시간을 다루기 위한 모듈

	기본적으로 날짜의 변환이 필요한 경우는 utc 시간을 기준으로 변경하도록 하겠읍니다
	음력의 자료는 KoreanLunarCalendar모듈을 사용
	주의 시작은 월요일

	윈도우시간  : 1601년 1월1일을 0으로하여 계산하는 윈도우의 시간
	엑셀 시간  : 1900년부터 시작하는 밀리초단위로 계산 (밀리초를 0단위로하여 계산), 기존에 더 유명했던 로터스의 시간과 맞추기위하여 적용
	리눅스 시간 : 1970년부터 시작하는 초단위를 기준 (초를 0단위로 계산, 소숫점이 있음)

	datetime의 객체는 local time을 기준으로 만듭니다
	datetime 객체를 기준으로 하여도 된다
	datetime : 1900.1.1을 1초로 시작
	datetime class : 1년 1월1일부터 날짜를 시작, 1년은 3600*24초로 계산

	utc  : 1970년 1월 1일을 0밀리초로 계산한 것
	utc  : 1640995200.0 또는 "", 1648037614.4801838 (의미 : 2022-03-23T21  13:34.480183+09:00)
	ISO형식 : 2023-03-01T10:01:23.221000, 2023-03-01T10:01:23.221000+09:00, 2023-03-01

	text_time : 문자열 형식으로된 시간표현, 시간객체가 아닌 글자로 표현된 시간
	dic_time : 사전형식으로 된 시간표현
	dt_obj : 시간 객체

	yyyy_mm_dd : 2025-04-19 형태
	ymd_list : [년, 월, 일], [2000, 01, 01]
	hms_list : [시, 분, 초]
	date_list    : [2000, 01, 01]
	ymdhms_list : [년, 월, 일, 시, 분, 초]
	intersect : 두시간이 곂치는 부분
	update : 시간의 일부를 바꾸는것
	shift : 시간의 일부를 이동시키는것, 현재의 값을 같은 형태에서 값을 이동시키는것
	isocalendar : [year, week, weekday]
	sec_datas : sec형식을 가진 여러개의 집합
	date : 2000-01-01
	time : 시간의 여러형태로 입력을 하면, 이에 맞도록 알아서 조정한다
	dhms : 2일3시간10분30초, day-hour-minute-sec
	move : 입력값에 더하거나 빼서 다른 값으로 바꾸는것, 입력값과 출력값이 다를때 (출력값을 입력의 형태로 바꾸면 값이 다른것)
	change     : 형태를 바꾼것
	read : 입력값을 원하는 형태로 변경해서 갖고오는것
	get  : 입력값에서 원하는 형태의 값을 갖고오는것
	utc class    : 1970년 1월1일부터 날짜를 시작
	week_no_7    : 요일에대한 번호 (0~6) 0은 일요일
	yearweekno  : 1년의 주번호 (1~55)
	week_no     : yearweekno를 뜻함
	timestamp : utc시간으로 만들어 주는것
	"""

	def __init__(self):
		self.ol_common = {}
		self.varx = xy_common.xy_common().varx  # package안에서 공통적으로 사용되는 변수들
		self.lunar_calendar = KoreanLunarCalendar()  # 음력

	def calc_day_between_two_dt_obj(self, input_dt_1, input_dt_2):
		"""
		날짜의 차이

		:param input_dt_1:
		:param input_dt_2:
		:return:
		"""
		if input_dt_1 > input_dt_2:
			input_dt_2, input_dt_1 = input_dt_1, input_dt_2

		base_ymd_list = self.get_ymd_list_for_dt_obj(input_dt_1)
		day_no_for_one_month_before = self.get_last_day_for_ym_list([base_ymd_list[0], base_ymd_list[1] - 1])
		ymd_list_2 = self.get_ymd_list_for_dt_obj(input_dt_2)

		if base_ymd_list[2] - ymd_list_2[2] <= 0:
			base_ymd_list[2] = base_ymd_list[2] + day_no_for_one_month_before
			base_ymd_list[1] = base_ymd_list[1] - 1

	def calc_day_between_two_times(self, input_date1, input_date2):
		"""
		두날짜의 빼기

		:param input_date1: 일반적으로 사용하는 날짜를 나타내는 문자나 리스트
		:param input_date2: 일반적으로 사용하는 날짜를 나타내는 문자나 리스트
		:return:
		"""
		dt_obj_1 = self.change_any_text_time_to_dt_obj(input_date1)
		dt_obj_2 = self.change_any_text_time_to_dt_obj(input_date2)

		result = abs((float(dt_obj_1.timestamp()) - float(dt_obj_2.timestamp())) / (60 * 60 * 24))
		return result

	def calc_degree_for_hms(self, input_dt_obj=""):
		"""
		현재의 시간을 각도로 만드는 방법
		시분초에 대한 각도를 계산해서 주는것이며 시계를 만들때 사용할 목적으로 만든것


		:param input_dt_obj:
		:return:
		"""
		if input_dt_obj != "":
			now_dt_obj = input_dt_obj
		else:
			now_dt_obj = self.get_dt_obj_for_now()
		hour, min, sec = self.get_hms_list_for_dt_obj(now_dt_obj)
		hour, min, sec = int(hour), int(min), int(sec)

		# 시간 : 1시간은 30도의 각도임, 1분은 0.5도를 더해주어야함
		if int(hour) > 12:
			degree_hour = int(((12 - hour) / 12) * 360 + min * 0.5)
		else:
			degree_hour = int(((hour / 12) * 360) + min * 0.5)

		degree_min = int((min / 60) * 360)
		degree_sec = int((sec / 60) * 360)
		return [degree_hour, degree_min, degree_sec]

	def calc_hsm_list_between_two_hms_list(self, input_hms_1, input_hms_2):
		"""
		hms_list : [시, 분, 초]
		두 시간에 대한 차이를 hms 형태로 돌려주는 것

		:param input_hms_1: hms_list : [시, 분, 초]
		:param input_hms_2: hms_list : [시, 분, 초]
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(input_hms_1)
		sec_2 = self.change_hms_list_to_sec(input_hms_2)
		delta_sec = abs(int(sec_2 - sec_1))
		result = self.change_sec_to_hms_list(delta_sec)
		return result

	def calc_overlap_sec_between_two_time(self, input_dt2_1, input_dt2_2, input_list):
		"""
		두시간 사이에 겹치는 시간을 초로 계산하는것

		:param input_dt2_1: datetime객체
		:param input_dt2_2: datetime객체
		:param input_list:
		:return:
		"""
		result = []
		check_data = self.overlap_area_for_two_dt_range(input_dt2_1, input_dt2_2)
		for one_list in input_list:
			base_sec_start = one_list[0] * 60 * 60 + one_list[1] * 60
			base_sec_end = one_list[2] * 60 * 60 + one_list[3] * 60
			overlap_area = self.intersect_two_time_range(base_sec_start, base_sec_end, check_data[0], check_data[1])
			result.append([overlap_area, one_list[4], one_list[5], one_list[6]])
		return result

	def chang_no_to_nth_eng(self, no):
		"""
		숫자를 서수로 돌려주는 것 ---> ['1ST']

		:param no:
		:return:
		"""
		data = ['1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH', '10TH', '11TH', '12TH', '13TH', '14TH',
				'15TH', '16TH', '17TH', '18TH', '19TH', '20TH', '21ST', '22ND', '23RD', '24TH', '25TH', '26TH', '27TH',
				'28TH', '29TH', '30TH', '31ST']
		return data[no - 1]

	def change_any_text_time_to_dt_obj(self, input_time=""):
		"""
		기존의 자료를 다른 형태러 만들어 본것
		어떤 문자열의 시간이 오더라도 datetime형으로 돌려주는것
		입력값으로 datetime 객체가가 오면 에러가 난다

		:param input_time: 문자열로된 시간
		:return:
		"""
		rex = xy_re.xy_re()
		input_time = str(input_time)

		result = {}

		result["yea"] = 0
		result["mon"] = 0
		result["day"] = 0
		result["hou"] = 0
		result["min"] = 0
		result["sec"] = 0
		result["week"] = 0
		result["bellow_sec"] = 0
		result["utc_+-"] = 0
		result["utc_h"] = 0
		result["utc_m"] = 0

		# 전처리를 실시
		dt_string = (str(input_time).strip()).lower()
		dt_string = dt_string.replace("/", "-")
		dt_string = dt_string.replace("#", "-")

		ymd_sql = []

		# 아래의 자료 형태들을 인식하는 것이다
		# '2022-03-04'
		# '3/12/2018' => '3-12-2018'
		# '20220607'
		# "180919 015519"
		# 'Jun 28 2018 7:40AM',
		# 'Jun 28 2018 at 7:40AM',
		# 'September 18, 2017, 22:19:55',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017 at 4:30pm'
		# '2023-09-09 00:00:00+00:00'
		# 'Sun, 05/12/1999, 12:30PM', => 'Sun, 05-12-1999, 12:30PM',
		# '2023-03-01T10:01:23.221000+09:00'

		# +00:00 을 찾아내는것
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("[+-:1~1][숫자:2~2]:[숫자:2~2]", dt_string)
		if resql_result:
			temp = resql_result[0][0].split(":")
			result["utc_+-"] = temp[0][0]
			result["utc_h"] = temp[0][1:3]
			result["utc_m"] = temp[1]
			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("1) +00:00       의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "2022-03-04"
		# "3-12-2018"
		# "20220607"
		# "180919 015519"
		# 'Jun 28 2018 7:40AM',
		# 'Jun 28 2018 at 7:40AM',
		# 'September 18, 2017, 22:19:55',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017 at 4:30pm'
		# "2023-09-09 00:00:00"
		# 'Sun, 05-12-1999, 12:30PM',
		# '2023-03-01T10:01:23.221000'

		# 7:40AM
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql = "([숫자:1~2]):([숫자:1~2])[공백&apm:1~3]"
		resql_result = rex.search_all_by_xsql(resql, dt_string)

		ampm = ""
		if resql_result:
			result["hou"] = resql_result[0][3][0]
			result["min"] = resql_result[0][3][1]
			searched_data = resql_result[0][0]
			if "am" in searched_data:
				ampm = "am"
				searched_data = searched_data.replace("am", "")
			if "pm" in searched_data:
				ampm = "pm"
				searched_data = searched_data.replace("pm", "")

			temp = searched_data.split(":")
			result["hou"] = str(temp[0]).strip()
			result["min"] = str(temp[1]).strip()

			if ampm == "pm" and int(result["hou"]) < 12:
				result["hou"] = int(result["hou"]) + 12
			elif ampm == "pm" and int(result["hou"]) == 12:
				result["hou"] = 0

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("2) 7:40AM       의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "2022-03-04"
		# "3-12-2018"
		# "20220607"
		# "180919 015519"
		# 'Jun 28 2018',
		# 'September 18, 2017, 22:19:55',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017'
		# "2023-09-09 00:00:00"
		# 'Sun, 05-12-1999,'
		# '2023-03-01T10:01:23.221000'

		# 17:08:00
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("[숫자:2~2]:[숫자:2~2]:[숫자:2~2]", dt_string)

		if resql_result:
			temp = resql_result[0][0].split(":")
			result["hou"] = temp[0]
			result["min"] = temp[1]
			result["sec"] = temp[2]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.replace("at", "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("3) 17:08:00     의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "2022-03-04"
		# "3-12-2018"
		# "20220607"
		# "180919 015519"
		# 'Jun 28 2018',
		# 'September 18, 2017,',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017'
		# 'Sun, 05-12-1999,'
		# '2023-03-01T.221000'

		# 2022-03-04
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		if rex.search_all_by_xsql("[숫자:4~4]-[숫자:1~2]-[숫자:1~2]", dt_string):
			resql_result = rex.search_all_by_xsql("[숫자:4~4]-[숫자:1~2]-[숫자:1~2]", dt_string)

			temp = resql_result[0][0].split("-")
			result["yea"] = temp[0]
			result["mon"] = temp[1]
			result["day"] = temp[2]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("4) 2022-03-04   의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "3-12-2018"
		# "20220607"
		# "180919 015519"
		# 'Jun 28 2018',
		# 'September 18, 2017,',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017'
		# 'Sun, 05-12-1999,'
		# 'T.221000'

		# 18/09/19 => 18-09-19
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("[숫자:1~2]-[숫자:1~2]-[숫자:1~4]", dt_string)
		if resql_result:
			temp = resql_result[0][0].split("-")
			result["yea"] = temp[2]
			result["mon"] = temp[1]
			result["day"] = temp[0]

			if int(temp[0]) > 12:
				result["mon"] = temp[1]
				result["day"] = temp[0]
			elif int(temp[1]) > 12:
				result["mon"] = temp[0]
				result["day"] = temp[1]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
			# print("5) 18/09/19     의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

			# "20220607"
			# "180919 015519"
			# 'Jun 28 2018',
			# 'September 18, 2017,',
			# 'Mon, 21 March, 2015',
			# 'Tuesday , 6th September, 2017'
			# 'Sun'

			# 20220607
			dt_string = dt_string.strip()
			old_dt_string = dt_string
			resql_result = rex.search_all_by_xsql("(20|19)[숫자:6~6]", dt_string)
		if resql_result:
			result["yea"] = resql_result[0][0][0:4]
			result["mon"] = resql_result[0][0][4:6]
			result["day"] = resql_result[0][0][6:8]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()

		if old_dt_string != "":
			pass
		# print("6) 20220607     의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "180919 015519"
		# 'Jun 28 2018',
		# 'September 18, 2017,',
		# 'Mon, 21 March, 2015',
		# 'Tuesday , 6th September, 2017'
		# 'Sun'

		# Tuesday
		for one_week in self.varx["week_vs_enum"].keys():
			if one_week in dt_string:
				result["week"] = self.varx["week_vs_enum"][one_week]
				dt_string = dt_string.replace(one_week, "")
				dt_string = dt_string.strip()

		if old_dt_string != "":
			pass
		# print("7) Tuesday      의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# "180919 015519"
		# 'Jun 28 2018',
		# 'September 18, 2017,',
		# ', 21 March, 2015',
		# ', 6th September, 2017'

		# "180919 015519"
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("[숫자:6~6][공백:1~1][숫자:6~6]", dt_string)
		if resql_result:
			result["day"] = resql_result[0][0][0:2]
			result["mon"] = resql_result[0][0][2:4]
			result["yea"] = resql_result[0][0][4:6]
			result["bellow_sec"] = resql_result[0][0][:-6]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("8) 180919 015519의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# 'Jun 28 2018',
		# 'September 18, 2017,',
		# ', 21 March, 2015',
		# ', 6th September, 2017'

		# Jun 28 2018 스타일 찾기
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("([영어:3~10])[공백&,.:0~3]([숫자:1~2])[공백&,.:1~3]([숫자:1~4])", dt_string)

		if resql_result:
			result["mon"] = self.varx["month_vs_no"][resql_result[0][3][0]]
			result["day"] = resql_result[0][3][1]
			result["yea"] = resql_result[0][3][2]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("9) Jun 28 2018  의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		# ', 21 March, 2015',
		# ', 6th September, 2017'
		#	'Tuesday , 6th September, 2017 at 4:30pm'

		# 6th September, 2017 스타일 찾기
		dt_string = dt_string.strip()
		old_dt_string = dt_string
		resql_result = rex.search_all_by_xsql("[숫자:1~2][영어:0~3][공백&,:1~3][영어:3~9][공백&,:0~3][숫자:4~4]", dt_string)
		if resql_result:
			found_text = resql_result[0][0]

			bbb = rex.search_all_by_xsql("[영어:3~9]", found_text)
			for num in self.varx["no_vs_month"].keys():
				if bbb[0][0] in self.varx["no_vs_month"][num]:
					result["mon"] = num
			found_text = found_text.replace(bbb[0][0], "")

			ccc = rex.search_all_by_xsql("[숫자:4~4]", found_text)
			result["yea"] = ccc[0][0]
			found_text = found_text.replace(ccc[0][0], "")

			ddd = rex.search_all_by_xsql("[숫자:1~2]", found_text)
			result["day"] = ddd[0][0]

			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()

		resql_result = rex.search_all_by_xsql("\.[숫자:6~6]", dt_string)
		if resql_result:
			dt_string = dt_string.replace(resql_result[0][0], "")
			# .586525
			# 초단위 이하의 자료
			result["bellow_sec"] = resql_result[0][0]

		# 여태 걸린것주에 없는 4가지 숫자는 연도로 추측한다
		resql_result = rex.search_all_by_xsql("[숫자:4~4]", dt_string)
		if resql_result:
			# print(resql_result)
			result["yea"] = int(resql_result[0][0])
			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()

		# 여태 걸린것 없는 2가지 숫자는 날짜로 추측한다
		resql_result = rex.search_all_by_xsql("[숫자:2~2]", dt_string)
		if resql_result:
			result["day"] = resql_result[0][0]
			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()

		resql_result = rex.search_all_by_xsql("pm[또는]am", dt_string)
		if resql_result:
			# print(resql_result)
			if resql_result[0][0] == "pm" and int(result["hou"]) <= 12:
				result["hou"] = int(result["hou"]) + 12
			dt_string = dt_string.replace(resql_result[0][0], "")
			dt_string = dt_string.strip()
		if old_dt_string != "":
			pass
		# print("10)6th September, 2017의 형태 ====>", " 기존 => ", old_dt_string, " 변경 => ", dt_string, " 찾은것 => ",  resql_result)

		result["yea"] = int(result["yea"])
		result["mon"] = int(result["mon"])
		result["day"] = int(result["day"])
		result["hou"] = int(result["hou"])
		result["min"] = int(result["min"])
		result["sec"] = int(result["sec"])
		# print("전체 인쇄 => ", result["yea"], result["mon"], result["day"], result["hou"], result["min"], result["sec"])

		try:
			text_time = str(result["yea"]) + "-" + str(result["mon"]) + "-" + str(result["day"]) + " " + str(
				result["hou"]) + "-" + str(result["min"]) + "-" + str(result["sec"])
			# print("시간 문자 ==> ", text_time)
			if len(str(result["yea"])) == 2:
				result = datetime.datetime.strptime(text_time, "%y-%m-%d %H-%M-%S")
			elif len(str(result["yea"])) == 4:
				result = datetime.datetime.strptime(text_time, "%Y-%m-%d %H-%M-%S")
		except:
			result = "error"

		return result

	def change_anytime_to_dt_obj(self, input_time=""):
		"""
		어떤 형태의 시간관련 문자를 datetime객체로 만드는 것

		:param input_time:
		:return:
		"""
		result = self.check_input_time(input_time)
		return result

	def change_anytime_to_formatted_text_time(self, input_time, input_time_format='%Y-%m-%d'):
		"""
		입력시간을 입력된 형태로 바꾸는 것

		:param input_time_format:
		:param input_format:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		result = time.strptime(dt_obj, input_time_format)
		return result

	def change_anytime_to_utc(self, input_time=""):
		"""
		어떤 시간이라도 utc형식의 시간으로 만들어 주는 것

		:param input_time:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		result = self.change_dt_obj_to_utc(dt_obj)
		return result

	def change_anytime_to_ymd_list(self, input_time=""):
		"""
		어떤 형식의 시간이라도 [2024, 10, 01]처럼 만들어 주는 것
		문자형시간 => [년, 월, 일]

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		result = self.get_ymd_list_for_dt_obj(dt_obj)
		return result

	def change_dic_time_to_dt_obj(self, input_dic):
		"""
		사전형식의 시간을 datetime객체로 만드는 것
		dic_time : {"yea":2024, "mon" : 2, "day":24, "hou":10, "min":33,"sec":45}와 같은 형식

		:param input_dic:
		:return:
		"""
		temp = self.make_dic_time(input_dic)
		text_time = str(temp["yea"]) + "-" + str(temp["mon"]) + "-" + str(temp["day"]) + "-" + str(
			temp["hou"]) + "-" + str(temp["min"]) + "-" + str(temp["sec"])
		dt_obj = datetime.datetime.strptime(text_time, "%Y-%m-%d-%H-%M-%S")
		return dt_obj

	def change_dt_obj_as_0h_0m_0s(self, input_dt):
		"""
		가끔 이메일을 날짜의 간격으로 갖고올때, 하루의 시작시간을 0시0분0초로 바꿔야 할때 사용합니다

		:param input_dt: datetime객체
		:return:
		"""
		result = datetime.datetime(input_dt.year, input_dt.month, input_dt.day, 0, 0, 0)
		return result

	def change_dt_obj_as_23h_59m_59s(self, input_dt):
		"""
		가끔 이메일을 날짜의 간격으로 갖고올때, 하루의 끝시간인 23시 59분 59초로 바꿔야 할때 사용합니다

		:param input_dt: datetime객체
		:return:
		"""

		result = datetime.datetime(input_dt.year, input_dt.month, input_dt.day, 23, 59, 59)
		return result

	def change_dt_obj_as_begin_of_day(self, input_dt):
		"""
		dt객체를 그날짜의 0시 0분 0초로 수정하는것

		:param input_dt: datetime객체
		:return:
		"""
		changed_dt = datetime.datetime(input_dt.year, input_dt.month, input_dt.day, 0, 0, 0)
		return changed_dt

	def change_dt_obj_as_end_of_day(self, input_dt):
		"""
		dt객체를 그날짜의 23 시 59 분 59 초로 수정하는것

		:param input_dt: datetime객체
		:return:
		"""
		changed_dt = datetime.datetime(input_dt.year, input_dt.month, input_dt.day, 23, 59, 59)

		return changed_dt

	def change_dt_obj_to_dic_time(self, input_dt=""):
		"""
		datetime객체를 사전형식의 시간으로 바꾸는 것

		:param input_dt: datetime객체
		:return:
		"""

		result = self.get_information_for_dt_obj_as_dic(input_dt)
		return result

	def change_dt_obj_to_dt_timestamp(self, input_dt=""):
		"""
		날짜객체 => utc의 timestamp로 만드는 것
		timestamp : utc기준으로 1970년 1월 1일부터 1초마다 숫자를 더해서 사용
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = self.get_information_for_dt_obj_as_dic(input_dt)["timestamp"]
		return result

	def change_dt_obj_to_formatted_text_time(self, input_dt="", input_format="%Y-%m-%d %H:%M:%S"):
		"""
		입력형식으로 되어있는 시간자료를 dt객체로 인식하도록 만드는 것이다
		dt = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")

		:param input_dt: datetime객체, 날짜 객체
		:param input_format:
		:return:
		"""

		input_dt = self.check_dt_obj(input_dt)
		input_format = self.check_time_format(input_format)
		result = input_dt.strftime(input_format)
		return result

	def change_dt_obj_to_hms_list(self, input_dt=""):
		"""
		datetime객체 => [시, 분, 초]

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		temp = input_dt.strftime("%H-%M-%S")
		result = temp.split("-")
		return result

	def change_dt_obj_to_several_text_time(self, input_dt):
		"""
		시간 자료를 여러가지 text 형식의 시간으로 바꾸는 것
		예제를 위해서 만드는 것이다

		:param input_dt:
		:return:
		"""
		result = []
		input_dt = self.check_dt_obj(input_dt)
		local_time_offset = time.localtime().tm_gmtoff
		offset_hours = local_time_offset // 3600
		offset_minutes = (local_time_offset % 3600) // 60
		offset_str = f"{offset_hours:+03}:{offset_minutes:02}"
		all_dic = self.get_information_for_dt_obj_as_dic(input_dt)
		dayth = self.varx["영어서수_1~31"][int(all_dic['day']) - 1]

		result.append(f"{all_dic['year4']}-{all_dic['month2']}-{all_dic['day2']}")
		result.append(f"{all_dic['year4']}/{all_dic['month2']}/{all_dic['day2']}")
		result.append(f"{all_dic['year4']}{all_dic['month2']}{all_dic['day2']}")
		result.append(f"{all_dic['year2']}{all_dic['month2']}{all_dic['day2']} {all_dic['hour2']}{all_dic['min']}{all_dic['sec']}")
		result.append(f"{all_dic['month3_eng']} {all_dic['day2']}{all_dic['year4']} {all_dic['hour1']}:{all_dic['min']}{all_dic['ampm']}")
		result.append(f"{all_dic['month3_eng']} {all_dic['day2']} {all_dic['year4']} at {all_dic['hour1']}:{all_dic['min']}{all_dic['ampm']}")
		result.append(f"{all_dic['month_eng']} {all_dic['day2']}, {all_dic['year4']}, {all_dic['hour1']}:{all_dic['min']}:{all_dic['sec']}")
		result.append(f"{all_dic['week3_eng']}, {all_dic['day2']} {all_dic['month_eng']} {all_dic['year4']},")
		result.append(f"{all_dic['week_eng']}, {dayth} {all_dic['month_eng']} {all_dic['year4']} at {all_dic['hour1']}:{all_dic['min']}{all_dic['ampm']}")
		result.append(input_dt.isoformat())
		result.append(input_dt.isoformat() + offset_str)
		return result

	def change_dt_obj_to_utc(self, input_dt=""):
		"""
		:param input_dt: datetime객체, 날짜 객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		dt_timestamp = self.change_dt_obj_to_dt_timestamp(input_dt)
		result = dt_timestamp - 32400
		return result

	def change_dt_obj_to_xy_list(self, input_dt=""):
		"""
		시간을 좌표로 만들어 주는것
		x좌표 : 년월일 (0 ~ 9999*365)
		y좌표 : 시분초 (0 ~ 24*60*60)

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		sec_total = self.get_dt_timestamp_for_dt_obj(input_dt)
		hms_list = self.change_dt_obj_to_hms_list(input_dt)
		sec_hms = self.change_hms_list_to_sec(hms_list)
		sec_ymd = sec_total - sec_hms
		return [sec_ymd, sec_hms]

	def change_dt_obj_to_ymd_list(self, input_dt=""):
		"""
		결과 : [년, 월, 일]
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = self.get_information_for_dt_obj_as_dic(input_dt)["ymd_list"]
		return result

	def change_dt_obj_to_ymd_style_with_connect_char(self, input_dt="", connect_str="-"):
		"""
		datetime는 utc local
		입력문자를 기준으로 yyyy-mm-dd이런 스타일로 만드는 것이다
		시간객체 => 년-월-일

		:param input_dt: datetime객체, 날짜 객체
		:param connect_str: 연결할 문자
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		dic_time = self.change_dt_obj_to_dic_time(input_dt)
		result = dic_time["yea"] + connect_str + dic_time["mon"] + connect_str + dic_time["day"]
		return result

	def change_dt_obj_to_ymdhms_list(self, input_dt=""):
		"""
		바꾸기 : datetime객체 => [년, 월, 일, 시, 분, 초]

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = self.get_information_for_dt_obj_as_dic(input_dt)["ymdhms_list"]
		return result

	def change_dt_obj_to_yyyy_mm_dd(self, input_dt=""):
		"""
		바꾸기 : datetime객체 => 2025-03-01

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		temp = self.get_information_for_dt_obj_as_dic(input_dt)["ymd_list"]
		result = str(temp[0]) + "-" + str(temp[1]) + "-" + str(temp[2])
		return result

	def change_excel_time_float_to_dt_obj(self, input_excel_float):
		"""
		엑셀의 44652.123을 날짜와 시간으로 만들어 주는것

		:param input_excel_float:
		:return:
		"""
		days = int(input_excel_float)
		seconds = int((input_excel_float - days) * 86400)
		result = datetime.datetime(1899, 12, 30, 0, 0, 0) + datetime.timedelta(days=days, seconds=seconds)
		return result

	def change_float_hour_to_hm_list(self, input_fh):
		"""
		5.5시간을 5시간 30분으로 바꿔주는 것

		:param input_fh:
		:return:
		"""
		big_hour = int(input_fh)
		small_hour = input_fh - int(input_fh)
		minute = int(60 * small_hour)
		return [big_hour, minute]

	def change_formatted_text_time_to_dt_obj(self, input_time, input_format):
		"""
		datetime는 utc local
		formatted_text_time : 간 문자열과 문자열의 형식
		입력한 시간 문자열과 문자열의 형식을 넣어주면 datetime객체를 만들어 준다

		:param input_time: 문자열로된 시간
		:param input_format:
		:return:
		"""
		dt_obj = datetime.datetime.strftime(input_time, input_format)
		return dt_obj

	def change_formatted_text_to_hms_list(self, hms_list, end_text=["시", "분", "초"]):
		"""
		시분초의 리스트를 텍스트로 연결하는 것

		:param hms_list: [시, 분, 초]
		:param end_text:
		:return:
		"""
		result = f"{hms_list[0]:0> 2}{end_text[0]} {hms_list[1]:0> 2}{end_text[1]} {hms_list[2]:0> 2}{end_text[2]}"
		return result

	def change_hmd_list_to_sec(self, input_list=[0, 0, 1]):
		"""
		몇년 몇월 몇일을 초로 바꾸는 것
		입력형태 : [몇년, 몇월, 몇일]
		현재일자를 기준으로
		월은 30일 기준으로 계산한다
		기준날짜에서 계산을 하는 것이다
		"""
		total_sec = int(input_list[0]) * 60 * 60 * 24 * 365 + int(input_list[1]) * 60 * 60 * 24 * 30 + int(
			input_list[2]) * 60 * 60 * 24
		return total_sec

	def change_hms_list_for_dt_obj(self, input_dt, input_hms):
		"""
		입력으로 들어오는 dt 객체의 시간-분-초를 원하는 것으로 바꾸는 기능입니다

		:param input_dt: datetime객체
		:return:
		"""
		result = datetime.datetime(input_dt.year, input_dt.month, input_dt.day, input_hms[0], input_hms[1], input_hms[2])
		return result

	def change_hms_list_to_float(self, hms_list, base="hou"):
		"""
		시간을 숫자로 만들어서 계산을 편하게 만들기 위해서 만들어 본것

		[1,1,30] (1시간 1분 30초) => 61.5
		분:정수부분
		초: 소숫점 아래

		:param hms_list: [시, 분, 초]
		:param base:
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(hms_list)
		if base == "day":
			result = sec_1 / (60 * 60 * 24)
		elif base == "hou":
			result = sec_1 / (60 * 60)
		elif base == "min":
			result = sec_1 / (60)
		else:
			result = sec_1
		return result

	def change_hms_list_to_sec(self, input_value=""):
		"""
		hmslist : [시, 분, 초]
		출력값 : 초, 입력값으로 온 시분초를 초로 계산한것
		"""
		total_sec = int(input_value[0]) * 3600 + int(input_value[1]) * 60 + int(input_value[2])
		return total_sec

	def change_hms_text_to_sec(self, input_value=""):
		"""
		input_value = "14:06:23" => 초로 변경

		:param input_value:
		:return:
		"""
		re_compile = re.compile("\d+")
		result = re_compile.findall(input_value)
		total_sec = int(result[0]) * 3600 + int(result[1]) * 60 + int(result[2])
		return total_sec

	def change_input_local_to_utc(self, local_time_zone=9):
		"""
		기본적으로 datetime은 utc와 같은것이라 보면 된다
		:return:
		"""
		KST = datetime.timezone(datetime.timedelta(hours=local_time_zone))
		dt = datetime.datetime.now(datetime.timezone.utc)
		utc_time = dt.replace(tzinfo=KST)
		utc = utc_time.timestamp()
		return utc

	def change_lunar_day_to_two_solar_day(self, input_ymd):
		"""
		음력 -> 양력으로 변환시 (음력은 윤달인지 아닌지에대한 기준이 필요하다)
		결과값 : [평달일때의 양력, 윤달일때의 양력]
		#변수:year(년),month(월),day(일),intercalation(윤달여부)
		:param input_ymd:
		:return:
		"""
		self.lunar_calendar.setLunarDate(input_ymd[0], input_ymd[1], input_ymd[2], False)
		moon_day_1 = self.lunar_calendar.SolarIsoFormat()

		moon_day_2 = ""
		try:
			# 윤달이 없는 달이면, False를 돌려준다
			self.lunar_calendar.setLunarDate(input_ymd[0], input_ymd[1], input_ymd[2], True)
			moon_day_2 = self.lunar_calendar.SolarIsoFormat()
		except:
			pass
		if moon_day_1 == moon_day_2:
			moon_day_2 = False
		return [moon_day_1, moon_day_2]

	def change_lunar_dt_obj_to_solar_dt_obj(self, input_dt="", yoon_or_not=True):
		"""
		음력을 양력으로 만들어 주는것

		:param input_dt: datetime객체
		:param yoon_or_not:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		ymd_list = self.get_ymd_list_for_dt_obj(input_dt)
		self.lunar_calendar.setLunarDate(int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2]), yoon_or_not)
		result = self.change_any_text_time_to_dt_obj(self.lunar_calendar.SolarIsoFormat())
		return result

	def change_lunar_ymd_to_solar_dt_obj_with_yoon(self, input_ymd):
		"""
		음력 -> 양력으로 변환시 (음력은 윤달인지 아닌지에대한 기준이 필요하다)
		윤달이 있으면, 윤달의 값을 갖고오는것
		:param input_ymd:
		:return:
		"""
		l1d = self.change_lunar_day_to_two_solar_day(input_ymd)
		yymmdd = l1d[0]
		if l1d[1]:
			yymmdd = l1d[1]
		dt_obj = self.change_any_text_time_to_dt_obj(yymmdd)
		return dt_obj

	def change_lunar_ymd_to_solar_ymd(self, ymd_list, yoon_or_not=True):
		"""
		음력을 양력으로 만들어 주는것

		:param ymd_list: [년, 월, 일]
		:param yoon_or_not:
		:return:
		"""
		self.lunar_calendar.setLunarDate(int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2]), yoon_or_not)
		dt_obj = self.change_any_text_time_to_dt_obj(self.lunar_calendar.SolarIsoFormat())
		result = self.get_ymd_list_for_dt_obj(dt_obj)
		return result

	def change_lunar_ymd_to_solar_ymd_1(self, ymd_list, yoon_or_not=True):
		"""
		음력을 양력으로 바꿔주는 기능

		:param input_year:
		:return:
		"""
		lunar_calendar = KoreanLunarCalendar()
		lunar_calendar.setLunarDate(int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2]), yoon_or_not)

		result = lunar_calendar.SolarIsoFormat()
		if lunar_calendar.solarYear == 0:
			result = "error"
		return result

	def change_month_no_to_month_eng(self, month):
		"""
		이것은 월을 숫자로 받아서 문자로 돌려주는 것입니다 ---> 'MARCH'

		:param month: 월
		:return:
		"""
		month_long = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER',
					  'NOVEMBER', 'DECEMBER']
		return month_long[month - 1]

	def change_num_to_nth_eng_day(self, no):
		"""
		이것은 그날을 서수로 돌려주는 것입니다 ---> ['1ST']

		:param no:
		:return:
		"""
		data = ['1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH', '10TH', '11TH', '12TH', '13TH', '14TH',
				'15TH', '16TH', '17TH', '18TH', '19TH', '20TH', '21ST', '22ND', '23RD', '24TH', '25TH', '26TH', '27TH',
				'28TH', '29TH', '30TH', '31ST']
		return data[no - 1]

	def change_sec_to_day(self, input_sec):
		"""
		초를 날자로 계산해 주는것

		:param input_sec:
		:return:
		"""
		nalsu = int(input_sec) / (60 * 60 * 24)
		return nalsu

	def change_sec_to_dhm_list(self, input_value=""):
		"""
		초단위의 숫자를 넣으면 날, 시,분, 초로 만들어주는 것
		input_value = 123456

		:param input_value:
		:return:
		"""
		step_1 = divmod(int(input_value), 60)
		step_2 = divmod(step_1[0], 60)
		final_result = [step_2[0], step_2[1], step_1[1]]
		return final_result

	def change_sec_to_dhms_list(self, input_sec=""):
		"""
		초 => [날, 시, 분, 초]
		1000초 => 2일3시간10분30초
		dhms : day-hour-minute-sec

		:param input_sec:
		:return:
		"""
		step_1 = divmod(int(input_sec), 60)
		step_2 = divmod(step_1[0], 60)
		day = int(input_sec) / (60 * 60 * 24)
		result = [day, step_2[0], step_2[1], step_1[1]]
		return result

	def change_sec_to_hms_list(self, input_sec=""):
		"""
		초를 hour로 바꾸는 것
		input_value = 123456 => 3시간 25분 45초
		입력값 : 123456 => [시, 분, 초]

		:param input_value:
		:return:
		"""
		step_1 = divmod(int(input_sec), 60)
		step_2 = divmod(step_1[0], 60)
		final_result = [step_2[0], step_2[1], step_1[1]]
		return final_result

	def change_solar_dt_obj_to_lunar_dt_obj(self, input_dt="", yoon_or_not=True):
		"""
		날짜 객체인데, 음력의 날짜 객체로 변경하는 것
		음력을 양력으로 만들어 주는것

		:param input_dt: datetime객체
		:param yoon_or_not:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		ymd_list = self.get_ymd_list_for_dt_obj(input_dt)
		self.lunar_calendar.setSolarDate(int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2]))
		result = self.change_any_text_time_to_dt_obj(self.lunar_calendar.LunarIsoFormat())
		return result

	def change_solar_ymd_list_to_lunar_ymd_list(self, ymd_list):
		"""
		양력 -> 음력으로 변환시
		결과값 : [음력, 윤달여부]

		:param ymd_list: [년, 월, 일]
		:return:
		"""
		self.lunar_calendar.setLunarDate(ymd_list[0], ymd_list[1], ymd_list[2], False)
		lunar_ymd = self.lunar_calendar.LunarIsoFormat()
		yoon_or_not = self.lunar_calendar.isIntercalation()

		return [lunar_ymd, yoon_or_not]

	def change_text_time_to_another_formatted_text_time(self, input_time, input_time_format):
		"""
		입력시간을 다른 형식으로 바꾸는 것

		:param input_time_format:
		:param input_format:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		result = time.strptime(dt_obj, input_time_format)
		return result

	def change_utc_to_day_list(self, input_utc=""):
		"""
		입력값 : utc시간숫자, 1640995200.0 또는 ""
		일 -----> ['05']
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc:utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["day1"], all_dic["day2"]]

	def change_utc_to_dt_obj(self, input_utc):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		utc  : 1970년 1월 1일을 0밀리초로 계산한 것
		utc  : 1640995200.0 또는 "", 1648037614.4801838 (의미 : 2022-03-23T21  13:34.480183+09:00)
		datetime : 1900.1.1을 1초로 시작

		:param input_utc:utc의 timestamp값이 들어오는 것
		:return:
		"""
		input_utc = self.check_input_utc(input_utc)
		dt_timestamp = input_utc + 1640995200
		dt_obj = self.change_anytime_to_dt_obj(dt_timestamp)
		return dt_obj

	def change_utc_to_end_of_day_for_month(self, input_utc=""):
		"""
		입력한 날짜나 시간의 마지막날을 게산하는것
		입력값 : 시간 또는 날짜
		출력값 : 그달의 마지막날

		:param input_utc:utc의 timestamp값이 들어오는 것
		:return:
		"""
		input_utc = self.check_input_utc(input_utc)
		lt = self.change_anytime_to_utc(input_utc)
		result = time.strftime('%W', lt)
		return result

	def change_utc_to_hour_list(self, input_utc=""):
		"""
		입력값 : utc시간숫자, 1640995200.0 또는 ""
		시 -----> ['10', '22']
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc:utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["hour1"], all_dic["hour2"]]

	def change_utc_to_text_time_as_format(self, input_utc, format_a):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		:param input_utc:utc의 timestamp값이 들어오는 것
		:param format_a:
		:return:
		"""
		input_utc = self.check_input_utc(input_utc)
		result = self.set_format_for_utc(format_a, input_utc)
		return result

	def change_utc_to_timedic(self, input_utc=""):
		"""
		입력된 시간에 대한 왠만한 모든 형식의 날짜 표현을 사전형식으로 돌려준다

		:param input_value:
		:return:
		"""

		dt_obj = self.change_utc_to_dt_obj(input_utc)
		result = self.get_information_for_dt_obj_as_dic(dt_obj)
		return result

	def change_utc_to_utc(self, input_utc):
		"""
		숫자형으로된 시간을 utc로 바꾸는 것
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		:param input_utc:utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		:return:
		"""
		result = time.gmtime(input_utc)
		return result

	def change_utc_to_week_list(self, input_utc):
		"""

		:param input_utc:utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		result = self.get_week_list_for_dt_obj(dt_obj)
		return result

	def change_utc_to_ymd_dash(self, input_utc):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		utc를 2023-2-2형태로 돌려주는 것

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return str(all_dic["year"]) + "-" + str(all_dic["month"]) + "-" + str(all_dic["day"])

	def change_utc_to_ymd_list(self, input_utc):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["year"], all_dic["month"], all_dic["day"]]

	def change_yearweekno_to_ymd_list_for_monday(self, input_year, input_yearweekno):
		"""
		년도, 위크번호 ==> 그주의 월요일

		:param input_year:
		:param input_yearweekno:
		:return:
		"""
		text_time = f"{input_year}-{input_yearweekno}"
		dt_obj = datetime.datetime.strptime(text_time + '-1', "%Y-%W-%w")
		result = self.get_ymd_list_for_dt_obj(dt_obj)
		return result

	def change_ymd_list_to_dt_obj(self, ymd_list):
		"""

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.check_input_time(ymd_list)
		return dt_obj

	def change_ymd_list_to_sec(self, ymd_list):
		"""
		[년, 월, 일] => 초

		:param ymd_list:
		:return:
		"""
		total_sec = int(ymd_list[0]) * self.varx["year_sec"] + int(ymd_list[1]) * self.varx["month_sec"] + int(
			ymd_list[2]) * self.varx["day_sec"]
		return total_sec

	def change_ymd_list_to_utc(self, ymd_list):
		"""
		입력 : [년, 월, 일]
		출력 : utc값

		:param ymd_list:
		:return:
		"""
		atime = arrow.get(int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2]))
		result = atime.timestamp()
		return result

	def change_ymd_list_to_yearweekno(self, ymd_list=""):
		"""
		yearweekno : 1년에서 몇번째 주인지 아는것
		입력한날의 week 번호를	계산
		입력값 : 날짜

		:param input_date: 일반적으로 사용하는 날짜를 나타내는 문자나 리스트
		:return:
		"""
		if ymd_list == "":
			today = self.get_yyyy_mm_dd_for_today()
			year, month, day = today.split("-")
			dt_obj = self.check_input_time([year, month, day])
		else:
			dt_obj = self.change_anytime_to_dt_obj(ymd_list)
		result = int(dt_obj.strftime("%W"))
		return result

	def change_ymdhms_list_to_dt_obj(self, input_ymdhms_list):
		"""
		[2023, 3, 1, 0, 0, 0] => datetime객체

		:param input_ymdhms_list:
		:return:
		"""
		dt_obj = ""
		temp = ""
		for one in input_ymdhms_list:
			temp = temp + str(one) + "-"
			dt_obj = datetime.datetime.strptime(temp[:-1], "%Y-%m-%d-%H-%M-%S")
		return dt_obj

	def change_yyyy_mm_dd_to_dt_obj(self, input_iso_format="2023-03-01"):
		"""
		많이 사용하는 형식이라 만든 것입니다
		date 클래스의 isoformat()  : YYYY-MM-DD의 형식

		:param input_iso_format:
		:return:
		"""
		dt_obj = datetime.datetime.fromisoformat(input_iso_format)
		return dt_obj

	def check_datetime(self, input_value):
		"""

		:param input_value:
		:return:
		"""
		if isinstance(input_value, (list, tuple)):
			result = []
			for one in input_value:
				aa = self.check_datetime(one)
				result.append(aa)
				return result
		elif isinstance(input_value, (pywintypes.TimeType)):
			temp = str(input_value).split("")
			if temp[1] == "0 군00:00+00:00":
				result = temp[0]
			else:
				aaa = temp[0] + "" + temp[1].split("+")[0]
				result = aaa
			return result
		elif isinstance(input_value, (float)):
			if 0 < input_value < 1:
				# ("1 보다 작은 정수 =>", input_value)
				return input_value
			elif isinstance(input_value, set):
				return set(self.check_datetime(x) for x in input_value)
			else:
				# print(type(input_value), input__data)
				return input_value

	def check_day_or_not(self, input_list):
		"""
		입력된 자료들이 년을 나타내는 자료인지를 확인하는것

		:param input_list:
		:return:
		"""
		result = []
		alphabet = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
		if type(input_list[0]) == type([]):
			changed_input_list = input_list
		else:
			changed_input_list = []
			for one in input_list:
				changed_input_list.append([one])

		for one_list in changed_input_list:
			if str(one_list[0])[0] in alphabet:
				# 알파벳으로 사용하는것은 월밖에 없다
				result.append(False)
			else:
				if len(str(one_list[0])) == 4:
					# 4개의 숫자는 년도를 나타내는 것
					result.append(False)
				elif len(one_list[0]) <= 2:
					result.append(True)

				if int(one_list[0]) > 31:
					# 31보다 크면, 년도이다
					result.append(False)
				else:
					# 12보다 크면, 월을 나타내는것이 아니다
					result.append(True)

		total_num = 0
		for one in result:
			total_num = total_num + one

		# 전체중에서 1보다 넘으면 년을 쓰인것으로 본다
		# 숫자가 2개이하인것과 12이상일때, 두번 True로 만들기때문에...
		if total_num / len(result) > 1:
			month_or_not = True
		else:
			month_or_not = False
		return month_or_not

	def check_dt_obj(self, input_dt=""):
		"""
		datetime객체를 만드는 것

		:param input_dt: datetime객체
		:return:
		"""
		if not input_dt:
			input_dt = self.get_dt_obj_for_now()
		else:
			input_dt = self.change_anytime_to_dt_obj(input_dt)
		return input_dt

	def check_holiday_on_year(self, input_year, input_value):
		"""
		입력받은 공휴일 자료중에서 양력으로 된것은 그대로 저장하고
		음력으로 된것을 양력 날짜로 바꾸는것

		:param input_year:
		:param input_value:
		:return:
		"""
		result = []
		if input_value[2] == "양":
			dt_obj = self.change_ymd_list_to_dt_obj([input_year, input_value[0], input_value[1]])
		elif input_value[2] == "음":
			if input_value[1] == "말일":
				input_value[1] = self.check_lunar_last_day_for_lunar_ym_list([input_year, input_value[0]])

			self.lunar_calendar.setLunarDate(input_year, input_value[0], input_value[1], False)
			dt_obj = self.change_any_text_time_to_dt_obj(self.lunar_calendar.SolarIsoFormat())

		week_no_7 = self.get_no_of_sunday_in_same_week_for_dt_obj(dt_obj)
		new_ymd_list = self.get_ymd_list_for_dt_obj(dt_obj)
		for index in range(int(input_value[3])):
			checked_ymd_list = self.check_ymd_list([new_ymd_list[0], new_ymd_list[1], int(new_ymd_list[2]) + index])
			result.append(
				[checked_ymd_list[0], checked_ymd_list[1], checked_ymd_list[2], divmod(int(week_no_7) + index, 7)[1],
				 input_value[-1]])
		return result

	def check_input_time(self, input_time=""):
		"""
		어떤 형태가 들어오더라도 datetime으로 돌려주는 것

		:param input_time: 문자열로된 시간
		:return:
		"""
		if input_time == "":  # 아무것도 입력하지 않으면 local time 으로 인식한다
			result = datetime.datetime.now()

		elif type(input_time) == type(datetime.datetime.now()):  # 만약 datetime객체일때
			result = input_time

		elif type(input_time) == pywintypes.TimeType:  # 만약 datetime 객체일때
			result = input_time

		elif type(input_time) == type(float(123.00)) or type(input_time) == type(int(123.00)):  # timestamp로 인식
			result = datetime.datetime.fromtimestamp(input_time)

		elif type("string") == type(input_time):  # 만약 입력형태가 문자열이면 : "202201O", "22/mar/01","22mar01"
			result = self.change_any_text_time_to_dt_obj(input_time)

		elif type(input_time) == type([]):  # 리스트 형태의 경우
			if len(input_time) >= 3:
				if input_time[2] == "말일":
					input_time[2] = 31
				self.year, self.month, self.day = int(input_time[0]), int(input_time[1]), int(input_time[2])
				result = datetime.datetime(self.year, self.month, self.day)
		else:
			result = datetime.datetime.now()  # 이두저두 아무것도 아닐때, 현재 시간객체를 돌려준다
		return result

	def check_input_utc(self, input_utc=""):
		"""

		:param input_utc:utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		:return:
		"""
		if input_utc == "":
			input_utc = self.get_utc_for_now()
		return input_utc

	def check_lunar_last_day_for_lunar_ym_list(self, input_ym_list):
		"""
		음력으로 말일을 찾는것

		:param input_ym_list: [년, 월]
		:return:
		"""
		result = 26
		for nun in range(27, 31):
			self.lunar_calendar.setLunarDate(input_ym_list[0], input_ym_list[1], nun, False)
			temp = self.lunar_calendar.SolarIsoFormat()
			ymd_list = temp.split("-")
			if int(ymd_list[2]) >= result:
				# print("말일 찾기 ==> ", result)
				result = int(ymd_list[2])
			else:
				break
		return result

	def check_month_or_not(self, input_list):
		"""
		입력된 자료들이 월을 나타내는 자료인지를 확인하는것

		:param input_list:
		:return:
		"""
		result = []
		alphabet = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
		if type(input_list[0]) == type([]):
			changed_input_list = input_list
		else:
			changed_input_list = []
			for one in input_list:
				changed_input_list.append([one])

		for one_list in changed_input_list:
			if str(one_list[0])[0] in alphabet:
				# 알파벳으로 사용하는것은 월밖에 없다
				result.append(True)
			else:
				if len(str(one_list[0])) == 4:
					# 4개의 숫자는 년도를 나타내는 것
					result.append(False)
				elif int(one_list[0]) > 31:
					# 31보다 크면, 년도이다
					result.append(False)
				elif int(one_list[0]) > 12 and int(one_list[0]) <= 31:
					# 12보다 크면, 월을 나타내는것이 아니다
					result.append(True)
		total_num = 0
		for one in result:
			total_num = total_num + one

		# 전체중에서 70%가 넘으면 월로쓰인것으로 본다
		if total_num / len(result) > 0.9:
			month_or_not = True
		else:
			month_or_not = False

		return month_or_not

	def check_next_day_of_holiday(self, holiday_list, input_l2d):
		"""
		대체공휴일을 확인하는것
		일요일인것만, 리스트로 만들어 준다

		:param holiday_list:
		:param input_l2d:
		:return:
		"""
		result = []
		if holiday_list == "all":
			for l1d in input_l2d:
				temp = []
				sunday = 0
				for one in l1d:
					if one[3] == 0:    sunday = 1
					one[2] = int(one[2]) + sunday
					temp.append(one)
				result.append(temp)
		else:
			for l1d in input_l2d:
				temp = []
				if l1d in holiday_list:
					sunday = 0
					for one in l1d:
						if one[3] == 0:  # 일요일의 값인 0이 있다면...
							sunday = 1
						one[2] = int(one[2]) + sunday
						temp.append(one)
					result.append(temp)
				else:
					result.append(l1d)

		return result

	def check_solar_day_for_last_day_of_lunar_ym_list(self, input_ym_list, yoon_or_not=True):
		"""
		음력으로 입력된 것중에 말일이라고 된것의 양력날짜를 구하는 것
		yoon_or_not : 윤달인지 아닌지에 대한 설정

		:param input_ym_list: [년, 월]
		:param yoon_or_not:
		:return:
		"""
		for num in range(27, 31):
			try:
				# 윤달이 아닌 날짜를 기준으로 확인
				self.lunar_calendar.setLunarDate(int(input_ym_list[0]), int(input_ym_list[1]), num, yoon_or_not)
				dt_obj = self.change_any_text_time_to_dt_obj(self.lunar_calendar.SolarIsoFormat())
				ymd_list = self.get_ymd_list_for_dt_obj(dt_obj)
			except:
				break
		return ymd_list

	def check_text_time_with_xsql(self, input_time, xsql):
		"""
		xsql = "[숫자:1~2](시간|시)[숫자:1~2](분)[숫자:0~2](초)[0~1]"

		:param input_time:
		:param xsql:
		:return:
		"""
		rex = xy_re.xy_re()
		result = rex.search_all_by_xsql(input_time, xsql)
		return result

	def check_time_format(self, input_text="년-월"):
		"""
		한글을 사용가능하도록 만들기 위한것

		:param input_text:
		:return:
		"""
		dic_data = {"년": "%Y", "월": "%m", "일": "%d", "시": "%H", "분": "%M", "초": "%S", }
		for one_key in dic_data.keys():
			input_text = input_text.replace(one_key, dic_data[one_key])
		return input_text

	def check_time_type_for_input_value(self, input_value):
		"""
		입력값이 시간형식의 값인지를 확인하는 것

		:param input_value:
		:return:
		"""
		result = False
		if type(input_value) is pywintypes.TimeType:
			result = str(input_value)
		return result

	def check_two_hms_list(self, hms_list_1, hms_list_2):
		"""
		기준시간을 기준으로 삼아서, 두번째 시간이 그것보다 앞인지 뒤인지를 나타내는것

		:param hms_list_1:
		:param hms_list_2:
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(hms_list_1)
		sec_2 = self.change_hms_list_to_sec(hms_list_2)
		if sec_1 >= sec_2:
			result = "기준시간 초과"
		else:
			result = "기준시간 이전"
		return result

	def check_year_or_not(self, input_list):
		"""
		입력된 자료들이 년을 나타내는 자료인지를 확인하는것

		:param input_list:
		:return:
		"""
		result = []
		alphabet = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
		if type(input_list[0]) == type([]):
			changed_input_list = input_list
		else:
			changed_input_list = []
			for one in input_list:
				changed_input_list.append([one])

		for one_list in changed_input_list:
			if str(one_list[0])[0] in alphabet:
				# 알파벳으로 사용하는것은 월밖에 없다
				result.append(False)
			else:
				if len(str(one_list[0])) == 4:
					# 4개의 숫자는 년도를 나타내는 것
					result.append(True)
				elif int(one_list[0]) > 31:
					# 31보다 크면, 년도이다
					result.append(True)
				elif int(one_list[0]) > 12 and int(one_list[0]) <= 31:
					# 12보다 크면, 월을 나타내는것이 아니다
					result.append(False)
		total_num = 0
		for one in result:
			total_num = total_num + one

		# 전체중에서 70%가 넘으면 년을 쓰인것으로 본다
		if total_num / len(result) > 0.5:
			month_or_not = True
		else:
			month_or_not = False
		return month_or_not

	def check_ymd_list(self, ymd_list):
		"""
		YMD리스트로 들어온값이 월과 일을 넘는 숫자이면 이것을 고치는것
		[2000, 14, 33] ==> [2001, 3, 31]

		:param ymd_list: [년, 월, 일]
		:return:
		"""
		year = int(ymd_list[0])
		month = int(ymd_list[1])
		day = int(ymd_list[2])
		if month > 12:
			year = year + divmod(month, 12)[0]
			month = divmod(month, 12)[1]
			if month == 0:
				year = year - 1
				month = 12

		if day > 25:
			delta_day = day - 25
			dt_obj = self.change_ymd_list_to_dt_obj([year, month, 25])
			dt_obj = self.shift_day_for_dt_obj(dt_obj, delta_day)
		else:
			dt_obj = self.change_ymd_list_to_dt_obj([year, month, day])

		result = self.get_ymd_list_for_dt_obj(dt_obj)
		return result

	def check_ymd_list_1(self, year, one_list):
		"""
		윤년의 날짜가 많이 틀려질수가 있어서, 12월은 "말일"이라는 단어를 쓰기때문에 이런것들을 확인하는 기능임
		현재 년도의 음력값을 갖고온다

		:param year:
		:param one_list:
		:return:
		"""
		if one_list[1][2] == "음":
			# "말일"이라는 단어가 있다면, 음력의 말일을 찾아서 넣는것이다
			if one_list[1][1] == "말일":
				one_list[1][1] = self.get_last_day_of_yyyymm_for_lunar(year, one_list[1][0])

			# 음력의 날짜를 양력의 날짜로 변경
			result = self.change_lunar_ymd_to_solar_ymd([year, one_list[1][0], one_list[1][1]], True)
			if result == "error": pass

		if one_list[1][2] == "양":
			result = [year, one_list[1][0], one_list[1][1]]
		return result

	def combine_date_obj_and_time_obj(self, input_date_obj, input_time_obj):
		"""
		날짜객체와 시간객체를 하나로 만드는 것

		:param input_date_obj:
		:param input_time_obj:
		:return:
		"""
		dt_obj = datetime.datetime.combine(input_date_obj, input_time_obj)
		return dt_obj

	def data_for_time_zone(self):
		"""

		:return:
		"""
		local_name = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
		sec = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
		hour = int(sec / 3600) * -1
		return [hour, local_name]

	def data_national_holiday_in_year(self, ymd_list1, ymd_list2):
		"""
		입력한 해의 국정공휴일을 반환해 주는 것이다
		[공휴일지정 시작일, 공휴일지정 끝나는날],[공휴일 월, 일, 음/양, 몇일간 연속된것인지, 윤달여부, 공휴일의 이름]

		:param ymd_list1:
		:param ymd_list2:
		:return:
		"""

		holiday_list2d = self.varx["holiday_list"]

		# 전체적으로 사용되는 변수들
		result_sun = []
		end_ymd_list_moon = self.shift_day_for_ymd_list(ymd_list2, 62)
		base_start_no = int(ymd_list1[0]) * 10000 + int(ymd_list1[1]) * 100 + int(ymd_list1[2])
		base_end_no = int(ymd_list2[0]) * 10000 + int(ymd_list2[1]) * 100 + int(ymd_list2[2])

		# 양력의 자료에 대해서 구한것
		period_list_sun = self.split_period_as_year_basis(ymd_list1, ymd_list2)
		for start_ymd_list, end_ymd_list in period_list_sun:
			year = int(start_ymd_list[0])
			for one_holiday in holiday_list2d:
				# 위의 자료를 모두 확인해서, 입력한 년도와 관계있는것만 골라내는 것
				if one_holiday[1][2] == "양":
					holiday_no = year * 10000 + int(one_holiday[1][0]) * 100 + int(one_holiday[1][1])
					if base_start_no <= holiday_no and base_end_no >= holiday_no and one_holiday[0][0] <= holiday_no and \
							one_holiday[0][1] >= holiday_no:
						result_sun.append([year, int(one_holiday[1][0]), int(one_holiday[1][1])] + one_holiday[1])

		# 음력중 평달인것만 구한것
		# 음력을 변환했을때의 양력날짜는 양력의 날짜보다 클수가 없다. 그래서 음력의 기간을 다시 설정하는 것이다
		period_list_moon = self.split_period_as_year_basis(ymd_list1, end_ymd_list_moon)

		for start_ymd_list, end_ymd_list in period_list_moon:
			year = int(start_ymd_list[0])

			for one_holiday in holiday_list2d:
				# 위의 자료를 모두 확인해서, 입력한 년도와 관계있는것만 골라내는 것
				if one_holiday[1][2] == "음":
					if one_holiday[1][1] == "말일":
						ymd_list_moon = self.check_lunar_last_day_for_lunar_ym_list([year, one_holiday[1][0]])
					else:
						ymd_list_moon = [year, one_holiday[1][0], one_holiday[1][1]]

					self.lunar_calendar.setLunarDate(ymd_list_moon[0], ymd_list_moon[1], ymd_list_moon[2], True)

					ymd_list_sun = self.change_lunar_ymd_to_solar_ymd(ymd_list_moon)
					holiday_no = int(ymd_list_sun[0]) * 10000 + int(ymd_list_sun[1]) * 100 + int(ymd_list_sun[2])

					if base_start_no <= holiday_no and base_end_no >= holiday_no and one_holiday[0][0] <= holiday_no and \
							one_holiday[0][1] >= holiday_no:
						result_sun.append(ymd_list_sun + one_holiday[1])
		return result_sun

	def get_1st_day_n_last_day_for_ym_list(self, input_ym_list):
		"""
		[2023, 05] => [(1,31), 1, 31]

		:param input_ym_list: [년, 월]
		:return:
		"""
		date = datetime.datetime(year=input_ym_list[0], month=input_ym_list[1], day=1).date()
		monthrange = calendar.monthrange(date.year, date.month)
		first_day = calendar.monthrange(date.year, date.month)[0]
		last_day = calendar.monthrange(date.year, date.month)[1]
		return [date, monthrange, first_day, last_day]

	def get_1st_day_n_last_day_for_yms_list(self, input_ymslist):
		"""
		입력으로 들어온 날짜를 기준으로 그 월의 시작날짜와 끝날짜를 돌려주는 것

		:param input_ymslist:
		:return:
		"""
		date = datetime.datetime(year=input_ymslist[0], month=input_ymslist[1], day=1).date()
		monthrange = calendar.monthrange(date.year, date.month)
		first_day = calendar.monthrange(date.year, date.month)[0]
		last_day = calendar.monthrange(date.year, date.month)[1]
		return [date, monthrange, first_day, last_day]

	def get_7_day_list_for_dt_obj(self, input_dt=""):
		"""
		월요일부터 시작하는 7 개의 날짜를 돌려준다
		2023-07-24 : f'{year} {week_no_year} 0' => f'{year} {week_no_year} 1'

		:param year:
		:param week_no_year:
		:return:
		"""
		dic_data = self.get_information_for_dt_obj_as_dic(input_dt)

		str_datetime = f'{dic_data["year"]} {dic_data["yearweek"]} 1'  # 1은 월요일 이다

		# 문자열형태로 입력받아서, 시간객체로 만들어 주는것
		startdate = datetime.datetime.strptime(str_datetime, '%Y %W %w')
		dates = []
		for i in range(7):
			day = startdate + datetime.timedelta(days=i)
			dates.append(day.strftime("%Y-%m-%d"))
		return dates

	def get_7_day_list_for_yearweekno(self, year, week_no):
		"""
		일요일부터 시작하는 7개의 날짜를 돌려준다
		"""
		str_datetime = f'{year} {week_no} 0'
		startdate = datetime.datetime.strptime(str_datetime, '%Y %W %w')
		dates = [startdate.strftime('%Y-%m-%d')]
		for i in range(1, 7):
			day = startdate + datetime.timedelta(days=i)
			dates.append(day.strftime('%Y-%m-%d'))
		return dates

	def get_all_day_list_for_year_month(self, input_year, input_month):
		"""
		년과 월을 주면, 한달의 리스트를 알아내는것
		월요일부터 시작

		:param input_year: 년
		:param input_month: 월
		:return:
		"""
		result = []
		week_no = []
		date_obj = datetime.datetime(year=input_year, month=input_month, day=1).date()
		first_day_wwek_no = calendar.monthrange(date_obj.year, date_obj.month)[0]
		last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
		if first_day_wwek_no == 0:
			pass
		else:
			for no in range(first_day_wwek_no):
				week_no.append("")
		for num in range(1, int(last_day) + 1):
			if len(week_no) == 7:
				result.append(week_no)
				week_no = [num]
			else:
				week_no.append(num)
		if week_no:
			result.append(week_no)
		return result

	def get_all_holiday_for_lunar_year(self, input_year):
		"""
		음력으로된 휴일
		:param input_year:
		:return:
		"""
		result = []
		for one_list in self.varx["lunar_holiday_list"]:
			if one_list[0][0] <= input_year and one_list[0][3] >= input_year:
				if one_list[1][1] == "말일":
					one_list[1][1] = self.get_last_day_of_yyyymm_for_lunar(input_year, one_list[1][0])

				# 음력의 날짜를 양력의 날짜로 변경
				solar_date = self.change_lunar_ymd_to_solar_ymd_1([input_year, one_list[1][0], one_list[1][1]], True)
				if solar_date == "0000-00-00" or solar_date == "error":
					pass
				else:
					year_2, month, day = str(solar_date).split("-")
					result.append([int(year_2), int(month), int(day), one_list[1][-1]])
		return result

	def get_all_holiday_for_solar_year(self, input_year):
		"""
		입력 년도의 양력의 휴일
		:param input_year: 년도를 입력하는 것
		:return:
		"""

		result = []
		for one_list in self.varx["solar_holiday_list"]:
			if one_list[0][0] <= input_year and one_list[0][3] >= input_year:
				result.append([input_year, one_list[1][0], one_list[1][1], one_list[1][-1]])
		return result

	def get_all_holiday_list_between_two_day(self, ymd_list_1, ymd_list_2):
		"""
		두날짜 사이의 휴일을 갖고오는것
		단, 음력은 한국/일본/중국이 같이 만들어가기 때문에, 당년도를 제외한 미래의 날짜는 알수가 없다
		:param ymd_list_1: [2025, 3, 1]
		:param ymd_list_2: [2025, 3, 1]
		:return:
		"""
		result = []
		total_holiday_list = []
		for one_year in range(ymd_list_1[0], ymd_list_2[0] + 1):
			solar_ymd_list = self.get_all_holiday_for_solar_year(one_year)
			for one in solar_ymd_list:
				total_holiday_list.append(one)

		# 음력의 경우는 2년을 더하기 빼기해서 계산한다
		for one_year in range(ymd_list_1[0] - 2, ymd_list_2[0] + 2):
			lunar_ymd_list = self.get_all_holiday_for_lunar_year(one_year)
			for one in lunar_ymd_list:
				total_holiday_list.append(one)

		dt_obj_date_1 = self.change_ymd_list_to_dt_obj(ymd_list_1)
		dt_obj_date_2 = self.change_ymd_list_to_dt_obj(ymd_list_2)
		for one in total_holiday_list:
			aaa = self.change_ymd_list_to_dt_obj([one[0], one[1], one[2]])
			if dt_obj_date_1 <= aaa <= dt_obj_date_2:
				result.append(one)
		# result.sort()
		return result

	def get_day_for_now(self, input_time=""):
		"""
		일 -----> 05

		:param input_time:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["day"]

	def get_day_for_utc(self, input_time=""):
		"""
		입력값 : utc시간숫자, 1640995200.0 또는 ""
		일 -----> 05

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["day"]

	def get_day_set_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		일 -----> ['05', '095']

		:param time_char:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["day2"], all_dic["day3"]]

	def get_day_set_for_now(self):
		"""
		일 -----> ['05', '095']
		:return:
		"""
		all_dic = self.get_information_for_dt_obj_as_dic("")
		return [all_dic["day2"], all_dic["day3"]]

	def get_day_set_for_utc(self, input_utc=""):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		일 -----> ['05']
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["day1"], all_dic["day2"]]

	def get_dic_time_for_dt_obj(self, input_dt=""):
		"""
		datetime객체를 사전형식의 시간으로 바꾸는 것

		:param input_dt: datetime객체
		:return:
		"""
		all_dic = self.get_information_for_dt_obj_as_dic(input_dt)
		return all_dic

	def get_dt_obj_for_now(self):
		"""
		기본인 datetime 객체를 돌려주는 것은 별도로 표기하지 않는다
		날짜와 시간(datetime) -> 문자열로 : strftime
		날짜와 시간 형식의 문자열을 -> datetime으로 : strptime

		:return:
		"""
		dt_obj = datetime.datetime.now()
		return dt_obj

	def get_dt_obj_for_now_as_local_time_zone(self):
		"""
		utc시간이 아니고 현재 지역적인 시간으로 변경하는 것
		3.6버전이후에 나타나는 astimezone를 사용하면 알아서 적용되는 것이다
		"""
		dt_obj = datetime.datetime.now()
		changed_dt_obj = dt_obj.astimezone()
		return changed_dt_obj

	def get_dt_obj_for_today(self):
		"""
		날짜와 시간(datetime) -> 문자열로 : strftime
		날짜와 시간 형식의 문자열을 -> datetime으로 : strptime

		:return:
		"""
		dt_obj = datetime.datetime.now()
		return dt_obj

	def get_dt_obj_for_ymd_list_as_0h_0m_0s(self, ymd_list=""):
		"""

		"""
		if ymd_list == "":
			today = self.get_dt_obj_for_today()
		else:
			today = self.change_ymd_list_to_dt_obj(ymd_list)
		start_of_today = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
		return start_of_today

	def get_dt_obj_for_ymd_list_as_23h_59m_59s(self, ymd_list=""):
		"""
		입력으로 드러오는 날짜객체의 시간을 그날의 마지막 시간으로 설정하기 위한 것이다
		"""
		if ymd_list == "":
			today = self.get_dt_obj_for_today()
		else:
			today = self.change_ymd_list_to_dt_obj(ymd_list)
		start_of_today = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
		return start_of_today

	def get_dt_timestamp(self):
		"""
		기본적으로 datetime은 utc와 같은것이라 보면 된다
		:return:
		"""

		dt = datetime.datetime.now(datetime.timezone.utc)
		# utc_time = dt.replace(tzinfo=datetime.timezone.utc)
		dt_timestamp = dt.timestamp()
		return dt_timestamp

	def get_dt_timestamp_for_dt_obj(self, input_dt=""):
		"""
		날짜객체 => timestamp로 만드는 것

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = input_dt.timestamp()
		return result

	def get_dt_timestamp_for_now(self):
		"""
		기본적으로 datetime은 utc와 같은것이라 보면 된다
		:return:
		"""

		dt = datetime.datetime.now(datetime.timezone.utc)
		dt_timestamp = dt.timestamp()
		return dt_timestamp

	def get_end_day_of_month_for_text_time(self, input_time=""):
		"""
		입력한 날의 월의 마지막 날짜를 계산
		입력받은 날자에서 월을 1나 늘린후 1일을 마이너스 한다
		예: 2023-04-19 -> 2023-05-01 -> 2023-05-01 - 1일 -> 2023-04-30

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		if dt_obj.month == 12:
			year = dt_obj.year + 1
			month = 1
		else:
			year = dt_obj.year
			month = dt_obj.month + 1
		dt_obj_1 = datetime.datetime(year, month, 1)
		dt_obj_2 = dt_obj_1 + datetime.timedelta(days=-1)
		result = dt_obj_2.day
		return result

	def get_hms_list_for_dt_obj(self, input_dt=""):
		"""
		datetime객체 => [시, 분, 초]

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		temp = input_dt.strftime("%H-%M-%S")
		result = temp.split("-")
		return result

	def get_hms_list_for_now(self):
		"""
		utc시간이 아니고 현재 지역적인 시간으로 변경하는 것
		3.6버전이후에 나타나는 astimezone를 사용하면 알아서 적용되는 것이다
		"""
		dt_obj = datetime.datetime.now()
		changed_dt_obj = dt_obj.astimezone()
		result = self.change_dt_obj_to_hms_list(changed_dt_obj)
		return result

	def get_holiday_list_between_day1_and_day2(self, input_anytime1, input_anytime2):
		"""
		날짜사이의 휴일의 리스트 얻기

		:param ymd_list1: [년, 월, 일]
		:param ymd_list2: [년, 월, 일]
		:return:
		"""

		dic_time_1 = self.get_information_for_dt_obj_as_dic(input_anytime1)
		dic_time_2 = self.get_information_for_dt_obj_as_dic(input_anytime2)

		start_day = int(dic_time_1["year"] + dic_time_1["mon"] + dic_time_1["day"])
		end_day = int(dic_time_2["year"] + dic_time_2["mon"] + dic_time_2["day"])

		result = []
		# self.varx["holiday_list"] = [[[20060101, 20061231], [9, 6, "양", 1, "", "임시공휴일"]],[[19880101, 19881231], [9, 17, "양", 1, "", "임시공휴일"]],....]
		for list1d in self.varx["holiday_list"]:
			if list1d[0][0] <= int(start_day) and list1d[0][1] >= int(end_day):
				if list1d[1][0] <= int(dic_time_1["mon"]) and list1d[1][0] <= int(dic_time_2["mon"]) and list1d[1][
					1] <= int(dic_time_1["day"]) and list1d[1][1] <= int(dic_time_2["day"]):
					temp_year = [str(list1d[0][0])[0:4]]
					result.append(temp_year + list1d[1])
		return result

	def get_holiday_list_between_two_ymd_list(self, ymd1_l1d, ymd2_l1d):
		"""
		두날짜 사이의 공휴일을 리스트로 갖고온다
		단, 정보는 날짜만이 아닌 다른 정보들도 들어있는 리스트형태이다

		:param ymd1_l1d:
		:param ymd2_l1d:
		:return:
		"""
		utilx = xy_util.xy_util()

		start_dt_obj = self.change_ymd_list_to_dt_obj(ymd1_l1d)
		end_dt_obj = self.change_ymd_list_to_dt_obj(ymd2_l1d)
		before_replace = []  # 대체공휴일 적용전

		for one in self.varx["휴일"]:
			# 휴일은 대체공휴일하고 상관없이 정해진 날짜라 기간안에만 잇으면 그대로 사용한다
			# 날짜 객체로 만들어서 기준 날짜 안에있는지 보는것
			check_dt_obj = self.change_ymd_list_to_dt_obj(one[0:3])
			if start_dt_obj <= check_dt_obj <= end_dt_obj:
				before_replace.append(one)

		for one in self.varx["기간-양력휴일"]:
			# [2013, 9999], 10,  9, 1, "양", "",  "토일","한글날"],
			# 휴일과 다르게 기간이 있는 자료이기때문에 그것으로 확인
			solar_start_dt_obj = self.change_ymd_list_to_dt_obj([one[0][0], one[1], one[2]])
			solar_end_dt_obj = self.change_ymd_list_to_dt_obj([one[0][1], one[1], one[2]])
			overlap_period = self.get_overlap_period_for_two_dt_obj(start_dt_obj, end_dt_obj, solar_start_dt_obj, solar_end_dt_obj)
			if overlap_period:
				year1 = self.get_ymd_list_for_dt_obj(overlap_period[0])[0]
				year2 = self.get_ymd_list_for_dt_obj(overlap_period[1])[0]
				for year in range(int(year1), int(year2) + 1):
					dt_obj_7 = self.change_ymd_list_to_dt_obj([year, one[1], one[2]])
					if start_dt_obj <= dt_obj_7 <= end_dt_obj:
						temp = utilx.depcopy(one)
						temp[0] = year
						before_replace.append(temp)

		for one in self.varx["기간-음력휴일"]:
			# 음력기간은 원래 기간에 2년을 더 넓힌다
			# 1년만 넓히면, 1루 차이가 나는 부분도 있을수가 있어서, 2년으로 만든 것이다
			for year in range(ymd1_l1d[0] - 2, ymd2_l1d[0] + 3):
				if one[0][0] <= year <= one[0][1]:
					if one[2] != "말일":
						# 말일은 윤달의 마지막날이라 날짜를 정할수가없다
						# 그래서 그다음말에서 -1일을하는 것으로 한다
						dt_obj_8 = self.change_ymd_list_to_dt_obj([year, one[1], one[2]])
						dt_obj_8 = self.change_lunar_dt_obj_to_solar_dt_obj(dt_obj_8, False)
					else:
						dt_obj_8 = self.change_lunar_dt_obj_to_solar_dt_obj([year + 1, 1, 1], False)
						dt_obj_8 = self.shift_day_for_dt_obj(dt_obj_8, -1)

					if start_dt_obj <= dt_obj_8 <= end_dt_obj:
						ymd_l1d = self.change_dt_obj_to_ymd_list(dt_obj_8)
						temp = utilx.depcopy(one)
						temp[0] = int(ymd_l1d[0])
						temp[1] = int(ymd_l1d[1])
						temp[2] = int(ymd_l1d[2])
						before_replace.append(temp)

		# 마지막으로 대체공휴일을 체크하는 부분
		# 위에서는 그냥 전체를 양력으로 다 바꿔서 저장하기만 하는 것이다
		final = []
		all_dt_obj = []
		for one in before_replace:
			dt_obj_9 = self.change_ymd_list_to_dt_obj([one[0], one[1], one[2]])
			if one[6] == "일":
				dt_obj = self.shift_alt_holiday(all_dt_obj, dt_obj_9, [0])
				if start_dt_obj <= dt_obj <= end_dt_obj:
					ymd_l1d = self.change_dt_obj_to_ymd_list(dt_obj)
					temp = utilx.depcopy(one)
					temp[0] = int(ymd_l1d[0])
					temp[1] = int(ymd_l1d[1])
					temp[2] = int(ymd_l1d[2])
					final.append(temp)
					all_dt_obj.append(dt_obj)

			elif one[6] == "토일":
				dt_obj11 = self.shift_alt_holiday(all_dt_obj, dt_obj_9, [0, 6])
				if start_dt_obj <= dt_obj11 <= end_dt_obj:
					ymd_l1d = self.change_dt_obj_to_ymd_list(dt_obj11)
					temp = utilx.depcopy(one)
					temp[0] = int(ymd_l1d[0])
					temp[1] = int(ymd_l1d[1])
					temp[2] = int(ymd_l1d[2])
					final.append(temp)
					all_dt_obj.append(dt_obj11)
			else:
				if start_dt_obj <= dt_obj_9 <= end_dt_obj:
					final.append(one)
					all_dt_obj.append(dt_obj_9)
		return final

	def get_holiday_list_for_year(self, input_year):
		"""
		특정년도의 휴일을 돌려 줍니다

		:param input_year: 년
		:return:
		"""
		result = []
		temp = []
		for year in [input_year - 1, input_year, input_year + 1]:
			aaa = self.data_national_holiday_in_year(year, year)
			for one in aaa:
				bbb = self.check_holiday_on_year(year, one)
				for one in bbb:
					temp.append(one)
		# print(year, temp)

		for one in temp:
			if int(one[0]) == int(input_year):
				result.append(one)
		return result

	def get_hour_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		시 -----> 10

		:param input_time:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		return dt_obj.strftime('%I')

	def get_hour_for_now(self):
		"""
		시 -----> 10

		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["hour24"]

	def get_hour_set_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		시 -----> ['10', '22', 'PM']

		:param time_char:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["hour1"], all_dic["hour2"], all_dic["ampm"]]

	def get_hour_set_for_now(self):
		"""
		시 -----> ['10', '22', 'PM']

		:param time_char:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["hour12"], all_dic["hour24"], all_dic["ampm"]]

	def get_hour_set_for_utc(self, input_utc):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		시 -----> ['10', '22']

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["hour1"], all_dic["hour2"], all_dic["ampm"]]

	def get_information_for_dt_obj_as_dic(self, input_dt=""):
		"""
		입력된 시간에 대한 왠만한 모든 형식의 날짜 표현을 사전형식으로 돌려준다

		:param input_dt: datetime객체, 날짜 객체
		:return:
		"""
		if not input_dt:
			input_dt = self.get_dt_obj_for_now()
		elif type(input_dt) == type(123.45):
			input_dt = self.change_anytime_to_dt_obj(input_dt)

		result = {}
		# s는 short, e는 english, l은 long
		result["year2"] = input_dt.strftime('%y')  # 22
		result["year4"] = result["year"] = input_dt.strftime('%Y')  # 2023

		result["month2"] = result["mon"] = result["month"] = input_dt.strftime('%m')  # 01
		result["month_s"] = input_dt.strftime('%b')  # jan
		result["month_l"] = input_dt.strftime('%B')  # january

		result["day2"] = result["day"] = input_dt.strftime('%d')  # 01
		result["day3"] = result["yearday"] = input_dt.strftime('%j')  # 023, 365

		result["week1"] = result["week"] = result["weekno"] = input_dt.strftime('%w')  # 6
		result["week2"] = result["yearweekno"] = result["yearweek"] = input_dt.strftime('%W')  # 34, 1년중에 몇번째 주인지

		result["week_s"] = input_dt.strftime('%a')  # mon
		result["week_l"] = input_dt.strftime('%A')  # monday

		result["hour12"] = result["hour1"] = input_dt.strftime('%I')  # 1
		result["hour24"] = result["hour2"] = result["hour"] = input_dt.strftime('%H')  # 23

		result["ampm"] = input_dt.strftime('%p')
		result["min"] = input_dt.strftime('%M')
		result["sec"] = input_dt.strftime('%S')

		result["month3_eng"] = input_dt.strftime('%b')  # jan
		result["month_eng"] = input_dt.strftime('%B')  # january
		result["week3_eng"] = input_dt.strftime('%a')  # mon
		result["week_eng"] = input_dt.strftime('%A')  # monday

		result["dt_timestamp"] = input_dt.timestamp()
		result["timestamp"] = input_dt.timestamp()
		result["utc"] = input_dt.timestamp() - 1640995200

		result["ymd"] = result["yyyy-mm-dd"] = input_dt.strftime("%Y-%m-%d")
		result["ymdhms"] = result["yyyy-mm-dd-hh-mm-ss"] = input_dt.strftime("%Y-%m-%d-%H-%M-%S")
		result["sec_total"] = int(result["timestamp"])
		result["day_total"] = int(int(result["timestamp"]) / 86400)
		result["ymd_list"] = result["ymd"].split("-")
		result["ymdhms_list"] = result["ymdhms"].split("-")
		return result

	def get_information_for_input_time_as_dic(self, input_time=""):
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		result = self.get_information_for_dt_obj_as_dic(dt_obj)
		return result

	def get_last_day_for_ym_list(self, input_ym_list):
		"""
		양력날짜에서 월의 마지막날을 찾는것
		입력 : [2023, 05]
		출력 : [날짜객체, [1,31], 1, 31]

		:param input_ym_list: [년, 월]
		:return:
		"""
		date = datetime.datetime(year=input_ym_list[0], month=input_ym_list[1], day=1).date()
		monthrange = calendar.monthrange(date.year, date.month)
		last_day = calendar.monthrange(date.year, date.month)[1]
		return last_day

	def get_last_day_of_yyyymm_for_lunar(self, input_yyyy, input_mm):
		"""
		음력의 년도와 월을 주면, 마지막날을 돌려주는 것
		12월은 "말일"을 날짜를 확인하기 위한것

		:param input_yyyy:
		:param input_mm:
		:return:
		"""
		self.lunar_calendar.setLunarDate(int(input_yyyy), int(input_mm), 1, True)
		result = self.lunar_calendar.LUNAR_BIG_MONTH_DAY
		return result

	def get_max_year_for_datetime(self):
		"""
		datetime객체에서 사용가능한 최대의 년도를 알려주는 것
		:return:
		"""
		result = datetime.MAXYEAR
		return result

	def get_min_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		분 -----> ['07']

		:param input_time:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["min"]

	def get_min_for_utc(self, input_utc):
		"""
		입력값 : utc시간숫자, 1640995200.0 또는 ""
		분 -----> ['07']
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["min"]

	def get_minute_for_now(self):
		"""
		분 -> 07

		:param time_char:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["min"]

	def get_month_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		월 -----> 4
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["mon"]

	def get_month_set_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		월 -----> ['04', 'Apr', 'April']

		:param input_time:
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["mon2"], all_dic["mon3_eng"], all_dic["mon_eng"]]

	def get_month_set_for_now(self):
		"""
		월 -> ['04', 'Apr', 'April']
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["mon2"], all_dic["mon3_eng"], all_dic["mon_eng"]]

	def get_month_set_for_utc(self, input_utc=""):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		월 -----> ['04', Apr, April]
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["mon2"], all_dic["mon3_eng"], all_dic["mon_eng"]]

	def get_nea_random_date_between_two_dt_obj(self, dt_obj_1, dt_obj_2, nea):
		"""
		두 날짜사이의 n개의 랜덤한 날짜를 갖고오는것
		"""
		result = []
		nday = self.minus_two_date(dt_obj_1, dt_obj_2)
		random_list = random.sample(range(0, abs(int(nday)) + 1), nea)
		for one_no in random_list:
			start_dt_obj = self.change_anytime_to_dt_obj(dt_obj_1)
			changed_dt_obj = self.shift_day_for_dt_obj(start_dt_obj, one_no)
			yymmdd = self.change_dt_obj_to_yyyy_mm_dd(changed_dt_obj)
			result.append(yymmdd)
		return result

	def get_no_of_sunday_in_same_week_for_dt_obj(self, input_dt=""):
		"""
		날짜객체의 week_no_7을 알아내는것
		주의 7번째 요일인 일요일의 날짜를 돌려줍니다

		:param input_dt: datetime객체, 날짜 객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = input_dt.strftime('%w')  # 6
		return result

	def get_one_month_list_for_year_month(self, input_year, input_month):
		"""
		년과 월을 주면, 한달의 리스트를 알아내는것
		월요일부터 시작

		:param input_year:년
		:param input_month:월
		:return:
		"""
		result = []
		week_no = []
		date_obj = datetime.datetime(year=input_year, month=input_month, day=1).date()
		first_day_wwek_no = calendar.monthrange(date_obj.year, date_obj.month)[0]
		last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
		if first_day_wwek_no == 0:
			pass
		else:
			for no in range(first_day_wwek_no):
				week_no.append("")
		for num in range(1, int(last_day) + 1):
			if len(week_no) == 7:
				result.append(week_no)
				week_no = [num]
			else:
				week_no.append(num)
		if week_no:
			result.append(week_no)
		return result

	def get_overlap_period_for_two_dt_obj(self, dt1_start, dt1_end, dt2_start, dt2_end):
		"""
		2 dt_obj의 곂치는 기간을 알아내는 것이다

		:param dt1_start:
		:param dt1_end:
		:param dt2_start:
		:param dt2_end:
		:return:
		"""

		overlap_start = max(dt1_start, dt2_start)  # 겹치는 기간의 시작은 두 시작 시간 중 더 늦은 시간
		overlap_end = min(dt1_end, dt2_end)  # 겹치는 기간의 끝은 두 끝 시간 중 더 이른 시간
		if overlap_start < overlap_end:
			return (overlap_start, overlap_end)
		else:
			return None

	def get_period_as_month_n_day_between_two_date(self, date1, date2, month_days=30):
		"""
		2날짜사이의 기간을 몇개월 몇일로 계산하는 것
		1달은 30일로 계산한 것이다
		get_period_as_month_n_day_between_two_date("2024-10-01", "2024-08-15")

		:param date1:
		:param date2:
		:param month_days:
		:return:
		"""
		dt1 = self.change_any_text_time_to_dt_obj(date1)
		ts1 = self.change_dt_obj_to_utc(dt1)
		dt2 = self.change_any_text_time_to_dt_obj(date2)
		ts2 = self.change_dt_obj_to_utc(dt2)

		delta = int(ts1 - ts2)
		mon_ts = month_days * 24 * 60 * 60
		months = int(delta / mon_ts)
		days = int((delta - months * mon_ts) / (24 * 60 * 60))

		return [months, days]

	def get_sec_for_dt_obj(self, input_dt=""):
		"""
		시간객체를 초로 나타내는 자료형으로 만드는 것

		:param input_dt: datetime객체
		:return: [timestamp, 날짜에대한 초, 나머지초]
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_dt)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["sec"]

	def get_sec_for_input_time(self, input_time=""):
		"""

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["sec"]

	def get_sec_for_now(self):
		"""
		초 -----> 48

		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["sec"]

	def get_sec_for_utc(self, input_utc=""):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""
		초 -----> 48
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["sec"]

	def get_sec_set_for_dt_obj(self, input_dt=""):
		"""
		시간 객체를 초로 나타내는 자료형으로 만드는 것

		:param input_dt: datetime객체
		:return: [timestamp, 날짜에대한 초, 나머지초]
		"""
		input_dt = self.check_dt_obj(input_dt)
		timestamp = self.get_dt_timestamp_for_dt_obj(input_dt)
		day = int(timestamp / 86400)
		sec = int(timestamp) - day * 86400
		return [timestamp, day, sec]

	def get_start_year_for_datetime(self):
		"""
		datetime객체의 최소한의 년도를 알려주는 것

		:return:
		"""
		result = datetime.MINYEAR
		return result

	def get_text_time_for_dt_obj_as_input_format(self, input_dt="", input_format="%Y-%m-%d %H:%M:%S"):
		"""
		입력형식으로 되어있는 시간자료를 dt객체로 인식하도록 만드는 것이다
		dt = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")

		:param input_dt: datetime객체, 날짜 객체
		:param input_format:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		input_format = self.check_time_format(input_format)
		result = input_dt.strftime(input_format)
		return result

	def get_total_day_for_dt_obj(self, input_dt=""):
		"""
		total_day : 시간 객체를 날수로 계산
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = self.get_information_for_dt_obj_as_dic(input_dt)["day"]
		return result

	def get_utc_for_now(self):
		"""
		기본적으로 datetime은 utc와 같은것이라 보면 된다
		:return:
		"""
		result = datetime.datetime.utcnow()
		return result

	def get_week_list_by_nth_week_later(self, n_week_later, base_date=""):
		"""
		어느날짜를 기준으로 n주후의 일주일의 날짜를 갖고오는것

		:param n_week_later:
		:param base_date:
		:return:
		"""
		input_dt_obj = self.check_dt_obj(base_date)
		year, week_number, weekday = input_dt_obj.isocalendar()
		if weekday != 1:
			month_dt_obj = input_dt_obj + datetime.timedelta(days=-(weekday - 1))
		else:
			month_dt_obj = input_dt_obj
		week_dates = [(month_dt_obj + datetime.timedelta(days=i + n_week_later * 7)).strftime('%Y-%m-%d') for i in range(7)]
		return week_dates

	def get_week_list_by_year_weekno(self, year, weekno):
		"""
		년도와 주번호를 넣으면, 주의 리스트를 돌려주는 것
		:param year:
		:param week:
		:return:
		"""
		# 년도와 주번호를 넣으면, 주의 리스트를 돌려주는 것
		# 주의 첫 번째 날(월요일)을 계산합니다
		first_day_of_year = datetime.datetime(year, 1, 1)
		year, week_number, weekday = first_day_of_year.isocalendar()
		# 그주의 첫번째 월요일의 객체
		if weekday != 1:
			month_dt_obj = first_day_of_year + datetime.timedelta(days=-(weekday - 1))
		else:
			month_dt_obj = first_day_of_year
		if week_number == 0:
			month_dt_obj = month_dt_obj + datetime.timedelta(days=7)
		week_dates = [(month_dt_obj + datetime.timedelta(days=i + (weekno - 1) * 7)).strftime('%Y-%m-%d') for i in range(7)]
		return week_dates

	def get_week_list_for_dt_obj(self, input_dt=""):
		"""
		월요일부터 시작하는 7 개의 날짜를 돌려준다
		2023-07-24 : f'{year} {yearweekno} 0' => f'{year} {yearweekno} 1'

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		dic_data = self.get_information_for_dt_obj_as_dic(input_dt)
		str_datetime = f'{dic_data["year"]} {dic_data["yearweek"]} 1'  # 1은 월요일 이다

		# 문자열형태로 입력받아서, 시간객체로 만들어 주는것
		startdate = datetime.datetime.strptime(str_datetime, '%Y %W %w')
		dates = []
		for i in range(7):
			day = startdate + datetime.timedelta(days=i)
			dates.append(day.strftime("%Y-%m-%d"))
		return dates

	def get_week_list_for_input_time(self, input_time=""):
		input_dt_obj = self.check_input_time(input_time)
		year, week_number, weekday = input_dt_obj.isocalendar()
		if weekday != 1:
			month_dt_obj = input_dt_obj + datetime.timedelta(days=-(weekday - 1))
		else:
			month_dt_obj = input_dt_obj
		week_dates = []
		[(month_dt_obj + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
		return week_dates

	def get_week_list_for_this_week(self, input_time=""):
		"""
		이번주에 대한 날짜 리스트

		:param input_time:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		# 오늘의 요일을 가져옵니다. (월요일=0, 일요일=6)
		today_weekday = dt_obj.weekday()
		# 일요일을 기준으로 이번 주의 시작 날짜를 계산합니다.
		# 일요일은 6이므로, 오늘의 요일에 1을 더한 후 7로 나눈 나머지를 빼줍니다.
		start_of_week = dt_obj - datetime.timedelta(days=(today_weekday + 1) % 7)
		# 이번 주의 7 일을 리스트에 저장합니다
		week_dates = [(start_of_week + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
		return week_dates

	def get_week_set_for_input_time(self, input_time=""):
		"""
		주 -----> ['5', '13', 'Fri', 'Friday']
		week1 : 0~6 (0:일요일)까지의 요일에 대한 숫자, 일요일 : 0,  토요일 :6
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["week1"], all_dic["week2"], all_dic["week_s"], all_dic["week_l"]]

	def get_week_set_for_now(self):
		"""
		주 -----> ['5', '13', 'Fri', 'Friday']

		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["week1"], all_dic["week2"], all_dic["week_s"], all_dic["week_l"]]

	def get_weekno_for_1st_day_of_ym_list(self, input_ym_list):
		"""
		week_no : 0~6 (0:일요일)까지의 요일에 대한 숫자
		입력한 월의 1일이 무슨요일인지 알아 내는것
		[2023, 05] => 0, 월요일

		:param input_ym_list: [년, 월]
		:return:
		"""
		date = datetime.datetime(year=input_ym_list[0], month=input_ym_list[1], day=1).date()
		monthrange = calendar.monthrange(date.year, date.month)
		first_day = calendar.monthrange(date.year, date.month)[0]
		return first_day

	def get_weekno_for_dt_obj(self, input_dt=""):
		"""
		week_no : 0~6까지의 요일에 대한 숫자, 일요일 : 0,  토요일 :6
		"""
		input_dt = self.check_dt_obj(input_dt)
		result = input_dt.strftime('%w')
		return result

	def get_weekno_for_utc(self, input_utc=""):
		"""
		시간이 들어온면
		입력값 : 년도, 위크번호
		한 주의 시작은 '월'요일 부터이다
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["weekno"]

	def get_weekno_set_for_dt_obj(self, input_dt=""):
		"""
		datetime는 utc local
		week_no : 0~6 (0:일요일)까지의 요일에 대한 숫자, 일요일 : 0,  토요일 :6

		:param input_dt: datetime객체, 날짜 객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_dt)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["week1"], all_dic["week2"], all_dic["week_s"], all_dic["week_l"]]

	def get_year_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		년 -----> ['2002']

		:param input_time:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["year"]

	def get_year_for_now(self):
		"""
		년 -----> 2002
		"""
		dt_obj = self.check_input_time("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["year"]

	def get_year_for_utc(self, input_utc):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		년 -----> ['22', '2022']
		닞은숫자 -> 많은글자 순으로 정리

		:param input_utc: utc 시간객체
		:return:
		"""
		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["year"]

	def get_year_set_for_input_time(self, input_time=""):
		"""
		입력한 시간(없을 때는 지금시간)을 아래의 형태에 대해서 알려주는 것
		년 -----> ['02', '2002']

		:param time_char:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return [all_dic["year1"], all_dic["year2"]]

	def get_yearweekno_for_dt_obj(self, input_dt=""):
		"""
		dt객체에 대한 한해의 몇번째 주인지를 알아낸다

		:param input_dt: datetime객체, 날짜 객체
		:return:
		"""
		dt_obj = self.check_input_time(input_dt)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["yearweekno"]

	def get_yearweekno_for_now(self):
		"""
		yearweekno : 1년에서 몇번째 주인지 아는것
		입력한날의 week 번호를	계산
		입력값 : 날짜

		:return:
		"""
		dt_obj = self.check_input_time("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["yearweekno"]

	def get_yearweekno_for_today(self):
		"""
		오늘 날짜의 weekno를 갖고온다
		:return:
		"""
		dt_obj = self.check_input_time("")
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["yearweekno"]

	def get_yearweekno_for_utc(self, input_time=""):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		시간이 들어온면
		입력값 : 년도, 위크번호
		한 주의 시작은 '월'요일 부터이다

		:param input_time: 문자열로된 시간
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		all_dic = self.get_information_for_dt_obj_as_dic(dt_obj)
		return all_dic["yearweekno"]

	def get_yearweekno_for_ymd_list(self, input_date=""):
		"""
		입력한날의 week 번호를 계산
		입력값 : 날짜
		"""

		if input_date == "":
			today = self.get_yyyy_mm_dd_for_today()
			# print(today)
			year, month, day = today.split("-")
			dt_obj = self.check_input_time([year, month, day])
		else:
			dt_obj = self.change_anytime_to_dt_obj(input_date)

		result = int(dt_obj.strftime('%W'))
		return result

	def get_ymd_dash_for_today(self):
		"""
		오늘 날짜를 yyyy-mm-dd형식으로 돌려준다
		지금의 날짜를 돌려준다
		입력값 : 없음
		출력값 : 2022-03-01,
		"""
		just_now = arrow.now()
		result = just_now.format("YYYY-MM-DD")
		return result

	def get_ymd_dash_for_utc(self, input_utc):
		"""
		utc를 2023-2-2형태로 돌려주는 것

		:param input_utc: utc 시간객체
		:return:
		"""
		input_utc = self.check_input_utc(input_utc)
		result = time.strftime('%Y-%m-%d', input_utc)
		return result

	def get_ymd_list_for_dt_obj(self, input_dt=""):
		"""
		datetime는 utc local
		datetime객체 => [년, 월, 일]

		:param input_dt: datetime객체
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		temp = input_dt.strftime("%Y-%m-%d")
		result = temp.split("-")
		return result

	def get_ymd_list_for_now_by_local(self):
		"""
		utc시간이 아니고 현재 지역적인 시간으로 변경하는 것
		3.6버전이후에 나타나는 astimezone를 사용하면 알아서 적용되는 것이다
		"""
		dt_obj = datetime.datetime.now()
		changed_dt_obj = dt_obj.astimezone()
		result = self.get_ymd_list_for_dt_obj(changed_dt_obj)
		return result

	def get_ymd_list_for_text_time(self, input_anytime):
		"""
		datetime는 utc local
		datetime객체 => [년, 월, 일]

		:param input_dt: datetime객체
		:return:
		"""
		dt_obj = self.change_anytime_to_dt_obj(input_anytime)
		temp = dt_obj.strftime("%Y-%m-%d")
		result = temp.split("-")
		return result

	def get_ymd_list_for_today(self):
		"""
		오늘날자를 yyyy-mm-dd형식으로 만들어주는 것

		:return:
		"""
		dt_obj = self.get_dt_obj_for_today()
		all_dic = self.get_information_for_input_time_as_dic(dt_obj)
		return all_dic["ymd_list"]

	def get_ymd_list_for_utc(self, input_utc):
		"""

		:param input_utc: utc 시간객체
		:return:
		"""

		dt_obj = self.change_utc_to_dt_obj(input_utc)
		all_dic = self.get_information_for_input_time_as_dic(dt_obj)
		return all_dic["ymd_list"]

	def get_ymdhms_list_for_dt_obj(self, input_dt=""):
		"""
		datetime는 utc local
		datetime객체 => [년, 월, 일, 시, 분, 초]

		:param input_dt: datetime객체
		:return:
		"""
		dt_obj = self.check_dt_obj(input_dt)
		all_dic = self.get_information_for_input_time_as_dic(dt_obj)
		return all_dic["ymdhms_list"]

	def get_ymdhms_list_for_now_by_local(self):
		"""
		지금시간을 ymdhms_list형태로 알려주는 것
		:return:
		"""
		dt_obj = datetime.datetime.now()
		changed_dt_obj = dt_obj.astimezone()
		result = self.get_ymdhms_list_for_dt_obj(changed_dt_obj)
		return result

	def get_yyyy_mm_dd_for_now(self):
		"""
		오늘 날짜를 yyyy-mm-dd형식으로 돌려준다
		지금의 날짜를 돌려준다
		입력값 : 없음
		출력값 : 2022-03-01,

		:return:
		"""
		dt_obj = self.check_input_time("")
		result = dt_obj.strftime("%Y-%m-%d")
		return result

	def get_yyyy_mm_dd_for_today(self):
		"""
		오늘날자를 yyyy-mm-dd형식으로 만들어주는 것

		:return:
		"""
		dt_obj = self.check_input_time("")
		result = dt_obj.strftime("%Y-%m-%d")
		return result

	def get_yyyymmdd_for_timestamp(self):
		"""
		화일이름으로 사용하는 목적으로 만드는 것입니다
		예를들어 : 20241101_2345678

		:return:
		"""

		timestamp = self.get_dt_timestamp()
		str_timestamp = str(timestamp * 1000000)[-8:-2]
		dt_obj = datetime.datetime.now()
		temp = self.get_information_for_dt_obj_as_dic(dt_obj)["ymd_list"]
		result = str(temp[0]) + str(temp[1]) + str(temp[2]) + "_" + str_timestamp

		return result

	def intersect_two_time_range(self, input_dt2_11, input_dt2_12, input_dt2_21, input_dt2_22):
		"""
		겼치는 시간 부분을 리스트로 돌려줌

		:param input_dt2_11:
		:param input_dt2_12:
		:param input_dt2_21:
		:param input_dt2_22:
		:return:
		"""

		start_1 = min(input_dt2_11, input_dt2_12)
		end_1 = max(input_dt2_11, input_dt2_12)
		start_2 = min(input_dt2_21, input_dt2_22)
		end_2 = max(input_dt2_21, input_dt2_22)
		if end_2 < start_1 or start_2 < end_1:
			# 겪치는 부분이 없는것
			result = False
		else:
			temp_1 = min(start_1, start_2)
			temp_2 = max(end_1, end_2)
			result = [temp_1, temp_2]
		return result

	def is_same_ymd_for_two_dt_obj(self, input_dt2_1, input_dt2_2):
		"""
		겼치는 시간 부분을 리스트로 돌려줌

		:param input_dt2_1:
		:param input_dt2_2:
		:return:
		"""
		ymd_list_1 = self.get_ymd_list_for_dt_obj(input_dt2_1)
		ymd_list_2 = self.get_ymd_list_for_dt_obj(input_dt2_2)
		result = False
		if ymd_list_1 == ymd_list_2:
			result = True
		return result

	def join_list_with_char(self, input_list, input_char):
		"""
		입력리스트자료를 연결문자를 이용해서 하나의 문자로 만들어 주는 것

		:param input_list:
		:param input_char:
		:return:
		"""
		result = ""
		for one in input_list[:-1]:
			result = result + str(one) + input_char
		result = result + str(input_list[-1])
		return result

	def make_dic_time(self, input_dic):
		"""
		ymdhms의 사전형식으로 만드는 것
		:param input_dic:
		:return:
		"""
		result = {"yea": 0, "mon": 0, "day": 0, "hou": 0, "min": 0, "sec": 0}
		result.update(input_dic)
		return result

	def make_nea_time_list_from_hms_list(self, start_hms_list, step=30, cycle=20):
		"""
		시작과 종료시간을 입력하면, 30분간격으로 시간목록을 자동으로 생성시키는것

		:param start_hms_list: [시, 분, 초]
		:param step:
		:param cycle:
		:return:
		"""
		result = []
		hour, min, sec = start_hms_list
		result.append([hour, min, sec])
		for one in range(cycle):
			min = min + step
			over_min, min = divmod(min, 60)
			if over_min > 0:
				hour = hour + over_min
			hour = divmod(hour, 24)[1]
			result.append([hour, min, sec])
		return result

	def make_text_style_from_two_hms_list(self, hms_list_1, hms_list_2):
		"""
		09:20 ~ 10:21로 나타내는 것

		:param hms_list_1: [시, 분, 초]
		:param hms_list_2: [시, 분, 초]
		:return:
		"""
		h_1, m_1, s_1 = hms_list_1
		h_2, m_2, s_2 = hms_list_2
		result = f"{h_1:0>2}:{m_1:0>2} ~ {h_2:0>2}:{m_2:0>2}"
		return result

	def make_time_list_between_2_hms_list_by_step(self, start_hms_list, end_hms_list, step=30):
		"""
		시작과 종료시간을 입력하면, 30분간격으로 시간목록을 자동으로 생성시키는것

		:param start_hms_list: [시, 분, 초]
		:param end_hms_list: [시, 분, 초]
		:param step:
		:return:
		"""
		result = []
		hour, min, sec = start_hms_list
		hour_end, min_end, sec_end = end_hms_list
		result.append([hour, min, sec])
		while 1:
			min = min + step
			over_min, min = divmod(min, 60)
			if over_min > 0:
				hour = hour + over_min
			hour = divmod(hour, 24)[1]
			if int(hour) * 60 + int(min) > int(hour_end) * 60 + int(min_end):
				break
			result.append([hour, min, sec])
		return result

	def make_two_digit(self, input_value):
		"""
		2자리 숫자로 만들어 주는 것

		:param input_value:
		:return:
		"""
		input_value = str(input_value)
		if len(input_value) == 1:
			result = "0" + input_value
		else:
			result = input_value
		return result

	def make_unique_nea_hms_list(self, input_nea):
		"""
		중복되지 않는 n개의 hms_list 를 만드는것

		:param input_nea:
		:return:
		"""
		utilx = xy_util.xy_util()
		result = []
		one_day_sec = 60 * 60 * 24
		l1d = utilx.make_unique_random_list_between_two_int(0, one_day_sec, input_nea)
		for one in l1d:
			temp = self.change_sec_to_hms_list(one)
			result.append(temp)
		return result

	def minus_two_date(self, input_date1, input_date2):
		"""
		두날짜의 빼기

		:param input_date1: 일반적으로 사용하는 날짜를 나타내는 문자나 리스트
		:param input_date2: 일반적으로 사용하는 날짜를 나타내는 문자나 리스트
		:return:
		"""
		start_timestampl, start_dayl, start_secl = self.get_sec_set_for_dt_obj(input_date1)
		start_timestamp2, start_day2, start_sec2 = self.get_sec_set_for_dt_obj(input_date2)
		result = abs((float(start_timestampl) - float(start_timestamp2)) / (60 * 60 * 24))
		return result

	def minus_two_date_2(self, date_1, date_2):
		"""
		두날자의 빼기

		:param date_1:
		:param date_2:
		:return:
		"""
		time_big = self.check_datetime(date_1)
		time_small = self.check_datetime(date_2)
		if time_big.lt_utc > time_small.lt_utc:
			pass
		else:
			time_big, time_small = time_small, time_big
		time_big.last_day = self.get_month_range_for_ym_list(time_big.year, time_big.month)[3]
		time_small.last_day = self.get_month_range_for_ym_list(time_small.year, time_small.month)[3]

		delta_year = abs(time_big.year - time_small.year)
		delta_day = int(abs(time_big.lt_utc - time_small.lt_utc) / (24 * 60 * 60))
		# 실제 1 년의 차이는 365 일 5 시간 48 분 46초 + 0.5초이다 (2 년에 1 번씩 윤초를 실시》
		actual_delta_year = int(abs(time_big.lt_utc - time_small.lt_utc) / (31556926 + 0.5))
		delta_month = abs((time_big.year * 12 + time_big.month) - (time_small.year * 12 + time_small.month))
		if time_big.day > time_small.day:
			actual_delta_month = delta_month - 1
		else:
			actual_delta_month = delta_month
		actual_delta_day = delta_day
		return [delta_year, delta_month, delta_day, actual_delta_year, actual_delta_month, actual_delta_day]

	def minus_two_dt_obj(self, input_dt1, input_dt2):
		"""
		두날짜의 빼기

		:param input_dt1: datetime객체
		:param input_dt2: datetime객체
		:return:
		"""

		yr_ct = 365 * 24 * 60 * 60  # 31536000
		day_ct = 24 * 60 * 60  # 86400
		hour_ct = 60 * 60  # 3600
		minute_ct = 60

		result = {}
		ccc = abs(input_dt1 - input_dt2)

		result["original"] = ccc
		result["total_seconds"] = total_sec = ccc.total_seconds()

		result["year"] = int(total_sec / yr_ct)
		changed_total_sec = total_sec - int(total_sec / yr_ct) * yr_ct

		result["day"] = int(changed_total_sec / day_ct)
		changed_total_sec = changed_total_sec - int(changed_total_sec / day_ct) * day_ct

		result["hour"] = int(changed_total_sec / hour_ct)
		changed_total_sec = changed_total_sec - int(changed_total_sec / hour_ct) * hour_ct

		result["minute"] = int(changed_total_sec / minute_ct)
		changed_total_sec = changed_total_sec - int(changed_total_sec / minute_ct) * minute_ct

		result["second"] = int(changed_total_sec)
		changed_total_sec = changed_total_sec - int(changed_total_sec)

		result["remain"] = changed_total_sec
		return result

	def minus_two_hms_list(self, hms_list_1, hms_list_2):
		"""
		2개의 시분초리스트를 빼기 한다

		:param hms_list_1: [시, 분, 초]
		:param hms_list_2: [시, 분, 초]
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(hms_list_1)
		sec_2 = self.change_hms_list_to_sec(hms_list_2)
		result = self.change_sec_to_dhms_list(abs(sec_1 - sec_2))
		return result

	def mix_ymd_list_and_connect_char(self, ymd_list, connect_char="-"):
		"""
		입력리스트자료를 연결문자를 이용해서 하나의 문자로 만들어 주는 것

		:param ymd_list:
		:param connect_char:
		:return:
		"""
		result = ymd_list[0] + connect_char + ymd_list[1] + connect_char + ymd_list[2]
		return result

	def multiple_two_hms_list(self, hms_list_1, hms_list_2, times=1):
		"""
		2기간 사이의 기간을 몇배를 곱하기로 내는것

		:param hms_list_1: [시, 분, 초]
		:param hms_list_2: [시, 분, 초]
		:param times:
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(hms_list_1)
		sec_2 = self.change_hms_list_to_sec(hms_list_2)
		result = self.change_sec_to_dhms_list(abs(sec_1 - sec_2) * times)
		return result

	def overlap_area_for_two_dt_obj(self, input_dt2_11, input_dt2_12):
		"""
		겹치는 시간 부분을 리스트로 돌려줌

		:param input_dt2_11:
		:param input_dt2_12:
		:return:
		"""
		start_dt_obj = min(input_dt2_11, input_dt2_12)
		end_dt_obj = max(input_dt2_11, input_dt2_12)
		start_timestamp, start_day, start_sec = self.get_sec_set_for_dt_obj(start_dt_obj)
		end_timestamp, end_day, end_sec = self.get_sec_set_for_dt_obj(end_dt_obj)
		differ_day = end_day - start_day
		if start_day == end_day:
			result = [start_sec, end_sec, None, None, 0]
		else:
			result = [start_sec, 86400, 1, end_sec, differ_day]
		return result

	def overtime(self):
		"""
		[시작시간, 끝시간, 일당몇배]

		:return:
		"""
		self.ol_common["common"] = [["0000", "0500", 1], ["0505", "0606", 1.2]]
		self.ol_common["company"] = ["0708"]

	def plus_dt_obj_and_hms_list(self, input_dt, hms_list_2):
		"""
		앞의시간에서 뒤의시간을 더하는데, -로 넣으면 뻘샘도 된다

		:param input_dt: datetime객체
		:param hms_list_2: [시, 분, 초]
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		sec_1 = self.get_dt_timestamp_for_dt_obj(input_dt)
		sec_2 = self.change_hms_list_to_sec(hms_list_2)
		temp = sec_1 + sec_2
		result = self.change_sec_to_hms_list(temp)
		return result

	def plus_two_hms_list(self, hms_list_1, hms_list_2):
		"""
		앞의시간에서 뒤의시간을 더하는데, -로 넣으면 뻘샘도 된다

		:param hms_list_1: [시, 분, 초]
		:param hms_list_2: [시, 분, 초]
		:return:
		"""
		sec_1 = self.change_hms_list_to_sec(hms_list_1)
		sec_2 = self.change_hms_list_to_sec(hms_list_2)
		result = self.change_sec_to_hms_list(sec_1 + sec_2)
		return result

	def read_no_only(self, input_text):
		"""
		입력텍스트에서 숫자만 분리해서 만든다

		:param input_text:
		:return:
		"""

		result = []
		temp = ""
		for one in input_text:
			if one in "1234567890" and temp:
				temp = temp + one
			elif one in "1234567890" and not temp:
				temp = one
			elif not one in "1234567890" and temp:
				result.append(temp)
				temp = ""
			elif not one in "1234567890" and not temp:
				pass
		return result

	def read_today_value(self, time_char=time.localtime(time.time())):
		"""
		종합 -----> ['04/05/02', '22:07:48', '04/05/02 22:07:48','2002-04-05']
		040621 : 이름을 변경 (total -> today)
		"""
		aaa = str(time.strftime('%c', time_char)).split()
		total_dash = time.strftime('%Y', time_char) + "-" + time.strftime('%m', time_char) + "-" + time.strftime('%d', time_char)
		return [aaa[0], aaa[1], time.strftime('%c', time_char), total_dash]

	def replace_dt_obj_by_dic_time(self, input_dt2, input_dic):
		"""
		datetime.replace(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute,
		second=self.second, microsecond=self.microsecond, tzinfo=self.tzinfo, fold=0)
		입력된 시간의 특정 단위를 바꿀수있다
		즉, 모든 년을 2002로 바꿀수도 있다는 것이다

		:param input_dt2: 날짜 객체
		:param input_dic:
		:return:
		"""
		new_dt_obj = input_dt2.replace(input_dic)
		return new_dt_obj

	def replace_holiday_for_sunday_old(self, input_value):
		"""
		대체공휴일의 날짜를 확인하는 것이다
		input_value : [2009, 5, 5, 5, 5, '양', 1, '', '어린이날']
		[시작일], [끝나는날],[월, 일, 음/양, 몇일간, 윤달여부],[요일 - 대체적용일], [설명]

		:param input_value:
		:return:
		"""
		holiday_replace = [
			[[19590327, 19601230], ["all"], [6], ["대체공휴일제도"]],  # 모든 공휴일에 대해서 대체공휴일 적용(일요일)
			[[19890301, 19901130], ["all"], [6], ["대체공휴일제도"]],  # 모든 공휴일에 대해서 대체공휴일 적용(일요일)

			[[20131105, 99991231], [12, "말일", "음", 1, "윤달"], [6], ["설날", "대체공휴일제도"]],
			[[20131105, 99991231], [1, 1, "음", 2, "평달"], [6], ["신정", "대체공휴일제도"]],
			[[20131105, 99991231], [5, 5, "양", 1, ""], [5, 6], ["어린이날", "대체공휴일제도"]],  # 토/일요일
			[[20131105, 99991231], [8, 14, "음", 3, "평달"], [6], ["추석", "대체공휴일제도"]],

			[[20210715, 99991231], [3, 1, "양", 1, ""], [6], ["31절", "대체공휴일제도"]],
			[[20210715, 99991231], [10, 3, "양", 1, ""], [6], ["개천절", "대체공휴일제도"]],
			[[20210715, 99991231], [10, 9, "양", 1, ""], [6], ["한글날", "대체공휴일제도"]],

			[[20230504, 99991231], [12, 25, "양", 1, ""], [6], ["기독탄신일", "대체공휴일제도"]],
			[[20230504, 99991231], [4, 8, "음", 1, "평달"], [6], ["부처님오신날", "대체공휴일제도"]],
		]

		result = []
		dt_obj = self.change_ymd_list_to_dt_obj(input_value[0:3])
		week_no_7 = self.get_weekno_set_for_dt_obj(dt_obj[0])
		day_no = int(input_value[0]) * 10000 + int(input_value[1]) * 100 + int(input_value[2])

		for list1d in holiday_replace:
			change_day = False
			if list1d[0][0] <= day_no and list1d[0][1] >= day_no:
				if list1d[1][0] == "all" and week_no_7 in list1d[3]:
					# 대체휴일적용대상임
					change_day = True
				elif input_value[-1] == list1d[-1][0] and week_no_7 in list1d[3]:
					change_day = True

			if change_day:
				# print("대체공휴일 적용 =====> ")
				new_dt_obj = dt_obj + datetime.timedelta(days=1)
				new_ymd_list = self.get_ymd_list_for_dt_obj(new_dt_obj)
				result = new_ymd_list + input_value[3:] + ["대체공휴일적용", ]

		return result

	def roundup_hms_list(self, hms_list, base="min", condition="무조건"):
		"""
		시분초를 기준으로 그 윗부분을 반올림하는 것

		:param hms_list: [시, 분, 초]
		:param base:
		:param condition:
		:return:
		"""
		if base == "min":
			if condition == "무조건" and (hms_list[1] > 0 or hms_list[2] > 0):
				hms_list[0] = hms_list[0] + 1
			elif condition == "무조건" and hms_list[1] == 0 and hms_list[2] == 0:
				pass
			elif condition != "무조건" and (hms_list[1] > 0 or hms_list[2] > 0):
				if hms_list[2] >= 30: hms_list[1] = hms_list[1] + 1
				if hms_list[1] >= 30: hms_list[0] = hms_list[0] + 1
			elif condition != "무조건" and hms_list[1] == 0 and hms_list[2] == 0:
				pass
			result = [hms_list[0], 0, 0]
		elif base == "sec":
			if condition == "무조건" and hms_list[2] > 0:
				mok, namuji = divmod(hms_list[1] + 1, 60)
				result = [hms_list[0] + mok, namuji, 0]
			elif condition == "무조건" and hms_list[2] == 0:
				result = [hms_list[0], hms_list[1], 0]
			elif condition != "무조건" and hms_list[2] > 0:
				if hms_list[2] > 30: hms_list[2] = hms_list[2] + 1
				mok, namuji = divmod(hms_list[2], 60)
				result = [hms_list[0] + mok, namuji, 0]
			elif condition != "무조건" and hms_list[2] == 0:
				result = [hms_list[0], hms_list[1], 0]
		else:
			result = "error"
		return result

	def set_format_for_utc(self, input_utc, input_format):
		"""
		utc : utc의 timestamp, utc시간숫자, 1640995200.0 또는 ""

		:param input_utc: utc 시간객체
		:param input_format:
		:return:
		"""
		input_utc = self.check_input_utc(input_utc)
		result = time.strftime(input_format, input_utc)
		return result

	def shift_alt_holiday(self, dt_obj_set, base_dt_obj, week_no_list):
		"""
		대체공휴일이 있을때 그것을 적용하기 위한 것

		:param dt_obj_set:
		:param base_dt_obj:
		:param week_no_list:
		:return:
		"""
		aa = self.get_weekno_set_for_dt_obj(base_dt_obj)
		if int(aa[0]) in week_no_list and base_dt_obj in dt_obj_set:
			base_dt_obj = self.shift_day_for_dt_obj(base_dt_obj, 1)
			self.shift_alt_holiday(dt_obj_set, base_dt_obj, week_no_list)
		else:
			return base_dt_obj

	def shift_day_for_dt_obj(self, dt_obj, input_no):
		"""
		날짜를 이동

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		dt_obj = self.check_dt_obj(dt_obj)
		new_dt_obj = dt_obj + datetime.timedelta(days=input_no)
		return new_dt_obj

	def shift_day_for_ymd_list(self, ymd_list="", input_no=0):
		"""
		입력한 날짜리스트를 기준으로 날을 이동시키는것
		아무것도 입력하지 않으면 현재 시간
		입력값 : [2022, 03, 02]
		출력값 : 2022-01-01

		:param ymd_list: [년, 월, 일]
		:param input_no:
		:return:
		"""
		dt_obj = self.change_ymd_list_to_dt_obj(ymd_list)
		changed_dt_obj = dt_obj + datetime.timedelta(days=int(input_no))
		result = self.get_ymd_list_for_dt_obj(changed_dt_obj)
		return result

	def shift_dt_obj_with_option(self, input_dt, **option):
		"""
		datetime객체를 입력하는 형태에따라서 이동시키는 것

		:param input_dt: datetime객체
		:param option:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)

		if "year" in option.keys(): input_dt = self.shift_year_for_dt_obj(input_dt, option["year"])

		if "mon" in option.keys(): input_dt = self.shift_month_for_dt_obj(input_dt, option["mon"])
		if "month" in option.keys(): input_dt = self.shift_month_for_dt_obj(input_dt, option["month"])

		if "day" in option.keys(): input_dt = input_dt + datetime.timedelta(days=int(option["day"]))
		if "hour" in option.keys(): input_dt = input_dt + datetime.timedelta(hours=int(option["hour"]))

		if "min" in option.keys(): input_dt = input_dt + datetime.timedelta(minutes=option["min"])
		if "minute" in option.keys(): input_dt = input_dt + datetime.timedelta(minutes=int(option["minute"]))

		if "sec" in option.keys(): input_dt = input_dt + datetime.timedelta(seconds=int(option["sec"]))
		if "second" in option.keys(): input_dt = input_dt + datetime.timedelta(seconds=int(option["second"]))

		return input_dt

	def shift_hour_for_dt_obj(self, input_dt="", input_no=0):
		"""
		시간을 이동

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		new_dt_obj = input_dt + datetime.timedelta(hours=input_no)
		return new_dt_obj

	def shift_min_for_dt_obj(self, input_dt="", input_no=0):
		"""
		분을 이동

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		new_dt_obj = input_dt + datetime.timedelta(minutes=input_no)
		return new_dt_obj

	def shift_month_for_dt_obj(self, input_dt, input_no):
		"""
		시간이동 : 입력시간에 대해서 n번째 월로 이동

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		original_mon = input_dt.month
		original_year = input_dt.year

		delta_year, delta_month = divmod(input_no, 12)

		if original_mon <= delta_month * -1 and 0 > delta_month:
			original_mon = original_mon + 12
			original_year = original_year - 1

		new_month = original_mon + delta_month
		new_year = original_year + delta_year

		delta_year_1, delta_month_1 = divmod(new_month, 12)
		final_new_year = original_year + delta_year_1

		new_dt_obj = input_dt.replace(year=final_new_year)
		new_dt_obj = new_dt_obj.replace(month=delta_month_1)
		return new_dt_obj

	def shift_month_for_text_time(self, input_time, input_no):
		"""
		기준날짜에서 몇번째 월로 이동시키는것

		:param input_time: 문자열로된 날짜나 시간
		:param input_no:
		:return:
		"""
		dt_obj = self.check_input_time(input_time)
		changed_dt_obj = self.shift_month_for_dt_obj(dt_obj, input_no)
		result = self.get_ymd_list_for_dt_obj(changed_dt_obj)
		return result

	def shift_month_for_ymd_list(self, ymd_list="", input_month=0):
		"""
		기준날짜에서 월을 이동시키는것

		:param ymd_list: 년월일의 리스트를 넣는다
		:param input_month: 월
		:return:
		"""

		dt_obj = self.check_input_time(ymd_list)
		changed_dt_obj = self.shift_month_for_dt_obj(dt_obj, input_month)
		result = self.get_ymd_list_for_dt_obj(changed_dt_obj)
		return result

	def shift_sec_for_dt_obj(self, input_dt="", input_sec=""):
		"""
		날짜객체를 초단위로 이동시키는 것
		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		dt_obj = self.check_dt_obj(input_dt)
		changed_dt_obj = self.shift_sec_for_dt_obj(dt_obj, input_sec)
		return changed_dt_obj

	def shift_week_for_dt_obj(self, input_dt, input_no):
		"""
		입력시간을 기준으로 n번째 주로 이동

		shift : 일부분만 변경
		move : 전체가 변경

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""

		dt_obj = self.check_dt_obj(input_dt)
		changed_dt_obj = self.shift_week_for_dt_obj(dt_obj, input_no)
		return changed_dt_obj

	def shift_year_for_dt_obj(self, input_dt="", input_no=""):
		"""
		입력시간을 기준으로 n번째 년으로 이동
		년도는 timedelta가 없어서 년도 자체랄 바꾸는 방법을 사용하는 것이다

		shift : 일부분만 변경
		move : 전체가 변경

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		dt_obj = self.check_dt_obj(input_dt)
		changed_dt_obj = self.shift_year_for_dt_obj(dt_obj, input_no)
		return changed_dt_obj

	def shift_year_for_ymd_list(self, ymd_list="", input_year=0):
		"""
		기준날짜에서 년을 이동시키는것
		입력형태 : [2022, 3, 1]

		:param ymd_list: [년, 월, 일] [2022, 3, 1]
		:param input_year: 년
		:return:
		"""
		dt_obj = self.check_input_time(ymd_list)
		dt_obj_changed = self.shift_year_for_dt_obj(dt_obj, input_year)
		result = self.get_ymd_list_for_dt_obj(dt_obj_changed)
		return result

	def shift_ymd_list_for_ymd_list(self, ymd_list_1, ymd_list_2):
		"""
		ymd_list형식의 입력값을 3년 2개월 29일을 이동시킬때 사용하는것

		:param ymd_list_1: [년, 월, 일]
		:param ymd_list_2: [년, 월, 일]
		:return:
		"""
		dt_obj = self.change_ymd_list_to_dt_obj(ymd_list_1)
		changed_dt_obj = self.shift_day_for_dt_obj(dt_obj, ymd_list_2[2])
		changed_dt_obj = self.shift_month_for_dt_obj(changed_dt_obj, ymd_list_2[1])
		changed_dt_obj = self.shift_year_for_dt_obj(changed_dt_obj, ymd_list_2[0])
		result = self.get_ymd_list_for_dt_obj(changed_dt_obj)
		return result

	def shift_ymdhms_list_for_dt_obj(self, input_dt="", input_ymdhms_list=""):
		"""
		날짜를 이동

		:param dt_obj: 날짜 객체
		:param input_no:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		changed_dt_obj = self.shift_sec_for_dt_obj(input_dt, input_ymdhms_list[0])
		changed_dt_obj = self.shift_min_for_dt_obj(changed_dt_obj, input_ymdhms_list[1])
		changed_dt_obj = self.shift_hour_for_dt_obj(changed_dt_obj, input_ymdhms_list[2])
		changed_dt_obj = self.shift_day_for_dt_obj(changed_dt_obj, input_ymdhms_list[3])
		changed_dt_obj = self.shift_month_for_dt_obj(changed_dt_obj, input_ymdhms_list[4])
		changed_dt_obj = self.shift_year_for_dt_obj(changed_dt_obj, input_ymdhms_list[5])
		return changed_dt_obj

	def sleep(self, input_sec):
		"""
		time.sleep를 실행시키는 것

		:param input_sec:
		:return:
		"""
		time.sleep(input_sec)

	def split_dt_obj_to_two_dt_obj_by_base_date(self, start_dt_obj, end_dt_obj, split_dt_obj):
		"""
		어떤 날짜를 기준으로 둘로 나누는것
		기준시간에서 1조전의 기간으로 나누는 것이다

		:param start_dt_obj: datetime객체
		:param end_dt_obj: datetime객체
		:param split_dt_obj: datetime객체
		:return:
		"""
		result = False
		if start_dt_obj > split_dt_obj > end_dt_obj:
			new_end_dt_obj = self.shift_sec_for_dt_obj(split_dt_obj, -1)
			result = [start_dt_obj, new_end_dt_obj, end_dt_obj, split_dt_obj]
		return result

	def split_period_as_year_basis(self, ymd_list1, ymd_list2):
		"""
		날짜기간이 년이 다른경우 같은 year들로 리스트형태로 기간을 만들어 주는것
		입력값을 확인하는 것이다

		:param ymd_list1: [년, 월, 일]
		:param ymd_list2: [년, 월, 일]
		:return:
		"""
		dt_obj1 = self.check_input_time(ymd_list1)
		ymd_list1 = self.get_ymd_list_for_dt_obj(dt_obj1)

		dt_obj2 = self.check_input_time(ymd_list2)
		ymd_list2 = self.get_ymd_list_for_dt_obj(dt_obj2)

		# 2가지의 날짜가 들어오면, 1년단위로 시작과 끝의 날짜를 만들어 주는 것이다
		start_1 = int(ymd_list1[0]) * 10000 + int(ymd_list1[1]) * 100 + int(ymd_list1[2])
		end_1 = int(ymd_list2[0]) * 10000 + int(ymd_list2[1]) * 100 + int(ymd_list2[2])
		result = []

		# 날짜가 늦은것을 뒤로가게 만드는 것이다
		start_ymd = ymd_list1
		end_ymd = ymd_list2
		if start_1 > end_1:
			start_ymd = ymd_list2
			end_ymd = ymd_list1

		# 만약 년도가 같으면, 그대로 돌려준다
		if int(start_ymd[0]) == int(end_ymd[0]):
			result = [[start_ymd, end_ymd]]
		# 만약 1년의 차이만 나면, 아래와 같이 간단히 만든다
		elif int(end_ymd[0]) - int(start_ymd[0]) == 1:
			result = [
				[start_ymd, [start_ymd[0], 12, 31]],
				[[end_ymd[0], 1, 1], end_ymd],
			]
		# 2년이상이 발생을 할때 적용하는 것이다
		else:
			result = [[start_ymd, [start_ymd[0], 12, 31]], ]
			for year in range(int(start_ymd[0]) + 1, int(end_ymd[0])):
				result.append([[year, 1, 1], [year, 12, 31]])
			result.append([[end_ymd[0], 1, 1], end_ymd])
		return result

	def split_range_time_per_day(self, input_dt1, input_dt2):
		"""
		시간간격을 매일 날짜로 나누어진 리스트형태로 만든다

		:param input_dt1: datetime객체
		:param input_dt2: datetime객체
		:return:
		"""
		result = []
		ymd_list_1 = self.get_ymd_list_for_dt_obj(input_dt1)
		ymd_list_1_shft_1 = self.shift_day_for_ymd_list(ymd_list_1, 1)
		ymd_list_2 = self.get_ymd_list_for_dt_obj(input_dt2)
		sec_datas_1 = self.get_sec_set_for_dt_obj(input_dt1)
		sec_datas_2 = self.get_sec_set_for_dt_obj(input_dt2)
		week_no_1 = self.change_ymd_list_to_yearweekno(ymd_list_1)
		week_no_2 = self.change_ymd_list_to_yearweekno(ymd_list_2)
		if ymd_list_1 == ymd_list_2:
			# [e₩u=, [2023,2,22], 19340, 25430]
			temp = [week_no_1, ymd_list_1, sec_datas_1[2], sec_datas_2[2]]
			result.append([temp])
		elif ymd_list_1_shft_1 == ymd_list_2:
			temp_1 = [week_no_1, ymd_list_1, sec_datas_1[2], sec_datas_2[2]]
			temp_2 = [week_no_2, ymd_list_2, sec_datas_2[2], sec_datas_2[2]]
			result.append(temp_1)
			result.append(temp_2)
		else:
			temp_1 = [week_no_1, ymd_list_1, sec_datas_1[2], sec_datas_2[2]]
			result.append(temp_1)
			delta_day = self.calc_day_between_two_dt_obj(ymd_list_2, ymd_list_1)
			for one in range(1, delta_day[2]):
				new_ymd_list = self.shift_day_for_ymd_list(ymd_list_1, one)
				week_no_3 = self.change_ymd_list_to_yearweekno(new_ymd_list)
				result.append([week_no_3, new_ymd_list, 1, 86400])
			temp_2 = [week_no_2, ymd_list_2, sec_datas_2[2], sec_datas_2[2]]
			result.append(temp_2)
		return result

	def update_dt_obj_by_dic_time(self, input_dt="", input_dic=""):
		"""
		사전형식의 입력값을 이용하여, 기존 시간값을 바꾼다

		:param input_dt: datetime객체
		:param input_dic:
		:return:
		"""
		input_dt = self.check_dt_obj(input_dt)
		dic_time = self.change_dt_obj_to_dic_time(input_dt)
		dic_time.update(input_dic)
		result = self.change_dic_time_to_dt_obj(dic_time)
		return result


	def get_weekends_between_two_dt_obj(self, dt_start, dt_end):
		dt_start = self.check_dt_obj(dt_start)
		dt_end = self.check_dt_obj(dt_end)
		result = []
		current_date = dt_start
		while current_date <= dt_end:
			# 현재 날짜가 토요일(5) 또는 일요일(6)인지 확인
			if current_date.weekday() == 5 or current_date.weekday() == 6:
				ymd_list = self.change_dt_obj_to_ymd_list(current_date)
				result.append([int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2])])
			# 하루를 더해 다음 날짜로 이동
			current_date += datetime.timedelta(days=1)
		return result

	def get_ymd_set_for_nea_working_day(self, start_ymd="", requested_qty=10):
		# 기준날짜부터 n번째 근무일까지의 리스트
		# 기준날짜는 제외한다
		if not start_ymd:
			start_ymd = self.get_ymd_list_for_today()
		start_dt = self.change_ymd_list_to_dt_obj(start_ymd)
		start_dt = self.shift_day_for_dt_obj(start_dt, 1)
		start_date = self.change_dt_obj_to_ymd_list(start_dt)
		temp = self.shift_day_for_dt_obj(start_date, requested_qty * 2 + 30)
		end_date = self.change_dt_obj_to_ymd_list(temp)
		temp1 = self.get_holiday_list_between_two_ymd_list(start_date, end_date)
		holiday_l2d = []
		for one in temp1:
			holiday_l2d.append(one[0:3])
		weekend_l2d = self.get_weekends_between_two_dt_obj(start_date, end_date)
		result = []
		for one in range(1, 100):
			ymd_list = self.change_dt_obj_to_ymd_list(start_dt)
			ymd_list = [int(ymd_list[0]), int(ymd_list[1]), int(ymd_list[2])]
			if not ymd_list in holiday_l2d and not ymd_list in weekend_l2d:
				result.append(ymd_list)
			if len(result) == requested_qty:
				break
			start_dt = self.shift_day_for_dt_obj(start_dt, 1)
		return result
