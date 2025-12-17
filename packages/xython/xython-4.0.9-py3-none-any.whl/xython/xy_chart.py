# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import xy_common

class xy_chart:
	def __init__(self):
		self.chart = plt
		self.chart.rc("font", family="Malgun Gothic")
		self.vars = xy_common.xy_common().varx
		self.qty = 0
		self.color_set = ["b", "g", "r", "y", "k", "c", "m"]
		self.line_set = ["solid", "dashed", "dotted", "dashdot"]
		self.marker_set = [".", "o", "v", "x", "s", "*", "+", "d", "|", "_", "h"]
		self.line_datas = []

	def legend(self, x_position0to1=None, y_position0to1=None):
		#self.chart.legend()
		# plt.legend(loc=(0.0, 0.0))
		# plt.legend(loc=(0.5, 0.5))
		self.chart.legend(loc=(1.0, 1.0))
		#self.chart.legend(loc='best')          # ncol = 1
		# plt.legend(loc='best', ncol=2)  # ncol = 2
		# plt.legend(loc='best', ncol=2, fontsize=14, frameon=True, shadow=True)

	def set_x_range(self, xmin, xmax):
		"""
		X축의 범위: [xmin, xmax]
		"""
		self.chart.xlim([xmin, xmax])

	def set_y_range(self, ymin, ymax):
		"""
		y축의 범위: [ymin, ymax]
		"""
		self.chart.ylim([ymin, ymax])

	def set_xtick(self, input_list):
		"""

		:param input_list:
		:return:
		"""
		self.chart.xticks(input_list[0], input_list[1])

	def set_ytick(self, input_list):
		"""

		:param input_list:
		:return:
		"""
		self.chart.yticks(input_list[0], input_list[1])

	def set_title(self, input_text):
		self.chart.title(input_text)

	def ytitle(self, input_value=""):
		self.chart.ylabel(input_value)

	def xtitle(self, input_value=""):
		self.chart.xlabel(input_value)


	def line_one(self, x_l1d, y_l1d, color=None, width=None, line_style=None, marker=None, maker_size=None, label=None):
		"""
		한개의 선을 만드는 것이다

		:param x_data: x 좌표자료
		:param y_data: y 좌표자료
		:param color:  색, auto_unique를 사용하면, 기본으로 정한 색을 순서대로 하나씩 가져와서 사용한다
		:param width: 선의 넓이
		:param line_style: 선의 종류 (점선, 실선...)
		:param marker: 마커의 종류
		:param maker_size: 마커크기
		:param label: 레이블이름
		:return:
		"""

		self.general_line_one(x_l1d, y_l1d, color, width, line_style, marker, maker_size, None, label, True, None)

	def general_line_one(self, x_l1d, y_l1d, color=None, width=None, line_style=None, alpha=None, marker=None, maker_size=None, marker_inside_color=None, label=None, antialiased=True, zorder=None):
		"""
		한개의 선을 만드는 것이다

		:param x_data: x 좌표자료
		:param y_data: y 좌표자료
		:param color:  색, auto_unique를 사용하면, 기본으로 정한 색을 순서대로 하나씩 가져와서 사용한다
		:param width: 선의 넓이
		:param line_style: 선의 종류 (점선, 실선...)
		:param alpha: 투명도 (0 ~ 1)
		:param marker: 마커의 종류
		:param maker_size: 마커크기
		:param marker_inside_color: 마커의 내부색
		:param label: 레이블이름
		:param antialiased: 선의 경계를 부드럽게 처리할지, 기본값은 True
		:param zorder: 선이 곂쳤을때 어느것이 위로 올것인지 설정
		:return:
		"""
		self.qty = self.qty +1
		if color == "": color = self.color_set[self.qty]
		if line_style == "": line_style = self.line_set[self.qty]
		if marker == "": marker = self.marker_set[self.qty]

		self.chart.plot(x_l1d, y_l1d)

	def heat(self):
		import matplotlib.pyplot as plt
		import numpy as np

		arr = np.random.standard_normal((30, 40))
		# cmap = plt.get_cmap('PiYG')
		# cmap = plt.get_cmap('BuGn')
		# cmap = plt.get_cmap('Greys')
		cmap = plt.get_cmap('bwr')

		plt.matshow(arr, cmap=cmap)
		plt.colorbar()
		plt.show()


	def pie (self, ratio_l1d,y_l1d):
		self.chart.pie(ratio_l1d, labels=y_l1d, autopct='%.1f%%', startangle=260, counterclock=False)


	def scatter(self, x, y, size_l1d=None, color_l1d=None, marker=None, cmap=None, norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, edgecolors = None, plotnonfinite=False, *, data=None, **kwargs):
		"""

		:param x:
		:param y:
		:param size_l1d: 원의	크기
		:param color_l1d: 원의 색상을 위한 숫자
		:param marker: 마커의 종류
		:param cmap: 컬러맴을 지정하는 것
		:param norm:
		:param vmin: 색상데이터의 최소, 최대(츠메과 같이 사용)
		:param vmax:
		:param alpha:
		:param linewidths:
		:param edgecolors:
		:param plotnonfinite:
		:param data:
		:param kwargs:
		:return:
		"""

		self.chart.scatter(x, y, s=size_l1d, c=color_l1d)


	def bar_one(self, x_l1d, y2_l1d, color="", width="", y1_l1d_bottom="", alpha="", align="", edgecolor=""):
		"""
		bar 차트는 기본 넓이는 0.8이다 그리고 정해진 x라인의 틱을 중심으로 0.4 만큼씩 영역을 차지한다
		one_bar(x_l1d, y2_l1d, y1_l1d_bottom, bgcolor, alpha, width, align, edgecolor) bar 의 각 윗부분에 값을 표시하고싶다면, bar 를 만든후 그 각 bar의 속성을 얻어와서 값을 쓰도록 한다 - x 좌파의 숫자 - 높이를 설정, y1이 0이면, 보통의 bar 가되며, 이것에 값이 있으면 거기부터 시작하는 bar가 된다 - bar 가 시작되는 위치 - bgcolor 배경색 - 투명도 0은 없음 bar 의 밑면의 넓이 align, x 좌표숫자의 tic 위치를 기준으로 어디를 기준으로 나타낼것인지 설정하는 것 edgecolor, bar의 테두리 색
		여러 개일때는 x_l1d를 잘 사용해야 겹체지 않는다, auto 기능을 넣어서 사용하는것도 좋을 듯 bgcolor = auto_unique (자동생성이지만, 겹치지 않게) y1_l1d_bottom 은 몇 개없을땐, [[3,10]]이렇게 사용가능하도록 한다. 아니면 [0,0,10,0,0]처럼 만들던지
		"""
		self.qty = self.qty + 1
		if color == "": color = self.color_set[self.qty]

		self.chart.bar(x_l1d, y2_l1d, color="", width="", y1_l1d_bottom="", alpha="", align="", edgecolor="")


	def colorbar(self):
		plt.colorbar()

	def xtick(self):
		plt.xticks(x="", years="")

	def show(self):
		self.chart.show()

	def grid(self):
		#plt.plot(x, x ** 2, color='#e35f62', marker='*', linewidth=2)
		#plt.plot(x, x ** 3, color='springgreen', marker='^', markersize=9)
		plt.grid(True, axis='y', color='red', alpha=0.5, linestyle='--')


	def write_text(self):
		# 5. 텍스트 삽입하기
		self.chart.text(1.5, 3.5, 'Max of Data B')

	def insert_shape(self):
		# 4. 사각형 그리기
		self.chart.add_patch(
			self.chart.patches.Rectangle(
				(1.8, 1.0),  # (x, y)
				0.4, 1.5,  # width, height
				edgecolor='deeppink',
				facecolor='lightgray',
				fill=True,
			))

	def set_tile_style(self):
		# plt.style.use('ggplot')
		# plt.style.use('classic')
		# plt.style.use('Solarize_Light2')
		# plt.style.use('default')
		plt.style.use('bmh')

	# plt.scatter(x, y, s=area, c=colors, alpha=0.5, cmap='Spectral')


