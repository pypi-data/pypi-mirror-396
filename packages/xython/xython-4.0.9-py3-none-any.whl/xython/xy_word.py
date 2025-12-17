# -*- coding: utf-8 -*-
import copy, os, ctypes
import win32com.client # pywin32의 모듈
from PIL import Image

import xy_re, xy_color, xy_common # xython 모듈

class xy_word:
	"""
	윈도우 워드를 컨트롤 하는 모듈

	형태적인 분류 : active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
	의미적인 분류 : active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)

	공통으로 사용할 변수들을 설정하는 것이다
	- 외부에서는 1부터 시작, 내부적으로는 0을 한다면, 가장 먼저 적용되는 부분에서 -1을 하도록 한다

	2024-04-27 : 전체적으로 이름을 terms에 따라서 변경함
	"""

	def __init__(self, file_name=""):

		self.colorx = xy_color.xy_color()
		self.rex = xy_re.xy_re()
		self.varx = xy_common.xy_common().varx # package안에서 공통적으로 사용되는 변수들

		# 워드 전체에 공통적으로 사용되는 변수
		self.common_range = None
		self.common_selection = None
		self.common_font_list = None
		self.x = None
		self.y = None
		self.font_dic = {}
		self.font_dic_default = {}
		self.letter_type_dic = {"line": "line", "줄": "line", "한줄": "line", "라인": "line",
								"paragraph": "paragraph", "패러그래프": "paragraph", "문단": "paragraph", "para": "paragraph",
								"word": "word", "단어": "word", "워드": "word",
								"sentence": "sentence", "문장": "sentence",
								"char": "char", "글자": "char", "문자": "char", "character": "char",
								"cell": "cell",
								"column": "column", "col": "column",
								"row": "row",
								"item": "item",
								"셀": "cell", "컬럼": "column", "아이템": "item", "파라그래프": "paragraph",
								"파라": "paragraph", "가로": "row", "섹션": "section", "스토리": "story",
								"section": "section", "story": "story", "table": "table", "테이블": "table",
								}

		self.obj_word = {} # 객체를 사용하기 위해서 사용하는것

		if file_name == "no" or file_name == "not":
			pass
		else:
			self.__start_ganada(file_name)

	def __start_ganada(self, file_name):
		"""
		워드를 처음 여릴때 실행되는 것

		:param file_name: 화일 이름
		:return:
		"""
		self.word_application = win32com.client.dynamic.Dispatch('Word.Application')
		self.word_application.Visible = 1
		self.selection = self.word_application.Selection

		self._check_doc(file_name)

	def __str__(self):
		return self.doc

	def _check_doc(self, file_name):
		"""
		다음줄, 다음단어의 의미 : 현재 기준에서 1을 한것
		단어의 시작 : 글자가 시작되는 지점에서 마지막 공백까지
		단어 : 문자열이 같은 형태의 묶음 (123가나다 => 공백이 없어도 2개단어)
		만약 오픈된 워드가 하나도 없으면,새로운 빈 워드를 만든다

		:param file_name: 입력한 화일 이름
		"""
		if file_name == "":
			# 만약 오픈된 워드가 하나도 없으면,새로운 빈 워드를 만든다
			try:
				self.doc = self.word_application.ActiveDocument
			except:
				self.doc = self.word_application.Documents.Add()
		elif file_name == "new":
			self.doc = self.word_application.Documents.Add()
		else:
			self.doc = self.word_application.Documents.Open(file_name)
			self.word_application.ActiveDocument.ActiveWindow.View.Type = 3

		self.selection = self.word_application.Selection
		self.range = self.doc.Range()

	def active_doc(self):
		"""
		현재 워드를 활성화 시키기

		:return:
		"""
		second_document = self.word_application.Documents(2)
		second_document.Activate()

	def change_selection_to_input_text(self, replace_text):
		"""
		바꾸기 : 선택한 영역의 모든문자를 입력으로 들어오는 글자로 변경하는 것

		:param replace_text: 바꿀 문자
		"""
		self.replace_in_selection(replace_text)

	def change_style_name(self, old_style_name, new_style_name):
		"""
		스타일의 이름을 바꾸는 것

		:param style_name: 바뀌기 전 스타일 이름
		:param new_style_name: 새로운 스타일 이름
		:return:
		"""
		try:
			style = self.doc.Styles(old_style_name)
		except Exception as e:
			print(f"스타일 '{old_style_name}'이(가) 존재하지 않습니다.")
			return
		# 스타일 이름 변경 (임시 이름으로)
		style.NameLocal = new_style_name

	def change_table_data_to_l2d(self, input_table_obj):
		"""
		테이블객체를 주면, 그 테이블안의 모든자료를
		테이블형식의 자료를 2차원의 리스트로 바꿔주는 것
		어떤 테이블 안의 모든 자료를 2차원으로 만들어 주는 것

		:param input_table_obj: 테이블객체
		:return:
		"""
		result = []
		x, y = self.get_xy_for_table(input_table_obj)
		for i in range(1, x + 1):
			one_line = []
			for j in range(1, y + 1):
				cell_value = input_table_obj.Cell(i, j).Range.Text
				# 셀 값에서 줄바꿈 문자를 제거합니다
				cell_value = cell_value.strip(chr(7)) # chr(7)은 Word 에서 셀 끝을 나타내는 특수 문자입니다
				one_line.append(cell_value)
			result.append(one_line)
		return result

	def check_blank_line_or_not(self):
		"""
		2 칸이상의 줄이 빈경우 삭제할려고 만드는 중

		:return:
		"""
		continius = []
		line_no = self.count_line_in_doc()
		for one in range(line_no + 1, 1, -1):
			self.select_nth_line_at_doc_start(one)
			line_text = self.read_text_for_selection()
			if len(line_text) < 10:
				if len(continius) == 2:
					self.delete_line_at_selection_end()
				else:
					continius.append(one)
			else:
				continius = []

	def check_content_name(self, input_name):
		"""
		어떤 기준으로 할것인지를 확인하는 것
		content로 사용되는 단어들을 이것저것 사용하여도 적용이 가능하도록 만든것
		그자들의 종류를 체크해주는 기능

		:param input_name: 이름입력
		"""
		result = self.letter_type_dic[input_name]
		return result

	def check_font_style(self, input_list):
		"""
		어떤 폰트의 속성이 오더라도 적용하게 만드는 것

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		check_bold = self.varx["check_bold"]
		check_italic = self.varx["check_italic"]
		check_underline = self.varx["check_underline"]
		check_breakthrough = self.varx["check_breakthrough"]
		check_alignment = self.varx["check_alignment"]
		for one in input_list:
			if one in check_bold.keys():
				self.font_dic["bold"] = True
			elif one in check_italic.keys():
				self.font_dic["italic"] = True
			elif one in check_underline.keys():
				self.font_dic["underline"] = True
			elif one in check_breakthrough.keys():
				self.font_dic["strikethrough"] = True
			elif one in check_alignment.keys():
				self.font_dic["align"] = self.varx["check_alignment"][one]
			elif type(one) == type(123) and one < 100:
				self.font_dic["size"] = one
			elif self.is_xcolor_style(one):
				self.font_dic["color"] = self.colorx.change_xcolor_to_rgbint(one)

	def check_letter_type(self, input_letter_type):
		"""
		글자의 형태를 확인하는 것

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:return:
		"""
		result = self.letter_type_dic[input_letter_type]
		return result

	def check_letter_type_no(self, input_letter_type):
		"""
		사용하는 글자 묶음의 형태를 기본 형으로 바꾸는 것

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:return:
		"""
		if type(input_letter_type) == type(123):
			result = input_letter_type
		else:
			result = self.varx["letter_type_vs_enum"][input_letter_type]
		return result

	def check_opend_file(self, input_file_name):
		"""
		열려져있는 모든 워드 화일의 이름을 갖고옵니다

		:param input_file_name: 화일 이름
		:return:
		"""
		doc_no = self.word_application.Documents.Count
		file_names = []
		for no in range(doc_no):
			file_names.append(self.word_application.Documents(no + 1).Name)

		if input_file_name in file_names:
			return True

		return False

	def check_range(self, input_range=""):
		"""
		입력으로 들어오는 range 객체를 갖고오는 것입니다

		:param input_range: range객체
		:return:
		"""
		if input_range != "":
			result = input_range
		else:
			if not self.range:
				result = self.word_application.Selection
			else:
				result = self.range
		return result

	def check_range_obj(self, input_range_obj=""):
		"""
		range객체를 갖고오는 것이며 없을때는 자동으로 selection으로 적용한다
		range와 selection을 함께 사용이 가능하도록 만드는 것

		:param input_range_obj: range 객체
		"""
		if input_range_obj == "":
			input_range_obj = self.selection

		return input_range_obj

	def check_table_obj(self, input_table_obj):
		"""
		숫자가 오면 index로 인식해서 테이블 객체를 찾아주는 것
		Tables : 0이 아닌 1번부터 시작한다

		:param input_table_obj: 테이블 객제
		"""

		if type(input_table_obj) == type(123):
			result = self.doc.Tables(input_table_obj)
		else:
			result = input_table_obj
		return result

	def check_visible_nth_word(self, input_no=0):
		"""
		눈으로 보는 기준으로 단어를 찾는 함수입니다
		모든 글자를 읽어와서 띄어쓰기를 기준으로 한글자씩 읽어가면서, 원하는 단어까지 만드는 것이다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		current_word = 0
		current_text = ""
		temp = True
		return_no = 0
		# 글머리 기호는 워드에서는 기호 자체도 1개의 단어로 인식을 하지만
		# 글에서는 보이는것을 기준으로 계산을 하지만, 코드상에서는 없는 것
		self.select_all()
		all_text = self.selection.Text
		# table 의 빈칸에 들어가는 벨소리부분을 지우는것
		for index, one in enumerate(all_text):
			# 특수문자중 code 상으로는 계산되지만, char로 인식되지 않는 문자의 합
			# 다음에 화면에서 영역을 선택할때 사용되는 정보이다
			if one in ["\x07"]:
				return_no = return_no + 1
			if current_text == "" and one in ["\x07", "Ir", "In", ""]:
				# 맨처음으로 특수문자만 있는 부분들은 제외하는 것이다
				pass
			else:
				if one in ["\r", "\n", " "] and temp == True:
					current_word = current_word + 1
					if current_word == input_no:
						return [current_text, index - len(current_text) + 1, index, return_no]
					temp = False
					current_text = ""
				elif one in ["\x07"]:
					pass
				else:
					temp = True
					current_text = current_text + one

	def close(self):
		"""
		현재 활성화된 문서를 닫는다
		"""
		self.doc.Close()

	def close_all_doc_with_save(self):
		"""
		현재 활성화된 문서를 저장하고 그냥 닫는다

		:return:
		"""
		self.word_application.DisplayAlerts = 0
		for one in self.word_application.Documents:
			one.Save()
			one.Close(SaveChanges=True)

	def close_all_doc_without_save(self):
		"""
		현재 활성화된 문서를 저장하지 않고 그냥 닫는다
		"""
		for one in self.word_application.Documents:
			one.Close(SaveChanges=False)

	def compress_all_inline_image(self, compress_rate_0to1, all_or_partial = ""):
		"""
		이미지를 압축하는 것

		:param compress_rate_0to1:
		:param all_or_partial: 전체를 다할것인지 부분만 할것인지
		:return:
		"""
		for shape in self.doc.InlineShapes:
			if shape.Type == 3: # wdInlineShapePicture
				try:
					# 그림을 임시 파일로 저장
					temp_path = os.path.join(os.path.dirname("C:\\"), "temp_image_01234.jpg")
					shape.Range.InlineShapes[1].PictureFormat.Crop.Picture.SaveAs(temp_path)
					# JPEG로 다시 저장하며 압축
					img = Image.open(temp_path)
					img.save(temp_path, "JPEG", quality=compress_rate_0to1)
					# 압축된 그림을 워드 문서에 다시 삽입
					shape.Range.InlineShapes[1].Delete()
					self.doc.InlineShapes.AddPicture(temp_path, False, True, shape.Range)

					# 임시 파일 삭제
					os.remove(temp_path)
				except Exception as e:
					print(f"오류 발생: {e}")

	def count_char_in_doc(self):
		"""
		개수세기 : 문서안의 총 글자수 (공백도 1개의 글자이다)
		계산하는 방법에 따라서 char의 갯수가 트릴수 있다
		"""
		result = len(self.doc.Characters)
		return result

	def count_char_in_range(self):
		"""
		개수세기 : range안의 글자수 (공백도 1개의 글자이다)
		"""
		if not self.range:
			self.range = self.word_application.Selection

		x = self.range.Start
		y = self.range.End
		result = y - x
		return result

	def count_char_in_selection(self):
		"""
		개수세기 : 선택영역안의 글자수 (공백도 1개의 글자이다)
		"""
		x = self.selection.Start
		y = self.selection.End
		result = y - x
		return result

	def count_doc(self):
		"""
		개수세기 : 현재 열려져있는 화일의 모든 갯수를 갖고온다
		"""
		result = self.word_application.Documents.Count
		return result

	def count_line_in_doc(self):
		"""
		개수세기 : 문서안의 총 줄수
		"""
		self.select_all()
		result = self.count_line_in_selection()
		return result

	def count_line_in_range(self, input_range=""):
		"""
		개수세기 : range안의 줄수

		ComputeStatistics의 입력숫자를 이용하여 선택영역의 정보를 갖고오는것
		예 => ComputeStatistics(3) 은 글자수
		3(글자수), 0(단어수), 1(라인수), 4(para수), 2(page수)

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		len_line = input_range.ComputeStatistics(1)
		return len_line

	def count_line_in_selection(self):
		"""
		개수세기 : 선택영역안의 줄수

		ComputeStatistics의 입력숫자를 이용하여 선택영역의 정보를 갖고오는것 :
			예 : ComputeStatistics(3) :글자수
			3 :글자수, 0 :단어수, 1 :라인수, 4 :para수, 2 :page수
		"""
		len_line = self.selection.Range.ComputeStatistics(1)
		return len_line

	def count_list_formation_from_doc_start_to_para_no(self, input_no):
		"""
		ListFormat.ListString :

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		result = [[], []]
		for index, paragraph in enumerate(self.doc.Paragraphs):
			if paragraph.Range.ListFormat.ListType != 0: # 0은 'wdListNoNumbering'을 의미합니다
				result[0].append(index + 1)
				result[1].append(paragraph.Range.ListFormat.ListString)
			if input_no == index + 1:
				return result

	def count_page_in_doc(self):
		"""
		개수세기 : 문서안의 총 페이지 수
		"""
		result = self.doc.ComputeStatistics(2)
		return result

	def count_page_in_range(self, input_range=""):
		"""
		개수세기 : range안의 줄수
		ComputeStatistics(2) :영역안의 통계정보중 page수

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		len_line = input_range.ComputeStatistics(2)
		return len_line

	def count_page_in_selection(self):
		"""
		개수세기 : 선택영역안의 페이지수
		ComputeStatistics(2) :영역안의 통계정보중 page수
		"""
		len_page = self.selection.Range.ComputeStatistics(2)
		return len_page

	def count_para_in_doc(self):
		"""
		개수세기 : 문서안의 종 문단수
		"""
		result = self.doc.Paragraphs.Count
		return result

	def count_para_in_range(self, input_range=""):
		"""
		개수세기 : range안의 문단수
		ComputeStatistics(4) :영역안의 통계정보중 para수

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		len_para = input_range.ComputeStatistics(4)
		return len_para

	def count_para_in_selection(self):
		"""
		개수세기 : 선택영역안의 문단수
		ComputeStatistics(4) :영역안의 통계정보중 para수
		"""
		len_para = self.selection.Range.ComputeStatistics(4)
		return len_para

	def count_shape_in_doc(self):
		"""
		문서안의 도형 갯수를 알려주는 것

		:return:
		"""
		result = self.doc.Shapes.Count
		return result

	def count_shape_in_range(self, input_range=""):
		"""
		입력영역안의 도형 갯수를 파악

		:param input_range: range객체
		:return:
		"""

		input_range = self.check_range(input_range)
		result = input_range.ShapeRange.Count
		return result

	def count_shape_in_selection(self):
		"""
		선택영역안의 도형 갯수를 파악

		:return:
		"""
		result = self.selection.ShapeRange.Count
		return result

	def count_table_in_doc(self):
		"""
		개수세기 : 현재 워드화일안의 테이블의 총 갯수
		"""
		result = self.doc.Tables.Count
		return result

	def count_table_in_range(self, input_range=""):
		"""
		개수세기 : range안의 문단수

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		result = input_range.Tables.Count
		return result

	def count_table_in_selection(self):
		"""
		개수세기 : 현재 워드화일안의 테이블의 총 갯수
		"""
		result = self.selection.Tables.Count
		return result

	def count_word_in_doc(self):
		"""
		개수세기 : 현재 워드화일안의 총단어숫자
		ComputeStatistics(0) :영역안의 통계정보중 단어수
		"""
		myrange = self.doc.StoryRanges(1)
		len_word = myrange.ComputeStatistics(0)
		return len_word

	def count_word_in_range(self, input_range=""):
		"""
		개수세기 : range안의 줄수
		ComputeStatistics(0) :영역안의 통계정보중 단어수

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		result = input_range.ComputeStatistics(0)
		return result

	def count_word_in_selection(self):
		"""
		개수세기 : 선택영역안의 단어수
		ComputeStatistics(0) :영역안의 통계정보중 단어수
		"""
		result = self.selection.Range.ComputeStatistics(0)
		return result

	def cut_range(self, input_range=""):
		"""
		잘라내기 : range 영역

		:param input_range: range객체
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.Cut()

	def cut_selected_shape(self):
		"""
		잘라내기 : 현재 선택된 도형을 잘라내기 하기
		"""
		img = self.selection.InlineShapes(1)
		shape = img.ConvertToShape()
		shape.Cut()

	def cut_selection(self):
		"""
		잘라내기 : 선택한 영역 잘라내기
		"""
		self.word_application.Selection.Cut()

	def delete_all_content_in_doc(self):
		"""
		삭제 : 문서안의 모든 것을 삭제하는 것
		"""
		self.selection.WholeStory()
		self.word_application.Selection.Delete()

	def delete_all_in_doc(self):
		"""
		삭제 : 문서안의 모든 것을 삭제하는 것
		"""
		self.delete_all_content_in_doc()

	def delete_empty_line_when_over2_including_special_chars(self, input_xsql="[특수문자&숫자:1~]", input_line_limit=2):
		"""
		각줄을 확인해서 전체 줄이 비어있거나 특수문자나 숫자만 들어있으면서, 2 줄 이상이 되는때부터 삭제
		단, 맨 아래부터 삭제를 한다

		:param input_xsql: xy_re스타일의 정규 표현식
		:param input_line_limit:
		:return:
		"""
		[x, y] = self.get_line_nos_for_selection()
		continu_no = 0

		for no in range(y, x - 1, -1):
			one_line = self.read_text_for_nth_line_at_doc_start(no)
			is_empty = False
			if one_line:
				tf = self.rex.is_fullmatch_with_xsql(input_xsql, one_line)
				if tf:
					is_empty = True
			else:
				is_empty = True

			if is_empty: # 만약 빈것이라면
				continu_no = continu_no + 1
				if continu_no >= input_line_limit:
					self.delete_nth_line(no)
			else:
				continu_no = 0

	def delete_from_doc_start_to_nth_char_end(self, input_no):
		"""
		삭제 : 문서 처음에서 n번째의 문자까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_doc_start_to_nth_letter_type_end(self, input_letter_type, input_no):
		"""
		삭제 : 글자형식에 따라서 문서 처음에서 n번째까지 삭제

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		self.select_from_selection_end_to_nth_letter_type_end(input_letter_type, input_no)

		self.word_application.Selection.range.Text = ""

	def delete_from_doc_start_to_nth_line_end(self, input_no):
		"""
		삭제 : 문서 처음에서 n번째 라인 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_doc_start_to_nth_para_end(self, input_no):
		"""
		삭제 : 문서 처음에서 n번째 문단끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)
		self.word_application.Selection.range.Text = ""

	def delete_from_doc_start_to_nth_sentence_end(self, input_no):
		"""
		sentence 삭제 : 문서 처음에서 n번째 sentence까지 삭제

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_from_doc_start_to_nth_sentence_end(input_no)
		self.word_application.Selection.Delete()

	def delete_from_doc_start_to_nth_word_end(self, input_no):
		"""
		삭제 : 문서 처음에서 n번째의 문자까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_range_end_to_nth_char_end(self, input_no):
		"""
		삭제 : range객체에서 n개의 글자를 삭제하는것
		만약 range의 영역이 있다면, 그것을 포함한다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.range.Range.Move(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		self.delete_range()

	def delete_from_range_end_to_nth_letter_type_end(self, input_letter_type, input_no):
		"""
		삭제 : 글자의 종류에 따라서 range안의 n번째의 것을 삭제

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 1부터시작하는 번호
		:return:
		"""
		current_range = self.get_current_range_obj()
		self.expand_range_to_nth_letter_type_end(current_range, input_letter_type, input_no)
		self.delete_range()

	def delete_from_range_end_to_nth_line_end(self, input_no):
		"""
		라인삭제 : range에서 n개의 줄을 삭제

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		current_range = self.get_current_range_obj()
		self.expand_range_to_nth_letter_type_end(current_range, "line", input_no)
		self.delete_range()

	def delete_from_range_end_to_nth_para_end(self, input_no):
		"""
		para삭제 : range에서 n개의 para를 삭제

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		current_range = self.get_current_range_obj()
		self.expand_range_to_nth_letter_type_end(current_range, "para", input_no)
		self.delete_range()

	def delete_from_range_end_to_nth_word_end(self, input_no):
		"""
		삭제 : range_end를 기준으로 n번째 단어의 끝까지 삭제하기

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		current_range = self.get_current_range_obj()
		self.expand_range_to_nth_letter_type_end(current_range, "word", input_no)
		self.delete_range()

	def delete_from_selection_end_to_nth_char_end(self, input_no):
		"""
		삭제 : 현재 선택된 영역의 끝에서 부터 n번째 글자까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_selection_end_to_nth_letter_type_end(self, input_letter_type, input_no):
		"""
		삭제 : 일반적인 글자의 형태를 n개 삭제하는것
		letter type : "sentence" = 3,"word" = 2, "char" = 1

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""

		letter_type_no = self.check_letter_type_no(input_letter_type)
		if input_no > 0:
			if letter_type_no in [3, 2, 1]: # "sentence" = 3,"word" = 2, "char" = 1
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no, Extend=1) # Extend = 0 은 이동을 시키는 것이다
			else:
				# "cell" = 12, , "column" = 9, "item" = 16, "line" = 5, "para" = 4, "row" = 10, "section" = 8, "story" = 6, "table" = 15,
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no, Extend=1)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no, Extend=1)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_selection_end_to_nth_line_end(self, input_no):
		"""
		라인삭제 : 선택영역에서 n개의 라인을 삭제

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_selection_end_to_nth_para_end(self, input_no=1):
		"""
		삭제 : 현재 선택된 영역의 끝에서 부터 n번째 문단까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_from_selection_end_to_nth_word_end(self, input_no=1):
		"""
		삭제 : 현재 선택된 영역의 끝에서 부터 n번째 단어까지
		:param input_no: 1부터시작하는 번호
		"""
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no, Extend=1)

		self.word_application.Selection.range.Text = ""

	def delete_header_text_all(self):
		"""
		삭제 : 헤더안의 모든것을 지우는 것

		:return:
		"""
		for section in self.doc.Sections:
			for header in section.Headers:
				header.Range.Text = ""

	def delete_line_at_selection_end(self):
		"""
		삭제 : 현재커서가 있는 라인 1개를 삭제

		:return:
		"""
		self.select_nth_line_at_doc_start(0)
		self.word_application.Selection.Delete()

	def delete_nth_line(self, input_no):
		"""
		삭제 : 문서의 처음을 기준으로 n번째 라인을 삭제하는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_nth_line_at_doc_start(input_no)
		self.word_application.Selection.Delete()

	def delete_nth_para(self, input_no):
		"""
		삭제 : 문서의 처음을 기준으로 n번째 문단을 삭제하는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		self.select_nth_para_at_doc_start(input_no)
		self.word_application.Selection.Delete()

	def delete_nth_shape(self, input_no):
		"""
		객체삭제 : 문서 처음에서 n번째 객체 1개만 삭제

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		pass

	def delete_nth_table(self, input_no):
		"""
		삭제 : n번째 테이블 삭제

		:param input_no: 1부터시작하는 번호
		"""
		self.doc.Tables(input_no).Delete()

	def delete_nth_word(self, input_no):
		"""
		삭제 : 문서의 처음을 기준으로 n번째 단어를 삭제하는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		self.select_nth_word_at_doc_start(input_no)
		self.word_application.Selection.Delete()

	def delete_one_char_at_selection_end(self):
		"""
		삭제 : 현재커서의 위치에서 1개의 글자를 삭제하는 것
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.select_nth_char_at_selection_end(0)
		self.word_application.Selection.Delete()

	def delete_para_at_selection_end(self):
		"""
		삭제 : 선택된 영역의 끝을 기준으로 문단을 삭제
		:return:
		"""
		self.select_from_selection_end_to_nth_para_end(0)
		self.delete_selection()

	def delete_range(self):
		"""
		삭제 : 선택한 영역을 삭제
		"""
		self.doc.Range.Delete()

	def delete_selection(self):
		"""
		삭제 : 선택한 영역을 삭제
		"""
		self.word_application.Selection.Delete()

	def delete_sentence_at_selection_end(self):
		"""
		삭제 : 커서가있는 sentence를 삭제
		"""
		self.select_from_doc_start_to_nth_sentence_end(0)
		self.word_application.Selection.Delete()

	def delete_font_option_all(self):
		"""
		삭제 : 텍스트의 모든 옵션을 삭제

		:return:
		"""
		self.varx["font_option"] = {"xcolor": "", "size": "", "underline": "", "italic": "", "bold": "",
									"strikethrough": "", "name": "", "align": "", "subscript": "", "superscript": ""}

	def delete_word_at_selection_end(self):
		"""
		삭제 : 커서가 있는 단어를 삭제
		"""
		self.select_from_doc_start_to_nth_word_end(0)
		self.word_application.Selection.Delete()

	def delete_xxline_in_table(self, input_table_obj, xx):
		"""
		삭제 : 현재 워드화일안의 테이블객체에서 가로행 번호를 이용하여 가로행을 삭제

		:param input_table_obj: 테이블 객제
		:param xx: 가로행의 시작번호
		"""
		for no in range(xx[1] - xx[0]):
			input_table_obj.Rows(xx[0]).Delete()

	def delete_yyline_in_table(self, input_table_obj, yy):
		"""
		삭제 : 현재 워드화일안의 테이블객체에서 세로행 번호를 이용하여 세로행을 삭제

		:param input_table_obj: 테이블 객제
		:param yy: 세로행의 시작번호
		"""
		for no in range(yy[1] - yy[0]):
			input_table_obj.Columns(yy[0]).Delete()

	def draw_line_color_for_table(self, input_table_obj, input_position, input_xcolor="bla"):
		"""
		그리기 : 테이블의 선을 색칠하기

		:param input_table_obj: 테이블 객제
		:param inside_color: 안쪽 색이름
		:param outside_color: 바깥쪽 색이름
		"""
		if type(input_position) != type([]):
			input_position = [input_position]
		border_color = self.colorx.change_xcolor_to_rgbint(input_xcolor)

		for one_position in input_position:
			enum = self.varx["table_line_position_vs_enum"][one_position]
			input_table_obj.Borders(enum).Color = border_color

	def draw_line_for_selection_as_default(self):
		"""
		그리기 : 선택영역의 외곽선 그리기
		"""
		self.selection.Font.Borders(1).LineStyle = 7 # wdLineStyleDouble	7
		self.selection.Font.Borders(1).LineWidth = 6 # wdLineWidth075pt	6
		self.selection.Font.Borders(1).ColorIndex = 7 # 7 :yellow

	def draw_line_style_for_table(self, input_table_obj, line_list, line_style):
		"""
		그리기 : 테이블 선의 모양을 선정

		:param input_table_obj: 테이블 객제
		:param line_list: 위치
		:param line_style: 선의 모양
		"""

		if type(line_list) != type([]):
			line_list = [line_list]

		for one_position in line_list:
			enum = self.varx["table_line_position_vs_enum"][one_position]
			input_table_obj.Borders(enum).LineStyle = self.varx["table_line_style_vs_enum"][line_style]

	def draw_outline_for_selection_as_default(self):
		"""
		그리기 : 선택영역의 글자들의 아웃라인을 그립니다
		:return:
		"""
		self.draw_line_for_selection_as_default()

	def draw_outline_for_selection_with_option(self, line_style=1, line_color="blu", line_width="+"):
		"""
		그리기 : 선택영역의 외곽선을 그리기

		:param line_style: 선의 스타일을 선택
		:param line_color: 선의 색을 선택
		:param line_width: 선의 두께를 선택
		"""
		self.selection.Borders.OutsideLineStyle = line_style
		self.selection.Borders.OutsideLineWidth = self.varx["linewidth_vs_enum"][line_width]
		self.selection.Borders.OutsideColor = self.varx["colorname_vs_24bit"][line_color]

	def expand_range_to_nth_char_end(self, input_range, input_no):
		"""
		영역확장 : range영역에서 뒤로 n번째 글자까지 확장하는것

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		new_range = self.expand_range_to_nth_letter_type_end(input_range, "char", input_no)
		return new_range

	def expand_range_to_nth_letter_type_end(self, input_range, letter_type, input_no, except_current=False):
		"""
		그리기 : 선택영역을 입력형식에 맞도록 옮기는 것이다
		except_current : 현재 단어나 글자를 포함할것인지 아닌지를 선택하는 것이다
		에를 들어 2개를 원해도 현재것을 포함하면, 3개가 선택되어진다는 뜻입니다

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param except_current: 현재 단어나 글자를 포함할것인지 아닌지를 선택하는 것이다
		:return:
		"""

		if input_range == "":
			input_range = self.word_application.Selection

		old_x = input_range.Start
		old_y = input_range.End
		letter_type_no = self.varx["letter_type_vs_enum"][letter_type]

		# 다음것의 처음으로 이동하는 것이다
		if except_current:
			if input_no > 0:
				input_range.Move(letter_type_no, 1)
			else:
				input_range.Move(letter_type_no, -1)
			old_x = input_range.Start
			old_y = input_range.End

		input_range.Move(letter_type_no, input_no)
		new_x1 = input_range.Start
		new_x2 = input_range.Start

		# selection의 영역을 선택할때는 start, end를 사용한다
		input_range.Start = min(new_x1, new_x2, old_x, old_y)
		input_range.End = max(new_x1, new_x2, old_x, old_y)

	def expand_range_to_nth_line_end(self, input_range, input_no):
		"""
		영역확장 : 현재 range에서 n번째 라인까지 영역확대

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		new_range = self.expand_range_to_nth_letter_type_end(input_range, "line", input_no)
		return new_range

	def expand_range_to_nth_para_end(self, input_range, input_no):
		"""
		영역확장 : 현재 range에서 n번째 para까지 영역확대

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		new_range = self.expand_range_to_nth_letter_type_end(input_range, "para", input_no)
		return new_range

	def expand_range_to_nth_word_end(self, input_range, input_no):
		"""
		영역확장 : 현재 range에서 n번째 word까지 영역확대

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		new_range = self.expand_range_to_nth_letter_type_end(input_range, "word", input_no)
		return new_range

	def expand_selection_by_line_base(self):
		"""
		시작커서의 라인처음에서,끝커서가있는 라안의 끝까지 모든 라인을 선택
		"""
		self.selection.Expand(self.varx["letter_type_vs_enum"]["line"])

	def expand_selection_by_word_base(self):
		"""
		Action : 현재 selection을 확장
		시작 : 시작커서가 속해있는 워드에서
		끝 : 끝커서가 있는 워드끝까지
		"""

		self.selection.Expand(self.varx["letter_type_vs_enum"]["word"])

	def expand_selection_to_nth_char_end(self, input_no):
		"""
		영역확장 : 선택영역에서 n번째 글자까지 영역을 확장하는것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no, Extend=1)
		return self.selection

	def expand_selection_to_nth_letter_type_end(self, letter_type, input_no, except_current=False):
		"""
		영역확장 : 선택영역을 입력형식에 맞도록 옮기는 것이다
		except_current : 현재 단어나 글자를 포함할것인지 아닌지를 선택하는 것이다
		에를 들어 2개를 원해도 현재것을 포함하면, 3개가 선택되어진다는 뜻입니다

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param except_current: 현재 단어나 글자를 포함할것인지 아닌지를 선택하는 것이다
		:return:
		"""

		old_x = self.selection.Start
		old_y = self.selection.End
		letter_type_no = self.varx["letter_type_vs_enum"][letter_type]

		# 다음것의 처음으로 이동하는 것이다
		if except_current:
			if input_no > 0:
				self.selection.Move(letter_type_no, 1)
			else:
				self.selection.Move(letter_type_no, -1)
			old_x = self.selection.Start
			old_y = self.selection.End

		self.selection.Move(letter_type_no, input_no)
		new_x1 = self.selection.Start
		new_x2 = self.selection.Start

		# selection의 영역을 선택할때는 start, end를 사용한다
		self.selection.Start = min(new_x1, new_x2, old_x, old_y)
		self.selection.End = max(new_x1, new_x2, old_x, old_y)

	def expand_selection_to_nth_line_end(self, input_no):
		"""
		영역확장 : 현재 selection에서 n번째 line까지 확장하는 것
		"line" = 5,"para" = 4,

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)

	def expand_selection_to_nth_para_end(self, input_no):
		"""
		영역확장 : 현재 selection에서 n번째 para까지 확장하는 것
		"line" = 5,"para" = 4,

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)

	def expand_selection_to_nth_word_end(self, input_no):
		"""
		영역확장 : 현재 selection에서 n번째 word까지 선택
		"character" = 1, "word" = 2, "sentence" = 3

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""

		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no, Extend=1)

	def find_nth_text_in_selection_with_colored(self, search_text, input_no, input_bg_xcolor="blu"):
		"""
		찾기/바꾸기 : 선택영역의 전체에서 입력글자를 찾아서 색깔을 넣기

		:param search_text: 찾을 문자
		:param input_no: 입력 숫자
		:param input_bg_xcolor: 백그라운드용 xcolor스타일 색
		:return:
		"""
		result = []
		no = 0
		while self.selection.Find.Execute(search_text):
			if no == input_no - 1:
				self.selection.Range.Font.Italic = True
				self.selection.Range.Font.Color = 50
				self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
					input_bg_xcolor] # input_bg_xcolor="blu"
				start_no = self.selection.Range.Start
				end_no = start_no + len(search_text)
				temp = [start_no, end_no, self.selection.Range.Text]
				result.append(temp)
				break
			else:
				no = no + 1
		return result

	def find_style_in_doc(self, input_style):
		"""
		찾기/바꾸기 : 문서에서 입력으로 들어오는 스타일을 찾는것

		:param input_style: 입력 스타일
		"""
		result = []
		rng = self.doc.Range()
		rng.Find.IgnoreSpace = True
		rng.Find.Style = input_style
		while 1:
			ret = rng.Find.Execute()
			if not ret:
				return result
			result.append(ret)

	def find_text_all_in_doc(self, search_text):
		"""
		1 : 워드 문서의 전체를 Range 로 만드는 것

		:param search_text: 찾을 문자
		"""
		result = []
		myrange = self.doc.StoryRanges(1) # 1
		myrange.Find.Text = search_text
		found_or_not = myrange.Find.Execute(Forward=True)
		while found_or_not:
			start_no = myrange.Start
			end_no = myrange.End
			result.append([start_no, end_no])
			found_or_not = myrange.Find.Execute(Forward=True)
		return result

	def find_text_all_in_doc_with_ignorespace(self, input_text):
		"""
		공백을 무시한상태에서 모든 문서에서 원하는 것 찾기

		:param input_text: 입력 문자
		:return:
		"""
		result = []
		rng = self.doc.Range()
		rng.Find.IgnoreSpace = True
		while 1:
			ret = rng.Find.Execute(input_text)
			if not ret:
				return result
			result.append(ret)
			start_no = rng.Start
			end_no = start_no + len(input_text)

	def find_text_all_in_range(self, input_range, search_text, replace_text=False):
		"""
		찾기/바꾸기 : range에서 글자를 찾은것을 x,y로 돌려주는 것

		:param search_text: 찾을 문자
		"""
		result = []
		input_range.Find.Text = search_text
		if replace_text:
			input_range.Find.Replacement.Text = replace_text
		found_or_not = input_range.Find.Execute(Forward=True)
		while found_or_not:
			start_no = input_range.Start
			end_no = input_range.End
			result.append([start_no, end_no])
			found_or_not = input_range.Find.Execute(Forward=True)
		return result

	def find_text_all_in_selection_with_colored(self, search_text, input_font_xcolor="red", input_bg_xcolor="blu"):
		"""
		찾기/바꾸기 : 선택영역의 전체에서 입력글자를 찾아서 색깔을 넣기

		:param search_text: 찾을 문자
		"""
		result = []
		while self.selection.Find.Execute(search_text):
			self.selection.Range.Font.Italic = True
			self.selection.Range.Font.Color = self.colorx.change_xcolor_to_rgbint(input_font_xcolor)
			self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
				input_bg_xcolor] # input_bg_xcolor="blu"
			start_no = self.selection.Range.Start
			end_no = start_no + len(search_text)
			temp = [start_no, end_no, self.selection.Range.Text]
			result.append(temp)
		return result

	def find_text_in_selection_start_only(self, search_text, input_bg_xcolor="blu"):
		"""
		현재 위치에서 찾는것을 입력하면, 바로 다음것을 선택하는 것
		search를 사용할것인지 find를 사용할것인지 정해보자
		replace

		:param search_text: 찾을 문자
		"""
		result = []
		if self.selection.Find.Execute(search_text):
			self.selection.Range.Font.Italic = True
			self.selection.Range.Font.Color = 255
			self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
				input_bg_xcolor] # input_bg_xcolor="blu"
			start_no = self.selection.Range.Start
			end_no = start_no + len(search_text)
			temp = [start_no, end_no, self.selection.Range.Text]
			result.append(temp)

		return result

	def font_option_for_align(self, input_align="left"):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 정렬
		정렬을 위한 옵션의 설정

		:param input_align: 정렬방법
		:return:
		"""
		self.varx["font_option"]["align"] = input_align

	def font_option_for_bold(self, input_bold=True):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 굵게

		:param input_bold: 굵게를 True/False로 입력
		:return:
		"""
		self.varx["font_option"]["bold"] = input_bold

	def font_option_for_color(self, input_color):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 색

		:param input_color: 색이름 (xcolor스타일)
		:return:
		"""
		self.varx["font_option"]["xcolor"] = input_color

	def font_option_for_italic(self, input_italic=True):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 이탤릭체

		:param input_italic: 이탤릭체
		:return:
		"""
		self.varx["font_option"]["italic"] = input_italic

	def font_option_for_name(self, input_name="Arial"):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 폰트명

		:param input_name: 폰트 이름
		:return:
		"""
		self.varx["font_option"]["name"] = input_name

	def font_option_for_size(self, input_size):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 폰트크기

		:param input_size: 폰트 사이즈
		:return:
		"""

		self.varx["font_option"]["size"] = input_size

	def font_option_for_strikethrough(self, input_strikethrough=True):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 취소선

		:param input_strikethrough: 취소선
		:return:
		"""

		self.varx["font_option"]["strikethrough"] = input_strikethrough

	def font_option_for_subscript(self, input_subscript):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 아랫첨자

		:param input_subscript: 아랫첨자
		:return:
		"""
		self.varx["font_option"]["subscript"] = input_subscript

	def font_option_for_superscript(self, input_superscript):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 윗첨자

		:param input_superscript: 윗첨자
		:return:
		"""
		self.varx["font_option"]["superscript"] = input_superscript

	def font_option_for_underline(self, input_underline=True):
		"""
		공통으로 사용하는 폰트의 옵션을 설정 : 밑줄

		:param input_underline: 밑줄
		:return:
		"""
		self.varx["font_option"]["underline"] = input_underline

	def get_active_doc_name(self):
		"""
		현재 활성화된 워드화일의 이름
		"""

		result = self.word_application.ActiveDocument.Name
		return result

	def get_basic_style_name_all(self):
		"""
		현재 화성화된 워드 화일안의 모든 스타일을 돌려준다

		:return:
		"""
		result = []
		style_count = self.doc.Styles.Count
		for i in range(1, style_count + 1):
			style_obj = self.doc.Styles(i)
			if style_obj.QuickStyle:
				result.append(style_obj.NameLocal)
				print(f"{style_obj.NameLocal:10s}, {str(style_obj.BaseStyle):14s}, {str(style_obj.Visibility):10s}")
		return result

	def get_bookmark_all_in_doc(self):
		"""
		북마크의 리스트를 돌려준다
		"""
		result = []
		for bookmark in self.doc.Bookmarks:
			bookmark_name = bookmark.Name
			my_range = self.doc.Bookmarks(bookmark.Name).Range
			my_range_text = my_range.Text
			start_no = my_range.Start
			end_no = my_range.End
			temp = [bookmark_name, start_no, end_no, my_range_text]
			result.append(temp)
		return result

	def get_char_no_at_selection_end(self):
		""" 선택영역의 끝글자 번호 """
		result = self.word_application.Selection.End
		return result

	def get_char_no_at_selection_start(self):
		""" 선택영역의 시작 문자 번호 """
		result = self.word_application.Selection.Start
		return result

	def get_current_range_obj(self):
		"""
		range객체를 갖고오는 것

		:return:
		"""
		my_range = self.doc.Range
		return my_range

	def get_doc_name_all(self):
		"""
		현재 열려있는 모든 문서의 이름을 돌려준다
		"""
		doc_no = self.word_application.Documents.Count
		result = []
		for no in range(doc_no):
			result.append(self.word_application.Documents(no + 1).Name)
		return result

	def get_document_text_with_bullets(self):
		"""
		단락이 머릿글 기호를 포함하는지 확인

		:return:
		"""
		result_dic = {}
		for index, paragraph in enumerate(self.doc.Paragraphs):
			# 단락이 머릿글 기호를 포함하는지 확인합니다
			if paragraph.Range.ListFormat.ListType != 0: # 0은 'wdListNoNumbering'을 의미합니다
				if not index + 1 in result_dic.keys():
					result_dic[index + 1] = []
					result_dic[index + 1].append(paragraph.Range.ListFormat.ListString)
		return result_dic

	def get_font_color_for_selection(self):
		"""
		선택영역의 글자색을 정하기
		"""
		result = self.selection.Font.Color
		return result

	def get_font_size_for_selection(self):
		"""
		선택영역의 글자크기 정하기
		"""
		result = self.selection.Font.Size
		return result

	def get_line_no_at_selection_end(self):
		"""
		선택영역의 끝줄 번호
		"""
		start_line = self.get_line_no_at_selection_start()
		len_line = self.selection.Range.ComputeStatistics(1)
		if len_line == 0:
			# 영역이 아닌 커서이다
			return start_line
		return start_line + len_line - 1

	def get_line_no_at_selection_start(self):
		"""
		선택영역의 시작 줄 번호
		"""
		result = self.selection.Information(10)
		return result

	def get_line_nos_for_selection(self):
		"""
		선택한 영역의 줄수
		:return:
		"""
		x = self.get_line_no_at_selection_start()
		y = self.get_line_no_at_selection_end()
		return [x, y]

	def get_opened_doc_name_all(self):
		"""
		열려있는 모든 문서의 이름을 갖고오는 것

		:return:
		"""
		result = self.get_doc_name_all()
		return result

	def get_page_no_at_selection_end(self):
		"""
		선택영역의 끝 페이지 번호
		"""
		result = self.selection.Information(3)
		return result

	def get_page_no_at_selection_start(self):
		"""
		선택영역의 시작 페이지 번호
		"""
		result = self.selection.Information(1)
		return result

	def get_para_no_at_selection_end(self):
		"""
		선택영역의 끝 문단 번호
		"""
		start_para = self.get_para_no_at_selection_start()
		len_para = self.selection.Range.ComputeStatistics(4)
		return start_para + len_para - 1

	def get_para_no_at_selection_start(self):
		"""
		선택영역의 시작 문단 번호
		문단의 제일 앞부분에 있으면, 문단의 번호가 앞의 번호로 나온다. 그러므로 그런지 아닌지를 확인이 필요하다
		"""

		x = self.word_application.Selection.Start
		y = self.word_application.Selection.End

		start_para_no = self.doc.Range(0, x).Paragraphs.Count

		try:
			if self.doc.Paragraphs(start_para_no + 1).Range.Start == x:
				# 문단의 제일 처음일때는 앞의 번호가 나타난다
				# 그것을 보정해주는 기능이 필요하다
				start_para_no = start_para_no + 1
		except:
			pass

		return start_para_no

	def get_para_nos_for_selection(self):
		"""
		선택영역의 시작 문단 번호
		문단의 제일 앞부분에 있으면, 문단의 번호가 앞의 번호로 나온다. 그러므로 그런지 아닌지를 확인이 필요하다
		"""

		x = self.word_application.Selection.Start
		y = self.word_application.Selection.End

		start_para_no = self.doc.Range(0, x).Paragraphs.Count
		end_para_no = self.doc.Range(0, y).Paragraphs.Count

		try:
			if self.doc.Paragraphs(start_para_no + 1).Range.Start == x:
				# 문단의 제일 처음일때는 앞의 번호가 나타난다
				# 그것을 보정해주는 기능이 필요하다
				start_para_no = start_para_no + 1
		except:
			pass

		return [start_para_no, end_para_no]

	def get_para_obj_all_in_doc(self):
		"""
		현재 화성화된 문서 모든 문단객체를 돌려준다
		형태적인 분류 : active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 : active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence : 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph : 줄바꿈이 이루어지기 전까지의 자료

		"""
		result = self.doc.Paragraphs
		return result

	def get_pxy_at_cursor_end(self):
		"""
		커서의 위치를 픽셀로 갖고오는 것
		:return:
		"""

		class POINT(ctypes.Structure):
			_fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

		pt = POINT()
		ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
		return [pt.x, pt.y]

	def get_range_for_word_no_at_cursor_end(self):
		"""
		range객체 : 커서의 끝을 기준으로 단어의 영역
		:return:
		"""
		gijun_no = self.information_for_selection()["len_word"]
		code_word_no = self.get_word_no_at_selection_end()
		start_char_no = None
		end_char_no = None
		code_word_no1 = copy.deepcopy(code_word_no)

		for no in range(1000):
			code_word_no1 = code_word_no1 - 1
			self.select_nth_word_at_doc_start(code_word_no1)
			current_word_no = self.information_for_selection()["len_word"]
			if gijun_no != current_word_no:
				start_char_no = self.get_char_no_at_selection_end()
				break

		code_word_no2 = copy.deepcopy(code_word_no)
		for no in range(1000):
			code_word_no2 = code_word_no2 + 1
			self.select_nth_word_at_doc_start(code_word_no2)
			current_word_no = self.information_for_selection()["len_word"]
			if gijun_no != current_word_no:
				end_char_no = self.get_char_no_at_selection_end()
				break
		return [start_char_no, end_char_no]

	def get_range_obj_for_selection(self):
		"""
		range객체 설정 : 선택영역을 range객체로 설정

		:return:
		"""
		result = self.selection.Range
		return result

	def get_range_obj_from_doc_start_to_nth_para_end(self, input_para_no):
		"""
		raange객체 : 문서시작 ~ n번째 문단 끝까지

		:param input_para_no: 문단번호
		:return:
		"""
		result = self.doc.Paragraphs(input_para_no - 1).Range
		return result

	def get_selected_shape_obj(self):
		"""
		선택된 객체가 Shape 인지 확인하고, 그렇다면 해당 Shape 객체를 가져옵니다.

		:return:
		"""
		if self.selection.Type == 8:
			# 8는 wdSelectionShape 를 의미합니다
			shape = self.selection.ShapeRange(1)
			print(f"선택된 Shape 의 이름: (shape.Name]")
		else:
			print("현재 선택된 객체는 Shape가 아닙니다.")

		return shape

	def get_shape_no_for_selected_shape(self):
		"""
		현재 선택된 도형의 번호
		:return:
		"""
		if self.selection.Type == 8:
			shape = self.selection.ShapeRange(1)
			shape_name = shape.Name
		# 전체 Shape 목록에서 몇 번째인지 확인합니다
		shapes = self.doc.Shapes
		shape_index = None
		for i in range(1, shapes.Count + 1):
			if shapes.Item(i).Name == shape_name:
				shape_index = i
				break
		return shape_index

	def get_start_table_index_in_selection(self):
		"""
		선택된 곳의 테이블의 index값을 갖고온다
		"""
		result = None
		if self.selection.Information(12) == False:
			pass
		else:
			IngStart = self.selection.Range.Start
			IngEnd = self.selection.Range.End
			self.selection.Collapse(Direction=1) # 0 : end, 1:start
			self.selection.MoveEnd(Unit=self.varx["letter_type_vs_enum"]["char"], Count=IngEnd - IngStart)
			tabnum = self.doc.Range(0, self.selection.Tables(1).Range.End).Tables.Count
			if self.selection.Cell.Count:
				result = tabnum
		return result

	def get_style_name_all(self):
		"""
		현재 화성화된 워드 화일안의 모든 스타일을 돌려준다
		"""
		result = []
		style_count = self.doc.Styles.Count
		for i in range(1, style_count + 1):
			style_obj = self.doc.Styles(i)
			result.append(style_obj.NameLocal)
		return result

	def get_table_no_all_in_selection(self):
		"""
		선택한 영역안의 테이블 번호들을 돌려준다
		"""
		result = []
		current_selection = self.selection.Range.Start
		for index, one in enumerate(self.doc.Tables):
			t_start = one.Range.Start
			t_end = one.Range.End
			if current_selection > t_start and current_selection < t_end:
				result.append(index + 1)
		return result

	def get_table_no_in_para_no(self, input_no):
		"""
		paragraph 번호에 따라서 그안에 테이블이 있으면, 테이블의 index 번호를 갖고온다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		result = None
		my_range = self.doc.Paragraphs(input_no + 1).Range
		try:
			if my_range.lnformation(12):
				tbl_index = self.count_table_in_selection()
				if tbl_index:
					result = tbl_index
		except:
			result = None
		return result

	def get_table_obj_all(self):
		"""
		현재 화성화된 워드 화일안의 모든 테이블객체를 돌려준다
		테이블 객체란 테이블에대한 모든 정보를 갖고있는 클래스의 인스턴스이다
		"""
		self.all_table_obj = self.doc.Tables
		return self.all_table_obj

	def get_table_obj_by_no(self, input_no):
		"""
		번호로 테이블객체를 갖고오는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		result = self.doc.Tables(input_no)
		return result

	def get_text_all_in_doc(self):
		"""
		문서안의 모든 텍스트를 선택
		"""
		all_para_text = {}
		table_text = {}
		self.move_cursor_to_doc_start()
		para_nos = self.count_para_in_doc()
		for no in range(para_nos):
			self.select_from_doc_start_to_nth_letter_type_end("para", no)
			text_value = self.read_text_for_selection()
			all_para_text[no] = text_value
			try:
				ddd = self.selection.Information(12)
				if ddd == True:
					zzz = self.count_table_in_selection()
			except:
				pass
		return para_nos

	def get_word_no_at_selection_end(self):
		"""
		선택영역의 끝단어 번호
		"""
		start_word = self.get_word_no_at_selection_start()
		len_word = self.selection.Range.ComputeStatistics(0)
		return start_word + len_word - 1

	def get_word_no_at_selection_start(self):
		"""
		선택영역의 시작 단어 번호
		"""
		x = self.word_application.Selection.Start
		y = self.word_application.Selection.End
		new_range = self.doc.Range(Start=0, End=x)

		result = new_range.Words.Count
		return result

	def get_x_at_selection_end(self):
		""" 선택영역의 끝글자 번호 """
		result = self.word_application.Selection.End
		return result

	def get_xy_between_two_line_no(self, input_no1, input_no2):
		"""
		문서의 처음을 기준으로 n1번째부터 n2번째까지 라인의 번호를 갖고오는 것이앋

		:param input_no1:
		:param input_no2:
		:return:
		"""
		x = self.get_xy_from_doc_start_to_nth_line_end(input_no1)[0]
		y = self.get_xy_from_doc_start_to_nth_line_end(input_no2)[1]
		return [x, y]

	def get_xy_for_line_at_selection_start(self):
		"""
		선택영역의 시작점을 기준으로 워드의 좌표

		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		gijun_x = self.selection.Start
		self.doc.Range(gijun_x, gijun_x).Select()
		self.selection.Expand(letter_type_no)
		return [self.selection.Start, self.selection.End]

	def get_xy_for_line_at_x(self, input_x):
		"""
		선택영역의 시작점을 기준으로 워드의 좌표

		:param input_x:
		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		self.doc.Range(input_x, input_x).Select()
		self.selection.Expand(letter_type_no)
		return [self.selection.Start, self.selection.End]

	def get_xy_for_range(self):
		"""
		range안의 문단수
		"""
		x = self.range.Start
		y = self.range.End
		return [x, y]

	def get_xy_for_selection(self):
		"""
		선택된 영역의 위치시작과 끝의 번호값을 갖고온다
		"""
		x = self.word_application.Selection.Start + 1
		y = self.word_application.Selection.End
		return [x, y]

	def get_xy_for_selection_end(self):
		"""

		:return:
		"""
		x = self.selection.Information(5)
		y = self.selection.Information(6)
		return [x, y]

	def get_xy_for_table(self, input_table_obj):
		"""
		테이블객체의 가로세로의 크기

		:param input_table_obj: 테이블객체
		"""
		table_obj = self.check_table_obj(input_table_obj)
		x_no = table_obj.Rows.Count
		y_no = table_obj.Columns.Count
		result = [x_no, y_no]
		return result

	def get_xy_from_doc_start_to_nth_line_end(self, input_no):
		"""
		문서의 처음을 기준으로 n번째라인의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		self.doc.Range(0, 0).Select()
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no - 1)
		self.selection.StartOf(letter_type_no, 0)
		x = self.selection.Start
		self.selection.EndOf(letter_type_no, 0)
		y = self.selection.End
		return [x, y]

	def get_xy_from_doc_start_to_nth_page_end(self, page_number):
		"""
		특정페이지의 시작과 끝의 글자번호

		:param page_number:
		:return:
		"""
		range_1 = self.doc.GoTo(What=1, Which=1, Count=page_number) # 페이지의 끝 위치로 이동합니다
		range_2 = self.doc.GoTo(What=1, Which=2, Count=page_number)
		return [range_1.start, range_2.start]

	def get_xy_from_doc_start_to_nth_para_end(self, input_no):
		"""
		글자의 영역 : 문서시작 ~ n번째 문단의 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		rng = self.doc.Paragraphs(input_no).Range
		return [rng.Start, rng.End]

	def get_xy_from_doc_start_to_nth_word_end(self, input_no):
		"""
		문서의 처음을 기준으로 n번째단어의 번호를 갖고온다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		self.doc.Range(0, 0).Select()
		self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no - 1)
		self.selection.Expand(self.varx["letter_type_vs_enum"]["word"])
		x = self.selection.Start
		y = self.selection.End
		return [x, y]

	def get_xy_from_range_end_to_nth_line_end(self, input_no):
		"""
		글자의 영역 : range의 끝 ~ n번째 라인의 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		[rng_x, rng_y] = self.save_xy_for_range()
		[sel_x, sel_y] = self.get_xy_for_selection()
		self.select_xy(rng_x, rng_y)
		result = self.get_xy_from_selection_end_to_nth_line_end(input_no)
		self.select_xy(sel_x, sel_y)
		return result

	def get_xy_from_range_end_to_nth_word_end(self, input_no):
		"""
		글자의 영역 : range의 끝 ~ n번째 단어의 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		[rng_x, rng_y] = self.save_xy_for_range()
		[sel_x, sel_y] = self.get_xy_for_selection()
		self.select_xy(rng_x, rng_y)
		result = self.get_xy_from_selection_end_to_nth_word_end(input_no)
		self.select_xy(sel_x, sel_y)
		return result

	def get_xy_from_range_start_to_nth_line_end(self, input_no):
		"""
		글자의 영역 : range의 시작 ~ n번째 라인의 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		[rng_x, rng_y] = self.save_xy_for_range()
		[sel_x, sel_y] = self.get_xy_for_selection()
		self.select_xy(rng_x, rng_y)
		result = self.get_xy_from_selection_start_to_nth_line_end(input_no)
		self.select_xy(sel_x, sel_y)
		return result

	def get_xy_from_range_start_to_nth_word_end(self, input_no):
		"""
		글자의 영역 : range의 시작 ~ n번째 단어의 끝까지

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		[rng_x, rng_y] = self.save_xy_for_range()
		[sel_x, sel_y] = self.get_xy_for_selection()
		self.select_xy(rng_x, rng_y)
		result = self.get_xy_from_selection_start_to_nth_word_end(input_no)
		self.select_xy(sel_x, sel_y)
		return result

	def get_xy_from_selection_end_to_nth_line_end(self, input_no):
		"""
		선택영역의 시작위치를 기준으로 n번째 라인의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		self.selection.Start = self.selection.End
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.StartOf(letter_type_no, 0)
		x = self.selection.Start
		self.selection.EndOf(letter_type_no, 0)
		y = self.selection.End
		return [x, y]

	def get_xy_from_selection_end_to_nth_word_end(self, input_no):
		"""
		선택영역의 시작위치를 기준으로 n번째 라인의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		self.selection.Collapse(0) # 0 : end, 1:start
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.StartOf(letter_type_no, 0)
		x = self.selection.Start
		self.selection.EndOf(letter_type_no, 0)
		y = self.selection.End
		return [x, y]

	def get_xy_from_selection_start_to_nth_line_end(self, input_no):
		"""
		선택영역의 시작위치를 기준으로 n번째 라인의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.StartOf(letter_type_no, 0)
		x = self.selection.Start
		self.selection.EndOf(letter_type_no, 0)
		y = self.selection.End
		return [x, y]

	def get_xy_from_selection_start_to_nth_word_end(self, input_no):
		"""
		선택영역의 시작위치를 기준으로 n번째 라인의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.StartOf(letter_type_no, 0)
		x = self.selection.Start
		self.selection.EndOf(letter_type_no, 0)
		y = self.selection.End
		return [x, y]

	def get_xy_from_selection_start_to_word_end(self):
		"""
		선택영역의 시작점을 기준으로 워드의 좌표

		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		gijun_x = self.selection.Start
		self.doc.Range(gijun_x, gijun_x).Select()
		self.selection.Expand(letter_type_no)
		return [self.selection.Start, self.selection.End]

	def get_xy_from_word_selection_start_start_to_nth_word_end(self, input_no):
		"""
		선택영역의 시작위치 단어의 시작점에서 n번째 단어의 끝까지의 시작과 끝 번호

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.Expand(letter_type_no)
		x = self.selection.Start
		self.selection.MoveRight(Unit=letter_type_no, Count=input_no)
		self.selection.Expand(letter_type_no)
		y = self.selection.End
		return [x, y]

	def get_xy_from_x_to_nth_line_end(self, input_x_no, input_no):
		"""
		커서위치인 x를 기준으로 n번째 라인의 시작과 끝 위치

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_x_no:
		:return:
		"""
		letter_type_no = self.check_letter_type_no("line")
		self.doc.Range(input_x_no, input_x_no).Select()
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no - 1)
		self.selection.StartOf(letter_type_no, 0)
		self.selection.EndOf(letter_type_no, 0)
		x = self.selection.Start = min(input_x_no, self.selection.Start, self.selection.End)
		y = self.selection.End = max(input_x_no, self.selection.Start, self.selection.End)
		return [x, y]

	def get_xy_from_x_to_nth_para_end(self, input_x_no, input_no):
		"""
		커서위치인 x를 기준으로 n번째 para의 시작과 끝 위치

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_x_no:
		:return:
		"""
		letter_type_no = self.check_letter_type_no("para")
		self.doc.Range(input_x_no, input_x_no).Select()
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no - 1)
		self.selection.StartOf(letter_type_no, 0)
		self.selection.EndOf(letter_type_no, 0)
		x = self.selection.Start = min(input_x_no, self.selection.Start, self.selection.End)
		y = self.selection.End = max(input_x_no, self.selection.Start, self.selection.End)
		return [x, y]

	def get_xy_from_x_to_nth_word_end(self, input_x_no, input_no):
		"""
		커서위치인 x를 기준으로 n번째 워드의 시작과 끝 위치

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		self.doc.Range(input_x_no, input_x_no).Select()
		self.selection.MoveRight(Unit=letter_type_no, Count=input_no - 1)
		self.selection.Expand(letter_type_no)
		x = self.selection.Start = min(input_x_no, self.selection.Start, self.selection.End)
		y = self.selection.End = max(input_x_no, self.selection.Start, self.selection.End)
		return [x, y]

	def get_xy_from_x_to_para_end(self, input_x):
		"""
		선택영역의 시작점을 기준으로 워드의 좌표

		:param input_x: 정수
		:return:
		"""
		letter_type_no = self.check_letter_type_no("para")
		self.doc.Range(input_x, input_x).Select()
		self.selection.Expand(letter_type_no)
		return [self.selection.Start, self.selection.End]

	def get_xy_from_x_to_word_end(self, input_x):
		"""
		선택영역의 시작점을 기준으로 워드의 좌표

		:param input_x:정수
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		self.doc.Range(input_x, input_x).Select()
		self.selection.Expand(letter_type_no)
		return [self.selection.Start, self.selection.End]

	def get_xy_n_text_for_nth_word_in_doc(self, input_no):
		"""
		ganada 에서 n번째 단어의 글자 위치를 갖고오는 코드를 만들어봅니다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		# 보이지는 않지만 모든 글자를 갖고오는것
		result = self.doc.Content.Text
		# table 의 빈칸에 들어가는 벨소리부분을 지우는것
		result = result.replace("\x07", "")
		# 공백이 1개이상인것을 기준으로 모든 자료를 갖고오는 것
		jf_result = self.rex.search_all_by_xsql("[공백:1~]", result)
		# 보통 맨 첫글자는 공백이 아니라서, 1번으로 오면 다시 만들어 주는것
		if input_no == 1:
			x = 0
			y = jf_result[0][2]
		else:
			x = jf_result[input_no - 2][2]
			y = jf_result[input_no - 1][1]
		text = result[x:y]
		return [x, y, text]

	def get_xy_size_for_table(self, input_table_obj):
		"""
		테이블객체의 가로세로의 크기

		:param input_table_obj: 테이블객체
		"""
		table_obj = self.check_table_obj(input_table_obj)
		x_no = table_obj.Rows.Count
		y_no = table_obj.Columns.Count
		result = [x_no, y_no]
		return result

	def goto_range(self, input_range, letter_type, go_back="back", step=1):
		"""
		range 의 next 와 비슷한 효과이지만，
		range 에 없는 다양한 형 태로 가능하다
		예를들어 spelling error 이 발생하거나, 코멘트한곳등

		:param input_range: range객체
		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param go_back:
		:param step:
		:return:
		"""
		input_range.GoTo(letter_type, go_back, step)

	def goto_range_by_date(self, input_range, input_letter_type, go_back="back", step=1):
		"""
		range 의 next 와 비슷한 효과이지만，
		range 에 없는 다양한 형 태로 가능하다
		예를들어 spelling error 이 발생하거나, 코멘트한곳등
		날짜로 이동하는 것

		:param input_range: range객체
		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param go_back:
		:param step:
		:return:
		"""
		input_range.GoTo(input_letter_type, go_back, step, "Date")

	def insert_new_para_with_properties(self, input_text, size=14, font="Arial", align="right", bold=True,
										input_color="red", style="표준"):
		"""
		선택한 위치에 글을 쓴다
		형태적인 분류 : active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 : active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence : 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph : 줄바꿈이 이루어지기 전까지의 자료


		wdAlignParagraphCenter	1	Center-aligned.
		wdAlignParagraphJustify	3	Fully justified.
		wdAlignParagraphLeft	0	Left-aligned.
		wdAlignParagraphRight	2	Right-aligned.

		:param input_text: 입력글자
		:param size: 폰트 사이즈
		:param font: 폰트이름
		:param align: 정렬
		:param bold: 굵게
		:param input_color: 색이름 (xcolor스타일)
		:param style: 폰트 스타일
		"""

		rgb_int = self.colorx.change_xcolor_to_rgbint(input_color)

		self.word_application.Selection.InsertAfter(input_text + "\r\n")
		para_no = self.get_para_no_at_selection_start()
		self.select_from_doc_start_to_nth_letter_type_end("para", para_no)

		self.selection.Style = style
		self.selection.Range.Font.Name = font
		self.selection.Range.Font.Bold = bold
		self.selection.Range.Font.Size = size
		self.selection.Font.TextColor.RGB = rgb_int
		self.doc.Paragraphs(para_no - 1).Alignment = 2

	def information_for_cursor(self):
		"""
		커서관련 정보들

		:return:
		"""
		result = {}
		selection_types = {
			0: "No Selection",
			1: "Insertion Point",
			2: "Normal Text", # 텍스트를 포함한 이것저것
			3: "Frame",
			4: "Column",
			5: "Row",
			6: "Block",
			7: "Inline Shape",
			8: "Shape"}
		result["selected_item"] = selection_types[self.selection.Type]
		# 도형이 선택된 경우는 선택영역이 0,1 을 나타낸다
		result["start"] = self.selection.Start + 1
		result["end"] = self.selection.End
		# 선택영역이 없이 커서만 있는지 확인하는것
		if result["start"] == result["end"]:
			result["cursor_only"] = "yes"
		else:
			result["cursor_only"] = "no"

		# 선택되어진 방향을 나타내며, 이동할때는 이 값이 필요함
		if self.selection.Flags == 24: # wdSelStartActive 플래그 확인
			result["cursor_position"] = "right, " + str(self.selection.End)
		elif self.selection.Flags == 25:
			result["cursor_position"] = "left, " + str(self.selection.Start + 1)
		else:
			result["cursor_position"] = "error"
		return result

	def information_for_doc(self):
		"""
		현재 문서의 기본적인 정보들을 알려줍니다

		:return:
		"""
		result = {}

		file_name = self.get_active_doc_name()
		para_no = self.count_para_in_doc()
		word_no = self.count_word_in_doc()
		char_no = self.count_char_in_doc()
		result["file_name"] = file_name
		result["para_no"] = para_no
		result["word_no"] = word_no
		result["char_no"] = char_no
		return result

	def information_for_range(self, input_range):
		"""
		range에대한 정보를 알려줍니다

		:param input_range: range객체
		:return:
		"""
		x = input_range.Start
		y = input_range.End
		self.doc.Range(Start=x, End=y).Select()
		result = self.information_for_selection()
		return result

	def information_for_selection(self):
		"""
		현재 선택된 자료의 정보를 알려준다
		"""
		result = {}
		len_char = self.selection.Range.ComputeStatistics(3)
		result["len_char"] = len_char
		len_word = self.selection.Range.ComputeStatistics(0)
		result["len_word"] = len_word
		len_line = self.selection.Range.ComputeStatistics(1)
		result["len_line"] = len_line
		len_para = self.selection.Range.ComputeStatistics(4)
		result["len_para"] = len_para
		len_page = self.selection.Range.ComputeStatistics(2)
		result["len_page"] = len_page

		start_word_no = self.get_char_no_at_selection_start()
		result["start_word_no"] = start_word_no

		result["start_page_no"] = self.selection.Information(1) #시작 페이지 번호
		result["end_page_no"] = self.selection.Information(3) #끝 페이지 번호
		result["end_section_no"] = self.selection.Information(2) #끝 섹션 번호
		result["is_in_table"] = self.selection.Information(12) #테이블안의 자료인지
		result["start_y_no_in_table"] = self.selection.Information(16) #테이블에서 처음것의 y번호
		result["start_x_no_in_table"] = self.selection.Information(13) #테이블에서 처음것의 x번호
		result["end_y_no_in_table"] = self.selection.Information(14) #테이블에서 마지막것의 y번호
		result["end_x_no_in_table"] = self.selection.Information(17) #테이블에서 마지막것의 x번호
		result["start_char_no_in_line"] = self.selection.Information(9) #라인의 처음에서 첫번째 문자의 시작 번호
		result["start_line_no"] = self.selection.Information(10) #첫번째 문자의 라인번호
		result["max_table_x_no"] = self.selection.Information(18) #테이블에서 최대가능 x줄수
		result["max_table_y_no"] = self.selection.Information(15) #테이블에서 최대가능 y줄수
		result["total_page_no"] = self.selection.Information(4)
		result["text"] = self.word_application.Selection.Text #선택된 문자

		return result

	def insert_check_box_at_selection_end(self):
		"""
		추가하기 : 현재 위치에 체크박스를 넣는것
		3:콤보박스

		:return:
		"""
		self.doc.ContentControls.Add(8, self.selection)

	def insert_new_line_at_selection_end(self, times = 1):
		"""
		추가하기 : 선택영역의 끝에 새로운 라인을 넣는 것
		:return:
		"""
		for one in range(times):
			self.selection.InsertBefore("\r\n")

	def insert_one_xline_at_end_of_table(self, input_table_obj):
		"""
		추가하기 : 테이블에 가로행을 추가하는것 (아랫부분에 추가)

		:param table_obj: 테이블 객제
		"""
		total_row = input_table_obj.Rows.Count
		input_table_obj.Rows(total_row).Select()
		self.selection.InsertRowsBelow(1)

	def insert_picture_at_selection_end(self, file_full_name, size_w, size_h):
		"""
		추가하기 : 커서위치에 그림삽입

		:param file_full_name: 화일 이름
		:param size_w: 넓이
		:param size_h: 높이
		"""
		current_pic = self.word_application.Selection.range.InlineShapes.AddPicture(file_full_name)
		current_pic.Height = size_h
		current_pic.Width = size_w

	def insert_picture_in_table_at_xy(self, input_table_obj, xy, file_full_name, padding=1):
		"""
		추가하기 : 테이블의 크기게 맞도록 사진을 넣기

		:param input_table_obj: 테이블 객제
		:param xy:
		:param file_full_name: 화일 이름
		:param padding:
		:return:
		"""
		if type(input_table_obj) == type(1):
			input_table_obj = self.doc.Tables(input_table_obj)
		range_obj = input_table_obj.Cell(Row=xy[0], Column=xy[1]).Range
		cell_w = input_table_obj.Cell(Row=xy[0], Column=xy[1]).Width - padding
		cell_h = input_table_obj.Cell(Row=xy[0], Column=xy[1]).Height - padding
		picture_obj = range_obj.InlineShapes.AddPicture(file_full_name)
		picture_obj.Width = cell_w
		picture_obj.Height = cell_h

	def insert_xxline_in_table(self, input_table_obj, xx):
		"""
		추가하기 : 테이블객체의 테이블에 가로행을 추가하는 것 (아랫부분에 추가)

		:param input_table_obj: 테이블 객제
		:param xx: 가로행의 시작 번호
		"""
		input_table_obj.Rows(xx[0]).Select()
		self.selection.InsertRowsBelow(xx[1] - xx[0])

	def insert_yyline_in_table(self, input_table_obj, yy):
		"""
		추가하기 : 테이블객체의 테이블에 세로행을 추가하는 것 (오른쪽에 추가)

		:param input_table_obj: 테이블 객제
		:param yy: 세로행의 시작 번호
		"""
		input_table_obj.Columns(yy[0]).Select()
		self.selection.InsertColumnsRight(yy[1] - yy[0])

	def is_xcolor_style(self, input_xcolor):
		"""
		xcolor용
		입력된 자료의 형태가, xcolor형식인지를 확인하는 것

		:param input_xcolor:색이름 (xcolor스타일)
		:return:
		"""
		result1 = self.rex.search_all_by_xsql("[한글&영어:2~10][숫자:0~7]", str(input_xcolor))
		result2 = self.rex.search_all_by_xsql("[한글&영어:2~10][+-:0~7]", str(input_xcolor))

		if result1 and result2:
			result = result1[0]
		elif result1 and not result2:
			result = result1[0]
		elif not result1 and result2:
			result = result2[0]
		elif not result1 and not result2:
			result = False
		return result

	def make_bookmark_for_range(self, input_range, input_bookmark_name):
		"""
		만들기 : 북마크를 영역으로 설정

		:param input_range: range객체
		:param input_bookmark_name: 북마크이름
		"""
		input_range.Bookmarks.Add(Name=input_bookmark_name)

	def make_bookmark_for_xy(self, xy, input_bookmark_name):
		"""
		만들기 : 북마크를 이름으로 설정

		:param xy:
		:param input_bookmark_name: 북마크이름
		"""
		my_range = self.make_new_range_by_xy(xy)
		my_range.Bookmarks.Add(Name=input_bookmark_name)

	def make_field_format(self, field_name, format_style=""):
		"""
		필드의 포멧을 적용하는 부분을 위한 것이다
		"PAGE" 이렇게 쌍따움표를 만들어야 한다

		:param field_name:
		:param format_style:
		:return:
		"""
		self.varx["field_type_vs_enum"] = {"today": "DATE", "createdate": "CREATEDATE", "filename": "FILENAME", "page": "PAGE", "total_page": "NUMPAGES",
										 "username": "USERNAME", "title": "TITLE", "now": "TIME", "subject": "SUBJECT"}
		if format_style == "":
			result = '"' + self.varx["field_type_vs_enum"][field_name] + '"'
		else:
			result = '"' + self.varx["field_type_vs_enum"][field_name] + '"' + f" \\@ {format_style}"
		return result

	def make_font_dic_by_auto(self, *input_list):
		"""
		자주 사용하는 폰트는 그냥 아무럿게나 편하게 입력하면 사용이 가능하도록 하기위하여 만든것이다

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		result = {}
		for one in input_list:
			if type(one) == type(123):
				result["size"] = one
			elif one in ["bold", "굵게", "찐하게", "진하게"]:
				result["bold"] = one
			elif one in ["italic", "이태리", "이태리체", "기울기"]:
				result["italic"] = one
			elif one in ["strikethrough", "취소선", "취소", "통과선", "strike"]:
				result["strikethrough"] = one
			elif one in ["underline", "밑줄"]:
				result["underline"] = one
			elif one in ["left", "right", "middle", "왼쪽", "중간", "오른쪽"]:
				result["align_h"] = one
			elif one in ["middle", "top", "bottom", "중간", "위", "아래"]:
				result["align_v"] = one
			else:
				try:
					self.colorx.check_input_color(one)
					result["rgbint"] = self.colorx.change_xcolor_to_rgbint(one)
				except:
					print("발견 못한 것 => ", one)
		return result

	def make_new_doc(self):
		"""
		만들기 : 새 문서 만들기
		"""
		self.word_application.Documents.Add()

	def make_new_doc_for_range(self, x, y, new_doc_name=""):
		"""
		만들기 : 워드화일의 일정부분을 새로운 워드를 열어서 저장하는 것

		:param x:
		:param y:
		:param new_doc_name: 새로운 문서이름
		:return:
		"""
		input_range = self.doc.Range(x, y)
		input_range.Copy()
		self._check_doc("new")
		self.selection.FormattedText = input_range
		self.save_as(new_doc_name)

	def make_new_line(self):
		"""
		만들기 : 새로운 라인을 넣는 것
		:return:
		"""
		self.insert_new_line_at_selection_end()

	def make_new_range_by_xy(self, xy):
		"""
		만들기 : 그냥 range 라는 단어를 썼다가，파이썬의 예약어와 충돌을 일으켰다

		:param xy:
		:return:
		"""
		new_range = self.doc.Range(xy[0] - 1, xy[1])
		return new_range

	def new_shape(self, shape_name=None, pxy_list=None, size_whlist=[100, 100], transparency_0_1=None,
				 rotation_degree=None):
		"""
		만들기 : 새로운 도형 만들기

		:param shape_name: 도형이름
		:param pxy_list:
		:param size_whlist:
		:param transparency_0_1:
		:param rotation_degree:
		:return:
		"""
		shape_enum = self.varx["shape_name_vs_enum"][shape_name]
		if not pxy_list: pxy_list = self.get_pxy_at_cursor_end()
		shape = self.doc.Shapes.AddShape(shape_enum, pxy_list[0], pxy_list[1], size_whlist[0], size_whlist[1])
		if rotation_degree:
			shape.Rotation = rotation_degree
		if transparency_0_1: shape.Fill.Transparency = transparency_0_1

	def merge_entire_xline_at_table_obj(self, input_table_obj, start_x):
		"""
		병합 : 선택된 가로줄을 전부 병합시키는것

		:param input_table_obj: 테이블 객제
		:param start_x: 가로줄번호
		"""
		count_y = input_table_obj.Columns.Count
		count_x = input_table_obj.Rows.Count
		input_table_obj.Cell(start_x, 1).Merge(MergeTo=input_table_obj.Cell(start_x, count_y))

	def merge_entire_yline_at_table_obj(self, input_table_obj, start_y):
		"""
		병합 : 선택된 세로줄을 전부 병합시키는것

		:param input_table_obj: 테이블 객제
		:param start_y: 세로줄번호
		"""
		count_y = input_table_obj.Columns.Count
		count_x = input_table_obj.Rows.Count
		input_table_obj.Cell(1, start_y).Merge(MergeTo=input_table_obj.Cell(count_x, start_y))

	def merge_xyxy_in_table_obj(self, input_table_obj, xyxy):
		"""
		병합 : 테이블의 가로와 세로번호까지의 영역을 병합

		:param input_table_obj: 테이블 객제
		:param xyxy: [가로시작, 세로시작, 가로끝, 세로끝]
		"""
		my_range = self.doc.Range(Start=input_table_obj.Cell(xyxy[0], xyxy[1]).Start,
								 End=input_table_obj.Cell(xyxy[2], xyxy[3]).End)
		my_range.Select()
		self.selection.Cells.Merge()

	def move_aaa(self):
		"""

		:return:
		"""
		self.selection.MoveEndUntil(self.varx["goto_vs_enum"]["line"])

	def move_cursor_from_doc_start_to_nth_char_end(self, input_no):
		"""
		커서이동 : 문서처음에서 n번째 글자의 위치로 커서를 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no - 1)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no - 1)

	def move_cursor_from_doc_start_to_nth_char_start(self, input_no):
		"""
		커서이동 : 문서의 처음에서 n번째 글자 위치로 커서를 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)

	def move_cursor_from_doc_start_to_nth_letter_type_end(self, letter_type, input_no):
		"""
		커서이동 : 문서처음에서 n번째 글자형식의 끝으로 커서 이동

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()

		letter_type_no = self.check_letter_type_no(letter_type)

		if input_no > 0:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no)

	def move_cursor_from_doc_start_to_nth_letter_type_start(self, letter_type, input_no):
		"""
		커서이동 : 문서처음에서 n번째 글자형식에 따라서 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		self.move_cursor_to_doc_start()

		letter_type_no = self.check_letter_type_no(letter_type)

		if input_no > 0:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveRight(Unit=letter_type_no,
										 Count=input_no) # self.varx["letter_type_vs_enum"]["char"]
			else:
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no)

	def move_cursor_from_doc_start_to_nth_line_end(self, input_no):
		"""
		이동 : 현재커서를 문서의 처음에서부터 n번째 라인의 맨앞으로 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_doc_start_to_nth_line_start(self, input_no):
		"""
		커서이동 : 현재커서를 문서의 처음에서부터 n번째 라인의 맨앞으로 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_doc_start_to_nth_para_end(self, input_no):
		"""
		이동 : 현재커서를 문서의 처음에서부터 n번째 문단의 맨앞으로 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no - 1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no - 1)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_doc_start_to_nth_para_start(self, input_no):
		"""
		커서이동 : 현재커서를 문서의 처음에서부터 n번째 문단의 맨앞으로 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no - 1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no - 1)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_doc_start_to_nth_word_end(self, input_no):
		"""
		커서이동 : 문서 처음을 기준으로 n번째 단어 끝으로 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_range_start_to_nth_letter_type_end(self, input_range, letter_type, input_no):
		"""
		이동 : range영역의 시작위치를 기준으로 입력 글자의 형태에 따라 n번째의 끝까지의 시작과 끝 번호

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_range == "":
			input_range = self.range
		letter_type_no = self.check_letter_type_no(letter_type)
		input_range.Collapse()
		# range_start
		if letter_type_no in [4]:
			input_no = input_no - 1
		input_range.Next(Unit=letter_type_no, Count=input_no)
		input_range.EndOf(letter_type_no, 0)

	def move_cursor_from_selection_end_to_next_line_end(self):
		"""
		이동 : Action : 다음줄로 이동
		끝커서의 위치를 기준으로 그다음줄로 커서가 이동
		영역없음, 커서만 이동
		"""

		self.selection.MoveDown(self.varx["letter_type_vs_enum"]["line"])
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_next_line_start(self):
		"""
		이동 : 기준커서 : 선택영역의 제일끝
		라인의 제일처음 커서로 이동
		:return:
		"""
		self.selection.GoToNext(self.varx["goto_vs_enum"]["line"])
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_next_word_end(self):
		"""
		커서이동 : 선택영역 끝에서 n번째 단어 끝위치로 커서 이동
		"""
		self.selection.MoveRight(self.varx["letter_type_vs_enum"]["word"])
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_char_end(self, input_no):
		"""
		커서이동 : 선택영역 끝에서 n번째 문자 끝위치로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_from_selection_end_to_nth_letter_type_end("char", input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_char_start(self, input_no):
		"""
		커서이동 : 선택영역에서 n번째 글자 위치로 커서를 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_letter_type_end(self, letter_type, input_no):
		"""
		커서이동 : 가능한 형식
		movedown이 되는 것
		"cell" = 12, "character" = 1, "char" = 1, "column" = 9
		"item" = 16, "line" = 5, "paragraph" = 4, "para" = 4
		"row" = 10, "section" = 8, "sentence" = 3, "story" = 6
		"table" = 15, "word" = 2

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no(letter_type)
		if input_no > 0:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no)

	def move_cursor_from_selection_end_to_nth_letter_type_start(self, letter_type, input_no):
		"""
		커서이동 : 선택영역에서 글자형태에 따라서 n번째로 커서 이동
		movedown이 되는 것
		"cell" = 12,"char" = 1, "column" = 9, "item" = 16, "line" = 5, "para" = 4
		"row" = 10, "section" = 8, "sentence" = 3, "story" = 6, "table" = 15, "word" = 2

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no(letter_type)
		if input_no > 0:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no)

	def move_cursor_from_selection_end_to_nth_line_end(self, input_no):
		"""
		커서이동 : 현재영역에서 n번째 line의 처음으로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_para_end(self, input_no):
		"""
		커서이동 : 선택영역에서 n번째 문단 끝으로 커서이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_para_start(self, input_no):
		"""
		커서이동 : 현재영역에서 n번째 para으로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_sentence_end(self, input_no):
		"""
		커서이동 : 선택영역에서 n번째 센텐스 끝으로 커서이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_from_selection_end_to_nth_letter_type_end("sentence", input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_sentence_start(self, input_no):
		"""
		커서이동 : 현재영역에서 n번째 sentence로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["sentence"], Count=input_no)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["sentence"], Count=input_no)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_word_end(self, input_no):
		"""
		이동 : 선택영역에서 n번째 단어 끝으로 커서이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_from_selection_end_to_nth_letter_type_end("word", input_no)
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_from_selection_end_to_nth_word_start(self, input_no):
		"""
		커서이동 : 현재영역에서 n번째 word로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no)
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_from_selection_start_to_nth_letter_type_end(self, input_letter_type, input_no):
		"""
		이동 : 선택영역의 시작위치를 기준으로 입력 글자의 형태에 따라 n번째의 끝위치까지의 시작과 끝 번호

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no(input_letter_type)
		self.selection.Collapse(1) # 0 : end, 1:start
		if letter_type_no in [4]:
			input_no = input_no - 1
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.EndOf(letter_type_no, 0)

	def move_cursor_from_selection_start_to_nth_letter_type_start(self, input_letter_type, input_no):
		"""
		이동 : 선택영역의 시작위치를 기준으로 입력 글자의 형태에 따라 n번째의 시작위치까지의 시작과 끝 번호

		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no(input_letter_type)
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.MoveDown(Unit=letter_type_no, Count=input_no)
		self.selection.StartOf(letter_type_no, 0)

	def move_cursor_from_selection_start_to_nth_line_start(self, input_no):
		"""
		커서이동 : 현재영역에서 n번째 line의 처음으로 커서 이동

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no)

		line_no = self.get_line_no_at_selection_start()
		self.move_cursor_from_doc_start_to_nth_line_start(line_no)

	def move_cursor_to_doc_end(self):
		"""
		이동 : 문서의 끝으로 커서를 이동
		맨마지막에 글자를 추가하거나 할때 사용한다
		"""
		self.selection.EndKey(Unit=6)

	def move_cursor_to_doc_start(self):
		"""
		커서이동 : 활성화된 워드화일의 처음으로 커서를 이동
		"""
		self.doc.Range(0, 0).Select()

	def move_cursor_to_selection_end(self):
		"""
		커서이동 :
		"""
		self.selection.Collapse(0) # 0 : end, 1:start

	def move_cursor_to_selection_start(self):
		"""
		커서이동 :
		"""
		self.selection.Collapse(1) # 0 : end, 1:start

	def move_cursor_to_start_of_doc(self):
		"""
		커서이동 : 활성화된 워드화일의 처음으로 커서를 이동
		"""
		self.doc.Range(0, 0).Select()

	def move_cursor_with_option(self, para=0, line=0, word=0, char=0):
		"""
		커서이동 : 현재 커서에서 원하는 곳으로 이동을 하는 것
		+ : 뒤로 이동
		- : 앞으로 이동
		0 : 그자리
		end : 끝으로
		start, start : 시작
		what : 3(라인), 1(페이지), 0(섹션), 2(테이블), 9(객체)
		Which : 1(처음), -1(끝),2(다음객체로), 3(전객체로)

		:param para: 문단
		:param line: 줄
		:param word: 단어
		:param char: 글자
		:return:
		"""

		if para != 0: self.selection.GoTo(What=4, Which=(lambda x: 2 if (x > 0) else 3)(para), Count=abs(para))
		if line != 0: self.selection.GoTo(What=3, Which=(lambda x: 2 if (x > 0) else 3)(line), Count=abs(line))
		if word != 0: self.selection.GoTo(What=2, Which=(lambda x: 2 if (x > 0) else 3)(word), Count=abs(word))
		if char != 0: self.selection.GoTo(What=1, Which=(lambda x: 2 if (x > 0) else 3)(char), Count=abs(char))

		return self.selection

	def move_range_at_nth_letter_type_end(self, input_range, input_letter_type, input_no):
		"""
		이동 : 현재 range영역 + 입력형태의 끝까지 영역을 확장 하는 것

		현재 위치에서 원하는 문자의 형태 끝까지 영역을 확대 하는 것
		move : range객체의 start를 이동시키는 것,

		letter_type : 어떻게 이동을 하는지를 설정하는 것입니다
		input_no : +는 뒤로, -는 앞으로 이동한다

		:param input_range: range 객체
		:param input_letter_type: 굴자형식
		:param input_no: 숫자
		:return:
		"""

		# 기존의 자료를 저장한다

		if input_range == "":
			input_range = self.word_application.Selection

		old_x = input_range.Start
		old_y = input_range.End
		letter_type_no = self.varx["letter_type_vs_enum"][input_letter_type]

		input_range.Move(letter_type_no, input_no)
		new_x1 = input_range.Start

		if input_letter_type in ["char", "word", "line", "para"]:
			# 어떤 형태라도 range의 끝점을 이동시키는 것
			if input_no > 0:
				input_range.Move(letter_type_no, 1)
				new_x2 = input_range.Start
				new_range_obj = self.doc.Range(old_x, new_x2)
			else:
				input_range.Move(letter_type_no, -1)
				new_x2 = input_range.Start
				new_range_obj = self.doc.Range(min(new_x1, new_x2), max(old_x, old_y))
		return new_range_obj

	def move_range_to_nth_letter_type(self, input_range, input_letter_type, input_no):
		"""
		이동 : 현재 range영역 + 입력형태의 끝까지 영역을 확장 하는 것

		현재 위치에서 원하는 문자의 형태 끝까지 영역을 확대 하는 것
		move : range객체의 start를 이동시키는 것,

		letter_type : 어떻게 이동을 하는지를 설정하는 것입니다
		input_no : +는 뒤로, -는 앞으로 이동한다

		:param input_range:
		:param input_letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		# 기존의 자료를 저장한다

		if input_range == "":
			input_range = self.word_application.Selection

		old_x = input_range.Start
		old_y = input_range.End
		letter_type_no = self.varx["letter_type_vs_enum"][input_letter_type]

		if input_letter_type in ["char", "word", "line", "para"]:
			# 어떤 형태라도 range의 끝점을 이동시키는 것
			if input_no > 0:
				input_range.Move(letter_type_no, input_no)
				new_x1 = input_range.Start
				input_range.Move(letter_type_no, 1)
				new_x2 = input_range.Start
				new_range_obj = self.doc.Range(old_x, new_x2)
			else:
				input_range.Move(letter_type_no, input_no)
				new_x1 = input_range.Start
				input_range.Move(letter_type_no, -1)
				new_x2 = input_range.Start
				new_range_obj = self.doc.Range(min(new_x1, new_x2), max(old_x, old_y))
		return new_range_obj

	def move_selection_for_graphic(self, direction_i=2, count_i=1):
		"""
		선택하는것을 이동하는 것이다

		:param item_i:
		:param direction_i: 방향
		:param count_i: 갯수
		:return:
		"""
		if type(direction_i) != type(123):
			direction_i = self.varx["direction_vs_enum"][direction_i]
		self.selection.GoTo(8, direction_i, count_i)

	def move_selection_for_item(self, item_i, direction_i=2, count_i=1):
		"""
		선택하는것을 이동하는 것이다

		:param item_i:
		:param direction_i: 방향
		:param count_i: 갯수
		:return:
		"""
		item_enum = self.varx["goto_vs_enum"][item_i]
		direction_enum = self.varx["direction_vs_enum"][direction_i]
		self.selection.GoTo(item_enum, direction_enum, count_i)

	def move_selection_for_shape(self, direction_i=2, count_i=1):
		"""
		선택하는것을 이동하는 것이다

		:param direction_i:방향
		:param count_i:갯수
		:return:
		"""
		if type(direction_i) != type(123):
			direction_i = self.varx["direction_vs_enum"][direction_i]
		self.selection.GoTo(9, direction_i, count_i)

	def move_selection_for_table(self, direction_i=2, count_i=1):
		"""
		선택하는것을 이동하는 것이다

		:param direction_i:방향
		:param count_i:갯수
		:return:
		"""
		item_enum = self.varx["goto_vs_enum"]["table"]
		direction_enum = self.varx["direction_vs_enum"][direction_i]
		self.selection.GoTo(item_enum, direction_enum, count_i)

	def move_shape_to_table(self, input_table_obj, xy_list, shape_obj):
		"""
		이것하기전에

		:param input_table_obj:
		:param xy_list:
		:param shape_obj:
		:return:
		"""
		shape_obj.Cut(input_table_obj.Cell(xy_list[0], xy_list[1]).Range.Paste())

	def new_doc(self):
		"""
		새 문서를 만들기
		"""
		self.word_application.Documents.Add()

	def new_doc_for_range(self, x, y, new_doc_name=""):
		"""
		a 워드화일의 일정부분을 새로운 워드를 열어서 저장하는 것

		:param x:
		:param y:
		:param new_doc_name:
		:return:
		"""
		input_range = self.doc.Range(x, y)
		input_range.Copy()
		self._check_doc("new")
		self.selection.FormattedText = input_range
		self.save_as(new_doc_name)

	def new_range_by_xy(self, xy):
		"""
		그냥 range 라는 단어를 썼다가，파이썬의 예약어와 충돌을 일으켰다

		:param xy:
		:return:
		"""
		new_range = self.doc.Range(xy[0] - 1, xy[1])
		return new_range

	def new_shape_by_ltwh_at_cursor_end(self, shape_name, x, y):
		"""
		새로운 도형을 left, top, width, height로 만드는 것

		:param shape_name: 도형이름
		:param x:
		:param y:
		:return:
		"""
		shape_enum = self.varx["shape_name_vs_enum"][shape_name]
		shape_obj = self.doc.Shapes.AddShape(Type=shape_enum, Left=x, Top=y, Width=50, Height=50,
											 Anchor=self.selection.Range)
		# shape_obj.ParagraphFormat.Alignment = 1

		"""
		shape_obj.PictureFormat.TransparentBackground = True
		shape_obj.Line.ForeColor.RGB = RGB(255, 0, 0)
		shape_obj.RelativeVerticalPosition = wdRelativeVerticalPositionPage
		shape_obj.Top = Selection.Information(wdVerticalPositionRelativeToPage)
		shape_obj.RelativeVerticalPosition = wdRelativeVerticalPositionPage
		shape_obj.Left = Selection.Information(wdHorizontalPositionRelativeToPage)
		shape_obj.WrapFormat.Type = wdWrapSquare

		"""

	def new_table_at_header_all(self, x_count, y_count):
		"""
		모든 헤더에 테이블을 만드는 것

		:param x_count: 세로줄수
		:param y_count: 가로줄수
		:return:
		"""
		sections = self.doc.Sections
		for section in sections:
			headers = section.Headers
			for header in headers:
				header.Range.Tables.Add(header.Range, x_count, y_count)

	def new_table_at_range_obj(self, range_obj, x_count, y_count):
		"""
		range 객체에 새로운 테이블을 만드는 것입니다

		:param range_obj: range 객체
		:param x_count: 테이블의 가로 번호
		:param y_count: 테이블의 세로 번호
		:return:
		"""
		range_obj.Tables.Add(range_obj, x_count, y_count)

	def new_table_with_black_line(self, x_no=3, y_no=3):
		"""
		만들기 : 검정색으로 테이블 만들기

		:param x_no:테이블의 가로 번호
		:param y_no:테이블의 세로 번호
		"""
		new_input_table_obj = self.new_table_with_options(x_no, y_no)
		return new_input_table_obj

	def new_table_with_no_color(self, x_no, y_no):
		"""
		추가하기 : 커서위치에 테이블삽입
		단, 선의 색이 없는 것을 적용해서 문서를 넣어서 사용하는 것을 만드는 것이다

		:param x_no: 테이블의 가로 번호
		:param y_no: 테이블의 세로 번호
		"""
		new_input_table_obj = self.new_table_with_options(x_no, y_no, "", "", "no")
		return new_input_table_obj

	def new_table_with_options(self, x_no, y_no, input_position="", input_xcolor="bla", input_line_style="basic",
							 input_height=""):
		"""
		데이블을 만드는 것

		:param x_no: 줄수
		:param y_no: 세로 항목수
		:param input_position: 라인의 위치들
		:param input_xcolor: 라인색
		:param input_line_style: 라인스타일
		:param input_height: 라인 높이
		:return:
		"""
		new_input_table_obj = self.doc.Tables.Add(self.selection.Range, x_no, y_no)
		border_color = self.colorx.change_xcolor_to_rgbint(input_xcolor)
		position_list = self.varx["position_vs_enum"][input_position]

		for line_position in position_list:
			enum = self.varx["table_line_position_vs_enum"][line_position]
			new_input_table_obj.Borders(enum).LineStyle = self.varx["table_line_style_vs_enum"][input_line_style]
			new_input_table_obj.Borders(enum).Color = border_color

		if input_height: new_input_table_obj.Rows.Height = input_height

		return new_input_table_obj

	def paint_background_for_selection(self, input_color):
		"""
		색칠하기 : 선택된 영역의 배경색을 지정하는것

		:param input_color: 색이름 (xcolor스타일)
		"""
		rgb_int = self.colorx.change_xcolor_to_rgbint(input_color)
		self.selection.Range.Shading.BackgroundPatternColor = rgb_int

	def paint_border_for_selection(self, input_color):
		"""
		색칠하기 : 선택한 영역의 외관선을 그리기

		:param input_color: 색이름 (xcolor스타일)
		"""
		rgbint = self.colorx.change_xcolor_to_rgbint(input_color)

		self.selection.Font.Borders(1).LineStyle = 1
		self.selection.Font.Borders(1).Color = rgbint

	def paint_border_for_selection_no_line(self, input_color):
		"""
		색칠하기 : 선택영역의 외곽선을 그리기

		:param input_color: 색이름 (xcolor스타일)
		"""
		self.selection.Font.Borders.Color = self.colorx.change_xcolor_to_rgbint(input_color)

	def paint_color_for_cell_in_table(self, input_table_obj, xy, color_index="red"):
		"""
		색칠하기 : 테이블객체의 가로세로번호의 셀의 배경색을 색칠하기

		:param input_table_obj: 테이블 객제
		:param xy: 테이블의 셀번호 [x, y]
		:param color_index:
		"""
		input_table_obj.Cell(xy[0], xy[1]).Shading.BackgroundPatternColor = self.varx["word"]["color_24bit"][color_index]

	def paint_foreground_for_selection(self, input_color):
		"""
		색칠하기 : 선택영역의 foreground의 음영설정
		:param input_color: 색이름 (xcolor스타일)
		"""
		self.selection.Font.Shading.ForegroundPatternColor = self.varx["colorname_vs_24bit"][input_color]

	def paint_highlight_for_selection(self, input_bg_xcolor="blu"):
		"""
		색칠하기 : 선택영역의 글자들의 배경을 하이라이트를 설정
		:param input_color: 색이름 (xcolor스타일)
		"""
		self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
			input_bg_xcolor] # input_bg_xcolor="blu"

	def paint_highlight_for_selection_by_1_10(self, input_bg_xcolor="blu"):
		"""
		색칠하기 : 선택영역의 글자들의 배경을 하이라이트를 1~10까지의 숫자로 입력
		:param input_color: 색이름 (xcolor스타일)
		"""
		# red":6,"bla": 1,"blu" : 2,"basic" : 0,"" : 0,"gra":16, "gre" : 11, "pin":5, "vio":12, "whi":8, "yel":7
		color_no_list = list(self.varx["colorname_vs_enum"].Value)
		self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
			input_bg_xcolor] # input_bg_xcolor="blu"

	def paint_highlight_from_char_no1_to_char_no2(self, input_no1, input_no2, input_bg_xcolor="blu"):
		"""
		색칠하기 : 선택영역의 글자들의 배경을 하이라이트를 설정
		:param input_color: 색이름 (xcolor스타일)

		:param input_no1: 입력번호
		:param input_no2: 입력번호
		:param input_bg_xcolor: 색이름 (xcolor스타일)
		:return:
		"""
		my_range = self.doc.Range(Start=input_no1, End=input_no2)
		my_range.HighlightColorIndex = self.varx["highlight_colorindex"][input_bg_xcolor] # input_bg_xcolor="blu"

	def paint_range(self, input_xcolor):
		"""
		색칠하기 : 선택된 영역의 배경색을 지정하는것

		:param input_color: 색이름 (xcolor스타일)
		"""
		rgb_int = self.colorx.change_xcolor_to_rgbint(input_xcolor)
		self.range.Shading.BackgroundPatternColor = rgb_int

	def paint_xcolor_for_yline_in_table(self, input_table_obj, y_no, xcolor="red"):
		"""
		색칠하기 : 테이블객체의 가로세로번호의 설의 배경색을 색칠하기

		:param input_table_obj: 테이블 객제
		:param y_no:
		:param xcolor: 색 이름 (xcolor스타일)
		:return:
		"""
		rgb_int = self.colorx.change_xcolor_to_rgbint(xcolor)
		input_table_obj.Columns(y_no).Shading.BackgroundPatternColor = rgb_int

	def paint_selection(self, input_color):
		"""
		색칠하기 : 선택영역을 색칠하기

		:param input_color: 색이름 (xcolor스타일)
		:return:
		"""

		rgb_int = self.colorx.change_xcolor_to_rgbint(input_color)
		self.selection.Range.Shading.BackgroundPatternColor = rgb_int

	def paint_shading_background_for_selection(self, input_color):
		"""
		색칠하기 : 선택영역의 배경색의 음영설정

		:param input_color: 색이름 (xcolor스타일)
		"""
		self.selection.Font.Shading.BackgroundPatternColor = self.varx["word"]["color_24bit"][input_color]

	def paint_shading_foreground_for_selection(self, input_color):
		"""
		색칠하기 : 선택영역의 foreground의 음영설정

		:param input_color: 색이름 (xcolor스타일)
		"""
		self.selection.Font.Shading.ForegroundPatternColor = self.varx["word"]["color_24bit"][input_color]

	def paint_xy_cell_in_table(self, input_table_obj, xy, color_index="red"):
		"""
		색칠하기 : 테이블객체의 가로세로번호의 셀의 배경색을 색칠하기

		:param input_table_obj: 테이블 객제
		:param xy:
		:param color_index:
		"""
		input_table_obj.Cell(xy[0], xy[1]).Shading.BackgroundPatternColor = self.varx["colorname_vs_24bit"][color_index]

	def paint_yline_in_table_with_xcolor(self, input_table_obj, y_no, xcolor="red"):
		"""
		색칠하기 : 테이블객체의 가로세로번호의 설의 배경색을 색칠하기

		:param input_table_obj: 테이블 객제
		:param y_no:
		:param xcolor: 색이름 (xcolor스타일)
		:return:
		"""

		rgb_int = self.colorx.change_xcolor_to_rgbint(xcolor)
		input_table_obj.Columns(y_no).Shading.BackgroundPatternColor = rgb_int

	def paste_selection(self):
		"""
		선택영역에 붙여넣기
		"""
		self.word_application.Selection.Paste()

	def paste_shape_at_cursor(self, input_selection):
		"""
		현재 커서의 위치에 도형을 붙여넣기 하는것
		:param input_selection:
		"""
		input_selection.Paste()

	def print_as_pdf(self, file_name):
		"""
		pdf로 저장

		:param file_name: 화일이름
		"""
		self.doc.ExportAsFixedFormat(OutputFileName=file_name, ExportFormat=17),

	def quit(self):
		"""
		워드 프로그램 종료
		"""
		self.word_application.Quit()

	def range_copy_to_selection(self):
		"""
		현재 range를 selection으로 만든다
		:return:
		"""
		self.select_xy(self.range.Start, self.range.End)

	def read_all_text_for_selection(self):
		"""
		읽어오기 : 선택영역의 텍스트
		"""
		x_no = self.word_application.Selection.Start
		y_no = self.word_application.Selection.End
		temp = self.doc.Range(x_no, y_no).Text
		result = temp.split(chr(13))
		all_text = ""
		for one in result:
			all_text = all_text + one
		return all_text

	def read_all_text_in_doc(self):
		"""
		읽어오기 : 현재 문서에서 모든 텍스트만 돌려준다
		"""
		self.select_all()
		result = self.read_all_text_for_selection()
		return result

	def read_table_as_l2d(self, table_no=1):
		"""
		읽어오기 : 테이블의 모든 값을 2차원 리스트형태의 값으로 읽어오는것

		:param table_no: 테이블 번호
		"""

		result = []
		table = self.doc.Tables(table_no)
		table_x_no = table.Rows.Count
		table_y_no = table.Columns.Count
		for x in range(1, table_x_no + 1):
			temp_line = []
			for y in range(1, table_y_no + 1):
				aaa = table.Cell(Row=x, Column=y).Range.Text
				temp_line.append(str(aaa).replace("\r\x07", ""))
			result.append(temp_line)
		return result

	def read_table_index_by_paragraph_index(self, input_no):
		"""
		읽어오기 : 아래의 것은 잘못된 부분이 있어서, 변경을 하였다
		paragraph번호에 따라서 그안에 테이블이 있으면, 테이블의 index번호를 갖고온다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		result = None
		my_range = self.doc.Paragraphs(input_no + 1).Range
		try:
			if my_range.Information(12):
				tbl_index = self.count_table_in_selection()
				if tbl_index:
					result = tbl_index
		except:
			result = None
		return result

	def read_text_between_para_1_to_para_2(self, para1_index, para2_index):
		"""
		읽어오기 : 선택한 2개의 문단 번호 사이의 글을 돌려준다

		:param para1_index: 문단 번호
		:param para2_index: 문단 번호
		"""
		start = self.doc.Paragraphs(para1_index).Range.Start
		end = self.doc.Paragraphs(para2_index).Range.End
		result = self.doc.Range(start, end).Text
		return result

	def read_text_for_all_para_as_l1d(self):
		"""
		읽어오기 : 모든 paragraph를 리스트로 만들어서 돌려주는 것
		"""
		result = []
		para_nums = self.doc.Paragraphs.Count
		for no in range(1, para_nums + 1):
			result.append(self.doc.Paragraphs(no).Range.Text)
		return result

	def read_text_for_current_char(self):
		"""
		읽어오기 : 현재 커서가 있는 문단을 선택해서, 그 문단 전체의 text를 돌려준다
		형태적인 분류 : active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 : active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence : 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph : 줄바꿈이 이루어지기 전까지의 자료

		:param input_no: 번호
		"""
		# self.expand_selection_to_nth_char(input_no)
		return self.word_application.Selection.Text

	def read_text_for_current_line(self):
		"""
		읽어오기 : 현재 커서가있는 라인의 전체글을 읽어오기

		:param input_no: 번호
		"""
		self.select_current_line_at_selection_end()
		return self.word_application.Selection.Text

	def read_text_for_current_para(self, input_no=1):
		"""
		읽어오기 : 현재 커서가 있는 문단을 선택해서, 그 문단 전체의 text를 돌려준다
		형태적인 분류 : active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 : active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence : 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph : 줄바꿈이 이루어지기 전까지의 자료

		Range객체.Goto : What=글자형태, Which=방향, Count=갯수

		:param input_no: 번호

		"""

		self.selection.GoTo(What=self.varx["goto_vs_enum"]["footnote"], Which=self.varx["direction_vs_enum"]["first"],
							Count=input_no)
		result = self.word_application.Selection.range.Text
		return result

	def read_text_for_current_range(self):
		"""
		읽어오기 : range영역의 text를 갖고온다
		"""
		result = self.doc.Range().Text
		return result

	def read_text_for_current_word(self):
		"""
		읽어오기 : 커서가 있는 단어를 읽어오기
		:return:
		"""
		myRange = self.word_application.Words(1)
		result = myRange.Text
		return result

	def read_text_for_doc(self):
		"""
		읽어오기 : 현재 문서에서 모든 텍스트만 돌려준다
		"""
		self.select_all()
		result = self.read_all_text_for_selection()
		return result

	def read_text_for_doc_for_code(self):
		"""
		읽어오기 : 현재 문서에서 모든 텍스트만 돌려준다
		"""
		result = self.doc.Range().Text
		return result

	def read_text_for_line_at_selection_end(self):
		"""
		읽어오기 : 현재 커서의 시작 라인번호
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_nth_line_at_doc_start(start_line_no_at_cursor)
		self.expand_selection_to_nth_line_end(1)
		return self.word_application.Selection.Text

	def read_text_for_nth_line_at_doc_start(self, input_no):
		"""
		읽어오기 : n번째 라인의 값을 갖고오기

		:param input_no: 번호
		"""
		self.select_nth_line_at_doc_start(input_no)
		result = self.read_all_text_for_selection()
		return result

	def read_text_for_nth_line_at_selection_end(self, input_no):
		"""
		읽어오기 : n번째 라인의 값을 갖고오기

		:param input_no: 번호
		"""
		self.select_from_selection_end_to_nth_line_end(input_no)
		line_no = self.get_line_no_at_selection_end()
		self.select_nth_line_at_doc_start(line_no)
		result = self.read_all_text_for_selection()
		return result

	def read_text_for_para_no(self, input_no):
		"""
		읽어오기 : paragraph 번호에 따라서 해당하는 paragraph의 text 를 갖고오는것
		형태적인 분류 - active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 - active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence - 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph - 줄바꿈이 이루어지기 전까지의 자료

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		aaa = self.doc.Paragraphs(input_no)
		result = aaa.Range.Text
		return result

	def read_text_for_range(self):
		"""
		읽어오기 : range가 있으면, 그것을 없으면 selection의 값을 갖고온다

		:param input_range_obj: range 객체
		"""
		if self.range:
			text = self.range.Text
		else:
			text = self.selection.Text

		return text

	def read_text_for_selection(self):
		"""
		선택한 영역의 글자 읽어오기

		:return:
		"""
		x_no = self.word_application.Selection.Start
		y_no = self.word_application.Selection.End
		temp = self.doc.Range(x_no, y_no).Text
		result = temp.split(chr(13))
		return result

	def read_text_for_selection_as_list(self):
		"""
		읽어오기 : 선택영역의 문자를 리스트로 읽어오기
		:return:
		"""
		x_no = self.word_application.Selection.Start
		y_no = self.word_application.Selection.End
		temp = self.doc.Range(x_no, y_no).Text
		result = temp.split(chr(13))
		return result

	def read_text_for_selection_as_one_text(self):
		"""
		읽어오기 : 선택영역의 글자를 읽어오기
		selection.Text도 있지만, 이것은 여러줄일때는 마지막줄만 나타난다

		:return:
		"""
		x_no = self.word_application.Selection.Start
		y_no = self.word_application.Selection.End
		temp = self.doc.Range(x_no, y_no).Text
		result = temp.split(chr(13))
		all_text = ""
		for one in result:
			all_text = all_text + one
		return all_text

	def read_text_from_cursor_to_next_line_end(self):
		"""
		읽어오기 : 현재 커서가 있는 라인의 다음줄을 뜻한다
		커서의 위치는 커서가 시작하는 위치이다
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_nth_line_at_doc_start(start_line_no_at_cursor + 1)
		self.expand_selection_to_nth_line_end(1)
		return self.word_application.Selection.Text

	def read_text_from_cursor_to_nth_line_end(self, input_no):
		"""
		읽어오기 : 현재 커서가 있는 라인의 다음줄을 뜻한다
		커서의 위치는 커서가 시작하는 위치이다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_nth_line_at_doc_start(start_line_no_at_cursor + 1)
		self.select_from_selection_end_to_nth_line_end(input_no)
		return self.word_application.Selection.Text

	def read_text_from_doc_start_to_nth_char_end(self, input_no):
		"""
		읽어오기 : 문서의 처음에서부터 n번째 글자를 선택하는 방법

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.select_from_doc_start_to_nth_char_end(input_no)
		self.expand_selection_to_nth_char_end(1)
		return self.word_application.Selection.Text

	def read_text_from_doc_start_to_nth_line_end(self, input_no):
		"""
		읽어오기 : 문서의 처음에서부터 n번째 라인을 선택하는 방법

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.select_nth_line_at_doc_start(input_no)
		self.expand_selection_to_nth_line_end(1)
		return self.word_application.Selection.Text

	def read_text_from_doc_start_to_nth_para_end(self, input_no):
		"""
		읽어오기 : paragraph 번호에 따라서 해당하는 paragraph의 text 를 갖고오는것
		형태적인 분류 - active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 - active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence - 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph - 줄바꿈이 이루어지기 전까지의 자료

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		aaa = self.doc.Paragraphs(input_no)
		result = aaa.Range.Text
		return result

	def read_text_from_doc_start_to_nth_word_end(self, input_no):
		"""
		읽어오기 : 문서의 처음에서부타 n번째의 단어를 갖고오는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		new_range = self.doc.Range(Start=0, End=len(self.doc.Characters))
		result = new_range.Words(input_no)
		return result

	def read_text_from_para_start_by_len(self, input_index, x, length):
		"""
		읽어오기 : 선택된 문단에서 몇번째의 글을 선택하는 것
		일정 영역의 자료를 갖고오는 3
		paragraph를 선택한다, 없으면 맨처음부터
		형태적인 분류 - active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 - active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence - 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph - 줄바꿈이 이루어지기 전까지의 자료

		:param input_index:
		:param x:
		:param length:
		"""
		paragraph = self.doc.Paragraphs(input_index)
		# 맨앞에서 몇번째부터, 얼마의 길이를 선택할지를 선정
		x_no = paragraph.Range.Start + x - 1
		y_no = paragraph.Range.Start + x + length - 1
		result = self.doc.Range(x_no, y_no).Text
		return result

	def read_text_from_selection_end_to_next_line_end(self):
		"""
		읽어오기 : 현재 커서가 있는 라인의 다음줄을 뜻한다
		커서의 위치는 커서가 시작하는 위치이다
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_nth_line_at_doc_start(start_line_no_at_cursor + 1)
		self.expand_selection_to_nth_line_end(1)
		return self.word_application.Selection.Text

	def read_text_from_selection_end_to_nth_char_end(self):
		"""
		읽어오기 : 선택영역의 끝에서 n번째 글자의 끝부분에 글씨쓰기
		:return:
		"""
		rng_obj = self.word_application.Selection
		return rng_obj.Text

	def read_text_from_selection_end_to_nth_line_end(self, input_no):
		"""
		읽어오기 : 현재 커서가 있는 라인의 다음줄을 뜻한다
		커서의 위치는 커서가 시작하는 위치이다

		:param input_no: 번호
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_nth_line_at_doc_start(start_line_no_at_cursor + 1)
		self.select_nth_line_at_selection_end(input_no)
		return self.word_application.Selection.Text

	def read_text_from_selection_start_to_nth_char_end(self, input_no):
		"""
		읽어오기 : 선택영역에서 n번째 글자까지의 문자를 읽어오기

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_from_selection_end_to_nth_char_end(input_no)
		return self.selection.Text

	def read_text_from_start_of_para_by_len(self, input_index, x, length):
		"""
		읽어오기 : 선택된 문단에서 몇번째의 글을 선택하는 것
		일정 영역의 자료를 갖고오는 3
		paragraph를 선택한다, 없으면 맨처음부터
		형태적인 분류 - active_doc(화일) > sentence(문장) > word(한 단어) > character(한글자)
		의미적인 분류 - active_doc(화일) > paragraph(문단) > line(줄) > word(한 단어) > character(한글자)
		sentence - 표현이 완결된 단위, 그 자체로 하나의 서술된 문장이 되는 것
		paragraph - 줄바꿈이 이루어지기 전까지의 자료

		:param input_index:
		:param x:
		:param length:
		"""
		paragraph = self.doc.Paragraphs(input_index)
		# 맨앞에서 몇번째부터, 얼마의 길이를 선택할지를 선정
		x_no = paragraph.Range.Start + x - 1
		y_no = paragraph.Range.Start + x + length - 1
		result = self.doc.Range(x_no, y_no).Text
		return result

	def read_text_from_x_to_y(self, index_1, index_2):
		"""
		읽어오기 : 활성화된 워드화일의 문자번호 사이의 글자를 갖고온다

		:param index_1:
		:param index_2:
		"""
		result = self.doc.Range(index_1, index_2).Text
		return result

	def read_text_from_xy(self, x, y):
		"""
		읽어오기 : 활성화된 워드화일의 문자번호 사이의 글자를 갖고온다
		화일의 글자수를 기준으로 text를 읽어오는 것

		:param x:
		:param y:
		"""
		result = self.doc.Range(x, y).Text

	def read_text_in_table_by_xy(self, input_table_no_or_obj, lxly):
		"""
		읽어오기 : 테이블객체에서 가로세로번호의 셀의 text값을 갖고온다

		:param input_table_no_or_obj: 테이블 번호나 객체를 입력
		:param lxly: 테이블객체에서 가로세로번호
		"""
		if type(input_table_no_or_obj) == type(123):
			table_obj = self.doc.Tables(input_table_no_or_obj)
		else:
			table_obj = input_table_no_or_obj
		result = table_obj.Cell(Row=lxly[0], Column=lxly[1]).Range.Text
		# str문자들은 맨 마지막에 끝이라는 문자가 자동으로 들어가서, 이것을 없애야 표현이 잘된다

		return result[:-1]

	def read_xy_cell_in_table(self, table_index, lxly):
		"""
		읽어오기 : 테이블객체에서 가로세로번호의 셀의 text값을 갖고온다

		:param table_index: 테이블 번호 (index)
		:param lxly: 테이블객체에서 가로세로번호
		"""
		table = self.doc.Tables(table_index)
		result = table.Cell(Row=lxly[0], Column=lxly[1]).Range.Text
		# str문자들은 맨 마지막에 끝이라는 문자가 자동으로 들어가서, 이것을 없애야 표현이 잘된다
		return result[:-1]

	def regex_for_selection(self, xsql):
		"""
		읽어오기 : 선택영역을 정규표현식으로 찾은 값을 갖고오기

		:param xsql: xy_re형식의 정규표현식
		:return:
		"""
		text_value = self.read_text_for_selection()
		result = self.rex.search_all_by_xsql(xsql, text_value)
		return result

	def release_selection(self, start_or_end=0):
		"""
		커서를 selection의 맨 끝을 기준으로 옮겨서 해제한것
		만약 선택영역에서 선택부분을 없애면서，커서를 기존 선택부분의 제일 앞으로 하려면 1을
		맨끝의 다음번 문자로 이동하려면，0을 넣는다
		예 : 12345678 중 345 가 선택되엇다면, 0 -> 6 앞에, 1 은 1 앞으로 커서이동

		:param start_or_end: 앞쪽으로 끝을 낼것인지 뒷쪽으로 커서를 옮길것인지 선택
		:return:
		"""
		self.selection.Collapse(start_or_end) # 0 : end, 1:start

	def repalce_for_selection(self, input_text):
		"""
		선택되어진 영역의 값을 변경

		:param input_text: 바꿀 문자
		"""
		self.selection.Range.Text = input_text

	def repalce_selection_text_to_input_text(self, input_text):
		"""
		선택되어진 영역의 값을 변경

		:param input_text: 바꿀 문자
		"""
		self.selection.Range.Text = input_text

	def replace_all(self, before_text, after_text):
		"""
		워드화일에서 한번에 원하는 글자를 바꾸는 것

		:param before_text: 찾을 문자
		:param after_text: 바꿀 문자
		:return:
		"""
		# aaa.Find.Execute(찾을단어, False, False, False, False, False, 앞쪽으로검색, 1, True, 바꿀문자, 전체변경/Replace)
		aaa = self.doc.Range(Start=0, End=self.doc.Characters.Count)
		aaa.Find.Execute(before_text, False, False, False, False, False, True, 1, True, after_text, 2)

	def replace_all_in_doc_with_colored(self, search_text, replace_text, font_xcolor="red", bg_color="yel"):
		"""
		찾기/바꾸기 : 화일안의 모든 문자를 바꾸고 색칠하기

		:param search_text: 찾을 문자
		:param replace_text: 바꿀 문자
		:param font_xcolor: 폰트용 색상
		:param bg_color: 백그라운드용 색상
		:return:
		"""

		self.release_selection()
		# 이것이 없으면, 커서이후부터 찾는다
		self.move_cursor_to_doc_start()
		result = []
		rgb_int = self.colorx.change_xcolor_to_rgbint(font_xcolor)

		while self.selection.Find.Execute(search_text, input_bg_xcolor="blu"):
			self.selection.Range.Font.Italic = True
			self.selection.Range.Font.TextColor.RGB = rgb_int
			self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
				bg_color] # input_bg_xcolor="blu"

			start_no = self.selection.Range.Start
			end_no = start_no + len(search_text)
			self.selection.Range.Text = replace_text

	def replace_all_in_doc_with_xsql(self, xsql="", replace_text=""):
		"""
		찾기/바꾸기 : xsql로 문서안의 모든 글자를 변경

		:param xsql: xy_re형식의 정규표현식
		:param replace_text: 바꿀 문자
		"""
		para_nos = self.count_para_in_doc()
		for index in range(para_nos):
			my_range = self.doc.Paragraphs(index + 1).Range
			my_range_text = my_range.Text
			regex_result = self.rex.search_all_by_xsql(xsql, my_range.Text)
			if regex_result:
				for l1d in regex_result:
					my_range.Find.Execute(l1d[0], False, False, False, False, False, True, 1, True, replace_text, 2)

	def replace_all_with_color_from_selection_to_end(self, search_text, replace_text, color_name="red",
													 input_bg_xcolor="blu"):
		"""
		찾기/바꾸기 : 현재위치 이후의 모든것을 변경

		:param search_text: 찾을 문자
		:param replace_text: 바꿀 문자
		:param color_name: 컬러이름
		:param input_bg_xcolor: 색이름 (xcolor스타일)
		:return:
		"""
		self.release_selection()
		# 이것이 없으면, 커서이후부터 찾는다
		# self.move_cursor_to_doc_start()
		result = []
		rgb_int = self.colorx.change_xcolor_to_rgbint(color_name)

		while self.selection.Find.Execute(search_text):
			self.selection.Range.Font.Italic = True
			self.selection.Range.Font.TextColor.RGB = rgb_int
			self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
				input_bg_xcolor] # input_bg_xcolor="blu"

			start_no = self.selection.Range.Start
			end_no = start_no + len(search_text)
			self.selection.Range.Text = replace_text

	def replace_each_para_by_xsql_for_selection(self, input_xsql, replace_text):
		"""
		선택한 영역의 문단 번호를 갖고오는 것이다

		:param input_xsql: xy_re형식의 정규표현식
		:param replace_text: 바꿀 문자
		:return:
		"""
		para_2nos = self.get_para_nos_for_selection()

		for para_no in range(para_2nos[0], para_2nos[1] + 1):
			# 선택영역의 각 문단에서 "[시작][숫자&공백&.\::0~10]"에 해당하는것을 지우는 코드
			self.replace_text_for_nth_para_by_xsql(para_no, input_xsql, replace_text)

	def replace_in_doc_by_xsql(self, xsql="", replace_text=""):
		"""
		xsql로 문서안의 모든 글자를 변경

		:param xsql: xy_re형식의 정규표현식
		:param replace_text: 바꿀 문자
		"""
		para_nos = self.count_para_in_doc()
		for index in range(para_nos):
			my_range = self.doc.Paragraphs(index + 1).Range
			my_range_text = my_range.Text
			regex_result = self.rex.search_all_by_xsql(xsql, my_range.Text)
			if regex_result:
				for l1d in regex_result:
					# self.replace_one_time_from_selection(regex_result[0][0], replace_text)

					my_range.Find.Execute(l1d[0], False, False, False, False, False, True, 1, True, replace_text, 2)

	def replace_in_selection(self, replace_text):
		"""
		찾기/바꾸기 : selection값을 변경

		:param replace_text: 바꿀 문자
		"""
		self.selection.Text = replace_text

	def replace_in_selection_with_color_size_bold(self, input_text, input_color="red", input_size=11, input_bold=False):
		"""
		글쓰기 : 선택한 영역에 글을쓰면서, 색깔과 크기, bold를 설정하는 것

		:param input_text: 입력값
		:param input_color: 색이름
		:param input_size: 크기
		:param input_bold: 굵게
		:return:
		"""
		# 현재 선택된 영역에 글씨를 넣는것
		my_range = self.word_application.Selection.Range
		my_range.Text = input_text
		my_range.Bold = input_bold
		my_range.Font.Size = input_size
		my_range.Font.Color = self.varx["colorname_vs_24bit"][input_color]
		my_range.Select()

	def replace_one_time_from_selection(self, search_text, replace_text):
		"""
		전체가 아니고 제일 처음에 발견된 것만 바꾸는것
		#1 : 워드의 모든 문서를 range객체로 만드는 것

		:param search_text: 찾을 문자
		:param replace_text: 바꿀 문자
		:return:
		"""
		self.varx["wdReplaceOne"] = 1
		range_obj = self.doc.Range(Start=0, End=self.doc.Characters.Count) # 1
		range_obj.Find.Execute(search_text, False, False, False, False, False, True, 1, True, replace_text, 1)

	def replace_selection_text_to_input_text(self, replace_text):
		"""
		selection값을 변경

		:param replace_text: 바꿀 문자
		"""
		self.selection.Text = replace_text

	def replace_selection_to_input_text(self, input_value):
		"""
		선택한 영역의 모든문자를 변경하는 것

		:param input_value:
		"""
		self.word_application.Selection.Delete()
		self.word_application.Selection.InsertBefore(input_value)

	def replace_start_one_time_for_selection(self, search_text, replace_text):
		"""
		찾기/바꾸기 : 전체가 아니고 제일 처음에 발견된 것만 바꾸는것
		#1 : 워드의 모든 문서를 range객체로 만드는 것

		:param search_text: 찾을 문자
		:param replace_text: 바꿀 문자
		:return:
		"""
		self.varx["wdReplaceOne"] = 1
		range_obj = self.doc.Range(Start=0, End=self.doc.Characters.Count) # 1
		range_obj.Find.Execute(search_text, False, False, False, False, False, True, 1, True, replace_text, 1)

	def replace_text_for_nth_para_by_xsql(self, input_no, input_xsql, replace_text=""):
		"""

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_xsql:
		:param replace_text: 바꿀 문자
		:return:
		"""
		para_text = self.read_text_for_para_no(input_no)
		self.move_cursor_from_doc_start_to_nth_para_start(input_no)
		char_no = self.get_char_no_at_selection_start()
		jf_l2d = self.rex.search_all_by_xsql(input_xsql, para_text)
		self.replace_text_from_char_no1_to_char_no2(char_no + jf_l2d[0][1], char_no + jf_l2d[0][2], replace_text)
		return jf_l2d[0][0]

	def replace_text_for_selection(self, input_value):
		"""
		찾기/바꾸기 : 선택한 영역의 모든문자를 변경하는 것

		:param input_value: 입력값
		"""
		self.word_application.Selection.Delete()
		self.word_application.Selection.InsertBefore(input_value)

	def replace_text_for_xy_list(self, input_position_l2d, replace_text):
		"""
		찾기/바꾸기 : find함수들에서 찾은 위치들을 가지고, 값을 변경하는데
		길이가 다를수가 있기때문에 맨뒤에서부터 바꾸는 것을 해야 한다

		:param input_position_l2d:
		:param replace_text: 바꿀 문자
		"""
		input_position_l2d.sort()
		input_position_l2d.reverse()
		for l1d in input_position_l2d:
			range_obj = self.doc.Range(Start=l1d[0], End=l1d[1])
			range_obj.Text = replace_text

	def replace_text_from_char_no1_to_char_no2(self, input_no1, input_no2, replace_text=""):
		"""

		:param input_no1: 정수
		:param input_no2: 정수
		:param replace_text: 바꿀 문자
		:return:
		"""
		self.read_text_from_xy(input_no1, input_no2)
		self.select_xy(input_no1, input_no2)
		self.change_selection_to_input_text(replace_text)

	def run_font_style(self, input_list):
		"""
		폰트에 대한 순서없이 들어온 자료를 찾아서 self.font_dic에 넣는것

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		self.check_font_style(input_list)
		if self.font_dic["size"]:
			self.selection.Font.Size = self.font_dic["size"]
		if self.font_dic["bold"]:
			self.selection.Font.Bold = self.font_dic["bold"]
		if self.font_dic["italic"]:
			self.selection.Font.Italic = self.font_dic["italic"]
		if self.font_dic["underline"]:
			self.selection.Font.Underline = self.font_dic["underline"]
		if self.font_dic["strikethrough"]:
			self.selection.Font.StrikeThrough = self.font_dic["strikethrough"]
		if self.font_dic["color"]:
			self.selection.Font.TextColor.RGB = self.font_dic["color"]
		if self.font_dic["align"]:
			self.selection.ParagraphFormat.Alignment = self.font_dic["align"]

	def sample_003(self):
		"""

		:return:
		"""

		# selection =self.doc.Selection
		self.selection.TypeText("현재 페이지: ")
		self.selection.Fields.Add(self.selection.Range, 33)
		# 총 페이지 수 필드 삽입
		self.selection.TypeText("/총 페이지: ")
		self.selection.Fields.Add(self.selection.Range, 26)
		self.selection.TypeText("오늘 날짜: ")
		# DATE 필드 삽입 및 형식 지정 # 형식 문자열은 ₩@ "형식" 으로 지정합니다. 예: "MMMM d, yyyy" -> "October 5, 2023"
		date_field_code = {'DATE Ww@ "yyyy 년 MM 월 dd 일"'}
		self.selection.Fields.Add(self.selection.Range, -1, date_field_code)

	def save(self, file_name=""):
		"""
		화일 저장하기

		:param file_name: 화일이름
		"""
		if file_name == "":
			self.doc.Save()
		else:
			self.doc.SaveAs(file_name)

	def save_as(self, file_name):
		"""
		저장 : 다른이름으로 화일을 저장

		:param file_name: 화일이름
		"""
		self.doc.SaveAs(file_name)

	def save_as_pdf(self, file_name):
		"""
		저장 : pdf로 저장

		:param file_name: 화일이름
		"""
		self.doc.SaveAs(file_name, FileFormat=2)

	def save_xy_for_range(self):
		"""
		range객체의 x, y값을 돌려주는 것

		:return:
		"""
		self.range_x = int(self.range.Start)
		self.range_y = int(self.range.End)
		return [self.range_x, self.range_y]

	def search_all_with_color_and_return_position(self, input_text, input_bg_xcolor="blu"):
		"""
		찾기/바꾸기 : 전체 화일에서 입력글자를 찾아서 색깔을 넣기

		:param input_text: 입력글자
		:return:
		"""
		result = []
		while self.selection.Find.Execute(input_text):
			self.selection.Range.Font.Italic = True
			self.selection.Range.Font.Color = 255
			self.selection.Range.HighlightColorIndex = self.varx["highlight_colorindex"][
				input_bg_xcolor] # input_bg_xcolor="blu"
			start_no = self.selection.Range.Start
			end_no = start_no + len(input_text)
			temp = [start_no, end_no, self.selection.Range.Text]
			result.append(temp)
		return result

	def search_nth_word_after_del_x07(self, input_no, input_text=""):
		"""
		찾기 : n번째의 단어를 갖고오는 것
		기준 : 워드자료를 매크로로 읽어온것에서 "\x07" 를 지우는 것까지만 한자료

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if not input_text:
			all_text = self.doc.Content.Text
			all_text = str(all_text).replace("\x07", "")
		else:
			all_text = input_text

		result = self.rex.search_nth_result_with_resql("\S+", input_no, all_text)
		# 현재 커서의 위치를 읽어온다
		return result

	def search_nth_word_including_list_format(self, input_no, input_text=""):
		"""
		n번째 단어를 찾는것
		search는 값과 다른 정보를 갖고온다
		get은 값만 갖고온다

		:param word_no_as_code:
		:return:
		"""
		if not input_text:
			all_text = self.doc.Content.Text
		else:
			all_text = input_text

		changed_all_text = str(all_text).replace("\x07", "")
		temp = self.rex.search_nth_result_with_resql("\S+", input_no, changed_all_text)
		self.select_xy(temp[0][1], temp[0][2])
		# 현재 단어가 있는 곳의 문단 번호
		cur_para_no = self.get_para_no_at_selection_start()

		# 입력문단까지의 머릿글 갯수를 리스트형태로 작성
		listformat_no_list, listformat_no_text_list = self.count_list_formation_from_doc_start_to_para_no(cur_para_no)
		word_no_as_screen = input_no
		for no in range(len(listformat_no_list) + 1):
			count_format = 0
			temp = self.rex.search_nth_result_with_resql("\S+", input_no - no, changed_all_text)
			self.select_xy(temp[0][1], temp[0][2])
			cur_para_no = self.get_para_no_at_selection_start()
			for one in listformat_no_list:
				if one <= cur_para_no:
					count_format = count_format + 1
			if input_no - no + count_format == word_no_as_screen:
				result = self.rex.search_nth_result_with_resql("\S+", input_no - no, changed_all_text)
				return result
			elif input_no - no + count_format < word_no_as_screen:
				return str(listformat_no_list[count_format]) + "번째 문단의 머릿글 기호 : " + str(
					listformat_no_text_list[count_format])

	def search_nth_word_with_original(self, input_no, input_text=""):
		"""
		찾기 : n번째의 단어를 갖고오는 것
		기준 : 워드자료를 매크로로 읽어온것 그대로
		찾고자 하는 문장에서 n번째 찾은 것을 들려주는 것

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_text: 입력 문자
		:return:
		"""
		if not input_text:
			all_text = self.doc.Content.Text
		else:
			all_text = input_text

		result = self.rex.search_nth_result_with_resql("\S+", input_no, all_text)
		return result

	def select_all(self):
		"""
		선택하기 : 전체문서를 선택
		"""
		self.selection.WholeStory()

	def select_bookmark_by_name(self, bookmark_name):
		"""
		선택하기 : 북마크의 이름을 기준으로 그 영역을 선택하는 것

		:param bookmark_name: 북마크 이름
		"""
		my_range = self.doc.Bookmarks(bookmark_name).Range
		my_range.Select()

	def select_by_xy(self, x, lengh):
		"""
		영역을 선택하는 것
		맨앞에서 몇번째부터，얼마의 길이를 선택할지를 선정

		:param x: 정수, 뮨서 맨처음에서 x번째를 뜻함
		:param lengh:
		"""
		self.doc.Range(x, x + lengh).Select()

	def select_current_line_at_selection_end(self):
		"""
		선택하기 : 현재 위치에서 줄의 끝까지 선택
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdLine"])

	def select_current_line_at_selection_start(self):
		"""
		선택하기 : 현재 위치에서 줄의 끝까지 선택
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.select_current_line_at_selection_end()

	def select_current_para_at_selection_end(self):
		"""
		선택하기 : 현재 위치의 문단을 선택
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdParagraph"])

	def select_current_para_at_selection_start(self):
		"""
		선택하기 : 현재 위치의 문단을 선택
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdParagraph"])

	def select_current_sentence_at_selection_end(self):
		"""
		선택하기 : 현재 위치에서 줄의 처음까지
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdSentence"])

	def select_current_sentence_at_selection_start(self):
		"""
		선택하기 : 현재 위치에서 줄의 처음까지
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdSentence"])

	def select_current_word_at_selection_end(self):
		"""
		선택하기 : 현재 위치에서 단어까지 확대 된다
		단, 현재 단어가 중간에서 시작되면 단어의 처음부터 선택되어진다
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["word"])

	def select_current_word_at_selection_start(self):
		"""
		선택하기 : 현재 위치에서 단어까지 확대 된다
		단, 현재 단어가 중간에서 시작되면 단어의 처음부터 선택되어진다
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.selection.Expand(self.varx["letter_type_vs_enum"]["word"])

	def select_doc_by_name(self, input_name):
		"""
		선택하기 : 현재 open된 문서중 이름으로 active문서로 활성화 시키기

		:param input_name: 문서이름
		"""
		self.doc = self.word_application.Documents(input_name)
		self.doc.Activate()

	def select_for_range(self):
		"""
		선택하기 : range 객체의 일정부분을 영역으로 선택
		"""
		self.selection = self.doc.range

	def select_from_char_no1_to_no2(self, input_no1, input_no2):
		"""
		선택하기 : 선택영역의 글자들의 배경을 하이라이트를 설정
		:param input_color: 색이름 (xcolor스타일)

		:param input_no1:숫자(정수, 1부터 시작하는 숫자)
		:param input_no2:숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_from_doc_start_to_nth_char_start(input_no1)
		step = input_no2 - input_no1
		self.expand_selection_to_nth_char_end(step)

	def select_from_doc_start_to_next_nth_letter_type_end(self, letter_type, input_no):
		"""
		현재 위치에서 n번째뒤의 단어, 라인들을 선택하는 것

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		checked_letter_type = self.check_letter_type(letter_type)
		letter_type_no = self.check_letter_type_no(checked_letter_type)
		if input_no > 0:
			if checked_letter_type in ["char", "word", "line"]:
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no - 1, Extend=0)
				self.selection.MoveRight(Unit=letter_type_no, Count=1, Extend=1)
			else:
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no - 1, Extend=0)
				self.selection.MoveDown(Unit=letter_type_no, Count=1, Extend=1)
		else:
			if checked_letter_type in ["char", "word", "line"]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no - 1, Extend=0)
				self.selection.MoveLeft(Unit=letter_type_no, Count=1, Extend=1)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no - 1, Extend=0)
				self.selection.MoveUp(Unit=letter_type_no, Count=1, Extend=1)

	def select_from_doc_start_to_nth_char_end(self, input_no):
		"""
		선택하기 : 문서처음에서 n번째 글자까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no,
									 Extend=1) # Extend = 0 은 이동을 시키는 것이다
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no, Extend=1)

	def select_from_doc_start_to_nth_letter_type_end(self, letter_type, input_no=1):
		"""
		선택하기 : 원하는 순서의 라인의 첫번째 위치로 이동

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		letter_type_no = self.check_letter_type_no(letter_type)
		self.selection.GoTo(What=letter_type_no, Which=1, Count=input_no)
		result = self.word_application.Selection.range.Text
		return result

	def select_from_doc_start_to_nth_line_end(self, input_no):
		"""
		기준점 : 문서의 시작
		선택하기 : 어디까지 : n번째 라인 끝까지, 문서의 처음부터 n번째 line까지 선택하는 것

		:param input_no: 1번째부터 시작하는 번호
		:return:
		"""
		self.move_cursor_to_doc_start()
		letter_type_no = self.check_letter_type_no("line")
		if input_no > 0:
			self.selection.MoveDown(Unit=letter_type_no, Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=letter_type_no, Count=abs(input_no), Extend=1)

	def select_from_doc_start_to_nth_para_end(self, input_no):
		"""
		선택하기 : 문서처음에서 n번째 para까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		letter_type_no = self.check_letter_type_no("para")
		if input_no > 0:
			self.selection.MoveDown(Unit=letter_type_no, Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=letter_type_no, Count=abs(input_no), Extend=1)

	def select_from_doc_start_to_nth_sentence_end(self, input_no):
		"""
		선택하기 : 문서처음에서 n번째 sentence까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.move_cursor_to_doc_start()
		letter_type_no = self.check_letter_type_no("sentence")
		if input_no > 0:
			self.selection.MoveDown(Unit=letter_type_no, Count=input_no, Extend=1)
		else:
			self.selection.MoveUp(Unit=letter_type_no, Count=abs(input_no), Extend=1)

	def select_from_doc_start_to_nth_word_end(self, input_no):
		"""
		선택하기 : 문서처음에서 n번째 word까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""

		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no + 1, Extend=1)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=abs(input_no) + 1, Extend=1)

	def select_from_range_end_to_nth_char_end(self, input_range="", input_no=1):
		"""
		선택하기 : range끝 ~ n번째의 문자 끝

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no - 1)
		self.selection.Expand(1)

	def select_from_range_end_to_nth_line_end(self, input_range="", input_no=1):
		"""
		선택하기 : range끝 ~ n번째의 라인 끝

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)

	def select_from_range_end_to_nth_para_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range에서 n번째 para 끝까지 선택

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)

	def select_from_range_end_to_nth_word_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range 끝 ~ n번째 word 끝까지

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no, Extend=1)

	def select_from_range_end_to_previous_nth_word_by_space(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 cursor 가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들，만약 숫주와문자가 섞여있으면，그것으로 구분한다
		우리가 생각하는 단어 : 맨앞은 글자로 시작하고 맨뒤는 공백이며，이 공백까지 포함한 사이의 모든 문자들

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		input_no = input_no * -1
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		count_space = 0
		no = input_range.End
		result_text = ""
		while True:
			one_text = self.doc.Range(no, no + 1).Text
			if one_text == " " or one_text == "\r":
				count_space = count_space + 1
			if count_space == input_no:
				result_text = one_text + result_text
			elif count_space == input_no + 1:
				return result_text.strip()
			if 1 > no:
				return result_text.strip()
			no = no - 1
		return end_range

	def select_from_range_end_to_previous_nth_word_start_by_space(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 cursor 가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들，만약 숫주와문자가 섞여있으면，그것으로 구분한다
		우리가 생각하는 단어 : 맨앞은 글자로 시작하고 맨뒤는 공백이며，이 공백까지 포함한 사이의 모든 문자들

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = input_no * -1
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		count_space = 0
		no = input_range.End
		result_text = ""
		while True:
			one_text = self.doc.Range(no, no + 1).Text
			if one_text == " " or one_text == "\r":
				count_space = count_space + 1
			if count_space == input_no:
				result_text = one_text + result_text
			elif count_space == input_no + 1:
				return result_text.strip()
			if 1 > no:
				return result_text.strip()
			no = no - 1
		return end_range

	def select_from_range_start_to_next_nth_word_end(self, input_range="", input_no=1):
		"""
		양수 / 음수 => 다가능
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 curso「가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들、만약 숫주와문자가 섞여있으면，그것으로 구분한다

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		step_no = 1
		if input_no < 0:
			input_no = input_no - 1
			step_no = -2
		elif input_no == 0:
			input_no = -1
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		input_range.Move(letter_type_no, input_no)
		start_x = input_range.Start
		input_range.Move(letter_type_no, 1)
		start_y = input_range.Start
		new_range = self.doc.Range(start_x, start_y)
		return new_range

	def select_from_range_start_to_next_nth_word_end_by_space(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 cursor 가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들, 만약 숫주와문자가 섞여있으면, 그것으로 구분한다
		우리가 생각하는 단어 : 맨앞은 글자로 시작하고 맨뒤는 공백이며, 이 공백까지 포함한 사이의 모든 문자들

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		total_len = len(self.doc.Characters)
		count_space = 0
		no = input_range.End
		result_text = ""
		while True:
			one_text = self.doc.Range(no, no + 1).Text
			if one_text == " " or one_text == "\r":
				count_space = count_space + 1
			if count_space == input_no:
				result_text = result_text + one_text
			elif count_space == input_no + 1:
				return result_text.strip()
			if total_len < no:
				return result_text.strip()
			no = no + 1
		return end_range

	def select_from_range_start_to_nth_char_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 위치에서 n번째의 라인

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no - 1)
		self.selection.Expand(1)

	def select_from_range_start_to_nth_line_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range에서 n번째의 라인까지 선택

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no, Extend=1)

	def select_from_range_start_to_nth_para_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range에서 n번째 para 끝까지 선택

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no, Extend=1)

	def select_from_range_start_to_nth_word_end(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range에서 n번째 word까지 선택

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_range = self.check_range(input_range)
		input_range.MoveDown(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no, Extend=1)

	def select_from_range_to_next_nth_word_end(self, input_range="", input_no=1):
		"""
		양수 / 음수 => 다가능
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 curso「가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들、만약 숫주와문자가 섞여있으면，그것으로 구분한다

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no("word")
		step_no = 1
		if input_no < 0:
			input_no = input_no - 1
			step_no = -2
		elif input_no == 0:
			input_no = -1
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		input_range.Move(letter_type_no, input_no)
		start_x = input_range.Start
		input_range.Move(letter_type_no, 1)
		start_y = input_range.Start
		new_range = self.doc.Range(start_x, start_y)
		return new_range

	def select_from_range_to_next_nth_word_end_by_space(self, input_range="", input_no=1):
		"""
		선택하기 : 현재 range 의 맨뒷부분에서 n 번째 워드를 선택
		양수일때，range 의 뒷부분으로 cursor 가 이동, 뒤로 입력된 숫자만큼 이동한다
		단어 : 공백으로 구분되거나 숫자나 문자의 묶음들, 만약 숫주와문자가 섞여있으면, 그것으로 구분한다
		우리가 생각하는 단어 : 맨앞은 글자로 시작하고 맨뒤는 공백이며, 이 공백까지 포함한 사이의 모든 문자들

		:param input_range: range객체
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		if input_range == "":
			input_range = self.get_range_obj_for_selection()
		total_len = len(self.doc.Characters)
		count_space = 0
		no = input_range.End
		result_text = ""
		while True:
			one_text = self.doc.Range(no, no + 1).Text
			if one_text == " " or one_text == "\r":
				count_space = count_space + 1
			if count_space == input_no:
				result_text = result_text + one_text
			elif count_space == input_no + 1:
				return result_text.strip()
			if total_len < no:
				return result_text.strip()
			no = no + 1
		return end_range

	def select_from_selection_end_to_current_line_end(self):
		"""
		선택하기 : 현재 선택영역에서 라인의 끝까지 선택을 확장

		고쳐야함 : 선택영역에 색을 칠하면 전체 라인이 색칠해 진다
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.word_application.Selection.EndOf(5, 1)

	def select_from_selection_end_to_line_start(self):
		"""
		선택하기 : 현재 선택영역에서 라인의 시작점까지 선택, 반대 부분으로 선택하는 것이다
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.word_application.Selection.StartOf(5, 1)

	def select_from_selection_end_to_next_para_end(self, input_no=1):
		"""
		선택하기 : 선택영역 끝에서 n번째 문단의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_next_basic_at_selection_end("para", input_no)

	def select_from_selection_end_to_next_sentence_end(self, input_no=1):
		"""
		선택하기 : 현재 선택영역의 끝 ~ 다음 문단의 끝

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_next_basic_at_selection_end("sentence", input_no)

	def select_from_selection_end_to_next_word_end(self, input_no=1):
		"""
		선택하기 : 현재 선택영역의 끝 ~ 다음 단어의 끝
		char, word는 moveright를 사용해야 한다

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_next_basic_at_selection_end("word", input_no)

	def select_from_selection_end_to_nth_char_end(self, input_no):
		"""
		선택하기 : 선택영역 끝에서 n번째 글자의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.expand_selection_to_nth_char_end(input_no)

	def select_from_selection_end_to_nth_letter_type_end(self, letter_type, input_no):
		"""
		영역선택 : 선택영역을 기존 선택영역을 기준으로 이동시키는 것이다
		movedown이 되는 것

		:param input_no: 라인번호
		:return:
		"""
		letter_type_no = self.check_letter_type_no(letter_type)
		if input_no > 0:
			if letter_type_no in [3, 2, 1]: # "sentence" = 3,"word" = 2, "char" = 1
				self.selection.MoveRight(Unit=letter_type_no, Count=input_no, Extend=1) # Extend = 0 은 이동을 시키는 것이다
			else:
				# "cell" = 12, , "column" = 9, "item" = 16, "line" = 5, "para" = 4, "row" = 10, "section" = 8, "story" = 6, "table" = 15,
				self.selection.MoveDown(Unit=letter_type_no, Count=input_no, Extend=1)
		else:
			if letter_type_no in [3, 2, 1]:
				self.selection.MoveLeft(Unit=letter_type_no, Count=input_no, Extend=1)
			else:
				self.selection.MoveUp(Unit=letter_type_no, Count=input_no, Extend=1)

	def select_from_selection_end_to_nth_line_end(self, line_no):
		"""
		선택하기 : (라인 선택) 전체 문서에서 줄수로 선택하는것

		:param line_no: 라인번호
		:return:
		"""
		self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["wdLine"], Count=line_no)
		self.selection.Expand(self.varx["letter_type_vs_enum"]["wdLine"])

	def select_from_selection_end_to_nth_para_end(self, input_no):
		"""
		선택하기 : 현재 선택영역에서 n번째 para 끝까지 선택을 확장

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.expand_selection_to_nth_para_end(input_no)

	def select_from_selection_end_to_nth_word_end(self, input_no):
		"""
		선택하기 : 선택영역 끝 ~ n번째 단어의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		self.expand_selection_to_nth_word_end(input_no)

	def select_from_selection_end_to_one_line_end(self, input_no=1):
		"""
		선택하기 : 현재 선택영역에서 라인의 끝까지 선택을 확장

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.word_application.Selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no,
												 Extend=1)

	def select_from_selection_end_to_previous_nth_char_end(self, input_no):
		"""
		선택하기 : 선택영역 끝 ~ n번째 앞의 단어의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_char_end(input_no * -1)

	def select_from_selection_end_to_previous_nth_line_end(self, input_no):
		"""
		선택하기 : 선택영역 끝 ~ n번째 앞의 라인의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_line_end(input_no * -1)

	def select_from_selection_end_to_previous_nth_para_end(self, input_no):
		"""
		선택하기 : 선택영역 끝에서 n번째 앞의 문단의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_para_end(input_no * -1)

	def select_from_selection_end_to_previous_nth_word_end(self, input_no):
		"""
		선택하기 : 선택영역 끝에서 n번째 앞의 단어의 끝까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_word_end(input_no * -1)

	def select_from_selection_start_to_current_line_end(self):
		"""
		영역선택 : 현재 선택영역의 시작지점을 기준으로 라인의 끝까지 선택
		고쳐야함 : 선택영역에 색을 칠하면 전체 라인이 색칠해 진다

		:return:
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.word_application.Selection.EndOf(5, 1)

	def select_from_selection_start_to_nth_char_end(self, input_no):
		"""
		영역선택 : 현재 선택영역에서 n번째 글자까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.expand_selection_to_nth_char_end(input_no)

	def select_from_selection_start_to_nth_line_end(self, input_no):
		"""
		영역선택 : 선택영역에서 n번째 line까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.expand_selection_to_nth_line_end(input_no)

	def select_from_selection_start_to_nth_para_end(self, input_no):
		"""
		선택하기 : 현재 선택영역에서 n번째 para 끝까지 선택을 확장

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.expand_selection_to_nth_para_end(input_no)

	def select_from_selection_start_to_nth_word_end(self, input_no):
		"""
		선택하기 : 선택영역에서 n번째 word까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.expand_selection_to_nth_word_end(input_no)

	def select_from_selection_start_to_previous_line_start(self):
		"""
		선택하기 : 현재 선택영역에서 라인의 시작점까지 선택, 앞으로 선택하는 것이다

		:return:
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.word_application.Selection.StartOf(5, 1)

	def select_from_selection_start_to_previous_nth_char_start(self, input_no):
		"""
		선택하기 : 선택영역에서 앞으로 n번째 글자까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_char_end(input_no * -1)

	def select_from_selection_start_to_previous_nth_line_start(self, input_no):
		"""
		선택하기 : 선택영역에서 앞으로 n번째 line까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_line_end(input_no * -1)

	def select_from_selection_start_to_previous_nth_para_start(self, input_no):
		"""
		선택하기 : 선택영역에서 앞으로 n번째 para까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_para_end(input_no * -1)

	def select_from_selection_start_to_previous_nth_word_start(self, input_no):
		"""
		선택하기 : 선택영역에서 앞으로 n번째 word까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		input_no = abs(input_no)
		self.expand_selection_to_nth_word_end(input_no * -1)

	def select_from_x_to_len_at_doc_start(self, input_x, char_count):
		"""
		선택하기 : 영역을 선택하는 것
		맨앞에서 몇번째부터，얼마의 길이를 선택할지를 선정

		:param input_x:정수, 문서 맨처음에서 x번째 글자
		:param char_count: 문자 갯수
		:return:
		"""
		self.doc.Range(input_x, input_x + char_count).Select()

	def select_from_x_to_nth_char_end(self, input_x, char_count):
		"""
		선택하기 : 문서 맨처음에서 x번째 글자 ~ n번째 글자의 끝까지 선택

		:param input_x: 정수, 문서 맨처음에서 x번째 글자
		:param char_count: 문자 갯수
		:return:
		"""
		self.selection.Start = min(input_x, input_x + char_count)
		self.selection.End = max(input_x, input_x + char_count)
		return [self.selection.Start, self.selection.End]

	def select_from_x_to_nth_line_end(self, input_x, line_count):
		"""
		선택하기 : 문서 맨처음에서 x번째 글자 ~ n번째 줄의 끝까지 선택

		:param input_x:정수, 문서 맨처음에서 x번째 글자
		:param line_count: 줄 갯수
		:return:
		"""
		[x, y] = self.get_xy_from_x_to_nth_line_end(input_x, line_count)
		self.selection.Start = min(input_x, x, y)
		self.selection.End = max(input_x, x, y)
		return [self.selection.Start, self.selection.End]

	def select_from_x_to_nth_para_end(self, input_x, para_count):
		"""
		선택하기 : 문서 맨처음에서 x번째 글자 ~ n번째 문단의 끝까지 선택

		:param input_x:정수, 문서 맨처음에서 x번째 글자
		:param para_count: 문단 갯수
		:return:
		"""
		[x, y] = self.get_xy_from_x_to_nth_para_end(input_x, para_count)
		self.selection.Start = min(input_x, x, y)
		self.selection.End = max(input_x, x, y)
		return [self.selection.Start, self.selection.End]

	def select_from_x_to_nth_word_end(self, input_x, word_count):
		"""
		선택하기 : 문서 맨처음에서 x번째 글자 ~ n번째 단어의 끝까지 선택

		:param input_x:정수, 문서 맨처음에서 x번째 글자
		:param word_count: 단어 갯수
		:return:
		"""
		[x, y] = self.get_xy_from_x_to_nth_word_end(input_x, word_count)
		self.selection.Start = min(input_x, x, y)
		self.selection.End = max(input_x, x, y)
		return [self.selection.Start, self.selection.End]

	def select_line_at_selection_end(self):
		"""
		선택하기 : 현재 커서가 있는 라인 전체를 선택

		:return:
		"""
		start_line_no_at_cursor = self.selection.Information(10)
		self.select_from_doc_start_to_nth_line_end(start_line_no_at_cursor)
		self.expand_selection_to_nth_line_end(1)
		return self.word_application.Selection.Text

	def select_multi_char_in_line_no(self, line_no, start_no, count_no):
		"""
		선택하기 : 전체 문서에서 몇번째 라인의 앞에서 a~b까지의 글자를 선택하는 것

		:param line_no: 줄번호
		:param start_no: 글자의 시작번호
		:param count_no: 글자의 갯수
		:return:
		"""
		self.selection.GoTo(What=3, Which=line_no, Count=count_no)
		self.selection.Move(Unit=count_no)
		result = self.word_application.Selection.range.Text
		return result

	def select_multi_char_in_para_no(self, para_no, y, length):
		"""
		선택하기 : 문단 번호로 문단 전체의 영역을 선택하는 것
		paragraph 를 선택한다, 없으면 맨처음부터

		:param para_no: 문단 번호
		:param y:
		:param length:
		:return:
		"""
		paragraph = self.doc.Paragraphs(para_no)
		# 맨앞에서 몇번째부터，얼마의 길이를 선택할지를 선정
		x = paragraph.Range.Start + y - 1
		y = paragraph.Range.Start + y + length - 1
		self.varx["new_range"] = self.doc.Range(x, y).Select()

	def select_multi_selection_basic(self, line_no_start=1, line_len=3, letter_type="line"):
		"""
		선택하기 : 전체 문서에서 줄수로 선택하는것

		:param line_no_start: 시작번호
		:param line_len: 줄수
		:param letter_type:
		:return:
		"""

		letter_type_no = self.check_letter_type_no(letter_type)
		# 현재 selction위치를 저장한다
		x = self.selection.Range.Start
		y = self.selection.Range.End

		# 시작점의 위치를 얻어낸다
		self.selection.MoveDown(Unit=letter_type_no, Count=line_no_start)
		self.selection.Expand(letter_type_no)
		x_start = self.selection.Range.Start

		# 원래위치로 이동한다
		self.doc.Range(x, y).Select()
		# 마지막위치로 이동한다
		self.selection.MoveDown(Unit=letter_type_no, Count=line_no_start + line_len)
		self.selection.Expand(letter_type_no)

		y_end = self.selection.Range.End
		self.doc.Range(x_start, y_end).Select()

	def select_next_basic(self, input_type, input_count=1, expand_type=1):
		"""
		선택하기 : 기본적인 형태로 사용이 가능하도록 만든것

		:param input_type:문서의 형태
		:param input_count:갯수
		:param expand_type:확장 방향
		"""
		checked_input_type = self.check_content_name(input_type)
		type_dic = {"line": 5, "paragraph": 4, "word": 2, "sentence": 3, }
		try:
			self.selection.MoveDown(Unit=type_dic[checked_input_type], Count=input_count)
		except:
			self.selection.MoveRight(Unit=type_dic[checked_input_type], Count=input_count)
		self.selection.Expand(expand_type)

	def select_next_basic_at_selection_end(self, input_type, input_count=1, expand_type=1):
		"""
		선택하기 : 기본적인 형태로 사용이 가능하도록 만든것

		:param input_type: 문서의 형태
		:param input_count: 갯수
		:param expand_type: 확장 방향
		"""
		checked_input_type = self.check_content_name(input_type)
		type_dic = {"line": 5, "paragraph": 4, "word": 2, "sentence": 3, }
		try:
			self.selection.MoveDown(Unit=type_dic[checked_input_type], Count=input_count)
		except:
			self.selection.MoveRight(Unit=type_dic[checked_input_type], Count=input_count)
		self.selection.Expand(expand_type)

	def select_nth_cell_in_table(self, table_no):
		"""
		선택하기 : 테이블 번호로 테이블을 선택

		:param table_no: 테이블 번호
		"""
		self.word_application.Tables(table_no).Select()

	def select_nth_char_at_doc_start(self, input_no):
		"""
		선택하기 : 문서의 처음을 기준으로 n번째 word를 선택

		:param input_no: 1번째부터 시작하는 번호
		:return:
		"""
		self.move_cursor_to_doc_start()
		self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no) # wdCharacter 1

	def select_nth_char_at_selection_end(self, input_no):
		"""
		선택 : 선택영역에서 n번째 글자 1개를 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_next_basic_at_selection_end("char", input_no - 1)

	def select_nth_line_at_doc_start(self, input_no):
		"""
		영역선택 : 문서의 처음을 기준으로 n번째 word를 선택

		:param input_no: 1번째부터 시작하는 번호
		:return:
		"""
		self.move_cursor_to_doc_start()

		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no - 1)

		self.select_current_line_at_selection_end()

	def select_nth_line_at_selection_end(self, input_no):
		"""
		선택 : 문서의 처음부터 n번째 line까지 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_next_basic_at_selection_end("line", input_no - 1)

	def select_nth_line_at_selection_start(self, input_no=1):
		"""
		선택하기 : 현재 선택영역에서 라인의 끝까지 선택을 확장

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.selection.Collapse(1) # 0 : end, 1:start
		self.word_application.Selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["line"], Count=input_no,
												 Extend=1)

	def select_nth_para_at_doc_start(self, input_no):
		"""
		영역선택 : 문서의 처음을 기준으로 n번째 para를 선택

		:param input_no: 1번째부터 시작하는 번호
		:return:
		"""
		self.move_cursor_to_doc_start()

		if input_no > 0:
			self.selection.MoveDown(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)
		else:
			self.selection.MoveUp(Unit=self.varx["letter_type_vs_enum"]["para"], Count=input_no)

		self.select_current_para_at_selection_end()

	def select_nth_shape(self, input_no):
		"""
		선택하기 : 번째의 도형을 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		first_shape = self.doc.Shapes(input_no)
		first_shape.Select()

	def select_nth_word(self, input_no, step=0):
		"""
		문서의 처음을 기준으로 n번째 단어 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param step: n번째
		:return:
		"""
		# 정확한 워드수를 계산하는 것
		self.select_from_doc_start_to_nth_word_end(input_no + step)
		aaa = self.information_for_selection()["len_word"]
		if aaa == input_no:
			self.move_cursor_to_selection_end()
			self.select_nth_char_at_doc_start(117)
			start_char_no, end_char_no = self.get_range_for_word_no_at_cursor_end()
			self.select_from_char_no1_to_no2(start_char_no, end_char_no)
		else:
			step = step + input_no - aaa
			self.select_nth_word(input_no, step)

	def select_nth_word_at_doc_start(self, input_no):
		"""
		선택하기 : 영역선택 : 문서의 처음을 기준으로 n번째 para를 선택

		:param input_no: 1번째부터 시작하는 번호
		:return:
		"""
		self.move_cursor_to_doc_start()
		if input_no > 0:
			self.selection.MoveRight(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no - 1)
		else:
			self.selection.MoveLeft(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no - 1)
		self.select_current_word_at_selection_end()

	def select_nth_word_in_doc(self, input_no):
		"""
		단어선택 : n번째 단어 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.select_all()
		self.selection.Words(input_no).Select()
		# 문제는 다음줄로만드는 '\r'이런것들도 1개의 문자로 인식한다는 것이다
		return [self.selection.Start, self.selection.End, self.selection.Text]

	def select_nth_word_in_selection(self, input_no):
		"""
		단어선택 : n번째 단어 선택

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.selection.Words(input_no).Select()
		return [self.selection.Start, self.selection.End, self.selection.Text]

	def select_previous_basic(self, input_type, input_count=1, expand_type=1):
		"""
		선택하기 : 입력형태에 따라서 영역을 선택하는것
		기본적인 형태로 사용이 가능하도록 만든것

		:param input_type: 문서형식
		:param input_count: 갯수
		:param expand_type: 확장 방향
		"""
		checked_input_type = self.check_content_name(input_type)
		type_dic = {"line": 5, "paragraph": 4, "word": 2, "sentence": 3, }
		try:
			self.selection.MoveUp(Unit=type_dic[checked_input_type], Count=input_count)
		except:
			self.selection.MoveLeft(Unit=type_dic[checked_input_type], Count=input_count)
		self.selection.Expand(expand_type)

	def select_range(self):
		"""
		선택하기 : range 객체의 일정부분을 영역으로 선택
		"""
		self.selection = self.doc.Range(0, 0)

	def select_shape_by_no(self, input_no):
		"""
		도형을 번호로 선택하기

		:param input_no: 도형번호
		:return:
		"""
		shape_obj = self.doc.Shapes(input_no)
		shape_obj.Select()
		return shape_obj

	def select_table_by_index(self, table_index):
		"""
		선택하기 : 테이블 번호로 테이블을 선택

		:param table_index: 테이블 번호 (index)
		"""
		self.word_application.Tables(table_index).Select()

	def select_xy(self, start_no, end_no):
		"""
		선택하기 : 문서의 처음에서 x번째 부터 y번째까지의 글자를 선택

		:param start_no: 시작 문자 번호 (문서 처음에서 부터)
		:param end_no: 끝 문자 번호 (문서 처음에서 부터)
		:return:
		"""
		self.selection.Start = start_no
		self.selection.End = end_no
		self.selection.Select()


	def select_xy_from_doc_start(self, start_no, end_no):
		"""
		선택하기 : 문서의 처음에서 x번째 부터 y번째까지의 글자를 선택

		:param start_no: 시작 문자 번호 (문서 처음에서 부터)
		:param end_no: 끝 문자 번호 (문서 처음에서 부터)
		:return:
		"""
		self.selection.Start = start_no
		self.selection.End = end_no
		self.selection.Select()

	def select_xy_cell_in_table(self, table_no, table_xy_no):
		"""
		선택하기 : 테이블의 xy번호로 셀을 선택하는것

		:param table_no:테이블 번호
		:param table_xy_no: 테이블의 셀번호(가로, 세로 번호)
		"""
		table = self.doc.Tables(table_no)
		# table_x_no = table.Rows.Count
		table_y_no = table.Columns.Count
		x = table_xy_no[0]
		y = table_xy_no[1]
		mok, namuji = divmod(y, table_y_no)
		if namuji == 0 and mok > 0:
			mok = mok - 1
			namuji = table_y_no
		if mok > 0:
			x = x + mok
			y = namuji
		range = table.Cell(x, y).Range
		range.Select()

	def set_active_doc(self):
		"""
		설정하기 : 현재 활성화된 문서를 기본 문서로 설정
		"""
		self.doc = self.word_application.ActiveDocument

	def set_alingment_to_middle_for_selection(self):
		"""
		현재 선택한 영역의 그림을 중간에 맞추고 외곽선을 그리는 것
		:return:
		"""
		self.selection.ParagraphFormat.Alignment = 1 #wdAlignParagraphCenter
		self.selection.Borders.OutsideColor = 0 #wdColorBlack
		self.selection.Borders.OutsideLineStyle = 1 #wdLineStyleSingle
		self.selection.Borders.OutsideLineWidth = 6 #wdLineWidth075pt

	def set_basic_height_for_table(self, input_table_obj, input_height=10):
		"""
		설정하기 : 테이블객체의 높이를 설정

		:param input_table_obj:테이블 객제
		:param input_height: 높이
		:return:
		"""
		# input_table_obj.Rows.SetHeight(RowHeight := InchesToPoints(0.5), HeightRule := wdRowHeightExactly)
		input_table_obj.Rows.Height = input_height

	def set_bookmark_at_range(self, input_range, bookmark_name):
		"""
		설정하기 : 북마크를 영역으로 설정

		:param input_range: range객체
		:param bookmark_name: 북마크 이름
		"""
		input_range.Bookmarks.Add(Name=bookmark_name)

	def set_bookmark_by_xy(self, xy, bookmark_name):
		"""
		설정하기 : 북마크를 이름으로 설정

		:param xy: 문서의 x번째부터 y번째까지의 글자
		:param bookmark_name: 북마크 이름
		"""
		my_range = self.new_range_by_xy(xy)
		my_range.Bookmarks.Add(Name=bookmark_name)

	def set_font_align_for_selection(self, input_value):
		"""
		설정하기 : 선택영역의 글자 정렬을 선택

		:param input_value: 입력값
		:return:
		"""
		self.selection.ParagraphFormat.Alignment = self.varx["check_alignment"][input_value]

	def set_font_bold_for_selection(self):
		"""
		설정하기 : 선택영역의 글자를 굵게적용
		:return:
		"""
		self.selection.Font.Bold = True

	def set_font_borderline_all_for_selection(self, input_range="", input_font_style="", input_font_size="", input_font_color=""):
		"""
		설정하기 : 글자의 외곽선 설정 : 선택영역의 모든방향의 라인을 설정

		:param input_range: range객체
		:param input_font_style: 폰트 스타일
		:param input_font_size: 폰트 사이즈
		:param input_font_color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		for num in [-1, -2, -3, -4]:
			if input_font_style != "": input_range.Font.Borders(num).LineStyle = input_font_style # wdLineStyleDouble 7.
			if input_font_size != "": input_range.Font.Borders(num).Lineidth = input_font_size # wdLineWidth075pt
			if input_font_color != "": input_range.Font.Borders(num).ColorIndex = input_font_color # 7 :yellow

	def set_font_borderline_bottom_for_selection(self, input_range="", input_font_style="", input_font_size="", input_font_color=""):
		"""
		설정하기 : 글자의 외곽선 설정 : 선택영역의 아래쪽 라인을 설정

		:param input_range: range객체
		:param input_font_style: 폰트 스타일
		:param input_font_size: 폰트 사이즈
		:param input_font_color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		if input_font_style != "": input_range.Font.Borders(-3).LineStyle = input_font_style # wdLineStyleDouble 7
		if input_font_size != "": input_range.Font.Borders(-3).LineWidth = input_font_size # wdLineWidth075pt 6
		if input_font_color != "": input_range.Font.Borders(-3).ColorIndex = input_font_color # 7 :yellow

	def set_font_borderline_left_for_selection(self, input_range="", input_font_style="", input_font_size="", input_font_color=""):
		"""
		설정하기 : 글자의 외곽선 설정 : 선택영역의 왼쪽끝 라인을 설정

		:param input_range: range객체
		:param input_font_style: 폰트 스타일
		:param input_font_size: 폰트 사이즈
		:param input_font_color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		if input_font_style != "": input_range.Font.Borders(-2).LineStyle = input_font_style
		if input_font_size != "": input_range.Font.Borders(-2).LineWidth = input_font_size
		if input_font_color != "": input_range.Font.Borders(-2).ColorIndex = input_font_color

	def set_font_borderline_right_for_selection(self, input_range="", input_font_style="", input_font_size="", input_font_color=""):
		"""
		설정하기 : 글자의 외곽선 설정 : 선택영역의 오른쪽끝 라인을 설정

		:param input_range: range객체
		:param input_font_style: 폰트 스타일
		:param input_font_size: 폰트 사이즈
		:param input_font_color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		if input_font_style != "": input_range.Font.Borders(-4).LineStyle = input_font_style
		if input_font_size != "": input_range.Font.Borders(-4).LineWidth = input_font_size
		if input_font_color != "": input_range.Font.Borders(-4).ColorIndex = input_font_color

	def set_font_borderline_top_for_selection(self, input_range="", input_font_style="", input_font_size="", input_font_color=""):
		"""
		설정하기 : 글자의 외곽선 설정 : 선택영역의 제일 윗부분의 라인을 설정

		:param input_range: range객체
		:param input_font_style: 폰트 스타일
		:param input_font_size: 폰트 사이즈
		:param input_font_color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		if input_font_style != "": input_range.Font.Borders(-1).LineStyle = input_font_style
		if input_font_size != "": input_range.Font.Borders(-1).LineWidth = input_font_size
		if input_font_color != "": input_range.Font.Borders(-1).ColorIndex = input_font_color

	def set_font_color_for_selection(self, input_xcolor):
		"""
		설정하기 : 선택한 영역의 폰트색을 설정
		:param input_xcolor: xcolor스타일의 색이름
		:return:
		"""
		rgbint = self.colorx.change_xcolor_to_rgbint(input_xcolor)
		self.selection.Font.Color = rgbint

	def set_font_default(self, *input_list):
		"""

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		self.font_dic_default = {}
		check_bold = self.varx["check_bold"]
		check_italic = self.varx["check_italic"]
		check_underline = self.varx["check_underline"]
		check_breakthrough = self.varx["check_breakthrough"]
		check_alignment = self.varx["check_alignment"]
		for one in input_list[1:]:
			if one in check_bold.keys():
				self.font_dic_default["bold"] = True
			elif one in check_italic.keys():
				self.font_dic_default["italic"] = True
			elif one in check_underline.keys():
				self.font_dic_default["underline"] = True
			elif one in check_breakthrough.keys():
				self.font_dic_default["strikethrough"] = True
			elif one in check_alignment.keys():
				self.font_dic_default["align"] = self.varx["check_alignment"][one]
			elif type(one) == type(123) and one < 100:
				self.font_dic_default["size"] = one
			elif self.is_xcolor_style(one):
				self.font_dic_default["color"] = self.colorx.change_xcolor_to_rgbint(one)
		return self.font_dic_default

	def set_font_default_for_selection(self):
		"""
		설정하기 : 기본설정된 font로 적용하는것
		"""
		self.font_dic["bold"] = False
		self.font_dic["italic"] = False
		self.font_dic["underline"] = False
		self.font_dic["strikethrough"] = False
		self.font_dic["size"] = 11
		self.font_dic["color"] = 197379
		self.font_dic["align"] = 0

		self.selection.Font.Size = self.font_dic["size"]
		self.selection.Font.Bold = self.font_dic["bold"]
		self.selection.Font.Italic = self.font_dic["italic"]
		self.selection.Font.Underline = 0
		self.selection.Font.StrikeThrough = self.font_dic["strikethrough"]
		self.selection.Font.TextColor.RGB = self.font_dic["color"]
		self.selection.ParagraphFormat.Alignment = self.font_dic["align"]

	def set_font_in_range_with_options(self, range_obj="", input_list=[]):
		"""
		설정하기 : range객체에 대해서 글자의 폰트를 설정하는 것

		:param range_obj: range 객체
		:param input_list: 리스트형태의 입력값
		:return:
		"""
		if range_obj == "":
			range_obj = self.selection

		self.setup_font_default() # 기본으로 만든다
		if input_list:
			# 아무것도 없으면, 기존의 값을 사용하고, 있으면 새로이 만든다
			if type(input_list) == type([]):
				self.setup_font(input_list)
			elif type(input_list) == type({}):
				# 만약 사전 형식이면, 기존에 저장된 자료로 생각하고 update한다
				self.varx["font_option"].update(input_list)

		range_obj.Font.Size = self.varx["font_option"]["size"]
		range_obj.Font.Bold = self.varx["font_option"]["bold"]
		range_obj.Font.Italic = self.varx["font_option"]["italic"]
		range_obj.Font.Name = self.varx["font_option"]["name"]

		range_obj.Font.Strikethrough = self.varx["font_option"]["strikethrough"]
		range_obj.Font.Subscript = self.varx["font_option"]["subscript"]
		range_obj.Font.Superscript = self.varx["font_option"]["superscript"]
		range_obj.Font.Underline = self.varx["font_option"]["underline"]
		rgbint = self.colorx.change_xcolor_to_rgbint(self.varx["font_option"]["color"])
		range_obj.Font.Color = rgbint

	def set_font_italic_for_selection(self):
		"""
		설정하기 : 선택영역의 이태릭체를 적용
		:return:
		"""
		self.selection.Font.Italic = True

	def set_font_name_for_selection(self, input_font_name):
		"""
		설정하기 : 선택영역에 폰트명 적용하기

		:param input_font_name: 폰트이름
		:return:
		"""
		self.selection.Font.Name = input_font_name

	def set_font_name_for_table(self, table_index, input_font_name="Georgia"):
		"""
		설정하기 : 테이블의 폰트이름을 설정

		:param input_font_name: 폰트이름
		"""
		self.word_application.table(table_index).Font.Name = input_font_name

	def set_font_name_in_table_at_nth_cell(self, table_index, cell_index, input_font_name="Georgia"):
		"""
		설정하기 : 테이블의 xy의 폰트를 설정

		:param table_index: 테이블 번호 (index)
		:param cell_index: 앞에서 n번째의 셀 (index)
		:param input_font_name: 폰트이름
		"""
		table = self.word_application.Tables(table_index)
		table(cell_index).Font.Name = input_font_name

	def set_font_name_in_table_at_xy_cell(self, table_index, cell_index, input_font_name="Georgia"):
		"""
		설정하기 : 테이블의 xy의 폰트를 설정

		:param table_index: 테이블 번호 (index)
		:param cell_index: 앞에서 n번째의 셀 (index)
		:param input_font_name: 폰트이름
		"""
		table = self.word_application.Tables(table_index)
		table(cell_index).Font.Name = input_font_name

	def set_font_options_for_reuse(self, *input_list):
		"""

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		self.check_font_style(self, input_list)

	def set_font_options_for_selection(self, input_list):
		"""
		설정하기 : 폰트의 옵션을 선택

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		self.run_font_style(input_list)

	def set_font_size_down_for_selection(self):
		"""
		설정하기 : 선택한것의 폰트사이즈를 한단계 내리기
		"""
		self.selection.Font.Shrink()

	def set_font_size_for_selection(self, input_font_size):
		"""
		설정하기 : 폰트크기 설정

		:param input_font_size: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.selection.Font.Size = input_font_size

	def set_font_size_for_table(self, table_index, input_font_size=10):
		"""
		설정하기 : 표에 대한 글자크기를 설정

		:param table_index: 테이블 번호 (index)
		:param input_font_size: 숫자(정수, 1부터 시작하는 숫자)
		"""
		table = self.doc.Tables(table_index)
		table.Font.Size = input_font_size

	def set_font_size_up_for_range(self, input_range_obj=""):
		"""
		설정하기 : 선택한것의 폰트를 한단계 올린다

		:param input_range_obj: range객체
		:return:
		"""
		range_obj = self.check_range_obj(input_range_obj)
		range_obj.Font.Grow()

	def set_font_strikethrough_for_selection(self):
		"""
		설정하기 : 취소선 적용하기

		:return:
		"""
		self.selection.Font.StrikeThrough = True

	def set_font_style(self, *input_list):
		"""
		설정하기 : 폰트의 옵션들을 설정한다

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		self.check_font_style(self, input_list)

	def set_font_style_for_selection(self, input_range="", color=""):
		"""
		설정하기 : 선택한 영역에 언더라인을 적용

		:param input_range: range객체
		:param color: 폰트 색
		:return:
		"""
		if input_range == "": input_range = self.selection
		input_range.Font.UnderlineColor = color
		self.selection.Font.StrikeThrough = True

		self.selection.Font.Underline = 1 # wdUnderlineSingle = 1, A single line

	def set_font_underline_for_selection(self):
		"""
		설정하기 : 선택영역의 밑줄 긋기
		:return:
		"""
		self.selection.Font.Underline = True

	def set_font_with_all_options(self, xcolor_i="", size_i="", bold_tf=False, italic_tf=False, underline_tf=False,
								 strike_tf=False, align_lmr="", bakground_xcolor="", name_i=""):
		"""
		폰트에 대한 모든 옵션으로 사전형식으로 만드는 것

		:param xcolor_i:
		:param size_i:
		:param bold_tf:
		:param italic_tf:
		:param underline_tf:
		:param strike_tf:
		:param align_lmr:
		:param bakground_xcolor:
		:param name_i:
		:return:
		"""
		if xcolor_i: self.selection.Font.TextColor.RGB = self.colorx.change_xcolor_to_rgbint(xcolor_i)
		if size_i: self.selection.Font.Size = size_i
		if bold_tf: self.selection.Font.Bold = bold_tf
		if italic_tf: self.selection.Font.Italic = italic_tf
		if underline_tf: self.selection.Font.Underline = underline_tf
		if strike_tf: self.selection.Font.StrikeThrough = strike_tf
		if align_lmr: self.selection.ParagraphFormat.Alignment = self.varx["check_alignment"][align_lmr]
		if bakground_xcolor:
			rgb_int = self.colorx.change_xcolor_to_rgbint(bakground_xcolor)
			self.selection.Range.Shading.BackgroundPatternColor = rgb_int
		if name_i:
			self.selection.Font.Name = name_i

	def set_footer(self):
		"""
		설정하기 : 문서의 footer를 삽입
		"""
		for section in self.doc.Sections:
			# header를 하나씩 설정할수는 없다
			section.Headers(1).PageNumbers.Add(PageNumberAlignment=2, FirstPage=True)
			section.Headers(1).PageNumbers.ShowFirstPageNumber = True
			section.Headers(1).PageNumbers.RestartNumberingAtSection = True
			section.Headers(1).PageNumbers.StartingNumber = 1

	def set_header(self):
		"""
		설정하기 : 문서의 헤더를 삽입
		"""
		for section in self.doc.Sections:
			# header를 하나씩 설정할수는 없다
			section.Headers(1).PageNumbers.Add(PageNumberAlignment=2, FirstPage=True)
			section.Headers(1).PageNumbers.ShowFirstPageNumber = True
			section.Headers(1).PageNumbers.RestartNumberingAtSection = True
			section.Headers(1).PageNumbers.StartingNumber = 1

	def set_height_for_table(self, input_table_obj, input_height=10):
		"""
		테이블의 높이를 설정합니다

		:param input_table_obj: 테이블 객제
		:param input_height: 높이 숫자
		:return:
		"""
		# input_table_obj.Rows.SetHeight(RowHeight := InchesToPoints(0.5), HeightRule := wdRowHeightExactly)
		input_table_obj.Rows.Height = input_height

	def set_line_width_for_table(self, input_table_obj, inside_width="", outside_width=""):
		"""
		설정하기 : 테이블의 선두께

		:param input_table_obj: 테이블 객제
		:param inside_width: 안쪽 테이블의 선두께
		:param outside_width: 바깥쪽 테이블의 선두께
		"""
		input_table_obj.Borders.InsideLineWidth = self.varx["linewidth_vs_enum"][inside_width]
		input_table_obj.Borders.OutsideLineWidth = self.varx["linewidth_vs_enum"][outside_width]

	def set_list_format_for_selection(self):
		"""
		설정하기 : 글머리기호 만들기

		:return:
		"""
		self.selection.ListFormat.ApplyBulletDefault()

	def set_margin_bottom_for_doc(self, input_no=20):
		"""
		설정하기 : 페이지의 아래 마진을 설정

		:param input_no: 입력 숫자
		"""
		self.doc.PageSetup.BottomMargin = input_no

	def set_margin_left_for_doc(self, input_no=20):
		"""
		페이지셋업 : 왼쪽 띄우기
		:param input_no: 입력 숫자
		"""
		self.doc.PageSetup.LeftMargin = input_no

	def set_margin_right_for_doc(self, input_no=20):
		"""
		페이지셋업 : 오른쪽 띄우기
		:param input_no: 입력 숫자
		"""
		self.doc.PageSetup.RightMargin = input_no

	def set_margin_top_for_doc(self, input_no=20):
		"""
		페이지셋업 : 위쪽 띄우기
		:param input_no: 입력 숫자
		"""
		self.doc.PageSetup.TopMargin = input_no

	def set_options_for_selected_shape(self, pxy_list=None, size_whlist=None, transparency_0_1=None,
									 rotation_degree=None):
		"""
		설정하기 : 선택한 도형의 설정을 변경하는 것
		:param pxy_list:
		:param size_whlist:
		:param transparency_0_1:
		:param rotation_degree:
		:return:
		"""
		img = self.selection.InlineShapes(1)

		shape = img.ConvertToShape()
		if rotation_degree:
			shape.Rotation = rotation_degree
		if not size_whlist:
			shape.Width = size_whlist[0]
			shape.Height = size_whlist[1]
		if not pxy_list:
			shape.Left = pxy_list[0]
			shape.Top = pxy_list[1]
		if transparency_0_1:
			shape.Fill.Transparency = transparency_0_1

	def set_orientation_for_doc(self, input_no=20):
		"""
		설정하기 : 페이지의 회전을 설정

		:param input_no: 입력값
		"""
		self.doc.PageSetup.Orientation = input_no

	def set_page_no_at_header(self, left_text="", right_start_no=1):
		"""
		설정하기 : 헤더부분에 페이지번호 넣기

		:param left_text:
		:param right_start_no:
		"""
		self.doc.Sections(1).Headers(1).Range.Text = left_text
		self.doc.Sections(1).Headers(1).PageNumbers.StartingNumber = right_start_no
		self.doc.Sections(1).Headers(1).PageNumbers.Add(True)

	def set_password(self, input_text):
		"""
		설정하기 : 암호설정

		:param input_text: 입력 문자
		"""
		self.doc.Password = input_text

	def set_range_by_xy(self, x, y):
		"""
		range영역을 설정 : 문서처음에서 x번째에서 y번째까지 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""

		my_range = self.doc.Range(x, y)
		return my_range

	def set_range_from_doc_start_to_char_end(self, input_no):
		"""
		range영역을 설정 : 문서처음에서 n번째 글자까지의 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		self.range = self.doc.Range(0, 0)
		self.range.Move(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		new_y = self.range.End
		self.range = self.doc.Range(0, new_y)
		return self.range

	def set_range_from_doc_start_to_nth_char_end(self, input_no=1):
		"""
		range영역을 설정 : 문서처음에서 n번째 글자까지의 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""

		self.range = self.doc.Range(0, 0)
		self.range.Move(Unit=self.varx["letter_type_vs_enum"]["char"], Count=input_no)
		new_y = self.range.End
		self.range = self.doc.Range(0, new_y)
		return self.range

	def set_range_from_doc_start_to_nth_letter_type_end(self, letter_type, input_no=1):
		"""
		range영역을 설정 : 문서처음에서 n번째 글자형식까지 range를 설정

		movedown이 되는 것
		"cell" = 12, "character" = 1, "char" = 1, "column" = 9
		"item" = 16, "line" = 5, "paragraph" = 4, "para" = 4
		"row" = 10, "section" = 8, "sentence" = 3, "story" = 6
		"table" = 15, "word" = 2

		:param letter_type: 문서형태
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		letter_type_no = self.check_letter_type_no(letter_type)
		self.range = self.doc.Range(0, 0)

		if letter_type_no in [1, 2]:
			self.range.Move(Unit=letter_type_no, Count=input_no + 1)
		else:
			self.range.MoveEnd(Unit=letter_type_no, Count=input_no + 1)

		y = self.range.End
		self.range = self.doc.Range(0, y)

	def set_range_from_doc_start_to_nth_line_end(self, input_no):
		"""
		range영역을 설정 : 문서처음에서 n번째 line까지의 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		new_range = self.select_from_doc_start_to_nth_letter_type_end("line", input_no)
		return new_range

	def set_range_from_doc_start_to_nth_para_end(self, input_no):
		"""
		range영역을 설정 : 문서처음에서 n번째 para까지의 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		"""
		new_range = self.set_range_from_doc_start_to_nth_letter_type_end("para", input_no)
		return new_range

	def set_range_from_doc_start_to_nth_word_end(self, input_no):
		"""
		range영역을 설정 : 문서처음에서 n번째 단어까지의 range를 설정

		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		self.range = self.doc.Range(0, 0)
		self.range.Move(Unit=self.varx["letter_type_vs_enum"]["word"], Count=input_no + 1)
		new_y = self.range.End
		self.range = self.doc.Range(0, new_y)
		return self.range

	def set_range_from_letter_type_no1_to_letter_type_no2(self, start_no, end_no):
		"""
		설정하기 :

		:param start_no: 레터타입에따른 시작 번호
		:param end_no: 레터타입에따른 끝 번호
		:return:
		"""
		my_range = self.doc.Range(start_no > end_no)
		return my_range

	def set_range_from_x_to_y(self, input_x, input_y):
		"""
		설정하기 : 글자의 맨앞부터의 숫자로 range객체의 영역을 설정

		:param input_x: 문서의 맨앞에서부터 x번째 문자의 뜻
		:param input_y: 문서의 맨앞에서부터 y번째 문자의 뜻
		"""
		self.range = self.doc.Range(input_x, input_y)
		return self.range

	def set_range_start_from_selection_start(self, letter_type, input_no=1):
		"""
		설정하기 : 선택영역의 첫커서부분을 range객체의 시작점으로 만드는 것

		:param letter_type: 글자의 형태 (글자, 단어, 문단 등)
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:return:
		"""
		a = self.selection.Start
		my_range = self.doc.Range(a, a)
		self.expand_range_to_nth_letter_type_end(my_range, letter_type, input_no)

	def set_screenupdate_off(self):
		"""
		screenupdate off
		:return:
		"""
		self.word_application.screenUpdating = False

	def set_screenupdate_on(self):
		"""
		screenupdate on
		:return:
		"""
		self.word_application.ScreenUpdating = True

	def set_space_size_for_selection(self, input_range="", input_value=1.5):
		"""
		설정하기 : 선택영역의 space의 사이즈를 설정하는 것

		:param input_range: range객체
		:param input_value: 입력값
		:return:
		"""
		if input_range == "": input_range = self.selection
		input_range.Font.Spacing = input_value

	def set_style_for_selection(self, style_name="표준"):
		"""
		설정하기 : 선택한 영역의 글씨 스타일을 변경한다

		:param style_name: 스타일 이름
		"""
		self.selection.Style = self.doc.Styles(style_name)

	def setup_font(self, input_list):
		"""
		기존적인 폰트의 설정
		["진하게", 12, "red50", "밑줄"] 이런형식으로 들어오면 알아서 값이 되는 것이다

		:param input_list: 리스트형태의 입력값
		:return:
		"""
		if self.varx["font_option"]:
			# 하위값이 있으면, 기존의것을 사용하고, 아무것도 없으면 기본값으로 설정한다
			pass
		else:
			self.setup_font_default()

		for one in input_list:
			if type(one) == type(123):
				self.varx["font_option"]["size"] = one
			elif one in ["진하게", "굵게", "찐하게", "bold"]:
				self.varx["font_option"]["bold"] = True
			elif one in ["italic", "이태리", "이태리체", "기울기"]:
				self.varx["font_option"]["italic"] = True
			elif one in ["strikethrough", "취소선", "통과선", "strike"]:
				self.varx["font_option"]["strikethrough"] = True
			elif one in ["subscript", "하위첨자", "밑첨자"]:
				self.varx["font_option"]["subscript"] = True
			elif one in ["superscript", "위첨자", "웃첨자"]:
				self.varx["font_option"]["superscript"] = True
			elif one in ["underline", "밑줄"]:
				self.varx["font_option"]["underline"] = True
			elif one in ["vertical", "수직", "가운데"]:
				self.varx["font_option"]["align_v"] = 3
			elif one in ["horizental", "수평", "중간"]:
				self.varx["font_option"]["align_h"] = 2
			elif one in self.colorx.varx["check_color_name"].keys():
				self.varx["font_option"]["color"] = one
			else:
				self.varx["font_option"]["name"] = one

		result = copy.deepcopy(self.varx["font_option"])
		return result

	def setup_font_default(self):
		"""
		기본자료를 만든다
		기본값을 만들고, 다음에 이것을 실행하면 다시 기본값으로 돌아온다
		"""

		self.varx["font_option"]["bold"] = False
		self.varx["font_option"]["color"] = "bla"
		self.varx["font_option"]["italic"] = False
		self.varx["font_option"]["name"] = "Arial"
		self.varx["font_option"]["size"] = 12
		self.varx["font_option"]["strikethrough"] = False
		self.varx["font_option"]["subscript"] = False
		self.varx["font_option"]["superscript"] = False
		self.varx["font_option"]["alpha"] = False # tintandshade를 이해하기 쉽게 사용하는 목적
		self.varx["font_option"]["underline"] = False
		self.varx["font_option"]["align_v"] = 3 # middle =3, top = 1, bottom = 4, default=2
		self.varx["font_option"]["align_h"] = 1 # None =1, center=2, left=1, default=1
		self.varx["font_option"]["color"] = 1

	def split_all_doc_by_style_name_as_l2d(self):
		"""
		분리하기 : 전체 문서를 스타일이 다른것을 기준으로 분리하는 것
		"""
		result = []
		story_all = []

		start = ""
		style_name = ""
		title = ""
		for para in self.doc.Paragraphs:
			story_or_title = para.Range.Text
			style = para.Style.NameLocal

			if style == "표준":
				story_all.append(story_or_title)
			else:
				if start == "":
					if story_all == []:
						story_all = [[]]
					result.append(["무제", "제목", story_all])
					story_all = []
					start = "no"
					style_name = style
					title = story_or_title
				else:
					result.append([title, style_name, story_all])
					style_name = style
					title = story_or_title
					start = "no"
					story_all = []

		return result

	def split_line_text_by_special_char_for_selection(self, input_char=":"):
		"""
		현재 선택한 영역의 값을 읽어온다
		읽어온 값을 어떤 문자를 기준으로 분리한후, 선택자료를 삭제한다

		:param input_char: 입력 문자
		:return:
		"""
		result = []
		l1d =self.read_text_for_selection()
		for ix, one_text in enumerate(l1d):
			split_text = one_text.split(input_char, 1)
			if len(split_text) ==2:
				result.append(split_text)
			else:
				result.append(["", one_text])
		return result

	def unmerge_for_table(self, input_table_obj):
		"""
		워드는 unmerge가 없으며, 셀분할로 만들어야 한다

		:param input_table_obj: 테이블 객제
		"""
		count_y = input_table_obj.Columns.Count
		count_x = input_table_obj.Rows.Count

	def write_l1d_from_selection_start_with_new_line(self, input_l1d):
		"""
		1차원의 자료를 역으로해서 써야 제대로 써진다

		:param input_l1d:1차원 리스트
		:return:
		"""
		input_l1d.reverse()
		for one_value in input_l1d:
			self.selection.InsertBefore(one_value + "\r")

	def write_l2d_with_new_table(self, input_l2d):
		"""
		새로운테이블에 2차원리스트 자료를 써넣는 것

		:param input_l2d: 2차원 리스트
		:return:
		"""
		table1 = self.new_table_with_black_line(len(input_l2d), len(input_l2d[0]))
		for ix, l1d in enumerate(input_l2d):
			for iy, one_value in enumerate(l1d):
				self.write_text_in_table_at_xy_cell(table1,[ix+1, iy+1], str(input_l2d[ix][iy]).strip())

	def write_l1d_with_new_table(self, input_l1d, yline_no = 2):
		"""
		새로운테이블에 1차원리스트 자료를 써넣는 것

		:param input_l1d:1차원 리스트
		:param yline_no: y라인 번호
		:return:
		"""
		table1 = self.new_table_with_black_line(len(input_l1d), yline_no)
		for ix, l1d in enumerate(input_l1d):
				self.write_text_in_table_at_xy_cell(table1,[ix+1, 1], str(input_l1d[ix]).strip())

	def write_left_middle_right_in_all_header(self, left_text="", middle_text="", right_text=""):
		"""
		해더의 왼쪽, 중간, 오른쪽에 글쓰기

		:param left_text: 왼쪽에 들어갈 문자
		:param middle_text: 중간에 들어갈 문자
		:param right_text: 오른쪽에 들어갈 문자
		:return:
		"""
		# 모든 섹션을 순회 no =1
		for section in self.doc.Sections:
			# 각 섹션의 기본 헤더 가져오기
			header = section.Headers(1)
			header_range = header.Range
			header_range.Collapse(0)
			header_range.ParagraphFormat.Alignment = 0
			header_range.Text = "작성자: 홍길동" # 작성자 이름을 필요에 따라 변경하세요
			header_range.Collapse(0) # 헤더의 중간에 오늘 날짜 삽입
			header_range.InsertAfter("₩t") # 탭을 추가하여 중간으로 이동
			header_range.Collapse(0) # header_range.ParagraphFormat Alignment
			header_range.Text = "오늘 날짜: "
			header_range.Collapse(0)
			date_field_code = 'DATE ₩₩@ "yyyy 년 MM 월 dd 일"'
			header_range.Fields.Add(header_range, -1, date_field_code)
			# time.sleep(0.5)
			# #header_range.Collapse(0)
			# 헤더의 오른쪽에 파일 제목 삽입
			header_range.InsertAfter("₩t") # 탭을 추가하여 오른쪽으로 이동
			header_range.Colapse(0)
			header_range.ParagraphFormat.Alignment = 1

	def write_l2d_with_new_table(self, input_l2d):
		"""
		글쓰기 : 2차원 자료를 알아서 테이블만들어서 넣기

		:param input_l2d: 2차원 리스트
		:return:
		"""
		x_len = len(input_l2d)
		y_len = len(input_l2d[0])
		table_obj = self.new_table_with_black_line(x_len, y_len)
		for x in range(1, x_len + 1):
			for y in range(1, y_len + 1):
				table_obj.Cell(Row=x, Column=y).Range.Text = input_l2d[x - 1][y - 1]

	def write_l2d_with_style(self, input_l2d):
		"""
		글쓰기 : [['050630', '제목', '내용']] ==> [제목, 제목의 스타일이름, 내용]
		위와같은 형태의 자료를 새로운 워드를 오픈해서 작성하는것

		:param input_l2d: 2차원 리스트
		"""
		total_len = len(input_l2d)
		for index, l1d in enumerate(input_l2d):
			title = str(l1d[0]).strip()
			style_name = str(l1d[1])
			text_data_old = l1d[2]
			text_data = ""

			for index, one in enumerate(text_data_old):
				text_data = text_data + one

			# 스타일이 있는 제목 부분을 나타내는 코드
			cursor = self.doc.Characters.Count # 워드의 가장 뒷쪽으로 커서위치를 설정
			self.selection.Start = cursor
			self.selection.End = cursor + len(title)
			self.selection.InsertAfter(title)
			self.selection.Style = self.doc.Styles(style_name) # 스타일 지정하는 코드

			# 스타일이 없는 부분을 표준으로 설정해서 나타내는 코드
			self.selection.InsertAfter("\r\n")
			cursor = self.doc.Characters.Count # 커서의 현재위치 확인
			self.selection.Start = cursor
			self.selection.InsertAfter(text_data)
			self.selection.End = cursor + len(text_data)
			self.selection.Style = self.doc.Styles("표준") # 스타일 지정하는 코드
			self.selection.InsertAfter("\r\n")

	def write_splited_selection_text_by_char_in_new_table(self, input_char=":"):
		"""
		현재 선택한 영역의 값을 읽어온다
		읽어온 값을 어떤 문자를 기준으로 분리한후, 선택자료를 삭제한다
		갯수에 맞는 table 을 만든뒤,분리한 자료를 테이블에 쓴다

		:param input_char: 입력문자
		:return:
		"""
		l1d =self.read_text_for_selection()
		self.delete_selection()
		table1 = self.new_table_with_black_line(len(l1d), 2)
		for ix, one_text in enumerate(l1d):
			split_text = one_text.split(input_char, 1)
			if len(split_text) ==2:
				self.write_text_in_table_at_xy_cell(table1,[ix+1, 1], split_text[0])
				self.write_text_in_table_at_xy_cell(table1,[ix+1, 2], split_text[1])
			else:
				self.write_text_in_table_at_xy_cell(table1,[ix+1, 2], one_text)

	def write_text(self, input_text):
		"""
		글쓰기 : 커서의 시작위치에 글을 쓰기

		:param input_text: 입력글자
		:return:
		"""
		self.write_text_at_selection_end(input_text)
		self.selection.Collapse(0) # 0 : end, 1:start

	def change_all_para_to_l1d(self):
		"""
		글쓰기 : 모든 paragraph를 리스트로 만들어서 돌려주는 것
		"""
		result = []
		para_nums = self.doc.Paragraphs.Count
		for no in range(1, para_nums + 1):
			result.append(self.doc.Paragraphs(no).Range.Text)
		return result

	def write_text_at_doc_end(self, input_text):
		"""
		글쓰기 : 문서의 제일 뒷부분에 글을 넣는것

		:param input_text: 입력 문자
		:return:
		"""
		self.doc.Content.InsertAfter(input_text)

	def write_text_at_doc_end_with_font_style(self, input_text, style_name):
		"""
		글쓰기 : 문서의 맨 뒷부분에 글을쓰고 스타일을 적용하는 것

		:param input_text: 입력글자
		:param style_name: 스타일 이름
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		self.doc.Content.InsertAfter(input_text + "\r\n")
		self.selection.Start = self.selection.Range.Start
		self.selection.End = self.selection.Start + len(input_text)
		self.selection.Style = self.doc.Styles(style_name) # 스타일 지정하는 코드

	def write_text_at_doc_end_with_new_line(self, input_text):
		"""
		글쓰기 : 문서의 맨 뒷부분에 글을쓰고 다음줄로 만드는 것

		:param input_text: 입력글자
		"""
		self.doc.Content.InsertAfter(input_text + "\r\n")

	def write_text_at_doc_start(self, input_text):
		"""
		글쓰기 : 문서의 제일 앞부분에 글을 넣는것

		:param input_text: 입력글자
		"""
		self.move_cursor_to_doc_start()
		self.write_text_at_selection_start(input_text)

	def write_text_at_selection_end(self, input_value):
		"""
		글쓰기 : 선택한것의 뒤에 글씨넣기

		:param input_value: 입력값
		:return:
		"""
		self.selection.InsertAfter(input_value)

	def write_text_at_nth_line_start(self, input_no, input_text):
		"""
		글쓰기 : 문서앞에서 n번째 라인의 제일앞에 글자를 쓰기

		:param input_no: 라인번호
		:param input_text: 입력글자
		"""
		self.move_cursor_from_doc_start_to_nth_line_start(input_no)
		self.write_text(input_text)

	def write_text_at_nth_para_end(self, para_no=1, input_text="hfs1234234234;lmk"):
		"""
		글쓰기 : 문단의 번호로 선택된 문단의 제일 뒷부분에 글을 넣는것

		:param para_no: 문단 번호
		:param input_text: 입력 문자
		"""
		self.doc.Paragraphs(para_no - 1).Content.InsertAfter(input_text)

	def write_text_at_range_end(self, input_text):
		"""
		글쓰기 : range의 끝부분에 글씨쓰기

		:param input_text: 입력 문자
		:return:
		"""
		y = self.range.End - 1
		self.doc.Range(y, y).Text = input_text

	def write_text_at_selection_end_with_color_size_bold(self, input_text, input_color="red", input_size=11, input_bold=False):
		"""
		글쓰기 : 선택한 영역에 글을쓰면서, 색깔과 크기, bold를 설정하는 것
		현재 선택된 영역에 글씨를 넣는것

		:param input_text: 입력문자
		:param input_color: 색이름
		:param input_size: 크기
		:param input_bold: 굵게
		"""

		self.selection.Collapse(0) # 0 : end, 1:start

		my_range = self.word_application.Selection.Range

		my_range.Text = input_text
		my_range.Bold = input_bold
		my_range.Font.Size = input_size
		my_range.Font.Color = self.colorx.change_xcolor_to_rgbint(input_color)
		my_range.Select()

	def write_text_at_selection_end_with_font_style(self, input_value, *option_font_list):
		"""
		글쓰기 : 선택영역의 맨 뒷부분에 폰트형식으로 글씨쓰기

		:param input_value: 입력 값
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		char_sno = self.selection.End
		self.selection.InsertAfter(input_value)
		self.select_xy(char_sno, char_sno + len(input_value))

		if option_font_list[0]:
			self.set_font_default_for_selection()
			self.run_font_style(option_font_list[0])
		self.selection.Collapse(0) # 0 : end, 1:start

	def write_text_at_selection_end_with_new_line(self, input_text):
		"""
		글쓰기 : 커서의 시작위치에 글을 쓰기
		:param input_text: 입력글자
		:return:
		"""
		self.write_text_at_selection_end(input_text + "\r\n")
		self.selection.Collapse(0) # 0 : end, 1:start

	def write_text_at_selection_start(self, input_text):
		"""
		글쓰기 : 선택영역의 처음에 글씨쓰기

		:param input_text: 입력 값
		:return:
		"""
		self.selection.InsertBefore(input_text)

	def write_text_for_all_table_header(self, xy=[1, 1], input_value="", field_code="", field_format="", position="left"):
		"""
		테이블의 해더를 쓰는것

		:param xy: 테이블의 셀위치 (가로열, 세로열)
		:param input_value: 입력값
		:param field_code:
		:param field_format:
		:param position:
		:return:
		"""
		self.varx["position_vs_enum"] = {"left": 0, "middle": 1, "right": 2}
		for section in self.doc.Sections:
			header = section.Headers(1)
			header_range = header.Range
			for table in header_range.Tables:
				if input_value != "" and field_code == "":
					aaa = table.Cell(xy[0], xy[1]).Range
					aaa.Text = input_value
					aaa.ParagraphFormat.Alignment = self.varx["position_vs_enum"][position]
				elif input_value != "" and field_code != "":
					# 맨 뒤에서부터 글을 써가야 한다
					aaa = table.Cell(xy[0], xy[1]).Range
					aaa.Collapse(1)
					aaa.Fields.Add(aaa, -1, field_code, True)
					aaa.Collapse(1)
					aaa.Text = input_value
					aaa.ParagraphFormat.Alignment = self.varx["position_vs_enum"][position]
				elif input_value == "" and field_code != "":
					aaa = table.Cell(xy[0], xy[1]).Range
					aaa.Collapse(0)
					aaa.Fields.Add(aaa, -1, field_code, True)
					aaa.ParagraphFormat.Alignment = self.varx["position_vs_enum"][position]

	def write_text_in_selected_shape(self, shape_obj, input_text=None, font_size=None, font_bold=None):
		"""
		글쓰기 : 선택한 도형의 안에 글씨를 쓰는 것

		:param input_text: 입력 문자
		:param font_size: 폰트 크기
		:param font_bold: 굵게
		:return:
		"""
		# img = self.selection.InlineShapes(0)
		# shape = shape_obj.ConvertToShape()
		if input_text: shape_obj.TextFrame.TextRange.Text = input_text
		if font_size: shape_obj.TextFrame.TextRange.Font.Size = font_size
		if font_bold: shape_obj.TextFrame.TextRange.Font.Bold = font_bold

	def write_text_in_table_at_nth_cell(self, input_table_no_or_obj, input_no=1, input_text=""):
		"""
		글쓰기 : 테이블의 n번째 셀에 값넣기

		:param input_table_no_or_obj: 테이블 번호나 객체를 입력
		:param input_no: 숫자(정수, 1부터 시작하는 숫자)
		:param input_text: 입력글자
		:return:
		"""

		if type(input_table_no_or_obj) == type(123):
			table_obj = self.doc.Tables(input_table_no_or_obj)
		else:
			table_obj = input_table_no_or_obj
		y_line = table_obj.Columns.Count
		x = int(input_no / (y_line + 1)) + 1
		y = input_no - int(input_no / (y_line + 1)) * y_line
		table_obj.Cell(x, y).Range.Text = str(input_text)

	def write_text_in_table_at_xy_cell(self, input_table_no_or_obj, xy, input_text):
		"""
		글쓰기 : 테이블의 가로세로 셀 위치에 값넣기

		:param input_table_no_or_obj: 테이블 번호나 객체를 입력
		:param xy: 테이블의 셀 (가로, 세로)
		:param input_text: 입력글자
		:return:
		"""
		if type(input_table_no_or_obj) == type(123):
			table_obj = self.doc.Tables(input_table_no_or_obj)
		else:
			table_obj = input_table_no_or_obj
		table_obj.Cell(int(xy[0]), int(xy[1])).Range.Text = str(input_text)

	def write_text_with_font_options(self, input_text):
		"""
		폰트옵션중 1개로 글자를 입력하는 것

		:param input_text: 입력 문자
		:return:
		"""
		self.selection.Collapse(0) # 0 : end, 1:start
		my_range = self.word_application.Selection.Range
		my_range.Text = input_text
		if self.varx["font_option"]["xcolor"]: my_range.Font.Color = self.colorx.change_xcolor_to_rgbint(
			self.varx["font_option"]["xcolor"])
		if self.varx["font_option"]["size"]: my_range.Font.Size = self.varx["font_option"]["size"]
		if self.varx["font_option"]["underline"]: my_range.Font.Underline = self.varx["font_option"]["underline"]
		if self.varx["font_option"]["italic"]: my_range.Font.Italic = self.varx["font_option"]["italic"]
		if self.varx["font_option"]["bold"]: my_range.Font.Bold = self.varx["font_option"]["bold"]
		if self.varx["font_option"]["strikethrough"]: my_range.Font.StrikeThrough = self.varx["font_option"][
			"strikethrough"]
		if self.varx["font_option"]["name"]: my_range.Font.Name = self.varx["font_option"]["name"]
		if self.varx["font_option"]["align"]: my_range.ParagraphFormat.Alignment = self.varx["font_option"][
			"align"]
		if self.varx["font_option"]["subscript"]: my_range.Font.Subscript = self.varx["font_option"]["subscript"]
		if self.varx["font_option"]["superscript"]: my_range.Font.Superscript = self.varx["font_option"]["superscript"]

	def split_selection_text_to_l1d_by_each_paragraph(self, input_text):
		"""
		워드의 선택영역을 줄바꿈을 기준으로 1차원리스트로 만들어 주는것

		:param input_text: 입력 문자
		:return:
		"""
		result = input_text.split(chr(13))
		return result

	def draw_black_border_to_images(self, alignment=""):
		"""
		모든 그림 객체에 대해 반복

		:param alignment: 정렬
		:return:
		"""
		for shape in self.doc.InlineShapes: # 그림 객체인지 확인
			if shape.Type == 3: # 3은 그림 객체를 의미
				# 테두리 색상 설정 (검정색)
				shape.Borders.Enable = True
				shape.Borders.OutsideLineStyle = 1 # 실선
				shape.Borders.OutsideLineWidth =8
				shape.Borders.OutsideColor =0 #검정색 (RGB 값:0)

				if alignment:
					shape.Range.ParagraphFormat.Alignment = alignment # alignment값이 있으면 중앙 정렬을 의미
