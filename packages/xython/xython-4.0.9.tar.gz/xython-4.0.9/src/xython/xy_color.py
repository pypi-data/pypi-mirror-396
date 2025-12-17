# -*- coding: utf-8 -*-
import re, math  # 내장모듈

from unittest.mock import patch
with patch("ctypes.windll.user32.SetProcessDPIAware", autospec=True):
	import pyautogui

import xy_re, xy_common  # xython 모듈

class xy_color:
	"""
	색을 편하게 사용하기위해 만든 모듈
	기본값의 형태 : rgb
	"""
	def __history(self):
		"""
		2024-04-25 : 전체적으로 이름을 terms에 따라서 변경함
		"""
		pass

	def __init__(self):
		"""
		self.varx : package안에서 공통적으로 사용되는 변수들
		"""

		self.varx = xy_common.xy_common().varx
		self.s_step = 5  # +, -의 각 1개에 hs1에서 s의 값의 변화

	def _change_xcolor_to_hsl(self, input_xcolor):
		"""
		input_l1d => [숫자만","색이름",숫자, "+ 갯수","- 갯수" rgb_list, rgb_int]
		         ==> [11,"red",60,3,5,[255,25,0], 12345]

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return:
		"""
		input_l1d = self._check_input_xcolor(input_xcolor)
		hsl_list = None

		if input_l1d[0]:  # 정수, 12가지 기본색
			hsl_list = self.varx["list_basic_12hsl"][input_l1d[0]]
		elif input_l1d[1]:  # 색이름
			hsl_list = self.varx["color_name_eng_vs_hsl_no"][input_l1d[1]]
			if input_l1d[2]:  # 명도
				hsl_list[2] = input_l1d[2]
			if input_l1d[3]:  # 채도 +
				temp = hsl_list[1] + self.s_step * input_l1d[3]
				if temp > 100:
					hsl_list[1] = 100
				else:
					hsl_list[1] = temp
			elif input_l1d[4]:  # 채도 -
				temp = hsl_list[1] - self.s_step * input_l1d[4]
				if temp < 0:
					hsl_list[1] = 0
				else:
					hsl_list[1] = temp
		elif input_l1d[5]:  # rgb_list
			hsl_list = self.change_rgb_to_hsl(input_l1d[5])
		elif input_l1d[6]:  # rgb_int
			hsl_list = self.change_rgbint_to_hsl(input_l1d[6])
		return hsl_list

	def _check_input_xcolor(self, input_xcolor):
		"""
		xcolor 형식의 입력값을 화인하는 것이다
		1. 정수만 오는경우 : 기본 12 색중에서 하나로 간주
		2. red++45 => red, ++, 45로 구분
		3. RGB 가 오는 경우
		4. 12 초과의 숫자가 오면 rgbint로 간주한다

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		return: ["숫자만","색이름", 숫자, "+갯수","-갯수" rgb_list, rgb_int]
		"""
		result = [None, None, None, None, None, None, None]
		if type(input_xcolor) == type([]):  # rgb 리스트일때
			result[5] = input_xcolor
		elif type(input_xcolor) == type(123):
			if input_xcolor < 13:  # 기본색상일때
				result[0] = input_xcolor
			else:  # 12 초과숫자로 rgbint로 간주
				result[6] = input_xcolor
		elif type(input_xcolor) == type("abc"):  # 영어나 한글로 된 색깔이름을 추출

			# xcolor 에서 숫자만 추출
			re_com2 = re.compile("[0-9]+")
			nos = re_com2.findall(input_xcolor)
			if nos:
				if nos[0] == input_xcolor:
					result[0] = int(nos[0])
					return result
				else:
					result[2] = int(nos[0])

			# 영어나 한글로 된 색깔이름을 추출
			re_com1 = re.compile("[a-zA-Z_가-힣]+")
			color_name = re_com1.findall(input_xcolor)
			checked_color_name = self.varx["check_color_name"][color_name[0]]
			result[1] = checked_color_name

			# xcolor에서 + 추출
			re_com3 = re.compile("[+]+")
			xcolor_plus = re_com3.findall(input_xcolor)
			if xcolor_plus: result[3] = len(xcolor_plus[0])

			# xcolor에서 - 추출
			re_com4 = re.compile("[-]+")
			xcolor_minus = re_com4.findall(input_xcolor)
			if xcolor_minus: result[4] = len(xcolor_minus[0])
		return result

	def calculate_distance_two_3d_point(self, input_1, input_2):
		"""
		3 차원의 거리를 기준으로 RGB 값의 차이를 계산하는 것

		:param input_1:
		:param input_2:
		:return:
		"""
		dist = math.sqrt(
			math.pow((input_1[0] - input_2[0]), 2) + math.pow((input_1[1] - input_2[1]), 2) + math.pow(
				(input_1[2] - input_2[2]), 2))
		return dist

	def change_56color_no_to_color_name(self, input_56color_no):
		result = self.change_56color_no_to_color_name_kor(input_56color_no)
		return result

	def change_56color_no_to_color_name_kor(self, input_56color_no):
		"""
		엑셀 56색의 번호 -> 한글 색이름

		:param input_56color_no:
		:return:
		"""
		result = self.varx["56color_vs_color_kor"][int(input_56color_no)]
		return result

	def change_56color_no_to_rgb(self, i_no):
		"""
		엑셀 56색의 번호 -> rgb 리스트

		:param input_56color:
		:return:
		"""
		result = self.varx["rgb56_for_excel"][int(i_no)]
		return result

	def change_any_color_to_hsl(self, input_color):
		"""
		any_color라는 단어가 사용자의 입장에서 이해하기 더 편할것 같아서 추가하여 만든 것

		:param input_color:
		:return:
		"""
		result = self.change_input_color_to_hsl(input_color)
		return result

	def change_any_color_to_rgb(self, input_color):
		"""
		any_color라는 단어가 사용자의 입장에서 이해하기 더 편할것 같아서 추가하여 만든 것

		:param input_color:
		:return:
		"""
		result = self.change_input_color_to_rgb(input_color)
		return result

	def change_any_color_to_rgbint(self, input_color):
		"""
		any_color라는 단어가 사용자의 입장에서 이해하기 더 편할것 같아서 추가하여 만든 것

		:param input_color:
		:return:
		"""
		rgb = self.change_input_color_to_rgb(input_color)
		result = self.change_rgb_to_rgbint(rgb)

		return result

	def change_hsl_as_bright_high(self, input_hsl):
		"""
		입력된 input_hsl값 -> 고명도로 바꾸는 것
		"""
		input_hsl[2] = 80
		return input_hsl

	def change_hsl_as_bright_low(self, input_hsl):
		"""
		입력된 input_hsl값 -> 저명도로 바꾸는 것 (저명도 : 명도값이 20%정도)
		"""
		input_hsl[2] = 20
		return input_hsl

	def change_hsl_as_bright_middle(self, input_hsl):
		"""
		입력된 input_hsl값 -> 중명도로 바꾸는 것
		"""
		input_hsl[2] = 50
		return input_hsl

	def change_hsl_as_color_high(self, input_hsl):
		"""
		입력된 input_hsl값 -> 고채도로 바꾸는 것
		"""
		input_hsl[1] = 80
		return input_hsl

	def change_hsl_as_contrast_high(self, input_hsl):
		"""
		입력된 input_hsl값 -> 중채도로 바꾸는 것
		"""
		input_hsl[0] = 100
		return input_hsl

	def change_hsl_as_contrast_low(self, input_hsl):
		"""
		입력된 input_hsl값 -> 저채도로 바꾸는 것
		"""
		input_hsl[0] = 20
		return input_hsl

	def change_hsl_as_contrast_middle(self, input_hsl):
		"""
		입력된 input_hsl값 -> 중채도로 바꾸는 것
		"""
		input_hsl[0] = 50
		return input_hsl

	def change_hsl_as_pastel_by_0to1(self, input_hsl, strong_level=0.5):
		"""
		입력받은 input_hsl값을 파스텔톤으로 적용시키는것

		level1 : 0~1사이의값
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl
		style = pastel = [0, 100]

		delta_s = (style[0] - s) * strong_level
		delta_l = (style[1] - l) * strong_level

		changed_s = s + delta_s
		changed_l = l + delta_l
		return [h, changed_s, changed_l]

	def change_hsl_by_plusminus100(self, hsl_list, plusminus100):
		"""
		hsl값을 미세조정하는 부분

		plusminus100 : ++, --, 70등의 값이 들어오면 변화를 시켜주는 것

		:param hsl_list:
		:param plusminus100:
		:return:
		"""
		if type(plusminus100) == type(123):
			# 50을 기본으로 차이나는 부분을 계산하는것
			l_value = plusminus100 - 50
			if l_value < 0:
				l_value = 0
		elif "+" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 밝아지도록 한다
			l_value = 10 * len(plusminus100)
		elif "-" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 어두워지도록 한다
			l_value = -10 * len(plusminus100)

		final_l_value = hsl_list[2] + l_value
		if final_l_value > 100:
			final_l_value = 100
		elif final_l_value < 0:
			final_l_value = 0

		result = [hsl_list[0], hsl_list[1], final_l_value]
		return result

	def change_hsl_for_bright_by_0to100(self, input_hsl, strong_level=50):
		"""
		입력받은 input_hsl값을 명도가 높은 쪽으로 이동시키는것

		level1 : 0~1사이의값
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl

		changed_s = s + (100 - s) * strong_level / 100
		changed_l = l + (100 - l) * strong_level / 100
		return [h, changed_s, changed_l]

	def change_hsl_for_dark_by_0to100(self, input_hsl, strong_level=0.5):
		"""
		입력받은 input_hsl값을 어두운 쪽으로 이동시키는것

		level1 : 0~1사이의값
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl
		style = dark = [0, 0]

		delta_s = (style[0] - s) * strong_level
		delta_l = (style[1] - l) * strong_level

		changed_s = s + delta_s
		changed_l = l + delta_l
		return [h, changed_s, changed_l]

	def change_hsl_for_gray_by_0to1(self, input_hsl, strong_level=0.5):
		"""
		입력받은 input_hsl값을 어두운 쪽으로 이동시키는것

		level1 : 0~1사이의값
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl
		style = [100, 0]

		delta_s = (style[0] - s) * strong_level
		delta_l = (style[1] - l) * strong_level

		changed_s = s + delta_s
		changed_l = l + delta_l
		return [h, changed_s, changed_l]

	def change_hsl_for_input_color_style_by_0to1(self, input_hsl, color_style="파스텔", style_step=5):
		"""
		hsl값을 색의 스타일과 강도로써 조정하는 것

		:param input_hsl:
		:param color_style:
		:param style_step:
		:return:
		"""

		checked_color_style = self.varx["check_color_tone"][color_style]

		step_2 = self.varx["basic_15tone_eng_vs_sl"][checked_color_style]
		step_1 = self.varx["sl_10_by_작은step"][style_step]
		h = int(input_hsl[0])
		s = int(step_1[0]) + int(step_2[0])
		l = int(step_1[1]) + int(step_2[1])

		changed_rgb = self.change_hsl_to_rgb([h, s, l])
		return changed_rgb

	def change_hsl_for_pastel_style_by_0to1(self, input_hsl, strong_level=0.5):
		"""
		입력받은 input_hsl값을 파스텔톤으로 적용시키는것

		level1 : 0~1사이의값
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl
		style = pastel = [0, 100]

		delta_s = (style[0] - s) * strong_level
		delta_l = (style[1] - l) * strong_level

		changed_s = s + delta_s
		changed_l = l + delta_l
		return [h, changed_s, changed_l]

	def change_hsl_for_sl_by_0to100(self, input_hsl, step_no):
		"""
		input_hsl값을 명도를 조정하는 방법
		+，-로 조정을 하는것이다

		:param input_hsl: [h,s,l]형식의 값
		:param step_no:
		:return:
		"""
		s, l = self.varx["색강도_vs_sl"][step_no]
		result = [input_hsl[0], input_hsl[1] + s, input_hsl[2] + l]

	def change_hsl_for_sl_by_plusminus100(self, input_hsl, s_step="++", l_step="++"):
		"""
		input_hsl값을 올리거나 내리는 것, sl의값을 조정하여 채도와 명도를 조절하는것
		입력 : [[36, 50, 50], "++", "--"]
		약 5씩이동하도록 만든다

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		step_no = 5  # 5단위씩 변경하도록 하였다
		h, s, l = input_hsl

		if s_step == "":
			pass
		elif s_step[0] == "+":
			s = s + len(s_step) * step_no
			if s > 100: s = 100
		elif s_step[0] == "-":
			s = s - len(s_step) * step_no
			if s < 0: s = 0

		if l_step == "":
			pass
		elif l_step[0] == "+":
			l = l + len(l_step) * step_no
			if l > 100: l = 100
		elif l_step[0] == "-":
			l = l - len(l_step) * step_no
			if l < 0: l = 0

		result = self.change_hsl_to_rgb([h, s, l])
		return result

	def change_hsl_for_vivid_by_0to1(self, input_hsl, strong_level=0.5):
		"""
		level1 : 0~1사이의값
		입력받은 input_hsl값을 어두운 쪽으로 이동시키는것
		bright = [100,100], sharp = [50,100], graish = [100,0], dark = [0,0], black = [50, 0]

		:param input_hsl: [h,s,l]형식의 값
		:param strong_level:
		:return:
		"""
		h, s, l = input_hsl
		style = sharp = [50, 100]

		delta_s = (style[0] - s) * strong_level
		delta_l = (style[1] - l) * strong_level

		changed_s = s + delta_s
		changed_l = l + delta_l
		return [h, changed_s, changed_l]

	def change_hsl_list_by_plusminus100(self, hsl_list, plusminus100):
		"""
		hsl값을 미세조정하는 부분

		plusminus100 : ++, --, 70등의 값이 들어오면 변화를 시켜주는 것

		:param hsl_list:
		:param plusminus100:
		:return:
		"""
		if type(plusminus100) == type(123):
			# 50을 기본으로 차이나는 부분을 계산하는것
			l_value = plusminus100 - 50
			if l_value < 0:
				l_value = 0
		elif "+" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 밝아지도록 한다
			l_value = 10 * len(plusminus100)
		elif "-" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 어두워지도록 한다
			l_value = -10 * len(plusminus100)

		final_l_value = hsl_list[2] + l_value
		if final_l_value > 100:
			final_l_value = 100
		elif final_l_value < 0:
			final_l_value = 0

		result = [hsl_list[0], hsl_list[1], final_l_value]
		return result

	def change_hsl_to_10_rgb_step_by_s(self, input_hsl, step=10):
		"""
		위쪽으로 5개, 아래로 5개의 채도가 비슷한 색을 돌려준다
		채도의 특성상 비슷한 부분이 많아서 10단위로 만든다

		:param input_hsl: [h,s,l]형식의 값
		:param step: 단계를 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl
		result = []
		for no in range(0, 100 + step, step):
			temp = self.change_hsl_to_rgb([h, no, l])
			result.append(temp)
		return result

	def change_hsl_to_2_hsl_for_near_bo(self, input_hsl, h_step=36):
		"""
		근접보색조합 : 보색의 근처색
		분열보색조합 : Split Complementary
		근접보색조합 : 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step + 180, 360)[1]
		new_h_3 = divmod(h + h_step + 180, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]
		return [hsl_1, hsl_3]

	def change_hsl_to_2_hsl_for_near_bo_step_by_h_0to100(self, input_hsl, h_step=36):
		"""
		level100 : -100 ~ 100사이의 값
		근접보색조합 : 보색의 근처색
		분열보색조합 : Split Complementary
		근접보색조합이라고도 한다. 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step + 180, 360)[1]
		new_h_3 = divmod(h + h_step + 180, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]
		result = [hsl_1, input_hsl, hsl_3]
		return result

	def change_hsl_to_2_hsl_for_side_color_by_l_0to100(self, input_hsl, l_step=30):
		"""
		level100 : -100 ~ 100사이의 값
		명도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl
		rgb_1 = self.change_hsl_to_rgb([h, s, l_step])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([h, s, 100 - l_step])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_hsl_for_side_color_by_s_0to100(self, input_hsl, s_step=30):
		"""
		level100 : -100 ~ 100사이의 값
		채도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], s_step, input_hsl[2]])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], 100 - s_step, input_hsl[2]])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_hsl_for_side_color_step_by_h_0to100(self, hsl, h_step=36):
		"""
		level100 : -100 ~ 100사이의 값
		근접색조합 : 양쪽 근처색

		:param hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = hsl

		new_h_1 = divmod(h - h_step, 360)[1]
		new_h_3 = divmod(h + h_step, 360)[1]

		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb(hsl)
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_near_bo_by_h_by_0to1(self, input_hsl, h_step=36):
		"""
		level100 : -100 ~ 100사이의 값
		근접보색조합 : 보색의 근처색
		분열보색조합 : Split Complementary
		근접보색조합이라고도 한다. 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step + 180, 360)[1]
		new_h_3 = divmod(h + h_step + 180, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]
		result = [hsl_1, input_hsl, hsl_3]
		return result

	def change_hsl_to_2_near_bo_hsl(self, input_hsl, h_step=36):
		"""
		근접보색조합 : 보색의 근처색
		분열보색조합 : Split Complementary
		근접보색조합 : 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step + 180, 360)[1]
		new_h_3 = divmod(h + h_step + 180, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]
		return [hsl_1, hsl_3]

	def change_hsl_to_2_near_bo_rgb(self, input_hsl, h_step=36):
		"""
		근접보색조합 : 보색의 양쪽 근처색
		분열보색조합 : Split Complementary
		근접보색조합 : 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용
		2차원 list의 형태로 돌려줌

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step + 180, 360)[1]
		new_h_3 = divmod(h + h_step + 180, 360)[1]
		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		result = [rgb_1, rgb_2, rgb_3]

		return result

	def change_hsl_to_2_near_rgb(self, input_hsl, h_step=36):
		"""
		입력으로 들어오는 색의 양꼬 근처의 색을 돌려주는 것
		기본으로 h의 값을 36만큼의 양쪽 색을 돌려준다
		근접색조합 : 양쪽 근처색

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step, 360)[1]
		new_h_3 = divmod(h + h_step, 360)[1]

		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_rgb_for_near_bo(self, input_hsl, h_step=36):
		"""
		근접보색조합 : 보색의 양쪽 근처색
		분열보색조합 : Split Complementary
		근접보색조합 : 보색의 강한 인상이 부담스러울때 보색의 근처에 있는 색을 사용
		2차원 list의 형태로 돌려줌

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		result = []
		hsl_set = self.change_hsl_to_2_hsl_for_near_bo(input_hsl, h_step=36)
		for one_hsl in hsl_set:
			result.append(self.change_hsl_to_rgb(one_hsl))
		return result

	def change_hsl_to_2_rgb_for_near_step_by_h_0to100(self, input_hsl, h_step=36):
		"""
		입력으로 들어오는 색의 양쪽 근처의 색을 돌려주는 것
		기본으로 h의 값을 36만큼의 양쪽 색을 돌려준다
		근접색조합 : 양쪽 근처색

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step, 360)[1]
		new_h_3 = divmod(h + h_step, 360)[1]

		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_side_color_by_h_by_0to1(self, input_hsl, h_step=36):
		"""
		level100 : -100 ~ 100사이의 값
		근접색조합 : 양쪽 근처색

		:param input_hsl: [h,s,l]형식의 값
		:param h_step: h값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h - h_step, 360)[1]
		new_h_3 = divmod(h + h_step, 360)[1]

		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_side_color_by_l_by_0to1(self, input_hsl, l_step=30):
		"""
		level100 : -100 ~ 100사이의 값
		명도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		h, s, l = input_hsl
		rgb_1 = self.change_hsl_to_rgb([h, s, l_step])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([h, s, 100 - l_step])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_2_side_color_by_s_by_0to1(self, input_hsl, s_step=30):
		"""
		level100 : -100 ~ 100사이의 값
		채도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], s_step, input_hsl[2]])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], 100 - s_step, input_hsl[2]])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_3_hsl_set_step_by_big_l(self, input_hsl, l_step=30):
		"""
		명도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], input_hsl[1], l_step])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], input_hsl[1], 100 - l_step])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_3_hsl_set_step_by_big_s(self, input_hsl, s_step=30):
		"""
		채도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], s_step, input_hsl[2]])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], 100 - s_step, input_hsl[2]])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_3_hsl_step_by_big_l(self, input_hsl, l_step=30):
		"""
		명도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], input_hsl[1], l_step])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], input_hsl[1], 100 - l_step])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_3_hsl_step_by_big_s(self, input_hsl, s_step=30):
		"""
		채도차가 큰 2가지 1가지색

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_hsl_to_rgb([input_hsl[0], s_step, input_hsl[2]])
		rgb_2 = self.change_hsl_to_rgb(input_hsl)
		rgb_3 = self.change_hsl_to_rgb([input_hsl[0], 100 - s_step, input_hsl[2]])
		result = [rgb_1, rgb_2, rgb_3]
		return result

	def change_hsl_to_3_rgb_set_as_0_120_240(self, input_hsl):
		result = self.change_hsl_to_3_rgb_set_step_by_h_120_degree(input_hsl)
		return result

	def change_hsl_to_3_rgb_set_step_by_h_120_degree(self, input_hsl):
		"""
		등간격 3색조합 : triad
		활동적인 인상과 이미지를 보인다

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h + 120, 360)[1]
		new_h_3 = divmod(h + 240, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]

		result_rgb = self.change_hsl_to_rgb([hsl_1, input_hsl, hsl_3])
		return result_rgb

	def change_hsl_to_3_rgb_step_by_0_120_240(self, input_hsl):
		"""
		input_hsl값을 0, 120, 240도의 3개의 rgb값으로 돌려주는 것
		:param input_hsl:
		:return:
		"""
		result = self.change_hsl_to_3_rgb_step_by_h_120(input_hsl)
		return result

	def change_hsl_to_3_rgb_step_by_h_120(self, input_hsl):
		"""
		등간격 3색조합 : triad
		활동적인 인상과 이미지를 보인다

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h + 120, 360)[1]
		new_h_3 = divmod(h + 240, 360)[1]

		hsl_1 = [new_h_1, s, l]
		hsl_3 = [new_h_3, s, l]

		result_rgb = self.change_hsl_to_rgb([hsl_1, input_hsl, hsl_3])
		return result_rgb

	def change_hsl_to_4_tetra_style_rgb(self, input_hsl):
		"""
		360도의 색을 90도씩 변하는 4단계로 나누어서 돌려주는 것

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h + 0, 360)[1]
		new_h_2 = divmod(h + 90, 360)[1]
		new_h_3 = divmod(h + 180, 360)[1]
		new_h_4 = divmod(h + 270, 360)[1]
		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb([new_h_2, s, l])
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		rgb_4 = self.change_hsl_to_rgb([new_h_4, s, l])
		result = [rgb_1, rgb_2, rgb_3, rgb_4]

		return result

	def change_hsl_to_bo_rgb(self, input_hsl):
		"""
		입력된 input_hsl에 대한 보색을 알려주는것
		보색 : Complementary
		2차원 list의 형태로 돌려줌

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""

		new_h = divmod(input_hsl[0] + 180, 360)[1]
		result = self.change_hsl_to_rgb([new_h, input_hsl[1], input_hsl[2]])
		return [result]

	def change_hsl_to_rgb(self, input_hsl):
		"""
		input_hsl을 rgb로 변경

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		h = float(h / 360)
		s = float(s / 100)
		l = float(l / 100)

		if s == 0:
			R = l * 255
			G = l * 255
			B = l * 255

		if l < 0.5:
			temp1 = l * (1 + s)
		else:
			temp1 = l + s - l * s

		temp2 = 2 * l - temp1

		# h = h / 360

		tempR = h + 0.333
		tempG = h
		tempB = h - 0.333

		if tempR < 0: tempR = tempR + 1
		if tempR > 1: tempR = tempR - 1
		if tempG < 0: tempG = tempG + 1
		if tempG > 1: tempG = tempG - 1
		if tempB < 0: tempB = tempB + 1
		if tempB > 1: tempB = tempB - 1

		if 6 * tempR < 1:
			R = temp2 + (temp1 - temp2) * 6 * tempR
		else:
			if 2 * tempR < 1:
				R = temp1
			else:
				if 3 * tempR < 2:
					R = temp2 + (temp1 - temp2) * (0.666 - tempR) * 6
				else:
					R = temp2

		if 6 * tempG < 1:
			G = temp2 + (temp1 - temp2) * 6 * tempG
		else:
			if 2 * tempG < 1:
				G = temp1
			else:
				if 3 * tempG < 2:
					G = temp2 + (temp1 - temp2) * (0.666 - tempG) * 6
				else:
					G = temp2
		if 6 * tempB < 1:
			B = temp2 + (temp1 - temp2) * 6 * tempB
		else:
			if 2 * tempB < 1:
				B = temp1
			else:
				if 3 * tempB < 2:
					B = temp2 + (temp1 - temp2) * (0.666 - tempB) * 6
				else:
					B = temp2
		R = int(abs(round(R * 255, 0)))
		G = int(abs(round(G * 255, 0)))
		B = int(abs(round(B * 255, 0)))

		return [R, G, B]

	def change_hsl_to_rgb_by_4_tetra_style(self, input_hsl):
		"""
		4가지 꼭지의 rgb값

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h + 0, 360)[1]
		new_h_2 = divmod(h + 90, 360)[1]
		new_h_3 = divmod(h + 180, 360)[1]
		new_h_4 = divmod(h + 270, 360)[1]
		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb([new_h_2, s, l])
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		rgb_4 = self.change_hsl_to_rgb([new_h_4, s, l])
		result = [rgb_1, rgb_2, rgb_3, rgb_4]

		return result

	def change_hsl_to_rgb_by_pccs_style(self, input_hsl, color_style="파스텔", style_step=5):
		"""
		input_hsl => pccs스타일의 rgb값으로 바꾸는 것
		:param input_hsl:
		:param color_style:
		:param style_step:
		:return:
		"""

		color_style_checked = self.varx["check_color_tone"][color_style]
		step_2 = self.varx["basic_15tone_eng_vs_sl"][color_style_checked]  # 스타일을 적용하는것
		step_1 = self.varx["sl_10_by_작은step"][style_step]  # 스타일을 얼마나 강하게 적용할것인가를 나타내는것

		h = int(input_hsl[0])
		s = int(step_1[0]) + int(step_2[0])
		l = int(step_1[1]) + int(step_2[1])

		changed_rgb = self.change_hsl_to_rgb([h, s, l])
		return changed_rgb

	def change_hsl_to_rgb_by_plusminus100(self, input_hsl, plusminus100):
		"""
		plusminus100 : ++, --, 70등의 값이 들어오면 변화를 시켜주는 것

		:param input_hsl: [h,s,l]값
		:param plusminus100:
		:return:
		"""
		if type(plusminus100) == type(123):
			# 50을 기본으로 차이나는 부분을 계산하는것
			l_value = plusminus100 - 50
			if l_value < 0:
				l_value = 0
		elif "+" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 밝아지도록 한다
			l_value = 10 * len(plusminus100)
		elif "-" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 어두워지도록 한다
			l_value = -10 * len(plusminus100)

		final_l_value = input_hsl[2] + l_value
		if final_l_value > 100:
			final_l_value = 100
		elif final_l_value < 0:
			final_l_value = 0

		result = [input_hsl[0], input_hsl[1], final_l_value]
		return result

	def change_hsl_to_rgb_by_tone(self, input_hsl, color_style="파스텔", style_step=5):
		"""
		입력된 기본 값을 스타일에 맞도록 바꾸고, 스타일을 강하게 할것인지 아닌것인지를 보는것
		color_style : pccs의 12가지 사용가능, 숫자로 사용가능, +-의 형태로도 사용가능
		입력예 : 기본색상, 적용스타일, 변화정도,("red45, 파스텔, 3)
		변화정도는 5를 기준으로 1~9까지임

		:param input_hsl: [h,s,l]형식의 값
		:param color_style:
		:param style_step:
		:return:
		"""

		color_style_checked = self.varx["check_color_tone"][color_style]
		step_2 = self.varx["basic_15tone_eng_vs_sl"][color_style_checked]  # 스타일을 적용하는것
		step_1 = self.varx["sl_10_by_작은step"][style_step]  # 스타일을 얼마나 강하게 적용할것인가를 나타내는것

		h = int(input_hsl[0])
		s = int(step_1[0]) + int(step_2[0])
		l = int(step_1[1]) + int(step_2[1])

		changed_rgb = self.change_hsl_to_rgb([h, s, l])
		return changed_rgb

	def change_hsl_to_rgb_by_triangle_style(self, input_hsl):
		result = self.change_hsl_to_3_rgb_set_step_by_h_120_degree(input_hsl)
		return result

	def change_hsl_to_rgbint(self, input_hsl):
		"""
		변경 : hsl -> rgbint

		:param input_hsl:
		:return:
		"""
		rgb = self.change_hsl_to_rgb(input_hsl)
		result = self.change_rgb_to_rgbint(rgb)
		return result

	def change_input_color_to_hsl(self, input_color):
		"""
		어떤 색을 나타내는 형태라도 hsl값을 돌려주는것

		:param input_value: rgb형식, hsl형식, xcolor형식
		:return: hsl값
		"""
		if type(input_color) == type("string"):  # 문자열 형식일때 xcolor형식으로 해석
			hsl = self.change_xcolor_to_hsl(input_color)

		elif type(input_color) == type(123):  # 숫자가 입력되면 rgbint값으로 해석
			rgb = self.change_rgbint_to_rgb(input_color)
			hsl = self.change_rgb_to_hsl(rgb)

		elif type(input_color) == type([]) and len(input_color) == 3:  # 3개의 리스트형식일때는 확인해서 hsl 이나 rgb로 해석
			if input_color[0] > 255:
				hsl = input_color
			else:
				if input_color[1] > 100 or input_color[2] > 100:
					hsl = self.change_rgb_to_hsl(input_color)
				else:
					hsl = input_color
		else:
			hsl = "error"
		return hsl

	def change_input_color_to_rgb(self, input_color):
		"""
		입력된 색깔을 rgb의 리스트형태로 바꾸는 것
		xcolor모듈 대신해서, 자주사용하는 것이라 여기더 만듦

		:param input_color: 어떤 형식이라도 들어오는 색이름
		"""
		result = ""
		input_type = type(input_color)
		if input_type == type(123):
			result = self.change_rgbint_to_rgb(input_color)
		elif input_type == type("abc"):
			result = self.change_xcolor_to_rgb(input_color)
		elif input_type == type([]):
			result = input_color
		return result

	def change_input_color_to_rgbint(self, input_color):
		"""
		입력된 색깔을 rgb의 리스트형태로 바꾸는 것
		xcolor모듈 대신해서, 자주사용하는 것이라 여기더 만듦

		:param input_color: 어떤 형식이라도 들어오는 색이름
		"""
		result = ""
		input_type = type(input_color)
		if input_type == type(123):
			rgb = self.change_rgbint_to_rgb(input_color)
		elif input_type == type("abc"):
			rgb = self.change_xcolor_to_rgb(input_color)
		elif input_type == type([]):
			rgb = input_color
		result = self.change_rgb_to_rgbint(rgb)
		return result

	def change_rgb_by_sl_plusminus100(self, input_rgb, s_step="++", l_step="++"):
		"""

		:param input_rgb:
		:param s_step: s값을 단계로 나타내는 의미
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		hsl = self.change_rgb_to_hsl(input_rgb)
		step_no = 5  # 5단위씩 변경하도록 하였다
		h, s, l = hsl

		if s_step == "":
			pass
		elif s_step[0] == "+":
			s = s + len(s_step) * step_no
			if s > 100: s = 100
		elif s_step[0] == "-":
			s = s - len(s_step) * step_no
			if s < 0: s = 0

		if l_step == "":
			pass
		elif l_step[0] == "+":
			l = l + len(l_step) * step_no
			if l > 100: l = 100
		elif l_step[0] == "-":
			l = l - len(l_step) * step_no
			if l < 0: l = 0

		result = self.change_hsl_to_rgb([h, s, l])
		return result

	def change_rgb_to_12_pccs_rgb_list(self, input_rgb):
		"""
		pccs : 일본색체연구서가 빌표한 12가지 색으로 구분한것
		어떤 입력된 색의 기본적인 PCSS 12색을 돌려준다
		pccs톤, input_rgb로 넘어온 색을 pcss톤 12개로 만들어서 돌려준다

		hsl : [색상, 채도, 밝기], rgb : [빨강의 농도, 초록의 농도, 파랑의 농도]
		rgbint = input_rgb[0] + input_rgb[1] * 256 + input_rgb[2] * (256 ** 2)

		:param input_rgb:  [r,g,b]값
		:return:
		"""
		result = []
		h, s, l = self.change_rgb_to_hsl(input_rgb)
		result4 = self.varx["basic_12color_hsl"]
		for one in result4:
			result.append([h, one[0], one[1]])
		return result

	def change_rgb_to_close_56color_no(self, input_rgb):
		"""
		입력으로 들어오는 RGB값중에서 엑셀의 56가지 기본색상의 RGB값과 가장 가까운값을 찾아내는것

		:param input_rgb:
		:return:
		"""
		result = 0
		max_rgbint = 255 * 255 * 255
		var_56_rgb = self.varx["56color_vs_rgb"]

		for excel_color_no in var_56_rgb.keys():
			excel_rgb = var_56_rgb[excel_color_no]
			differ = self.calculate_distance_two_3d_point(input_rgb, excel_rgb)
			if max_rgbint > differ:
				max_rgbint = differ
				result = excel_color_no
		return result

	def change_rgb_to_close_highlight_no(self, input_rgb):
		"""
		rgb값을 주면 가강 근처의 하이라이트색으로 바꿔주는 것

		:param input_rgb:
		:return:
		"""
		result = 0
		max_rgbint = 255 * 255 * 255
		var_56_rgb = self.varx["highlight_vs_rgb"]

		for excel_color_no in var_56_rgb.keys():
			excel_rgb = var_56_rgb[excel_color_no]
			differ = self.calculate_distance_two_3d_point(input_rgb, excel_rgb)
			if max_rgbint > differ:
				max_rgbint = differ
				result = excel_color_no
		return result

	def change_rgb_to_hex(self, input_rgb, option="#"):
		"""
		엑셀의 Cells(1, i).Interior.Color는 hex값을 사용한다

		:param input_rgb: rgb형태의 값
		:return:
		"""
		r, g, b = input_rgb
		if option != "#":
			result = '0x{:02x}{:02x}{:02x}'.format(r, g, b)
		else:
			result = '#{:02x}{:02x}{:02x}'.format(r, g, b)
		return result

	def change_rgb_to_hex_rgb(self, r, g, b):
		"""
		win32에서 사용하는 색에대한 헥사코드를 만드는 것인데, 일반적인 형태와 틀려서 이렇게 만든 것이다
		:param r:
		:param g:
		:param b:
		:return:
		"""
		return (b << 16) | (g << 8) | r

	def change_rgb_to_hsl(self, input_rgb):
		"""
		input_rgb를 hsl로 바꾸는 것이다

		:param input_rgb:  [r,g,b]값
		:return:
		"""
		r = float(input_rgb[0] / 255)
		g = float(input_rgb[1] / 255)
		b = float(input_rgb[2] / 255)
		max1 = max(r, g, b)
		min1 = min(r, g, b)
		l = (max1 + min1) / 2

		if max1 == min1:
			s = 0
		elif l < 0.5:
			s = (max1 - min1) / (max1 + min1)
		else:
			s = (max1 - min1) / (2 - max1 - min1)

		if s == 0:
			h = 0
		elif r >= max(g, b):
			h = (g - b) / (max1 - min1)
		elif g >= max(r, b):
			h = 2 + (b - r) / (max1 - min1)
		else:
			h = 4 + (r - g) / (max1 - min1)
		h = h * 60
		if h > 360:
			h = h - 360
		if h < 0:
			h = 360 - h

		return [int(h), int(s * 100), int(l * 100)]

	def change_rgb_to_rgbint(self, input_rgb):
		"""
		input_rgb인 값을 color에서 인식이 가능한 정수값으로 변경하는 것
		엑셀에서는 input_rgb형태의 리스트나 정수를 사용하여 색을 지정한다

		:param input_rgb:  [r,g,b]값
		:return:
		"""
		result = int(input_rgb[0]) + (int(input_rgb[1])) * 256 + (int(input_rgb[2])) * (256 ** 2)
		return result

	def change_rgbint_to_color_name(self, rgbint):
		"""
		rgb의 정수값을 color이름으로 변경

		:param rgbint: change rgb value to int, rgb를 정수로 변환한 값
		:return:
		"""
		try:
			rgblist = self.change_rgbint_to_rgb(rgbint)
			color_index = self.change_rgb_to_close_56color_no(rgblist)
			colorname = self.change_56color_no_to_color_name(color_index)
		except:
			colorname = None
		return colorname

	def change_rgbint_to_hsl(self, input_rgbint):
		"""
		정수형태의 int값을 [h,s,l]의 리스트형태로 바꾸는 것

		:param input_rgbint: rgb의 정수값
		:return:
		"""
		rgb = self.change_rgbint_to_rgb(input_rgbint)
		hsl = self.change_rgb_to_hsl(rgb)
		return hsl

	def change_rgbint_to_rgb(self, input_rgbint):
		"""
		정수형태의 int값을 [r,g,b]의 리스트형태로 바꾸는 것

		:param input_rgbint: rgb의 정수값
		:return:
		"""
		mok0, namuji0 = divmod(input_rgbint, 256 * 256)
		mok1, namuji1 = divmod(namuji0, 256)
		result = [namuji1, mok1, mok0]
		return result

	def change_style(self, input_xcolor, style_name):
		"""
		자주 사용하는 형태라서 입력되는 색을 pccs스타일중의 하나로 변경하는 것

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param style_name:
		:return:
		"""
		hsl = self.change_xcolor_to_hsl(input_xcolor)
		plusminus100 = self.varx["check_color_step"][style_name]
		result = self.change_hsl_to_rgb_by_plusminus100(hsl, plusminus100)
		return result

	def change_xcolor_to_0xhex(self, xcolor):
		"""
		엑셀의 Cells(1, i).Interior.Color는 hex값을 사용한다

		:param input_rgb: rgb형태의 값
		:return:
		"""
		r, g, b = self.change_xcolor_to_rgb(xcolor)
		result = '0x{:02x}{:02x}{:02x}'.format(b, g, r)
		return result

	def change_xcolor_to_5_rgb_for_pastel(self, input_xcolor):
		"""
		기본적인 pastel은 [s, l] = [100, 90] 정도이다
		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return:
		"""

		result = []
		h, s, l = self._change_xcolor_to_hsl(input_xcolor)

		for strong_level in [0.97, 0.95, 0.93, 0.9, 0.87]:
			new_hsl = [h, 100 * strong_level, 90 * strong_level]
			result.append(self.change_hsl_to_rgb(new_hsl))
		return result

	def change_xcolor_to_any_color(self, input_xcolor):
		"""
		xcolor값을 왠만한 모든 색의 값으로 돌려준다

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return:
		"""
		result = {}
		rgbint = self.change_xcolor_to_rgbint(input_xcolor)
		rgb = self.change_xcolor_to_rgb(input_xcolor)
		hsl = self._change_xcolor_to_hsl(input_xcolor)
		hex = self.change_xcolor_to_hex(input_xcolor)
		color56 = self.change_rgb_to_close_56color_no(rgb)
		highlight_no = self.change_rgb_to_close_highlight_no(rgb)
		result["rgbint"] = rgbint
		result["rgb"] = rgb
		result["hsl"] = hsl
		result["hex"] = hex
		result["56color"] = color56
		result["highlight_no"] = highlight_no
		return result

	def change_xcolor_to_close_56color_no(self, input_xcolor):
		"""
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return:
		"""
		rgb_value = self.change_xcolor_to_rgb(input_xcolor)
		result = self.change_rgb_to_close_56color_no(rgb_value)
		return result

	def change_xcolor_to_hex(self, input_xcolor):
		"""
		xcolor값을 16진수인 hex로 변경하는 것
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return:
		"""
		my_rgb_color = self.change_xcolor_to_rgb(input_xcolor)
		result = self.change_rgb_to_hex(my_rgb_color)
		return result

	def change_xcolor_to_hsl(self, input_xcolor):
		"""
		입력된 자료를 기준으로 hsl값을 돌려주는것
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return: [h, s, l]
		"""
		if type(input_xcolor) == type([]):  # 리스트형태 일때는 rgb로 인식
			result = self.change_rgb_to_hsl(input_xcolor)
		else:
			[value_only, color_name, basic_l_value] = self.check_input_xcolor(input_xcolor)

			if value_only:
				h_value, s_value, l_value = self.varx["basic_18color_hsl"][int(value_only)]

			elif color_name in ["whi", "bla", "gra"]:  # 색이 흰색, 검정, 회색일 경우는 h,s는 0으로 한다
				h_value = 0
				s_value = 0
				l_code_dic = {"bla": 0, "gra": 50, "whi": 100}
				l_value = int(l_code_dic[color_name])

				if color_name == "whi":
					l_value = basic_l_value *2
				elif color_name == "gra":
					l_value = 50 + (basic_l_value - 50)
				elif color_name == "bla":
					l_value = 100 - (basic_l_value * 2)

				if l_value <= 0:
					l_value = 0
				elif l_value >= 100:
					l_value = 100

			elif color_name:
				h_value, s_value, l_value = self.varx["basic_20color_name_eng_vs_hsl"][color_name]
				l_value = basic_l_value

			if int(l_value) > 100: l_value = 100
			if int(l_value) < 0: l_value = 0
			result = [h_value, s_value, l_value]
		return result

	def change_xcolor_to_nth_near_rgb_set(self, input_xcolor="red", step=10):
		"""
		하나의 색을 지정하면 10가지의 단계로 색을 돌려주는 것이다
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param step: 단계를 나타내는 의미
		:return:
		"""
		result = []
		for no in range(0, 100, int(100 / step)):
			temp = self.change_xcolor_to_rgb(input_xcolor + str(no))
			result.append(temp)
		return result

	def change_xcolor_to_rgb(self, input_xcolor):
		"""
		xcolor값을 rgb값으로 변경
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		"""
		hsl_list = self.change_xcolor_to_hsl(input_xcolor)
		result = self.change_hsl_to_rgb(hsl_list)
		return result

	def change_xcolor_to_rgb_as_bright_by_0to1(self, input_xcolor, step1=.3):
		"""
		xcolor값을 0~1사이의 밝음정도로 색을 바꾸는 것

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param step1:
		:return:
		"""
		hsl = self._change_xcolor_to_hsl(input_xcolor)
		if step1 < 1: step1 = step1 * 100

		basic_value = hsl[2]
		max_value = 100
		changed_value = (max_value - basic_value) * step1 + basic_value

		result = [hsl[0], hsl[1], changed_value]
		return result

	def change_xcolor_to_rgb_as_dark_by_0to1(self, input_xcolor, step1=.3):
		"""
		xcolor값을 0~1사이의 어두운정도로 색을 바꾸는 것

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param step1:
		:return:
		"""
		hsl = self._change_xcolor_to_hsl(input_xcolor)
		if step1 < 1: step1 = step1 * 100

		basic_value = hsl[2]
		changed_value = basic_value * step1

		result = [hsl[0], hsl[1], changed_value]
		return result

	def change_xcolor_to_rgb_as_pastel_style_by_0to1(self, input_xcolor, step1=.3):
		"""
		** 추루 사용하지 말아주세요
		control의 의미는 입력의 자료형태를 그대로 유지하면서 미세 조정을 하는것인데, 이것은 다른 의미이므로 사용을 저제 하여 주시기 바랍니다

		level1 : 0~1사이의 값
		xcolor값을 파스텔톤으로 변경한후, 명도를 조절하는 것

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param my_value:
		:return:
		"""
		hsl = self._change_xcolor_to_hsl(input_xcolor)
		result = self.change_hsl_as_pastel_by_0to1(hsl, step1)
		return result

	def change_xcolor_to_rgb_as_pastel_style_by_1to3(self, input_xcolor, level1to3=2):
		"""
		입력받은 색의 값을 파스텔의 3가지 강도로 변경하는 방법
		level1to3 : 1~3 사이의 값

		pastel_style : ["연한", "밝은회색", "회색", "어두운회색", "옅은", "부드러운", "탁한", "어두운", "밝은", "강한", "짙은", "선명한"]
		basic_data의 self.varx["check_color_tone"] 를 이용해서 pastel_style의 공식적인 이름을 찾읍니다
		pastel의 0에서 100 : 중간값(sl) [100, 85]

		:return:
		"""
		level = [[95, 80], [100, 85], [90, 90]]  # 약, 중, 강
		hsl = self.change_xcolor_to_hsl(input_xcolor)
		h, s, l = hsl
		s = level[level1to3 - 1][0]
		l = level[level1to3 - 1][1]
		result = self.change_hsl_to_rgb([h, s, l])
		return result

	def change_xcolor_to_rgb_as_pccs_style_by_0to10(self, input_xcolor="red45", color_style="파스텔", style_step=5):
		"""
		입력된 기본 값을 스타일에 맞도록 바꾸고, 스타일을 강하게 할것인지 아닌것인지를 보는것
		xcolor형식 : 12, "red", "red45", "red++"

		입력예 : 기본색상, 적용스타일, 변화정도,("red45, 파스텔, 3)

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param color_style: pccs의 12가지 사용가능, 숫자로 사용가능, +-의 형태로도 사용가능
		:param style_step: 변화정도는 5를 기준으로 1~9까지임
		"""
		basic_hsl = self._change_xcolor_to_hsl(input_xcolor)
		checked_color_style = self.varx["check_color_tone"][color_style]

		step_2 = self.varx["basic_15tone_eng_vs_sl"][checked_color_style]
		step_1 = self.varx["sl_10_by_작은step"][style_step]

		h = int(basic_hsl[0])
		s = int(basic_hsl[1]) + int(step_1[0]) + int(step_2[0])
		l = int(basic_hsl[2]) + int(step_1[1]) + int(step_2[1])

		changed_rgb = self.change_hsl_to_rgb([h, s, l])
		return changed_rgb

	def change_xcolor_to_rgb_as_vivid_by_0to1(self, input_xcolor, step1=.3):
		"""
		** 추후 사용하지 말아주세요
		control의 의미는 입력의 자료형태를 그대로 유지하면서 미세 조정을 하는것인데, 이것은 다른 의미이므로 사용을 저제 하여 주시기 바랍니다

		vivid : 생생한, 밝은
		level1 : 0~1사이의 값

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param my_value:
		:return:
		"""
		hsl = self._change_xcolor_to_hsl(input_xcolor)
		result = self.change_hsl_for_vivid_by_0to1(hsl, step1)
		return result

	def change_xcolor_to_rgb_for_pastel_style_by_0to1(self, input_xcolor, strong_level=0.5):
		input_hsl = self.change_xcolor_to_hsl(input_xcolor)
		hsl = self.change_hsl_as_pastel_by_0to1(input_hsl, strong_level)
		rgb = self.change_hsl_to_rgb(hsl)
		return rgb

	def change_xcolor_to_rgb_with_tone(self, input_xcolor="red45", color_style="파스텔", style_step=5):
		"""
		입력된 기본 값을 스타일에 맞도록 바꾸고, 스타일을 강하게 할것인지 아닌것인지를 보는것
		color_style : pccs의 12가지 사용가능, 숫자로 사용가능, +-의 형태로도 사용가능
		입력예 : 기본색상, 적용스타일, 변화정도,("red45, 파스텔, 3)
		변화정도는 5를 기준으로 1~9까지임
		"""
		# 넘어온 자료중 color값을 hsl로 변경한다
		basic_hsl = self.change_xcolor_to_hsl(input_xcolor)
		# 스타일을 적용하는것
		aaa = self.varx["color_tone_12_names_vs_no"][color_style]
		step_2 = self.varx["sl_small_step_vs_sl_no"][aaa]
		# 스타일을 얼마나 강하게 적용할것인가를 나타내는것
		step_1 = self.varx["basic_9color_sl_big_step"][str(style_step)]

		h = int(basic_hsl[0])
		s = int(basic_hsl[1]) + int(step_1[0]) + int(step_2[0])
		l = int(basic_hsl[2]) + int(step_1[1]) + int(step_2[1])

		changed_rgb = self.change_hsl_to_rgb([h, s, l])
		return changed_rgb

	def change_xcolor_to_rgbint(self, input_xcolor):
		"""
		xcolor값을 rgbint로 변경
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		"""
		rgb_list = self.change_xcolor_to_rgb(input_xcolor)
		result = self.change_rgb_to_rgbint(rgb_list)
		return result

	def check_color_name(self, input_value):
		result = self.varx["check_color_name"][input_value]
		return result

	def check_color_name_by_rgbint(self, rgbint):
		"""
		예전 코드를 위해 남겨 놓는것

		original : change_rgbint_to_colorname
		"""
		result = self.change_rgbint_to_color_name(rgbint)
		return result

	def check_color_name_for_input_color(self, input_color):
		"""
		입력으로 들어오는 색이름을 확인해 주는 것

		:param input_list:
		:return:
		"""
		result = False
		result = self.check_color_name(input_color)
		return result

	def check_input_color(self, input_value):
		"""
		입력으로 들어오는 색을 확인하는 것
		:param input_value:
		:return:
		"""
		if type(input_value) == type([]):
			if input_value[1] > 100 or input_value[2] > 100:
				hsl = self.change_rgb_to_hsl(input_value)
			else:
				hsl = input_value
		else:
			hsl = self.check_input_xcolor(input_value)
		return hsl

	def check_input_hsl(self, input_color):
		"""
		입력으로 들어온 색에 대한 hsl값을 돌려준다

		:param input_color:
		:return:
		"""
		result = hsl = self.check_input_xcolor(input_color)
		return result

	def check_input_rgb(self, input_value):
		"""
		입력값이 rgbint인지 rgb리스트인지를 확인후 돌려주는것
		결과값 : [r,g,b]의 형식

		:param input_value: rgb의 값
		:return: [r,g,b]의 형식으로 돌려주는 것
		"""
		if type(input_value) == type(123):
			rgb = self.change_rgbint_to_rgb(input_value)
		else:
			rgb = input_value
		return rgb

	def check_input_xcolor(self, input_xcolor):
		"""
		xcolor형식의 입력값을 확인하는 것이다
		xcolor형식 : 12, "red", "red45", "red++"

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:return: ["숫자만","색이름","변화정도"] ==> ["","red","60"]
		"""
		# 잘못입력했을때를 대비하여 기본값을 넣는것
		color_name = "bla"
		l_value = 50
		value_only = None

		# 영어나 한글로 된 색깔이름을 추출
		re_com1 = re.compile("[a-zA-Z_가-힣]+")
		xcolor_color = re_com1.findall(input_xcolor)

		# xcolor에서 숫자만 추출
		re_com2 = re.compile("[0-9]+")
		xcolor_no = re_com2.findall(input_xcolor)

		# xcolor에서 + 추출
		re_com3 = re.compile("[+]+")
		xcolor_plus = re_com3.findall(input_xcolor)

		# xcolor에서 - 추출
		re_com4 = re.compile("[-]+")
		xcolor_minus = re_com4.findall(input_xcolor)

		# 숫자만 입력이 되었을때
		if xcolor_no and str(xcolor_no) == str(input_xcolor):
			value_only = int(input_xcolor)
			color_name = None
			l_value = None
		else:
			if xcolor_color:
				if xcolor_color[0] in self.varx["check_color_name"].keys():
					color_name = self.varx["check_color_name"][xcolor_color[0]]
				else:
					color_name = "not_found_" + str(xcolor_color[0])

			if xcolor_no:
				l_value = int(xcolor_no[0])
			elif xcolor_plus:
				l_value = 50 + 5 * len(xcolor_plus[0])  # +를 10개까지 사용가능하며, 숫자로 바꾸는것
			elif xcolor_minus:
				l_value = 50 - 5 * len(xcolor_minus[0])  # -를 10개까지 사용가능하며, 숫자로 바꾸는것

		return [value_only, color_name, l_value]

	def check_plusminus100(self, plusminus100):
		"""

		:param plusminus100:
		:return:
		"""
		result = ""
		if type(plusminus100) == type([]):
			result = plusminus100
		elif "+" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 밝아지도록 한다
			l_value = 10 * len(plusminus100)
			result = [0, 0, l_value]
		elif "-" == str(plusminus100)[0]:
			# 현재의 값에서 10만큼 어두워지도록 한다
			l_value = -10 * len(plusminus100)
			result = [0, 0, l_value]
		elif plusminus100 in self.varx["tone_vs_index"].keys():
			no = self.varx["tone_vs_index"][plusminus100]
			result = self.varx["basic_9color_sl_big_step"][no]
		return result

	def control_hsl(self, input_hsl, position, strength=50):
		"""
		입력된 input_hsl값의 일부분을 변경하는 것

		(고) high = 80, (중) middle = 50, (저) low=20

		:param input_hsl: [h,s,l]형식의 값
		:param position: h,s,l중에 한다
		:return:
		"""
		dic_data = {"high": 80, "middle": 50, "low": 20}

		if type(strength) == type(123):
			pass
		elif strength in dic_data.keys():
			strength = dic_data[strength]

		if position == "h":
			result = input_hsl[0] = strength
		elif position == "s":
			result = input_hsl[1] = strength
		elif position == "l":
			result = input_hsl[2] = strength
		return result

	def control_hsl_by_plusminus100(self, input_hsl, step_no):
		"""
		input_hsl값을 명도를 조정하는 방법
		+，-로 조정을 하는것이다

		:param input_hsl: [h,s,l]형식의 값
		:param step_no:
		:return:
		"""
		s, l = self.varx["색강도_vs_sl"][step_no]
		result = [input_hsl[0], input_hsl[1] + s, input_hsl[2] + l]

	def control_hsl_for_sl_by_plusminus100(self, input_hsl, s_step="++", l_step="++"):
		"""
		input_hsl값을 올리거나 내리는 것, sl의값을 조정하여 채도와 명도를 조절하는것
		입력 : [[36, 50, 50], "++", "--"]
		약 5씩이동하도록 만든다

		:param input_hsl: [h,s,l]형식의 값
		:param s_step: s값을 단계로 나타내는 의미
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		step_no = 5  # 5단위씩 변경하도록 하였다
		h, s, l = input_hsl

		if s_step == "":
			pass
		elif s_step[0] == "+":
			s = s + len(s_step) * step_no
			if s > 100: s = 100
		elif s_step[0] == "-":
			s = s - len(s_step) * step_no
			if s < 0: s = 0

		if l_step == "":
			pass
		elif l_step[0] == "+":
			l = l + len(l_step) * step_no
			if l > 100: l = 100
		elif l_step[0] == "-":
			l = l - len(l_step) * step_no
			if l < 0: l = 0

		result = self.change_hsl_to_rgb([h, s, l])
		return result

	def control_rgb_for_sl_by_plusminus100(self, input_rgb, s_step="++", l_step="++"):
		"""

		:param input_rgb:
		:param s_step: s값을 단계로 나타내는 의미
		:param l_step: l값을 단계로 나타내는 의미
		:return:
		"""
		hsl = self.change_rgb_to_hsl(input_rgb)
		step_no = 5  # 5단위씩 변경하도록 하였다
		h, s, l = hsl

		if s_step == "":
			pass
		elif s_step[0] == "+":
			s = s + len(s_step) * step_no
			if s > 100: s = 100
		elif s_step[0] == "-":
			s = s - len(s_step) * step_no
			if s < 0: s = 0

		if l_step == "":
			pass
		elif l_step[0] == "+":
			l = l + len(l_step) * step_no
			if l > 100: l = 100
		elif l_step[0] == "-":
			l = l - len(l_step) * step_no
			if l < 0: l = 0

		result = self.change_hsl_to_rgb([h, s, l])
		return result

	def control_xcolor_to_bright_style_by_0to1(self, input_xcolor, step1=.3):
		"""
		입력으로 들어오는 xcolor를 밝아지는 스타일로 조정하는 것
		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param step1:
		:return:
		"""
		hsl = self.change_xcolor_to_hsl(input_xcolor)
		if step1 < 1: step1 = step1 * 100

		basic_value = hsl[2]
		max_value = 100
		changed_value = (max_value - basic_value) * step1 + basic_value

		result = [hsl[0], hsl[1], changed_value]
		return result

	def control_xcolor_to_dark_style_by_0to1(self, input_xcolor, step1=.3):
		"""
		입력으로 들어오는 xcolor를 어두어지는 스타일로 조정하는 것

		:param input_xcolor: solor형태의 색깔입력, (12, "red", "red45", "red++")
		:param step1:
		:return:
		"""
		hsl = self.change_xcolor_to_hsl(input_xcolor)
		if step1 < 1: step1 = step1 * 100

		basic_value = hsl[2]
		changed_value = basic_value * step1

		result = [hsl[0], hsl[1], changed_value]
		return result

	def find_near_list(self, rgb_list, target_rgb):
		"""
		주어진 RGB의 형태로 만든 리스트에서
		타겟 RGB와 어느 값에 가장 가까운 RGB 값인지를 찾는것
		꼭 3차원이 아닌 4차원, 5차원의 자료들도 가능하다

		:param rgb_list:
		:param target_rgb:
		:return:
		"""
		result = None
		min_distance = float('inf')  # 파이썬에서 양의 무한대를 나타내는 방법
		for rgb in rgb_list:
			distance = self.euclidean_distance(rgb, target_rgb)
			if distance < min_distance:
				min_distance = distance
				result = rgb
		return result

	def euclidean_distance(self, point1, point2):
		"""
		n차원 공간에서 두 점 사이의 유클리드 거리를 계산합니다

		:param point1: 첫 번째 점 (리스트 또는 튜플)
		:param point2: 두 번째 점 (리스트 또는 튜플)
		:return: 두 점 사이의 유클리드 거리
		"""
		if len(point1) != len(point2):
			raise ValueError("두 점은 같은 차원이어야 합니다.")
		distance = math.sqrt(sum((p - q) * 2 for p, q in zip(point1, point2)))
		return distance

	def get_12_pccs_name(self):
		"""
		pccs(퍼스널컬러)의 영어 12가지 이름
		"""
		result = ['white', 'vivid', 'soft', 'deep', 'pale', 'gray', 'darkgrayish', 'grayish', 'lightgrayish',
				  'strong', 'light', 'bright', 'black', 'dull', 'dark']
		return result

	def get_12_pccs_name_kor(self):
		"""
		pccs(퍼스널컬러)의 한글 12가지 이름
		"""
		result = ['밝은', '기본', '파스텔', '부드러운', '검정', '연한', '탁한', '어두운', '밝은회색', '검은', '짙은', '강한', '회색', '진한', '옅은',
				  '어두운회색', '흐린', '선명한']

		return result

	def get_4_rgb_for_input_hsl_by_step_of_90h(self, input_hsl):
		"""
		360도의 색을 90도씩 변하는 4단계로 나누어서 돌려주는 것

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""
		h, s, l = input_hsl

		new_h_1 = divmod(h + 0, 360)[1]
		new_h_2 = divmod(h + 90, 360)[1]
		new_h_3 = divmod(h + 180, 360)[1]
		new_h_4 = divmod(h + 270, 360)[1]
		rgb_1 = self.change_hsl_to_rgb([new_h_1, s, l])
		rgb_2 = self.change_hsl_to_rgb([new_h_2, s, l])
		rgb_3 = self.change_hsl_to_rgb([new_h_3, s, l])
		rgb_4 = self.change_hsl_to_rgb([new_h_4, s, l])
		result = [rgb_1, rgb_2, rgb_3, rgb_4]

		return result

	def get_8_rgb_as_contrast_for_backgound_n_text(self):
		"""
		백그라운드와 텍스트용으로 대비가 높은 8개의 rgb값

		:return:
		"""
		result = [[[239, 68, 68], [255, 255, 255]],
				  [[250, 163, 27], [0, 0, 0]],
				  [[255, 240, 0], [0, 0, 0]],
				  [[130, 195, 65], [0, 0, 0]],
				  [[0, 159, 117], [255, 255, 255]],
				  [[136, 198, 237], [0, 0, 0]],
				  [[57, 75, 160], [255, 255, 255]],
				  [[231, 71, 153], [255, 255, 255]],
				  ]
		return result

	def get_all_color_name(self):
		"""
		모든 색깔의 이름들
		"""
		result = list(set(self.varx["check_color_name"].values()))
		return result

	def get_basic_12_color_name(self):
		"""
		12가지 영어 색깔이름을 돌려준다
		"""
		result = self.varx["color_12_basic"]
		return result

	def get_basic_12_color_tone_by_kor(self):
		"""
		칼라톤에 대한 한글이름
		"""
		result = self.varx["color_12_kor_basic"]
		return result

	def get_basic_12_color_tone_kor(self):
		"""
		칼라톤에 대한 한글이름
		data로 시작하는 함수는 자료를 돌려주는 목적이다
		"""
		result = self.varx["color_12_kor_basic"]
		return result

	def get_basic_12_hsl_set(self):
		"""
		12가지 hsl의 값

		:return:
		"""
		result = self.varx["basic_12color_hsl"]
		return result

	def get_basic_12_rgb_set(self):
		"""
		기본 12가지 색에 대한 rgb 리스트 값
		"""
		result = self.varx["basic_12color_rgb"]
		return result

	def get_basic_36_hsl_set(self):
		"""
		기본적인 hsl로된 36색을 갖고온다
		빨간색을 0으로하여 시작한다
		"""
		result = []
		for one in range(0, 360, 10):
			temp = [one, 100, 50]
			result.append(temp)
		return result

	def get_basic_4356_hsl_set(self):
		"""
		h : 36가지
		s : 11단계
		l : 11단계
		총 4356개의 색집합

		:return:
		"""
		result = {}
		for h in range(0, 360, 10):
			for s in range(0, 110, 10):
				for l in range(0, 110, 10):
					temp = self.change_hsl_to_rgb([h, s, l])
					result[str(h) + str("_") + str(s) + str("_") + str(l)] = temp
		return result

	def get_basic_46_excel_rgb_set(self):
		"""
		엑셀 기본 46 rgb 값
		"""
		result = self.varx["rgb_46_for_excel46"]
		return result

	def get_basic_56_excel_rgb_set(self):
		"""
		엑셀 기본 56 rgb 값
		"""
		result = self.varx["rgb_56_for_excel56"]
		return result

	def get_basic_8_pastel_rgb_set(self):
		"""
		기본적인 자료가 있는 색들의 배경색으로 사용하면 좋은 색들
		"""
		color_set = self.varx["basic_12color_hsl"][:-4]
		result = []
		for hsl_value in color_set:
			rgb = self.change_xcolor_to_rgb_as_pccs_style_by_0to10(hsl_value, "pastel", 4)
			result.append(rgb)
		return result

	def get_contrast_2set_8(self):
		"""
		대비가 잘되는 8가지 배경과 텍스트를 위한 색조합
		data로 시작하는 함수는 자료를 돌려주는 목적이다
		"""
		result = [[[239, 68, 68], [255, 255, 255]],
				  [[250, 163, 27], [0, 0, 0]],
				  [[255, 240, 0], [0, 0, 0]],
				  [[130, 195, 65], [0, 0, 0]],
				  [[0, 159, 117], [255, 255, 255]],
				  [[136, 198, 237], [0, 0, 0]],
				  [[57, 75, 160], [255, 255, 255]],
				  [[231, 71, 153], [255, 255, 255]],
				  ]
		return result

	def get_contrast_by_backgound_n_text_8_color_set(self):
		"""
		색의 대비가 잘되는 8개의 색 조합돌려주는 것

		:return:
		"""

		result = [[[239, 68, 68], [255, 255, 255]],
				  [[250, 163, 27], [0, 0, 0]],
				  [[255, 240, 0], [0, 0, 0]],
				  [[130, 195, 65], [0, 0, 0]],
				  [[0, 159, 117], [255, 255, 255]],
				  [[136, 198, 237], [0, 0, 0]],
				  [[57, 75, 160], [255, 255, 255]],
				  [[231, 71, 153], [255, 255, 255]],
				  ]
		return result

	def get_hilight_7(self):
		"""
		하이라이트로 사용가능할 만한 7가지 색을 만든것
		data로 시작하는 함수는 자료를 돌려주는 목적이다
		"""
		result = [[240, 117, 117], [240, 178, 117], [240, 240, 117], [178, 240, 117], [117, 240, 118], [117, 240, 179], [117, 239, 240]]
		return result

	def get_hsl_set_for_12_pccs(self, hsl):
		"""
		12가지 스타일의 hsl을 돌려주는 것이다

		:param hsl: [h,s,l]형식의 값
		"""
		result = []
		for one_value in self.varx["basic_12color_hsl"]:
			temp = self.change_hsl_to_rgb([hsl[0], one_value[0], one_value[1]])
			result.append(temp)
		return result

	def get_name_set_for_cool_style(self):
		"""
		차가운 색깔의 이름들
		"""
		result = ["파랑", "초록", "보라"]
		return result

	def get_name_set_for_worm_style(self):
		"""
		따뜻한 색깔의 이름들

		:return:
		"""
		result = ["빨강", "주황", "노랑"]
		return result

	def get_nea_rgb_set(self, input_no=36):
		"""
		입력된 숫자만큼, rgt리스트를 갖고오는것
		기본적인 hsl로된 36색을 갖고온다
		빨간색을 0으로하여 시작한다
		결과값 : hsl

		:param input_no:
		:return:
		"""
		result = []
		for one in range(0, 360, int(360 / input_no)):
			temp = self.change_hsl_to_rgb([one, 100, 50])
			result.append(temp)
		return result

	def get_nth_hsl_from_input_hsl_by_step_of_h(self, input_hsl, input_nth=10):
		"""
		입력으로 들어온 input_hsl값의 h를 n개로 나누어서 만들어 주는 것
		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		for no in range(1, 361, input_nth):
			temp = [no, input_hsl[1], input_hsl[2]]
			result.append(temp)
		return result

	def get_nth_hsl_from_input_hsl_by_step_of_l(self, input_hsl, input_nth=10):
		"""
		입력으로 들어온 input_hsl값의 l를 n개로 나누어서 만들어 주는 것

		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		step = int(100 / input_nth)
		for no in range(1, 101, step):
			temp = [input_hsl[0], input_hsl[1], no]
			result.append(temp)
		return result

	def get_nth_hsl_from_input_hsl_by_step_of_s(self, input_hsl, input_nth=10):
		"""
		입력으로 들어온 input_hsl값의 s를 n개로 나누어서 만들어 주는 것

		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		step = int(100 / input_nth)
		for no in range(1, 101, step):
			temp = [input_hsl[0], no, input_hsl[2]]
			result.append(temp)
		return result

	def get_nth_rgb_between_xcolor1_to_xcolor2_by_step(self, xcolor_1, xcolor_2, step=10):
		"""
		두가지색을 기준으로 몇단계로 색을 만들어주는 기능
		예를들어, 발강 ~파랑사이의 색을 10단계로 만들어 주는 기능

		:param xcolor_1:
		:param xcolor_2:
		:param step: 단계를 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_xcolor_to_rgb(xcolor_1)
		rgb_2 = self.change_xcolor_to_rgb(xcolor_2)
		r_step = int((rgb_2[0] - rgb_1[0]) / step)
		g_step = int((rgb_2[1] - rgb_1[1]) / step)
		b_step = int((rgb_2[2] - rgb_1[2]) / step)
		result = [rgb_1, ]
		for no in range(1, step - 1):
			new_r = int(rgb_1[0] + r_step * no)
			new_g = int(rgb_1[1] + g_step * no)
			new_b = int(rgb_1[2] + b_step * no)
			result.append([new_r, new_g, new_b])
		result.append(rgb_2)
		return result

	def get_nth_rgb_by_step_of_h(self, input_no=36):
		"""
		입력된 숫자만큼, rgt리스트를 갖고오는것
		기본적인 hsl로된 36색을 갖고온다
		빨간색을 0으로하여 시작한다
		결과값 : hsl

		:param input_no:
		:return:
		"""
		result = []
		for one in range(0, 360, int(360 / input_no)):
			temp = self.change_hsl_to_rgb([one, 100, 50])
			result.append(temp)
		return result

	def get_nth_rgb_from_input_hsl_by_step_of_h(self, input_hsl, input_nth=10):
		"""
		입력으로 들어오는 갯수만큼의 h값을 변화시키면서 만드는 것
		sl은 그대로를 유지한다
		결과값 : rgb

		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		for no in range(1, 361, input_nth):
			temp = self.change_hsl_to_rgb([no, input_hsl[1], input_hsl[2]])
			result.append(temp)
		return result

	def get_nth_rgb_from_input_hsl_by_step_of_l(self, input_hsl, input_nth=10):
		"""
		입력으로 들어오는 갯수만큼의 l값을 변화시키면서 만드는 것
		sl은 그대로를 유지한다
		결과값 : rgb

		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		for no in range(1, 101, input_nth):
			temp = self.change_hsl_to_rgb([input_hsl[0], input_hsl[1], no])
			result.append(temp)
		return result

	def get_nth_rgb_from_input_hsl_by_step_of_s(self, input_hsl, input_nth=10):
		"""
		입력으로 들어오는 갯수만큼의 s값을 변화시키면서 만드는 것
		sl은 그대로를 유지한다
		결과값 : rgb

		:param input_hsl:
		:param input_nth:
		:return:
		"""
		result = []
		for no in range(1, 101, input_nth):
			temp = self.change_hsl_to_rgb([input_hsl[0], no, input_hsl[2]])
			result.append(temp)
		return result

	def get_rgb_by_bo_style_for_input_hsl(self, input_hsl):
		"""
		입력된 input_hsl에 대한 보색을 알려주는것
		보색 : Complementary
		2차원 list의 형태로 돌려줌

		:param input_hsl: [h,s,l]형식의 값
		:return:
		"""

		new_h = divmod(input_hsl[0] + 180, 360)[1]
		result = self.change_hsl_to_rgb([new_h, input_hsl[1], input_hsl[2]])
		return [result]

	def get_rgb_for_input_pxy(self, input_pxy=""):
		"""
		pyclick에 같은 것 있음

		입력으로 들어오는 pxy위치의 rgb값을 갖고온다
		만약 "" 이면, 현재 마우스가 위치한곳의 rgb를 갖고온다
		:param input_pxy:
		:return:
		"""
		if input_pxy:
			x, y = input_pxy
		else:
			x, y = pyautogui.position()
		r, g, b = pyautogui.pixel(x, y)
		return [r, g, b]

	def get_rgb_set_for_12_pastel_color(self):
		"""
		12개의 파스텔톤의  rgb값을 돌려주는 것
		:return:
		"""
		result = []
		for num in range(0, 360, 30):
			result.append(self.change_hsl_to_rgb([num, 90, 80]))
		return result

	def get_rgb_set_for_faber(self, start_color=11, code=5):
		"""
		파버 비덴의의 색체 조화론을 코드로 만든것이다
		한가지 색에대한 조화를 다룬것

		White(100-0) - Tone(10-50) - Color(0-0) : 색이 밝고 화사
		Color(0-0) - Shade(0-75) - Black(0-100) : 색이 섬세하고 풍부
		White(100-0) - GrayGray(25-75) - Black(0-100) : 무채색의 조화
		Tint(25-0) - Tone(10-50) - Shade(0-75) 의 조화가 가장 감동적이며 세련됨
		White(100-0) - Color(0-0) - Black(0-100) 는 기본적인 구조로 전체적으로 조화로움
		Tint(25-0) - Tone(10-50) - Shade(0-75) - Gray(25-75) 의 조화는 빨강, 주황, 노랑, 초록, 파랑, 보라와 모두 조화를 이룬다

		:param start_color:
		:param code:
		:return:
		"""
		h_list = self.varx["basic_12color_hsl"]
		sl_faber = self.varx["faber_to_sl"]

		h_no = h_list[start_color][0]
		result = []
		temp_hsl = sl_faber[code]
		for one_sl in temp_hsl:
			rgb = self.change_hsl_to_rgb([h_no, one_sl[0], one_sl[1]])
			result.append(rgb)
		return result

	def get_rgb_set_for_high_contrast(self):
		"""
		대비가 좋은색 10개를 보여드리는 것입니다(배경색, 폰트)

		:return:
		"""
		rgb_list = [[[0, 0, 0], [255, 255, 255]],
					[[255, 255, 255], [0, 0, 0]],
					[[0, 0, 255], [255, 255, 0]],
					[[255, 255, 0], [0, 0, 255]],
					[[255, 0, 0], [255, 255, 255]],
					[[0, 128, 0], [255, 255, 255]],
					[[128, 0, 128], [255, 255, 255]],
					[[139, 0, 0], [255, 255, 255]],
					[[255, 165, 0], [0, 0, 0]],
					[[0, 100, 0], [255, 255, 255]]
					]
		return rgb_list

	def get_rgb_set_for_johannes(self, start_color=11, num_color=4, stongness=5):
		"""
		요하네스 이텐의 색체 조화론을 코드로 만든것이다

		:param start_color: 처음 시작하는 색 번호, 총 색은 12색으로 한다
		:param num_color: 표현할 색의 갯수(2, 3, 4, 6만 사용가능)
		:param stongness: 색의 농도를 나타내는 것, 검정에서 하양까지의 11단계를 나타낸것, 중간이 5이다
		:return:
		"""
		h_list = self.varx["basic_12color_hsl"]
		sl_list = self.varx["sl11_step"]
		hsl_johannes = self.varx["johannes_to_hsl"]
		color_set = [[], [], [0, 6], [0, 5, 9], [0, 4, 7, 10], [0, 3, 5, 8, 10], [0, 3, 5, 7, 9, 11]]

		h_no = h_list[start_color][0]
		new_color_set = []
		for temp in color_set[num_color]:
			new_color_set.append((temp + int(h_no / 30)) % 12)

		result = []
		for no in new_color_set:
			temp_hsl = hsl_johannes[no][stongness]
			rgb = self.change_hsl_to_rgb(temp_hsl)
			result.append(rgb)
		return result

	def is_xcolor_style(self, input_xcolor):
		"""
		xcolor용
		입력된 자료의 형태가, xcolor형식인지를 확인하는 것
		"""
		rex = xy_re.xy_re()
		result1 = rex.is_match_all("[한글&영어:2~10][숫자:0~7]", str(input_xcolor))
		result2 = rex.is_match_all("[한글&영어:2~10][+-:0~7]", str(input_xcolor))
		if result1 and result2:
			result = result1
		elif result1 and not result2:
			result = result1
		elif not result1 and result2:
			result = result2
		elif not result1 and not result2:
			result = False

		return result

	def split_two_xcolor_to_nth_rgb(self, xcolor_1, xcolor_2, step=10):
		"""
		두가지색을 기준으로 몇단계로 색을 만들어주는 기능
		예를들어, 발강 ~파랑사이의 색을 10단계로 만들어 주는 기능

		:param xcolor_1:
		:param xcolor_2:
		:param step: 단계를 나타내는 의미
		:return:
		"""
		rgb_1 = self.change_xcolor_to_rgb(xcolor_1)
		rgb_2 = self.change_xcolor_to_rgb(xcolor_2)
		r_step = int((rgb_2[0] - rgb_1[0]) / step)
		g_step = int((rgb_2[1] - rgb_1[1]) / step)
		b_step = int((rgb_2[2] - rgb_1[2]) / step)
		result = [rgb_1, ]
		for no in range(1, step - 1):
			new_r = int(rgb_1[0] + r_step * no)
			new_g = int(rgb_1[1] + g_step * no)
			new_b = int(rgb_1[2] + b_step * no)
			result.append([new_r, new_g, new_b])
		result.append(rgb_2)
		return result

	def change_56color_to_color_name(self, input_56color):
		"""
		엑셀의 기본 56색의 번호에 대한 색의 이름

		:param input_56color:
		:return:
		"""
		result = self.colorx.change_56color_no_to_color_name(input_56color)
		return result

	def change_56color_to_rgb(self, input_56color):
		"""
		엑셀의 기본 56색의 번호에 rgb값을 갖고오는 것

		:param input_56color:
		:return:
		"""
		result = self.change_56color_to_rgb(int(input_56color))
		return result

	def change_56color_to_rgbint(self, input_56color):
		"""
		엑셀의 56가지 색번호 => rgb int값

		:param input_56color: 엑셀의 56가지 색번호
		"""
		rgb = self.change_56color_no_to_rgb(input_56color)
		result = self.colorx.change_rgb_to_rgbint(rgb)
		return result


