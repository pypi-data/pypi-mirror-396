# -*- coding: utf-8 -*-
import sys, datetime #내장모듈
import pickle, win32clipboard, csv
import pyperclip

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCore import QCoreApplication

class basic_cell_class_for_mygrid():
	# 각 셀에대해서 어떤 자료들을 넣을수있을지 설정하도록 만든 것이다
	# 다음에 추가적인것들도 가능하도록 클래스로 만든 것이다

	def __init__(self):
		self.values = {
			"font_dic": {"font_color": None, "font_size": None, "background": None, "bold": None, "color": None,
						 "colorindex": None, "creator": None, "style": None, "italic": None,
						 "name": None, "size": None, "strikethrough": None, "subscript": None, "superscript": None,
						 "themecolor": None, "themefont": None, "tintandshade": None, "underline": None},
			"line_top_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
							 "style": None, "brush": None, },
			"line_bottom_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
								"style": None, "brush": None, },
			"line_left_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
							  "style": None, "brush": None, },
			"line_right_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
							   "style": None, "brush": None, },
			"line_x1_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
							"style": None, "brush": None, },
			"line_x2_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None,
							"style": None, "brush": None, },
			"widget_dic": {"value": None, },
			"kind_dic": {"big": None, "middle": None, },
			"memo_dic": {"value": None},
			"checked": None,
			"fun": None,
			"kind_1": None,
			"kind_2": None,
			"user_type": None,
			"text": None,
			"text_kind": None,
			"value": None,
			"value2": None,
			"formularr1c1": None,
			"formular": None,
			"background_color": None,
			"background_colorindex": None,
			"numberformat": None,
			"widget": None,
			"align": None,
			"decoration": None,
			"edit": None,
			"access_text": None,
			"access": None,
			"order": None,
			"size": None,
			"check": None,
			"color": None,
			"function": None,
			"icon": None,
			"memo": None,
			"draw_line": None,
			"protect": None,
			"status": None,
			"what": None,
			"setup": None,
			"tool_tip": None,
			"etc": None,
			"user_1": None,
			"user_2": None,
			"user_3": None,
			"x": None,
			"y": None,
		}

bbb = basic_cell_class_for_mygrid()

# 코드 전체에서 사용할 변수를 설정한다

basic_datas =  {"basic_color": [217, 217, 217],
					  "color": "",
					  "copy_items": [],
					  "grid_x_len": 5000,
					  "grid_y_len": 100,
					  "window_title": "Grid_Man",
					  "background_color": [123, 123, 123],
					  "grid_height": 25,
					  "grid_width": 50,
					  }
xy_datas = [
					{"x": 2, "y": 1, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},
					{"x": 2, "y": 3, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 5, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 7, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},
					{"x": 8, "y": 8, "draw_line":"yes", "line_top_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 9, "draw_line": "yes",
					 "line_top_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 8, "draw_line": "yes",
					 "line_bottom_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 8, "draw_line": "yes",
					 "line_left_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},

					{"x": 2, "y": 6, "kind_1": "tool_tip", "text": "tool_tip", "tool_tip": "툴팁입니다"},
					{"x": 5, "y": 3, "kind_1": "widget", "kind_2":"combo", "value": [1, 2, 3, 4, 5]},
					{"x": 5, "y": 5, "kind_1": "widget", "kind_2": "check_box", "checked": 1, "text":"check"},
					{"x": 5, "y": 7, "kind_1": "widget", "kind_2":"progress_bar", "value": 30},
					{"x": 5, "y": 8, "kind_1": "widget", "kind_2":"button", "caption": "button_1", "action":"action_def"},

					{"x": 10, "y": 10, "kind_1": "memo", "value": "memo memo"},
					{"x": 2, "y": 2, "kind_1": "memo", "value": "memo memo"},

					{"x": 7, "y": 3, "kind_1": "font_color", "value": [255, 63, 24]},
					{"x": 7, "y": 5, "kind_1": "background_color", "value": [255, 63, 24]},
							   ]

#테이블에 값을 넣기위해, 2차원자료를 클래스로 만든것
class make_table_datas():
    def __init__(self, parent=None):
        """
        테이블에 값을 넣기위해, 2차원자료를 클래스로 만든것

        모든 자료를 먼저 만들고 싶은만큼 빈 2차원 빈 cell객체를 넣는다
        이후에 각 리스트안에 원하는 값들을 cell객체의 내용을 변경한다
        기본 설정한 가로세로에 맞는 2차원 리스트에 cell객체를 넣는다
        """

        self.all_cell_sets = [[basic_cell_class() for j in range(basic_datas["grid_y_len"])] for i in
                          range(basic_datas["grid_x_len"])]

    def get_cell_sets(self):
        """
        2차원의 빈 cell객체에 값을 넣고 2차원의 객체를 돌려준다
        외부에서도 바꿔서 사용할수있도록하기위해 2개의 리스트형태로 만들었다
        """
        # 이것처름 쓰면 본인이 만든것을 쉽게 넣을수도 있다
        # 모든 2차원 자료를 확인하면서 동일하게 만들것을 적용한다
        for one_value in xy_datas:
            x = one_value["x"]
            y = one_value["y"]
            self.all_cell_sets[x][y].values.update(one_value)
        return self.all_cell_sets

#들어온 값을 모양을 제외하고 표현하는것
class display_cell_class(QAbstractTableModel):
    """
    들어온 값을 표현하는것
    """

    def __init__(self, list, headers=[], parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.grid_xy_datas = list
        self.headers_titles = headers

    def rowCount(self, parent):
        """
        표현하는 최대 갯수를 알아오기 위한 것이다

        :param parent:
        :return:
        """
        return len(self.grid_xy_datas)

    def columnCount(self, parent):
        """

        :param parent:
        :return:
        """
        return len(self.grid_xy_datas[0])

    def flags(self, index):
        """

        :param index:
        :return:
        """
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            # y축의 header글자를 넣는것
            if orientation == Qt.Horizontal:
                if section < len(self.headers_titles):
                    # header의 자료로 넘어오는것이 잇으면 그것을 사용하는 것이다
                    return self.headers_titles[section]
                else:
                    return "Y-%d" % (section + 1)

            if orientation == Qt.Vertical:
                # x축의 header글자를 넣는것
                return "X-%d" % (section + 1)

    def data(self, index, role):
        """
        각 셀별로 자료를 표현할 때마다 이것이 실행되는 것이다
        모든 것을 각 셀마다 다르게 설정할수가 있다
        화면을 움직이거나 하면 매번 다시 실행된다
        """
        x = index.row()
        y = index.column()
        cell_obj = self.grid_xy_datas[x][y]
        xy_datas = cell_obj.values
        #xy_datas = xy_datas = table_data_01.write_data()
        #print(xy_datas)


        if role == Qt.DisplayRole:
            # 0 : 문자를 표현하는 방법 (QString)
            #print("data-display-role")
            try:
                if xy_datas["kind_2"] == "date" and xy_datas["kind_2"] == "=today()":
                        return "2022-08-20"
                elif type(xy_datas["text"]) == type(1):
                    return "숫자 : " + str(xy_datas["text"])

                elif xy_datas["kind_2"] == "date" and isinstance(xy_datas["value"], datetime):
                    return xy_datas["value"].strftime('%Y-%m-%d')
                else:
                    return xy_datas["text"]
            except:
                pass

        if role == Qt.DecorationRole:
            # 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)
            try:

                if xy_datas["kind_2"] == "date" and isinstance(xy_datas["value"], datetime):
                    return QIcon('calendar.png')
                elif xy_datas["kind_2"] == "date" and xy_datas["value"] == "=today()":
                        return QIcon('calendar.png')
                elif str(xy_datas["text"]) == "=":
                    return QIcon('calendar.png')
            except:
                pass

        if role == Qt.EditRole:
            # 2   The data in a form suitable for editing in an editor. (QString)
            # 수정할때 나타나는 것
            return xy_datas["text"]

        if role == Qt.ToolTipRole:
            # 3   각 셀마다 툴팁을 설정할수있는것. (QString)
            if xy_datas["kind_1"] == "tool_tip":
                return xy_datas["tool_tip"]

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

        if role == Qt.TextAlignmentRole:
            # 7   The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
            return int(Qt.AlignLeft | Qt.AlignBottom)

        #if role == Qt.BackgroundColorRole:
            # 8   The background brush used for items rendered with the default delegate. (QBrush)
        #    color = xy_datas["background_color"]
        #    if color:
        #        return QColor(color[0], color[1], color[2])

        if role == Qt.ForegroundRole:
            # 9   The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
            try:
                font_color = xy_datas["font_dic"]["color"]
                if font_color:
                    return QColor(font_color[0], font_color[1], font_color[2])
            except:
                pass

        if role == Qt.CheckStateRole:
            # 10  This role is used to obtain the checked state of an item. (Qt.CheckState)
            pass
            #    if self.grid_xy_datas[row][column].isChecked():
            #        return QVariant(Qt.Checked)
            #    else:
            #        return QVariant(Qt.Unchecked)

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
        cell_obj = self.grid_xy_datas[x][y]
        xy_datas = cell_obj.values

        if role == Qt.EditRole:
            try:
                text = int(xy_datas["text"])
                text = "숫자 : " + str(text)
            except:
                pass

            xy_datas["text"] = value

            self.dataChanged.emit(index, index)
            return True

        if role == Qt.DecorationRole:
            # 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)
            if isinstance(xy_datas["text"], datetime):
                return QIcon('calendar.png')
            if xy_datas["fun"]:
                if xy_datas["fun"][0] == "date" and xy_datas["fun"][2] == "=today()":
                    return QIcon('calendar.png')

        if role == Qt.CheckStateRole and y == 0:
            self.grid_xy_datas[x][y] = QCheckBox('')
            if xy_datas["text"] == Qt.Checked:
                self.grid_xy_datas[x][y].setChecked(True)
            else:
                self.grid_xy_datas[x][y].setChecked(False)
            self.dataChanged.emit(index, index)
            return True
        return False

#모양을 나타내기 위해 만든 것
class display_cell_upgrade_class(QStyledItemDelegate): #모양을 나타내기 위해 만든 것
    """
    모양을 나타내기 위해 만든 것
    """
    def __init__(self, list, parent=None):
        super().__init__()
        self.grid_xy_datas = list

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
        xy_datas = self.grid_xy_datas[x][y].values

        x0 = option.rect.x()
        y0 = option.rect.y()

        x1 = option.rect.topRight().x()
        y1 = option.rect.topRight().y()

        x2 = option.rect.bottomLeft().x()
        y2 = option.rect.bottomLeft().y()

        x3 = option.rect.bottomRight().x()
        y3 = option.rect.bottomRight().y()

        options = QStyleOptionViewItem(option)

        if xy_datas["kind_1"] == "memo":
            print("----------->", x, y)
            painter.setBrush(Qt.red)
            painter.drawEllipse(QPoint(x1-5, y1+5), 4, 4)

        if xy_datas["draw_line"] == "yes":
            if xy_datas["line_top_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x0, y0, x1, y1)

            if xy_datas["line_bottom_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x2, y2, x3, y3)

            if xy_datas["line_left_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x0, y0, x2, y2)

            if xy_datas["line_right_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x1, y1, x3, y3)

            if xy_datas["line_x1_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x0, y0, x3, y3)

            if xy_datas["line_x2_dic"]["do"]:
                values = xy_datas["line_top_dic"]
                painter.setBrush(Qt.red)
                painter.setPen(QPen(values["color"], values["thick"], values["style"]))
                painter.drawLine(x1, y1, x2, y2)

        super(display_cell_upgrade_class, self).paint(painter, option, index)
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
        pass

#테이블의 가로세로의 갯수들을 만드는것
class TableModel(QAbstractTableModel):

    def __init__(self, table_data, parent=None):
        super().__init__(parent)
        self.table_data = table_data

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """

        :param parent:
        :return:
        """
        return self.table_data.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """

        :param parent:
        :return:
        """
        return self.table_data.shape[1]

    def data(self, index, role):
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
        cell_obj = self.grid_xy_datas[x][y]
        xy_datas = cell_obj.values

        if role == Qt.DisplayRole:
            # 0 : 문자를 표현하는 방법 (QString)
            # print("data-display-role")

            print("표시 시작 ==> ")
            if xy_datas["kind_2"] == "date" and xy_datas["kind_2"] == "=today()":
                return "2022-08-20"
            elif type(xy_datas["text"]) == type(1):
                return "숫자 : " + str(xy_datas["text"])

            elif xy_datas["kind_2"] == "date" and isinstance(xy_datas["value"], datetime):
                print("닐찌에 대한것 ==> ")
                return xy_datas["value"].strftime('%Y-%m-%d')
            else:
                return xy_datas["text"]

        if role == Qt.DecorationRole:
            # 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)

            if xy_datas["kind_2"] == "date" and isinstance(xy_datas["value"], datetime):
                return QIcon('calendar.png')
            elif xy_datas["kind_2"] == "date" and xy_datas["value"] == "=today()":
                return QIcon('calendar.png')
            elif str(xy_datas["text"]) == "=":
                return QIcon('calendar.png')

        if role == Qt.EditRole:
            # 2   The data in a form suitable for editing in an editor. (QString)
            # 수정할때 나타나는 것
            return xy_datas["text"]

        if role == Qt.ToolTipRole:
            # 3   각 셀마다 툴팁을 설정할수있는것. (QString)
            if xy_datas["kind_1"] == "tool_tip":
                return xy_datas["tool_tip"]
        if role == Qt.StatusTipRole:
            # 4   status bar에 나타나는것 (QString)
            pass

        if role == Qt.WhatsThisRole:
            # 5   The data displayed for the item in "What's This?" mode. (QString)
            pass

        if role == Qt.FontRole:
            # 6   The font used for items rendered with the default delegate. (QFont)
            font = QFont()
            font.setPixelSize(8)
            return Qt.QVariant(font)

        if role == Qt.TextAlignmentRole:
            # 7   The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
            return Qt.QVariant(int(Qt.AlignLeft | Qt.AlignBottom))

        if role == Qt.BackgroundColorRole:
            # 8   The background brush used for items rendered with the default delegate. (QBrush)
            color = xy_datas["background_color"]
            if color:
                return Qt.QVariant(QColor(color[0], color[1], color[2]))

        if role == Qt.ForegroundRole:
            # 9   The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
            font_color = xy_datas["font_dic"]["color"]
            if font_color:
                return Qt.QVariant(QColor(font_color[0], font_color[1], font_color[2]))
            pass

        if role == Qt.CheckStateRole:
            # 10  This role is used to obtain the checked state of an item. (Qt.CheckState)
            pass
        #    if self.grid_xy_datas[row][column].isChecked():
        #        return QVariant(Qt.Checked)
        #    else:
        #        return QVariant(Qt.Unchecked)

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
        # print("data-setdata")
        x = index.row()
        y = index.column()
        cell_obj = self.grid_xy_datas[x][y]
        xy_datas = cell_obj.values

        if role == Qt.EditRole:
            try:
                text = int(xy_datas["text"])
                text = "숫자 : " + str(text)
            except:
                pass

            xy_datas["text"] = value

            self.dataChanged.emit(index, index)
            return True

        if role == Qt.DecorationRole:
            # 1   셀안에 값의 앞부분에 나타나는 아이콘같은 모양의 그림 (QColor, QIcon or QPixmap)
            if isinstance(xy_datas["text"], datetime):
                return QIcon('calendar.png')
            if xy_datas["fun"]:
                if xy_datas["fun"][0] == "date" and xy_datas["fun"][2] == "=today()":
                    return QIcon('calendar.png')

        if role == Qt.CheckStateRole and y == 0:
            self.grid_xy_datas[x][y] = QCheckBox('')
            if xy_datas["text"] == Qt.Checked:
                self.grid_xy_datas[x][y].setChecked(True)
            else:
                self.grid_xy_datas[x][y].setChecked(False)
            self.dataChanged.emit(index, index)
            return True
        return False

#    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        #if orientation == Qt.Horizontal and role == Qt.DisplayRole:
#            return str(self.table_data.columns[section])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            # y축의 header글자를 넣는것
            if orientation == Qt.Horizontal:
                if section < len(self.headers_titles):
                    # header의 자료로 넘어오는것이 잇으면 그것을 사용하는 것이다
                    return self.headers_titles[section]
                else:
                    return "Y-%d" % (section + 1)

            if orientation == Qt.Vertical:
                # x축의 header글자를 넣는것
                return "X-%d" % (section + 1)


    def setColumn(self, col, array_items):
        """Set column data"""
        self.table_data[col] = array_items
        # Notify table, that data has been changed
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def getColumn(self, col):
        """Get column data"""
        return self.table_data[col]

#테이블이 실행후에 이벤트를 만든다
class CreateTable(QTableWidget): # QTableWidget

    def __init__(self, row, col): # Index, ColumnHeaders
        super(CreateTable, self).__init__()

        self.cliptext = [] # undo가가능하도록 하는것
        self.history = []
        self.x = ""
        self.y = ""
        self.xy = ""
        self.xx= [0, 0]
        self.yy = [0, 0]
        self.xyxy = [0, 0, 0, 0]

        self.old_item = ""
        self.old_cell = ""
        self.old_text = ""

        self.selected_xyxy = ""
        self.usedrange = [0, 0]

        self.max_x = 1
        self.max_y = 1
        self.max_x_len = row
        self.max_y_len = col

        self.cell_drag_t = 10
        self.cell_drag_h = 20
        self.cell_drag_w = 20

        self.basic_font = "맑은 고딕"
        self.basic_font_bold = False
        self.basic_font_size = 10

        #기본적인 설정을 하는 곳
        self.var = {}
        self.var["odd_y_colored"] = True # 반복되는 행의 색깔을 지정하는 코드
        self.var["one_page_no"] = 25 # page up/down을 누르면 변하는 갯수들
        self.var["basic_cell_width"] = 85
        self.var["basic_cell_height"] = 27
        self.var["mouse_tracking"] = True

        self.var["line_select"] = False #1줄씩 선택하도록 하는 것
        self.var["cell_edit_no"] = False #모든셀의 수정을 못하게 하는것
        self.var["no_grid_line"] = False #그리드라인을 안보이게
        self.var["no_header_x"] = False # 열번호 안나오게 하는 코드
        self.var["no_header_y"] = False # 행번호 안나오게 하는 코드

        stylesheet_1 = "::section{Background-color:rgb(255,236,236)}"
        stylesheet_2 = "::section{Background-color:rgb(236,247,255)}"

        self.setMouseTracking(True)
        self.setRowCount(row)
        self.setColumnCount(col)
        self.horizontalHeader().setStyleSheet(stylesheet_1)
        self.verticalHeader().setStyleSheet(stylesheet_2)

        h_labells = [f"y-{a}" for a in range(1, col+1)]
        v_labells = [f"x-{a}" for a in range(1, row+1)]
        self.setHorizontalHeaderLabels(h_labells)
        self.setVerticalHeaderLabels(v_labells)

        #header설정에 대한것
        #self.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        #header에서 마우스오른쪽을 누르면 나타나는메뉴
        self.horizontalHeader().customContextMenuRequested.connect(self.menu_header_y)
        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        #header에서 마우스오른쪽을 누르면 나타나는메뉴
        self.verticalHeader().customContextMenuRequested.connect(self.menu_header_x)

        self.set_basic_setting()
        #화면에 나오게 하기 위해 설정이 필요


        # 기본적인 event에 대한 설정하는 부분
        self.currentCellChanged.connect(self.action_current_cell_changed)
        self.currentItemChanged.connect(self.action_current_item_changed)
        self.cellChanged.connect(self.action_cell_changed)
        self.cellEntered.connect(self.action_cell_entered)
        self.cellActivated.connect(self.action_cell_activated)
        self.itemChanged.connect(self.action_item_changed)
        self.itemSelectionChanged.connect(self.action_item_selection_changed)
        self.itemClicked.connect(self.action_item_clicked)

    def set_no_scrollbar(self):
        #스크롤바를 없애는 것
        """
        setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        verticalScrollBar()->hide();
        verticalScrollBar()->resize(0, 0);
        """
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWindowFlags(Qt.FramelessWindowHint)

        header1 = self.horizontalHeader()  # 테이블의 세로 길이 설정
        header1.setStretchLastSection(True)  # 맨마지막 남는 길이는 자동으로 늘리는것

        header2 = self.verticalHeader()  # 테이블의 세로 길이 설정
        header2.setStretchLastSection(True)  # 맨마지막 남는 길이는 자동으로 늘리는것

        self.verticalHeader().hide()
        self.horizontalHeader().hide()





    ###################################### 이벤트 실행용
    def keyPressEvent(self, e):
        """

        :param e:
        :return:
        """

        #x0, y0 = self.read_first_xy_in_selection()

        x0, y0 = self.x, self.y

        ctrl_key = ""
        shift_key = ""
        alt_key = ""

        if e.modifiers() & Qt.ControlModifier: ctrl_key = "on"
        if e.modifiers() & Qt.ShiftModifier: shift_key = "on"
        if e.modifiers() & Qt.AltModifier: alt_key = "on"

        if ctrl_key == "" and shift_key == "" and alt_key == "":
            if e.key() == Qt.Key_Delete:
                print('press key : Delete')
                # self.press_delete_key()
            elif e.key() == Qt.Key_Backspace:
                print('press key : Backspace')
            elif e.key() in [Qt.Key_Return, Qt.Key_Enter]:
                print('press key : Enter')
                # self.press_enter_key()
            elif e.key() == Qt.Key_Escape:
                print('press key : Escape')
                self.clearSelection()
            elif e.key() == Qt.Key_Right:
                print('press key : Right')
                if y0 + 1 > self.max_y_len - 1: y0 = y0 - 1
                self.setCurrentCell (x0, y0+1)
            elif e.key() == Qt.Key_Left:
                if y0 - 1 < 0: y0 = 1
                print('press key : Left')
                self.setCurrentCell (x0, y0-1)
            elif e.key() == Qt.Key_Up:
                print('press key : Up')
                if x0 - 1 < 0: x0 = 1
                self.setCurrentCell(x0 - 1, y0)
            elif e.key() == Qt.Key_Down:
                print('press key : Down')
                if x0 + 1 > self.max_x_len - 1: x0 = x0 - 1
                self.setCurrentCell(x0 + 1, y0)
            elif e.key() == Qt.Key_Insert:
                print('press key : Insert')
            elif e.key() == Qt.Key_PageUp:
                print('press key : PageUp')
                if x0 - self.var["one_page_no"] < 0 :
                    x0 = 0
                else:
                    x0 = x0 - 25
                self.setCurrentCell(x0, y0)
            elif e.key() == Qt.Key_PageDown:
                print('press key : PageDown')
                if x0 + self.var["one_page_no"] > self.max_x_len - 1:
                    x0 = self.max_x_len - 1
                else:
                    x0 = x0 + 25
                self.setCurrentCell(x0, y0)

            elif e.key() == Qt.Key_Home:
                print('press key : Home')
                self.clearSelection()
                self.setCurrentCell(x0, 0)
            elif e.key() == Qt.Key_End:
                print('press key : End')
            else:
                pass

        if ctrl_key == "" and shift_key == "on" and alt_key == "":
            print('press key : Shift')

        if ctrl_key == "" and shift_key == "" and alt_key == "on":
            print('press key : Alt')

        if ctrl_key == "on" and shift_key == "" and alt_key == "":
            if e.key() == Qt.Key_A:
                print("press key : Ctrl + A")
                self.selectAll()
            elif e.key() == Qt.Key_B:
                print("press key : Ctrl + B")
            elif e.key() == Qt.Key_C:
                print("press key : Ctrl + C")
                # self.press_copy_key()
            elif e.key() == Qt.Key_V:
                print("press key : Ctrl + V")
                # self.press_paste_key()
            elif e.key() == Qt.Key_X:
                print("press key : Ctrl + X")
                # self.paste_cut_key()
            elif e.key() == Qt.Key_Z:
                print("press key : Ctrl + Z")
                # self.undo()
            elif e.key() == Qt.Key_Right:
                self.clearSelection()
                print('press key : Ctrl + Right')
                self.setCurrentCell(x0, self.max_y_len - 1)
            elif e.key() == Qt.Key_Left:
                print('Ctrl + Left')
                self.clearSelection()
                self.setCurrentCell(x0, 0)
            elif e.key() == Qt.Key_Up:
                self.clearSelection()
                print('Ctrl + Up')
                self.setCurrentCell(0, y0)
            elif e.key() == Qt.Key_Down:
                self.clearSelection()
                print('Ctrl + Down')
                self.setCurrentCell(self.max_x_len - 1, y0)
            else:
                pass

    def mouseMoveEvent(self, event):
        """
        마우스가 움직이면 자동으로 실행되는 기본 이벤트
        """
        super(CreateTable, self).mouseMoveEvent(event)

        mouse_xpx = event.x()
        mouse_ypx = event.y()

        #item = self.itemAt(event.pos())
        #item_x = self.row(item)
        #item_y = self.column(item)

        cell = self.indexAt(event.pos())
        cell_rect = self.visualRect(cell)

        #x : computer x,  컴퓨터에서사용하는 x로 0부터시작하는것, px : person x (사람을 위한것만 px로 사용하자)
        #cell_x = cell.row()
        #cell_y = cell.column()

        #cell_x_width = cell_rect.width()
        #cell_y_height = cell_rect.height()

        cell_x0px = cell_rect.x()
        cell_y0px = cell_rect.y()

        cell_x1px = cell_x0px + cell_rect.width()
        cell_y1px = cell_y0px + cell_rect.height()

        cell_x2px = cell_x1px - self.cell_drag_w
        cell_y2px = cell_y1px - self.cell_drag_t

        cell_x3px = cell_x1px - self.cell_drag_t
        cell_y3px = cell_y1px - self.cell_drag_h

        #오른쪽 하단에 마우스가 오면 십자모양으로 커서가 변경되게 하였다
        if (cell_x2px < mouse_xpx and cell_x1px > mouse_xpx and cell_y2px < mouse_ypx and cell_y1px > mouse_ypx) or (cell_x3px < mouse_xpx and cell_x1px > mouse_xpx and cell_y3px < mouse_ypx and cell_y1px > mouse_ypx):
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def action_cell_activated(self, now_x, now_y):
        #셀이 활성화되면 실행되는것
        print("action_cell_activated", now_x, now_y)

    def action_current_cell_changed(self, x, y, old_x, old_y):
        """
        이젠에 선택된 셀에서 다른 셀이 선택되었을때, 같은셀이 선택되면 실행되지 않는다
        Item이 있고 없고는 상관없음
        range를 선택하면, 마지막셀만 나타내고, old_x, old_y는 드래그하는동안의 주소가 넘어간다
        마우스클릭이 된것을 파악해서 정리해야 함
        """
        self.currunt_x = x
        self.currunt_y = y
        self.old_x = old_x
        self.old_y = old_y
        #print("현재위치 ==> ", x, y, "이전위치 ==> ", old_x, old_y)

    def action_current_item_changed(self, item):
        """
        item이 다른것으로 선택되었을때, 같은것을 다시한번 클릭하면 적용이 않된다
        self.select_item_changed = "yes"
        1개가 아닌 여러 영역을 선택하면 제일 마지막 셀만 위치만 가리키며
        1개의 셀 위치만 나타냄
        새로운 item이 넘어오는 것이다
        """
        if item:
            x = item.row()
            y = item.column()
            self.select_item_xy = [x, y]
            self.item = item
            print("action_current_item_changed", x, y)

    def action_cell_changed(self, x, y):
        """
        셀값이 변경되었을때,
        None셀이던 아니던 상관없음
        """
        try:
            self.value = self.item(x, y).text()
            print("action_cell_changed", x, y)

            # cells = self.read_attribute_in_range([x, y])
            # self.old_cell = {"type": "change", "range": [x, y], "cells": cells}
            # self.check_max_xy(x, y)
            #print("입력값이 변경되었네요", (x, y), input_text)
            #셀에 입력이 "="으로 입력되었을때 적용하는것
            #if input_text == "=1":
            #    self.add_combo_in_cell([2, 2], ["abc", "def", "xyz"])
            #elif input_text == "=2":
                #print("=2 를 입력했네요")
            #    self.add_combo_in_cell([3, 3], ["111abc", "222def", "333xyz"])
        except:
            pass

    def action_item_selection_changed(self ):
        """
        셀이 선택되면 실행
        어떤 형태의 셀이라도 좋음
        """
        try:
            selected_range = self.read_address_in_selection()[0]
            seleted_items = self.selectedItems()
            #print("action_item_selection_changed ==> ", selected_range)
            #print("selection_item ==> ", seleted_items)

            #self.setSelection()
        except:
            pass

    def action_item_clicked(self, item):
        """
        1. item이있는 셀을 클릭이나 더블클릭하면 실행되는것
        2. 빈셀에 입력을위해 더블클릭해서 들어가는 순간에 입력을 하던 아니던 item이 만들어 진것이고, 만약 다시 그곳을 클릭하면 실행됨
        여러영역이 선택되어질때는 실행되지 않는다
        """
        x = item.row()
        y = item.column()
        self.old_item = item
        print("item이 있는 셀을 클락했읍니다", [x,y])

    def action_item_changed(self, item):
        """
        마우스가 셀위를 움직일때, 선택한것은 아니며, item이있는 셀만 알려준다
        기본 item을 변경하는 것이 적용될때
        1. item의 선택이 바뀔때 (마우스로)
        2. item안의 값이 바뀔때 실행된다
        """
        self.item = item
        self.x = item.row()
        self.y = item.column()
        #print("item이 변경됨")


            #print(input_text)
            #셀에 입력이 "="으로 입력되었을때 적용하는것
        #    if input_text[0:2] == "=1":
        #        self.add_combo_in_cell(2, 2, ["abc", "def", "xyz"])
        #    elif input_text[0:2] == "=2":
        #        self.add_combo_in_cell(3, 3, ["111abc", "222def", "333xyz"])
        #except:
        #    pass

    def action_cell_entered(self, now_x, now_y):
        """
        마우스가 셀에 접근하면 실행되는 코드를 만들수 있다
        너무 많이 실행되서 pass로 만든다
        """
        #print("마우스가 셀안으로 이동 ==> ",now_x+1, now_y+1)
        pass

    def add_cols(self, xyxy):
        """

        :param xyxy:
        :return:
        """
        xyxy = self.read_select_address()[0]
        for x in (xyxy[0], xyxy[2]):
            self.InsertCols(x)
        self.add_history({"type": "add_cols", "range": [xyxy[0], 0, xyxy[2], 0], "cells": ""})

    def add_rows(self, xyxy):
        """

        :param xyxy:
        :return:
        """
        xyxy = self.read_select_address()[0]
        for y in range(xyxy[1], xyxy[3]):
            self.insertRow(y)
        self.add_history({"type": "add_rows", "range": [0, xyxy[1], 0, xyxy[3]], "cells": ""})

    def add_history(self, change):
        """

        :param change:
        :return:
        """
        self.history.append(change)

    def contextMenuEvent(self, event):
        """
        마우스 오른쪽으로 누르면 나타나는 메뉴를 만드는 것
        """
        menu = QMenu(self)
        aaa = menu.addAction("test")
        copy_action = menu.addAction("복사하기")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == quit_action:
            #pass
            #아직 잘 되지 않음
            app.quit
        elif action == copy_action:
            print("copy...")
        elif action == aaa:
            print("test...")

    def check_usedrange(self, xyxy):
        """

        :param xyxy:
        :return:
        """
        if len(xyxy) == 2:
            self.usedrange[0] = max(xyxy[0], self.usedrange[0])
            self.usedrange[1] = max(xyxy[0], self.usedrange[1])
        else:
            self.usedrange[0] = max(xyxy[0], self.usedrange[0], self.usedrange[2])
            self.usedrange[1] = max(xyxy[0], self.usedrange[1], self.usedrange[3])

    def check_address(self, xyxy):
        """
        주소를 확인하는 코드
        입력값 : [x0, y0, x1, y1], [x0, y0]
        결과값 : [x0, y0, x1, y1]
        아무것도 없으면 [0, 0, 0, 0]이 나타난다
        """
        if len(xyxy) ==2:
            x0, y0, x1, y1 = [xyxy[0], xyxy[1], xyxy[0], xyxy[1]]
        elif len(xyxy) ==4:
            x0, y0, x1, y1 = [xyxy[0], xyxy[1], xyxy[2], xyxy[3]]
        elif xyxy == []:
            x0, y0, x1, y1 = [0, 0, 0, 0]

        #최소와 최대의 위치를 변경하는 것이다
        x0_checked = min(x0, x1)
        x1_checked = max(x0, x1)
        y0_checked = min(y0, y1)
        y1_checked = max(y0, y1)
        x0, y0, x1, y1 = x0_checked, x1_checked, y0_checked, y1_checked
        result = [x0, y0, x1, y1]

        return result

    def copy_item_object_in_xxline(self, xx):
        #선택한 영역의 1개의 item객체를 복사하는 것이다
        #복사를 하기위해서는 clone을 이용해야 한다

        result = []
        y_no = self.max_y_len
        #print("y_no",y_no)

        for x in range(xx[0], xx[1]+1):
            temp = []
            for y in range(0, y_no):
                self.old_item = self.item(x, y)
                one_item = self.old_item.clone()
                temp.append(one_item)
            result.append(temp)
        return result

    def copy_item_object_in_cell(self, xy):
        """
        선택한 영역의 1개의 item객체를 복사하는 것이다
        복사를 하기위해서는 clone을 이용해야 한다
        """
        self.old_item = self.item(xy[0], xy[1])
        result = self.old_item.clone()
        return result

    def check_data_limit(self, xyxy, input_data):
        """
        자료가 넘어온것이 범위를 넘어가지 않는지를 확인하는것
        """
        input_data_status = "good"
        input_xyxy_status = "good"

        #xyxy의 값을 확인한다
        x0, y0, x1, y1 = 0,0,0,0
        if len(xyxy) == 2 :
            x0, y0, x1, y1 = xyxy[0], xyxy[1], xyxy[0], xyxy[1]
        elif  len(xyxy) == 4 :
            x0, y0, x1, y1 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
        else:
            input_xyxy_status = "error"

        if input_xyxy_status == "good":
            x0_checked = min(x0, x1)
            x1_checked = max(x0, x1)
            y0_checked = min(y0, y1)
            y1_checked = max(y0, y1)
            x0, y0, x1, y1 = x0_checked, x1_checked, y0_checked, y1_checked

        #input_data의 갯수를 확인한다
        input_data_x_max = len(input_data)
        input_data_y_max = 1
        if type(input_data) == type("123") or type(input_data) == type(123):
            input_data_x_max = 1
            input_data_y_max = 1
        elif type(input_data) == type([123]) or type(input_data) == type((123)):
            input_data_x_max = len(input_data)
            for no in input_data:
                if type(input_data[no]) == type([123]) or type(input_data[no]) == type((123)):
                    input_data_y_max = max(input_data_y_max, len(input_data[no]))
                elif type(input_data) == type("123") or type(input_data) == type(123):
                    input_data_y_max = 1
                else:
                    input_data_status = "error"
        else:
            input_data_status = "error"


        x0_new = x0 + input_data_x_max
        x1_new = x1 + input_data_y_max
        y0_new = y0 + input_data_x_max
        y1_new = y1 + input_data_y_max


        if x0_new > self.max_x_len - 1:
            if x0 > self.max_x_len - 1:
                input_data_status = "error"
            else:
                input_xyxy_status = "good"
        elif int(x0) < self.max_x_len - 1 and int(x1) > self.max_x_len - 1:
            x1 = self.max_x_len - 1
            input_range_status = "error"
        elif int(x0) > self.max_x_len - 1 and int(x1) > self.max_x_len - 1:
            x1 = self.max_x_len - 1
            input_range_status = "error"
        elif int(x0) > self.max_x_len - 1 and int(x1) > self.max_x_len - 1:
            x1 = self.max_x_len
            input_range_status = "error"

        if int(y0) > self.max_x_len - 1: result = "error"
        if int(x0) < self.max_x_len - 1 and int(x1) > self.max_x_len - 1:
            x1 = self.max_x_len

        return result

    def check_max_xy(self, x, y):
        """
        usedrange를 확정하기위해 사용되는것

        :param x:
        :param y:
        :return:
        """
        if x !="":
            self.max_x = max(x, self.max_x)
        if y !="":
            self.max_y = max(y, self.max_y)

    def check_used_range(self, xyxy):
        """

        :param xyxy:
        :return:
        """
        if len(xyxy) == 2:
            self.usedrange[0] = max(xyxy[0], self.usedrange[0])
            self.usedrange[1] = max(xyxy[0], self.usedrange[1])
        else:
            self.usedrange[0] = max(xyxy[0], self.usedrange[0], self.usedrange[2])
            self.usedrange[1] = max(xyxy[0], self.usedrange[1], self.usedrange[3])

    def delete_range_select(self, many_range):
        # selected ranges
        #print("delete action")
        for xyxy in many_range:
            for x in range(xyxy[0], xyxy[2]+1):
                for y in range(xyxy[1], xyxy[3]+1):
                    self.setItem(x, y, QTableWidgetItem(""))

    def delete_cell_attribute(self, xy):
        # 옛날 작성한것을 위한 보관용
        # delete_attribute_in_cell로 변경
        self.removeCellWidget(xy[0], xy[1])

    def delete_attribute_in_range(self, xyxy):
        # tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        # 즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        for x in range(xyxy[0], xyxy[2] + 1):
            for y in range(xyxy[1], xyxy[3] + 1):
                self.removeCellWidget(x, y)

    def delete_attribute_in_cell(self, xy):
        # tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        # 즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        self.removeCellWidget(xy[0], xy[1])

    def delete_attribute_in_yline(self, y_no):
        # 세로열의 1줄의 모든 위젯을 삭제하는 것
        for no in range(self.max_x_len):
            self.removeCellWidget(no, y_no)

    def delete_attribute_for_all_cells(self):
        self.clear()

    def remove_y_line(self, y_no):
        self.removeColumn(y_no)

    def remove_x_line(self, x_no):
        self.removeRow(x_no)

    def delete_cols(self, xyxy):
        xyxy = self.read_select_address()[0]
        cells = self.read_attribute_in_xxline(xyxy)
        for y in range(xyxy[2], xyxy[0], -1):
            self.removeColumn(y)
        self.add_history({"type": "delete_cols", "range": [xyxy[0], 0, xyxy[2], 0], "cells": cells})

    def delete_rows(self, xyxy):
        """

        :param xyxy:
        :return:
        """
        xyxy = self.read_select_address()[0]
        cells = self.read_attribute_in_yyline(xyxy)
        for y in range(xyxy[3], xyxy[1], -1):
            self.removeRow(y)
        self.add_history({"type": "delete_rows", "range": [0, xyxy[1], 0, xyxy[3]], "cells": cells})

    def delete_yyline_in_range(self, yy=""):
        """

        :param yy:
        :return:
        """
        self.model = QStandardItemModel()
        """
        yy열을 삭제하는 것이다
        """
        #print("delete yy")
        if yy =="":
            aa = self.read_address_in_selection()[0]
            yy = [aa[1], aa[3]]
        #print("delete yy", aa)

        if len(yy) == 4:
            y0 = yy[1]
            y1 = yy[3]
        elif len(yy) == 2:
            y0 = yy[0]
            y1 = yy[1]

        y0_checked = min(y0, y1)
        y1_checked = max(y0, y1)
        #selected_rows = self.selectionModel().selectedColumns()

        #model = self.model
        #indices = self.tableView.selectionModel().selectedRows()
        #for index in sorted(indices):
        #    model.removeColumn(index.column(), Qt.QModelIndex())

        indexes = self.selectionModel().selectedColumns()
        for index in reversed(sorted(indexes)):
            #print('Column %d is selected' % index.column())
            self.removeColumn(3)


        #for each_row in reversed(sorted(selected_rows)):
        #    print(each_row.column())
        #    self.model.removeColumn(each_row.column())
            #self.removeColumn(each_row.column())

        #for y in range(y0_checked, y1_checked + 1):
                #if y < self.max_y_len - 1:
                #aa = self.setItem(0, y,"")

        #        print("삭제할 y열은 ==>", y)
                #item1 = self.itemFromIndex(y)
                # if y < self.max_y_len - 1:
                #self.insertColumn(item1.column())
                #self.clearSelection()
        #        self.removeColumn(item1.column())
            #self.add_history({"action": "delete_yyline_in_range", "range": [0, xyxy[1], 0, xyxy[3]], "cells": cells})

    def delete_value_in_range(self, input_2drange):
        """
        영역의 값만을 삭제하는 것이다
        2차원 영역이 입력되어야 한다
        입력값 : [[1,2,3,4], [5,6,7,8]]
        """
        #혹시 1차원의 리스트가 들어오면 2차원으로 만들어 주는 것이다
        if type(input_2drange[0]) !=type([]):
            input_2drange = [input_2drange]

        for xyxy in input_2drange:
            xyxy = self.check_address(xyxy)
            for x in range(xyxy[0], xyxy[2]+1):
                if x < self.max_x_len - 1:
                    for y in range(xyxy[1], xyxy[3]+1):
                        if y < self.max_y_len - 1:
                            self.delete_value_in_cell([x, y])

    def delete_value_in_cell(self, xy):
        # 선택된 셀의 item의 text를 ""으로 만드는 것이다
        # 다른 속성은 그대로 유지한다

        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            old_item = self.item(xy[0], xy[1])
            if old_item:
                pass
            else:
                old_item = self.item(xy[0], xy[1])
                old_item.text = ""
                self.setItem(xy[0], xy[1], old_item)

    def delete_widget_in_cell(self, xy):
        """
        tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        """
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.removeCellWidget(xy[0], xy[1])

    def delete_widget_in_range(self, xyxy):
        # 모든 버튼이나 객체들을 지우는 것
        x1, y1, x2, y2 = xyxy
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                self.delete_widget_in_cell([x, y])

    def delete_item_object_in_cell(self, xy):
        """
        tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        """
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setItem(xy[0], xy[1], QTableWidgetItem())

    def delete_xxline_in_range(self, xx=""):
        """
        xx열을 삭제하는 것이다
        """

        #print("delete_xxline_in_range")
        if xx =="":
            aa = self.read_address_in_selection()[0]
            #print("선택영역은", aa)
            xx = [aa[0], aa[2]]
        if len(xx) ==4:
            x0 = xx[0]
            x1 = xx[2]
        elif len(xx) ==2:
            x0 = xx[0]
            x1 = xx[1]

        x0_checked = min(x0, x1)
        x1_checked = max(x0, x1)

        for x in range(x1_checked, x0_checked-1, -1):
            if x < self.max_x_len - 1:
                self.removeRow(x)
                #self.removeColumn(x)
            #self.add_history({"action": "delete_xxline_in_range", "range": [xyxy[0], 0, xyxy[2], 0], "cells": cells})

    def get_colordialog_color(self):
        """
        프로그래스 바를 만드는 것이다
        """
        result = QColorDialog.getColor()
        return result

    def get_all_attribute_in_item(self, item):
        """
        넘어온 item의 속성을 저장하는 것인데, 이것은 차후에 그냥 Item을 Clone해서 저장을 하여도 된다
        """
        item_dic = {"background" : item.background(), #배경색
                    "column": item.column(),  #y열
                    "flags": item.flags(),
                    "font": item.font(), #폰트
                    "icon": item.icon(),
                    "isselected": item.isSelected(), #선택되었을때
                    "row": item.row(), #x열
                    "text": item.text(), #텍스트값
                    "textalignment": item.textAlignment(), #텍스트 정렬
                    "textcolor": item.textColor(), #텍스트색
                    "tooltip": item.toolTip(),
                    "type": item.type(),
                    }
        return item_dic

    def isPrintable(key):
        """

        :return:
        """
        printable = [
            Qt.Key_Space, Qt.Key_Exclam, Qt.Key_QuoteDbl, Qt.Key_NumberSign, Qt.Key_Dollar,
            Qt.Key_Percent, Qt.Key_Ampersand, Qt.Key_Apostrophe, Qt.Key_ParenLeft, Qt.Key_ParenRight,
            Qt.Key_Asterisk, Qt.Key_Plus, Qt.Key_Comma, Qt.Key_Minus, Qt.Key_Period, Qt.Key_Slash,
            Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
            Qt.Key_Colon, Qt.Key_Semicolon, Qt.Key_Less,
            Qt.Key_Equal, Qt.Key_Greater,
            Qt.Key_Question, Qt.Key_At,
            Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
            Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
            Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z,
            Qt.Key_BracketLeft, Qt.Key_Backslash, Qt.Key_BracketRight, Qt.Key_AsciiCircum,
            Qt.Key_Underscore, Qt.Key_QuoteLeft, Qt.Key_BraceLeft, Qt.Key_Bar,
            Qt.Key_BraceRight, Qt.Key_AsciiTilde, Qt.Key_Insert, Qt.Key_PageUp,
            Qt.Key_PageDown, Qt.Key_End, Qt.Key_Home,
        ]
        if key in printable:
            return True
        else:
            return False

    def insert_xxline_in_range(self, xx=""):
        """
        xx열을 삽입하는 것이다
        """
        if xx =="":
            aa = self.read_address_in_selection()[0]
            xx = [aa[0], aa[2]]

        if len(xx) ==4:
            x0 = xx[0]
            x1 = xx[2]
        elif len(xx) ==2:
            x0 = xx[0]
            x1 = xx[1]

        x0_checked = min(x0, x1)
        x1_checked = max(x0, x1)


        for x in (x0_checked, x1_checked+1):
            if x < self.max_x_len - 1:
                self.insertRow(x)
            #self.add_history({"action": "insert_xxline_in_range", "range": xyxy})

    def insert_yyline_in_range(self, yy=""):
        """
        yy열을 삽입하는 것이다
        """
        if yy =="":
            aa = self.read_address_in_selection()[0]
            yy = [aa[1], aa[3]]

        if len(yy) ==4:
            y0 = yy[1]
            y1 = yy[3]
        elif len(yy) ==2:
            y0 = yy[0]
            y1 = yy[1]

        y0_checked = min(y0, y1)
        y1_checked = max(y0, y1)

        #item = self.itemAt(event.pos())
        #item_x = self.row(item)
        #item_y = self.column(item)


        #xyxy = self.read_address_in_selection()[0]
        #cells = self.read_attribute_in_yyline(xyxy)
        for y in range(y0_checked, y1_checked+1):
            if y < self.max_y_len - 1:
                self.insertColumn(y)
            #self.add_history({"action": "delete_yyline_in_range", "range": [0, xyxy[1], 0, xyxy[3]], "cells": cells})

    def paint_color_in_cell(self, xy, input_rgb=[123,123,123]):
        """

        :param xy:
        :param input_rgb:
        :return:
        """
        now_item = self.item(xy[0], xy[1])
        if now_item:
            pass
        else:
            now_item = QTableWidgetItem()
        now_item.setBackground(QColor(input_rgb[0], input_rgb[1], input_rgb[2]))
        self.setItem(xy[0], xy[1], now_item)

        #value = self.read_value_in_cell(xy)
        #aaa = self.setItem(xy[0], xy[1], QTableWidgetItem())
        #aaa.setBackground(input_color)
        #item1 = QTableWidgetItem(value)
        #item1.setBackground(QColor(input_color[0], input_color[1], input_color[2]))
        #self.setItem(xy[0], xy[1], item1)
        #self.setItem(xy[0], xy[1], QTableWidgetItem())
        #self.item(xy[0], xy[1]).setBackground(QColor(255, 128, 128))
        #self.setStyleSheet("QTableWidget::item::selected { background-color:#F9F6F5 ; color:black; border: 3px  solid black;}")

    def menu_header_x(self, pos):
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
            self.delete_xxline_in_range()
        elif selected_menu == ddd:
            print("1번을 눌렀네요")

    def menu_header_y(self, pos):
        """
        Header에서 마우스 오른쪽으로 누르면 나타나는 메뉴를 만드는 것
        """
        global_pos = self.mapToGlobal(pos)
        menu = QMenu()
        ddd = menu.addAction("y해드의 1번을 누르세요")
        del_yy_action = menu.addAction("yy삭제하기")
        quit_action = menu.addAction("Quit")

        selected_menu = menu.exec_(self.viewport().mapToGlobal(pos))
        if selected_menu == quit_action:
            print("Quit을 눌렀네요")
        elif selected_menu == del_yy_action:
            self.delete_yyline_in_range()
        elif selected_menu == ddd:
            print("1번을 눌렀네요")

    def paste_item_object_in_xxline(self, xx, input_2ditem):
        #선택한 영역의 1개의 item객체를 복사하는 것이다
        #복사를 하기위해서는 clone을 이용해야 한다

        for x in range(xx[0], xx[1]+1):
            y_no = len(input_2ditem[x-xx[0]])
            for y in range(0, y_no):
                self.setItem(x, y, input_2ditem[x-xx[0]][y])

    def paste_item_object_in_cell(self, xy, old_item):
        """
        복사한것을 붙여넣기 하는 것이다
        """
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setItem(xy[0], xy[1], old_item)

    def press_cut_key(self):
        self.press_copy_key()
        self.press_delete_key()

    def press_paste_key(self):
        input_text = pyperclip.paste()
        result = []
        semi_list = input_text.split("\n")
        for one_text in semi_list:
            temp = one_text.split("\t")
            result.append(temp)

        xyxy = self.read_address_in_selection()[0]
        self.write_value_in_range(result, [xyxy[0][0], xyxy[0][1]])

    def press_copy_key(self):
        self.cliptext = []
        xyxy = self.read_address_in_selection()[0]
        #print("press_copy_key ==>", xyxy)
        result = ""
        if len(xyxy)==2:
            xyxy = [xyxy[0], xyxy[1], xyxy[0], xyxy[1]]

        for x in range(xyxy[0], xyxy[2]+1):
            temp = []
            for y in range(xyxy[1], xyxy[3]+1):
                item_temp = self.item(x, y)
                if item_temp is not None:
                    value = item_temp.text()
                else:
                    value = ""
                temp.append(value)
                result = result+value +"\t"
            result = result[:-2]+"\n"
            self.cliptext.append(temp)
        #print("press_copy_key, cliptext ==>", self.cliptext)
        pyperclip.copy(result[:-2])
        return result

    def press_delete_key(self):
        #print("delete")
        xyxy_s = self.read_address_in_selection()[0]
        cells = []
        for xyxy in xyxy_s:
            cell = self.read_attribute_in_range(xyxy)
            cells.append(cell)
        self.delete_value_in_range(xyxy_s)
        self.add_history({"action": "delete", "range": xyxy_s, "cells": cells})

    def press_enter_key(self):
        current = self.currentIndex()
        nextIndex = current.sibling(current.row() + 1, current.column())
        self.setItem(current.row() + 1, current.column(), QTableWidgetItem(str("")))
        if nextIndex.isValid():
            self.setCurrentCell(current.row() + 1, current.column())
            self.edit(nextIndex)

    def read_attribute_in_range(self, xyxy):
        """
        선택한영역의 주소와 속성을 하나씩 저장하는 것이다
        결과물 = [[x,y,값]....]
        """
        result = []
        if len(xyxy) == 2:
            xyxy = [xyxy[0], xyxy[1], xyxy[0], xyxy[1]]

        for x in range(xyxy[0], xyxy[2]):
            for y in range(xyxy[1], xyxy[3]):
                result.append([x, y, self.item(x, y).text()])
        return result

    def read_attribute_in_yyline(self, xyxy):
        """
        세로를 삭제하였을때 값과 속성을 하나씩 저장하는 것이다
        """
        old_xyxy = self.read_address_in_selection()[0]
        end_xy = self.usedrange
        xyxy = [0, old_xyxy[1], end_xy[0], old_xyxy[3]]
        result = []
        for x in range(xyxy[0], xyxy[2]):
            temp = {}
            for y in range(xyxy[1], xyxy[3]):
                # 추가로 속성을 넣을수있도록 만든것이다
                temp["x"] = x
                temp["y"] = y
                temp["value"] = self.item(x, y).text()
            result.append(temp)
        return result

    def read_attribute_in_xxline(self, xyxy):
        # 가로를 삭제하였을때 값과 속성을 하나씩 저장하는 것이다
        old_xyxy = self.read_address_in_selection()[0]
        end_xy = self.usedrange
        xyxy = [old_xyxy[0], 0, old_xyxy[2], end_xy[1]]
        result = []
        for x in range(xyxy[0], xyxy[2]):
            temp = {}
            for y in range(xyxy[1], xyxy[3]):
                # 추가로 속성을 넣을수있도록 만든것이다
                temp["x"] = x
                temp["y"] = y
                temp["value"] = self.item(x, y).text()
            result.append(temp)
        return result

    def read_value_in_cell(self, xy):
        """
        cell의 값을 읽어오는것
        만약 Item이 없으면
        """
        xy = self.check_address(xy)
        try:
            result = self.item(xy[0], xy[1]).text()
        except:
            result = ""
        return result

    def read_value_in_range(self, xyxy):
        """
        영역안의 값을 읽어오는것
        item이 아닌것만 갖고오는 것이다
        """
        result = []
        for x in range(xyxy[0], xyxy[2]):
            temp = []
            for y in range(xyxy[1], xyxy[3]):
                try:
                    value = self.item(x, y).text()
                except:
                    value = ""
                temp.append(value)
            result.append(temp)
        self.max_x = max(xyxy[2], self.max_x)
        self.max_y = max(xyxy[3], self.max_y)
        return result

    def read_address_in_all_selection(self):
        """
        현재 선택된것이 아니고 전에 선택되어졌던 영역을 돌려준다
        선택한 여러영역의 좌표를 돌려준다 ===> [[1,2,7,4],[5,6,7,8],[9,10,11,12]]
        만약 영역이 선택되어있지 않으면 [[]]를 돌려준다
        """
        selected_range = self.selectedRanges()
        result = []
        if selected_range:
            for idx, sel in enumerate(selected_range):
                [x0, y0, x1, y1] = [sel.topRow(), sel.leftColumn(), sel.bottomRow(), sel.rightColumn()]
                if self.max_x_len == x1 + 1: x1 = 0
                if self.max_y_len == y1 + 1: y1 = 0
                result.append([x0, y0, x1, y1])
        else:
            result = [[]]
        return result

    def read_address_in_selection(self):
        """
        현재 선택된 영역을 돌려 준다
        """
        result = []
        range_s = self.selectedRanges()
        for range in range_s:
            result.append([range.topRow(), range.leftColumn(), range.bottomRow(), range.rightColumn()])
        return result

    def read_items_in_range(self, xyxy_list):
        """
        선택된 영역의 item을 돌려준다
        여러곳을 선택할수가 있어서
        final_result = [[2ditem_자료들, xyxy], [2ditem_자료들, xyxy], ]
        """

        final_result = []
        result = []

        for xyxy_one in xyxy_list:
            x0, y0, x1, y1 = self.check_address(xyxy_one)
            for x in range(x0, x1+1):
                temp = []
                for y in range(y0, y1+1):
                    self.old_item = self.item(x, y)
                    one_item = self.old_item.clone()
                    temp.append(one_item)
                result.append(temp)
            final_result.append([result, xyxy_one])
        self.old_item = final_result
        return result

    def read_first_xy_in_selection(self):
        """
        선택한 영역의 제일 처음 좌표를 알려주는 것이다
        아무런 영역도 지정을하지 않았다면 [0, 0]을 돌려준다
        """
        range_list = self.read_address_in_selection()[0]
        if range_list:
            result = [range_list[0][0], range_list[0][1]]
        else:
            result = [0,0]
        return result

    def sort_by_no(self, x):
        """
        x 번재 자리에 column 삽입
        """
        self.sortItems(x, Qt.DescendingOrder)

    def set_basic_setting(self):
        """
        처음의 시작시의 설정을 하도록 한다
        행과열 : 갯수, 색깔, 번호등을 설정
        """
        if self.var["line_select"] : self.setSelectionBehavior(QAbstractItemView.SelectRows)
        if self.var["cell_edit_no"] : self.setEditTriggers(QAbstractItemView.NoEditTriggers) # 셀 edit 금지
        if self.var["no_grid_line"]: self.setShowGrid(False)
        if self.var["no_header_x"]: self.verticalHeader().setVisible(False) # 행번호 안나오게 하는 코드
        if self.var["no_header_y"]: self.horizontalHeader().setVisible(False) # 열번호 안나오게 하는 코드
        if self.var["basic_cell_width"]: self.horizontalHeader().setDefaultSectionSize(self.var["basic_cell_width"]) # 열번호 안나오게 하는 코드
        if self.var["basic_cell_height"]: self.verticalHeader().setDefaultSectionSize(self.var["basic_cell_height"]) # 열번호 안나오게 하는 코드
        if self.var["odd_y_colored"]:
            self.setAlternatingRowColors(True)  # 행마다 색깔을 변경 하는 코드
            self.gui_palette = QPalette()  # 반복되는 행의 색깔을 지정하는 코드
            self.gui_palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0, 0))  # 반복되는 행의 색깔을 지정하는 코드
        if self.var["mouse_tracking"]:
            self.setMouseTracking(True)
        else:
            self.setMouseTracking(False)

    def sort_range_byno(self, x):
        """
        x 번재 자리에 column 삽입
        """
        self.sortItems(x, Qt.DescendingOrder)

    def undo(self):
        """
        실행 취소를 누르면 취소되는 기능
        """
        if len(self.history):
            action = self.history.pop()
            xyxy = action["range"]
            value_s = action["cells"]
            #print("undo 실행", action["action"], xyxy, value_s)

            if action["action"] == "change" or action["action"] == "delete":
               self.write_range_attribute(action)

            elif action["action"] == "delete_yyline_in_range":
                self.insert_yyline_in_range(xyxy)
                for row, col, attribute in value_s:
                    self.write_value_in_cell([row, col], attribute["value"])

            elif action["action"] == "delete_xxline_in_range":
                self.insert_xxline_in_range(xyxy)
                for row, col, attribute in value_s:
                    self.write_value_in_cell([row, col], attribute["value"])

            elif action["action"] == "insert_yyline_in_range":
                self.del_rows(xyxy)

            elif action["action"] == "insert_xxline_in_range":
                self.del_cols(xyxy)
            else:
                return

    def update_usedrange(self, x, y):
        """
        usedrange를 확정하기위해 사용되는것
        이것은 usedrange가 없으므로 이것을 만드는 것이다
        """
        if x < self.max_x_len:
            self.usedrange[0] = max(x, self.usedrange[0])
        if y < self.max_y_len:
            self.usedrange[1] = max(y, self.usedrange[1])

    def write_calendar_in_cell(self, xy):
        self.add_calendar_in_cell(xy)

    def add_calendar_in_cell(self, xy):
        """

        :param xy:
        :return:
        """
        dateedit = QDateEdit(calendarPopup=True)
        #self.menuBar().setCornerWidget(self.dateedit, Qt.TopLeftCorner)
        dateedit.setDateTime(QDateTime.currentDateTime())
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setCellWidget(xy[0], xy[1], dateedit)

    def write_radio_button_in_cell(self, xy, title="group box", group_list="", output_xy=[2,3]):
        """
        """
        self.groupbox_output_xy = output_xy

        self.groupbox = QGroupBox(title)
        self.group_obj = []

        for index, name in enumerate(group_list):
            exec(f"self.radio{index} = QRadioButton('{name}')")
            exec(f"self.group_obj.append(self.radio{index})")
            exec(f"self.radio{index}.clicked.connect(self.action_radio_button)")
        self.group_obj[0].setChecked(True)

        vbox = QVBoxLayout()
        for one_obj in self.group_obj:
            vbox.addWidget(one_obj)
        self.groupbox.setLayout(vbox)
        self.setCellWidget(xy[0], xy[1], self.groupbox)

    def add_radiobutton_in_cell(self, xy, title="ExE", input_list=["a", "b", ""]):
        self.radio_group = []
        groupBox = QGroupBox(title, self)
        lay = QVBoxLayout()

        for index, one in enumerate(input_list):
            obj_name = str("radio_") + str(index)
            radio_obj = QRadioButton(one, self)
            self.radio_group.append(radio_obj)
            radio_obj.clicked.connect(self.radioButtonClicked)
            lay.addWidget(radio_obj)

        groupBox.setLayout(lay)
        groupBox.show()

        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setCellWidget(xy[0], xy[1], groupBox)

    def action_radio_button(self):
        """
        radio_button 객체가 click가 되었을때 실행되는것
        """
        for one_obj in self.group_obj:
            if one_obj.isChecked():
                self.groupbox_output = one_obj.text()
        self.write_value_in_cell(self.groupbox_output_xy, self.groupbox_output)

    def write_checkbox_in_cell(self, xy, value = 1):
        self.add_checkbox_in_cell(self, xy, title = "입력값", checked = value)

    def add_checkbox_in_cell(self, xy, title = "입력값", checked = 0):
        """
        셀에 체크박스를 넣는 것이다
        """
        cbox = QCheckBox(str(title))
        cbox.setChecked(int(checked))
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setCellWidget(xy[0], xy[1], cbox)

    def write_cell_button(self, xy, action, caption):
        """
        셀에 버튼을 만들어서 넣는 것이다
        """
        self.write_button_in_cell(xy, action, caption)

    def write_button_in_cell(self, xy, action, caption = "abc", tool_tip=""):
        """
        button객체를 넣는것
        """
        # tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        # 즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        btnRun = QPushButton(caption, self)  # 버튼 텍스트
        btnRun.clicked.connect(action)
        btnRun.setFont(QFont(self.basic_font, self.basic_font_size))

        if tool_tip != "":
            btnRun.setToolTip(tool_tip)
        btnRun.setStyleSheet("QPushButton { text-align: left;font-color:black}")

        self.setCellWidget(xy[0], xy[1], btnRun)

    def write_combo_in_cell(self, xy, combo_list, output_xy=[2,3]):
        """
        combo객체를 넣는것
        """
        self.combo = QComboBox()
        for one in combo_list:
            self.combo.addItem(str(one))

        self.combo.currentTextChanged.connect(self.action_combo)

        self.setCellWidget(xy[0], xy[1], self.combo)

    def add_combo_in_cell(self, xy, combo_list):
        """
        # tablewidget은 셀에 객체의 형식으로 넣어야 들어간다
        # 즉, 값, 색깔, 위치등을 지정해 주어야 들어가는 것이다
        #self.check_usedrange(xy)
        """
        combo_object = QComboBox()
        for one in combo_list:
            combo_object.addItem(str(one))
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setCellWidget(xy[0], xy[1], combo_object)

    def action_combo(self, text):
        """
        dial 객체가 click가 되었을때 실행되는것
        """
        self.write_value_in_cell(self.groupbox_output_xy, text)

    def write_groupbox_in_cell(self, xy, title="group box", group_list="", output_xy=[2,3]):
        """
        groupbox객체를 넣는것
        """
        self.groupbox_output_xy = output_xy

        self.groupbox = QGroupBox(title)
        self.group_obj = []

        for index, name in enumerate(group_list):
            exec(f"self.radio{index} = QRadioButton('{name}')")
            exec(f"self.group_obj.append(self.radio{index})")
            exec(f"self.radio{index}.clicked.connect(self.action_groupbox)")
        self.group_obj[0].setChecked(True)

        vbox = QVBoxLayout()
        for one_obj in self.group_obj:
            vbox.addWidget(one_obj)
        self.groupbox.setLayout(vbox)
        self.setCellWidget(xy[0], xy[1], self.groupbox)

    def action_groupbox(self):
        """
        groupbox 객체가 click가 되었을때 실행되는것
        """
        for one_obj in self.group_obj:
            if one_obj.isChecked():
                self.groupbox_output = one_obj.text()
        self.write_value_in_cell(self.groupbox_output_xy, self.groupbox_output)

    def write_file_dialog_in_cell(self, xy, caption="file dialog", output_xy=[2,3]):
        """
        file_dialog객체를 넣는것
        """
        btnRun = QPushButton(caption, self)  # 버튼 텍스트
        self.output_xy = output_xy
        btnRun.clicked.connect(self.action_file_dialog)
        #btnRun.setFont(QFont('Malgun Gothic', QFont))
        btnRun.setStyleSheet("QPushButton { text-align: left;font-color:black}")
        self.setCellWidget(xy[0], xy[1], btnRun)

    def action_file_dialog(self):
        """
        dial 객체가 click가 되었을때 실행되는것
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.write_value_in_cell(self.output_xy, fname[0])

    def write_color_dialog_in_cell(self, xy, caption="color dialog", output_xy=[4,3]):
        """
        color_dialog객체를 넣는것
        """
        self.output_xy = output_xy
        btnRun = QPushButton(caption, self)  # 버튼 텍스트
        btnRun.clicked.connect(self.action_color_dialog)
        #btnRun.setFont(QFont('Malgun Gothic', QFont))
        btnRun.setStyleSheet("QPushButton { text-align: left;font-color:black}")
        self.setCellWidget(xy[0], xy[1], btnRun)

    def action_color_dialog(self):
        """
        dial 객체가 click가 되었을때 실행되는것
        """
        col = QColorDialog.getColor()
        self.write_value_in_cell(self.output_xy, col.rgb())

    def write_slider_in_cell(self, xy, output_xy=None):
        """
        slider객체를 넣는것
        """
        if output_xy == "":
            self.slider_output_xy = [xy[0], xy[1]+1]
        elif output_xy == None:
            self.slider_output_xy = None
        else:
            self.slider_output_xy = output_xy
        self.check_used_range(xy)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.move(30, 30)
        self.slider.setRange(0, 50)
        self.slider.setSingleStep(2)

        self.slider.setPageStep(10)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)

        self.slider.valueChanged.connect(self.action_slider)
        self.setCellWidget(xy[0], xy[1], self.slider)

    def action_slider(self):
        """
        dial 객체가 click가 되었을때 실행되는것
        """
        if self.slider_output_xy == None:
            pass
        else:
            self.slider_output = self.dial.value()
        self.write_value_in_cell(self.slider_output_xy, self.slider_output)

    def write_dial_in_cell(self, xy, output_xy=None):
        """
        dial객체를 넣는것
        """
        if output_xy == "":
            self.dial_output_xy = [xy[0], xy[1]+1]
        elif output_xy == None:
            self.dial_output_xy = None
        else:
            self.dial_output_xy = output_xy

        self.check_used_range(xy)
        self.dial = QDial()
        self.dial.move(20, 80)
        self.dial.setRange(0, 100)
        self.dial.setNotchesVisible(True)
        self.dial.valueChanged.connect(self.action_dial)
        self.setCellWidget(xy[0], xy[1], self.dial)

    def action_dial(self):
        """
        dial 객체가 click가 되었을때 실행되는것
        """
        if self.dial_output_xy == None:
            pass
        else:
            self.dial_output = self.dial.value()
        self.write_value_in_cell(self.dial_output_xy, self.dial_output)

    def write_progressbar_in_cell(self, xy, value=50):
        self.add_progressbar_in_cell(xy, value=50)

    def add_progressbar_in_cell(self, xy, value=50):
        """
        프로그래스 바를 만드는 것이다
        """
        progress = QProgressBar()
        progress.setValue(int(value))
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setCellWidget(xy[0], xy[1], progress)

    def write_attribute(self, action):
        """
        """
        action_type = action["type"]
        xyxy = action["range"]
        value_s = action["cells"]
        for one_list in value_s:
            for x, y, value in one_list:
                self.setItem(x, y, QTableWidgetItem(str(value)))

    def write_value_in_cell(self, xy, input_text):
        """
        셀하나에 값을 넣는것이다
        """
        self.setItem(xy[0], xy[1], QTableWidgetItem(str(input_text)))


    def write_value_in_cell_01(self, xy, input_text):
        """
        셀하나에 값을 넣는것이다
        """
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            self.setItem(xy[0], xy[1], QTableWidgetItem(str(input_text)))
            self.check_max_xy(xy[0], xy[1])

    def write_value(self, xy, input_list):
        """
        값을 쓰는것
        """
        self.check_used_range(xy)
        if type([]) != type(input_list[0]):
            input_list = [input_list]

        for x in range(len(input_list)):
            for y in range(len(input_list[0])):
                self.setItem(xy[0]+x, xy[1]+y, QTableWidgetItem(str(input_list[x][y])))
        self.check_max_xy(xy[0]+len(input_list), xy[1]+len(input_list[0]))

    def write_value_in_range(self, xy, input_2dlist):
        self.write_list_2d_in_range(xy, input_2dlist)

    def write_list_2d_in_range(self, xy, input_2dlist):
        """
        2차원자료 형태의 것을 입력하는 것이다
        """
        if type([]) != type(input_2dlist[0]):
            input_2dlist = [input_2dlist]

        for x in range(len(input_2dlist)):
            if xy[0] + x < self.max_x_len - 1:
                for y in range(len(input_2dlist[0])):
                    if xy[1] + y < self.max_y_len - 1:
                        self.setItem(xy[0]+x, xy[1]+y, QTableWidgetItem(str(input_2dlist[x][y])))

    def write_list_1d_in_range(self, xy, input_list):
        """
        1차원자료를 입력하면 셀에 입력하는것
        처음시작할 위치를 알아낸다
        """
        if xy[0] < self.max_x_len - 1 and xy[1] < self.max_y_len - 1:
            for y in range(len(input_list)):
                if xy[1]+y < self.max_y_len - 1:
                    self.setItem(xy[0], xy[1]+y, QTableWidgetItem(str(input_list[y])))

    def write_value_for_list_1d(self, xy, input_list):
        self.write_list_1d_in_range(xy, input_list)

    def write_range_1dvalue(self, xy, input_list):
        self.write_list_1d_in_range(xy, input_list)

    def merge_range(self, xy, x_count, y_count):
        """
        1차원자료를 입력하면 셀에 입력하는것
        처음시작할 위치를 알아낸다
        xy는 시작위치
        x_count : 아래쪽으로 몇개까지 병합될지
        y_count : 오른쪽으로 몇개까지 병합될지
        """
        if xy[0]+x_count < self.max_x_len - 1 and xy[1]+y_count < self.max_y_len - 1:
            self.setSpan(xy[0], xy[1], x_count, y_count)

    def write_merge_in_range(self, xy, x_count, y_count):
        self.merge_range(xy, x_count, y_count)

class view_main_windows(QWidget):
	def __init__(self, parent=None):
		super(view_main_windows, self).__init__()

		#super().__init__(self, None)
		self.setWindowTitle(basic_datas['window_title'])
		# 최대크기로 보여주기
		self.setWindowState(Qt.WindowMaximized)

		self.click_status = 0

		self.grid = QTableView()

		self.grid.setStyleSheet("QTableView{gridline-color: lightgray; font-size: 12pt;}")
		self.grid.setStyleSheet("QTableView::item{ border-color: lightgray; border-style: solid; border-width: 0px; }")
		self.grid.setStyleSheet("QTableView{border : 1px solid red}")

		self.grid.horizontalHeader().setStyleSheet("::section{Background-color:rgb(255,236,236)}")
		self.grid.verticalHeader().setStyleSheet("::section{Background-color:rgb(236,247,255)}")
		self.grid.horizontalHeader().setDefaultSectionSize(basic_datas["grid_width"])
		self.grid.verticalHeader().setDefaultSectionSize(basic_datas["grid_height"])

		base_data_set = make_table_datas()
		self.grid_cells_values = self.open_data_as_pickle()

		if not self.grid_cells_values:
				self.grid_cells_values = base_data_set.get_cell_sets()

		self.headers_titles = ["▽", "컬럼 2", 3, "DDD", "Y-5", "FFFFF", "GGGGG"]

		self.grid_all_indexes = display_cell_class(self.grid_cells_values, self.headers_titles)
		# index들을 연결시키면, grid에 item객체들이 만들어 지는 것이다
		# item은 자동으로 만들어지는 것이기 때문에 별도의 세팅이 필요없다
		# 서로 바뀌엇을때 연결이 된는 것은 index와 item이다
		# 예를들어 그리드에서 2번열을 삭제하였을때, 2번은 그대로 있지만 item은 변경이 되어져야 하기때문에 이런 시스템을 만들어 놓는것이다
		# 즉, 현재의 item을 알기위해서는 index를 통해서 들어가는것이 제일 좋다

		self.grid.setModel(self.grid_all_indexes)
		# setmodel이 item을 만들어서 연결하는것으로 보인다
		# 내부적으로 만들어지는 item은 변경할수가 없다

		self.grid.setItemDelegate(display_cell_upgrade_class(self.grid))
		#edit를 실행하면 실행 되는것
		self.grid.setItemDelegate(display_cell_upgrade_class(self.grid_cells_values))

		self.selectRow = self.grid_all_indexes.rowCount(QModelIndex())
		# self.selectColumn = 30

		# 셀의 자료에 widget을 만들도록 하는것은 아래의 메소드에서 하도록 한다
		self.basic_setup_widget()

		self.grid.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
		# header에서 마우스오른쪽을 누르면 나타나는메뉴
		self.grid.horizontalHeader().customContextMenuRequested.connect(self.menupopup_header_y)
		self.grid.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
		# header에서 마우스오른쪽을 누르면 나타나는메뉴
		self.grid.verticalHeader().customContextMenuRequested.connect(self.menupopup_header_x)
		# 셀의 선택이 변경되면 실행되는것

		self.selection_model = self.grid.selectionModel()
		self.selection_model.selectionChanged.connect(self.action_selection_changed)

		self.filters = "CSV files (*.csv)"
		self.fileName = None

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
		self.make_widget_test()

		self.grid.clicked.connect(self.view_click)

	def evtaction_cell_changed(self, x, y):
		# 이동된후의 값을 나타낸다
		self.add_history(self.old_cell)
		self.check_max_xy(x, y)

		try:
			input_text = self.item(x, y).text()

			print("입력값이 변경되었네요", (x, y), input_text)
			# 셀에 입력이 "="으로 입력되었을때 적용하는것
			if input_text == "=1":
				self.write_cell_combo([2, 2], ["abc", "def", "xyz"])
			elif input_text == "=2":
				print("=2 를 입력했네요")
				self.write_cell_combo([3, 3], ["111abc", "222def", "333xyz"])
		except:
			pass

	def evtaction_item_changed(self, item):
		print(f"Item Changed ({item.row()}, {item.column()})")

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
			print("selected.indexes : ", ix.data())
			pass

		for ix in deselected.indexes():
			print("deselected.indexes : ", ix.data())
			pass

	def basic_setup_widget(self):
		# 모든자료중에서 widget이 있는것을 찾아서 실행시키는 것이다
		for x in range(len(self.grid_cells_values)):
			for y in range(len(self.grid_cells_values[x])):
				one_values = self.grid_cells_values[x][y].values

				if one_values["kind_1"] == "widget":

					if one_values["kind_2"] == "button":
						self.write_cell_button([one_values["x"], one_values["y"]], one_values["caption"])
					elif one_values["kind_2"] == "check_box":
						self.write_cell_checkbox([one_values["x"], one_values["y"]], one_values["checked"])
					elif one_values["kind_2"] == "combo":
						self.write_cell_combo([one_values["x"], one_values["y"]], one_values["value"])
					elif one_values["kind_2"] == "progress_bar":
						self.write_cell_progressbar([one_values["x"], one_values["y"]], one_values["value"])

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
		basic_datas["color"] = list(color.getRgb())[:3]
		btn = self.sender()
		btn.setStyleSheet("background-color : rgb({0}, {1}, {2})".format(basic_datas["color"][0], basic_datas["color"][1],
																		 basic_datas["color"][2]))

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
				self.grid.setIndexWidget(self.grid_all_indexes.index(x, y), None)

	def delete_xyxy_selection(self, xyxy_list):
		# 선택영역안의 객체 삭제
		for xyxy in xyxy_list:
			for x in range(xyxy[0], xyxy[2] + 1):
				for y in range(xyxy[1], xyxy[3] + 1):
					self.setItem(x, y, QTableWidgetItem(""))

	def delete_cell_attribute(self, xy):
		self.removeCellWidget(xy[0], xy[1])


	def file_new(self):
		print("file_new")
		pass

	def file_save(self):
		print("file_save")
		if self.fileName == None or self.fileName == '':
			self.fileName, self.filters = QFileDialog.getSaveFileName(self, \
																	  filter=self.filters)
		if (self.fileName != ''):
			with open(self.fileName, 'wt') as stream:
				csvout = csv.writer(stream, lineterminator='\n')
				csvout.writerow(self.headers_titles)
				for row in range(self.grid_all_indexes.rowCount(QModelIndex())):
					print(self.grid_all_indexes.rowCount(QModelIndex()))
					rowdata = []
					for column in range(self.grid_all_indexes.columnCount(QModelIndex())):
						item = self.grid_all_indexes.index(row, column, QModelIndex()).data(Qt.DisplayRole)
						if column == 0:
							rowdata.append('')
							continue

						if item is not None:
							rowdata.append(item)
						else:
							rowdata.append('')
					csvout.writerow(rowdata)
					print(rowdata)

	def file_open(self):
		print("file_open")
		self.fileName, self.filterName = QFileDialog.getOpenFileName(self)

		if self.fileName != '':
			with open(self.fileName, 'r') as f:
				reader = csv.reader(f)
				header = next(reader)
				buf = []
				for row in reader:
					row[0] = QCheckBox("-")
					buf.append(row)

				self.grid_all_indexes = None
				self.grid_all_indexes = display_cell_class(buf, self.headers_titles)
				self.grid.setModel(self.grid_all_indexes)
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
		x0, y0, x1, y1 = self.read_selection_xyxy()
		insert_list = [bbb for y in range(len(self.grid_cells_values[x0]))]

		self.grid_all_indexes.beginInsertRows(QModelIndex(), x0, x1)
		for no in range(x0, x1 + 1):
			self.grid_cells_values.insert(no, insert_list)
		self.grid_all_indexes.endInsertRows()

		return True

	def insert_y(self, position, cols=1, index=QModelIndex()):
		x0, y0, x1, y1 = self.read_selection_xyxy()
		self.grid_all_indexes.beginInsertColumns(QModelIndex(), y0, y1)
		for y in range(y0, y1 + 1):
			for x in range(len(self.grid_cells_values)):
				self.grid_cells_values[x].insert(y, bbb)
		self.grid_all_indexes.endInsertColumns()

		return True

	def keyPressEvent(self, event):
		# 키보드를 누르면 실행되는 것
		super().keyPressEvent(event)
		if event.key() in (Qt.Key_Return, Qt.Key_Enter):
			print("enter키를 누름")
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
		new_index = self.grid_all_indexes.index(old_xy[0], old_xy[1])
		index_widget = self.grid.indexWidget(new_index)
		self.grid.setIndexWidget(self.grid_all_indexes.index(new_xy[0], new_xy[1]), index_widget)

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
				self.grid_cells_values=pickle.load(fr)
		except:
			self.grid_cells_values = ""
		return self.grid_cells_values

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
				new_index = self.grid_all_indexes.index(x, y)
				text = new_index.data()
				temp.append(text)
			result.append(temp)
		basic_datas["copy_items"] = result
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
		copy_data = basic_datas["copy_items"]
		x0, y0, x1, y1 = self.read_selection_xyxy()
		for x in range(len(copy_data)):
			for y in range(len(copy_data[x])):
				self.grid_all_indexes.setData(self.grid_all_indexes.index(x0 + x, y0 + y), copy_data[x][y])

	def paint_cell_color(self, xy="", input_rgb=[123, 123, 123]):
		# 셀의 배경색을 넣기위해 만드는 것이다
		x0, y0, x1, y1 = self.read_selection_xyxy()
		if basic_datas["color"]:
			color = basic_datas["color"]
		else:
			color = "gray"
		for x in range(x0, x1 + 1):
			for y in range(y0, y1 + 1):
				if basic_datas["color"]:
					rgb_color = basic_datas["color"]
				else:
					rgb_color = basic_datas["basic_color"]
				self.grid_cells_values[x][y].values["background_color"] = rgb_color
				# self.tableWidget.item(3, 5).setBackground(QtGui.QColor(100,100,150))

	def press_key_cut(self):
		self.press_key_copy()
		self.press_key_delete()

	def press_enter_key(self):
		print("Press Enter")

	def press_key_delete(self):
		print("delete")
		for one_index in self.grid.selectedIndexes():
			self.grid_all_indexes.setData(one_index, None)

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

		self.grid_all_indexes.beginRemoveRows(QModelIndex(), x0, x1)
		for no in range(x1, x0 - 1, -1):
			# print(no)
			# self.grid_all_indexes.removeRow(no)
			self.grid_cells_values.pop(no)
		self.grid_all_indexes.endRemoveRows()

		return True

	def read_cell_all_values(self, xy):
		# self.grid_cells_values[x][y].values["background_color"] = rgb_color
		x, y = xy

	def read_cell_item(self, xy):
		"""
		인덱스로 넘어온 자료의 item을 돌려준다
		"""
		new_index = self.grid_all_indexes.index(xy[0], xy[1])
		aaa = QStandardItemModel(self.grid.model()).item(3, 4)
		self.grid.model().setItem(7, 7, aaa)

	def read_xyxy_items(self, xyxy_list):
		# 선택된 영역의 item을 돌려준다
		# 여러곳을 선택할수가 있어서
		# final_result = [[2ditem_자료들, xyxy], [2ditem_자료들, xyxy], ]

		final_result = []
		result = []

		for xyxy_one in xyxy_list:
			print("영역의 item값 ==> ", xyxy_one)
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
		self.grid_all_indexes.beginRemoveColumns(QModelIndex(), y0, y1)
		for y in range(y1, y0 - 1, -1):
			# self.grid_all_indexes.removeRow(no)
			# 자료삭제를 item에서하니 계속 같은 자료가 다시 나타났다
			for x in range(len(self.grid_cells_values)):
				self.grid_cells_values[x].pop(y)
		self.grid_all_indexes.endRemoveColumns()
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
			pickle.dump(self.grid_cells_values, f)

	def save_pickle(self):
		# view객체는 서로 연결이 되어있어서 pickle로 안된다고 한다.
		# 직렬화후 역직렬화를 하면 된다는데...
		# 잘 모르겠다
		# ddd = self.grid_all_indexes
		# ccc = open("save_pyqt_grid_items.pickle", "b")
		# pickle.dump(ddd, ccc)
		# ccc.close()
		# self.grid.model().setItem(7,7, aaa)
		# self.grid_all_indexes.setItem(7,7, aaa)
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
			print("undo 실행", action["kind_1"], xyxy, value_s)

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
		print('view_click 클릭함 : (x: %s  y: %s)' % (indexClicked.row(), indexClicked.column()))
		self.px = indexClicked.row() + 1
		self.py = indexClicked.column() + 1
		self.click_status = 1

		print('px : %s  py %s' % (indexClicked.row() + 1, indexClicked.column() + 1))
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
		self.grid.setIndexWidget(self.grid_all_indexes.index(xy[0], xy[1]), btnRun)

	def write_cell_checkbox(self, xy, value=1, title=""):
		cbox = QCheckBox(title)
		cbox.setChecked(int(value))
		self.grid.setIndexWidget(self.grid_all_indexes.index(xy[0], xy[1]), cbox)

	def write_cell_combo(self, xy, combo_list):
		combo = QComboBox()
		for one in combo_list:
			combo.addItem(str(one))
		self.grid.setIndexWidget(self.grid_all_indexes.index(xy[0], xy[1]), combo)

	def write_cell_progressbar(self, xy, value=50):
		progress_bar = QProgressBar()
		progress_bar.setValue(int(value))
		self.grid.setIndexWidget(self.grid_all_indexes.index(xy[0], xy[1]), progress_bar)

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

#사용법을 보이기위해 만든것
class mygrid_example(QMainWindow):
    def __init__(self, parent = None):
        """
        이것 자체를 실행하면, 이것이 실행되도록 만들었다
        이렇게 사용하는 것이다
        """
        super().__init__(parent)
        grid = CreateTable(30,30)

        self.create_menubar()

        self.resize(500,500)

        grid.write_slider_in_cell([1,1])

        grid.write_dial_in_cell([2,1])

        grid.write_color_dialog_in_cell([3,1])

        grid.write_file_dialog_in_cell([4,1])

        grid.write_groupbox_in_cell([6,1],"그룹 박스",  ["a", "b", "c", "d"], [6,4])

        grid.write_combo_in_cell([7,1], ["a", "b", "c", "d"], [7,4])

        self.setCentralWidget(grid)

        self.show()

    def create_menubar(self):
        """
        메뉴바를 만드는 것
        """
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

        menu_2_1 = QAction('누가 만들었나요 ?', self)
        menu_2_1.triggered.connect(self.text_manual)
        menu_2.addAction(menu_2_1)

        menu_2_2 = QAction('Logo의 의미', self)
        menu_2_2.triggered.connect(self.text_manual)
        menu_2.addAction(menu_2_2)

        menu_3 = menubar.addMenu("끝내기")

        menu_3_1 = QAction(QIcon('exit.png'), 'Exit', self)
        menu_3_1.triggered.connect(QCoreApplication.instance().quit())
        menu_3.addAction(menu_3_1)

    def text_manual(self):
        """
        메뉴얼을 보여주는 것
        """
        print("메뉴의 테스트")

class main(QMainWindow):
    def __init__(self, xsize=100, y_size=100, parent = None):
        super().__init__(parent)
        grid = view_main_windows()
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

class table_data_for_mygrid:
	# 테이블에 나타나는 값을 위하여 만든 것
	def __init__(self):

		self.result = []
		for x in range(0, 20):
			for y in range(0, 50):
				temp = {"x": x, "y": y, "text": str(str(x) + "-" + str(y))}
				self.result.append(temp)

		self.my_values_1 = [
					{"x": 2, "y": 1, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},
					{"x": 2, "y": 2, "kind_1": "memo", "value": "memo memo"},
					{"x": 2, "y": 3, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 5, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 6, "kind_1": "tool_tip", "text": "tool_tip", "tool_tip": "툴팁입니다"},
					{"x": 2, "y": 7, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},

			{"x": 3, "y": 3, "kind_1": "basic", "kind_2": "basic", "text": "테스트용 값입니다"},

			{"x": 8, "y": 8, "draw_line":"yes", "line_top_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 9, "draw_line": "yes",
					 "line_top_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 10, "draw_line": "yes",
					 "line_bottom_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 11, "draw_line": "yes",
					 "line_left_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine, "brush": "basic", }},

					{"x": 5, "y": 3, "kind_1": "widget", "kind_2":"combo", "value": [1, 2, 3, 4, 5]},
					{"x": 5, "y": 5, "kind_1": "widget", "kind_2": "check_box", "checked": 1, "text":"check"},
					{"x": 5, "y": 7, "kind_1": "widget", "kind_2":"progress_bar", "value": 30},
					{"x": 5, "y": 8, "kind_1": "widget", "kind_2":"button", "caption": "button_1", "action":"action_def"},

					{"x": 10, "y": 10, "kind_1": "memo", "value": "memo memo"},

					{"x": 7, "y": 3, "kind_1": "font_color", "value": [255, 63, 24]},
					{"x": 7, "y": 5, "kind_1": "background_color", "value": [255, 63, 24]},
							   ]

		self.my_values_2 = {2:
						   {2: {"kind_1": "memo", "kind_2": "", "value": "memo memo"},
							4: {"kind_1": "basic", "kind_2": "date", "value": datetime.datetime(2002, 2, 2)},
							3: {"kind_1": "basic", "kind_2": "basic", "text": "값"},
							5: {"kind_1": "basic", "kind_2": "basic", "text": "값"},
							7: {"kind_1": "basic", "kind_2": "date", "value": datetime.datetime(2002, 2, 2)},
							6: {"kind_1": "tool_tip", "kind_2": "", "text": "tool_tip", "tool_tip": "툴팁입니다"}},

					   3:
						   {3: {"kind_1": "basic", "kind_2": "", "text": "[255, 63, 24]"},
							5: {"kind_1": "basic", "kind_2": "", "text": "[255, 63, 24]"}},


					   8:
						   {6: {"draw_line": "yes",
								"line_top_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine,
												 "brush": "basic", }},
							9: {"draw_line": "yes",
								"line_top_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine,
												 "brush": "basic", }},
							8: {"draw_line": "yes",
								"line_bottom_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine,
													"brush": "basic", }},
							10: {"draw_line": "yes",
								 "line_left_dic": {"do": "yes", "color": Qt.red, "thick": 3, "style": Qt.SolidLine,
												   "brush": "basic", }}},

					   5:
						   {3: {"kind_1": "widget", "kind_2": "combo", "value": [1, 2, 3, 4, 5]},
							5: {"kind_1": "widget", "kind_2": "check_box", "checked": 1, "text": "check"},
							7: {"kind_1": "widget", "kind_2": "progress_bar", "value": 30},
							8: {"kind_1": "widget", "kind_2": "button", "caption": "버튼입니다", "action": "action_def"}},

					   7:
						   {3: {"kind_1": "font_color", "kind_2": "", "value": [255, 63, 24]},
							5: {"kind_1": "background_color", "kind_2": "", "value": [255, 63, 24]}},
					   10:
						   {10: {"kind_1": "memo", "kind_2": "", "value": "memo memo"}}}

		self.result.extend(self.my_values_1)
		self.common_var = {"basic_color": [217, 217, 217],
					  "color": "",
					  "copy_items": [],
					  "grid_x_len": 40,
					  "grid_y_len": 50,
					  "window_title": "Grid_Man",
					  "background_color": [123, 123, 123],
					  "grid_height": 25,
					  "grid_width": 100,
					  }

	def all_data_dic(self):
		return self.my_values_2

	def write_data(self):
		return self.my_values_1

	def setup_data(self):

		return self.common_var

class table_data_for_mygrid_01:
	def __init__(self):
		self.result = []
		for x in range(0, 20):
			for y in range(0, 50):
				temp = {"x": x, "y": y, "text": str(str(x) + "-" + str(y))}
				self.result.append(temp)

		self.mydic = {
			"font_color": None, "font_size": None, "font_background": None, "font_bold": None,
			"font_colorindex": None, "font_creator": None, "font_style": None, "font_italic": None,
			"font_name": None, "font_strikethrough": None, "font_subscript": None, "font_superscript": None,
			"font_themecolor": None, "font_themefont": None, "font_tintandshade": None, "font_underline": None,
			"line_top_do": None, "line_top_color": None, "line_top_colorindex": None, "line_top_tintandshade": None,
			"line_top_thick": None, "line_top_style": None, "line_top_brush": None,
			"line_bottom_do": None, "line_bottom_color": None, "line_bottom_colorindex": None, "line_bottom_tintandshade": None,
			"line_bottom_thick": None, "line_bottom_style": None, "line_bottom_brush": None,
			"line__do": None, "line__color": None, "line__colorindex": None, "line__tintandshade": None, "line__thick": None,
			"line__style": None, "line__brush": None,
			"line_right_do": None, "line_right_color": None, "line_right_colorindex": None, "line_right_tintandshade": None,
			"line_right_thick": None, "line_right_style": None, "line_right_brush": None,
			"line_left_do": None, "line_left_color": None, "line_left_colorindex": None, "line_left_tintandshade": None,
			"line_left_thick": None, "line_left_style": None, "line_left_brush": None,
			"line_x1_do": None, "line_x1_color": None, "line_x1_colorindex": None, "line_x1_tintandshade": None,
			"line_x1_thick": None, "line_x1_style": None, "line_x1_brush": None,
			"line_x2_do": None, "line_x2_color": None, "line_x2_colorindex": None, "line_x2_tintandshade": None,
			"line_x2_thick": None, "line_x2_style": None, "line_x2_brush": None,
			"kind_big": None, "kind_middle": None,	"memo": None,	"action": None,
			"checked": None,	"caption": None,	"fun": None,	"kind_1": None,
			"kind_2": None,	"user_type": None,	"text": None,	"text_kind": None,
			"value": None,	"value2": None,	"formularr1c1": None,	"formular": None,
			"background_color": None,	"background_colorindex": None,	"numberformat": None,	"widget": None,
			"align": None,	"decoration": None,	"edit": None,	"access_text": None,
			"access": None,	"order": None,	"size": None,	"check": None,
			"color": None,	"function": None,	"icon": None,	"draw_line": None,
			"protect": None,	"status": None,	"what": None,	"setup": None,
			"tool_tip": None,	"etc": None,	"user_1": None,	"user_2": None,
			"user_3": None,	"x": None,	"y": None,
		}


		self.my_values_1 = [
					{"x": 2, "y": 1, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},
					{"x": 2, "y": 3, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 5, "kind_1": "basic", "kind_2":"basic", "text": "값"},
					{"x": 2, "y": 7, "kind_1": "basic", "kind_2":"date", "value": datetime.datetime(2002, 2, 2)},
					{"x": 8, "y": 8, "draw_line":"yes", "line_top_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 9, "draw_line": "yes",
					 "line_top_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 8, "draw_line": "yes",
					 "line_bottom_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},
					{"x": 8, "y": 8, "draw_line": "yes",
					 "line_left_dic": {"do": "yes", "color": Qt.GlobalColor.red, "thick": 3, "style": Qt.PenStyle.SolidLine, "brush": "basic", }},

					{"x": 2, "y": 6, "kind_1": "tool_tip", "text": "tool_tip", "tool_tip": "툴팁입니다"},
					{"x": 5, "y": 3, "kind_1": "widget", "kind_2":"combo", "value": [1, 2, 3, 4, 5]},
					{"x": 5, "y": 5, "kind_1": "widget", "kind_2": "check_box", "checked": 1, "text":"check"},
					{"x": 5, "y": 7, "kind_1": "widget", "kind_2":"progress_bar", "value": 30},
					{"x": 5, "y": 8, "kind_1": "widget", "kind_2":"button", "caption": "button_1", "action":"action_def"},

					{"x": 10, "y": 10, "kind_1": "memo", "value": "memo memo"},
					{"x": 2, "y": 2, "kind_1": "memo", "value": "memo memo"},

					{"x": 7, "y": 3, "kind_1": "font_color", "value": [255, 63, 24]},
					{"x": 7, "y": 5, "kind_1": "background_color", "value": [255, 63, 24]},
							   ]



		self.common_var = {"basic_color": [217, 217, 217],
					  "color": "",
					  "copy_items": [],
					  "grid_x_len": 5000,
					  "grid_y_len": 100,
					  "window_title": "Grid_Man",
					  "background_color": [123, 123, 123],
					  "grid_height": 25,
					  "grid_width": 50,
					  }

	def write_data(self):
		return self.my_values_1

	def setup_data(self):
		return self.common_var

class main_menu_for_mygrid:
	def make_menu(self):
		self.menu = {}
		self.tree_menu = {}
		self.title_menu = {}

		self.menu["add_text_in_range_at_left"] = {
			"1st": "add(추가)", "2nd": "text", "3rd": "왼쪽에 글자 추가",
			"manual": "선택영역의 왼쪽에 글자를 추가한다\n값을 입력하세요",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_text": "입력필요", }}

		self.menu["add_text_in_range_at_right"] = {
			"1st": "add(추가)", "2nd": "text", "3rd": "오른쪽에 글자 추가",
			"manual": "선택한 영역의 오른쪽에 입력한 글자를 추가",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_text": "입력필요", }}

		self.menu["add_text_in_range_bystep"] = {
			"1st": "add(추가)", "2nd": "text", "3rd": "n번째 셀마다 값 넣기",
			"manual": "선택한 영역의 시작점부터 n번째 셀마다 기존값에 추가하여 값을 넣기",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_text": "", "step": "", }}

		self.menu["add_text_in_range_by_xystep"] = {
			"1st": "add(추가)", "2nd": "text",
			"3rd": "시작점부터 x,y번째 셀마다 값 넣기",
			"manual": "선택한 영역의 시작점부터 x,y 번째 셀마다 값을 넣기",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_text": "", "xystep": "", }}

		self.menu["change_value_in_range_to_capital"] = {
			"1st": "change", "2nd": "value",
			"3rd": "첫글자만 대문자로 변경",
			"manual": "선택한 영역의 값들을 첫글자만 대문자로 변경",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["change_value_in_range_to_lower"] = {
			"1st": "change", "2nd": "text",
			"3rd": "소문자로 변경",
			"manual": "선택영역안의 모든글자를 소문자로 만들어 주는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["change_value_in_range_to_ltrim"] = {
			"1st": "change", "2nd": "value",
			"3rd": "왼쪽끝의 공백을 삭제",
			"manual": "왼쪽 공백을 제거",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["change_value_in_range_to_rtrim"] = {
			"1st": "change", "2nd": "value",
			"3rd": "오른쪽 공백을 제거",
			"manual": "선택한 영역의 셀 값들의 오른쪽 공백을 없앤것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["change_value_in_range_to_trim"] = {
			"1st": "change", "2nd": "value",
			"3rd": "양쪽 공백을 삭제",
			"manual": "왼쪽끝의 공백을 삭제하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["change_value_in_range_to_upper"] = {
			"1st": "change", "2nd": "value",
			"3rd": "대문자로 변경",
			"manual": "선택한 영역의 값들을 대문자로 변경",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["delete_all_drawing_in_sheet"] = {
			"1st": "delete", "2nd": "drawing",
			"3rd": "모든 객체를 삭제",
			"manual": "시트안의 모든 객체를 삭제하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": ""}}

		self.menu["delete_continious_samevalue_in_range"] = {
			"1st": "delete", "2nd": "samevalue",
			"3rd": "밑으로 연속된 값을 삭제",
			"manual": "밑으로 같은 값들이 있으면 지우는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["delete_link_in_range"] = {
			"1st": "delete", "2nd": "link",
			"3rd": "링크를 삭제",
			"manual": "영역안의 링크를 삭제하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["delete_panthom_rangname"] = {
			"1st": "delete", "2nd": "rangname",
			"3rd": "이름영역중에서 연결이 끊긴것을 삭제하는 것",
			"manual": "이름영역중에서 연결이 끊긴것을 삭제하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {}}

		self.menu["delete_patial_value_in_range_as_0toN"] = {
			"1st": "delete", "2nd": "value",
			"3rd": "앞에서부터 N개까지의 글자를 삭제",
			"manual": "앞에서부터 N개까지의 글자를 삭제하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "num": ""}}

		self.menu["delete_rangename_all"] = {
			"1st": "delete", "2nd": "rangename",
			"3rd": "모든 rangename을 삭제",
			"manual": "모든 rangename을 삭제하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {}}

		self.menu["delete_samevalue_in_range"] = {
			"1st": "delete", "2nd": "samevalue",
			"3rd": "같은 값을 삭제",
			"manual": "영역안의 같은 값을 지우는 것이다",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": ""}}

		self.menu["delete_same_line_nos"] = {
			"1st": "delete", "2nd": "same_line",
			"3rd": "입력된 라인 번호대로 삭제",
			"manual": "위에서 부터 같은것을 삭제 한다",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"input_2dlist": ""}}

		self.menu["delete_xxline_value_in_range_by_same_line"] = {
			"1st": "delete", "2nd": "xxline",
			"3rd": "같은 줄을 삭제",
			"manual": "줄의 모든 값이 똑같으면 처음것을 제외하고 다음 자료부터 값만 삭제",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["delete_value_in_range_between_specific_letter"] = {
			"1st": "delete", "2nd": "value",
			"3rd": "입력자료의 사이의 자료를 포함한것 삭제",
			"manual": "입력자료의 두사이의 자료를 포함하여 삭제하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_list": "",}}

		self.menu["delete_value_in_range_by_continious_samevalue"] = {
			"1st": "delete", "2nd": "value",
			"3rd": "연속된 같은 값을 삭제",
			"manual": "영역안에서 연속된 같은 값을 삭제 한다",
			"folder": "/user_files",
			"filename": "aaa.py",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["delete_value_in_range_by_step"] = {
			"1st": "delete", "2nd": "value",
			"3rd": "n번째 가로열의 자료를 삭제",
			"manual": "선택자료중 n번째 가로열의 자료를 값만 삭제",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "", }}
		self.menu["delete_xline_in_range_as_empty"] = {
			"1st": "delete", "2nd": "xline_",
			"3rd": "빈 x줄을 삭제",
			"manual": "선택한영역에서 x줄의 값이 없으면 x줄을 삭제한다",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["delete_xline_in_range_by_step"] = {
			"1st": "delete", "2nd": "xline_",
			"3rd": "매 몇번째의 x열을 삭제",
			"manual": "영역안의 자료에서 선택한 가로행을 삭제한다",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "",}}

		self.menu["delete_xline_value_in_range_by_step"] = {
			"1st": "delete", "2nd": "xline_",
			"3rd": "n번째 세로줄의 값만 삭제",
			"manual": "선택자료중 n번째 세로줄의 자료를 값만 삭제하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",  "step_no": "",}}

		self.menu["delete_yline_in_range_bystep"] = {
			"1st": "delete", "2nd": "yline",
			"3rd": "n번째 가로줄을 삭제",
			"manual": "선택한 영역안의 세로줄중에서 선택한 몇번째마다 y라인을 삭제하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "", }}

		self.menu["delete_yline_value_in_range_bystep"] = {
			"1st": "delete", "2nd": "yline",
			"3rd": "n번째 가로줄의 값만 삭제",
			"manual": "선택한 영역안의 세로줄중에서 선택한 몇번째마다 y라인의 값을 삭제하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "", }}

		self.menu["fill_emptycell_in_range_as_uppercell"] = {
			"1st": "fill", "2nd": "emptycell",
			"3rd": "빈셀을 위의것으로 채우기",
			"manual": "빈셀을 위의것으로 채우는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["insert_xline_in_range_bystep"] = {
			"1st": "insert", "2nd": "xline",
			"3rd": "n번째마다 x열을 추가",
			"manual": "n번째마다 열을 추가하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "", }}

		self.menu["insert_yline_in_range_bystep"] = {
			"1st": "insert", "2nd": "yline",
			"3rd": "n번째마다 열을 추가",
			"manual": "n번째마다 열을 추가하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "step_no": "",}}

		self.menu["paint_color_in_range_as_samevalue_by_excelcolorno"] = {
			"1st": "paint", "2nd": "samevalue",
			"3rd": "영역에서 같은 값을 색칠하기",
			"manual": "영역에서 같은 값을 색칠하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "excelcolorno": "",}}

		self.menu["paint_color_in_cell_as_emptycell"] = {
			"1st": "paint", "2nd": "emptycell",
			"3rd": "빈셀일때 색칠하는 것",
			"manual": "빈셀일때 색칠하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["paint_color_in_range_bywords"] = {
			"1st": "paint", "2nd": "samevalue",
			"3rd": "입력글자와 같은 글자 색칠하기",
			"manual": "영역안에 입력받은 글자가 있으면 색칠하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["paint_color_in_range_in_maxvalue_in_each_xline"] = {
			"1st": "paint", "2nd": "maxvalue",
			"3rd": "각 x라인별로 최대값에 색칠",
			"manual": "각 x라인별로 최대값에 색칠하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", }}

		self.menu["paint_color_in_range_in_samevalue"] = {
			"1st": "paint", "2nd": "samevalue",
			"3rd": "같은 값 색칠하기",
			"manual": "선택한 영역에서 2번이상 반복된것만 색칠하기",
			"folder": "/user_files", "filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_color": "",}}

		self.menu["paint_color_in_range_in_spacecell"] = {
			"1st": "paint", "2nd": "spacecell",
			"3rd": "space문자가 들어간것 색칠하기",
			"manual": "빈셀처럼 보이는데 space문자가 들어가 있는것 찾기",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_color": "", }}

		self.menu["paint_color_in_range_in_specific_text"] = {
			"1st": "paint", "2nd": "specific_text",
			"3rd": "입력받은 글자와 같은것이 색칠하기",
			"manual": "영역안에 입력받은 글자와 같은것이 있으면 색칠하는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_color": "", }}

		self.menu["paint_color_in_range_with_minvalue_in_each_xline"] = {
			"1st": "paint", "2nd": "minvalue",
			"3rd": "x라인별로 최소값에 색칠",
			"manual": "각 x라인별로 최소값에 색칠하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["pick_unique_value_in_range"] = {
			"1st": "pick", "2nd": "unique_value",
			"3rd": "고유한 자료만을 골라내기",
			"manual": "선택한 자료중에서 고유한 자료만을 골라내는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "",}}

		self.menu["remove_vba_module"] = {
			"1st": "remove", "2nd": "vba_module",
			"3rd": "메크로를 삭제",
			"manual": "메크로를 삭제",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"module_name_list": "",}}

		self.menu["write_nansu_in_range"] = {
			"1st": "write", "2nd": "nansu",
			"3rd": "입력한 숫자범위에서 난수를 만들기",
			"manual": "입력한 숫자범위에서 난수를 만들어서 영역에 써주는것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "","input_list": "", }}

		self.menu["write_value_in_range_xystep"] = {
			"1st": "write", "2nd": "xystep",
			"3rd": "x,y 번째 셀마다 값을 넣기",
			"manual": "선택한 영역의 시작점부터 x,y 번째 셀마다 값을 넣기",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "","input_list": "","xystep": "", }}

		self.menu["write_value_in_range_by_trans"] = {
			"1st": "write", "2nd": "trans",
			"3rd": "xy를 바꿔서 입력",
			"manual": "입력자료의 xy를 바꿔서 입력하는 것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_list2d": "",}}

		self.menu["test_test_test"] = {
			"1st": "test", "2nd": "test",
			"3rd": "test",
			"manual": "py 화일을 실행하기 위한것",
			"folder": "/user_files",
			"filename": "aaa.py",
			"pcell_method_name": "",
			"params": {"sheet_name": "", "xyxy": "", "input_list2d": "",}}

		menu_list = list(self.menu.keys())
		for menu_id in menu_list:
			title = self.menu[menu_id]["1st"]+self.menu[menu_id]["2nd"]+self.menu[menu_id]["3rd"]

			self.title_menu[title] = menu_id #제목을 기준으로 찾을수있도록 만든것

			step_1 = self.menu[menu_id]["1st"]
			step_2 = self.menu[menu_id]["2nd"]
			step_3 = self.menu[menu_id]["3rd"]

			#tree형식으로 메뉴를 만들기 위한것
			if not step_1 in self.tree_menu.keys():
				self.tree_menu[step_1] ={}

			if not step_2 in self.tree_menu[step_1].keys():
				self.tree_menu[step_1][step_2] = {}

			if not step_3 in self.tree_menu[step_1][step_2].keys():
				self.tree_menu[step_1][step_2][step_3] =""


		return [self.menu, self.tree_menu, self.title_menu]


class basic_cell_class():
	# 각 셀에대해서 어떤 자료들을 넣을수있을지 설정하도록 만든 것이다
	# 다음에 추가적인것들도 가능하도록 클래스로 만든 것이다
	def __init__(self):
		self.values = {
			"font_dic": {"font_color": None, "font_size": None, "background": None, "bold": None, "color": None, "colorindex": None, "creator": None, "style": None, "italic": None,
				"name": None, "size": None, "strikethrough": None, "subscript": None, "superscript": None, "themecolor": None, "themefont": None, "tintandshade": None, "underline": None},
			"line_top_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"line_bottom_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"line_left_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"line_right_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"line_x1_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"line_x2_dic": {"do": None, "color": None, "colorindex": None, "tintandshade": None, "thick": None, "style": None, "brush": None, },
			"widget_dic": {"value": None, },
			"kind_dic": {"big": None, "middle": None, },
			"memo_dic": {"value": None},
			"checked": None,
			"fun": None,
			"kind_1": None,
			"kind_2": None,
			"user_type": None,
			"text": None,
			"text_kind": None,
			"value": None,
			"value2": None,
			"formularr1c1": None,
			"formular": None,
			"background_color": None,
			"background_colorindex": None,
			"numberformat": None,
			"widget": None,
			"align": None,
			"decoration": None,
			"edit": None,
			"access_text": None,
			"access": None,
			"order": None,
			"size": None,
			"check": None,
			"color": None,
			"function": None,
			"icon": None,
			"memo": None,
			"draw_line": None,
			"protect": None,
			"status": None,
			"what": None,
			"setup": None,
			"tool_tip": None,
			"etc": None,
			"user_1": None,
			"user_2": None,
			"user_3": None,
			"x": None,
			"y": None,
		}


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mygrid_example = main()
    sys.exit(app.exec())