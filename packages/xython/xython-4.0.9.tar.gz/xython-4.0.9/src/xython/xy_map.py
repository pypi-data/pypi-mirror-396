# -*- coding: utf-8 -*-
import folium
from folium import plugins
from folium.features import DivIcon
from folium.plugins import MarkerCluster

import json, webbrowser, os, math
import xy_color, xy_re, xy_util, xy_common, xy_common


class xy_map:
	"""
	지도를 좀더 쉽게 만들어주는 기능을 위해서 만든 것입니다
	기본적으로 folium을 사용합니다
	"""

	def __init__(self):
		self.varx = xy_common.xy_common().varx
		self.main_map = None
		#self.all_cxy = xy_map_common.xy_map_common().varx
		self.cxy = None  # cxy의 c는 coordinate의 약어임
		xy_map_data = {
			"zoom_control": True,
			"scrollWheelZoom": True,
			"dragging": True,
			"basic_cxy": [36.7835555121117, 126.99992340628],
			"location": [37.388738, 126.967983],
			"width": "100%",
			"height": "100%",
			"min_zoom": 0,
			"max_zoom": 18,
			"zoom_start": 10,
			"tiles": "OpenStreetMap",
			"prefer_canvas": False,
			"control_scale": False,
			"no_touch": False,
			"font_size": "1rem",
			"attr": None,
			"crs": "EPSG3857",
			"min_lat": None,
			"max_lat": None,
			"min_lon": None,
			"max_lon": None,

		}
		self.varx.update(xy_map_data)

		self.colorx_list = ['lightred', 'gray', 'lightgreen', 'pink', 'lightblue', 'beige', 'black', 'darkgreen', 'darkblue',
						   'lightgray', 'green', 'white', 'red', 'blue', 'orange', 'darkred', 'purple', 'cadetblue',
						   'darkpurple']
		self.tile_list = ["OpenStreetMap", "Cartodb Positron", "Cartodb dark_matter"]
		self.icon_list = ["cloud", "info-sign", "star", "bookmark", "flag", "cloud", "home",
						  "search", "envelope", "heart", "user", "camera",
						  "bell", "camera", "car", "bicycle", "bus", "train", "plane", "ship", "globe"]
		self.icon_4arrow = ["arrow-down", "arrow-up", "arrow-left", "arrow-right"]

		self.xy_icon_list = ['cloud', 'star', 'bookmark', 'flag', 'home', 'envelope', 'heart', 'user', 'camera', 'bell', 'car', 'bicycle', 'bus', 'train', 'plane', 'ship']
		self.xy_marker_color_list = ['gray', 'darkred', 'darkgreen', 'darkblue', 'darkpurple', 'cadetblue']
		self.xy_color_list = ['red', 'white', 'orange', 'pink', 'beige']

	def _check_l2d(self, input_value):
		"""
		_로 시작되는 것은 공통자료로도 사용가능한 것입니다

		2차원 자료를 확인하는 것
		cxy의 자료는 2차원료를 기본으로 사용하며,
		그래서 자료를 확인해서 1차원으로 들어오는 자료를 2차로 만드는 것이다
		1. 리스트가아닌 다른 자료형일때
		2. 1차원일때

		:param input_cxy_list:
		:return:
		"""
		if type(input_value) == type(()):
			input_value = list(input_value)

		if type(input_value) == type([]):
			if type(input_value[0]) == type([]) or type(input_value[0]) == type(()):
				pass
			else:
				input_value = [input_value]
		else:
			input_value = [[input_value]]

		return input_value

	def calc_circle_size_by_input_no(self, input_value=123, min_v=1, max_v=200, min_s=1, max_s=20):
		"""
		원의 크기를 자료의 형태에 따라서 정해주는 것
		원의 사이즈를 데이터의 크기에 따라서 다르게 할려고 하는 것이다
		자료에따라서 원의 크기를 다르게 만들고 싶을때 사용한다

		:param input_value:
		:param min_v:
		:param max_v:
		:param min_s:
		:param max_s:
		:return:
		"""
		min_size = min_s
		max_size = max_s
		min_value = min_v
		max_value = max_v
		if min_value > input_value:
			result = min_size
		elif max_value < input_value:
			result = max_size
		else:
			result = (max_value - min_value + 1) / (max_size - min_size + 1)
		return result

	def calc_midpoint_and_angle_with_two_cxy(self, coord1, coord2):
		"""
		두좌표의 중간지점과 각도를 계산해 주는것
		:param coord1:
		:param coord2:
		:return:
		"""
		x1, y1 = coord1
		x2, y2 = coord2
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		# 각도 계산 (라디안 단위)
		angle_radians = math.atan2(y2 - y1, x2 - x1)
		# 라디안을 도 단위로 변환
		angle_degrees = math.degrees(angle_radians)
		return (mid_x, mid_y), angle_degrees

	def change_address_to_cxy(self, input_address=""):
		"""
		일반 주소를 좌표로 만들어 주는것
		그러나 주소가 너무 짧으면 찾기가 어려우므로 찾은것이 3개이하가 되면, 문제가 있는 주소로 생각해야 한다

		기번 좌표의 형태 : [22218, '인천광역시', '', '중구', '', '송월동3가', 37.478114, 126.620739, '인천광역시 중구 송월동3가'],

		:param input_address:
		:return:
		"""
		rex = xy_re.xy_re()
		fix_list = [["부산시", "부산광역시"], ["인천시", "인천광역시"], ["대구시", "대구광역시"], ["대전시", "대전광역시"],
					["광주시", "광주광역시"], ["울산시", "울산광역시"], ["세종시", "세종특별자치시"], ["서울시", "서울특별시"],
					["강원특별자치도", "강원도"], ["전북특별자치도", "전라북도"], ["제주도", "제주특별자치도"],
					["충남", "충천남도"], ["충북", "충청북도"], ["전북", "전라북도"], ["전남", "전라남도"], ["경남", "경상남도"], ["경북", "경상북도"],
					]
		for one in fix_list:
			input_address = input_address.replace(one[0], one[1])
		all_address_l1d = input_address.strip().split(" ")
		# print(all_address_l1d)
		all_found_cxy_l2d = self.all_cxy

		for address_part in all_address_l1d[::-1]:
			temp = []
			# print("확인할 갯수는 => ", len(all_found_cxy_l2d), address_part)
			found_num = rex.search_with_xsql("[숫자:1~]", address_part)

			for l1d in all_found_cxy_l2d:
				if address_part in l1d[8]:
					temp.append(l1d)

			# 만약 찾은값이 없고, 혹시 중간에 숫자가 있을때
			# 다시한번 숫자부터 뒷부분을 제거하고 찾는 것
			if temp == [] and found_num:
				# print(found_num, address_part[0:found_num[0][1]])
				for l1d in all_found_cxy_l2d:
					if address_part[0:found_num[0][1]] in l1d[8]:
						temp.append(l1d)
			all_found_cxy_l2d = temp

		# 만약 찾은것이 여러개일때는 제일 처음의 것을 사용하도록 하자
		# print(all_found_cxy_l2d)
		if len(all_found_cxy_l2d) > 1:
			all_found_cxy_l2d = all_found_cxy_l2d[0]
		return all_found_cxy_l2d[6:8]

	def change_date_data_to_time_line_style(self, input_l2d):
		"""
		plugin중 timeline을 만들때 사용하는 자료의 형태로 바꿔주는 것

		예제:

		::

					lines = [
				{
					"coordinates": [
						[139.76451516151428, 35.68159659061569],
						[139.75964426994324, 35.682590062684206],
					],
					"dates": ["2017-06-02T00:00:00", "2017-06-02T00:10:00"],
					"color": "red",
				},
				{
					"coordinates": [
						[139.7575843334198, 35.679505030038506],
						[139.76337790489197, 35.678040905014065],
					],
					"dates": ["2017-06-02T00:20:00", "2017-06-02T00:30:00"],
					"color": "green",
					"weight": 15,
				},
			]

		:param input_l2d:
		:return:
		"""
		result = []
		# l1d = [cxy1[0], cxy1[1], cxy2[0], cxy2[1], date1, date2, color, thickness]
		for l1d in input_l2d:
			temp_dic = {}
			temp_dic["coordinates"] = [[l1d[0], l1d[1]], [l1d[2], l1d[3]]]
			temp_dic["dates"] = [l1d[4], l1d[5]]
			temp_dic["color"] = l1d[6]
			temp_dic["weight"] = l1d[7]
			result.append(temp_dic)
		return result

	def change_xcolor_to_text_rgb(self, input_xcolor):
		"""
		xcolor값을 "rgb(255, 0, 0)"의 형식으로 바꾸는 것
		folium의 rgb값의 형식은 이런식으로 넣어주어야 한다

		:param input_xcolor:
		:return:
		"""
		colorx = xy_color.xy_color()
		rgb_list = colorx.change_xcolor_to_rgb(input_xcolor)
		result = "rgb(" + str(rgb_list[0]) + "," + str(rgb_list[1]) + "," + str(rgb_list[2]) + ")"
		return result

	def check_list_data(self, input_l1d, default_value):
		"""

		:param input_l1d:
		:param default_value:
		:return:
		"""
		if type(input_l1d) != type([]):
			angle_list = [input_l1d]

		if len(input_l1d) > len(input_l1d):
			for one in range(len(input_l1d) - len(input_l1d)):
				input_l1d.append(default_value)

	def check_value(self, input_value, input_index):
		"""
		값을 확인해 주는 것

		:param input_value:
		:param input_index:
		:return:
		"""
		if input_value == type([]):
			try:
				return_value = input_value[input_index]
			except:
				return_value = input_value[-1]
		elif not input_value:
			return_value = None
		else:
			return_value = input_value
		return return_value

	def check_xy_data(self, input_list_1, input_list_2):
		"""
		선을 그리는 좌표를 알아서 확인해주는 기능
		folium에서 선을 그리는 것은 x는 x의 자료들만
		y는 y들만의 좌표로만 나타내는 것이다


		:param input_list_1:
		:param input_list_2:
		:return:
		"""
		result_1 = []
		result_2 = []

		if type(input_list_1[0]) == type([]):
			# 2차원의 자료이다
			for l1d in input_list_1:
				result_1.append(l1d[0])
				result_2.append(l1d[1])
		else:
			result_1 = input_list_1
			result_2 = input_list_2

		return [result_1, result_2]

	def get_color_type(self):
		"""
		색깔의 종류

		:return:
		"""
		result = self.varx["color_type"]
		return result

	def get_icon_type(self):
		"""
		icon형태에 대한 자료

		:return:
		"""
		result = self.varx["icon_type"]
		return result

	def get_tile_style(self):
		"""
		기본적인 설정값은 맨앞의 자료로 정한다

		:return:
		"""
		result = self.varx["tile_style"]
		return result

	def draw_polygon_by_cxy2d(self, input_map_obj, input_cxy_list):
		"""
		다각형의 닫힌 도형을 만드는 것이다

		:param input_map_obj:
		:param input_cxy_list:
		:return:
		"""
		folium.PolyLine(
			locations=input_cxy_list,
			tooltip='Polygon',
			fill=True,
		).add_to(input_map_obj)

	def draw_arrow_marker_at_cxy2d(self, input_cxy_list, angle_list=[]):
		"""
		화살표 방향을 표시할수있는 마커

		:param input_cxy_list:
		:param icon_no:
		:param tooltip_text:
		:return:
		"""
		kw = {"prefix": "fa", "color": "green", "icon": "arrow-up"}
		input_cxy_list = self._check_l2d(input_cxy_list)
		default_angle = 90
		if type(angle_list) != type([]):
			angle_list = [angle_list]

		if len(input_cxy_list) > len(angle_list):
			for one in range(len(input_cxy_list) - len(angle_list)):
				angle_list.append(default_angle)

		for index, one_cxy in enumerate(input_cxy_list):
			folium.Marker(location=one_cxy, icon=folium.Icon(angle=angle_list[index], **kw)).add_to(self.main_map)

	def draw_arrow_marker_at_cxy(self, input_cxy, i_angle, i_color):
		"""
		화살표 마커를 1개만 표시
		"""
		folium.Marker(location=input_cxy, icon=folium.Icon(angle=i_angle, prefix="fa", color=i_color, icon="arrow-up")).add_to(self.main_map)

	def draw_choropleth(self, input_title, input_geo, input_df, col_name_for_geo, col_name_for_data, input_property="동"):
		"""
		columns = (지도 데이터와 매핑할 데이터, 시각화 하고려는 데이터)
		등치 지역도는 데이터 값에 따라 행정 구역에 색상이 지정되거나 음영 처리되는 주제별 지도입니다
		choropleth : 행정구역별 구분되는 지도

		:param input_geo:
		:param input_data:
		:param input_columns:
		:return:
		"""
		self.main_map = folium.Choropleth(
			geo_data=input_geo,
			data=input_df,
			columns=[col_name_for_geo, col_name_for_data],
			key_on='feature.properties.' + input_property,
			fill_color='BuPu',
			legend_name=input_title,
		).add_to(self.main_map)

	def draw_choropleth_at_map(self, geo_data, table_data, bar_title):
		"""
		Choropleth 레이어를 만들고, 맵에 추가합니다.

		:param geo_data:
		:param table_data:
		:param bar_title:
		:return:
		"""
		self.main_map = self.make_map_obj("", 8)
		folium.Choropleth(
			geo_data=geo_data,
			data=table_data,
			columns=('name', 'code'),
			key_on='feature.properties.name',
			fill_color='BuPu',
			legend_name=bar_title,
		).add_to(self.main_map)

	def draw_circle_at_cxy2d(self, input_cxy_list, input_size_meter, popup_text=None, line_xcolor=None, fill_xcolor=None):
		"""
		원을 만드는 방법

		:param input_cxy_list: 원을 만들고 싶은 좌표
		:param input_size_meter: 원의 크기
		:param popup_text:
		:param line_xcolor:
		:param fill_xcolor:
		:return:
		"""
		if line_xcolor: line_xcolor = self.change_xcolor_to_text_rgb(line_xcolor)
		if fill_xcolor: fill_xcolor = self.change_xcolor_to_text_rgb(fill_xcolor)

		input_cxy_list = self._check_l2d(input_cxy_list)

		for index, one_cxy in enumerate(input_cxy_list):
			folium.CircleMarker(
				location=one_cxy,
				radius=input_size_meter,  # 점의 크기
				popup=popup_text,
				color=line_xcolor,
				fill=True,
				fill_color=fill_xcolor,
			).add_to(self.main_map)

	def draw_marker_at_clicked_place(self):
		"""
		화면을 클릭하면 마커가 만들어지는 것
		교육용으로 사용가능 한 방법으로 보인다
		:return:
		"""
		self.main_map.add_child(folium.ClickForMarker())

	def draw_colorline_at_cxy2d(self, input_cxy_list, input_xcolor_list):
		"""
		색을 입히면서 만드는 라인
		:return:
		"""

		folium.ColorLine(
			positions=input_cxy_list,
			colors=input_xcolor_list,
			colormap=["y", "orange", "r"],
			weight=10,
		).add_to(self.main_map)

	def draw_custom_marker_at_cxy(self, input_cxy, icon_image_path, shadow_image_path=None, tooltip_text=None):
		"""
		사용자가 만든 마커를 넣는 것

		:param input_cxy:
		:param icon_image_path:
		:param shadow_image_path:
		:param tooltip_text:
		:return:
		"""
		icon_image = icon_image_path
		my_icon = folium.CustomIcon(
			icon_image,
			icon_size=(38, 38),
			icon_anchor=(22, 94),
			shadow_image=shadow_image_path,
			shadow_size=(50, 64),
			shadow_anchor=(4, 62),
			popup_anchor=(-3, -76),
		)
		folium.Marker(location=input_cxy, icon=my_icon, tooltip=tooltip_text).add_to(self.main_map)

	def draw_heatmap_at_cxy2d(self, input_cxy_list, circle_size=500):
		"""
		서로 가까이 점이 있으면, 색이 진하게 되는 것입니다. 히트 맵 레이어 생성

		:param input_cxy_list:
		:param circle_size:
		:return:
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)

		folium.plugins.HeatMap(input_cxy_list,
							   # min_opacity=0.2,
							   radius=circle_size,
							   blur=50,
							   max_zoom=1).add_to(self.main_map)

	def draw_heatmap_with_time_period(self, heat_data, circle_size=40, total_date2=None):
		"""
		자료는 frame개념으로 보여준다
		1개의 프레임은 1개의 자료의 묶음이다
		즉, 시간으로 나타내는 부분이 아닌것이다, 만약 시간별로 나타내고싶다면, 자료 자체를 일정한 간격으로 만들면 됩니다

		data 파라미터는 파이썬 리스트 자료형만 인식

		HeatMapWithTime 은 특정지역의 시간에 따른 변화를 나타내는 역할을 하기 때문에, 공간과 시간, 이렇게 두 가지 축이 필요하다.

		lat_lng_by_hour = [
			[[37.56071136, 126.91485473, 0.3]],  # 0
			[[37.56071136, 126.91485473, 0.4]],  # 1
			[[37.56071136, 126.91485473, 0.5]],  # 2
			[[37.56071136, 126.91485473, 0.6]],  # 3
			[[37.56071136, 126.91485473, 0.1]],  # 4 ]

		lat_lng_by_hour[0] 은 0번째 시간의 모든 점들을 담고 있으며,
		lat_lng_by_hour[0][1] 은 0번째 시간의 점 중, 첫 번째 점을 나타낸다.
		lat_lng_by_hour[0][1][0] 은 0번째 시간의 점 중, 첫 번째 점의 위도를 나타낸다.

		:param heat_data:
		:param total_date2:
		:return:
		"""

		folium.plugins.HeatMapWithTime(heat_data, radius=circle_size, index=total_date2).add_to(self.main_map)

	def draw_json_data(self, input_map_obj, json_data, input_name):
		"""
		json자료를 지도위에 그리는 것

		:param input_map_obj:
		:param json_data:
		:param input_name:
		:return:
		"""
		if not input_map_obj: input_map_obj = self.main_map

		folium.GeoJson(
			json_data,
			name=input_name
		).add_to(input_map_obj)

	def draw_json_file(self, input_json_file='skorea_municipalities_geo_simple.json'):
		"""
		json화일로 그리기

		:param input_json_file:
		:return:
		"""
		# input_json_file = "skorea_municipalities_geo_simple.json" #시단위

		with open(input_json_file, mode='rt', encoding='utf-8') as f:
			geo = json.loads(f.read())
			f.close()
		folium.GeoJson(geo, name='seoul_provinces').add_to(self.main_map)

	def draw_line_at_cxy2d(self, input_cxy_list, input_xcolor, thickness_1to10=5, tooltip=None, opacity_oto1=1):
		"""
		input으로 시작하는 인수는 꼭 입력해야하는것이고, 아닌 것은 앞에 붙이지 않거나 다른 용어를 사용한다
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)
		if input_xcolor: input_xcolor = self.change_xcolor_to_text_rgb(input_xcolor)

		folium.PolyLine(
			locations=[input_cxy_list[0], input_cxy_list[1]],
			color=input_xcolor,
			weight=thickness_1to10,
			opacity=opacity_oto1,
			tooltip=tooltip
		).add_to(self.main_map)

	def draw_line_with_number_marker_at_cxy2d(self, input_cxy_list, popup_list=None, tooltip_list=None, color_list="blue", use_line_detail=False, start_no=1):
		input_cxy_list = self._check_l2d(input_cxy_list)
		self.set_for_line_detail()
		for index, one_cxy in enumerate(input_cxy_list):
			if not index == len(input_cxy_list) - 1:
				folium.PolyLine(
					locations=[input_cxy_list[index], input_cxy_list[index + 1]],
					color=self.check_value(color_list, index),
					# weight=lambda x, index=0: x[index] if isinstance(x, list) else (x if x else None),
					# opacity=self.line_detail["alpha"),
				).add_to(self.main_map)

				folium.Marker(
					location=one_cxy,
					icon=folium.Icon(color=self.check_value(color_list, index), icon=str(index + start_no), prefix="fa"),
					tooltip=self.check_value(tooltip_list, index),
					popup=self.check_value(popup_list, index), ).add_to(self.main_map)

	def draw_line_with_numbered_marker_at_cxy2d(self, input_cxy_list, marker_style, input_popup, input_tool_tip, input_bgcolor, icon_style, input_line_color, icon_outline_shape, icon_border_width=2,
									   input_text_color='#00ABDC', start_no=1):
		"""
		번호가 있는 마커를 선을 그으면서 만드는것

		:param input_cxy_list:
		:param marker_style:
		:param input_popup:
		:param input_tool_tip:
		:param input_bgcolor:
		:param icon_style:
		:param input_line_color:
		:param icon_outline_shape:
		:param icon_border_width:
		:param input_text_color:
		:param start_no:
		:return:
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)

		folium.PolyLine(
			locations=[input_cxy_list[0], input_cxy_list[1]],
		).add_to(self.main_map)

		for index, one_cxy in enumerate(input_cxy_list):
			new_icon = plugins.BeautifyIcon(
				icon=marker_style,
				icon_shape=icon_style,
				number=start_no,
				border_color=input_line_color,
				background_color=input_bgcolor,
				text_color=input_text_color,
				border_width=icon_border_width,
			)
			# 마커 생성
			folium.Marker(one_cxy, popup=input_popup, tooltip=input_tool_tip, icon=new_icon).add_to(self.main_map)

	def draw_marker_at_cxy2d_with_option(self, input_cxy_list, i_tooltip=None, i_draggable_tf=False, i_popup=None, icon_style="이름 또는 index", icon_angle=0, icon_color=None, bg_color=None):
		"""
		마커를 넣는 것
		icon_style : 숫자가 오면, 기본 아이콘리스트에서 이름을 갖고오며, 아닐때는 그냥 사용한다
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)
		if type(icon_style) == type(123):
			icon_style = self.icon_list[icon_style]
		for index, one_cxy in enumerate(input_cxy_list):
			folium.Marker(
				location=one_cxy,
				popup=i_popup,
				tooltip=i_tooltip,
				draggable=i_draggable_tf,
				icon=folium.Icon(angle=icon_angle, color=bg_color, icon_color=icon_color, icon=icon_style)
			).add_to(self.main_map)

	def draw_marker_cluster_at_cxy2d(self, input_cxy_list, i_tooltip=None, i_popup=None, ):
		"""
		여러개의 마커가 일정부분 가까워지면, 통합해서 갯수로 표현되는 것

		:param input_cxy_list:
		:param i_tooltip:
		:param i_popup:
		:return:
		"""
		mc = MarkerCluster()
		for index, one_cxy in enumerate(input_cxy_list):
			mc.add_child(
				folium.Marker(
					location=one_cxy,
					tooltip=i_tooltip,
					popup=i_popup)
			)

	def draw_marker(self, input_cxy_list, tooltip_text=None, setup_draggable_tf=False):
		"""
		좌표에 마커를 만드는 것

		:param input_cxy_list:
		:param tooltip_text:
		:param setup_draggable_tf:
		:return:
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)

		for index, one_cxy in enumerate(input_cxy_list):
			folium.Marker(location=one_cxy, tooltip=tooltip_text, draggable=setup_draggable_tf).add_to(self.main_map)

	def draw_marker_for_text_address(self, text_address):
		cxy = self.change_address_to_cxy(text_address)
		self.draw_marker(cxy)

	def draw_marker_for_text_address_with_tool_tip(self, text_address, tool_tip):
		cxy = self.change_address_to_cxy(text_address)
		self.draw_marker(cxy, tool_tip)

	def draw_marker_with_icon(self, input_cxy_l2d, i_icon_name_l1d, i_bg_color_l1d, i_popup_l1d, i_tooltip_l1d, i_icon_shape="marker", i_icon_textcolor="black", i_border_width=2,
							  i_icon_linecolor="black"):
		"""
		아이콘형식의 마커

		icon=None, Font-Awesome의 아이콘 이름
		icon_shape=None, 아이콘의 모양, [circle, circle-dot, doughnut, rectangle, rectangle-dot, marker] 이렇게 6개가 적용가능
		border_width=3, 아이콘의 경계선 굵기
		border_color='#000', 아이콘의 경계선 색
		text_color='#000', 글자색
		background_color='#FFF', 아이콘의 배경색
		inner_icon_style='', 아이콘의 css 스타일
		spin=False,
		number=None,
		"""

		i_popup_l1d = self.check_list_data(i_popup_l1d, None)
		i_tooltip_l1d = self.check_list_data(i_tooltip_l1d, None)
		i_bg_color_l1d = self.check_list_data(i_bg_color_l1d, "green")

		input_cxy_l2d = self._check_l2d(input_cxy_l2d)
		for index, one_cxy in enumerate(input_cxy_l2d):
			bt_icon = plugins.BeautifyIcon(
				icon=i_icon_name_l1d,  # Font-Awesome의 아이콘 이름
				background_color=i_bg_color_l1d[index],

				icon_shape=i_icon_shape,
				text_color=i_icon_textcolor,
				border_color=i_icon_linecolor,
				border_width=i_border_width,
			)
			# 마커 생성
			folium.Marker(one_cxy, popup=i_popup_l1d[index], tooltip=i_tooltip_l1d[index], icon=bt_icon).add_to(self.main_map)

	def draw_marker_with_icon_type(self, input_cxy_list, icon_no=1, tooltip_text=None):
		"""
		마커에 표시하는 아이콘을 선택할수가 있다

		icon의 색은 hex도 가능하다.
		예제:

		::

			fm = folium.Map(location=(44,3), tiles="Stamen Terrain")
			folium.Marker(
					location=(44,3.2),
					popup="data1",
					icon=folium.Icon(color='#8000ff',icon_color='#4df3ce', icon="star", prefix="fa"),).add_to(fm)

		:param input_cxy_list:
		:param icon_no:
		:param tooltip_text:
		:return:

		"""

		input_cxy_list = self._check_l2d(input_cxy_list)

		for index, one_cxy in enumerate(input_cxy_list):
			folium.Marker(location=one_cxy, icon=folium.Icon(color='red', icon=self.varx["icon_type"][icon_no - 1]),
						  tooltip=tooltip_text).add_to(self.main_map)

	def draw_marker_at_cxy2d(self, input_l2d):
		"""
		마커에 표시하는 아이콘을 선택할수가 있다
		icon의 색은 hex도 가능하다.
		"""

		for index, l1d in enumerate(input_l2d):
			folium.Marker(
				location=[l1d[0], l1d[1]],
				icon=folium.Icon(color=l1d[2], icon=l1d[3]),
				tooltip=l1d[4],
				popup=l1d[5],
			).add_to(self.main_map)

	def draw_marker_at_cxy2d_for_tooltip_menu(self, input_l2d):
		"""
		엑셀의 자료를 갖고올때, 쉽게 사용가능하도록 만드는 것이다

		input_l2d =  [[cx, cy, tool_tip, menu]....]
		만약 cxy대신에 주소가 들어가면 그분은 자동으로 변경이 되도록 한다

		1개씩 자료를 마커로 만들면, 필터로 나타나는 것이 여러개 나타나므로, 한번에 모든 자료를 넣어야 합니다

		자료의 정확성을 위해 다음의 기능을 추가하였읍니다
		- 만약 메뉴부분을 넣지 않으면 그냥 빈문자열을 넣는다
		- 만약 cxy가 아닌 일반 주소가 들어가면, cxy로 변경하는 기능도 추가하였읍니다
		- 만약 1개의 자료만 온다면, 그것은 어떤 의미가 있는지 모르므로, 잘못된 자료로 인식해서, 그냥 넘어가도록 합니다

		"""
		utilx = xy_util.xy_util()
		input_l2d = utilx.change_any_data_to_l2d(input_l2d)
		print(input_l2d)

		unique_data = set()
		# 자료가 맞는지를 확인하는 것, 틀리면 고치는 것
		for i, l1d in enumerate(input_l2d):
			unique_data.add(l1d[3])

		icon_dic = {}
		icon_count = len(self.colorx_list)
		for index, one in enumerate(list(unique_data)):
			icon_dic[one] = self.colorx_list[divmod(index, icon_count)[1]]

		for i, l1d in enumerate(input_l2d):
			if type(l1d[0]) == type("abc"):
				cxy_new = self.change_address_to_cxy(l1d[0])
				print(l1d[0], cxy_new)
				l1d[0] = cxy_new[0]
				l1d[1] = cxy_new[1]

			folium.Marker(
				location=[l1d[0], l1d[1]],
				tooltip=l1d[2],
				tags=[l1d[3]],
				icon=folium.Icon(color=icon_dic[l1d[3]])
			).add_to(self.main_map)

		folium.plugins.TagFilterButton(list(unique_data)).add_to(self.main_map)

	def draw_marker_at_cxy_with_menu(self, cxy, tool_tip, menu):
		if type(cxy) == type("abc"):
			cxy = self.change_address_to_cxy(cxy)
		folium.Marker(
			location=cxy,
			tooltip=tool_tip,
			tags=[menu],
		).add_to(self.main_map)

		folium.plugins.TagFilterButton(menu).add_to(self.main_map)

	def draw_marker_at_cxy2d_with_no(self, input_cxy_list, tooltip_l1d=None, color_l1d=None, start_no=1):
		"""
		숫자 번호를가진 마커를 만드는 것

		:param input_cxy_list:
		:param tooltip_l1d:
		:param color_l1d:
		:param start_no:
		:return:
		"""

		input_cxy_list = self._check_l2d(input_cxy_list)
		tooltip_l1d = self.check_list_data(tooltip_l1d, None)
		color_l1d = self.check_list_data(color_l1d, "green")

		for index, one_cxy in enumerate(input_cxy_list):
			folium.Marker(location=one_cxy, icon=folium.Icon(color=color_l1d[index], number=str(start_no + index)), tooltip=tooltip_l1d[index]).add_to(self.main_map)

	def draw_marker_at_cxy2d_with_numbered_icon(self, input_cxy_l2d, i_bg_color_l1d, i_popup_l1d, i_tooltip_l1d, i_icon_shape="marker", i_start_no=1, i_icon_textcolor="black", i_border_width=2,
									   i_icon_linecolor="black"):
		"""
		icon=None, Font-Awesome의 아이콘 이름
		icon_shape=None, 아이콘의 모양, [circle, circle-dot, doughnut, rectangle, rectangle-dot, marker] 이렇게 6개가 적용가능
		border_width=3, 아이콘의 경계선 굵기
		border_color='#000', 아이콘의 경계선 색
		text_color='#000', 글자색
		background_color='#FFF', 아이콘의 배경색
		inner_icon_style='', 아이콘의 css 스타일
		spin=False,
		number=None,
		"""
		input_cxy_l2d = self._check_l2d(input_cxy_l2d)
		for index, one_cxy in enumerate(input_cxy_l2d):
			bt_icon = plugins.BeautifyIcon(
				background_color=i_bg_color_l1d[index],

				icon_shape=i_icon_shape,
				number=str(i_start_no + index),  # icon대신에 숫자를 넣고싶을때
				text_color=i_icon_textcolor,
				border_color=i_icon_linecolor,
				border_width=i_border_width,
			)
			# 마커 생성
			folium.Marker(one_cxy, popup=i_popup_l1d[index], tooltip=i_tooltip_l1d[index], icon=bt_icon).add_to(self.main_map)

	def draw_marker_at_cxy2d_with_serial_no(self, input_cxy_list, start_no=1):
		"""
		한줄이 아닌 여러 줄을 연결할때, 각 줄의 끝부분에 번호로된 마커를 넣는 방법
		시작 번호를 지정할수가 있다

		:param input_cxy_list:
		:param start_no:
		:return:
		"""
		input_cxy_list = self._check_l2d(input_cxy_list)

		for index, one_cxy in enumerate(input_cxy_list):
			new_no = start_no + index
			folium.Marker(
				location=[one_cxy[0], one_cxy[1]],
				icon=plugins.BeautifyIcon(icon="arrow-down",
										  icon_shape="circle",
										  border_width=2,
										  number=new_no,
										  tooltip=one_cxy[2]),
			).add_to(self.main_map)

	def draw_polyline_at_cxy2d(self, input_map_obj, input_cxy_list):
		"""
		다각형의 닫힌 도형을 만드는 것이다

		:param input_map_obj: 다각형을 그릴 그림 객체
		:param input_cxy_list: 다각형으로 그릴 좌표들
		:return:

		"""
		if not input_map_obj: input_map_obj = self.main_map

		folium.PolyLine(
			locations=input_cxy_list,
			tooltip='Polygon',
			fill=True,
		).add_to(input_map_obj)

	def draw_polyline_with_time_period(self, input_l2d=""):
		"""
		다각형자료를 시간때별로 변하는 지도를 만드는 것

		예제:

		::
			lines = [{	"coordinates": [[139.76451516151428, 35.68159659061569],[139.75964426994324, 35.682590062684206],],
					"dates": ["2017-06-02T00:00:00", "2017-06-02T00:10:00"],"color": "red",	},
					{"coordinates": [[139.7575843334198, 35.679505030038506],[139.76337790489197, 35.678040905014065],],
					"dates": ["2017-06-02T00:20:00", "2017-06-02T00:30:00"],
					"color": "green",
					"weight": 15,},
					]

		:param input_l2d:
		:return:

		"""
		# Lon, Lat order.
		lines = self.change_date_data_to_time_line_style(input_l2d)

		features = [
			{
				"type": "Feature",
				"geometry": {
					"type": "LineString",
					"coordinates": line["coordinates"],
				},
				"properties": {
					"times": line["dates"],
					"style": {
						"color": line["color"],
						"weight": line["weight"] if "weight" in line else 5,
					},
				},
			}
			for line in lines
		]

		folium.plugins.TimestampedGeoJson({"type": "FeatureCollection", "features": features, },
										  period="PT1M",
										  add_last_point=True,
										  ).add_to(self.main_map)

	def draw_rectangle_at_cxy2d(self, input_map_obj, input_cxy_list):
		"""
		사각형 그리기

		:param input_map_obj:
		:param input_cxy_list:
		:return:
		"""
		if not input_map_obj:
			input_map_obj = self.main_map
		input_cxy_list = self._check_l2d(input_cxy_list)

		folium.PolyLine(
			locations=input_cxy_list,
			tooltip='Rectangle'
		).add_to(input_map_obj)

	def get_360_out_side(self, input_xy_list, base_xy):
		"""
		모든 xy리스자료중에서 기준좌표를 기준으로하여 360도로 가장 먼 좌표들만 만드는 것

		:param input_xy_list:
		:param base_xy:
		:return:
		"""
		input_xy_list = self._check_l2d(input_xy_list)

		pi = 3.1415926535
		result = {}
		x0, y0 = base_xy
		for old_xy in input_xy_list:
			one_xy = [float(old_xy[0]), float(old_xy[1])]
			x, y = one_xy
			# print(base_xy, one_xy)
			degree = int(math.atan2(x0 - x, y0 - y) * 180 / pi)
			a = (x0 - x)
			b = (y0 - y)
			distance = math.sqrt((a * a) + (b * b))

			if degree in result.keys():
				if result[degree][0] < distance:
					result[degree] = [distance, x, y]
			else:
				result[degree] = [distance, x, y]
		return result

	def get_test_cxy_list(self, x_count=5, y_count=4, distance=0.1):
		result = []
		for x in range(x_count):
			for y in range(y_count):
				result.append([self.varx["basic_cxy"][0] + x * distance, self.varx["basic_cxy"][1] + y * distance])
		return result

	def insert_plugin_for_click_marker(self):
		"""
		화면을 클릭하면 마커가 만들어지는 것
		교육용으로 사용가능 한 방법으로 보인다
		:return:
		"""
		self.main_map.add_child(folium.ClickForMarker())

	def insert_plugin_for_filter(self, input_data):
		"""
		menu group와같이 비슷한 형태로 사용되는것으로, filter라는 개념으로 사용합니다

		:param input_data:
		:return:
		"""

		unique_data = set()
		for i, cxy in enumerate(input_data):
			folium.Marker(
				cxy,
				tags=[input_data[i][2]]
			).add_to(self.main_map)
			unique_data.add(input_data[i][2])

		folium.plugins.TagFilterButton(list(unique_data)).add_to(self.main_map)

	def insert_plugin_for_minimap(self):
		"""
		화면에 미니지도를 넣는것
		:return:
		"""
		minimap = plugins.MiniMap()
		self.main_map.add_child(minimap)

	def insert_plugin_for_mouse_position(self):
		"""
		마우스의 위치를 알려주는 것을 넣는 것
		:return:
		"""
		folium.plugins.MousePosition().add_to(self.main_map)

	def insert_plugin_for_my_position(self):
		"""
		나의 위치를 알려주는 것을 넣는 것
		:return:
		"""
		folium.plugins.LocateControl().add_to(self.main_map)

	def main_menu_n_sub_menu(self, input_lists, main_n_sub, icon_n_color):
		"""
		input_lists = [
			['37.55440684521157', '127.12937429453059','food_land','방이 샤브샤브','맛나는데 여자들이 더 좋아해요'],
			['37.1834787433397','128.466953597959','food_land','미탄집','메밀전병'],
			['37.2079513137108','128.986557255629','food_land','구와우순두부','순두부'],
			]

		# 메인 메뉴와 서브메뉴를 정의한다
		main_n_sub = [['육해공군', 'food_land', 'food_sea', 'food_sky'], ["카페를 한눈에", 'cafe', 'food_etc','etc']]
		# 서브메뉴에 보일 아이콘과 색을 정의한다
		icon_n_color = {'food_land': ['lightred', 'cloud'], 'food_sea': ['gray', 'info-sign'], 'food_sky': ['lightgreen', 'star'], 'cafe': ['gray', 'info-sign'], 'food_etc': ['lightgreen', 'star'], 'etc': ['pink', 'bookmark']}

		:param input_lists:
		:param main_n_sub:
		:param icon_n_color:
		:return:
		"""
		menu_dic = {}
		sub_menu_dic = {}
		for ix, one_list in enumerate(main_n_sub):
			exec(f"main_menu_{ix} = folium.FeatureGroup(name='{one_list[0]}')")
			exec(f"self.main_map.add_child(main_menu_{ix})")
			exec(f"menu_dic['{one_list[0]}'] = main_menu_{ix}")

			for iy, sub_menu in enumerate(one_list[1:]):
				exec(f"sub_menu_{iy} = plugins.FeatureGroupSubGroup(main_menu_{ix}, '{sub_menu}')")
				exec(f"self.main_map.add_child(sub_menu_{iy})")
				exec(f"sub_menu_dic['{sub_menu}'] = sub_menu_{iy}")

		# 만약 icon_n_color에 아무런 값도 없을때 만들어 지는 것
		if not icon_n_color:
			icon_type = self.icon_list
			color_type = self.colorx_list
			icon_color = {}
			for ix, one_list in enumerate(main_n_sub):
				for iy, sub_menu in enumerate(one_list[1:]):
					icon_color[sub_menu] = [color_type[ix + iy], icon_type[ix + iy]]
			print(icon_color)

		folium.LayerControl(collapsed=False).add_to(self.main_map)
		for one_data in input_lists:
			folium.Marker(
				location=[one_data[0], one_data[1]],
				popup=one_data[2],
				icon=folium.Icon(color=icon_n_color[one_data[2]][0], icon=icon_n_color[one_data[2]][1]),
				tooltip=one_data[3],
			).add_to(sub_menu_dic[one_data[2]])

	def make_basic_data_set(self, input_lists):
		"""
		읽어오고 싶은 자료들을 자료의 형태에 따라서 만들어야 한다

		:param input_lists:
		:return:
		"""
		result = []
		for one_data in input_lists:
			temp_dic = {}
			temp_dic["address_full"] = one_data[9]
			temp_dic["address_middle"] = one_data[8]
			temp_dic["address_top"] = one_data[7]
			temp_dic["water_element"] = one_data[6]
			temp_dic["temp"] = one_data[5]
			temp_dic["ph"] = one_data[4]
			temp_dic["water_type"] = one_data[3]

			# 아래의 자료는 기본적으로 folium에서 사용되는 형태이다
			temp_dic["title"] = str(one_data[3]) + "<br>" + str(one_data[4]) + "<br>" + str(one_data[5]) + "<br>" + str(
				one_data[6]) + "<br>" + str(one_data[7]) + "<br>" + str(one_data[8]) + "<br>" + str(one_data[9])
			temp_dic["xy"] = [one_data[2], one_data[1]]
			temp_dic["pop_text"] = one_data[8]
			temp_dic["html"] = one_data[8] + "<br>" + temp_dic["title"]
			temp_dic["iframe"] = folium.IFrame(html=temp_dic["html"], width=300, height=200)
			result.append(temp_dic)
		return result

	def make_map_obj(self, input_cxy="", zoom_no=8):
		"""
		지도의 중앙지점과 줌의 정도를 설정한다
		우리나라의 중앙일것같은 온양온천을 기준으로 표시

		:param input_cxy:
		:param zoom_no:
		:return:
		"""
		if not input_cxy:
			input_cxy = self.varx["basic_cxy"](input_cxy)

		self.main_map = folium.Map(
			location=input_cxy,
			zoom_start=zoom_no,
			# width=750,
			# height=500,
			# tiles='Stamen Toner' #타일의 종류를 설정하는 것이다
		)
		return self.main_map

	def make_menu_with_main_n_sub_menu(self, input_lists, main_n_sub, icon_n_color):
		"""
		input_lists = [
			['37.55440684521157', '127.12937429453059','food_land','방이 샤브샤브','맛나는데 여자들이 더 좋아해요'],
			['37.1834787433397','128.466953597959','food_land','미탄집','메밀전병'],
			['37.2079513137108','128.986557255629','food_land','구와우순두부','순두부'],
			]

		# 메인 메뉴와 서브메뉴를 정의한다
		main_n_sub = [['육해공군', 'food_land', 'food_sea', 'food_sky'], ["카페를 한눈에", 'cafe', 'food_etc','etc']]
		# 서브메뉴에 보일 아이콘과 색을 정의한다
		icon_n_color = {'food_land': ['lightred', 'cloud'], 'food_sea': ['gray', 'info-sign'], 'food_sky': ['lightgreen', 'star'], 'cafe': ['gray', 'info-sign'], 'food_etc': ['lightgreen', 'star'], 'etc': ['pink', 'bookmark']}

		:param input_lists:
		:param main_n_sub:
		:param icon_n_color:
		:return:
		"""
		menu_dic = {}
		sub_menu_dic = {}
		for ix, one_list in enumerate(main_n_sub):
			exec(f"main_menu_{ix} = folium.FeatureGroup(name='{one_list[0]}')")
			exec(f"self.main_map.add_child(main_menu_{ix})")
			exec(f"menu_dic['{one_list[0]}'] = main_menu_{ix}")

			for iy, sub_menu in enumerate(one_list[1:]):
				exec(f"sub_menu_{iy} = plugins.FeatureGroupSubGroup(main_menu_{ix}, '{sub_menu}')")
				exec(f"self.main_map.add_child(sub_menu_{iy})")
				exec(f"sub_menu_dic['{sub_menu}'] = sub_menu_{iy}")

		# 만약 icon_n_color에 아무런 값도 없을때 만들어 지는 것
		if not icon_n_color:
			icon_type = self.get_icon_type()
			color_type = self.get_color_type()
			icon_color = {}
			for ix, one_list in enumerate(main_n_sub):
				for iy, sub_menu in enumerate(one_list[1:]):
					icon_color[sub_menu] = [color_type[ix + iy], icon_type[ix + iy]]
			print(icon_color)

		folium.LayerControl(collapsed=False).add_to(self.main_map)
		for one_data in input_lists:
			folium.Marker(
				location=[one_data[0], one_data[1]],
				popup=one_data[2],
				icon=folium.Icon(color=icon_n_color[one_data[2]][0], icon=icon_n_color[one_data[2]][1]),
				tooltip=one_data[3],
			).add_to(sub_menu_dic[one_data[2]])

	def make_sub_menu_group(self, top_menu_title, category_location, input_title, all_data_set):
		"""
		서브 메뉴를 만드는 것
		오른쪽의 선택하는 그룹에 나타나게 할것인지를 설정하는 것이다

		:param top_menu_title:
		:param category_location:
		:param input_title:
		:param all_data_set:
		:return:
		"""
		main_map_obj = self.make_map_obj("", 8)
		dic_sub_menus = {}
		fg_name = folium.FeatureGroup(name=top_menu_title)
		main_map_obj.add_child(fg_name)

		for num in range(len(category_location)):
			sun_menu_name = category_location[num]
			aaa = plugins.FeatureGroupSubGroup(fg_name, sun_menu_name, show=True)
			main_map_obj.add_child(aaa)
			dic_sub_menus[sun_menu_name] = aaa

			for one_dic in all_data_set:
				if one_dic[input_title] in list(dic_sub_menus.keys()):
					folium.Marker(
						location=one_dic["xy"],
						popup=folium.Popup(one_dic["iframe"]),
						icon=folium.Icon(icon_size=(25)),  # 아이콘을 설정한 것이다
						tooltip=one_dic["title"],
					).add_to(dic_sub_menus[one_dic[input_title]])

	def make_top_menu_group(self, top_menu_name):
		"""
		탑메뉴를 만드는 것

		:param top_menu:
		:return:
		"""
		main_map_obj = self.make_map_obj("", 8)
		top_menu_obj = folium.FeatureGroup(name=top_menu_name)
		main_map_obj.add_child(top_menu_name)
		return [top_menu_obj, main_map_obj]

	def make_unique_list(self, input_lists, input_no):
		"""
		리스트의 자료중에서 고유한것들만 돌려주는 것

		:param input_lists:
		:param input_no:
		:return:
		"""
		result = set()
		for one in input_lists:
			result.add(one[input_no])
		return list(result)

	def manual_for_words(self):
		"""
		용어 정의에 대한 설명
		:return:
		"""
		result = """
		cxy : coordinate xy의 뜻으로 지도좌표를 뜻한다

		"""
		return result

	def minimap(self):
		"""
		화면에 미니지도를 넣는것
		:return:
		"""
		minimap = plugins.MiniMap()
		self.main_map.add_child(minimap)

	def mouse_position(self):
		"""
		마우스의 위치를 알려주는 것을 넣는 것
		:return:
		"""
		folium.plugins.MousePosition().add_to(self.main_map)

	def my_position(self):
		"""
		나의 위치를 알려주는 것을 넣는 것
		:return:
		"""
		folium.plugins.LocateControl().add_to(self.main_map)

	def new_map(self, start_cxy="", zoom_no=8, **input_dic):
		"""
		지도의 중앙지점과 줌의 정도를 설정한다
		우리나라의 중앙일것 같은 온양온천을 기준으로 표시

		:param start_cxy:
		:param zoom_no:
		:param input_dic:
		:return:
		"""

		if not start_cxy:
			start_cxy = [37.388738, 126.967983]

		self.varx.update(input_dic)
		self.varx["location"] = start_cxy
		self.varx["zoom_start"] = zoom_no

		self.main_map = folium.Map(
			zoom_control=self.varx["zoom_control"],
			scrollWheelZoom=self.varx["scrollWheelZoom"],
			dragging=self.varx["dragging"],
			location=self.varx["location"],
			width=self.varx["width"],
			height=self.varx["height"],
			min_zoom=self.varx["min_zoom"],
			max_zoom=self.varx["max_zoom"],
			zoom_start=self.varx["zoom_start"],
			tiles=self.varx["tiles"],
			prefer_canvas=self.varx["prefer_canvas"],
			control_scale=self.varx["control_scale"],
			no_touch=self.varx["no_touch"],
			font_size=self.varx["font_size"],
			attr=self.varx["attr"],
			crs=self.varx["crs"],
			min_lat=None,
			max_lat=None,
			min_lon=None,
			max_lon=None,
		)

		return self.main_map

	def new_map_as_empty(self, start_cxy="", zoom_no=8, **input_dic):
		"""
		지도없이 좌표에 표시만 하기
		지도의 중앙지점과 춤의 정도를 설정한다
		우리나라의 중앙일것같은 온양은천을 기준으로 표시

		:param start_cxy:
		:param zoom_no:
		:param input_dic:
		:return:
		"""

		# self.main_map = folium.Map( location=start_cxy, zoom_start=zoom_no, tiles=None)
		self.varx["tiles"] = None
		self.new_map(start_cxy, zoom_no, **input_dic)

	def read_json_data(self, file_path):
		"""
		json자료를 읽어오는 것
		:param file_path:
		:return:
		"""
		with open(file_path, mode='rt', encoding='utf-8') as f:
			result = json.loads(f.read())
			f.close()
		return result

	def reset_for_font_detail(self):
		"""
		폰트에 대한 정보를 저장하는 사전을 reset하는 것
		:return:
		"""
		self.font_detail = {"align_,": None, "align_h": None, "bold": None, "color": None, "size": None, "italic": None, "name": None, "strike": None, "sub": None, "super": None, "alpha": None,
							"underline": None, }

	def reset_for_line_detail(self):
		"""
		라인에 대한 정보를 저장하는 사전을 reset하는 것

		:return:
		"""
		self.line_detail = {"style": None, "color": None, "width": None, }

	def reset_for_marker_detail(self):
		"""
		마커에 대한 정보를 저장하는 사전을 reset하는 것

		:return:
		"""
		self.marker_detail = {"style": "arrow-down", "popup": None, "tooltip": None, "color": None, "icon": None, "line_ style": None, "line _color": None, "line_width": None, }

	def reset_for_outline_detail(self):
		"""
		아웃라인에 대한 정보를 저장하는 사전을 reset하는 것

		:return:
		"""
		self.outline_detail = {"style": None, "color": None, "width": None}

	def set_for_line_detail(self, i_style=None, i_xcolor=None, i_width=None, i_alpha_0to1=0):
		"""
		라인의 세부정보를 설정하는 것

		:param i_style:
		:param i_xcolor:
		:param i_width:
		:param i_alpha_0to1:
		:return:
		"""
		if i_style: self.line_detail["style"] = i_style
		if i_xcolor: self.line_detail["color"] = i_xcolor
		if i_width: self.line_detail["width"] = i_width
		if i_alpha_0to1: self.line_detail["alpha"] = i_alpha_0to1

	def set_for_marker_detail(self, i_style="arrow-down", i_color=None, i_icon=None, i_line_style=None, i_line_color=None, i_line_width=None):
		"""
		마커정보에 대한 것을 설정하는 것

		:param i_style:
		:param i_color:
		:param i_icon:
		:param i_line_style:
		:param i_line_color:
		:param i_line_width:
		:return:
		"""
		if i_style: self.line_detail["style"] = i_style
		if i_color: self.line_detail["color"] = i_color
		if i_icon: self.line_detail["icon"] = i_icon
		if i_line_style: self.line_detail["line_style"] = i_line_style
		if i_line_color: self.line_detail["line_color"] = i_line_color
		if i_line_width: self.line_detail["line_width"] = i_line_width

	def setup_dragging_for_map_by_0or1(self, input_tf=False):
		"""
		드래그를 가능하게 할것인지 : 키거나 끄는 설정

		:param input_tf:
		:return:
		"""
		self.varx["dragging"] = input_tf

	def setup_height_for_map(self, input_no):
		"""
		화면의 크기(높이)를 설정

		:param input_no:
		:return:
		"""
		self.varx["width"] = input_no

	def setup_width_for_map(self, input_no):
		"""
		화면의 크기(넓이)를 설정

		:param input_no:
		:return:
		"""
		self.varx["width"] = input_no

	def setup_onoff_for_zoom_by_0or1(self, input_tf=False):
		"""
		줌 : 키거나 끄는 설정

		:param input_tf:
		:return:
		"""
		self.varx["zoom_control"] = input_tf

	def setup_scroll_wheel_zoom_by_0or1(self, input_tf=False):
		"""
		마우스 스크롤 : 키거나 끄는 설정

		:param input_tf:
		:return:
		"""
		self.varx["scrollWheelZoom"] = input_tf

	def setup_show_cxy_by_click(self):
		"""
		클릭하면 좌표를 표시하는 기능
		:return:
		"""
		self.main_map.add_child(folium.LatLngPopup())

	def setup_zoom_by_0or1(self, input_tf=False):
		"""
		줌 : 키거나 끄는 설정

		:param input_tf:
		:return:
		"""
		self.varx["zoom_control"] = input_tf

	def setup_zoom_start_by_0to18(self, input_no=8):
		"""
		맨처음 보이는 지도의 줌상태를 설정하는 것

		:param input_no:
		:return:
		"""
		self.varx["zoom_start"] = input_no

	def show_map(self, input_file_name="xymap_sample.html"):
		"""
		사전을 보여주는 메소드

		:param input_file_name:
		:return:
		"""
		if not input_file_name.endswith(".html"): input_file_name = input_file_name + ".html"
		self.main_map.save(input_file_name)
		webbrowser.open('file://' + os.path.abspath(input_file_name))

	def sub_menu(self, top_menu_title, category_location, input_title, all_data_set):
		"""
		서브 메뉴를 만드는 것
		오른쪽의 선택하는 그룹에 나타나게 할것인지를 설정하는 것이다

		:param top_menu_title:
		:param category_location:
		:param input_title:
		:param all_data_set:
		:return:
		"""
		self.main_map = self.make_map_obj("", 8)
		dic_sub_menus = {}
		fg_name = folium.FeatureGroup(name=top_menu_title)
		self.main_map.add_child(fg_name)

		for num in range(len(category_location)):
			sun_menu_name = category_location[num]
			aaa = plugins.FeatureGroupSubGroup(fg_name, sun_menu_name, show=True)
			self.main_map.add_child(aaa)
			dic_sub_menus[sun_menu_name] = aaa

			for one_dic in all_data_set:
				if one_dic[input_title] in list(dic_sub_menus.keys()):
					folium.Marker(
						location=one_dic["xy"],
						popup=folium.Popup(one_dic["iframe"]),
						icon=folium.Icon(icon_size=(25)),  # 아이콘을 설정한 것이다
						tooltip=one_dic["title"],
					).add_to(dic_sub_menus[one_dic[input_title]])

	def top_menu_group(self, top_menu_name):
		"""
		탑메뉴를 만드는 것

		:param top_menu:
		:return:
		"""
		self.main_map = self.make_map_obj("", 8)
		top_menu_obj = folium.FeatureGroup(name=top_menu_name)
		self.main_map.add_child(top_menu_name)
		return [top_menu_obj, self.main_map]

	def write_text_at_cxy_with_box(self, input_cxy, input_text=""):
		"""
		사각형안에 글씨쓰기

		:param input_text:
		:param input_cxy:
		:return:
		"""
		folium.map.Marker(input_cxy,
						  icon=DivIcon(
							  icon_size=(150, 50),
							  icon_anchor=(0, 0),
							  html=f"""<div style="display: flex; justify-content: center; align items: center; border: 2px solid blue; background-color: lightblue; 
						  padding: 10px;p style="margin: 0;">{input_text}</p></div>""", ),
						  ).add_to(self.main_map)

	def write_text_at_cxy_with_circle(self, input_cxy, input_text="123"):
		"""
		원안에 글자를 쓰도록 만든것
		사각형의 형태가 기본이라, 너무 많이 쓰면 원을 조금 넘어간다

		:param input_cxy:
		:param input_text:
		:return:
		"""
		folium.map.Marker(input_cxy, icon=DivIcon(icon_size=(50, 50), icon_anchor=(0, 0),
												  html=f"""<div style="display: flex; border-radius: 50%; justify-content: center; align items: center; border: 2px solid blue; background-color: lightblue; 
						padding: 10px;p style="margin: 0;">{input_text}</p></div>""", )).add_to(self.main_map)


	def make_easy_maker_map_for_l2d_by_cx_cy_title_menu(self, input_cx_cy_title_menu_2d):
		"""
		자료만 맞게 넣으면 자동으로 map을 만들어서 돌려주는 것

		:param input_l2d: [[cx, cy, tool_tip, menu]....] 이런 형태의 자료
		:return:
		"""
		self.make_map_obj("", 7)
		self.draw_marker_at_cxy2d_for_tooltip_menu(input_cx_cy_title_menu_2d)
		self.show_map()


	def make_easy_line_n_number_map_for_l2d_by_cx_cy_title_menu(self, input_cx_cy_title_2d):
		"""
		자료를 넣으면, 선을 그으면서 순서대로 번호를 붙여주는것

		:param input_l2d: [[cx, cy, tool_tip]....] 이런 형태의 자료
		:return:
		"""
		self.make_map_obj("", 7)
		self.draw_line_at_cxy2d(input_cx_cy_title_2d, "blu50")
		self.draw_marker_at_cxy2d_with_serial_no(input_cx_cy_title_2d)
		self.show_map()


	def make_easy_maker_map_for_excel_data_by_cx_cy_title_menu(self, sheet_name, xyxy):
		"""
		자료만 맞게 넣으면 자동으로 map을 만들어서 돌려주는 것

		:param input_l2d: [[cx, cy, tool_tip, menu]....] 이런 형태의 자료
		:return:
		"""
		import xy_excel
		excel = xy_excel.xy_excel()
		input_cx_cy_title_menu_2d = excel.read_range(sheet_name, xyxy)

		self.make_map_obj("", 7)
		self.draw_marker_at_cxy2d_for_tooltip_menu(input_cx_cy_title_menu_2d)
		self.show_map()

	def check_dosi(self, input_value):
		#도에 대한 것인지를 확인하는 것
		result = False
		dosi_add = {"경북":"경상북도","경남":"경상남도", "전남":"전라남도", "전북":"전라북도", "충남":"충청남도", "충북":"충청북도"}
		temp.do.update(dosi_add)
		for one_value in list(temp.do.keys()):
			if one_value[0:2]== input_value[0:2]:
				result = temp.do[one_value]
				break
		return result

	def check_si(self, input_value):
		#시에 대한 것인지를 확인하는 것
		result = False
		if input_value[-1] != "시":
			input_value = input_value +"시"
		try:
			result = temp.si[input_value]
		except:
			pass
		return result

	def check_gungu(self, input_value):
		#군구자료를 빼먹음
		#읍면동의 자료를 확인
		result = False
		try:
			if input_value[-1] in "군":
				result = temp.gun[input_value]
			elif input_value[-1] in "구":
				result = temp.gu[input_value]
		except:
			pass
		return result

	def check_ymdg(self, input_value):
		#읍면동가의 자료를 확인
		result = False
		try:
			if input_value[-1] in "읍":
				result = temp.yep[input_value]
			elif input_value[-1] in "면":
				result = temp.myun[input_value]
			elif input_value[-1] in "동":
				result = temp.dong[input_value]
			elif input_value[-1] in "가":
				result = temp.ga[input_value]
		except:
			pass
		return result

	def check_rijangso(self, input_value):
		#리소의 자료를 확인
		result = False
		try:
			if input_value[-1] in "리":
				result = temp.ri[input_value]
			elif input_value[-1] in "소":
				result = temp.so[input_value]
		except:
			pass
		return result

	def check_kor_n_num(self, input_text):
		#적절한 주소인지 알아보는것
		rex = xy_re.xy_re()
		my_sql = "[한글:1~10][숫자:0~2][한글:1~2]"
		result = rex.is_fullmatch_with_xsql(my_sql, input_text)
		return result

	def check_input_address_list(self, input_l1d):
		result = []
		for one in input_l1d:
			temp = self.check_kor_n_num(one)
			if temp:
				result.append(one)
		return result

	def check_address(self, input_address):
		#찾을 주소에 대한것만 추출하는 것이다
		address_list1d = input_address
		if type(input_address) ==type("abc"):
			address_list1d = input_address.split()
		result = self.check_input_address_list(address_list1d)
		return result

	def check_map_xy_data_for_address(self, input_address):
		#각 주소에 맞는 자료를 갖고온다
		result = {}
		checked_address_list1d = self.check_address(input_address)
		print(checked_address_list1d)
		dosi_found = False
		si_found = False
		gungu_found = False
		ymdg_found = False
		rijangso_found = False

		for index, address_part in enumerate(checked_address_list1d):
			if not dosi_found:
				dosi_data = self.check_dosi(address_part)
				if dosi_data:
					dosi_found = True
					result[address_part] = dosi_data
			if not si_found:
				si_data = self.check_si(address_part)
				if si_data:
					si_found = True
					result[address_part] = si_data

			if not gungu_found:
				gungu_data = self.check_gungu(address_part)
				if gungu_data:
					gungu_found = True
					result[address_part] = gungu_data
			if not ymdg_found:
				ymdg_data = self.check_ymdg(address_part)
				if ymdg_data:
					ymdg_found = True
					result[address_part] = ymdg_data

			if not rijangso_found:
				rijangso_data = self.check_rijangso(address_part)
				if rijangso_data:
					rijangso_found = True
					result[address_part] = rijangso_data
		return result

	def kyo_jip_hap(self, input_1, input_2):
		#두 범위중에서 교집합만 추출하는것
		result =[]
		for value1 in input_1:
			value_1_split = str(value1).split("~")
			for value2 in input_2:
				value_2_split = str(value2).split("~")
				if len(value_1_split) ==2 and len(value_2_split) ==2:
					if int(value_1_split[0]) <= int(value_2_split[0]) and int(value_1_split[1]) >= int(value_2_split[1]):
						result.append(value2)
				elif len(value_1_split) ==2 and len(value_2_split) ==1:
					if int(value_1_split[0]) <= int(value_2_split[0]) <= int(value_1_split[1]):
						result.append(value2)
				elif len(value_1_split) ==1 and len(value_2_split) ==1:
					result.append(value2)
		return result

	def final_xy(self, input_value):
		#최종적인 위도/경도의 자료를 갖고옵니다
		result = []
		for one in input_value:
			if "~" in str(one):
				value_split = str(one).split("~")
				int_value = int((int(value_split[0]) + int(value_split[1]))/2)
				result = temp.xy[int_value]
			else:
				result = temp.xy[int(one)]
		return result


	def chane_address_to_cxy(self, input_address):
		no_for_address = self.check_map_xy_data_for_address(input_address)
		print("주소에 해당되는것 => ", no_for_address)
		val_list = list(no_for_address.values())
		print("찾은 번호값 => ", val_list)
		final_no = []
		for index in range(len(val_list)):
			if index == 0:
				final_no = val_list[0]
			else:
				final_no = self.kyo_jip_hap(final_no, val_list[index])
		print("최종 번호값 => ", final_no)
		print("최종 위도/경도값 => ", self.final_xy(final_no))
		return self.final_xy(final_no)
