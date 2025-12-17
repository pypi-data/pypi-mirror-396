# -*- coding: utf-8 -*-
import sys, datetime #내장모듈
import pickle, win32clipboard, csv
import pyperclip

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCore import QCoreApplication
import xy_color


colorx = xy_color.xy_color()

# 테이블용 기본 자료
general_setup =  {"basic_color": [217, 217, 217],
					  "color": "",
					  "copy_items": [],
					  "grid_x_len": 500,
					  "grid_y_len": 100,
					  "window_title": "Grid_Man",
					  "background_color": [123, 123, 123],
					  "grid_height": 25,
					  "grid_width": 50,
					  }

empty_dic = {"kind_1": None, "kind_2":None, "value": None, "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None}

# 테이블에 나타날 자료
dic_2d = {2:{
			1:{"kind_1": "basic", "kind_2":"date", "value": "=today()", "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			2:{"kind_1": "memo",  "kind_2":None,   "value": "memo memo", "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			3:{"kind_1": "basic", "kind_2":"basic", "value": None, "text": "값", "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			5:{"kind_1": "basic", "kind_2":"basic", "value": None, "text": "값", "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			6:{"kind_1": "tool_tip","kind_2":None, "value": None, "text": "tool_tip", "tool_tip": "툴팁입니다", "caption": None, "action":None, "draw_line":None, "line_detail":None},
			7:{"kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2), "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None}},
	5 :{
			3:{"kind_1": "widget", "kind_2":"combo", "value": [1, 2, 3, 4, 5], "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			5:{"kind_1": "widget", "kind_2": "check_box", "value": None, "checked": 1, "text":"check", "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			7:{"kind_1": "widget", "kind_2":"progress_bar", "value": 30, "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			8:{"kind_1": "widget", "kind_2":"button", "value": None, "text": None, "tool_tip": None, "caption": "button_1", "action":"action_def", "draw_line":None, "line_detail":None}},
	7:{
			3:{"kind_1": "font_color",  "kind_2":None, "value": [255, 63, 24], "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			5:{"kind_1": "background_color", "kind_2": None, "value": [255, 63, 24], "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None},
			6:{"kind_1": "background_color", "kind_2": None, "value": [250, 234, 214],       "text": None, "tool_tip": None, "caption": None, "action": None, "draw_line": None, "line_detail": None},
			1: {"kind_1": "background_color", "kind_2": None, "value": "blu89", "text": None, "tool_tip": None, "caption": None, "action": None, "draw_line": None, "line_detail": None},
	},
	8:{
			8:{"kind_1": None,"kind_2":None, "value": None, "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":"yes", "line_detail":{"line_top_dic": {"do": "yes", "color": Qt.GlobalColor.blue, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }}},
			9:{"kind_1": None,"kind_2":None, "value": None, "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line": "yes", "line_detail":{"line_top_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }}}},
	10:{
			10:{"kind_1": "memo","kind_2":None, "value": "memo memo", "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None }},
}


class data_connect_with_table_model(QAbstractTableModel):
	# 실제자료가 grid에 나타날수있도록 connection을 만든다
	def __init__(self, all_data, title_names, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self.dic_2d = all_data
		self.header_title_l1d = title_names

	def rowCount(self, parent: QModelIndex = ...) -> int:
		first_key = list(self.dic_2d.keys())[0]
		second_key = list(self.dic_2d[first_key].keys())[0]
		len_dic = len(self.dic_2d[first_key][second_key].keys())
		return len_dic

	def columnCount(self, parent: QModelIndex = ...) -> int:
		total = 0
		all_keys = list(self.dic_2d.keys())
		for one_key in all_keys:
			total = total + len(list(self.dic_2d[one_key].keys()))
		return total

	def data(self, index, role=Qt.DisplayRole):
		"""
		각 셀별로 자료를 표현할 때마다 이것이 실행되는 것이다
		모든 것을 각 셀마다 다르게 설정할수가 있다
		화면을 움직이거나 하면 매번 다시 실행된다
		:param index:
		:param role:
		:return:
		"""
		x = index.row()
		y = index.column()
		
		if x in self.dic_2d.keys():
			if y in self.dic_2d[x].keys():
				cell_data = self.dic_2d[x][y]
				if role == Qt.DisplayRole:
					# 0 : 문자를 표현하는 방법 (QString)
					try:
						if cell_data["kind_2"] == "date" and cell_data["value"] == "=today()":
							return "2022-08-20"
						elif type(cell_data["text"]) == type(1):
							return "숫자 : " + str(cell_data["text"])

						elif cell_data["kind_2"] == "date" and isinstance(cell_data["value"], datetime.datetime):
							return cell_data["value"].strftime('%Y-%m-%d')
						else:
							if cell_data["kind_1"] == "basic":
								#print(x, y, cell_data["text"])
								return cell_data["text"]
					except:
						#print("error", "Qt.DisplayRole:", cell_data)
						pass

				if role == Qt.DecorationRole:
					# 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)
					try:

						if cell_data["kind_2"] == "date" and isinstance(cell_data["value"], datetime.datetime):
							return QIcon('calendar.png')
						elif cell_data["kind_2"] == "date" and cell_data["value"] == "=today()":
								return QIcon('calendar.png')
						elif str(cell_data["text"]) == "=":
							return QIcon('calendar.png')
					except:
						pass

				if role == Qt.EditRole:
					# 2   The data in a form suitable for editing in an editor. (QString)
					# 수정할때 나타나는 것
					return cell_data["text"]

				if role == Qt.ToolTipRole:
					# 3   각 셀마다 툴팁을 설정할수있는것. (QString)
					try:
						if cell_data["kind_1"] == "tool_tip":
							return cell_data["tool_tip"]
					except:
						#print("툴팁에러")
						pass
				if role == Qt.StatusTipRole:
					# 4   status bar에 나타나는것 (QString)
					pass

				if role == Qt.WhatsThisRole:
					# 5   The data displayed for the item in "What's This?" mode. (QString)
					pass

				if role == Qt.FontRole:
					# 6   The font used for items rendered with the default delegate. (QFont)
					font = QFont()
					font.setPixelSize(12)
					return font
					#return Qt.QVariant(font)

				if role == Qt.TextAlignmentRole:
					# 7   The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
					#return Qt.QVariant(int(Qt.AlignLeft | Qt.AlignBottom))
					return int(Qt.AlignLeft | Qt.AlignBottom)

				if role == Qt.BackgroundRole:
					#배경색을 칠하는 부분
					# 8   The background brush used for items rendered with the default delegate. (QBrush)
					try:
						if cell_data["kind_1"] == "background_color":
							if type(cell_data["value"]) == type("abc"):

								acolor = colorx.change_xcolor_to_rgb(cell_data["value"])

								#print("----> ", acolor)
							else:
								#print(cell_data["value"])
								acolor = cell_data["value"]
						return QColor(acolor[0], acolor[1], acolor[2])
					except:
						pass

				if role == Qt.ForegroundRole:
					try:
						# 9   The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
						font_color = cell_data["font_dic"]["color"]
						if font_color:
							return Qt.QVariant(QColor(font_color[0], font_color[1], font_color[2]))
					except:
						pass

				if role == Qt.CheckStateRole:
					# 10  This role is used to obtain the checked state of an item. (Qt.CheckState)
					pass
				#	if self.dic_2d[row][column].isChecked():
				#		return QVariant(Qt.Checked)
				#	else:
				#		return QVariant(Qt.Unchecked)

				if role == Qt.AccessibleTextRole:
					# 11  The text to be used by accessibility extensions and plugins, such as screen readers. (QString)
					pass

				if role == Qt.AccessibleDescriptionRole:
					# 12  A description of the item for accessibility purposes. (QString)
					pass

				if role == Qt.SizeHintRole:
					# 13  The size hint for the item that will be supplied to views. (QSize)
					pass

				if role == Qt.InitialSortOrderRole:
					# 14  This role is used to obtain the initial sort order of a header view section. (Qt.SortOrder). This role was introduced in Qt 4.8.
					pass

				if role == Qt.UserRole:
					# 32  The first role that can be used for application-specific purposes.
					pass



	def setData(self, index, value, role=Qt.EditRole):
		"""
		셀에서 값을 바꾸면 실행되는 코드
		editor가 실행을 마치고 넘어오는 value값이 저장되는 것이다
		"""
		x = index.row()
		y = index.column()
		print("setData ===> ")

		if not x in self.dic_2d.keys():
			self.dic_2d[x]={}
		if not y in self.dic_2d[x].keys():
			self.dic_2d[x][y] = {"kind_1": None, "kind_2":None, "value": None, "text": None, "tool_tip": None, "caption": None, "action":None, "draw_line":None, "line_detail":None}
			self.dic_2d[x][y]["text"] = value
			self.dic_2d[x][y]["kind_1"] = "basic"
			print(self.dic_2d[x][y])

		if x in self.dic_2d.keys():
			if y in self.dic_2d[x].keys():
				cell_data = self.dic_2d[x][y]

				if role == Qt.EditRole:
					try:
						value = int(self.dic_2d[x][y]["text"])
						value = "숫자 : " + str(value)
					except:
						pass

					self.dic_2d[x][y]["text"] = value

					self.dataChanged.emit(index, index, [Qt.DisplayRole])
					return True

				if role == Qt.DecorationRole:
					# 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)
					if isinstance(cell_data["text"], datetime.datetime):
						return QIcon('calendar.png')
					if cell_data["fun"]:
						if cell_data["fun"][0] == "date" and cell_data["fun"][2] == "=today()":
							return QIcon('calendar.png')

				if role == Qt.CheckStateRole and y == 0:
					self.dic_2d[x][y] = QCheckBox('')
					if cell_data["text"] == Qt.Checked:
						self.dic_2d[x][y].setChecked(True)
					else:
						self.dic_2d[x][y].setChecked(False)
					self.dataChanged.emit(index, index)
					return True
				return False


	def headerData(self, index, orientation, role=Qt.DisplayRole):
		if role == Qt.DisplayRole:
			# y축의 header글자를 넣는것
			if orientation == Qt.Horizontal:
				if index in self.header_title_l1d.keys():
					# header의 자료로 넘어오는것이 잇으면 그것을 사용하는 것이다
					return self.header_title_l1d[index]
				else:
					return "Y-%d" % (index + 1)

			if orientation == Qt.Vertical:
				# x축의 header글자를 넣는것
				return "X-%d" % (index + 1)


	def flags(self, index):
		"""

		:param index:
		:return:
		"""
		return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable


	def setColumn(self, col, array_items):
		"""Set column data"""
		self.dic_2d[col] = array_items
		# Notify table, that data has been changed
		self.dataChanged.emit(QModelIndex(), QModelIndex())

	def getColumn(self, col):
		"""Get column data"""
		return self.dic_2d[col]

class view_for_edit(QStyledItemDelegate):
	"""
	선이나 도형을 그리기위한곳
	"""
	def __init__(self, input_data, parent=None):
		super().__init__()
		self.dic_2d = input_data

	def paint(self, painter, option, index):
		"""

		:param painter:
		:param option:
		:param index:
		:return:
		"""
		painter.save()
		x = index.row()
		y = index.column()
		if x in self.dic_2d.keys():
			if y in self.dic_2d[x].keys():
				cell_data = self.dic_2d[x][y]

				x0 = option.rect.x()
				y0 = option.rect.y()

				x1 = option.rect.topRight().x()
				y1 = option.rect.topRight().y()

				x2 = option.rect.bottomLeft().x()
				y2 = option.rect.bottomLeft().y()

				x3 = option.rect.bottomRight().x()
				y3 = option.rect.bottomRight().y()

				#options = QStyleOptionViewItem(option)

				if cell_data["kind_1"] == "memo":
					painter.setBrush(Qt.red)
					painter.drawEllipse(QPoint(x1-5, y1+5), 4, 4)

				if cell_data["draw_line"] == "yes":
					if "line_top_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x0, y0, x1, y1)

					if "line_bottom_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x2, y2, x3, y3)

					if "line_left_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x0, y0, x2, y2)

					if "line_right_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x1, y1, x3, y3)

					if "line_x1_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x0, y0, x3, y3)

					if "line_x2_dic" in cell_data["line_detail"].keys():
						values = cell_data["line_detail"]["line_top_dic"]
						painter.setBrush(Qt.red)
						painter.setPen(QPen(values["color"], values["thick"], values["style"]))
						painter.drawLine(x1, y1, x2, y2)

			super(view_for_edit, self).paint(painter, option, index)
			painter.restore()


	def createEditor(self, parent, option, index):
		"""
		cell이 수정을 할때 나타나는 셀의 화면
		문자를 돌려주면 문자가 출력되고 widget 을 돌려주면 widget이 표현된다
		widget의 결과값이 표시된다
		"""
		#print("선택한 컬럼번호 ==> ", index.column())
		if index.column() == 0:
			check_widget = QCheckBox(parent)
			return check_widget
		if index.column() == 2:
			combo_widget = QComboBox(parent)
			combo_widget.addItems(['', 'item1', 'item2'])
			return combo_widget
		else:
			# 아무것도 조건에 맞는것이 없으면 기본으로 설정된것을 적용하는 것이다
			return QStyledItemDelegate.createEditor(self, parent, option, index)

	def setEditor(self, editor, index):
		"""
		createeditor에서 만들어진 결과값을 선택된 cell에 값을 입력한다
		"""
		x = index.row()
		y = index.column()
		print("setEditor")
		pass



class view_main(QWidget):
	# QTableView를 이용해서 화면을 보여주고, edit화면을 보여주는것을 연결한다
	def __init__(self, parent=None):
		super(view_main, self).__init__()

		self.setWindowTitle(general_setup['window_title'])
		self.setWindowState(Qt.WindowMaximized) # 최대크기로 보여주기

		self.click_status = 0

		self.grid = QTableView()
		#self.grid = CreateTable(500,500)

		self.grid.setStyleSheet("QTableView{gridline-color: lightgray; font-size: 20pt;}")
		self.grid.setStyleSheet("QTableView::item{ border-color: lightgray; border-style: solid; border-width: 0px; }")
		self.grid.setStyleSheet("QTableView{border : 1px solid red}")

		self.grid.horizontalHeader().setStyleSheet("::section{Background-color:rgb(255,236,236)}")
		self.grid.verticalHeader().setStyleSheet("::section{Background-color:rgb(236,247,255)}")
		self.grid.horizontalHeader().setDefaultSectionSize(general_setup["grid_width"])
		self.grid.verticalHeader().setDefaultSectionSize(general_setup["grid_height"])

		#self.data_class_l2d = self.open_data_as_pickle()
		self.data_class_l2d = dic_2d

		self.header_title_l1d = {3:"▽", 5:"컬럼 2", 7: 3, 9:"DDD", 11:"Y-5", 23:"FFFFF", 2:"GGGGG"}

		self.table_model = data_connect_with_table_model(self.data_class_l2d, self.header_title_l1d)

		#self.table_model.dataChanged.connect(self.action_cell_changed)

		# index들을 연결시키면, grid에 item객체들이 만들어 지는 것이다
		# item은 자동으로 만들어지는 것이기 때문에 별도의 세팅이 필요없다
		# 서로 바뀌엇을때 연결이 된는 것은 index와 item이다
		# 예를들어 그리드에서 2번열을 삭제하였을때, 2번은 그대로 있지만 item은 변경이 되어져야 하기때문에 이런 시스템을 만들어 놓는것이다
		# 즉, 현재의 item을 알기위해서는 index를 통해서 들어가는것이 제일 좋다

		self.grid.setModel(self.table_model)
		# setmodel이 item을 만들어서 연결하는것으로 보인다
		# 내부적으로 만들어지는 item은 변경할수가 없다

		#self.grid.setItemDelegate(view_for_edit(self.grid))
		#edit를 실행하면 실행 되는것
		self.grid.setItemDelegate(view_for_edit(self.data_class_l2d))

		#self.selectRow = self.table_model.rowCount(QModelIndex())
		#self.selectColumn = 30

		# 셀의 자료에 widget을 만들도록 하는것은 아래의 메소드에서 하도록 한다
		self.basic_setup_widget()

		self.grid.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
		# header에서 마우스오른쪽을 누르면 나타나는메뉴
		self.grid.horizontalHeader().customContextMenuRequested.connect(self.menupopup_header_y)
		self.grid.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
		# header에서 마우스오른쪽을 누르면 나타나는메뉴
		self.grid.verticalHeader().customContextMenuRequested.connect(self.menupopup_header_x)
		# 셀의 선택이 변경되면 실행되는것

		#self.selection_model = self.grid.selectionModel()
		#self.selection_model.selectionChanged.connect(self.action_selection_changed)

		#self.filters = "CSV files (*.csv)"
		#self.fileName = None

		# 기본적인 event에 대한 설정하는 부분
		#self.grid.currentChanged.connect(self.action_current_cell_changed)
		#self.grid.change
		#self.grid.currentItemChanged.connect(self.action_current_item_changed)
		#self.grid.cellChanged.connect(self.action_cell_changed)
		#self.grid.cellEntered.connect(self.action_cell_entered)
		#self.grid.cellActivated.connect(self.action_cell_activated)
		#self.grid.itemChanged.connect(self.action_item_changed)
		#self.grid.itemSelectionChanged.connect(self.action_item_selection_changed)
		#self.grid.itemClicked.connect(self.action_item_clicked)





		self.buttonNew = QPushButton('NEW', self)
		self.buttonOpen = QPushButton('Open', self)
		self.buttonSave = QPushButton('Save', self)
		self.buttonAdd = QPushButton('Add-X', self)
		self.buttonAddc = QPushButton('Add-Y', self)
		self.buttonDelr = QPushButton('Del-X', self)
		self.buttonDelc = QPushButton('Del-Y', self)
		self.button_color = QPushButton('Color', self)
		self.button_open_pickle = QPushButton('Open pickle', self)
		self.button_save_pickle = QPushButton('Save pickle', self)
		self.text_01 = QLineEdit("")

		self.group = QButtonGroup()
		self.group.addButton(self.buttonNew)
		self.group.addButton(self.buttonOpen)
		self.group.addButton(self.buttonSave)
		self.group.addButton(self.buttonAdd)
		self.group.addButton(self.buttonAddc)
		self.group.addButton(self.buttonDelr)
		self.group.addButton(self.buttonDelc)
		self.group.addButton(self.button_color)
		self.group.addButton(self.button_open_pickle)
		self.group.addButton(self.button_save_pickle)

		self.buttonNew.clicked.connect(self.file_new)
		self.buttonOpen.clicked.connect(self.file_open)
		self.buttonSave.clicked.connect(self.file_save)
		self.buttonAdd.clicked.connect(self.insert_x)
		self.buttonAddc.clicked.connect(self.insert_y)
		self.buttonDelr.clicked.connect(self.remove_x)
		self.buttonDelc.clicked.connect(self.remove_y)
		self.button_color.clicked.connect(self.color_picker)
		self.button_open_pickle.clicked.connect(self.open_data_as_pickle)
		self.button_save_pickle.clicked.connect(self.save_data_as_pickle)

		layout = QHBoxLayout()
		layout.addWidget(self.buttonNew)
		layout.addWidget(self.buttonOpen)
		layout.addWidget(self.buttonSave)
		layout.addWidget(self.buttonAdd)
		layout.addWidget(self.buttonAddc)
		layout.addWidget(self.buttonDelr)
		layout.addWidget(self.buttonDelc)
		layout.addWidget(self.button_color)
		layout.addWidget(self.button_open_pickle)
		layout.addWidget(self.button_save_pickle)
		layout.addWidget(self.text_01)

		Vlayout = QVBoxLayout()
		Vlayout.addWidget(self.grid)
		Vlayout.addLayout(layout)

		self.setLayout(Vlayout)
		self.make_widget_test() # 1,1에 버튼을 만드는 것

		self.grid.clicked.connect(self.view_click)

	def action_cell_changed(self, index, value, role=Qt.EditRole):
		if role == Qt.DisplayRole:
			print(f"Data changed at row ")
			#print("Updated model data:", model._values)
			#print("Original data:", A)

	def evtaction_cell_changed(self, x, y):
		# 이동된후의 값을 나타낸다
		self.add_history(self.old_cell)
		self.check_max_xy(x, y)

		try:
			input_text = self.item(x, y).text()

			#print("입력값이 변경되었네요", (x, y), input_text)
			# 셀에 입력이 "="으로 입력되었을때 적용하는것
			if input_text == "=1":
				self.write_cell_combo([2, 2], ["abc", "def", "xyz"])
			elif input_text == "=2":
				#print("=2 를 입력했네요")
				self.write_cell_combo([3, 3], ["111abc", "222def", "333xyz"])
		except:
			pass

	def evtaction_item_changed(self, item):
		#print(f"Item Changed ({item.row()}, {item.column()})")

		# 이동된후의 값을 나타낸다
		x = self.currentRow()
		y = self.currentColumn()
		self.add_history(self.old_cell)
		self.check_max_xy(x, y)
		try:
			input_text = self.item(x, y).text()

			# print(input_text)
			# 셀에 입력이 "="으로 입력되었을때 적용하는것
			if input_text[0:2] == "=1":
				self.write_cell_combo(2, 2, ["abc", "def", "xyz"])
			elif input_text[0:2] == "=2":
				self.write_cell_combo(3, 3, ["111abc", "222def", "333xyz"])
		except:
			pass

	def evtaction_item_selection_changed(self):

		# print("item_selection_changed")
		# 이동된후의 값을 나타낸다
		x = self.currentRow()
		y = self.currentColumn()
		cells = self.read_xyxy_attribute([x, y])
		self.old_cell = {"kind_1": "change", "xyxy": [x, y], "cells": cells}
		self.check_max_xy(x, y)
		return self.old_cell

	def add_history(self, change):
		self.history.append(change)

	def action_selection_changed(self, selected, deselected):
		for ix in selected.indexes():
			#print("selected.indexes : ", ix.data())
			pass

		for ix in deselected.indexes():
			#print("deselected.indexes : ", ix.data())
			pass

	def basic_setup_widget(self):
		# 모든자료중에서 widget이 있는것을 찾아서 실행시키는 것이다
		try:

			for x in self.data_class_l2d.keys():
				for y in self.data_class_l2d[x].keys():
					one_values = self.data_class_l2d[x][y]
					#print("widget", one_values)

					if one_values["kind_1"] == "widget":
						if one_values["kind_2"] == "button":
							self.write_cell_button([x, y], one_values["caption"])
						elif one_values["kind_2"] == "check_box":
							self.write_cell_checkbox([x, y], one_values["checked"])
						elif one_values["kind_2"] == "combo":
							self.write_cell_combo([x, y], one_values["value"])
						elif one_values["kind_2"] == "progress_bar":
							self.write_cell_progressbar([x, y], one_values["value"])
		except:
			pass

	def contextMenuEvent(self, event):
		"""
		마우스 오른쪽으로 누르면 나타나는 메뉴를 만드는 것
		"""
		menu = QMenu(self)
		aaa = menu.addAction("test")
		copy_action = menu.addAction("복사하기")
		paste_action = menu.addAction("붙여넣기")
		quit_action = menu.addAction("Quit")
		backgroundcolor_action = menu.addAction("배경색넣기")
		delete_widget_action = menu.addAction("위젯삭제하기")

		action = menu.exec_(self.mapToGlobal(event.pos()))

		if action == quit_action:
			QCoreApplication.instance().quit()
		elif action == copy_action:
			self.press_key_copy()
		elif action == paste_action:
			self.press_key_paste()
		elif action == aaa:
			print("test...")
		elif action == backgroundcolor_action:
			self.paint_cell_color()
		elif action == delete_widget_action:
			self.delete_xyxy_widget()

	def check_max_xy(self, x, y):
		# usedrange를 확정하기위해 사용되는것
		if x != "":
			self.max_x = max(x, self.max_x)
		if y != "":
			self.max_y = max(y, self.max_y)

	def color_picker(self):
		# 이것을 누르면 color picker가 나타나고 그 결과를 text에 나타내도록 한다
		# 색을 선택한 것이다
		color = QColorDialog.getColor()
		# self.text_01.setText(str(color.getRgb()))
		self.rgb_color = color.getRgb()
		general_setup["color"] = list(color.getRgb())[:3]
		btn = self.sender()
		btn.setStyleSheet("background-color : rgb({0}, {1}, {2})".format(general_setup["color"][0], general_setup["color"][1], general_setup["color"][2]))

	def check_usedrange(self, xyxy):
		# usedrange를 확인하는 것이다
		if len(xyxy) == 2:
			self.usedrange[0] = max(xyxy[0], self.usedrange[0])
			self.usedrange[1] = max(xyxy[0], self.usedrange[1])
		else:
			self.usedrange[0] = max(xyxy[0], self.usedrange[0], self.usedrange[2])
			self.usedrange[1] = max(xyxy[0], self.usedrange[1], self.usedrange[3])

	def check_xyxy(self, xyxy):
		if len(xyxy) == 2:
			xyxy = [xyxy[0], xyxy[1], xyxy[0], xyxy[1]]
		elif len(xyxy) == 4:
			pass
		return xyxy

	def delete_xyxy_widget(self):
		#그리드안의 선택된 영역에 위젯을 삭제하는 것이다
		x0, y0, x1, y1 = self.read_selection_xyxy()

		for x in range(x0, x1 + 1):
			for y in range(y0, y1 + 1):
				self.grid.setIndexWidget(self.table_model.index(x, y), None)

	def delete_xyxy_selection(self, xyxy_list):
		# 선택영역안의 객체 삭제
		for xyxy in xyxy_list:
			for x in range(xyxy[0], xyxy[2] + 1):
				for y in range(xyxy[1], xyxy[3] + 1):
					self.setItem(x, y, QTableWidgetItem(""))

	def delete_cell_attribute(self, xy):
		self.removeCellWidget(xy[0], xy[1])


	def file_new(self):
		#print("file_new")
		pass

	def file_save(self):
		if self.fileName == None or self.fileName == '':
			self.fileName, self.filters = QFileDialog.getSaveFileName(self, filter=self.filters)
		if (self.fileName != ''):
			with open(self.fileName, 'wt') as stream:
				csvout = csv.writer(stream, lineterminator='\n')
				csvout.writerow(self.header_title_l1d)
				for row in range(self.table_model.rowCount(QModelIndex())):
					rowdata = []
					for column in range(self.table_model.columnCount(QModelIndex())):
						item = self.table_model.index(row, column, QModelIndex()).data(Qt.DisplayRole)
						if column == 0:
							rowdata.append('')
							continue

						if item is not None:
							rowdata.append(item)
						else:
							rowdata.append('')
					csvout.writerow(rowdata)

	def file_open(self):
		self.fileName, self.filterName = QFileDialog.getOpenFileName(self)

		if self.fileName != '':
			with open(self.fileName, 'r') as f:
				reader = csv.reader(f)
				header = next(reader)
				buf = []
				for row in reader:
					row[0] = QCheckBox("-")
					buf.append(row)

				self.table_model = None
				self.table_model = data_connect_with_table_model(buf, self.header_title_l1d)
				self.grid.setModel(self.table_model)
				self.fileName = ''

	def get_index_by_push_button(self):
		# 버튼누르면 그것의 index를 갖고오는 코드
		pos = self.sender().parent().pos()
		index = self.grid.indexAt(pos)
		return index

	def get_index_by_widget(self):
		# 버튼누르면 그것의 index를 갖고오는 코드
		pos = self.sender().parent().pos()
		index = self.grid.indexAt(pos)
		return index

	def insert_x(self, position, rows=1, index=QModelIndex()):
		#try:
		#x0, y0, x1, y1 = self.read_selection_xyxy()
		#insert_list = [basic_cell_class() for y in range(len(self.data_class_l2d[x0]))]

		#self.table_model.beginInsertRows(QModelIndex(), x0, x1)
		#for no in range(x0, x1 + 1):
		#	self.data_class_l2d.insert(no, insert_list)
		#self.table_model.endInsertRows()

		#return True
		pass

	def insert_y(self, position, cols=1, index=QModelIndex()):
		#x0, y0, x1, y1 = self.read_selection_xyxy()
		#self.table_model.beginInsertColumns(QModelIndex(), y0, y1)
		#for y in range(y0, y1 + 1):
		#	for x in range(len(self.data_class_l2d)):
	#			self.data_class_l2d[x].insert(y, basic_cell_class())
		#self.table_model.endInsertColumns()

		#return True
		pass

	def keyPressEvent(self, event):
		# 키보드를 누르면 실행되는 것
		super().keyPressEvent(event)
		if event.key() in (Qt.Key_Return, Qt.Key_Enter):
			#print("enter키를 누름")
			self.press_enter_key()
		elif event.key() == Qt.Key_Delete:
			self.press_key_delete()
		elif event.key() == Qt.Key_A and (event.modifiers() & Qt.ControlModifier):
			self.SelectAll()
		elif event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
			self.press_key_copy()
		elif event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
			self.press_key_paste()
		elif event.key() == Qt.Key_X and (event.modifiers() & Qt.ControlModifier):
			self.paste_cut_key(event)
		elif event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier):
			self.undo()

	def make_widget_test(self):
		# 테스트용도로 상용하는 것이다
		self.write_cell_button([1, 1], "abc", "action_def")

	def move_cell_widget(self, old_xy, new_xy):
		"""
		이전에 있는 위젯을 다른곳에 옮기기 위한것
		위젯용으로 다른것을 만드는것도 좋을듯 하다
		"""
		new_index = self.table_model.index(old_xy[0], old_xy[1])
		index_widget = self.grid.indexWidget(new_index)
		self.grid.setIndexWidget(self.table_model.index(new_xy[0], new_xy[1]), index_widget)

	def menupopup_header_y(self, pos):
		"""
		Header에서 마우스 오른쪽으로 누르면 나타나는 메뉴를 만드는 것
		"""
		# action = menu.exec_(self.viewport().mapToGlobal(pos))

		global_pos = self.mapToGlobal(pos)
		menu = QMenu()
		ddd = menu.addAction("y해드의 1번을 누르세요")
		del_yy_action = menu.addAction("yy삭제하기")
		quit_action = menu.addAction("Quit")

		selected_menu = menu.exec_(global_pos)
		if selected_menu == quit_action:
			print("Quit을 눌렀네요")
		elif selected_menu == del_yy_action:
			self.delete_xyxy_yy()
		elif selected_menu == ddd:
			print("1번을 눌렀네요")

	def menupopup_header_x(self, pos):
		"""
		Header에서 마우스 오른쪽으로 누르면 나타나는 메뉴를 만드는 것
		"""
		global_pos = self.mapToGlobal(pos)
		menu = QMenu()
		ddd = menu.addAction("x해드의 1번을 누르세요")
		delete_xx_action = menu.addAction("xx삭제하기")
		quit_action = menu.addAction("Quit")

		selected_menu = menu.exec_(global_pos)
		if selected_menu == quit_action:
			print("Quit을 눌렀네요")
		elif selected_menu == delete_xx_action:
			self.delete_xyxy_xx()
		elif selected_menu == ddd:
			print("1번을 눌렀네요")

	def open_data_as_pickle(self):
		try:
			with open("save_xxxl_data.pickle", "rb") as fr:
				self.data_class_l2d=pickle.load(fr)
		except:
			self.data_class_l2d = ""
		return self.data_class_l2d

	def press_key_copy_high(self):
		pass

	def press_key_copy(self):
		"""
		선택한 영역의 값만을 복사한다
		내용전체를 복사하는것은 다른것으로 하도록한다
		"""
		x0, y0, x1, y1 = self.read_selection_xyxy()
		result = []
		for x in range(x0, x1 + 1):
			temp = []
			for y in range(y0, y1 + 1):
				new_index = self.table_model.index(x, y)
				text = new_index.data()
				temp.append(text)
			result.append(temp)
		general_setup["copy_items"] = result
		# 윈도우 클립보드에
		self.copy_to_clipboard(result)

	def copy_to_clipboard(self, input_2dlist):
		"""
		윈도우의 클립보드에 붙여 넣는다
		"""
		clipboard = ""
		for x in range(len(input_2dlist)):
			for y in range(len(input_2dlist[x])):
				clipboard += input_2dlist[x][y] + '\t'
			clipboard = clipboard[:-1] + '\n'

		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardText(clipboard)
		win32clipboard.CloseClipboard()

	def press_key_paste(self):
		copy_data = general_setup["copy_items"]
		x0, y0, x1, y1 = self.read_selection_xyxy()
		for x in range(len(copy_data)):
			for y in range(len(copy_data[x])):
				self.table_model.setData(self.table_model.index(x0 + x, y0 + y), copy_data[x][y])

	def paint_cell_color(self, xy="", input_rgb=[123, 123, 123]):
		# 셀의 배경색을 넣기위해 만드는 것이다
		x0, y0, x1, y1 = self.read_selection_xyxy()
		if general_setup["color"]:
			color = general_setup["color"]
		else:
			color = "gray"
		for x in range(x0, x1 + 1):
			for y in range(y0, y1 + 1):
				if general_setup["color"]:
					rgb_color = general_setup["color"]
				else:
					rgb_color = general_setup["basic_color"]
				#self.data_class_l2d[x][y]["background_color"] = rgb_color
				#self.tableWidget.item(3, 5).setBackground(QtGui.QColor(100,100,150))

	def press_key_cut(self):
		self.press_key_copy()
		self.press_key_delete()

	def press_enter_key(self):
		print("Press Enter")

	def press_key_delete(self):
		#print("delete")
		for one_index in self.grid.selectedIndexes():
			self.table_model.setData(one_index, None)

	def read_yy_attribute(self, xyxy):
		# 세로를 삭제하였을때 값과 속성을 하나씩 저장하는 것이다
		old_xyxy = self.read_selection_xyxy()
		end_xy = self.usedrange
		xyxy = [0, old_xyxy[1], end_xy[0], old_xyxy[3]]
		result = []
		for x in range(xyxy[0], xyxy[2]):
			temp = {}
			for y in range(xyxy[1], xyxy[3]):
				# 추가로 속성을 넣을수있도록 만든것이다
				temp["x"] = x
				temp["y"] = y
				temp["text"] = self.item(x, y).text()
			result.append(temp)
		return result

	def remove_x(self, position, rows=1, index=QModelIndex()):
		# remove는 열자체를 없애고 아랫것이 위로 올라가는 것이다
		# delete는 값만 없애는 것이다
		x0, y0, x1, y1 = self.read_selection_xyxy()

		self.table_model.beginRemoveRows(QModelIndex(), x0, x1)
		for no in range(x1, x0 - 1, -1):
			# print(no)
			# self.table_model.removeRow(no)
			self.data_class_l2d.pop(no)
		self.table_model.endRemoveRows()

		return True

	def read_cell_all_values(self, xy):
		# self.data_class_l2d[x][y].values["background_color"] = rgb_color
		x, y = xy

	def read_cell_item(self, xy):
		"""
		인덱스로 넘어온 자료의 item을 돌려준다
		"""
		new_index = self.table_model.index(xy[0], xy[1])
		aaa = QStandardItemModel(self.grid.model()).item(3, 4)
		self.grid.model().setItem(7, 7, aaa)

	def read_xyxy_items(self, xyxy_list):
		# 선택된 영역의 item을 돌려준다
		# 여러곳을 선택할수가 있어서
		# final_result = [[2ditem_자료들, xyxy], [2ditem_자료들, xyxy], ]

		final_result = []
		result = []

		for xyxy_one in xyxy_list:
			#print("영역의 item값 ==> ", xyxy_one)
			x0, y0, x1, y1 = xyxy_one
			for x in range(x0, x1 + 1):
				temp = []
				for y in range(y0, y1 + 1):
					self.old_item = self.grid.model().data()
					one_item = self.old_item.clone()
					temp.append(one_item)
				result.append(temp)
			final_result.append([result, xyxy_one])
		self.old_item = final_result
		return result

	def remove_y(self, position, cols=1, index=QModelIndex()):
		x0, y0, x1, y1 = self.read_selection_xyxy()
		self.table_model.beginRemoveColumns(QModelIndex(), y0, y1)
		for y in range(y1, y0 - 1, -1):
			# self.table_model.removeRow(no)
			# 자료삭제를 item에서하니 계속 같은 자료가 다시 나타났다
			for x in range(len(self.data_class_l2d)):
				self.data_class_l2d[x].pop(y)
		self.table_model.endRemoveColumns()
		return True

	def read_selection_xyxy_new(self):
		selection_range = self.grid.selectionModel().selection()
		x0 = selection_range.first().topLeft().row()
		y1 = selection_range.last().bottomRight().column()
		y0 = selection_range.first().topLeft().column()
		x1 = selection_range.last().bottomRight().row()

		result = [x0, y0, x1, y1]
		return result

	def read_selection_xyxy(self):
		"""
		read_selection_xyxy()
		선택한 여러영역의 좌표를 돌려준다
		[[1,2,3,4],[5,6,7,8],[9,10,11,12],]
		"""
		result = []
		selection_xyxy = self.grid.selectionModel().selection()
		x0 = selection_xyxy.first().topLeft().row()
		y1 = selection_xyxy.last().bottomRight().column()
		y0 = selection_xyxy.first().topLeft().column()
		x1 = selection_xyxy.last().bottomRight().row()

		result = [x0, y0, x1, y1]

		return result

	def read_xx_attribute(self, xyxy):
		# 가로를 삭제하였을때 값과 속성을 하나씩 저장하는 것이다
		old_xyxy = self.read_selection_xyxy()
		end_xy = self.usedrange
		xyxy = [old_xyxy[0], 0, old_xyxy[2], end_xy[1]]
		result = []
		for x in range(xyxy[0], xyxy[2]):
			temp = {}
			for y in range(xyxy[1], xyxy[3]):
				# 추가로 속성을 넣을수있도록 만든것이다
				temp["x"] = x
				temp["y"] = y
				temp["text"] = self.item(x, y).text()
			result.append(temp)
		return result

	def read_xyxy_value(self, xyxy):
		result = []
		xyxy = self.check_xyxy(xyxy)

		for x in range(xyxy[0], xyxy[2]):
			temp = []
			for y in range(xyxy[1], xyxy[3]):
				try:
					text = self.item(x, y).text()
				except:
					text = ""
				temp.append(text)
			result.append(temp)

		self.max_x = max(xyxy[2], self.max_x)
		self.max_y = max(xyxy[3], self.max_y)
		return result

	def read_xyxy_attribute(self, xyxy):
		# 선택한영역의 주소와 속성을 하나씩 저장하는 것이다
		# 결과물 = [[x,y,값]....]
		result = []
		if len(xyxy) == 2: xyxy = [xyxy[0], xyxy[1], xyxy[0], xyxy[1]]
		for x in range(xyxy[0], xyxy[2]):
			for y in range(xyxy[1], xyxy[3]):
				result.append([x, y, self.item(x, y).text()])
		return result

	def read_cell_value(self, xy):
		try:
			result = self.item(xy[0], xy[1]).text()
		except:
			result = ""
		return result

	def save_data_as_pickle(self):
		# 셀에서 값을 바꾸면, 기본 자료값에도 값이 바뀐다
		with open('save_xxxl_data.pickle', 'wb') as f:
			pickle.dump(self.data_class_l2d, f)

	def save_pickle(self):
		# view객체는 서로 연결이 되어있어서 pickle로 안된다고 한다.
		# 직렬화후 역직렬화를 하면 된다는데...
		# 잘 모르겠다
		# ddd = self.table_model
		# ccc = open("save_pyqt_grid_items.pickle", "b")
		# pickle.dump(ddd, ccc)
		# ccc.close()
		# self.grid.model().setItem(7,7, aaa)
		# self.table_model.setItem(7,7, aaa)
		aaa = QStandardItemModel(self.grid.model()).item(3, 4)

	def sort_by_no(self, x):
		# x 번재 자리에 column 삽입
		self.sortItems(x, Qt.DescendingOrder)

	def setup_header_name(self):
		pass

	def undo(self):
		if len(self.history):
			action = self.history.pop()
			xyxy = action["xyxy"]
			value_s = action["cells"]
			#print("undo 실행", action["kind_1"], xyxy, value_s)

			if action["kind_1"] == "change" or action["kind_1"] == "delete":
				self.write_xyxy_attribute(action)

			elif action["kind_1"] == "delete_rows":
				self.add_rows(xyxy)
				for row, col, attribute in value_s:
					self.write_cell_value([row, col], attribute["text"])

			elif action["kind_1"] == "delete_cols":
				self.add_cols(xyxy)
				for row, col, attribute in value_s:
					self.write_cell_value([row, col], attribute["text"])

			elif action["kind_1"] == "add_rows":
				self.del_rows(xyxy)

			elif action["kind_1"] == "add_cols":
				self.del_cols(xyxy)
			else:
				return

	def view_click(self, indexClicked):
		#print('view_click 클릭함 : (x: %s  y: %s)' % (indexClicked.row(), indexClicked.column()))
		self.px = indexClicked.row() + 1
		self.py = indexClicked.column() + 1
		self.click_status = 1

		#print('px : %s  py %s' % (indexClicked.row() + 1, indexClicked.column() + 1))
		self.selectRow = indexClicked.row()

	def write_cell_button(self, xy, title="abc", action_def="", style_sheet=""):
		"""
		셀에 버튼을 만들어서 넣는 것이다
		"""
		if style_sheet == "":
			style_sheet = "QPushButton { text-align: left;font-weight: bold;font-color:black}"
		btnRun = QPushButton(title, self)
		# btnRun.clicked.connect(action_def)
		btnRun.setFont(QFont('Malgun Gothic', 8))
		btnRun.setStyleSheet(style_sheet)
		aaa = QModelIndex()
		self.grid.setIndexWidget(self.table_model.index(xy[0], xy[1]), btnRun)

	def write_cell_checkbox(self, xy, value=1, title=""):
		cbox = QCheckBox(title)
		cbox.setChecked(int(value))
		self.grid.setIndexWidget(self.table_model.index(xy[0], xy[1]), cbox)

	def write_cell_combo(self, xy, combo_list):
		combo = QComboBox()
		for one in combo_list:
			combo.addItem(str(one))
		self.grid.setIndexWidget(self.table_model.index(xy[0], xy[1]), combo)

	def write_cell_progressbar(self, xy, value=50):
		progress_bar = QProgressBar()
		progress_bar.setValue(int(value))
		self.grid.setIndexWidget(self.table_model.index(xy[0], xy[1]), progress_bar)

	def write_cell_value(self, xy, input_text):
		self.setItem(xy[0], xy[1], QTableWidgetItem(str(input_text)))
		self.check_max_xy(xy[0], xy[1])

	def write_xyxy_attribute(self, action):
		action_type = action["kind_1"]
		xyxy = action["xyxy"]
		value_s = action["cells"]
		for one_list in value_s:
			for x, y, value in one_list:
				self.setItem(x, y, QTableWidgetItem(str(value)))

	def write_xyxy_value(self, xy, input_list):
		"""
		영역에 값을 써 넣는것
		"""
		for x in range(len(input_list)):
			for y in range(len(input_list[0])):
				self.setItem(xy[0] + x, xy[1] + y, QTableWidgetItem(str(input_list[x][y])))

	def write_xyxy_1dvalue(self, input_list):
		for y in range(len(input_list)):
			self.setItem(1, y, QTableWidgetItem(str(input_list[y])))

class main(QMainWindow):
	def __init__(self, parent = None):
		super().__init__(parent)
		grid = view_main()
		self.create_menubar()

		self.resize(500,500)
		self.setCentralWidget(grid)
		self.show()

	def create_menubar(self):
		# 메뉴바를 만드는 것
		menubar = self.menuBar()
		menu_1 = menubar.addMenu("사용법")

		menu_1_1 = QAction('내부실행용', self)
		menu_1_1.triggered.connect(self.text_manual)
		menu_1.addAction(menu_1_1)

		menu_1_2 = QAction('외부화일 실행용', self)
		menu_1_2.triggered.connect(self.text_manual)
		menu_1.addAction(menu_1_2)

		menu_1_3 = QAction(QIcon("save.png"), '참고사이트', self)
		menu_1_3.triggered.connect(self.text_manual)
		menu_1.addAction(menu_1_3)

		menu_2 = menubar.addMenu("Made by")

		menu_2_1 = QAction('누가 만들었나요?', self)
		menu_2_1.triggered.connect(self.text_manual)
		menu_2.addAction(menu_2_1)

		menu_2_2 = QAction('Logo의 의미', self)
		menu_2_2.triggered.connect(self.text_manual)
		menu_2.addAction(menu_2_2)

		menu_3 = menubar.addMenu("끝내기")

		menu_3_1 = QAction(QIcon('exit.png'), 'Exit', self)
		menu_3_1.triggered.connect(QCoreApplication.quit())
		menu_3.addAction(menu_3_1)

	def text_manual(self):
		print("메뉴의 테스트")


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mygrid_example = main()
	sys.exit(app.exec())