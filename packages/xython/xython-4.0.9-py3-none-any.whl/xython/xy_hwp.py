# -*- coding: utf-8 -*-
import win32com.client  # pywin32의 모듈
import pythoncom
import xy_color, xy_time, xy_common

class xy_hwp:
	"""
	아래아 한글을 쉽게 사용이 가능하도록 만든 모듈
	"""
	def __history(self):
		"""
		2025-03-30 : 전체적으로 손을 봄
		"""
		pass
	def ___terms___(self):
		"""
		현재의 용어는 가능하면 cursor로 사용한다 (커서가 있는곳을 의미)

		:return:
		"""
		pass

	def __check_hwp_obj(self):
		"""
		현재 오픈된 한글 문서가 있으면, 그 객체를 갖고온다

		:return:
		"""
		result = False
		context = pythoncom.CreateBindCtx(0)
		running_coms = pythoncom.GetRunningObjectTable()
		monikers = running_coms.EnumRunning()
		for moniker in monikers:
			name = moniker.GetDisplayName(context, moniker)
			if "hwpobject" in str(name).lower():
				#print("실행중인 한글 프로그램", name)
				result = True
				obje = running_coms.GetObject(moniker)
				# 만약 실행중일때는 기존의 프로그램을 self.han_program으로 할당하는 것이다
				self.han_program = win32com.client.Dispatch(obje.QueryInterface(pythoncom.IID_IDispatch))
				#print("is visible => ", self.han_program.XHwpWindows.Active_XHwpWindow.Visible, name)

		#if result:
		#	print('한글 application이 실행중이네요 (O)')
		#else:
		#	print('한글 application이 실행중이지 않네에요 (X)')
		return result

	def __init__(self, file_name=""):
		"""
		기본적인 변수들을 설정합니다

		:param file_name:
		"""
		self.varx = xy_common.xy_common().varx  # package안에서 공통적으로 사용되는 변수들
		self.han_program = ""
		self.var_action_name_vs_parameter_set_id = self.varx["han"]["action_name_vs_parameter_set_id"]
		self.var_action_name_vs_manual = self.varx["han"]["action_name_vs_manual"]
		self.current = {}

		# 한글 application이 실행중인지 확인한다
		if self.__check_hwp_obj():
			if not self.han_program:
				self.han_program = win32com.client.Dispatch("HWPFrame.HwpObject")
			if file_name == "":
				#print("실행1 : 한글프로그램 실행중 + ''")
				self.han_program.XHwpWindows.Active_XHwpWindow.Visible = 1  # 혹시 hidden으로 되어있을지 몰라서 show로 만드는 것
			elif file_name == "new":
				#print("실행2 : 한글프로그램 실행중 + 'new'")
				self.one_hwp = self.han_program.XHwpDocuments.Add(0)
				self.han_program.XHwpWindows.Active_XHwpWindow.Visible = 1  # 혹시 hidden으로 되어있을지 몰라서 show로 만드는 것
			else:
				self.han_program.Open(file_name)
		else:
			if file_name == "" or file_name == "new":
				#print("실행3 : 한글프로그램 실행 X + '' 또는 'new'")
				self.han_program = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
				self.han_program.RegisterModule("FilePathCheckDLL", "AutomationModule")  # 보안모둘 실행
				self.han_program.XHwpWindows.Active_XHwpWindow.Visible = 1
			else:
				self.han_program.Open(file_name)

	def active_doc(self):
		"""
		현재 오픈된 한글 문서의 객체를 갖고온다

		:return:
		"""
		context = pythoncom.CreateBindCtx(0)
		running_coms = pythoncom.GetRunningObjectTable()
		monikers = running_coms.EnumRunning()
		for moniker in monikers:
			name = moniker.GetDisplayName(context, moniker)
			if "hwp" in str(name).lower():
				obje = running_coms.GetObject(moniker)
				self.han_program = win32com.client.Dispatch(obje.QueryInterface(pythoncom.IID_IDispatch))
				self.han_program.RegisterModule("FilePathCheckDLL", "AutomationModule")  # 보안모둘 실행
				self.han_program.XHwpWindows.Item(0).Visible = 1

		return self.han_program

	def apply_font_style_for_selection(self, my_range):
		"""
		선택영역에 대한 공동폰트로 설정한것을 적용

		:param my_range:
		:return:
		"""
		if self.varx["han"]["basic_underline"]:
			my_range.Font.Underline = 1
		if self.varx["han"]["basic_size"]:
			my_range.Font.Size = self.varx["han"]["basic_size"]
		if self.varx["han"]["basic_bold"]:
			my_range.Font.Bold = 1
		if self.varx["han"]["rgb_int"]:
			my_range.Font.TextColor.RGB = self.varx["han"]["rgb_int"]

	def check_action_name(self, input_action):
		"""
		입력으로 드렁온 글자가 있는 모든 action name을 확인하는 것입니다

		:param input_action:action 이름
		:return:
		"""
		result = []

		for a_action in self.var_action_name_vs_parameter_set_id.keys():
			if str(input_action).lower() in str(a_action).lower():
				result.append(a_action)
			try:
				manual = self.var_action_name_vs_manual[a_action]
				if input_action in manual:
					result.append(a_action)
			except:
				pass

		return result

	def check_action_name_as_dic(self, input_action_name):
		"""
		별도의 입력값없이 결과만 갖고오는 action id에대한 모든 결과값을 dic형태로 갖고오는것

		:param input_action_name:
		:return:
		"""
		result = {}

		parameter_name = self.varx["han"]["action_name_vs_parameter_set_id"][input_action_name]

		action_obj = self.han_program.CreateAction(input_action_name)
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		action_obj.Execute(parameter_set_obj)

		for one in self.varx["han"]["parameter_set_id_vs_parameters"][parameter_name]:
			result[one] = parameter_set_obj.Item(one)
		return result

	def check_information_for_doc(self):
		"""
		현재 열려져있는 문서의 기본 정보를 갖고옵니다

		:return:
		"""
		action_obj = self.han_program.CreateAction("DocumentInfo")
		# 변수를 넣는 변수객체를 만든다
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)

		# 결과를 얻고싶은 변수를 넣읍니다
		parameter_set_obj.SetItem("DetailInfo", 1)
		action_obj.Execute(parameter_set_obj)

		result = {}
		para_id_set = ["CurPos", "CurParaLen", "CurCtrl", "CurParaCount",
					   "RootPara", "RootPos", "RootParaCout", "DetailInfo", "DetailCharCount", "DetailWordCount",
					   "DetailLineCount", "DetailPageCount", "DetailCurPage", "DetailCurPrtPage",
					   "SectionInfo", "SecDef", ]

		for one_id in para_id_set:
			result[one_id] = parameter_set_obj.Item(one_id)

		return result

	def check_options(self, input_parameter):
		"""
		입력요소에 대하여 확인하는 것

		:param input_parameter:
		:return:
		"""
		# all_data = basic_data_for_han.basic_data().xvar
		try:
			result = self.varx["han"]["parameter_vs_parameter_option"][input_parameter]
		except:
			result = "없음"
		if not result:
			result = "없음"
		return result

	def check_parameter_set_id(self, input_action):
		"""
		액션이름이 들어오면 parameter_set_id를 돌려주는 것
		all_data = basic_data_for_han.basic_data().xvar

		:param input_action:action 이름
		:return:
		"""
		result = "없음"
		try:
			result = self.varx["han"]['action_name_vs_parameter_set_id'][input_action]
		except:
			pass
		return result

	def check_parameters(self, input_parameter_set_id):
		"""
		입력 parameters에 대하여 확인하는 것

		:param input_parameter_set_id:
		:return:
		"""
		# all_data = basic_data_for_han.basic_data().xvar
		try:
			result = self.varx["han"]["parameter_set_id_vs_parameters"][input_parameter_set_id]
		except:
			result = "없음"
		if not result:
			result = "없음"
		return result

	def close(self):
		"""
		현재 활성화가된 한글 객체를 닫는다

		:return:
		"""
		self.han_program.Clear(3)
		self.han_program.Quit()

	def close_all(self):
		"""
		열려져있는 모든 한글 객체를 닫는다

		:return:
		"""
		context = pythoncom.CreateBindCtx(0)
		running_coms = pythoncom.GetRunningObjectTable()
		monikers = running_coms.EnumRunning()
		for moniker in monikers:
			name = moniker.GetDisplayName(context, moniker)
			if "hwpobject" in str(name).lower():
				#print(name)
				obje = running_coms.GetObject(moniker)
				self.han_program = win32com.client.Dispatch(obje.QueryInterface(pythoncom.IID_IDispatch))
				self.han_program.RegisterModule("FilePathCheckDLL", "AutomationModule")  # 보안모둘 실행
				self.han_program.Clear(3)
				self.han_program.Quit()

	def copy(self):
		"""
		복사하기

		:return:
		"""
		self.han_program.HAction.Run('Copy')

	def copy_for_selection(self):
		"""
		복사 : 선택한 영역을 복사

		:return:
		"""
		self.han_program.HAction.Run('Copy')

	def count_char_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 전체 글자수

		:return:
		"""
		result = self.check_information_for_doc()["DetailCharCount"]
		return result

	def count_char_for_selection(self):
		"""
		갯수 : 선택영역의 전체 글자갯수 (공백도 1개의 글자임)

		:return:
		"""

		aaa = self.read_value_for_selection()
		result = len(str(aaa))
		return result

	def count_doc(self):
		"""
		갯수 : 열려져있는 문서의 총 갯수를 돌려준다

		:return:
		"""
		result = self.han_program.XHwpWindows.Count  # 총문서 갯수
		return result

	def count_hwp_obj(self):
		"""
		갯수 : 현재 오픈된 한글 문서가 있으면, 그 객체를 갖고온다

		:return:
		"""
		result = []
		context = pythoncom.CreateBindCtx(0)
		running_coms = pythoncom.GetRunningObjectTable()
		monikers = running_coms.EnumRunning()
		for moniker in monikers:
			name = moniker.GetDisplayName(context, moniker)
			if "hwp" in str(name).lower():
				#print(name)
				result.append(name)

		#print("갯수는 => ", len(result), len)
		return result

	def count_line_in_doc(self):
		"""
		갯수 : 현재 문서의 전체 줄수

		:return:
		"""
		action_obj = self.han_program.CreateAction("DocumentInfo")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("DetailInfo", 1)
		action_obj.Execute(parameter_set_obj)
		result = parameter_set_obj.Item("DetailLineCount")
		return result

	def count_page_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 총 페이지수

		:return:
		"""
		result = self.check_information_for_doc()["DetailPageCount"]
		return result

	def count_para_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 총 문단수

		:return:
		"""
		pass

	def count_shape_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 총 그리기 개체수
		첫번째 컨트롤(HaedCtrl)를 사용해서 탐색 시작할수있다

		:return:
		"""
		ctrl = self.han_program.HeadCtrl
		count = 0
		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "gso":
				count += 1
			ctrl = nextctrl
		return count

	def count_table_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 총 테이블수
		첫번째 컨트롤(HaedCtrl)부터 탐색 시작
		"""
		ctrl = self.han_program.HeadCtrl
		count = 0
		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "tbl":
				count += 1
			ctrl = nextctrl
		return count

	def count_word_in_doc(self):
		"""
		갯수 : 현재 선택된 문서의 총 단어수

		:return:
		"""
		action_obj = self.han_program.CreateAction("DocumentInfo")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("DetailInfo", 1)
		action_obj.Execute(parameter_set_obj)

		result = parameter_set_obj.Item("DetailWordCount")
		return result

	def count_word_for_selection(self):
		"""
		갯수 : 선택영역안의 단어수

		:return:
		"""
		aaa = self.read_text_for_selection()
		result = len(str(aaa).split(" "))
		return result

	def data_control_id(self):
		"""
		control의 id

		:return:
		"""
		aaa = {
			"cold": ["ColDef", "단"],
			"secd": ["SecDef", "구역"],
			"fn": ["FootnoteShape", "각주"],
			"en": ["FootnoteShape", "미주"],
			"tbl": ["Table", "표"],
			"eqed": ["EqEdit", "수식"],
			"gso": ["ShapeObject", "그리기 개체"],
			"atno": ["AutoNum", "번호 넣기"],
			"nwno": ["AutoNum", "새 번호로"],
			"pgct": ["PageNumCtrl", "페이지 번호 제어 "],
			"pghd": ["PageHiding", "감추기"],
			"pgnp": ["PageNumPos", "쪽 번호 위치"],
			"head": ["HeaderFooter", "머리말"],
			"foot": ["HeaderFooter", "꼬리말"],
			"%dte": ["FieldCtrl", "현재의 날짜/시간 필드"],
			"%ddt": ["FieldCtrl", "파일 작성 날짜/시간 필드"],
			"%pat": ["FieldCtrl", "문서 경로 필드"],
			"%bmk": ["FieldCtrl", "블록 책갈피"],
			"%mmg": ["FieldCtrl", "메일 머지"],
			"%xrf": ["FieldCtrl", "상호 참조"],
			"%fmu": ["FieldCtrl", "계산식"],
			"%clk": ["FieldCtrl", "누름틀"],
			"%smr": ["FieldCtrl", "문서 요약 정보 필드"],
			"%usr": ["FieldCtrl", "사용자 정보 필드"],
			"%hlk": ["FieldCtrl", "하이퍼링크"],
			"bokm": ["TextCtrl", "책갈피"],
			"idxm": ["IndexMark", "찾아보기"],
			"tdut": ["Dutmal", "덧말"],
			"tcmt": ["없음", "주석"], }
		return aaa

	def delete_all_in_doc(self):
		"""
		삭제 : 문서의 모든 것을 삭제

		:return:
		"""
		self.han_program.Run('SelectAll')
		self.han_program.HAction.Run("Delete")

	def delete_all_in_document(self):
		"""
		삭제 : 문서의 모든 것을 삭제

		:return:
		"""
		self.han_program.Run('SelectAll')
		self.han_program.HAction.Run("Delete")

	def delete_char_by_no(self, input_no):
		"""
		삭제 : 문서의 시작에서부터 n번째의 문자를 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no - 1)
		self.select_nth_char_from_selection(1)
		self.han_program.HAction.Run("Delete")

	def delete_char_from_cursor_to_end_of_line(self):
		"""
		삭제 : 현재 커서에서 줄끝가지의 글자를 삭제
		selection이 있으면 실행이 되지 않는다

		:return:
		"""
		self.move_cursor_to_begin_of_selection()
		self.han_program.HAction.Run("DeleteLineEnd")

	def delete_char_from_cursor_to_nth_char(self, input_no):
		"""
		삭제 : 현재 커서에서 n번째 글자까지 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_char_from_selection(input_no - 1)
		self.han_program.HAction.Run("Delete")

	def delete_current_line_at_cursor(self):
		"""
		삭제 : 현재 커서가있는 라인의 삭제

		:return:
		"""
		self.han_program.HAction.Run("DeleteLine")

	def delete_header_footer(self):
		"""
		삭제 : 현재 선택된 문서의 머릿글과 꼬릿글을 삭제

		:return:
		"""
		return self.han_program.HAction.Run("HeaderFooterDelete")

	def delete_line_at_cursor(self):
		"""
		삭제 : 현재 커서가 있는 라인 삭제

		:return:
		"""
		self.han_program.HAction.Run("DeleteLine")

	def delete_line_by_no(self, input_no):
		"""
		삭제 : 줄번호로 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no - 1)
		self.han_program.HAction.Run("DeleteLine")

	def delete_nth_char_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서의 시작에서 부터 n번째의 글자를 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no - 1)
		self.select_nth_char_from_selection(1)
		self.han_program.HAction.Run("Delete")

	def delete_nth_line_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서시작에서 n번째 라인을 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no - 1)
		self.han_program.HAction.Run("DeleteLine")

	def delete_nth_para_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서시작에서 n번째 문단을 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_para_from_begin_of_doc(input_no - 1)
		self.select_current_para()
		self.han_program.HAction.Run("Delete")

	def delete_nth_shape_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서시작에서 n번째 그리기 객체 번호로 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0

		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "gso":
				count += 1
				if input_no == count:
					# self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					# self.han_program.FindCtrl()
					self.han_program.DeleteCtrl(ctrl)
					break
			ctrl = nextctrl

	def delete_nth_table_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서시작에서 n번째 테이블 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0

		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "tbl":
				count += 1
				if input_no == count:
					# self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					# self.han_program.FindCtrl()
					self.han_program.DeleteCtrl(ctrl)
					break
			ctrl = nextctrl

	def delete_nth_word_from_selection(self):
		"""
		삭제 : 선택한 영역을 기준으로 왼쪽 여역을 기준으로 n번째 단어 삭제

		:return:
		"""
		self.han_program.HAction.Run("DeleteWordBack")

	def delete_nth_word_from_start_of_doc(self, input_no):
		"""
		삭제 : 문서처음에서부터 n번째 단어 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no - 1)
		self.han_program.HAction.Run("Delete")

	def delete_one_word_at_cursor(self):
		"""
		삭제 : 커서에서 단어1개 삭제

		:return:
		"""
		self.han_program.HAction.Run("DeleteWord")

	def delete_para_by_no(self, input_no):
		"""
		삭제 : 문단번호로 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_para_by_no(input_no - 1)
		self.select_current_para()
		self.han_program.HAction.Run("Delete")

	def delete_previous_word_from_cursor(self):
		"""
		삭제 : 현재커서의 전 단어 삭제

		:return:
		"""
		self.han_program.HAction.Run("DeleteWordBack")

	def delete_selection(self):
		"""
		삭제 : 선택영역 삭제

		:return:
		"""
		self.han_program.HAction.Run("Delete")

	def delete_shape_by_no(self, input_no):
		"""
		삭제 : 그리기 객체 번호로 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0

		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "gso":
				# print(ctrl.CtrlID,count )
				count += 1
				if input_no == count:
					# self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					# self.han_program.FindCtrl()
					self.han_program.DeleteCtrl(ctrl)
					break
			ctrl = nextctrl

	def delete_table_by_no(self, input_no):
		"""
		삭제 : 테이블 번호로 삭제

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0

		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "tbl":
				# print(ctrl.CtrlID,count )
				count += 1
				if input_no == count:
					# self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					# self.han_program.FindCtrl()
					self.han_program.DeleteCtrl(ctrl)
					break
			ctrl = nextctrl

	def delete_word_at_cursor(self):
		"""
		삭제 : 커서가 있는 단어1개 삭제하는데, 만약 영역이 선택되었다면, 제일 왼쪽의 단어가 삭제된다

		:return:
		"""
		self.han_program.HAction.Run("DeleteWord")

	def delete_word_by_no(self, input_no):
		"""
		삭제 : 전체문장에서 n번째 단어를 삭제하는 것입니다

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no - 1)
		self.han_program.HAction.Run("Delete")

	def delete_xline_in_table(self, table_no, x):
		"""
		삭제 : 현재 문서의 n번째 테이블의 x번째 가로줄 하나를 삭제

		:param table_no: 테이블 번호
		:param x:
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		for no in range(x - 1):
			self.han_program.Run("TableLowerCell")
		self.han_program.CreateAction("DeleteLine")

	def delete_yline_in_table(self, table_no, y):
		"""
		삭제 : 현재 문서의 n번째 테이블의 y번째 세로줄 하나를 삭제

		:param table_no: 테이블 번호
		:param y:
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")
		for no in range(y - 1):
			self.han_program.Run("TableRightCell")
		self.han_program.CreateAction("SelectColumn")
		self.han_program.CreateAction("Delete")

	def doc_info(self):
		"""
		문서의 정보

		:return:
		"""
		self.han_program.HAction.GetDefault("DocumentInfo", self.han_program.HParameterSet.HDocumentInfo.HSet)
		self.han_program.HParameterSet.HDocumentInfo.HSet("DetailInfo", 1)
		self.han_program.HAction.Execute("DocumentInfo", self.han_program.HParameterSet.HDocumentInfo.HSet)
		#print(self.han_program.HParameterSet.HDocumentInfo.DetailCharCount)
		result = self.han_program.HParameterSet.HDocumentInfo.Item("DetailCharCount")
		return result

	def draw_outline_for_selection(self):
		"""
		선택영역의 테두리 그리기

		:return:
		"""
		self.han_program.CreateAction("CharShapeOutline")

	def filter_all_action_name_by_input_text(self, input_text):
		"""
		모든 액션 리스트중 입력값과 같은 이름이 들어간것을 갖고오는것

		:return:
		"""
		result = []
		for one_action_name in list(self.varx["han"]['action_name_vs_manual'].keys()):
			if str(input_text).lower() in str(one_action_name).lower():
				result.append(one_action_name)
		return result

	def free_basic_font_style(self):
		"""
		기본 font로 저장된 자료들을 초기화하는 것이다

		:return:
		"""
		self.varx["han"]["apply_basic_font"] = False
		self.varx["han"]["basic_underline"] = False
		self.varx["han"]["basic_size"] = False
		self.varx["han"]["basic_bold"] = False
		self.varx["han"]["rgb_int"] = False

	def get_all_action_name(self):
		"""
		모든 액션의 리스트를 갖고옵니다
		아래아한글은 action이라는 형태로 메소드의 기능을 할당하는데, 어떤 메소드들이 가능한지를 갖고오는 것입니다

		:return:
		"""
		result = list(self.varx["han"]['action_name_vs_manual'].keys())
		return result

	def get_all_document_information(self):
		"""
		기본 문서의 정보를 돌려줍니다

		:return:
		"""
		action = self.han_program.CreateAction("DocumentInfo")
		para_set = action.CreateSet()
		action.GetDefault(para_set)
		para_set.SetItem("SectionInfo", 1)
		result = action.Execute(para_set)
		return result

	def get_all_information_for_current_cursor(self):
		"""
		커서의 모든 정보를 알아 보은 것

		:return:
		"""
		lpp = self.han_program.GetPosBySet()
		result = {}
		result["para_no"] = lpp["Para"] + 1
		result["line_no"] = self.get_current_line_no()
		result["char_no"] = lpp["Pos"]

		return result

	def get_all_parameter_data_for_action_name(self, input_action_name):
		"""
		모든 액션의 리스트를 갖고옵니다

		:param input_action_name:
		:return:
		"""
		result = {}
		result["action_name"] = input_action_name
		result["parameter_name"] = self.get_parameter_name_for_action_name(input_action_name)
		result["parameter_items"] = None
		result["parameter_option"] = {}
		if result["parameter_name"]:
			result["parameter_items"] = self.get_all_parameter_item_by_parameter_name(result["parameter_name"])
			if result["parameter_items"]:
				for one_item in result["parameter_items"]:
					result["parameter_option"][one_item] = {}
					result["parameter_option"][one_item] = self.get_parameter_option_for_paramater_item(one_item)

		return result

	def get_all_parameter_item_by_parameter_name(self, input_parameter_set_id):
		"""
		parameter_name : 각 action에 연결된 parameter의 번호, parameter id와 같은 개념
		parameter_item_set : all parameter element, parameter id의 모든 파라미타 들
		parameter_item_option_set : 한개의 parameter_item 의 option 사항들

		:param input_parameter_set_id:
		:return:
		"""
		result = None

		try:
			result = self.varx["han"]["parameter_set_id_vs_parameters"][input_parameter_set_id]
		except:
			pass
		return result

	def get_char_no_at_cursor(self):
		"""
		커서위치를 문단과 문단에서의 위치로 나타낸다
		GetPos : 문단의 번호 + 문단의 시작에서 몇번째 위치

		:return:
		"""
		result = self.han_program.KeyIndicator()[6]
		return result

	def get_char_no_for_end_of_selection(self):
		"""
		선택영역의 오른쪽 끝의 글자번호

		:return:
		"""
		no1 = self.get_char_no_at_cursor()
		no2 = self.count_char_for_selection()
		return no1 + no2 - 1

	def get_char_no_for_start_of_selection(self):
		"""
		선택영역의 시작 글자가 전체 문서에서 몇번째 글자인지를 알아내는 것

		:return:
		"""
		result = self.get_char_no_at_cursor()
		return result

	def get_current_line_no(self):
		"""
		현재 커서가 위치한곳의 줄번호

		:return:
		"""
		result = self.han_program.KeyIndicator()[5]  # 줄
		return result

	def get_current_page_no(self):
		"""
		현재 커서가 위치한곳의 페이지번호

		:return:
		"""
		result = self.han_program.Item(0).XHwpDocumentInfo.CurrentPage
		return result

	def get_current_pos(self):
		"""
		list : 캐럿이 위치한 문서내 리스트 ID
		para : 캐럿이 위치한 문단 번호
		pso : 캐럿이 위치한 문단내 글자위치

		:return:
		"""
		result = self.han_program.Getpos()
		return result

	def get_current_xy_in_table(self):
		"""
		테이블안의 어느곳에있는 커서의 xy번호를 알아내는 것

		:return:
		"""
		# aaa = self.han_program.KeyIndicator()
		# cell_a1 = aaa.Split('(', ')')[1]

		if not self.han_program.CellShape:  # 표 안에 있을 때만 CellShape 오브젝트를 리턴함
			raise AttributeError("현재 캐럿이 표 안에 있지 않습니다.")
		return self.han_program.KeyIndicator()[-1][1:].split(")")[0]

	def get_docsummaryinfo_as_dic(self):
		"""
		문서 전체의 정보를 갖고온다

		:return:
		"""
		result = self.check_action_name_as_dic("DocSummaryInfo")
		return result

	def get_documentinfo_as_dic(self):
		"""
		문서 전체의 정보를 갖고온다

		:return:
		"""
		result = self.check_action_name_as_dic("DocumentInfo")
		return result

	def get_end_char_no_of_selection(self):
		"""
		현재 선택한 영역에서 오른쪽 끝의 글자의 번호를 돌려준다

		:return:
		"""
		no1 = self.get_char_no_at_cursor()
		no2 = self.count_char_for_selection()
		return no1 + no2 - 1

	def get_information_for_current_cursor(self):
		"""
		커서의 모든 정보를 알아 보은 것

		:return:
		"""
		lpp = self.han_program.GetPosBySet()
		result = {}
		result["para_no"] = lpp["Para"] + 1
		result["line_no"] = self.get_line_no_at_cursor()
		result["char_no"] = lpp["Pos"]

		return result

	def get_information_for_doc(self):
		"""
		기본 문서의 정보

		:return:
		"""
		action_obj = self.han_program.CreateAction("DocumentInfo")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("SectionInfo", 1)
		result = action_obj.Execute(parameter_set_obj)
		return result

	def get_information_for_selection(self):
		"""
		GetSelectedPos함수의 결과값

		slist : 설정된 블록의 시작 리스트 아이디.
		spara : 설정된 블록의 시작 문단 아이디.
		spos : 설정된 블록의 문단 내 시작 글자 단위 위치.
		elist : 설정된 블록의 끝 리스트 아이디.
		epara : 설정된 블록의 끝 문단 아이디.
		epos : 설정된 블록의 문단 내 끝 글자 단위 위치.

		bcbc => [block_start, char_start,block_end, char_end]

		:return:
		"""
		result = {"ok_or_no": "", "sel_list_start_no": "", "sel_para_start_no": "", "sel_char_start_no": "", "sel_list_end_no": "", "sel_para_end_no": "", "sel_char_end_no": ""}

		[result["ok_or_no"], result["sel_list_start_no"], result["sel_para_start_no"], result["sel_char_start_no"],
		 result["sel_list_end_no"], result["sel_para_end_no"], result["sel_char_end_no"]] = self.han_program.GetSelectedPos()
		aaa = self.get_information_for_statusbar()
		result.update(aaa)

		return result

	def get_information_for_statusbar(self):
		"""
		statusbar에 나타나는 정보들
		기본적으로 information은 dic형식의 결과로 돌려준다

		:return:
		"""
		result = {"ok_or_no": "", "section_no_total": "총구역", "section_no": "현재구역", "page_no": "쪽",
				  "col_no": "단", "line_no": "줄", "char_no": "칸", "over": "", "ctrl_name": "컨트롤이름"}

		[result["ok_or_no"], result["section_no_total"], result["section_no"], result["page_no"], result["col_no"], result["line_no"],
		 result["char_no"], result["over"], result["ctrl_name"]] = self.han_program.KeyIndicator()
		return result

	def get_information_for_statusbar_old(self):
		"""
		statusbar에 나타나는 정보들

		:return:
		"""
		parameter_set_obj = self.han_program.KeyIndicator()
		result = {}
		result["성공/실패"] = parameter_set_obj[0]
		result["총구역"] = parameter_set_obj[1]
		result["현재구역"] = parameter_set_obj[2]
		result["쪽"] = parameter_set_obj[3]
		result["단"] = parameter_set_obj[4]
		result["줄"] = parameter_set_obj[5]
		result["칸"] = parameter_set_obj[6]  # 한글은 1글자가 2칸을 차지한다
		result["삽입/겹침"] = parameter_set_obj[7]
		result["컨트롤 종류"] = parameter_set_obj[8]
		return result

	def get_line_no_at_cursor(self):
		"""
		커서의 줄번호
		마지막의 커서위치이다

		:return:
		"""
		result = self.han_program.KeyIndicator()[5]  # 줄
		return result

	def get_line_no_for_start_of_selection(self):
		"""
		선택영역의 첫번째 줄이 전체 문서에서 몇번째 줄번호 인지를 확인하는 것
		잘못됨, 다시 확인해야 함

		:return:
		"""
		result = self.get_line_no_at_cursor()
		return result

	def get_page_no_at_cursor(self):
		"""
		현재커서의 페이지 번호

		:return:
		"""
		result = self.han_program.Item(0).XHwpDocumentInfo.CurrentPage
		return result

	def get_page_no_for_start_of_selection(self):
		"""
		선택영역의 시작 페이지 번호

		:return:
		"""
		result = self.get_page_no_at_cursor()
		return result

	def get_para_no_at_cursor(self):
		"""
		현재커서의 문단 번호

		:return:
		"""
		result = self.han_program.GetPos()[1]
		# result = self.han_program.KeyIndicator()[4]  # 단
		return result

	def get_parameter_name_for_action_name(self, input_action):
		"""
		액션이름이 들어오면 parameter_set_id를 돌려주는 것
		all_data = basic_data_for_han.basic_data().xvar

		:param input_action:action 이름
		:return:
		"""
		result = None
		try:
			result = self.varx["han"]['action_name_vs_parameter_set_id'][input_action]
		except:
			pass
		return result

	def get_parameter_option_for_paramater_item(self, input_parameter):
		"""
		입력변수는 option들이 있는데, 어떤 옵션이 있는지 확인해 주는 것입니다

		:param input_parameter:
		:return:
		"""
		result = None

		try:
			result = self.varx["han"]["parameter_vs_parameter_option"][input_parameter]
		except:
			pass
		return result

	def get_parameters_for_parameter_set_id(self, input_parameter_set_id):
		"""
		parameter_set_id에대한 parameter를 알아내는 것

		:param input_parameter_set_id:
		:return:
		"""
		result = None
		try:
			result = self.varx["han"]['parameter_set_id_vs_parameters'][input_parameter_set_id]
		except:
			pass
		return result

	def get_pos_at_cursor(self):
		"""
		현재 커서의 아래 정보를 알아내는 것
		list : 캐럿이 위치한 문서내 리스트 ID
		para : 캐럿이 위치한 문단 번호
		pso : 캐럿이 위치한 문단내 글자위치

		:return:
		"""
		result = self.han_program.GetPos()
		return result

	def get_pos_for_selection(self):
		"""
		API로 갖고오는 정보
		:return:

		slist : 시작 리스트 번호
		spara : 시작 문단 번호
		spos : 문단내의 시작 글자 단위 위치
		elist : 끝 작리스트 번호
		epara : 끝  문단 번호
		epos : 문단내의 끝 글자 단위 위치

		:return:
		"""
		_, slist, spara, spos, elist, epara, epos = self.han_program.GetSelectedPos()
		return slist, spara, spos, elist, epara, epos

	def get_shape_obj_by_no(self, input_no):
		"""
		그리기 개개체를 번호로 선택하기

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0
		result = False

		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "gso":
				count += 1
				if input_no == count:
					self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					self.han_program.FindCtrl()
					break
			ctrl = nextctrl
		return result

	def get_start_char_no_of_selection(self):
		"""
		선택영역의 시작 글자의 번호

		:return:
		"""
		result = self.get_char_no_at_cursor()
		return result

	def get_start_line_no_of_selection(self):
		"""
		선택영역의 첫번째 줄이 전체 문서에서 몇번째 줄번호 인지를 확인하는 것

		:return:
		"""
		result = self.get_line_no_at_cursor()
		return result

	def get_start_page_no_of_selection(self):
		"""
		선택영역의 시작 페이지 번호

		:return:
		"""
		result = self.get_page_no_at_cursor()
		return result

	def insert_left_line_at_end_of_table(self):
		"""
		테이블의 맨 왼쪽에 새로운 한줄 삽입

		:return:
		"""
		self.han_program.CreateAction("TableInsertLeftColumn")

	def insert_lower_line_at_end_of_table(self):
		"""
		테이블의 맨 아레쪽에 새로운 한줄 삽입

		:return:
		"""
		self.han_program.CreateAction("TableInsertLowerRow")

	def insert_multi_xline_in_table(self, input_no):
		"""
		테이블의 아래쪽에 새로운 n개의 여러줄 삽입

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.CreateAction("TableInsertLowerRow")

	def insert_new_line(self, repeat_no=1):
		"""
		현재 커서가있는 위치에 새로운 라인을 삽입

		:param repeat_no: 반복횟수
		:return:
		"""
		for one in range(repeat_no):
			self.han_program.Run("BreakLine")

	def insert_new_page(self):
		"""
		새로운 페이지를 삽입

		:return:
		"""
		self.han_program.Run("BreakPage")

	def insert_new_para(self):
		"""
		새로운 문서를 삽입

		:return:
		"""
		self.han_program.Run("BreakPara")

	def insert_new_section(self):
		"""
		새로운 문단을 삽입

		:return:
		"""
		self.han_program.Run("BreakSection")

	def insert_next_line_at_cusor(self, input_no=1):
		"""
		입력한 숫자만큼 다음줄을 만든다

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(int(input_no)):
			self.han_program.HAction.Run("BreakPara")  # 줄바꾸기

	def insert_right_line_at_end_of_table(self):
		"""
		테이블의 오른쪽끝에 새로운 한줄 삽입

		:return:
		"""
		self.han_program.CreateAction("TableInsertRightColumn")

	def insert_table_x_line_at_cusor(self):
		"""
		테이블의 아래쪽에 가로 한줄 삽입

		:return:
		"""
		self.han_program.HAction.Run("TableInsertLowerRow")  # 줄추가

	def insert_upper_line_at_end_of_table(self):
		"""
		테이블의 위쪽에 한줄 삽입

		:return:
		"""
		self.han_program.CreateAction("TableInsertUpperRow")

	def is_empty(self):
		"""
		빈 화일인지 확인하는 것

		:return:
		"""
		return self.han_program.IsEmpty

	def is_modified(self) -> bool:
		"""

		:return:
		"""
		return self.han_program.IsModified

	def is_selection(self):
		"""
		선택한 영역인지 확인하는 것

		:return:
		"""
		result = self.han_program.SelectionMode
		return result

	def make_table(self, x, y):
		"""
		현재 커서에 새로운 x,y개의 테이블을 만드는 것

		:param x:
		:param y:
		:return:
		"""
		# self.han_program.HParameterSet.HTableCreation.HSet = {}
		self.han_program.HAction.GetDefault("TableCreate", self.han_program.HParameterSet.HTableCreation.HSet)
		self.han_program.HParameterSet.HTableCreation.Rows = x
		self.han_program.HParameterSet.HTableCreation.Cols = y
		# self.han_program.HParameterSet.HTableCreation.WidthType = 2
		# self.han_program.HParameterSet.HTableCreation.HeightType = 1
		self.han_program.HParameterSet.HTableCreation.WidthValue = self.han_program.MiliToHwpUnit(148.0)
		self.han_program.HParameterSet.HTableCreation.HeightValue = self.han_program.MiliToHwpUnit(150)
		# self.han_program.HParameterSet.HTableCreation.CreateItemArray("ColWidth", x)
		# self.han_program.HParameterSet.HTableCreation.CreateItemArray("RowHeight", y)
		self.han_program.HParameterSet.HTableCreation.TableProperties.TreatAsChar = 1  # 글자처럼 취급
		# self.han_program.HParameterSet.HTableCreation.TableProperties.Width = self.han_program.MiliToHwpUnit(148)
		self.han_program.InsertCtrl("tbl", self.han_program.HParameterSet.HTableCreation.HSet)

	def make_table_old(self, x, y):
		"""

		:param x:
		:param y:
		:return:
		"""
		parameter_set_obj = self.han_program.CreateSet("Table")
		parameter_set_obj.SetItem("Rows", x)
		parameter_set_obj.SetItem("Cols", y)
		result = self.han_program.InsertCtrl("tbl", parameter_set_obj)
		return result


	def move_1(self, a, b, c):
		"""

		:param a:
		:param b:
		:param c:
		:return:
		"""
		self.han_program.MovePos(2, 0, 0)
		self.han_program.MovePos(a, b, c)

	def move_begin_cell_of_table(self):
		"""
		테이블의 처음으로 커서 옮기기

		:return:
		"""
		self.han_program.HAction.Run("ShapeObjTableSelCell")

	def move_begin_of_xline_for_table(self):
		"""
		테이블의 가로줄의 처음르로 커서 옮기기

		:return:
		"""
		self.han_program.HAction.Run("TableRowBegin")

	def move_begin_of_yline_for_table(self):
		"""
		테이블의 세로줄의 처음르로 커서 옮기기

		:return:
		"""
		self.han_program.HAction.Run("TableColBegin")

	def move_cell_to_begin_of_xline_at_table(self):
		"""
		테이블의 가로줄의 처음르로 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=104)

	def move_cell_to_begin_of_yline_at_table(self):
		"""
		테이블의 세로줄의 처음르로 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=106)

	def move_cell_to_end_of_xline_at_table(self):
		"""
		테이블의 오른쪽으로 끝칸으로 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=105)

	def move_cell_to_end_of_yline_at_table(self):
		"""
		테이블의 아래쪽으로 끝칸으로 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=107)

	def move_cell_to_one_down_at_table(self):
		"""
		테이블의 아래로 한칸 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=103)

	def move_cell_to_one_left_at_table(self):
		"""
		테이블의 왼쪽으로 한칸 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=100)

	def move_cell_to_one_right_at_table(self):
		"""
		테이블의 오른쪽으로 한칸 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=101)

	def move_cell_to_one_up_at_table(self):
		"""
		테이블의 한칸위로 커서 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=102)

	def move_cursor_by_filed_name(self, filed_name):
		"""
		필드이름으로 커서를 옮기기

		:param filed_name: 필드이름
		:return:
		"""
		self.han_program.MoveToField(filed_name, True, True, True)

	def move_cursor_nth_char_from_current_para(self, input_no):
		"""
		현재 문단의 n번째 글자로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		return self.han_program.MovePos(pos=input_no)

	def move_cursor_to_begin_of_current_line(self):
		"""
		현재라인의 시작으로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=22)

	def move_cursor_to_begin_of_current_para(self):
		"""
		현재 문단의 시작으로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=6)

	def move_cursor_to_begin_of_current_word(self):
		"""
		현재 단어의 시작으로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=8)

	def move_cursor_to_begin_of_doc(self):
		"""
		현재 문서의 시작으로 커서를 옮기기

		:return:
		"""
		self.han_program.MovePos(2)

	def move_cursor_to_begin_of_line_no(self, input_no):
		"""
		줄번호의 위치로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		self.move_cursor_to_nth_line_from_selection(input_no)

	def move_cursor_to_begin_of_next_para(self):
		"""
		커서이동 : 다음 문잔의 시작으로

		:return:
		"""
		self.han_program.MovePos(moveID=10)

	def move_cursor_to_begin_of_selection(self):
		"""
		선택영역의 시작 위치로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("MoveListBegin")

	def move_cursor_to_end_of_current_line(self):
		"""
		현재 줄의 끝위치로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=23)

	def move_cursor_to_end_of_current_para(self):
		"""
		현재 문단의 끝위치로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=7)

	def move_cursor_to_end_of_current_word(self):
		"""
		현재 단어의 끝으로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=9)

	def move_cursor_to_end_of_doc(self):
		"""
		현재 문서의 끝위치로 커서를 옮기기

		:return:
		"""
		self.han_program.MovePos(moveID=3)

	def move_cursor_to_end_of_previous_para(self):
		"""
		전 문단의 끝으로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=11)

	def move_cursor_to_end_of_range(self):
		"""
		영역의 끝으로 커서를 이동

		:return:
		"""
		self.han_program.HAction.Run("MoveListEnd")

	def move_cursor_to_end_of_selection(self):
		"""
		선택영역의 끝 위치로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("MoveListEnd")

	def move_cursor_to_left_cell_of_table(self):
		"""
		테이블의 한칸 왼쪽셀로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("TableLeftCell")

	def move_cursor_to_next_char(self):
		"""
		한 글자뒤로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=12)

	def move_cursor_to_next_char_from_selection(self):
		"""
		선택영역에서 한글자 뒤로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("MoveNextChar")

	def move_cursor_to_next_line(self):
		"""
		선택영역에서 한줄 뒤로 커서를 옮기기

		이것은 오류가 남
		self.han_program.HAction.Run("moveNextLine")
		"""
		self.han_program.HAction.Run("MoveLineDown")

	def move_cursor_to_next_line_from_selection(self):
		"""
		선택영역에서 다음 단어로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("MoveLineDown")

	def move_cursor_to_next_para_from_selection(self):
		"""
		선택영역에서 n번째 문단 뒤로 커서를 옮기기

		:return:
		"""
		self.han_program.MovePos(10)

	def move_cursor_to_next_shape_obj(self):
		"""
		다음 그리기객체로 커서이동

		:return:
		"""
		return self.han_program.HAction.Run("ShapeObjNextObject")

	def move_cursor_to_next_word(self):
		"""
		커서이동 : 다음단어로

		:return:
		"""
		self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_next_word_from_selection(self):
		"""
		선택영역에서 다음 단어로 커서를 옮기기

		:return:
		"""
		self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_nth_char(self, input_no=1):
		"""
		커서이동 : 현재에서 n번째 이후 문자로 이동

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextChar")

	def move_cursor_to_nth_char_from_begin_of_doc(self, input_no):
		"""
		문서의 n번째 글자로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		self.move_cursor_to_nth_char_from_selection(input_no)

	def move_cursor_to_nth_char_from_begin_of_doc_1(self, input_no):
		"""
		문서의 n번째 글자로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextChar")

	def move_cursor_to_nth_char_from_current_para(self, input_no):
		"""
		현재 문단의 n번째 글자로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		return self.han_program.MovePos(pos=input_no)

	def move_cursor_to_nth_char_from_selection(self, input_no):
		"""
		선택영역에서 n번째 글자 뒤로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		if input_no > 0:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveNextChar")
		else:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveNextChar")

	def move_cursor_to_nth_line(self, input_no=1):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveLineDown")

	def move_cursor_to_nth_line_from_begin_of_doc(self, input_no):
		"""
		문서의 n번째 줄로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		for no in range(input_no - 1):
			self.han_program.HAction.Run("MoveLineDown")

	def move_cursor_to_nth_line_from_selection(self, input_no):
		"""
		선택영역에서 n번째 줄뒤로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		if input_no > 0:
			for no in range(input_no + 1):
				self.han_program.HAction.Run("MoveNextLine")
		else:
			for no in range(input_no + 1):
				self.han_program.HAction.Run("MovePrevLine")

	def move_cursor_to_nth_next_char(self, input_no=1):
		"""
		현재 커서를 n번째 문자뒤로 이동한다

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char(input_no)

	def move_cursor_to_nth_next_line(self, input_no=1):
		"""
		현재 커서를 n번째 라인뒤로 이동한다

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line(input_no)

	def move_cursor_to_nth_next_para(self, input_no=1):
		"""
		현재 커서를 n번째 문단뒤로 이동한다

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_para(input_no)

	def move_cursor_to_nth_next_para_1(self, input_no):
		"""
		n번째 문단으로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		return self.han_program.MovePos(Para=input_no)

	def move_cursor_to_nth_next_word(self, input_no=1):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_word(input_no)

	def move_cursor_to_nth_para(self, input_no=1):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.MovePos(10)

	def move_cursor_to_nth_para_from_begin_of_doc(self, input_no):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		for no in range(input_no):
			self.han_program.MovePos(10)

	def move_cursor_to_nth_para_from_selection(self, input_no):
		"""
		선택영역에서 n번째 문단 뒤로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		position_obj = self.han_program.GetPos()
		self.han_program.SetPos(position_obj.list, position_obj.para + input_no, position_obj.pos)

	def move_cursor_to_nth_word(self, input_no=1):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_nth_word_from_begin_of_doc(self, input_no):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_nth_word_from_selection(self, input_no):
		"""
		선택영역에서 n번째 단어 뒤로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_nth_word_from_selection_old(self, input_no):
		"""

		:param input_no: 숫자(정수)
		:return:
		"""
		if input_no > 0:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveNextWord")
		else:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveNextWord")

	def move_cursor_to_para_by_no(self, input_no):
		"""
		n번째 문단으로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		return self.han_program.MovePos(Para=input_no)

	def move_cursor_to_previous_char(self):
		"""
		바로전 글자로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=13)

	def move_cursor_to_previous_line(self):
		"""
		바로전 줄로 커서를 옮기기

		:return:
		"""
		return self.han_program.MovePos(moveID=21)

	def move_cursor_to_previous_nth_char_from_selection(self, input_no):
		"""
		선택영역에서 n번째전 글자로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.MovePos(moveID=13)

	def move_cursor_to_previous_nth_line_from_selection(self, input_no):
		"""
		선택영역에서 n번째전 줄로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.MovePos(moveID=21)

	def move_cursor_to_previous_nth_para_from_selection(self, input_no):
		"""
		선택영역에서 n번째전 문단으로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		if input_no > 0:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveUp")
		else:
			for no in range(input_no):
				self.han_program.HAction.Run("MoveUp")

	def move_cursor_to_previous_nth_word_from_selection(self, input_no):
		"""
		선택영역에서 n번째전 단어로 커서를 옮기기

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MovePrevWord")

	def move_cursor_to_previous_para(self):
		"""
		커서이동 : 앞 para로 이동

		:return:
		"""
		self.move_cursor_to_previous_nth_para_from_selection(1)

	def move_cursor_to_previous_word(self):
		"""
		커서이동 : 앞 단어로 이동

		:return:
		"""
		return self.han_program.HAction.Run("MovePrevWord")

	def move_cursor_to_start_of_next_para(self):
		"""
		다음 분단이 올때까지 이동

		:return:
		"""
		self.han_program.HAction.Run("MoveParaEnd")

	def move_cursor_to_start_of_range(self):
		"""
		커서이동 : range의 시작으로 이동

		:return:
		"""
		self.han_program.HAction.Run("MoveListBegin")

	def move_page(self, input_no):
		"""
		5페이지로 이동

		:param input_no: 숫자(정수)
		:return:
		"""
		target_page = input_no
		self.han_program.HAction.Run("MoveDocBegin")  # 문서 시작으로 이동
		for _ in range(target_page - 1):
			self.han_program.HAction.Run("MovePageDown")  # 문서 시작으로 이동
		self.han_program.InitScan(...)

	def move_to_previous_char_from_selection(self):
		"""
		현재 선택한 영역을 기준으로 앞쪽글자로 하나 이동한다
		보통, 한문자씩 이동하면서 어떤것을 확인할때 사용한다

		:return:
		"""
		self.han_program.HAction.Run("MoveSelPrevChar")

	def new_doc(self):
		"""
		새로운 문서 open

		:return:
		"""
		self.han_program.XHwpDocuments.Add(0)

	def new_tab(self):
		"""
		새로운 탭만들기

		:return:
		"""
		self.han_program.XHwpDocuments.Add(1)

	def new_table_at_cursor(self, x, y):
		"""
		새로운 테이블 만들기

		:param x:
		:param y:
		:return:
		"""
		self.han_program.HParameterSet.HTableCreation.Rows = x
		self.han_program.HParameterSet.HTableCreation.Cols = y
		self.han_program.HParameterSet.HTableCreation.WidthType = 2
		self.han_program.HParameterSet.HTableCreation.HeightType = 1
		self.han_program.HParameterSet.HTableCreation.WidthValue = self.han_program.MiliToHwpUnit(148.0)
		self.han_program.HParameterSet.HTableCreation.HeightValue = self.han_program.MiliToHwpUnit(150)
		self.han_program.HParameterSet.HTableCreation.TableProperties.Width = self.han_program.MiliToHwpUnit(148)
		self.han_program.HAction.Execute("TableCreate", self.han_program.HParameterSet.HTableCreation.HSet)

	def page_break(self):
		"""
		페이지 바꾸기

		:return:
		"""
		self.han_program.HAction.Run("BreakPage")  # 쪽나눔

	def paint_border_for_selection_with_pen(self):
		"""
		형광펜

		:return:
		"""
		self.select_current_line()
		action_obj = self.han_program.CreateAction("MarkPenShape")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("Color", 65535)
		action_obj.Execute(parameter_set_obj)

	def paint_font_red_color_for_selection(self):
		"""
		선택영역을 빨간색으로 칠하기

		:return:
		"""
		self.han_program.HAction.Run("CharShapeTextColorRed")  # 선택한 텍스트의 색을 빨간색으로 만든다

	def paint_highlight_for_selection(self):
		"""
		형광펜

		:return:
		"""
		self.select_current_line()
		action_obj = self.han_program.CreateAction("MarkPenShape")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("Color", 65535)
		action_obj.Execute(parameter_set_obj)

	def paint_table(self):
		"""
		테이블의 색을 칠하는 것

		:return:
		"""
		action_obj = self.han_program.CreateAction("CellFill")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		fillattrSet = parameter_set_obj.CreateItemSet("FillAttr", "DrawFillAttr")

		fillattrSet.SetItem("Type", 1)
		fillattrSet.SetItem("WinBrushFaceStyle", 0xffffffff)
		fillattrSet.SetItem("WinBrushHatchColor", 0x00000000)
		fillattrSet.SetItem("WinBrushFaceColor", self.han_program.RGBColor(153, 153, 153))
		action_obj.Execute(parameter_set_obj)

	def quit(self):
		"""
		종료

		:return:
		"""
		return self.han_program.Quit()

	def read_all_text_for_one_page(self, input_page_no):
		"""
		한페이지의 모든 text를 갖고온다

		:param input_page_no: 페이지 번호
		:return:
		"""
		return self.han_program.GetPageText(pgno=input_page_no)

	def read_table_index_for_selection(self):
		"""
		선택된곳의 테이블의 index값을 갖고온다

		:return:
		"""
		result = None
		if self.selection.Information(12) == False:
			pass
		else:
			lngStart = self.selection.Range.Start
			lngEnd = self.selection.Range.End

			# get the numbers for the END of the selection range
			iSelectionRowEnd = self.selection.Information(14)
			iSelectionColumnEnd = self.selection.Information(17)

			# collapse the selection range
			self.selection.Collapse(Direction=1)

			# get the numbers for the END of the selection range
			# now of course the START of the previous selection
			iSelectionRowStart = self.selection.Information(14)
			iSelectionColumnStart = self.selection.Information(17)

			# RESELECT the same range
			self.selection.MoveEnd(Unit=1, Count=lngEnd - lngStart)

			tabnum = self.active_word_file.Range(0, self.selection.Tables(1).Range.End).Tables.Count

			# display the range of cells covered by the selection
			if self.selection.Cells.Count:
				#print(tabnum, self.selection.Cells.Count, iSelectionRowStart, iSelectionColumnStart, iSelectionRowEnd, iSelectionColumnEnd)
				result = tabnum
		return result

	def read_text_for_current_line(self):
		"""
		현재 커서가 있는 라인의 text를 갖고오는 것

		:return:
		"""
		self.select_current_line()
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_current_para(self):
		"""
		현재 커서가 있는 문단의 text를 갖고오는 것

		:return:
		"""
		self.move_cursor_to_begin_of_current_para()
		self.select_current_para()
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_current_word(self):
		"""
		현재 커서가 있는 단어의 text를 갖고오는 것

		:return:
		"""
		self.select_current_word()
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_all_text_for_doc(self):
		"""
		문서의 모든 text를 갖고오는 것

		:return:
		"""
		self.select_all()
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_nth_char_from_start_of_doc(self, input_no):
		"""
		문서처음에서 n번째 글자를 갖고오는 것

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_char_from_begin_of_doc(input_no)
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_nth_line_from_start_of_doc(self, input_no):
		"""
		문서처음에서 n번째 라인의 text갖고오기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no)
		self.select_current_line()
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_nth_para_from_start_of_doc(self, input_no):
		"""
		문서처음에서 n번째 문단의 text갖고오기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		self.select_nth_para_from_begin_of_doc(input_no)
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_nth_word_from_start_of_doc(self, input_no):
		"""
		문서처음에서 n번째 단어의 text갖고오기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no)
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_para_no(self, input_no):
		"""
		문단번호로 text갖고오기

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		self.select_nth_para_from_begin_of_doc(input_no)
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_from_index1_to_index2(self, input_no1, input_no2):
		"""
		문서처음을 0으로해서, 글자번호 두개사이의 text갖고오기

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no1)
		self.select_nth_char_from_selection(input_no2)
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_for_selection(self):
		"""
		선택영역의 text갖고오기

		:return:
		"""
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_text_in_table_by_xy(self, table_obj, x, y):
		"""
		테이블의 위치로 셀의 text갖고오기

		:param table_obj:
		:param x:
		:param y:
		:return:
		"""
		table_obj.Run("ShapeObjTableSelCell")

		for no in range(y - 1):
			table_obj.Run("TableRightCell")

		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def read_value_for_selection(self):
		"""
		선택영역의 text갖고오기

		:return:
		"""
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def rgb_color(self, red, green, blue):
		"""
		rgb값

		:param red:
		:param green:
		:param blue:
		:return:
		"""
		return self.han_program.RGBColor(red=red, green=green, blue=blue)

	def save(self, file_name=""):
		"""
		저장

		:param file_name:
		:return:
		"""
		self.han_program.SaveAs(file_name)
		self.han_program.Quit()

	def search_action(self, input_action):
		"""
		모든 액션 번호에서 입력받은 단어가 포함된 액션을 찾는 것

		:param input_action:action 이름
		:return:
		"""
		action_name_list = self.check_action_name(input_action)
		for index, a_action in enumerate(action_name_list):
			parameter_set_id = self.get_parameter_name_for_action_name(a_action)
			if parameter_set_id == "없음":
				print(f"{a_action}의 Parameter들은 ==> ", "없음")
			else:
				parameters = self.get_parameters_for_parameter_set_id(parameter_set_id)
				print(f"{a_action}의 Parameter들은 ==> ", parameters)
				for a_parameter in parameters:
					print("                                 Parameter는 ==> ", a_parameter)
					option = self.get_parameter_option_for_paramater_item(a_parameter)
					print("                                             Parameter의 Option은 ==> ", option)

	def select_1st_line_of_selection(self):
		"""
		선택영역의 첫번째 라인을 선택

		:return:
		"""
		self.han_program.HAction.Run('MoveSelLineBegin')

	def select_1st_para_of_selection(self):
		"""
		선택영역의 첫번째 문단을 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelParaBegin")

	def select_1st_word_of_selection(self):
		"""
		선택영역의 첫번째 단어를 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelWordEnd")

	def select_all(self):
		"""
		문서의 모든 것을 선택

		:return:
		"""
		self.han_program.Run('SelectAll')

	def select_char_from_no1_to_no2_from_begin_of_doc(self, input_no1, input_no2):
		"""
		두 글자번호 사이를 선택

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no1)
		self.select_nth_char_from_selection(input_no2 - input_no1)

	def select_current_char(self):
		"""
		현재 선택한것의 첫번째 글자나 공백을 선택한다

		:return:
		"""
		self.move_cursor_to_nth_char_from_selection(0)

	def select_current_line(self):
		"""
		커서가 있는 현재 라인을 선태

		:return:
		"""
		self.select_line_at_current()

	def select_current_para(self):
		"""
		커서가 있는 현재 문단을 선태

		:return:
		"""
		self.select_para_at_current()

	def select_current_word(self):
		"""
		커서가 있는 현재 단어를 선태

		:return:
		"""
		self.select_word_at_current()

	def select_end_of_line_from_selection(self):
		"""
		현재 선택영역에서 줄의 끝까지 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelLineEnd")

	def select_end_of_para_from_selection(self):
		"""
		현재 선택영역에서 문단의 끝까지 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelParaEnd")

	def select_first_cell_of_table(self, table_no):
		"""
		테이블의 처음 셀을 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")

	def select_from_begin_of_doc_to_nth_char(self, input_no):
		"""
		문서의 시작에서부터 n번째 글짜까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_char_from_begin_of_doc(input_no)

	def select_from_begin_of_doc_to_nth_line(self, input_no):
		"""
		문서의 시작에서부터 n번째 줄까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.han_program.Run("Select")
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextLine")
		self.han_program.HAction.Run("MoveSelLineEnd")

	def select_from_begin_of_doc_to_nth_para(self, input_no):
		"""
		문서의 시작에서부터 n번째 문단까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_para_from_selection(input_no)

	def select_from_begin_of_doc_to_nth_word(self, input_no):
		"""
		문서의 시작에서부터 n번째 단어까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no)

	def select_from_char_no1_to_no2_from_begin_of_doc(self, input_no1, input_no2):
		"""
		두 글자번호 사이를 선택

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no1)
		self.select_nth_char_from_selection(input_no2 - input_no1)

	def select_from_cursor_to_nth_char(self, input_no):
		"""
		현재커서에서 n번째 글자까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_char_from_selection(input_no)

	def select_from_cursor_to_nth_word(self, input_no):
		"""
		현재커서에서 n번째 단어까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_selection(input_no - 1)

	def select_from_cursor_to_previous_nth_char(self, input_no):
		"""
		현재커서에서 n번째 앞의 글자까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		for one in range(input_no):
			self.move_cursor_to_previous_char()

	def select_from_cursor_to_previous_nth_word(self, input_no):
		"""
		현재커서에서 n번째 앞의 단어까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_previous_nth_word_from_selection(input_no)
		self.select_current_word()

	def select_from_line_no1_to_no2_from_selection(self, input_no1, input_no2):
		"""
		두 줄사이를 선택

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_selection(input_no1)
		self.select_nth_line_from_selection(input_no2 - input_no1)

	def select_from_para_no1_to_no2_from_selection(self, input_no1, input_no2):
		"""
		두 문단사이를 선택

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.select_nth_para_from_selection(input_no2 - input_no1)

	def select_line_at_current(self):
		"""
		현재 줄을 선택
		# self.han_program.Run("Select")
		# self.han_program.HAction.Run("MoveLineEnd")

		:return:
		"""
		self.move_cursor_to_begin_of_current_line()
		self.han_program.HAction.Run("MoveSelLineEnd")

	def select_line_at_end_of_selection(self):
		"""
		현재 선택영역에서 줄의 끝까지 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelLineEnd")

	def select_line_by_no(self, input_no):
		"""
		줄번호로 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no)
		self.select_current_line()

	def select_line_by_no_from_begin_of_doc(self, input_no):
		"""
		줄번호로 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no - 1)
		self.select_current_line()

	def select_line_from_no1_to_no2_from_selection(self, input_no1, input_no2):
		"""
		두 줄사이를 선택

		:param input_no1:
		:param input_no2:
		:return:
		"""
		self.move_cursor_to_nth_line_from_selection(input_no1)
		self.select_nth_line_from_selection(input_no2 - input_no1)

	def select_line_of_begin_of_selection(self):
		"""
		선택영역의 첫번째 라인을 선택

		:return:
		"""
		self.han_program.HAction.Run('MoveSelLineBegin')

	def select_next_char_from_selection(self, input_no):
		"""
		선택영역에서 n번째 글짜를 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_selection(1)

	def select_next_line_from_selection(self):
		"""
		선택영역에서 다음 줄을 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelNextLine")

	def select_next_para_from_selection(self):
		"""
		선택영역에서 n번째 문단을 선택

		:return:
		"""
		self.move_cursor_to_next_para_from_selection()
		self.select_current_para()

	def select_next_word_from_selection(self):
		"""
		선택영역에서 n번째 단어을 선택

		:return:
		"""
		self.select_nth_word_from_selection(1)

	def select_nth_char_from_begin_of_doc(self, input_no):
		"""
		문서의 시작에서부터 n번째 글짜까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_char_from_begin_of_doc(input_no)

	def select_nth_char_from_begin_of_doc_1(self, input_no):
		"""
		n번째 글자를 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_begin_of_doc(input_no)

	def select_nth_char_from_selection(self, input_no):
		"""
		선택영역에서 n번째 글짜까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_char_from_selection(input_no)

	def select_nth_line_from_begin_of_doc(self, input_no):
		"""
		n번째 줄을 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no)
		self.select_current_line()

	def select_nth_line_from_begin_of_doc_1(self, input_no):
		"""
		문서의 시작에서부터 n번째 줄까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.han_program.Run("Select")
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextLine")
		self.han_program.HAction.Run("MoveSelLineEnd")

	def select_nth_line_from_cursor(self, input_no):
		"""
		선택영역에서 n번째 줄까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		for one in range(input_no):
			self.han_program.HAction.Run("MoveNextLine")
		self.select_current_line()

	def select_nth_line_from_selection(self, input_no):
		"""
		선택영역에서 n번째 글짜까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveSelNextLine")

	def select_nth_para_from_begin_of_doc(self, input_no):
		"""
		n번째 문단을 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_para_from_begin_of_doc(input_no - 1)
		self.select_current_para()

	def select_nth_para_from_begin_of_doc_1(self, input_no):
		"""
		문서의 시작에서부터 n번째 문단까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_para_from_selection(input_no)

	def select_nth_para_from_selection(self, input_no):
		"""
		선택영역에서 n번째 문단을 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.move_cursor_to_nth_para_from_selection(input_no)
		self.select_current_para()

	def select_nth_word_from_begin_of_doc(self, input_no):
		"""
		n번째 단어를 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no)

	def select_nth_word_from_begin_of_doc_1(self, input_no):
		"""
		문서의 시작에서부터 n번째 단어까지 선택

		:param input_no: 숫자(정수)
		:return:
		"""
		self.select_nth_word_from_begin_of_doc(input_no)

	def select_nth_word_from_selection(self, input_no):
		"""
		선택영역에서 n번째 단어를 선택

		:return:
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MoveNextWord")
		self.han_program.HAction.Run("MoveSelNextWord")

	def select_para_at_current(self):
		"""
		현재 문단 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveParaBegin")
		self.han_program.Run("Select")
		self.han_program.HAction.Run("MoveParaEnd")

	def select_para_at_end_of_selection(self):
		"""
		현재 선택영역에서 문단의 끝까지 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelParaEnd")

	def select_para_from_no1_to_no2_from_selection(self, input_no1, input_no2):
		"""
		두 문단사이를 선택

		:param input_no1: 숫자(정수)
		:param input_no2: 숫자(정수)
		:return:
		"""
		self.select_nth_para_from_selection(input_no2 - input_no1)

	def select_para_of_begin_of_selection(self):
		"""
		선택영역의 첫번째 문단을 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelParaBegin")

	def select_previous_char_from_selection(self):
		"""
		선택영역에서 앞으로 n번째 글자를 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelPrevPos")

	def select_previous_line_from_selection(self):
		"""
		선택영역에서 앞 줄을 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelLineUp")

	def select_previous_nth_line_from_selection(self, input_no):
		"""
		선택영역에서 앞으로 n번째 줄을 선택
		
		:param input_no: 숫자(정수)
		:return: 
		"""
		for no in range(input_no):
			self.han_program.HAction.Run("MovePrevLine")

	def select_previous_nth_para_from_selection(self):
		"""
		선택영역에서 앞으로 n번째 문단을 선택

		:return:
		"""
		self.move_cursor_to_previous_nth_para_from_selection(1)
		self.select_current_para()

	def select_previous_nth_word_from_selection(self):
		"""
		선택영역에서 앞으로 n번째 단어를 선택

		:return:
		"""
		self.move_cursor_to_previous_nth_word_from_selection(1)
		self.select_current_word()

	def select_previous_para_from_selection(self):
		"""
		선택영역에서 앞 문단을 선택

		:return:
		"""
		self.han_program.HAction.Run("MovePrevPara")
		self.han_program.HAction.Run("MoveParaBegin")
		self.han_program.Run("Select")
		self.han_program.HAction.Run("MoveParaEnd")

	def select_previous_word_from_selection(self):
		"""
		선택영역에서 앞 단어를 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelPrevWord")

	def select_start(self):
		"""
		선택 시작

		:return:
		"""
		self.han_program.HAction.Run("Select")

	def select_start_of_list_from_selection(self):
		"""
		선택영역의 리스트의 시작 번호

		:return:
		"""
		self.han_program.HAction.Run('MoveSelListBegin')

	def select_table_obj_by_no(self, input_no):
		"""
		한글에서는 객체를 넘겨주는 부분이 아니고
		원하는 객체를 문서 젠체에서 사용가능한 선택을 하고, 다른곳에서 선택한것을 가지고 무엇인가 한다

		:param input_no: 숫자(정수)
		:return:
		"""
		ctrl = self.han_program.HeadCtrl  # 첫번째 컨트롤(HaedCtrl)부터 탐색 시작.
		count = 0
		while ctrl != None:
			nextctrl = ctrl.Next
			if ctrl.CtrlID == "tbl":
				count += 1
				if input_no == count:
					self.han_program.SetPosBySet(ctrl.GetAnchorPos(0))
					self.han_program.FindCtrl()  # 객체를 선택하는 것
					break
			ctrl = nextctrl

	def select_word_at_current(self):
		"""
		현재 단어 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveWordBegin")
		self.han_program.Run("Select")
		self.han_program.HAction.Run("MoveWordEnd")

	def select_word_from_no1_to_no2_from_begin_of_doc(self, input_no1, input_no2):
		"""
		두 글자번호 사이를 선택

		:param input_no1:
		:param input_no2:
		:return:
		"""
		self.move_cursor_to_nth_word_from_begin_of_doc(input_no1)
		self.select_nth_word_from_selection(input_no2 - input_no1)

	def select_word_of_begin_of_selection(self):
		"""
		선택영역의 첫번째 단어를 선택

		:return:
		"""
		self.han_program.HAction.Run("MoveSelWordEnd")

	def select_xline_in_table(self, table_no, x_no):
		"""
		선택한 테이블의 n번째 가로줄 선택

		:param table_no: 테이블 번호
		:param x_no:
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")
		for no in range(x_no - 1):
			self.han_program.Run("TableLowerCell")
		self.han_program.CreateAction("SelectRow")

	def select_yline_in_table(self, table_no, y):
		"""
		선택한 테이블의 n번째 세로줄 선택

		:param table_no: 테이블 번호
		:param y:
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")
		for no in range(y - 1):
			self.han_program.Run("TableRightCell")
		self.han_program.CreateAction("SelectColumn")

	def selection_value(self):
		"""
		선택영역의 텍스트

		:return:
		"""
		result = self.han_program.GetTextFile("TEXT", "saveblock")
		return result

	def set_alignment_left_for_current_para(self):
		"""
		왼쪽 정렬

		:return:
		"""
		self.han_program.HAction.Run("ParagraphShapeAlignLeft")

	def set_basic_font_style(self, **input_dic):
		"""

		:param input_dic:
		:return:
		"""
		colorx = xy_color.xy_color()
		self.varx["han"]["apply_basic_font"] = True

		if "size" in input_dic.keys():
			self.varx["han"]["basic_size"] = input_dic["size"]
		if "color" in input_dic.keys():
			self.varx["han"]["rgb_int"] = colorx.change_xcolor_to_rgbint(input_dic["color"])
		if "bold" in input_dic.keys():
			self.varx["han"]["basic_bold"] = True
		if "underline" in input_dic.keys():
			self.varx["han"]["basic_underline"] = True
		if "italic" in input_dic.keys():
			self.varx["han"]["basic_italic"] = True

	def set_cur_field_name(self, field_name):
		"""
		현재 캐럿이 있는 곳의 필드이름을 설정

		:param field_name:
		:return:
		"""
		return self.han_program.SetCurFieldName(Field=field_name)

	def set_font_bold_for_selection(self):
		"""
		진하게 적용

		:return:
		"""
		self.han_program.HAction.Run("CharShapeBold")

	def set_font_border_for_selection(self):
		"""
		테두리 그리기

		:return:
		"""
		self.han_program.CreateAction("CharShapeOutline")

	def set_font_center_for_selection(self):
		"""
		가운데 정렬

		:return:
		"""
		self.han_program.HAction.Run("ParagraphShapeAlignCenter")

	def set_font_color_as_red_for_selection(self):
		"""
		글자를 빨간색으로 색칠하기
		선택한 텍스트의 색을 빨간색으로 만든다

		:return:
		"""
		self.han_program.HAction.Run("CharShapeTextColorRed")

	def set_font_color_for_selection_by_rgb(self, input_rgb):
		"""
		선택영역 rgb값으로 색칠하기

		:param input_rgb: rgb값
		:return:
		"""
		rgb_value = self.han_program.RGBColor(red=input_rgb[0], green=input_rgb[1], blue=input_rgb[2])
		action_obj = self.han_program.CreateAction("CharShape")
		cs = action_obj.CreateSet()
		action_obj.GetDefault(cs)
		cs.SetItem("TextColor", rgb_value)
		action_obj.Execute(cs)

	def set_font_color_for_selection_by_xcolor(self, input_xcolor):
		"""
		선택영역 xcolor형식으로 색칠하기

		:param input_xcolor: xcolor형식의 색깔
		:return:
		"""
		colorx = xy_color.xy_color()
		input_rgb = colorx.change_xcolor_to_rgb(input_xcolor)
		self.set_font_color_for_selection_by_rgb(input_rgb)

	def set_font_left_for_selection(self):
		"""
		왼쪽 정렬

		:return:
		"""
		self.han_program.HAction.Run("ParagraphShapeAlignLeft")

	def set_font_right_for_selection(self):
		"""
		오른쪽 정렬

		:return:
		"""
		self.han_program.HAction.Run("ParagraphShapeAlignRight")

	def set_font_shadow_for_selection(self):
		"""
		그림자

		:return:
		"""
		self.han_program.HAction.Run("CharShapeShadow")

	def set_font_size_down_for_selection(self, input_step=1):
		"""
		폰트크기 n단계 줄이기

		:param input_step:
		:return:
		"""
		for no in range(input_step):
			self.han_program.HAction.Run("CharShapeHeightDecrease")

	def set_font_size_up_for_selection(self, input_step=1):
		"""
		폰트크기 n단계 키우기

		:param input_step:
		:return:
		"""
		for no in range(input_step):
			self.han_program.HAction.Run("CharShapeHeightIncrease")

	def set_font_strikethrough_for_selection(self):
		"""
		선택영역의 글자들에 대해서 취소선

		:return:
		"""
		self.han_program.CreateAction("CharShapeCenterline")

	def set_font_style_for_selection(self, my_range):
		"""
		선택영역의 글자들에 대해서 폰트 스타일을 설정하는것

		:param my_range:
		:return:
		"""
		if self.varx["han"]["basic_underline"]:
			my_range.Font.Underline = 1
		if self.varx["han"]["basic_size"]:
			my_range.Font.Size = self.varx["han"]["basic_size"]
		if self.varx["han"]["basic_bold"]:
			my_range.Font.Bold = 1
		if self.varx["han"]["rgb_int"]:
			my_range.Font.TextColor.RGB = self.varx["han"]["rgb_int"]

	def set_font_underline_for_selection(self):
		"""
		선택영역의 글자들에 대해서 밑줄적용

		:return:
		"""
		self.han_program.CreateAction("CharShapeUnderline")

	def set_pos_for_cursor(self, input_list, input_para, input_pos):
		"""
		현재 커서의 아래 정보를 설정하는 것
		list : 캐럿이 위치한 문서내 리스트 ID
		para : 캐럿이 위치한 문단 번호
		pso : 캐럿이 위치한 문단내 글자위치
		
		:param input_list: 
		:param input_para: 
		:param input_pos: 
		:return: 
		"""
		result = self.han_program.SetPos(input_list, input_para, input_pos)
		return result

	def set_table_cell_address(self, addr):
		"""
		셀번호를 a1형태로 돌려준다

		:param addr:
		:return:
		"""
		init_addr = self.han_program.KeyIndicator()[-1][1:].split(")")[0]  # 함수를 실행할 때의 주소를 기억.
		if not self.han_program.CellShape:  # 표 안에 있을 때만 CellShape 오브젝트를 리턴함
			raise AttributeError("현재 캐럿이 표 안에 있지 않습니다.")
		if addr == self.han_program.KeyIndicator()[-1][1:].split(")")[0]:  # 시작하자 마자 해당 주소라면
			return  # 바로 종료
		self.han_program.HAction.Run("CloseEx")  # 그렇지 않다면 표 밖으로 나가서
		self.han_program.FindCtrl()  # 표를 선택한 후
		self.han_program.HAction.Run("ShapeObjTableSelCell")  # 표의 첫 번째 셀로 이동함(A1으로 이동하는 확실한 방법 & 셀선택모드)
		while True:
			current_addr = self.han_program.KeyIndicator()[-1][1:].split(")")[0]  # 현재 주소를 기억해둠
			self.han_program.HAction.Run("TableRightCell")  # 우측으로 한 칸 이동(우측끝일 때는 아래 행 첫 번째 열로)
			if current_addr == self.han_program.KeyIndicator()[-1][1:].split(")")[0]:  # 이동했는데 주소가 바뀌지 않으면?(표 끝 도착)
				# == 한 바퀴 돌았는데도 목표 셀주소가 안 나타났다면?(== addr이 표 범위를 벗어난 경우일 것)
				self.set_table_cell_address(init_addr)  # 최초에 저장해둔 init_addr로 돌려놓고
				self.han_program.HAction.Run("Cancel")  # 선택모드 해제
				raise AttributeError("입력한 셀주소가 현재 표의 범위를 벗어납니다.")
			if addr == self.han_program.KeyIndicator()[-1][1:].split(")")[0]:  # 목표 셀주소에 도착했다면?
				return  # 함수 종료

	def write_text_at_begin_of_line_no(self, input_no, input_text):
		"""
		줄번호의 시작에 텍스트입력

		:param input_no: 숫자(정수)
		:param input_text: 입력 문자
		:return:
		"""
		self.move_cursor_to_begin_of_doc()
		self.move_cursor_to_nth_line_from_begin_of_doc(input_no)
		self.move_cursor_to_begin_of_current_line()
		self.write_text_at_cursor(input_text, True)

	def write_text_at_begin_of_selection(self, input_value):
		"""
		선택영역 시작에 텍스트입력

		:param input_value: 입력값
		:return:
		"""
		self.move_cursor_to_begin_of_selection()
		self.write_text_at_cursor(input_value)

	def write_text_at_cursor(self, input_value, next_line=False):
		"""
		커서위치에 텍스트입력

		:param input_value: 입력값
		:param next_line:
		:return:
		"""
		try:
			changed_text = input_value.split("\n")
			for one_text in changed_text:
				action_obj = self.han_program.CreateAction("InsertText")
				parameter_set_obj = action_obj.CreateSet()
				parameter_set_obj.SetItem("Text", one_text)
				action_obj.Execute(parameter_set_obj)
				if next_line:
					self.han_program.Run("BreakLine")
		except:
			pass

		self.han_program.HAction.GetDefault("InsertText", self.han_program.HParameterSet.HInsertText.HSet)
		#self.han_program.HParameterSet.HInsertText.Text = "개는 멍멍멍"
		#self.han_program.HAction.Execute("InsertText", self.han_program.HParameterSet.HInsertText.HSet)

	def write_text_at_end_of_doc(self, input_text, new_line=False):
		"""
		문서의 끝에 텍스트입력

		:param input_text: 입력 문자
		:param new_line:
		:return:
		"""
		self.move_cursor_to_end_of_doc()
		self.write_text_at_cursor(input_text, new_line)

	def write_text_at_end_of_selection(self, input_text):
		"""
		선택영역의 끝에 텍스트입력

		:param input_text: 입력 문자
		:return:
		"""
		self.move_cursor_to_end_of_selection()
		self.write_text_at_cursor(input_text)

	def write_text_at_nth_cell_in_table(self, table_no, cell_no, input_text):
		"""
		테이블의 순번째에 텍스트입력

		:param table_no: 테이블 번호
		:param cell_no: 셀번호
		:param input_text: 입력 문자
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")
		for no in range(cell_no - 1):
			self.han_program.Run("TableRightCell")

		self.write_text_at_cursor(input_text)

	def write_text_at_start_of_selection(self, input_text):
		"""
		선택영역의 처음에 텍스트입력

		:param input_text: 입력 문자
		:return:
		"""
		self.move_cursor_to_begin_of_selection()
		self.write_text_at_cursor(input_text)

	def write_text_in_table_by_xy(self, table_no, x, y, input_text, next_line=True):
		"""
		선택영역의 처음에 텍스트입력

		:param table_no: 테이블 번호
		:param x:
		:param y:
		:param input_text: 입력 문자
		:param next_line:
		:return:
		"""
		self.select_table_obj_by_no(table_no)
		self.han_program.Run("ShapeObjTableSelCell")
		for no in range(x - 1):
			self.han_program.Run("TableLowerCell")

		for no in range(y - 1):
			self.han_program.Run("TableRightCell")
		self.write_text_at_cursor(input_text, next_line)

	def write_text_with_new_line_at_end_of_doc(self, input_text):
		"""
		문서의 끝에 새로운 라인으로 텍스트입력

		:param input_text: 입력 문자
		:return:
		"""
		self.move_cursor_to_end_of_doc()
		self.insert_next_line_at_cusor()
		self.write_text_at_cursor(input_text)

	def write_value_at_end_of_para_no(self, input_text):
		"""
		특정 문단의 끝에 텍스트입력

		:param input_text: 입력 문자
		:return:
		"""
		self.move_cursor_to_end_of_current_para()
		self.write_text_at_cursor(input_text)

	def zzz_test_001(self):
		"""
		HwpCtrl API를 사용한 경우

		:return:
		"""
		action_obj = self.han_program.CreateAction("InsertText")
		parameter_set_obj = action_obj.CreateSet()
		parameter_set_obj.SetItem("Text", "가나다라마바사아")
		action_obj.Execute(parameter_set_obj)

		# HAction을 사용한 경우
		self.han_program.HAction.GetDefault("InsertText", self.han_program.HParameterSet.HInsertText.HSet)
		self.han_program.HParameterSet.HInsertText.Text = "123456789"
		self.han_program.HAction.Execute("InsertText", self.han_program.HParameterSet.HInsertText.HSet)

	def paint_background_for_selection_by_xcolor(self, input_xcolor="red50"):
		"""
		색칠하기 : 선택영역을 빨간색으로 칠하기

		:return:
		"""
		colorx = xy_color.xy_color()

		input_rgb = colorx.change_xcolor_to_rgb(input_xcolor)
		rgb_value = self.han_program.RGBColor(red=input_rgb[0], green=input_rgb[1], blue=input_rgb[2])

		action_obj = self.han_program.CreateAction("MarkPenShape")
		parameter_set_obj = action_obj.CreateSet()
		action_obj.GetDefault(parameter_set_obj)
		parameter_set_obj.SetItem("Color", rgb_value)
		action_obj.Execute(parameter_set_obj)

	def paint_font_for_selection_by_xcolor(self, input_xcolor="red50"):
		"""
		선택영역 xcolor형식으로 색칠하기

		:param input_xcolor: xcolor형식의 색깔
		:return:
		"""
		colorx = xy_color.xy_color()
		input_rgb = colorx.change_xcolor_to_rgb(input_xcolor)
		self.set_font_color_for_selection_by_rgb(input_rgb)
		"""
		hwp.set_font()의 파라미터 목록

		
		DiacSymMark: 강조점(0~12)
		Emboss: 양각(True/False)
		Engrave: 음각(True/False)
		FaceName: 서체 이름
		FontType: 1(TTF, 기본값)
		Height: 글자크기(pt, 0.1 ~ 4096)
		
		Offset: 글자위치-상하오프셋(-100 ~ 100)
		OutLineType: 외곽선타입(0~6)
		Ratio: 장평(50~200)
		ShadeColor: 음영색(RGB, 0x000000 ~ 0xffffff) ~= hwp.rgb_color(255,255,255), 취소는 0xffffffff(4294967295)
		ShadowColor: 그림자색(RGB, 0x0~0xffffff) ~= hwp.rgb_color(255,255,255), 취소는 0xffffffff(4294967295)
		ShadowOffsetX: 그림자 X오프셋(-100 ~ 100)
		ShadowOffsetY: 그림자 Y오프셋(-100 ~ 100)
		ShadowType: 그림자 유형(0: 없음, 1: 비연속, 2:연속)
		Size: 글자크기 축소확대%(10~250)
		Spacing: 자간(-50 ~ 50)
		StrikeOutColor: 취소선 색(RGB, 0x0~0xffffff) ~= hwp.rgb_color(255,255,255), 취소는 0xffffffff(4294967295)
		StrikeOutShape: 취소선 모양(0~12, 0이 일반 취소선)
		StrikeOutType: 취소선 유무(True/False)
		SubScript: 아래첨자(True/False)
		SuperScript: 위첨자(True/False)
		TextColor: 글자색(RGB, 0x0~0xffffff) ~= hwp.rgb_color(255,255,255), 기본값은 0xffffffff(4294967295)
		UnderlineColor: 밑줄색(RGB, 0x0~0xffffff) ~= hwp.rgb_color(255,255,255), 기본값은 0xffffffff(4294967295)
		UnderlineShape: 밑줄형태(0~12)
		UnderlineType: 밑줄위치(0:없음, 1:하단, 3:상단)
		UseFontSpace: 글꼴에 어울리는 빈칸 적용여부(True/False)
		"""

	def set_font_underline_for_selection_with_xcolor(self, input_xcolor="bla", underline_position = 1):
		"""
		선택영역 rgb값으로 색칠하기

		:param input_xcolor:  xcolor형식의 색깔
		:param underline_position:
		:return:
		"""
		colorx = xy_color.xy_color()
		input_rgb = colorx.change_xcolor_to_rgb(input_xcolor)
		rgb_value = self.han_program.RGBColor(red=input_rgb[0], green=input_rgb[1], blue=input_rgb[2])

		action_obj = self.han_program.CreateAction("CharShape")
		cs = action_obj.CreateSet()
		action_obj.GetDefault(cs)
		cs.SetItem("UnderlineType", underline_position)
		cs.SetItem("UnderlineColor", rgb_value)
		action_obj.Execute(cs)

	def replace_all_in_doc(self, input_text, replace_text):
		"""
		바꾸기 : 문서안의 모든것을 바꾸는 것

		:param input_text: 입력 문자
		:param replace_text: 바꿀 문자
		:return:
		"""
		pset = self.han_program.HParameterSet.HFindReplace
		pset.Direction = self.han_program.FindDir("AllDoc")
		pset.FindString = input_text
		pset.ReplaceString = replace_text
		pset.IgnoreMessage = 1
		self.han_program.HAction.Execute("AllReplace", pset.HSet)

	def replace_one_time_in_doc(self, input_text, replace_text):
		"""
		바꾸기 : 문서에서 찾은것을 1번만 바꾸기

		:param input_text: 찾을 문자
		:param replace_text: 바꿀 문자
		:return: 
		"""
		pset = self.han_program.HParameterSet.HFindReplace
		pset.Direction = 0 # 0: 아래쪽
		pset.FindString = input_text
		pset.ReplaceString = replace_text
		pset.IgnoreMessage = 1
		self.han_program.HAction.Execute("ExecReplace", pset.HSet)

	def find_one_time_in_doc(self, input_text):
		"""
		찾기 : 현재 커서의 우치에서 아래쪽으로 입력문자를 찾는 것

		:param input_text: 찾을 문자
		:return:
		"""

		action_obj = self.han_program.CreateAction("ReverseFind")
		cs = action_obj.CreateSet()
		action_obj.GetDefault(cs)
		cs.SetItem("Direction", 1)
		cs.SetItem("FindString", input_text)
		cs.SetItem("IgnoreMessage", 1)
		action_obj.Execute(cs)
		"""
		아래와같은 형식으로 도 가능하다
		pset = self.han_program.HParameterSet.HFindReplace
		pset.Direction = 2 # 0: 아래쪽, 2:문서전체
		pset.FindString = input_text
		pset.IgnoreMessage = 1
		self.han_program.HAction.Execute("BackwardFind", pset.HSet)
		"""

	def get_font_bold_for_selection(self):
		"""
		Bold: 진하게 적용(True/False)

		:return:
		"""
		result = self.han_program.CharShape.Item("Bold")
		return result

	def get_font_italic_for_selection(self):
		"""
		Italic: 이탤릭(True/False)

		:return:
		"""
		result = self.han_program.CharShape.Item("Italic")
		return result

	def get_font_underline_for_selection(self):
		"""
		UnderlineType: 밑줄위치(0:없음, 1:하단, 3:상단)

		:return:
		"""
		result = self.han_program.CharShape.Item("UnderlineType")
		return result

	def get_font_color_for_selection(self):
		"""
		TextColor: 글자색(RGB, 0x0~0xffffff) ~= hwp.rgb_color(255,255,255), 기본값은 0xffffffff(4294967295)

		:return:
		"""
		result = self.han_program.CharShape.Item("TextColor")
		return result

	def get_font_name_for_selection(self):
		"""
		FaceNameHangul: 한글폰트이름
		FaceNameLatin: 영어폰트이름

		:return:
		"""
		result1 = self.han_program.CharShape.Item("FaceNameHangul")
		result2 = self.han_program.CharShape.Item("FaceNameLatin")
		return [result1,result2]

	def insert_picture_at_selection_end(self, file_full_name="D:/my_code/icons/bibi2.png", input_w=100, input_h=100):
		"""
		이미지 삽입
		
		:param file_full_name: 파일이름
		:param input_w: 이미지의 넒이
		:param input_h: 이미지의 높이
		:return: 
		"""
		self.han_program.InsertPicture(file_full_name, Embedded=True,  sizeoption=1, width=input_w, height=input_h)  


	def set_page_no_at_header(self, left_text="", right_start_no=1):
		"""
		
		:param left_text: 
		:param right_start_no: 
		:return: 
		"""
		action_obj = self.han_program.CreateAction("InsertPageNum")
		#parameter_set_obj = action_obj.CreateSet()
		#action_obj.GetDefault(parameter_set_obj)
		#parameter_set_obj.SetItem("Color", rgb_value)
		#action_obj.Execute(parameter_set_obj)

	def write_today_at_cursor(self):
		"""
		현재 커서에 yyyy-mm-dd를 넣는 것

		:return:
		"""
		timex = xy_time.xy_time()
		yyyymmdd = timex.get_yyyy_mm_dd_for_today()
		self.write_text_at_cursor(yyyymmdd)


	def set_page_with_margin(self, input_left=15, input_right=15):
		"""
		왼쪽과 오른쪽의 마진을 설정하는 것
		
		:param input_left: 왼쪽 마진용 숫자
		:param input_right: 오른쪽 마진용 숫자
		:return:
		"""
		action_obj = self.han_program.CreateAction("PageSetup")
		cs = action_obj.PageDef.CreateSet()
		cs.SetItem("LeftMargin", input_left)
		cs.SetItem("RightMargin", input_right)

		"""
		Act = hwp.CreateAction("PageSetup")
		Set = Act.CreateSet()
		Act.GetDefault(Set)
		Set.SetItem("ApplyTo", 3)  # 2:현재구역, 3:문서전체, 4:새구역으로
		Pset = Set.CreateItemSet("PageDef", "PageDef")
		Pset.SetItem("TopMargin", 0)
		Pset.SetItem("BottomMargin", 0)
		Pset.SetItem("LeftMargin", hwp.MiliToHwpUnit(30))
		Pset.SetItem("RightMargin", hwp.MiliToHwpUnit(30))
		Pset.SetItem("HeaderLen", 0)
		Pset.SetItem("FooterLen", 0)
		Pset.SetItem("GutterLen", 0)
		"""

	def find(self, input_text):
		"""
		찾기
		
		:param input_text: 찾을 문자
		:return: 
		"""

		action_obj = self.han_program.CreateAction("RepeatFind")
		cs = action_obj.CreateSet()
		action_obj.GetDefault(cs)
		cs.SetItem("Direction", self.han_program.FindDir("Forward")) # 1 : self.han_program.FindDir("Forward")
		cs.SetItem("FindString", input_text)
		cs.SetItem("IgnoreMessage", 1)
		cs.SetItem("FindType", 1)
		action_obj.Execute(cs)
		print(self.han_program.GetPos())
