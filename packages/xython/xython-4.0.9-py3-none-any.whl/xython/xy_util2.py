# -*- coding: utf-8 -*-
import cv2, pickle
import sys, screeninfo #기본모듈
import numpy as np
from konlpy.tag import Komoran
from PIL import ImageFont
import paho.mqtt.client as mqtt
from unittest.mock import patch
with patch("ctypes.windll.user32.SetProcessDPIAware", autospec=True):
	import pyautogui

import xy_re, xy_color, xy_common  # xython 모듈

class xy_util2():
	"""
	여러가지 사무용에 사용할 만한 메소드들을 만들어 놓은것이며,
	좀더 특이한 것은 youtil2로 만들어서 사용할 예정입니다
	"""

	def __init__(self):
		self.rex = xy_re.xy_re()
		self.colorx = xy_color.xy_color()
		self.varx = xy_common.xy_common().varx

		# 가끔 사용하다보면, css를 좀더 쉽게 사용했으면 할때가 있다
		self.varx["line_style_dic"] = {"solid": "solid", "dotted": "dotted", "dot": "dotted", "dashed": "dashed",
									   "dash": "dashed",
									   "double": "double", "outset": "outset", "inset": "inset", "groove": "groove",
									   "ridge": "ridge",
									   "": "solid", ".": "dotted", "--": "dashed", "=": "double"}




	def get_pxy_for_same_position_for_picture_vs_monitor_screen(self, search_picture="D://epro_x_button.jpg"):
		"""
		스크린 캡쳐를 해서, 네이버의 처음 화면을 naver_big이란 이름으로 저장
		스크린 캡쳐한것을 흑백화면으로 변경
		찾을 화면 naver_small_q을 흑백으로 변경
		화일이 들중에 하나라도 없으면, 중지
		원본화면이 가로세로의 픽셀이 얼마나 인지를 계산해서, 비교를 하기 위한것이다
		두영상의 같은위치에 존재하는 픽셀값을 더하는것
		두영상을 비교한 결과를 그레이 스케일로 나타내는 것
		"""
		current_screen = "D:/naver_big_1.jpg"
		pyautogui.screenshot(current_screen)  # 1
		current_screen_gray = cv2.imread(current_screen, cv2.IMREAD_GRAYSCALE)  # 2
		search_screen_gray = cv2.imread(search_picture, cv2.IMREAD_GRAYSCALE)  # 3
		if current_screen_gray is None or search_screen_gray is None: sys.exit()  # 3-1
		result_table = np.zeros(current_screen_gray.shape, np.int32)  # 4
		changed_current_screen = cv2.add(current_screen_gray, result_table, dtype=cv2.CV_8UC3)  # 6
		match_result = cv2.matchTemplate(changed_current_screen, search_screen_gray, cv2.TM_CCOEFF_NORMED)  # 7
		_, maxv, _, maxloc = cv2.minMaxLoc(match_result)  # 9
		cv2.waitKey()  # m
		cv2.destroyAllWindow()
		return [maxloc[0], maxloc[1]]



	def get_pxy_for_same_position_for_picture_vs_monitor_screen_1(self, file_target):
		"""
		현재 화면에서 같은 그림의 위치를 돌려주는 것

		:param file_target:
		:return:
		"""
		pyautogui.screenshot('D:/naver_big_1.jpg')
		src = cv2.imread('D:/naver_big_1.jpg', cv2.IMREAD_GRAYSCALE)  # 흑백으로 색을 읽어온다
		# 에제를 위해서, 네이버의 검색란을 스크린 캡쳐해서 naver_small_q란 이름으로 저장하는 것이다
		templ = cv2.imread(file_target, cv2.IMREAD_GRAYSCALE)

		if src is None or templ is None:
			print('Image load failed!')
			sys.exit()

		noise = np.zeros(src.shape, np.int32)  # zeros함수는 만든 갯수만큼 0이 들어간 행렬을 만드는것
		cv2.randn(noise, 50, 10)
		src = cv2.add(src, noise, dtype=cv2.CV_8UC3)

		res = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)  # 여기서 최댓값 찾기
		res_norm = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
		_, maxv, _, maxloc = cv2.minMaxLoc(res)

		th, tw = templ.shape[:2]
		dst = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
		cv2.rectangle(dst, maxloc, (maxloc[0] + tw, maxloc[1] + th), (0, 0, 255), 2)

		cv2.waitKey()  # msec시간 단위, 공란 또는 0일 경우엔 무한정으로 대기
		cv2.destroyAllWindows()  # 모든 이미지 창을 닫음

		pyautogui.moveTo(maxloc[0] + 45, maxloc[1] + 15)
		pyautogui.mouseDown(button='left')
		return [maxloc[0] + 45, maxloc[1] + 15]

	def get_pxy_for_same_position_for_two_image_file(self, img_big, img_small):
		"""
		그림 두개의 같은 위치를 찾아내는것

		:param img_big:
		:param img_small:
		:return:
		"""
		src = cv2.imread(img_big, cv2.IMREAD_GRAYSCALE)
		templ = cv2.imread(img_small, cv2.IMREAD_GRAYSCALE)

		noise = np.zeros(src.shape, np.int32)
		cv2.randn(noise, 50, 10)
		src = cv2.add(src, noise, dtype=cv2.CV_8UC3)
		res = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
		res_norm = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
		_, maxv, _, maxloc = cv2.minMaxLoc(res)
		print('maxv : ', maxv)
		print('maxloc : ', maxloc)

		if maxv > 0.85:
			print("found")
			result = maxloc
		else:
			pass
			result = ""
		return result

	def search_same_picture_xy(self, file_target):
		"""
		현재 화면에서 같은 그림의 위치를 돌려주는 것

		:param file_target:
		:return:
		"""
		pyautogui.screenshot('D:/naver_big_1.jpg')
		src = cv2.imread('D:/naver_big_1.jpg', cv2.IMREAD_GRAYSCALE)  # 흑백으로 색을 읽어온다
		# 에제를 위해서, 네이버의 검색란을 스크린 캡쳐해서 naver_small_q란 이름으로 저장하는 것이다
		templ = cv2.imread(file_target, cv2.IMREAD_GRAYSCALE)

		if src is None or templ is None:
			print('Image load failed!')
			sys.exit()

		noise = np.zeros(src.shape, np.int32)  # zeros함수는 만든 갯수만큼 0이 들어간 행렬을 만드는것
		cv2.randn(noise, 50, 10)
		src = cv2.add(src, noise, dtype=cv2.CV_8UC3)

		res = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)  # 여기서 최댓값 찾기
		res_norm = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
		_, maxv, _, maxloc = cv2.minMaxLoc(res)

		th, tw = templ.shape[:2]
		dst = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
		cv2.rectangle(dst, maxloc, (maxloc[0] + tw, maxloc[1] + th), (0, 0, 255), 2)

		cv2.waitKey()  # msec시간 단위, 공란 또는 0일 경우엔 무한정으로 대기
		cv2.destroyAllWindows()  # 모든 이미지 창을 닫음

		pyautogui.moveTo(maxloc[0] + 45, maxloc[1] + 15)
		pyautogui.mouseDown(button='left')
		return [maxloc[0] + 45, maxloc[1] + 15]

	def template_matching(self, img_big, img_small):
		"""
		큰사진안에서 작은사진이 맞는지를 확인하는 것

		:param img_big:
		:param img_small:
		:return:
		"""
		src = cv2.imread(img_big, cv2.IMREAD_GRAYSCALE)
		templ = cv2.imread(img_small, cv2.IMREAD_GRAYSCALE)

		noise = np.zeros(src.shape, np.int32)
		cv2.randn(noise, 50, 10)
		src = cv2.add(src, noise, dtype=cv2.CV_8UC3)
		res = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
		res_norm = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
		_, maxv, _, maxloc = cv2.minMaxLoc(res)
		print('maxv : ', maxv)
		print('maxloc : ', maxloc)

		if maxv > 0.85:
			print("found")
			result = maxloc
		else:
			pass
			result = ""
		return result


	def write_value_in_df_by_jfinderv1(self, df, xy, value):
		"""
		dataframe에 좌표로 값을 저장

		:param df: dataframe
		:param xy:
		:param value:
		:return:
		"""
		x_max = df.index.size
		y_max = df.columns.size
		if xy[1] > y_max:
			for no in range(y_max, xy[1]):
				df[len(df.columns)] = np.NaN
		if xy[0] > x_max:
			data_set = [(lambda x: np.NaN)(a) for a in range(len(df.columns))]
			for no in range(xy[0] - x_max):
				df.loc[len(df.index)] = data_set
		df.iat[int(xy[0]), int(xy[1])] = value




	def calc_pixel_size(self, input_text, font_size, font_name):
		"""
		폰트와 글자를 주면, 필셀의 크기를 돌려준다

		:param input_text:
		:param font_size:
		:param font_name:
		:return:
		"""
		font = ImageFont.truetype(font_name, font_size)
		size = font.getsize(input_text)
		return size

	def get_pixel_size_for_text(self, input_text, font_size, font_name):
		"""
		폰트와 글자를 주면, 필셀의 크기를 돌려준다
		"""
		font = ImageFont.truetype(font_name, font_size)
		size = font.getsize(input_text)
		return size

	def calculate_pixel_size_for_input_text(self, input_text, font_size, font_name):
		"""
		폰트와 글자를 주면, 필셀의 크기를 돌려준다
		"""
		font = ImageFont.truetype(font_name, font_size)
		size = font.getsize(input_text)
		return size


	def search_korean_in_text(self, input_text):
		"""
		문장을 갖고와서 단어별로 품사를 나누는 것이다
		"""
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		result = komoran.pos(input_text)
		return result
	def split_calue_성공한것_한글_품사로_나누기(self, input_text):
		"""
		문장을 갖고와서 단어별로 품사를 나누는 것이다
		"""
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		split_value = komoran.pos(input_text)
		print(split_value)

		#Save pickle
		with open("data.pickle", "wb") as fw:
			pickle.dump(split_value, fw)

	def split_kor_words(self, input_text):
		"""
		문장을 갖고와서 단어별로 품사를 나누는 것이다

		:param input_text:
		:return:
		"""
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		split_value = komoran.pos(input_text)
		print(split_value)

		# Save pickle
		with open("data.pickle", "wb") as fw:
			pickle.dump(split_value, fw)


	def split_word_in_text_as_word_type(self, input_text):
		"""
		문장을 갖고와서 단어별로 품사를 나누는 것이다
		"""
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		split_value = komoran.pos(input_text)
		print(split_value)

		# Save pickle
		with open("data.pickle", "wb") as fw:
			pickle.dump(split_value, fw)


	def value_split_성공한것_한글_품사로_나누기(self, input_text):
		"""
		문장을 갖고와서 단어별로 품사를 나누는 것이다
		"""
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		split_value = komoran.pos(input_text)
		print(split_value)

		#Save pickle
		with open("data.pickle", "wb") as fw:
			pickle.dump(split_value, fw)

	def calculate_text_pixel(self, input_text, target_pixel, font_name="malgun.ttf", font_size=12, fill_char=" "):
		"""
		원하는 길이만큼 텍스트를 근처의 픽셀값으로 만드는것
		원래자료에 붙이는 문자의 픽셀값
		"""
		fill_px = self.get_pixel_size_for_text(fill_char, font_size, font_name)[0]
		total_length = 0
		for one_text in input_text:
			# 한글자씩 필셀값을 계산해서 다 더한다
			one_length = self.get_pixel_size_for_text(fill_char, font_size, font_name)[0]
			total_length = total_length + one_length

		# 원하는 길이만큼 부족한 것을 몇번 넣을지 게산하는것
		times = round((target_pixel - total_length) / fill_px)
		result = input_text + " " * times

		# 최종적으로 넣은 텍스트의 길이를 한번더 구하는것
		length = self.get_pixel_size_for_text(result, font_size, font_name)[0]

		# [최종변경문자, 총 길이, 몇번을 넣은건지]
		return [result, length, times]

	def calculate_value_text_pixel(self, input_text, target_pixel, font_name="malgun.ttf", font_size=12, fill_char=" "):
		"""
		원하는 길이만큼 텍스트를 근처의 픽셀값으로 만드는것
		원래자료에 붙이는 문자의 픽셀값
		"""
		fill_px = self.calc_pixel_size(fill_char, font_size, font_name)[0]
		total_length = 0
		for one_text in input_text:
			# 한글자씩 필셀값을 계산해서 다 더한다
			one_length = self.calc_pixel_size(fill_char, font_size, font_name)[0]
			total_length = total_length + one_length

		# 원하는 길이만큼 부족한 것을 몇번 넣을지 게산하는것
		times = round((target_pixel - total_length) / fill_px)
		result = input_text + " " * times

		# 최종적으로 넣은 텍스트의 길이를 한번더 구하는것
		length = self.calc_pixel_size(result, font_size, font_name)[0]

		# [최종변경문자, 총 길이, 몇번을 넣은건지]
		return [result, length, times]


	def get_text_pixel_for_input_text(self, input_text, target_pixel, font_name="malgun.ttf", font_size=12, fill_char=" "):
		"""
		원하는 길이만큼 텍스트를 근처의 픽셀값으로 만드는것
		원래자료에 붙이는 문자의 픽셀값
		"""
		fill_px = self.get_pixel_size_for_text(fill_char, font_size, font_name)[0]
		total_length = 0
		for one_text in input_text:
			# 한글자씩 필셀값을 계산해서 다 더한다
			one_length = self.get_pixel_size_for_text(fill_char, font_size, font_name)[0]
			total_length = total_length + one_length

		# 원하는 길이만큼 부족한 것을 몇번 넣을지 게산하는것
		times = round((target_pixel - total_length) / fill_px)
		result = input_text + " " * times

		# 최종적으로 넣은 텍스트의 길이를 한번더 구하는것
		length = self.get_pixel_size_for_text(result, font_size, font_name)[0]

		# [최종변경문자, 총 길이, 몇번을 넣은건지]
		return [result, length, times]

	def get_monitors_properties(self):
		"""
		연결된 모니터들의 속성을 알려준다

		:return:
		"""
		result = {}
		sub_result = {}
		num = 0
		for m in screeninfo.get_monitors():
			num = num + 1
			# print(m)
			sub_result["x"] = m.x
			sub_result["y"] = m.y
			sub_result["height_mm"] = m.height_mm
			sub_result["width_mm"] = m.width_mm
			sub_result["height"] = m.height
			sub_result["width"] = m.width
			sub_result["primary"] = m.is_primary
			sub_result["name"] = m.name
			name = "monitor" + str(num)
			result[name] = sub_result
		return result



	def search_objs_by_visited_a_tag(self):
		pass


	def search_objs_by_2_near_tags(self):
		pass


	def search_objs_by_mother_n_son_tags(self):
		pass


	def search_objs_by_tag_n_attr(self):
		pass


	def search_objs_by_tag_n_attr_n_value_as_same(self):
		pass


	def search_objs_by_tag_n_attr_n_value_as_in(self):
		pass


	def search_objs_by_tag_n_attr_n_value_as_start(self):
		pass


	def search_objs_by_tag_n_attr_n_value_as_end(self):
		pass


	def search_objs_by_checked_radio(self):
		pass


	def search_first_obj_by_tag(self):
		pass


	def search_nth_child_obj_by_tag(self):
		pass


	def search_nth_last_child_obj_by_tag(self):
		pass


	def search_nth_of_type_obj_by_tag(self):
		pass

	def search_nth_last_of_type_obj_by_tag(self):
		pass

	def search_first_child_obj_by_tag(self):
		pass

	def search_last_child_obj_by_tag(self):
		pass

	def search_only_child_obj_by_tag(self):
		pass

	def search_only_of_type_obj_by_tag(self):
		pass

	def search_first_of_type_obj_by_tag(self):
		pass


	def mqtt_connect(self, client, userdata, flags, rc):
		"""
		connect_mqtt

		:param client:
		:param userdata:
		:param flags:
		:param rc:
		:return:
		"""
		if rc == 0:
			print("connected OK")
		else:
			print("Bad connection Returned code=", rc)

	def mqtt_receive_data(self, topic='halmoney/data001'):
		"""
		mqtt의 서버에서 자료받기

		:param topic:
		:return:
		"""
		self.topic = topic
		client = mqtt.Client()
		client.on_connect = self.on_connect
		client.on_disconnect = self.on_disconnect
		client.on_subscribe = self.on_subscribe
		client.on_message = self.on_message

		client.connect(self.broker, self.port, 60)
		client.subscribe(self.topic, 1)
		client.loop_forever()

	def mqtt_send_data(self, input_text="no message", topic='halmoney/data001'):
		"""

		:param input_text:
		:param topic:
		:return:
		"""
		self.topic = topic
		client = mqtt.Client()
		# 새로운 클라이언트 생성

		# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
		client.on_connect = self.on_connect
		client.on_disconnect = self.on_disconnect
		client.on_publish = self.on_publish
		client.connect(self.broker, self.port)
		client.loop_start()

		client.publish(self.topic, str(input_text), self.qos)
		client.loop_stop()
		client.disconnect()

	def mqtt_start(self, broker="broker.hivemq.com", port=1883, qos=0):
		"""

		:param broker:
		:param port:
		:param qos:
		:return:
		"""
		self.broker = broker
		self.port = port
		self.qos = qos
