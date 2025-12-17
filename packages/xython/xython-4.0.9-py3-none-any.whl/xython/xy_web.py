# -*- coding: utf-8 -*-
import time
import xy_re, xy_util

# from webdriver_manager.chrome import ChromeDriverManager # 크롬 드라이버 설치
from selenium.webdriver.chrome.service import Service  # 자동적 접근
from selenium.webdriver.chrome.options import Options  # 크롭 드라이버 옵션 지정
from selenium.webdriver.common.by import By  # find_element 함수 쉽게 쓰기 위함
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options


class xy_web:
	"""
	셀레니움과 자바스크립트를 쉽게 사용이 가능하도록 만드는것
	"""
	def __init__(self, input_url="", sleep_sec=30):

		#공통 변수들을 설정한다
		self.utilx = xy_util.xy_util()
		self.rex = xy_re.xy_re()

		self.varx_all_tag_name = ["checkbox", "div", "footer", "form", "head", "header", "i","iframe",
					 "img","input","li", "link", "meta", "nav", "ul", "ol", "a", "body",
					 "br", "button", "p", "span", "strong", "style", "table",
					 "td", "th", "title", "tr" ]

		self.varx_all_key_enum = {"ALT": Keys.ALT, "ARROW_DOWN": Keys.ARROW_DOWN, "ARROW_LEFT": Keys.ARROW_LEFT,
					"ARROW_RIGHT": Keys.ARROW_RIGHT, "ARROW_UP": Keys.ARROW_UP,
					"LEFT": Keys.LEFT, "LEFT_ALT": Keys.LEFT_ALT, "LEFT_CONTROL": Keys.LEFT_CONTROL,
					"LEFT_SHIFT": Keys.LEFT_SHIFT, "RIGHT": Keys.RIGHT, "SHIFT": Keys.SHIFT}

		self.select_obj = None

		#크롬의 옵션을 설정하는 것
		chrome_options = Options()
		chrome_options.add_experimental_option("detach", True)
		chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
		chrome_options.add_experimental_option("useAutomationExtension", False)
		chrome_options.add_argument("--disable-notifications") #알림 비활성화
		chrome_options.add_argument("--disable-infobars") #정보 표시 비활성화
		#chrome_options.add_argument("--disable-popup-blocking") #팝업차단 비활성화

		if input_url:
			self.driver = webdriver.Chrome(options = chrome_options)  # 크롬의 웹드라이버를 실행
			self.driver.get(input_url)

		if sleep_sec:
			time.sleep(sleep_sec)

	def border_outline(self, input_dic):
		result = ""
		if "position" in input_dic.keys():
			if input_dic["position"] == "bottom":
				result = result + "border-bottom :"
		if "thickness" in input_dic.keys():
			result = result + "border-width : " + self.margin_or_padding(input_dic["thickness"]) + "; "
		if "style" in input_dic.keys():
			result = result + "border-style : " + input_dic["style"] + "; "
		if "color" in input_dic.keys():
			result = result + "border-color : " + input_dic["color"] + "; "
		if "radius" in input_dic.keys():
			result = result + "border-radius : " + self.margin_or_padding(input_dic["radius"]) + "; "
		return result

	def change_attribute_only_input_time(self, input_path, input_text, input_time):
		"""
		어떤 속성을 바꾼후에 몇초뒤에 다시 원상태로 바꾸는 기능

		:param input_path:
		:param input_text:
		:param input_time:
		:return:
		"""
		script = "return " + str(input_path) + ";"
		result = self.driver.execute_script(script)

		script = str(input_path) + " = " + "'" + str(input_text) + "';"
		self.driver.execute_script(script)
		print("sleep 시작 =================>")
		time.sleep(input_time)

		script = str(input_path) + " = " + "'" + str(result) + "';"
		self.driver.execute_script(script)
		print(result)

		return result

	def check_1(self):
		# 모든 창의 핸들 가져오기
		window_handles = self.driver.window_handles
		# 모든 창의 핸들 출력
		for handle in window_handles:
			self.driver.switch_to.window(handle)
			title = self.driver.title

		if title == "안전하지 않은 양식":
			abc = self.search_by_id("proceed-button")
			abc.click()

	def check_nth(self, input_text):
		"""
		[3, "2n+1", "nth-child(3)","nth-child(3~5)", "t(2n+1)", "c(2n+1)"]

		:param input_text:
		:return:
		"""
		print(input_text)
		input_text = str(input_text)
		if "(" in input_text and "~" in input_text:
			head, num = input_text.split("(")
			head, num = head[:-1], num[:-1]
			start, end = str(num).split("~")

			temp1 = self.check_nth_option("+" + str(start))
			temp2 = self.check_nth_option("-" + str(end))
			if input_text.startswith("nth-child") or input_text.startswith("c"):
				result = "nth-child(" + temp1 + "):" + "nth-child(" + temp2 + ")"
			elif input_text.startswith("nth-of-type") or input_text.startswith("t"):
				result = "nth-of-type(" + temp1 + "):" + "nth-of-type(" + temp2 + ")"

		# ["nth-child(3)", "t(2n+1)", "c(2n+1)"]
		elif "(" in input_text and not "~" in input_text:
			head, num = input_text.split("(")
			num = num[:-1]

			try:
				start = int(num)
				if start == 0:
					result = "first-child"
				elif start == -1:
					result = "last-child"
				elif start < -1:
					result = "nth-last-child(" + str(int(start * -1)) + ")"
				elif start > 0:
					if input_text.startswith("nth-child") or input_text.startswith("c"):
						result = "nth-child(" + num + ")"
					elif str(input_text).startswith("nth-of-type") or input_text.startswith("t"):
						result = "nth-of-type(" + num + ")"

			except:
				if input_text.startswith("only-child"):
					result = "only-child"
				elif input_text.startswith("empty"):
					result = "empty"
				elif input_text.startswith("nth-child") or input_text.startswith("c"):
					result = "nth-child(" + num + ")"
				elif str(input_text).startswith("nth-of-type") or input_text.startswith("t"):
					result = "nth-of-type(" + num + ")"

			# [3, "2n+1"]
		elif not "(" in input_text and not "~" in input_text:
			result = "nth-child(" + input_text + "):"

		return result

	def check_nth_option(self, input_text):
		"""

		:param input_text:
		:return:
		"""
		is_num = self.rex.is_number_only(input_text)

		if is_num:
			result = input_text
		elif input_text == "even":
			result = "2n"
		elif input_text == "odd":
			result = "2n+1"
		elif input_text.startswith("+"):
			result = "n+" + input_text[1:]
		elif input_text.startswith("-"):
			result = "-n+" + input_text[1:]
		elif "n" in input_text:
			result = input_text
		else:
			result = False
		return result

	def check_pixel(self, input_value):
		"""
		px단위가 없는 것은 집어 넣는 것이다

		:param input_value:
		:return:
		"""
		if type(input_value) == type(123):
			result = str(input_value) + "px"
		elif type(input_value) == type("abc") and input_value.endswith("px"):
			result = input_value
		else:
			result = str(input_value) + "px"
		return result

	def make_style_by_dic(self, option_dic):
		"""
		자바스크립트에서 사용되는 style을 사전형식으로 입력하면 만들어지는 것이다
		모양을 나타내는 부분
		사전형태

		:param option_dic:
		:return:
		"""
		style = ""
		all_keys = list(option_dic.keys())
		if "size" in option_dic.keys():
			temp = self.check_pixel(option_dic["size"])
			style = style + "font-size: " + temp + ";"
		if "align" in all_keys: style = style + "font-align: " + option_dic["align"] + ";"
		if "bold" in all_keys: style = style + "font-weight:bold;"
		if "color" in all_keys: style = style + "color: " + option_dic["color"] + ";"
		if "collapse" in all_keys: style = style + "borser-collapse: " + option_dic["collapse"] + ";"
		if "background" in all_keys: style = style + "background-color: " + option_dic["background"] + ";"
		if "width" in all_keys: style = style + "width: " + self.check_pixel(option_dic["width"]) + ";"
		if "padding" in all_keys: style = style + "padding: " + option_dic["padding"] + ";"
		if "border" in all_keys: style = style + self.border_outline(option_dic["border"])
		return style

	def check_text_outline(self, input_text):
		"""
		글자의 외곽선을 그리기
		입력으로 들어온 텍스트를 분리 => 3가지 종류로 확인 => 다시 올바른 text로 만듦
		temp = ["1", "solid", "; "]

		:param input_text:
		:return:
		"""
		temp = [" ", " ", "; "]
		line_style_dic = {"solid": "solid", "dotted": "dotted", "dot": "dotted", "dashed": "dashed", "dash": "dashed",
						  "double": "double", "outset": "outset", "inset": "inset", "groove": "groove",
						  "ridge": "ridge",
						  "": "solid", ".": "dotted", "--": "dashed", "=": "double"}
		input_list = input_text.split()
		input_list_1 = list(input_list)
		for one in input_list:
			aaa = self.rex.search_all_by_xsql("[숫자:1~][단어(px):0~1]", one)
			if aaa:
				temp[0] = aaa[0][0]
				input_list_1.remove(one)

			if one in line_style_dic.keys():
				temp[1] = line_style_dic[one]
				input_list_1.remove(one)

		if input_list_1:
			temp[2] = input_list_1[0] + "; "

		result = self.utilx.change_list_1d_to_text_with_chain_word(temp, " ")
		return result

	def click_input_obj(self, input_obj):
		"""
		입력으로 들어오는 객체의 click이벤트를 실행한다

		:param input_obj:
		:return:
		"""
		input_obj.click()

	def click_button(self):
		"""
		선택한 객체를 클릭하는 것
		:return:
		"""
		self.select_obj.click()

	def click_searched_item(self):
		"""
		선택한 객체를 클릭하는 것

		:return:
		"""
		self.select_obj.click()

	def click_selected_obj(self):
		"""
		선택한 객체를 클릭하는 것

		:return:
		"""
		self.select_obj.click()

	def close(self):
		"""

		:return:
		"""
		btnSave = self.driver.find_element(By.ID, "divpop_close")
		self.driver.execute_script('arguments[0].click();', btnSave)

	def close_iframe(self):
		"""

		:return:
		"""
		isLoad = False
		for i in range(1, 5):
			try:
				document = self.driver.find_elements(By.CLASS_NAME, 'layer_divpop ui-draggable')[0]
				self.driver.switch_to.frame(document)
				self.driver.close()
			except:
				print('XXX화면이 로딩되지 않았습니다. 2초 뒤에 재시도 합니다...')
				self.driver.switch_to.default_content()
				time.sleep(2)
				pass
		if not isLoad:
			print('XXX화면을 찾지 못하였습니다')
		return

	def close_popup_in_worksite(self):
		"""
		현재 열려 있는 창의 개수 출력
		window_handles = self.driver.window_handles
		print(f"현재 열려 있는 창의 개수: {len(window_handles)}")

		:return:
		"""
		

		# 모든 창의 핸들 가져오기
		window_handles = self.driver.window_handles

		# 모든 창의 핸들 출력
		print("All window handles:")
		for handle in window_handles:
			self.driver.switch_to.window(handle)
			# 현재 창의 제목 가져오기
			title = self.driver.title
			# 창의 핸들과 제목 출력
			print(f"Handle: {handle}, Title: {title}")
		popup_layers = self.driver.find_elements(By.CSS_SELECTOR, '.divpop_close')
		print(len(popup_layers))
		if len(popup_layers) > 0:
			for popup_layer in popup_layers:
				# element = self.driver.find_element(By.CSS_SELECTOR, '#divPortalBoardPopUP0_px.divpop_close')
				# 요소 클릭
				popup_layer.click()

	def close_popup_in_worksite_1(self):
		"""

		:return:
		"""
		# 현재 열려 있는 창의 개수 출력
		# window_handles = self.driver.window_handles
		# print(f"현재 열려 있는 창의 개수: {len(window_handles)}")

		# 모든 창의 핸들 가져오기
		window_handles = self.driver.window_handles

		# 모든 창의 핸들 출력
		print("All window handles:")
		for handle in window_handles:
			self.driver.switch_to.window(handle)
			# 현재 창의 제목 가져오기
			title = self.driver.title
			# 창의 핸들과 제목 출력
			print(f"Handle: {handle}, Title: {title}")
			popup_layers = self.driver.find_elements(By.CSS_SELECTOR, '.dhxwin_button_close')[0].click()
		# print(len(popup_layers))
		# if len(popup_layers) > 0:
		# for popup_layer in popup_layers:
		# element = self.driver.find_element(By.CSS_SELECTOR, '#divPortalBoardPopUP0_px.divpop_close')
		# 요소 클릭
		# print(popup_layer.text)
		# popup_layer.click()

	def count_iframe(self):
		"""

		:return:
		"""

		# self.driver.switch_To().frame
		aaa = self.driver.switch_to.active_element
		# bbb = self.driver.find_element(By.CLASS_NAME, 'dhx_cell_wins')

		# chkboxes = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")

		# chkboxes.click()

		# self.driver.find_elements(By.CSS_SELECTOR, '.dhxwin_button_close')[0].click()

		print("현재 사이트의 타이틀 => ", self.driver.title)

		# iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
		# iframe의 개수 출력
		# iframe = self.driver.find_elements(By.TAG_NAME, 'iframe')
		# count = len(iframes)
		# 각 iframe의 title 속성 가져오기
		# for index, iframe in enumerate(iframes):
		# try:
		# self.driver.switch_to.frame(iframe)
		# print("iframe의 갯수 => ", len(iframes), "title => ", self.driver.title)
		# except:
		# pass
		# count += self.count_iframe()
		# self.driver.switch_to.parent_frame()
		# print(self.driver.title)
		# return count

	def count_tag_name(self):
		"""


		:return:
		"""
		iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
		# iframe의 개수 출력
		print(f"iframe의 개수: {len(iframes)}")
		# iframe = self.driver.find_elements(By.TAG_NAME, 'iframe')
		count = len(iframes)
		# 각 iframe의 title 속성 가져오기
		for index, iframe in enumerate(iframes):
			self.driver.switch_to.frame(iframe)
			print(index, self.driver.title)
			count += self.count_tag_name()
			self.driver.switch_to.parent_frame()
		return count

	def delete_all_value_in_text_box(self):
		"""

		:return:
		"""
		self.select_obj.clear()
		return self.select_obj

	def get_all_attribute(self, input_ele):
		"""
		어떤 객체의 모든 속성을 갖고오는 것

		:param input_ele:
		:return:
		"""
		script = '''
		var items = {};
		for (index = 0; index < arguments[0].attributes.length; ++index) {
		items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
		};
		return items;
		'''
		attributes = self.driver.execute_script(script, input_ele)

		# 모든 속성 출력
		for attr, value in attributes.items():
			print(f'{attr}: {value}')

	def get_size_n_xy_for_element(self, input_ele):
		"""
		어떤 요소의 위치를 돌려주는것
		자바스크립트에 객체를 전달하는 방법은 var input_ele = arguments[0] 이런식을 사용한다

		:param input_ele:
		:return:
		"""
		xy = input_ele.location
		size = input_ele.size

		js_script = """
		var input_ele = arguments[0];
		var rect = input_ele.getBoundingClientRect();
		return { left: rect.left, top: rect.top };
		"""
		xyxy = self.driver.execute_script(js_script, input_ele)

		return [xy, size, xyxy]

	def get_title(self):
		"""
		웹의 제목을 갖고오는 것

		:return:
		"""
		result = self.driver.title
		return result

	def get_value_for_full_path(self, input_path):
		"""
		어떤 객체의 속성값을 갖고오는 방법
		document.body.style.background 와 같이 사용하는 형식입니다

		:param input_path:
		:return:
		"""
		script = "return " + str(input_path) + ";"
		result = self.driver.execute_script(script)
		print(result)

		return result

	def make_css(self, selector, style):
		"""

		:param selector:
		:param style:
		:return:
		"""
		aaa = self.make_selector(selector)
		bbb = self.make_style_by_dic(style)
		return aaa + "{" + bbb + "}"

	def make_selector(self, i_l1d):
		"""
		selector는 너무 다양해서, 가능하면 3부분으로 분리

		:param i_l1d:
		:return:
		"""
		result = ""

		# 제일 앞의것을 리스트형태로 변경
		if type(i_l1d[0]) != type([]): i_l1d[0] = [i_l1d[0]]

		for one in i_l1d[0]:
			result = result + one + " "
		result = result[:-1]

		if i_l1d[1]:
			result = result + "::" + self.check_nth(str(i_l1d[1]))

		if i_l1d[2]:
			result = result + str(i_l1d[2])
		return result

	def margin_or_padding(self, *input_list):
		"""

		:param input_list:
		:return:
		"""
		result = ""
		if len(input_list) == 1:
			result = input_list[0] + " " + input_list[0] + " " + input_list[0] + " " + input_list[0]
		elif len(input_list) == 2:
			result = input_list[0] + " " + input_list[1] + " " + input_list[0] + " " + input_list[1]
		elif len(input_list) == 3:
			result = input_list[0] + input_list[1] + " " + input_list[2] + " " + input_list[1]
		elif len(input_list) == 4:
			result = input_list
		return result

	def move_obj_to_up(self, input_elem):
		"""

		:param input_elem:
		:return:
		"""
		pass

	def move_site(self, input_url):
		"""
		입력한 웹사이트로 이동하는 것

		:param input_url:
		:return:
		"""
		self.driver.get(input_url)

	def move_to_main_window(self):
		"""

		:return:
		"""
		self.driver.switch_to.default_content()

	def new_obj(self, input_tag):
		"""

		:param input_tag:
		:return:
		"""

		script = 'let new_obj =;'
		self.driver.execute_script(script)

	def run_javascript(self, js_code):
		"""
		자바스크립트를 실행시키기 위한것

		:param js_code:
		:return:
		"""
		self.driver.execute_script(js_code)

	def scroll_screen(self, xy_list=[0, 200]):
		"""
		마우스로 스크롤을 움직이는 기능

		:param xy_list:
		:return:
		"""
		self.driver.execute_script(f"window.scrollTo({xy_list[0]}, {xy_list[1]});")
		last_height = self.driver.execute_script("return document.body.scrollHeight")
		print(last_height)

	def search_nth_item_for_listitem(self, input_no=1):
		"""

		:param input_no:
		:return:
		"""
		listitem = Select(self.driver.find_element(By.NAME, 'pets'))
		listitem.search_by_index(input_no)
		listitem.search_by_visible_text('Cat')
		listitem.search_by_value('hamster')

	def search_all_obj_by_tag_name(self, input_tag_name):
		"""
		태그이름으로 모든 요소를 찾는것
		
		:param input_tag_name: 
		:return: 
		"""
		input_tag_name = str(input_tag_name).lower()
		if input_tag_name in self.varx_all_tag_name:
			self.select_all_obj = self.driver.find_elements(By.TAG_NAME, input_tag_name)
		return self.select_all_obj

	def search_all_obj_by_class_name(self, input_class_name):
		"""
		클래스 이름으로 모든 요소를 찾는것
		
		:param input_class_name: 
		:return: 
		"""
		input_class_name = str(input_class_name).lower()
		self.select_all_obj = self.driver.find_elements(By.CLASS_NAME, input_class_name)
		return self.select_all_obj

	def search_all_obj_by_css_selector(self, input_selector):
		"""
		css selector에서 맞는 모든 객체를 돌려준다

		:param input_selector:
		:return:
		"""
		input_selector = str(input_selector).lower()
		self.select_all_obj = self.driver.find_elements(By.CSS_SELECTOR, input_selector)
		return self.select_all_obj

	def search_all_obj_by_full_link_text(self, input_full_link_text):
		"""
		링크된 텍스트에서 모든 텍스트가 맞는 모든 객체를 찾는 것

		:param input_full_link_text:
		:return:
		"""
		input_full_link_text = str(input_full_link_text).lower()
		self.select_all_obj = self.driver.find_elements(By.LINK_TEXT, input_full_link_text)
		return self.select_all_obj

	def search_all_obj_by_id(self, input_id):
		"""
		id중에서 찾은 모든 객체를 찾는 것

		:param input_id:
		:return:
		"""
		input_id = str(input_id).lower()
		self.select_all_obj = self.driver.find_elements(By.ID, input_id)
		return self.select_all_obj

	def search_all_obj_by_link_text(self, input_link_text):
		"""
		링크로된 text중에서 맞는 것중에서 모든것을 돌려주는 것

		:param input_link_text:
		:return:
		"""
		input_link_text = str(input_link_text).lower()
		self.select_all_obj = self.driver.find_elements(By.ID, input_link_text)
		return self.select_all_obj

	def search_all_obj_by_name(self, input_name):
		"""
		이름으로 적합한 모든 객체를 찾는 것

		:param input_name:
		:return:
		"""
		input_name = str(input_name).lower()
		self.select_all_obj = self.driver.find_elements(By.NAME, input_name)
		return self.select_all_obj

	def search_all_obj_by_partial_link_text(self, input_partial_link_text):
		"""
		부분입력텍스트로 적합한 모든 텍스트객체를 찾는 것

		:param input_partial_link_text:
		:return:
		"""
		input_partial_link_text = str(input_partial_link_text).lower()
		self.select_all_obj = self.driver.find_elements(By.PARTIAL_LINK_TEXT, input_partial_link_text)
		return self.select_all_obj

	def search_obj_by_class_name(self, input_class_name):
		"""
		class name에서 맞는것중에 처음의 객체를 돌려준다

		:param input_class_name:
		:return:
		"""
		input_class_name = str(input_class_name).lower()
		self.select_obj = self.driver.find_element(By.CLASS_NAME, input_class_name)
		return self.select_obj

	def search_obj_by_css_selector(self, input_selector):
		"""
		css selector에서 맞는것중에 처음의 객체를 돌려준다

		:param input_selector:
		:return:
		"""
		input_selector = str(input_selector).lower()
		self.select_obj = self.driver.find_element(By.CSS_SELECTOR, input_selector)
		return self.select_obj

	def search_obj_by_full_link_text(self, input_full_link_text):
		"""
		링크로된 text중에서 전체가 맞는 것중에서 처음것을 돌려주는 것

		:param input_full_link_text:
		:return:
		"""
		input_full_link_text = str(input_full_link_text).lower()
		self.select_obj = self.driver.find_element(By.LINK_TEXT, input_full_link_text)
		return self.select_obj

	def search_obj_by_id(self, input_id):
		"""
		id로 객체 찾기

		:param input_id:
		:return:
		"""
		input_id = str(input_id).lower()
		self.select_obj = self.driver.find_element(By.ID, input_id)
		return self.select_obj

	def search_obj_by_link_text(self, input_link_text):
		"""
		링크로된 text중에서 제일 처음것을 돌려주는 것

		:param input_link_text:
		:return:
		"""
		input_link_text = str(input_link_text).lower()
		self.select_obj = self.driver.find_element(By.ID, input_link_text)

	def search_obj_by_name(self, input_name):
		"""
		이름으로 객체 찾기

		:param input_name:
		:return:
		"""
		input_name = str(input_name).lower()
		self.select_obj = self.driver.find_element(By.NAME, input_name)
		return self.select_obj

	def search_obj_by_partial_link_text(self, input_partial_link_text):
		"""
		부분입력텍스트로 적합한 텍스트를 찾는 것

		:param input_partial_link_text:
		:return:
		"""
		input_partial_link_text = str(input_partial_link_text).lower()
		self.select_obj = self.driver.find_element(By.PARTIAL_LINK_TEXT, input_partial_link_text)
		return self.select_obj

	def search_obj_by_x_path(self, input_x_path):
		"""
		x-path로 객체 찾기

		:param input_x_path:
		:return:
		"""
		input_x_path = str(input_x_path).lower()
		self.select_obj = self.driver.find_element(By.XPATH, input_x_path)
		return self.select_obj

	def search_all_obj_by_x_path(self, input_x_path):
		"""
		x-path로 모든 객체 찾기

		:param input_x_path:
		:return:
		"""
		input_x_path = str(input_x_path).lower()
		self.select_all_obj = self.driver.find_elements(By.XPATH, input_x_path)
		return self.select_all_obj

	def search_all_obj_by_many_class_name(self, input_list=[]):
		"""

		:param input_list:
		:return:
		"""
		input_text = ""
		for one in input_list:
			input_text = input_text + "." + one + " "
		self.select_obj = self.driver.find_element(By.CSS_SELECTOR, input_text)

	def search_obj_by_input_text(self, input_text):
		"""

		:param input_text:
		:return:
		"""
		# 글씨가 있는 태그를 찾아주는것
		elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{input_text}')]")
		return elements

	def search_window_by_title(self, input_title):
		"""

		:param input_title:
		:return:
		"""
		# 입력받은 제목을 포함한 창을 선택한다
		# 없으면 맨마지막것이 된다
		window_handles = self.driver.window_handles
		for handle in window_handles:
			self.driver.switch_to.window(handle)
			title = self.driver.title
			if input_title in title:
				print("찾은 title은 => ", title)
				return self.driver
			else:
				pass
		return False

	def switch_to_iframe_by_id(self, input_id="ifrmHidden"):
		"""

		:param input_id:
		:return:
		"""
		self.driver.switch_to.frame(input_id)

	def type_enter(self):
		"""
		키보드를 enter키를 누르는 것

		:return:
		"""
		self.select_obj.send_keys(Keys.ENTER)

	def type_enter_key(self):
		"""
		키보드를 enter키를 누르는 것

		:return:
		"""
		self.select_obj.send_keys(Keys.RETURN)

	def type_keyboard(self, *key_list):
		"""

		:param key_list:
		:return:
		"""

		final_key_value = 0
		one_char = ""
		for one_key in key_list:
			if one_key in self.varx_all_key_enum.keys():
				final_key_value = final_key_value + self.varx_all_key_enum[one_key]
			else:
				one_char = one_key
		if one_char and final_key_value:
			self.select_obj.send_keys(final_key_value + one_char)
		elif one_char and not final_key_value:
			self.select_obj.send_keys(one_char)
		elif not one_char and final_key_value:
			self.select_obj.send_keys(final_key_value)
		else:
			print("error")

	def type_tab(self, input_no=1):
		"""

		:param input_no:
		:return:
		"""
		for num in range(input_no):
			self.select_obj.send_keys(Keys.TAB)

	def write_date_at_focus(self, input_text='2024-12-03'):
		"""

		:param input_text:
		:return:
		"""
		self.select_obj.send_keys(input_text)

	def write_text_at_focus(self, input_text='파이썬'):
		"""

		:param input_text:
		:return:
		"""
		self.select_obj.send_keys(input_text)
		self.select_obj.send_keys(Keys.RETURN)

	def write_text_at_parameter(self, input_ele, input_text=""):
		"""
		어떤 객체에 글씨를 쓰는 기능으로
		보통 input과같이 글을 쓸수있는 객체에 적용하여야 한다

		:param input_ele:
		:param input_text:
		:return:
		"""
		script = 'arguments[0].value = arguments[1];'
		self.driver.execute_script(script, input_ele, input_text)

	def search_element_by_id(self, input_id):
		"""

		:param input_id:
		:return:
		"""
		result = self.driver.find_element(By.ID, input_id)
		return result

	def search_element_by_class_name(self, input_text="query"):
		"""

		:param input_text:
		:return:
		"""
		self.search_box = self.driver.find_element(By.CLASS_NAME, input_text)

	def search_element_by_many_class_name(self, input_list=[]):
		"""

		:param input_list:
		:return:
		"""
		input_text = ""
		for one in input_list:
			input_text = input_text + "." + one + " "
		self.search_box = self.driver.find_element(By.CSS_SELECTOR, input_text)

	def search_button_by_text(self, input_text):
		"""
		버튼 태그안의 텍스트중에서 입력한 글자가 들어간 버튼tag를 찾는것

		:param input_id:
		:return:
		"""
		result = None
		buttons = self.driver.find_elements(By.TAG_NAME, "button")
		# 찾은 버튼 요소 출력
		for button in buttons:
			if input_text in button.text:
				result = button
				break
		return result


	def search_checkbox_by_id(self, input_id="query"):
		"""

		:param input_id:
		:return:
		"""

		self.search_box = self.driver.find_element(By.ID, input_id)

	def search_tag_by_full_full_link_text(self, input_id="query"):
		"""

		:param input_id:
		:return:
		"""
		self.search_box = self.driver.find_element(By.ID, input_id)

	def search_tag_by_link_text(self, input_id="query"):
		"""

		:param input_id:
		:return:
		"""
		self.search_box = self.driver.find_element(By.ID, input_id)

	def search_listitem_by_id(self, input_id="query"):
		"""

		:param input_id:
		:return:
		"""
		self.search_box = self.driver.find_element(By.ID, input_id)

	def select_nth_item_for_listitem(self, input_no=1):
		"""

		:param input_no:
		:return:
		"""
		listitem = Select(self.driver.find_element(By.NAME, 'pets'))
		listitem.select_by_index(input_no)
		listitem.select_by_visible_text('Cat')
		listitem.select_by_value('hamster')

	def check_style(self, option_dic):
		"""

		:param option_dic:
		:return:
		"""
		# 모양을 나타내는 부분
		# 사전형태
		css = ""
		all_keys = list(option_dic.keys())
		if "size" in option_dic.keys():
			temp = self.check_pixel(option_dic["size"])
			css = css + "font-size: " + temp + ";"
		if "align" in all_keys: css = css + "font-align: " + option_dic["align"] + ";"
		if "bold" in all_keys: css = css + "font-weight:bold;"
		if "color" in all_keys: css = css + "color: " + option_dic["color"] + ";"
		if "collapse" in all_keys: css = css + "borser-collapse: " + option_dic["collapse"] + ";"
		if "background" in all_keys: css = css + "background-color: " + option_dic["background"] + ";"
		if "width" in all_keys: css = css + "width: " + self.check_pixel(option_dic["width"]) + ";"
		if "padding" in all_keys: css = css + "padding: " + option_dic["padding"] + ";"
		if "border" in all_keys: css = css + self.border_outline(option_dic["border"])
		return css

	def search_tags_by_input_text(self, input_text):
		"""
		글씨가 있는 태그를 찾아주는것

		:param input_text:
		:return:
		"""
		elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{input_text}')]")
		return elements

	def get_value_at_next_line_at_same_position(self, input_text, search_text):
		# 입력자료의 각줄별로 찾는 자료가 있는 라인에, 몇번째 tab에 있는지 화인
		# 다음 라인의 같은 위치의 자료를 갖고오는 것
		# 테이블의 제목의 위치를 찾아서 다음줄의 값을 갖고오는 목적
		multi_line_text = input_text.split("\n")
		for ix, one_line in enumerate(multi_line_text):
			for iy, one_text in enumerate(one_line.split("\t")):
				if search_text == one_text:
					result =multi_line_text[ix+1].split("\t")[iy]
					return result


	def get_value_at_next_tab(self, input_text, search_text):
		# 테이블의 제목의 위치를 찾아서 옆의 값을 갖고오는 목적
		multi_line_text = input_text.split("\n")
		for ix, one_line in enumerate(multi_line_text):
			one_line_tab = one_line.split("\t")
			for iy, one_text in enumerate(one_line_tab):
				if search_text == one_text:
					result =one_line_tab[iy+1]
					return result


	def change_text_to_l2d_by_tab_n_line(self, input_text):
		# text 자료를 줄과 tab 을 기준으로 나누어서 2 차원 자료로 만든것
		result = []
		multi_line_text = input_text.split("\n")
		for one_line in multi_line_text:
			result.append(one_line.split("\t"))
		return result

	def search_objs_in_many_tags(self, input_tag_list):
		css_text = ""
		for one in input_tag_list:
			css_text = css_text + " " + one

		result = self.driver.find_elements(By.CSS_SELECTOR, css_text)
		return result

	def click_input_button_obj(self, input_button_obj):
		from selenium.webdriver.common.action_chains import ActionChains
		actions = ActionChains(self.driver)
		actions.move_to_element(input_button_obj).click().perform()


	def get_selected_value_for_list(self, input_list_obj):
		from selenium.webdriver.support.ui import Select
		select = Select(input_list_obj)
		selected_option = select.first_selected_option
		selected_value = selected_option.text


	def select_nth_value_for_list(self, input_list_obj, input_no):
		from selenium.webdriver.support.ui import Select
		select = Select(input_list_obj)
		# 두 번째 옵션 선택 (인덱스는 0부터 시작하므로 1이 두 번째 옵션)
		select.select_by_index(input_no-1)
		# 선택된 옵션 확인
		selected_option = select.first_selected_option
		selected_value = selected_option.text
		print(f"선택된 값: {selected_value}")


	def get_check_value_for_checkbox(self, input_checkbox_obj):
		is_checked = input_checkbox_obj.is_selected()
		print(f"체크박스 선택 상태: {is_checked}")
		# 체크박스 선택 (체크되지 않은 경우)
		if not is_checked:
			input_checkbox_obj.click()
			print( "체크박스를 선택했습니다.")


