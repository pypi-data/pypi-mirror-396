# -*- coding: utf-8 -*-
import datetime

class xy_example:
	"""
	d1d : dic - 1차원
	d2d : dic - 2차원 dic
	l1d : list - 1차원
	l2d : list - 2차원
	t2d : text - 텍스트로 여러줄인것
	"""
	def d1d_machine_name_01(self):
		result = {"밸브": "valve", "교반기": "agitator", "아지테이터": "agitator",
							   "송풍기": "blower", "블로어": "blower", "s/p": "spare part",
							   "케이블": "cable", "스페어파트": "spare part", "컨트롤밸브": "control valve",
							   "컨트롤벨브": "control valve",
							   "컨테이너": "container", "정화관": "", "배터리": "battery", "차저": "charger",
							   "액츄에이터": "actuator",
							   "토너공장": "", "환경운영": "", "다이아프램": "diaphgram", "압축기": "compressor",
							   "컨트롤valve": "control valve",
							   "볼valve": "ball valve", "그린소재": "", "메셀로스": "", "신설": "", "개선": "",
							   "완제품": "", "호이스트": "hoist", "확보용": "", "보수재": "", "작업용": "",
							   "시운전": "", "노후장치교체": "", "환경설비": "", "변경": "", "기존품": "",
							   "교체관련": "", "교쳬": "", "호환": "", "판넬": "panel", "배관재": "piping",
							   "파이프": "pipe",
							   "펌프": "pump", "배관담당": "", "보수용": "", "보일러": "boiler", "자동화": "",
							   "변압기": "transformer", "티타늄": "titanium", "라인드": "linned",
							   "탱크": "tank", "피팅류": "fitting", "컨트롤": "control",
							   "글로브": "globe", "열교환기": "heat exchanger",
							   "인버터판넬": "invertor panel", "스위치": "switch",
							   "산소농도측정기": "o2 analyzer", "수분분석기": "h20 analyzer",
							   "분석기": "analyzer", "인버터": "invertor", "가구": "", "가성소다": "",
							   "가스감지기": "gas detector", "가스검지기": "gas detector",
							   "가스켓": "gasket", "가스탐지기": "gas detector", "감지": "", "검사장비": "",
							   "경고표지": "", "계단": "",
							   "교체": "", "구공장": "", "구동부": "", "구매": "", "구매요청건": "", "구축": "",
							   "구축용": "", "기계담당": "",
							   "기업용": "", "기존": "", "기초물성": "", "냉매합리화": "", "노후": "",
							   "노후panel": "", "단관": "",
							   "담당": "", "등": "", "等": "", "마곡연구소": "", "메인": "", "목": "",
							   "및": "", "보수": "", "보완": "",
							   "부속10종": "", "비용정산": "", "상부": "", "선입고": "", "설치": "", "순환": "",
							   "순환식": "", "스티커": "",
							   "신규": "", "신규제작": "", "연구1팀": "", "연구부문": "", "연구소": "", "이동": "",
							   "이물": "", "이송": "",
							   "일반": "", "일반형": "", "전해c": "", "전해c공장": "", "전해공장용": "", "주요": "",
							   "철거": "", "추가": "",
							   "추가부품": "", "추가정산": "", "투자": "", "투자관련": "", "포함": "",
							   "한국요꼬가와전기": "", "한중유화": "",
							   "합리화": "", "합성공정": "", "협력사": "", }
		return result

	def d2d_country_01(self):
		result = {
			"1번째열": {'Country': 'Russia', 'Capital': 'Moscow', 'Area(Sq.Miles)': 6601670, 'Population': 146171015},
			"2번째열": {'Country': 'Canada', 'Capital': 'Ottawa', 'Area(Sq.Miles)': 3855100, 'Population': 38048738},
			"3번째열": {'Country': 'China', 'Capital': 'Beijing', 'Area(Sq.Miles)': 3705407, 'Population': 1400050000},
			"4번째열": {'Country': 'United States of America', 'Capital': 'Washington, D.C.',
					 'Area(Sq.Miles)': 3796742, 'Population': 331449281},
			"5번째열": {'Country': 'Brazil', 'Capital': 'Brasília', 'Area(Sq.Miles)': 3287956,
					 'Population': 210147125},
			"6번째열": {'Country': 'Russia', 'Capital': 'Moscow', 'Area(Sq.Miles)': 6601670, 'Population': 146171015},
			"7번째열": {'Country': 'Canada', 'Capital': 'Ottawa', 'Area(Sq.Miles)': 3855100, 'Population': 38048738},
			"8번째열": {'Country': 'China', 'Capital': 'Beijing', 'Area(Sq.Miles)': 3705407, 'Population': 1400050000},
			"9번째열": {'Country': 'United States of America', 'Capital': 'Washington, D.C.',
					 'Area(Sq.Miles)': 3796742, 'Population': 331449281},
			"10번째열": {'Country': 'Brazil', 'Capital': 'Brasília', 'Area(Sq.Miles)': 3287956,
					  'Population': 210147125}
		}
		return result

	def d2d_01(self):
		result  =  [
			{"x": 2, "y": 1, "kind_1": "basic", "kind_2": "date", "value": datetime.datetime(2002, 2, 2)},
			{"x": 2, "y": 3, "kind_1": "basic", "kind_2": "basic", "text": "값"},
			{"x": 2, "y": 5, "kind_1": "basic", "kind_2": "basic", "text": "값"},
			{"x": 2, "y": 7, "kind_1": "basic", "kind_2": "date", "value": datetime.datetime(2002, 2, 2)},
			{"x": 2, "y": 6, "kind_1": "tool_tip", "text": "tool_tip", "tool_tip": "툴팁입니다"},
			{"x": 5, "y": 3, "kind_1": "widget", "kind_2": "combo", "value": [1, 2, 3, 4, 5]},
			{"x": 5, "y": 5, "kind_1": "widget", "kind_2": "check_box", "checked": 1, "text": "check"},
			{"x": 5, "y": 7, "kind_1": "widget", "kind_2": "progress_bar", "value": 30},
			{"x": 5, "y": 8, "kind_1": "widget", "kind_2": "button", "caption": "button_1", "action": "action_def"},
			{"x": 10, "y": 10, "kind_1": "memo", "value": "memo memo"},
			{"x": 2, "y": 2, "kind_1": "memo", "value": "memo memo"},
			{"x": 7, "y": 3, "kind_1": "font_color", "value": [255, 63, 24]},
			{"x": 7, "y": 5, "kind_1": "background_color", "value": [255, 63, 24]}, ]
		return result

	def l1d_word_01(self):
		result = ["1: 가나다", "2: 라마바", "3: 사아자", "4: 차카파", "5: 가나다라마바", "17.: 사아자차카파파하", "8888: ABC 가나다라마", "9: 카파파하 BCD"]
		return result

	def l1d_mixed_data_01(self):
		result  = ["1번째열_2번째", 'A1', "", None,  [], (), '러시아_인가?','Capital', 'Moscow', '면적---', 6601670,   '인구', "14617_1015"]
		return result

	def l1d_mixed_data_02(self):
		result = [12345, 12345.67, "1234567",
						'A1B2', "가나다#$%@", None, [],
						(), 'abcd=efgh', 'Capital',
						'Moscow', '면적---', 6601670,
						'인구', "14617_1015"]
		return result

	def l1d_datetime_01(self):
		result  = [
			"20230301",
			'02/28/2023 02:30 PM',
			'180919 015519',
			'18/09/19 01:55:19',
			'2019-02-02 15:56:15.197103-05:00',
			'2018-06-29 08:15:27.243860',
			'2018-03-12T10:12:45Z',
			'2018-03-12',
			'2018-06-29 17:08:00.586525+00:00',
			'2018-06-29 17:08:00.586525+05:00',
			'Jun 28 2018 7:40AM',
			'Jun 28 2018 at 7:40AM',
			'September 18, 2017, 22:19:55',
			'Sun, 05/12/1999, 12:30PM',
			'Mon, 21 March, 2015',
			'Tuesday , 6th September, 2017 at 4:30pm'
		]
		return result

	def l1d_macine_name_01(self):
		result  =  ['fitting', 'ball',
										'flowmeter', 'on-off',
										'battery', 'flange',
										'electric', 'cable',
										'gasket', 'seal',
										'invertor', 'plate',
										'level', 'gauge', 'gas',
										'meter', 'centrifugal',
										'magnetic', 'psv',
										'titanium',
										'pressure', 'motor',
										'boiler', 'globe',
										'gate', 'transformer',
										'charger', 'blower',
										'inverter',
										'orifice', 'ph', 'ebd',
										'mass', 'plug',
										'diaphragm', 'dcs',
										'detector', 'heater',
										'hv', 'scale',
										'instrument', 'ups',
										'pg', 'reactor',
										'compressor', 'vessel',
										'butterfly',
										'mechanical', 'element',
										'tube', 'bellows',
										'mixer', 'agitator',
										'hose', 'diaphgram',
										'separator', 'mcc',
										'plc', 'frp',
										'cooler', 'rubber',
										'ngr', 'bolt', 'nut',
										'rtd', 'bolt/nut',
										'graphite', 'drum',
										'relay', 'LV',
										'palstic', 'rotary',
										'sensor', 'microwave',
										'column', 'screen',
										'manual', 'balance',
										'bundle',
										'plastivc', 'acb',
										'carbon', 'change',
										'cell', 'strainer',
										'type', 'cover', 'tg',
										'membrane', 'prv',
										'ptfe', 'check',
										'nickel', 'analyzer',
										'oil', 'water',
										'temperature', 'glove',
										'channel', 'ring',
										'etfe', 'sheet', 'tms',
										'scrubber', 'lift',
										'oven', 'holder',
										'container', 'cctv',
										'vcb', 'condensor',
										'casting', 'metal',
										'rupture', 'disc',
										'gear', 'screw', 'leak',
										'3-way', 'canned',
										'package', 'dryer',
										'feeder', '양극전극', 'bag',
										'air', '농도계', 'pin',
										'impeller', 'metering',
										'kit', 'actuator',
										'aircon',
										'column', 'compressor',
										'concentration',
										'condenser',
										'conductivity',
										'connector',
										'contcnrator',
										'contol', 'control',
										'control ball valve',
										'control-valve',
										'convection',
										'conveyor', 'cooler',
										'cover', 'crusher',
										'cryogel', 'cw',
										'cyclone', 'cylinder',
										'd/p']
		return result

	def l1d_country_name_01(self):
		result  =  ['가나', '가봉', '가이아나',
								 '감비아', '과테말라', '그레나다',	 '그루지야',
								 '그리스', '기니', '기니비사우', '나미비아', '나우루', '나이지리아',
								 '남수단', '남아프리카 공화국',	 '네덜란드', '네팔', '노르웨이',
								 '뉴질랜드', '니제르', '니카라과', '덴마크', '도미니카 연방',
								 '도미니카 공화국', '독일', '동티모르',	 '라오스', '라이베리아', '라트비아',
								 '러시아', '레바논', '레소토', '루마니아', '룩셈부르크',
								 '르완다', '리비아', '리투아니아', '리히텐슈타인', '마다가스카르',
								 '마셜 제도', '말라위', '말레이시아',
								 '말리', '멕시코', '모나코',
								 '모로코', '모리셔스',
								 '모리타니', '모잠비크', '몬테네그로',
								 '몰도바', '몰디브', '몰타', '몽골',
								 '미국',
								 '미얀마', '미크로네시아 연방',
								 '바누아투', '바레인', '바베이도스',
								 '바티칸', '바하마', '방글라데시',
								 '베네수엘라', '베냉', '베트남',
								 '벨기에', '벨라루스', '벨리즈',
								 '보스니아 헤르체고비나', '보츠와나',
								 '볼리비아', '부룬디', '부르키나파소',
								 '부탄', '북마케도니아',
								 '북조선(북한)', '불가리아', '브라질',
								 '브루나이', '산마리노', '사모아',
								 '사우디아라비아', '상투메 프린시페',
								 '세네갈', '세르비아', '세이셸',
								 '세인트루시아', '세인트빈센트 그레나딘',
								 '세인트키츠 네비스', '소말리아',
								 '솔로몬 제도', '수단', '수리남',
								 '스리랑카', '스웨덴', '스위스',
								 '스페인(에스파냐)', '슬로바키아',
								 '슬로베니아', '시리아', '시에라리온',
								 '싱가포르', '아랍에미리트',
								 '아르메니아', '아르헨티나',
								 '아이슬란드', '아이티', '아일랜드',
								 '아제르바이잔',
								 '아프가니스탄', '안도라', '알바니아',
								 '알제리', '앙골라', '앤티가 바부다',
								 '에스와티니', '에콰도르',
								 '에리트레아', '에스토니아',
								 '에티오피아', '엘살바도르', '영국',
								 '예멘', '오만', '오스트레일리아',
								 '오스트리아', '온두라스', '요르단',
								 '우간다', '우루과이', '우즈베키스탄',
								 '우크라이나', '이라크',
								 '이란', '이스라엘', '이집트',
								 '이탈리아', '인도', '인도네시아',
								 '일본', '자메이카', '잠비아',
								 '적도 기니', '중앙아프리카공화국',
								 '중화인민공화국', '지부티', '짐바브웨',
								 '차드', '체코', '칠레',
								 '카메룬', '카자흐스탄', '카보베르데',
								 '카타르', '캄보디아', '캐나다',
								 '케냐', '코모로', '코스타리카',
								 '코트디부아르', '쿠바', '쿠웨이트',
								 '콜롬비아', '콩고인민공화국',
								 '콩고민주공화국', '크로아티아',
								 '키르기스스탄', '키리바시', '키프로스',
								 '타지키스탄', '탄자니아', '태국',
								 '토고', '통가', '투르크메니스탄',
								 '투발루', '튀니지', '튀르키예',
								 '트리니다드 토바고', '파나마',
								 '파라과이', '파키스탄', '파푸아뉴기니',
								 '팔라우', '페루', '포르투갈',
								 '폴란드', '프랑스', '피지',
								 '핀란드', '필리핀', '한국',
								 '헝가리']
		return result

	def l1d_keyboard_action_01(self):
		result  = ['\\t', '\\n', '\\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
										 ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
										 '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
										 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
										 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
										 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
										 'browserback', 'browserfavorites', 'browserforward', 'browserhome',
										 'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
										 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
										 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1','f10',
										 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2','f20',
										 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
										 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
										 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
										 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
										 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
										 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
										 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
										 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
										 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop','subtract', 'tab',
										 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft','winright', 'yen',
										 'command', 'option', 'optionleft', 'optionright']
		return result

	def l1d_company_name_01(self):
		result = ["한강주식회사", "한강 주식회사", "한강㈜", "㈜한강", "한강(유)", "한강유한회사", "고려", "고구려", "백제", "신라", "고조선"]
		return result

	def l2d_machine_01(self):

		result  = [
			['fitting', 'ball', 'flowmeter', 'on-off', 'battery', 'flange', 'electric', 'cable', 'gasket', 'seal', ],
			['invertor', None, 'level', 'gauge', 'gas', 'meter', 'centrifugal', 'magnetic', 'psv', 'titanium', ],
			['pressure', 'motor', 'boiler', 'globe', 'gate', 'transformer', 'charger', 'blower', 'inverter', ],
			['', 'ph', 'ebd', 'mass', 'plug', 'diaphragm', 'dcs', 'detector', 'heater', 'hv', 'scale', ],
			['', 'ups', 'pg', 'reactor', '', 'vessel', 'butterfly', 'mechanical', 'element', ],
			['tube', 'bellows', 'mixer', '', 'hose', 'diaphgram', 'separator', 'mcc', 'plc', 'frp', ],
			['', 'rubber', 'ngr', 'bolt', '', 'rtd', 'bolt/nut', 'graphite', 'drum', 'relay', 'LV', ],
			[None, 'rotary', 'sensor', None, 'column', 'screen', 'manual', 'balance', 'bundle', ],
			['plastivc', 'acb', 'carbon', None, 'cell', 'strainer', 'type', 'cover', 'tg', 'membrane', 'prv', ],
			['ptfe', 'check', 'nickel', 'analyzer', 'oil', 'water', 'temperature', 'glove', 'channel', 'ring', ],
			['etfe', 'sheet', 'tms', 'scrubber', 'lift', 'oven', 'holder', 'container', 'cctv', 'vcb', 'condensor', ],
			['casting', 'metal', 'rupture', 'disc', 'gear', 'screw', 'leak', '3-way', 'canned', 'package', 'dryer', ],
			['feeder', '양극전극', 'bag', 'air', '농도계', 'pin', 'impeller', 'metering', 'kit', 'actuator', 'aircon', ],
			['column', 'compressor', 'concentration', 'condenser', 'conductivity', 'connector', 'contcnrator', ],
			['contol', 'control', 'control ball valve', 'control-valve', 'convection', 'conveyor', 'cooler', ],
			['cover', 'crusher', 'cryogel', 'cw', 'cyclone', 'cylinder', 'd/p']]
		return result

	def l2d_pcell_sample_01(self):

		result  = [["엑셀","쓰기", "3333셀(2,2)에 값넣기", """excel.write_value_in_cell("", [2, 2], "테스트입니다")"""],
				   ["엑셀","색칠하기","셀(2,3)에 빨간색 넣기", """excel.paint_scolor_in_cell("", [2, 3], "red")"""],
				   ["엑셀", "색칠하기", "셀(3,3)에 빨간색 넣기", """excel.paint_scolor_in_cell("", [2, 3], "red")"""],
				   ["엑셀123", "색칠하기", "셀(3,3)에 빨간색 넣기", """excel.paint_scolor_in_cell("", [2, 3], "red")"""],
				   ["기타", "삭제", "선택영역에서 전체가 빈 모든 x열 삭제", """excel.delete_empty_xline_in_range("",[1,1,10,10])"""],
				   ["기타", "삭제", "선택영역에서 전체가 빈 모든 y열 삭제", """excel.delete_empty_yline_in_range("",[1,1,10,10])"""],
				   ]
		return result

	def l2d_country_name_01(self):
		result  = [['가나', '가봉', '가이아나', '감비아', '과테말라', '그레나다', '그루지야'],
					['그리스', '기니', '기니비사우', '나미비아', '나우루', '나이지리아', '남수단','남아프리카 공화국'],
					['네덜란드', '네팔', '노르웨이', '뉴질랜드', '니제르', '니카라과', '덴마크', '도미니카 연방'],
					['도미니카 공화국', '독일', '동티모르', '라오스', '라이베리아', '라트비아', '러시아', '레바논'],
					['레소토', '루마니아', '룩셈부르크', '르완다', '리비아', '리투아니아', '리히텐슈타인', '마다가스카르'],
					['마셜 제도', '말라위', '말레이시아', '말리', '멕시코', '모나코', '모로코', '모리셔스'],
					['모리타니', '모잠비크', '몬테네그로', '몰도바', '몰디브', '몰타', '몽골', '미국'],
					['미얀마', '미크로네시아 연방', '바누아투', '바레인', '바베이도스', '바티칸', '바하마', '방글라데시'],
					['베네수엘라', '베냉', '베트남', '벨기에', '벨라루스', '벨리즈', '보스니아 헤르체고비나', '보츠와나'],
					['볼리비아', '부룬디', '부르키나파소', '부탄', '북마케도니아', '북조선(북한)', '불가리아',	 '브라질'],
					['브루나이', '산마리노', '사모아', '사우디아라비아', '상투메 프린시페', '세네갈', '세르비아','세이셸'],
					['세인트루시아', '세인트빈센트 그레나딘', '세인트키츠 네비스', '소말리아', '솔로몬 제도', '수단', '수리남'],
					['스리랑카', '스웨덴', '스위스', '스페인(에스파냐)', '슬로바키아', '슬로베니아', '시리아','시에라리온'],
					['싱가포르', '아랍에미리트', '아르메니아', '아르헨티나', '아이슬란드', '아이티', '아일랜드','아제르바이잔'],
					['아프가니스탄', '안도라', '알바니아', '알제리', '앙골라', '앤티가 바부다', '에스와티니', '에콰도르'],
					['에리트레아', '에스토니아', '에티오피아', '엘살바도르', '영국', '예멘', '오만', '오스트레일리아'],
					['오스트리아', '온두라스', '요르단', '우간다', '우루과이', '우즈베키스탄', '우크라이나', '이라크'],
					['이란', '이스라엘', '이집트', '이탈리아', '인도', '인도네시아', '일본', '자메이카',	 '잠비아'],
					['적도 기니', '중앙아프리카공화국', '중화인민공화국', '지부티', '짐바브웨', '차드', '체코',	 '칠레'],
					['카메룬', '카자흐스탄', '카보베르데', '카타르', '캄보디아', '캐나다', '케냐', '코모로', '코스타리카'],
					['코트디부아르', '쿠바', '쿠웨이트', '콜롬비아', '콩고인민공화국', '콩고민주공화국', '크로아티아'],
					['키르기스스탄', '키리바시', '키프로스', '타지키스탄', '탄자니아', '태국', '토고', '통가','투르크메니스탄'],
					['투발루', '튀니지', '튀르키예', '트리니다드 토바고', '파나마', '파라과이', '파키스탄','파푸아뉴기니'],
					['팔라우', '페루', '포르투갈', '폴란드', '프랑스', '피지', '핀란드', '필리핀', '한국','헝가리']]
		return result

	def l2d_macine_name_01(self):
		result  = [
			["드럼", " drum "], ["펄프밀", " pulp mill "], ["슬러리", " slury "], ["펄프분쇄기", " pulp mill "],
			["엘레먼트", " element "],
			["가스캐비넷", " gas cabinet "], ["공기 compressor", " air compressor "], ["고압", " high voltage "],
			["건조기", " dryer "], ["믹서", " mixer "],
			["가스감지기", " gas detector "], ["가스검지기", " gas detector "], ["가스탐지기", " gas detector "], ["게이트", " gate "],
			["v/v", " valve "], ["on-off", " on/off "], ["on off", " on/off "], ["s/p", " spare parts "],
			["컴프레서", " compressor "],
			["쿨러", " cooler "], ["톤백", " ton bag "], ["체크", " check "], ["저압", " low voltage "],
			["판형", " plate type "], ["플라스틱", " plastic "], ["티타늄", " titanium "],
			["파이프", " pipe "], ["튜브", " tube "], ["번들", " bunddle "], ["피팅", " fitting "], ["플러그", " plug "],
			["핀튜브", " pin tube "], ["럽쳐디스크", " rupture disc "], ["라인드체크", " lined check "],
			["라인드", " lined "], ["플랜지", " flange "], ["케이블", " cable "], ["보일러", " boiler "],
			["전기히터", " electric heater "], ["호스가스켓", " hose gasket "],
			["반응기", " reactor "], ["쿨링타워", " cooling tower "], ["스페어", " spare "], ["모니터링", " monitoring "],
			["필터", " filter "], ["온도", " temperature "], ["진공", " vaccum "],
			["모터", " motor "], ["유량계", " floemeter "], ["탱크", " tank "], ["변압기", " tranformer "],
			["로딩암", " loading arm "], ["교반기", " mixer "],
			["판넬", " panel "], ["배관", " piping "], ["오리피스", " orificr "], ["열교환기", " heat exchanger "],
			["펌프", " pump "], ["호스", " hose "], ["가스켓", " gasket "],
			["배터리", " battery "], ["터보블로어", " turbo blower "], ["패키지", " package "], ["버너", " bunner "],
			["오링", " oring "],
			["인버터", " inverter "], ["전동valve", " control valve "], ["호퍼", " hopper "], ["토너", " tonner "],
			["분석기", " anayzer "],
			["저울", " scale "], ["컨트롤", " control "], ["글로브", " glove "], ["컨트롤벨브", " control valve "],
			["컨트롤밸브", " control valve "],
			["아지테이터", " agitator "], ["송풍기", " blower "], ["블로어", " blower "], ["볼 valve", " ball valve "],
			["fitting류", " fitting "],
			["원심", " centrifugal "],
			["컴프레샤", " compressor "], ["컴프레셔", " compressor "], ["압축기", " compressor "], ["호이스트", " hoist "],
			["메카니카씰", " mechanical seal "],
			["메카니칼", " mechanical "], ["메카니컬", " mechanical "], ["밸브", " valve "], ["벨브", " valve "],
			["그라파이트", " graphite "],
			["언로딩시스템", " unloading system "], ["플레어스택", " flare stack "], ["센서", " sensor "], ["발전기", " generator "],
			["액츄에이터", " actuator "],
			["온오프", " on-off "], ["질량", " mass "], ["마그네틱", " magnetic "], ["임펠러", " impellar "],
			["컨테이너", " container "],
			["전기", " electric "], ["스크러버", " scrubber "], ["무정전저원장치", " ups "], ["mech-seal", " mechanical seal "],
			["메커미널 씰", " mechanical seal "],
			["차저", " changer "], ["s/parts", " spare parts "], ["spare 파트", " spare parts "], ]
		return result

	def l2d_table_style_01(self):
		result  = [
			["입사일", '퇴사일', '근무년월일수', '근무년수', '정답'],
			["2000-2-10", "2010-1-31", "10년0월0일", '10년', 10.0],
			["2000-2-11", "2001-1-31", '1년0월0일', '1년', 1.0],
			["2000-2-13", "2030-1-31", '30년0월0일', '30년', 30.0],
			["2000-2-21", "2009-1-31", '9년0월0일', '9년', 9.0],
			["2000-3-1", "2008-1-31", '8년0월0일', '8년', 8.0],
			["2000-2-10", "2007-1-31", '7년0월0일', '7년', 7.0],
			["2000-2-18", "2006-2-1", '6년0월1일', '7년', 7.0]
		]
		return result

	def l2d_macine_name_with_none_01(self):
		result = [
			['fitting', 'ball', 'flowmeter', 'on-off', 'battery', 'flange', 'electric', 'cable', 'gasket', 'seal', ],
			['invertor', None, 'level', 'gauge', 'gas', 'meter', 'centrifugal', 'magnetic', 'psv', 'titanium', ],
			['pressure', 'motor', 'boiler', 'globe', 'gate', 'transformer', 'charger', 'blower', 'inverter', ],
			['', 'ph', 'ebd', 'mass', 'plug', 'diaphragm', 'dcs', 'detector', 'heater', 'hv', 'scale', ],
			['', 'ups', 'pg', 'reactor', '', 'vessel', 'butterfly', 'mechanical', 'element', ],
			['tube', 'bellows', 'mixer', '', 'hose', 'diaphgram', 'separator', 'mcc', 'plc', 'frp', ],
			['', 'rubber', 'ngr', 'bolt', '', 'rtd', 'bolt/nut', 'graphite', 'drum', 'relay', 'LV', ],
			[None, 'rotary', 'sensor', None, 'column', 'screen', 'manual', 'balance', 'bundle', ],
			['plastivc', 'acb', 'carbon', None, 'cell', 'strainer', 'type', 'cover', 'tg', 'membrane', 'prv', ],
			['ptfe', 'check', 'nickel', 'analyzer', 'oil', 'water', 'temperature', 'glove', 'channel', 'ring', ],
			['etfe', 'sheet', 'tms', 'scrubber', 'lift', 'oven', 'holder', 'container', 'cctv', 'vcb', 'condensor', ],
			['casting', 'metal', 'rupture', 'disc', 'gear', 'screw', 'leak', '3-way', 'canned', 'package', 'dryer', ],
			['feeder', '양극전극', 'bag', 'air', '농도계', 'pin', 'impeller', 'metering', 'kit', 'actuator', 'aircon', ],
			['column', 'compressor', 'concentration', 'condenser', 'conductivity', 'connector', 'contcnrator', ],
			['contol', 'control', 'control ball valve', 'control-valve', 'convection', 'conveyor', 'cooler', ],
			['cover', 'crusher', 'cryogel', 'cw', 'cyclone', 'cylinder', 'd/p']]
		return result

	def l2d_number_only_01(self):
		result = [[11, 12, 13, 14, 15, 16, 17, 18, 19],
				  [21, 22, 23, 24, 25, 26, 27, 28, 29],
				  [31, 32, 33, 34, 35, 36, 37, 38, 39],
				  [41, 42, 43, 44, 45, 46, 47, 48, 49],
				  [51, 52, 53, 54, 55, 56, 57, 58, 59],
				  [61, 62, 63, 64, 65, 66, 67, 68, 69],
				  [71, 72, 73, 74, 75, 76, 77, 78, 79],
				  [81, 82, 83, 84, 85, 86, 87, 88, 89],
				  [91, 92, 93, 94, 95, 96, 97, 98, 99]]
		return result

	def l2d_number_n_string_01(self):
		result = [[11, 12, 13, 14, 15, 16, 17, 18, 19],
				  [21, 22, 23, 24, 25, 26, 27, 28, 29],
				  [31, 32, 33, "abc", 35, 36, 37, 38, "zzz"],
				  [41, 42, 43, 44, 45, 46, 47, 48, ""],
				  [51, 52, 53, 54, 55, 56, 57, 58, 59],
				  [61, 62, 63, " ", " space ", 66, 67, 68, 69],
				  [71, 72, 73, 74, 275, 76, 77, 78, 79],
				  [81, 82, 83, 84, " space ", 88886, 87, 88, 89],
				  [91, 92, 93, 94, -23, 96, 97, 98, 99],
				  ["abc", "abc", 13, 14, 15, 16, 17, 18, 19],
				  ["abc", 22, 23, "abc", 25, 26, 27, 28, "zzz"],
				  [31, 32, 33, "abc", "abc", 36, 37, 38, "zzz"],
				  ["3/1", 42, 43, "3/1", "3/1", 46, 47, 48, ""],
				  [51, "가나다", "3/1", 54, 55, 56, 57, 58, 59],
				  [61, 61, 61, " ", " space ", 66, 67, 68, 69],
				  [71, 72, 73, 74, "space", 76, 77, 78, 79],
				  [81, 82, "가나다", 84, " space ", 88886, 87, 88, 89],
				  [91, 100, "가나다", 94, -23, 96, 97, 98, 99]]
		return result

	def l2d_table_style_02(self):
		result = [
			["", "y1","y2","y3","y4","y5","y6","y7""y8","y9"],
				  ["x1", 21, 22, 23, 24, 25, 26, 27, 28, 29],
				  ["x2", 31, 32, 33, 123, 35, 36, 37, 38, 254],
				  ["x3", 41, 42, 43, 44, 45, 46, 47, 48, 123],
				  ["x4", 51, 52, 53, 54, 55, 56, 57, 58, 59],
				  ["x5", 61, 62, 63, 55, 122, 66, 67, 68, 69],
				  ["x6", 71, 72, 73, 74, 275, 76, 77, 78, 79],
				  ["x7", 81, 82, 83, 84, 432, 886, 87, 88, 89],
				  ["x8", 91, 92, 93, 94, 23, 96, 97, 98, 99],
				  ["x9", 61, 61, 61, 323, 234, 66, 67, 68, 69],
				  ["x10", 71, 72, 73, 74, 534, 76, 77, 78, 79],
				  ["x11", 81, 82, 13, 84, 324, 888, 87, 88, 89],
				  ["x12", 91, 100, 132, 94, 23, 96, 97, 98, 99]]
		return result

	def l2d_special_char_01(self):
		result = [
					["1111", 2, 3, 4, 5, 6, 7, 8, 9],
					["_2", "", 3, 4,"", 6, "", 8, ""],
					["  3", 2,"", 4,"", 6, "", 8, ""],
					["1234", "가123", 3, 4,"나", 6, "", 8, ""],
					["??5", "가가345", 3, 4,"나", 6, "", 8, ""],
					["**6", "가가abc", 3, 4,"나", 6, "", 8, ""],
					["*7", "가가나나다", 3, 4,"나", 6, "", 8, ""],
					[" 8", "가가 가가멜", 3, 4,"나", 6, "", 8, ""],
					]
		return result

	def l2d_control_sheet_01(self):
		result = [['번호', '업체명', 'REQ_NO', '수량', '단위', 'payment', 'payment status', 'REVISION', ' AMOUNT ', 'LI_DATE', 'ITEM', 'CONDITION', '통화단위', '대분류'] ,
											['1001', '산본', 'Fz-F01', '1 ', 'SET', '100-45', '100', '0', '            24,159.38 ', '2010-01-31', 'FRP TANK', 'FOT', 'KWON', 'VESSEL'] ,
											['1002', '산본', 'LP-01', '1 ', 'LOT', '90-10-90', 'PAR', '0', '        3,581,118.00 ', '2010-05-10', 'ELECTRIC MATERIAL', 'FOT', 'KWON', 'PIPING'] ,
											['1003', '산본', 'LP-01', '1 ', 'LOT', '90-10-90', 'PAR', '0', '          397,902.00 ', '2010-05-10', 'ELECTRIC MATERIAL', 'FOT', 'KWON', 'PIPING'] ,
											['1004', '산본', 'LP-01', '1 ', 'LOT', '90-10-90', '100', '0', '        3,979,020.00 ', '2010-10-25', 'ELECTRIC MATERIAL', 'FOT', 'KWON', 'PIPING'] ,
											['1005', '산본', 'NNN-01', '3 ', 'SETS', '100-30', '100', '0', '            29,750.00 ', '2010-05-10', 'CONTROL VALVE', 'FOT', 'JPY', 'PIPING'] ,
											['1006', '산본', 'NNN-01', '3 ', 'SETS', '100-30-CASH', '100', '0', '            29,750.00 ', '2010-05-10', 'CONTROL VALVE', 'FOT', 'JPY', 'PIPING'] ,
											['1007', '대원', 'zS-O-01', '1 ', 'SET', '100-30-CASH', '100', '0', '          340,000.00 ', '2010-03-04', 'STACK', 'FOT', 'KWON', 'VESSEL'] ,
											['1008', '안양', 'DNN-001', '1 ', 'SET', '100-30-CASH', '100', '0', '             3,400.00 ', '2010-11-08', 'COLLECTOR LAMINAR', 'FOB', 'JPY', 'VESSEL'] ,
											['1009', '삼성', 'NNzL-001', '25 ', 'SETS', '100-30-CASH', 'PAR', '0', '          311,397.36 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1010', '삼성', 'NNzL-001', '25 ', 'SETS', '100-30-CASH', 'PAR', '0', '            94,664.62 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1011', '삼성', 'NNzL-001', '25 ', 'SETS', '100-30-CASH', 'PAR', '0', '            56,057.50 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1012', '삼성', 'NNzL-001', '25 ', 'SETS', '100-30-CASH', 'PAR', '0', '            45,118.00 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1013', '삼성', 'NNzL-001', '25 ', 'SETS', '100-30-CASH', '100', '0', '          451,180.00 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1014', '삼성', 'GNNL-05', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '          123,019.65 ', '2011-05-08', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1015', '삼성', 'GNNL-05', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '            54,460.35 ', '2011-05-08', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1016', '삼성', 'GNNL-05', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '            20,111.00 ', '2011-05-08', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1017', '삼성', 'GNNL-05', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '            19,720.00 ', '2011-05-08', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1018', '삼성', 'GNNL-05', '7 ', 'SETS', '100-30-CASH', '100', '0', '          197,200.00 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1019', '삼성', 'GNNL-05', '1 ', 'LOT', '100-30-CASH', '100', '0', '            25,075.00 ', '2011-05-08', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1020', '삼성', 'GNNL-05', '1 ', 'LOT', '100-30-CASH', '100', '0', '            21,250.00 ', '2011-09-27', 'ROTOR ASSEMBLY', 'FOT', 'KWON', 'PIPING'] ,
											['1021', '삼성', 'GNNL-05', '1 ', 'LOT', '100-30-CASH', '100', '0', '            15,261.75 ', '2011-04-16', 'ROTOR ASSEMBLY', 'FOT', 'KWON', 'PIPING'] ,
											['1022', '삼성', 'GNNL-04', '39 ', 'SETS', '100-30-CASH', 'PAR', '0', '          697,680.00 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1023', '삼성', 'GNNL-04', '39 ', 'SETS', '100-30-CASH', 'PAR', '0', '            77,520.00 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1024', '삼성', 'GNNL-04', '39 ', 'SETS', '100-30-CASH', 'PAR', '0', '            76,245.00 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1025', '삼성', 'GNNL-04', '39 ', 'SETS', '100-30-CASH', '100', '0', '          775,200.00 ', '2010-02-21', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1026', '군포', 'FNN-L-01NN', '15 ', 'SET', '100-30-CASH', '100', '0', '        1,022,550.00 ', '2010-01-19', 'CS VESSELS', 'FOT', 'KWON', 'VESSEL'] ,
											['1027', '군포', 'ENNG02NNSP', '1 ', 'SET', '100-30-CASH', '100', '0', '            23,800.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1028', '군포', 'ENN-G-02NN', '15 ', 'SET', '100-30-CASH', '100', '0', '        2,295,000.00 ', '2010-01-19', 'SUS H/EX', 'FOT', 'KWON', 'VESSEL'] ,
											['1029', '강원도', 'ME-02', '1 ', 'LOT', '100-30-CASH', 'PAR', '0', '        1,304,112.43 ', '2010-07-14', 'TRANSFORMER', 'FOT', 'KWON', 'PIPING'] ,
											['1030', '강원도', 'ME-02', '1 ', 'LOT', '100-30-CASH', 'PAR', '0', '            68,637.50 ', '2010-07-14', 'TRANSFORMER', 'FOT', 'KWON', 'PIPING'] ,
											['1031', '강원도', 'ME-02', '1 ', 'LOT', '100-30-CASH', '100', '0', '        1,372,750.00 ', '2010-09-26', 'TRANSFORMER', 'FOT', 'KWON', 'PIPING'] ,
											['1032', '가을여행', 'ME-02', '1 ', 'LOT', '100-30-CASH', '100', '0', '        1,071,000.00 ', '2010-07-14', 'UPS', 'FOT', 'KWON', 'PIPING'] ,
											['1033', '가을여행', 'GNNL-03', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '        1,528,427.57 ', '2010-07-14', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1034', '가을여행', 'GNNL-03', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '          169,745.00 ', '2010-07-14', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1035', '가을여행', 'GNNL-03', '14 ', 'SETS', '100-30-CASH', 'PAR', '1', '             3,782.50 ', '2010-07-14', 'SPARE PARTS', 'FOT', 'KWON', 'PIPING'] ,
											['1036', '가을여행', 'GNNL-03', '3 ', 'SETS', '100-30-CASH', '100', '1', '        1,701,955.00 ', '2010-07-14', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1037', '가을여행', 'GNNL-02', '14 ', 'SETS', '100-30-CASH', 'PAR', '1', '          336,982.50 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1038', '가을여행', 'GNNL-02', '14 ', 'SETS', '100-30-CASH', 'PAR', '1', '            37,570.00 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1039', '가을여행', 'GNNL-02', '14 ', 'SETS', '100-30-CASH', 'PAR', '1', '            32,784.50 ', '2010-02-25', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1040', '가을여행', 'GNNL-02', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '            10,993.05 ', '2010-02-25', 'SPARE PARTS', 'FOT', 'KWON', 'PIPING'] ,
											['1041', '가을여행', 'GNNL-02', '14 ', 'SETS', '100-30-CASH', '100', '1', '          418,330.05 ', '2010-07-14', 'PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1042', '황해도', 'ENN-G-04', '4 ', 'SET', '100-30-CASH', '100', '0', '          263,500.00 ', '2010-02-25', 'DUSUPERHEATER', 'FOT', 'KWON', 'VESSEL'] ,
											['1043', '군포', 'JP-01', '3 ', 'SET', '100-30-CASH', '100', '0', '            89,250.00 ', '2010-02-25', 'STATIC MIXER', 'FOT', 'KWON', 'VESSEL'] ,
											['1044', '황해도', 'DL-L-01L', '1 ', 'SET', '100-30-CASH', '100', '0', '            25,500.00 ', '2010-02-15', 'STRAINER', 'FOB', 'JPY', 'VESSEL'] ,
											['1045', '황해도', 'DL-L-01z', '1 ', 'LOT', '100-30-CASH', '100', '0', '            25,500.00 ', '2010-02-15', 'Mixer', 'DDU', 'JPY', 'VESSEL'] ,
											['1046', '강원도', 'GLL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '0', '          410,184.50 ', '2011-06-15', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1047', '강원도', 'GLL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '0', '          117,130.00 ', '2011-06-15', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1048', '강원도', 'GLL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '0', '            58,590.50 ', '2011-06-15', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1049', '강원도', 'GLL-01', '12 ', 'SETS', '100-30-CASH', '100', '1', '          585,905.00 ', '2010-07-10', 'Flange', 'FOT', 'KWON', 'PIPING'] ,
											['1050', '강원도', 'NNO-02', '2 ', 'SETS', '100-30-CASH', '100', '0', '             1,530.00 ', '2011-06-15', 'REVISION INDUCER', 'FOB', 'USD', 'PIPING'] ,
											['1051', '강원도', 'NNO-02', '6 ', 'SETS', '100-30-CASH', '100', '1', '          151,130.00 ', '2010-07-26', 'PIPE', 'FOT', 'JPY', 'PIPING'] ,
											['1052', '강원도', 'NNO-02', '17 ', 'SETS', '100-30-CASH', '100', '1', '            47,043.25 ', '2010-07-26', 'PIPE', 'FOT', 'JPY', 'PIPING'] ,
											['1053', '강원도', 'NNzL-001', '2 ', 'SETS', '100-30-CASH', '100', '1', '            16,757.75 ', '2010-07-26', 'Forged Valve', 'FOT', 'JPY', 'PIPING'] ,
											['1054', '경상일보', 'NNO-02', '2 ', 'SETS', '100-30-CASH', '100', '2', '          101,295.35 ', '2010-07-24', 'Forged Valve', 'FOT', 'KWON', 'PIPING'] ,
											['1055', '경상일보', 'DD-11', '13 ', 'SETS', '100-30-CASH', '100', '2', '          136,135.15 ', '2010-07-24', 'Fitting', 'FOT', 'KWON', 'PIPING'] ,
											['1056', '경상일보', 'DNN-P01', '5 ', 'SET', '100-30-CASH', '100', '0', '          469,200.00 ', '2010-01-17', 'PACKING', 'FOB', 'JPY', 'VESSEL'] ,
											['1057', '제주도', 'GLL-01', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '        3,789,606.00 ', '2010-07-10', 'REFRIGERATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1058', '제주도', 'GLL-01', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '        1,541,594.00 ', '2010-07-10', 'REFRIGERATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1059', '제주도', 'GLL-01', '3 ', 'SETS', '100-30-CASH', 'PAR', '1', '        1,315,800.00 ', '2010-07-10', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1060', '제주도', 'GLL-01', '1 ', 'LOT', '100-30-CASH', 'PAR', '1', '          297,500.00 ', '2010-07-10', 'REFRIGERATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1061', '제주도', 'GLL-01', '3 ', 'SETS', '100-30-CASH', '100', '1', '        6,647,000.00 ', '2010-07-10', 'REFRIGERATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1062', '충청회사', 'GzL-04', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '          126,225.00 ', '2010-10-04', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1063', '충청회사', 'GzL-04', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '             9,775.00 ', '2010-10-04', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1064', '충청회사', 'GzL-04', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '             1,105.00 ', '2010-10-04', 'MMA', 'FOB', 'USD', 'PIPING'] ,
											['1065', '충청회사', 'GzL-04', '2 ', 'SETS', '100-30-CASH', '100', '1', '          137,105.00 ', '2010-07-10', 'Fitting', 'FOT', 'KWON', 'PIPING'] ,
											['1066', '엘지', 'LP-01', '1 ', 'LOT', '100-30-CASH', 'PAR', '0', '        6,740,840.00 ', '2010-01-13', 'MCC & SWGR', 'FOT', 'KWON', 'PIPING'] ,
											['1067', '엘지', 'LP-01', '1 ', 'LOT', '100-30-CASH', 'PAR', '0', '          842,605.00 ', '2010-01-13', 'MCC & SWGR', 'FOT', 'KWON', 'PIPING'] ,
											['1068', '엘지', 'LP-01', '1 ', 'LOT', '100-30-CASH', 'PAR', '0', '          842,605.00 ', '2010-01-13', 'MCC & SWGR', 'FOT', 'KWON', 'PIPING'] ,
											['1069', '엘지', 'LP-01', '1 ', 'LOT', '100-30-CASH', '100', '0', '        8,426,049.73 ', '2010-10-04', 'MCC & SWGR', 'FOT', 'KWON', 'PIPING'] ,
											['1070', '경상일보', 'ENN-S01', '27 ', 'SET', '100-30-CASH', '100', '0', '          299,691.71 ', '2010-01-13', 'SPIRAL H/E', 'FOB', 'JPY', 'VESSEL'] ,
											['1071', '전라회사', 'GzL-03', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '          442,000.00 ', '2010-07-10', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1072', '전라회사', 'GzL-03', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '          110,500.00 ', '2010-07-10', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1073', '전라회사', 'GzL-03', '7 ', 'SETS', '100-30-CASH', 'PAR', '0', '            71,094.00 ', '2010-07-10', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1074', '전라회사', 'GzL-03', '7 ', 'SETS', '100-30-CASH', '100', '1', '          559,215.00 ', '2010-07-10', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1075', '전라회사', 'GzL-01', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '          494,360.00 ', '2011-01-31', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1076', '전라회사', 'GzL-01', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '          123,590.00 ', '2011-01-31', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1077', '전라회사', 'GzL-01', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '            29,412.98 ', '2011-01-31', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1078', '전라회사', 'GzL-01', '2 ', 'SETS', '100-30-CASH', '100', '1', '          647,362.99 ', '2010-07-10', 'COMPRESSOR', 'FOT', 'KWON', 'PIPING'] ,
											['1079', '마음기업', 'EE-O-01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '             7,480.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1080', '마음기업', 'EE-O-01NN', '8 ', 'SET', '100-30-CASH', '100', '0', '          467,500.00 ', '2010-10-17', 'CONDENSER', 'FOT', 'KWON', 'VESSEL'] ,
											['1081', '마음기업', 'EE-O-01', '30 ', 'SET', '100-30-CASH', '100', '0', '          790,500.00 ', '2010-03-08', 'EJECTOR', 'FOT', 'KWON', 'VESSEL'] ,
											['1082', '배2', 'DNN-T01', '6 ', 'SET', '100-30-CASH', '100', '0', '          425,000.00 ', '2010-01-21', 'SIEVE TRAY', 'FOT', 'KWON', 'VESSEL'] ,
											['1083', '배2', 'DNN-P01NN', '8 ', 'SET', '100-30-CASH', '100', '0', '          663,000.00 ', '2010-02-09', 'TOWER INTERNAL', 'FOT', 'KWON', 'VESSEL'] ,
											['1084', '귤회사', 'DP-01', '7 ', 'SET', '100-30-CASH', '100', '0', '          174,250.00 ', '2010-01-31', 'SILENCER', 'FOT', 'KWON', 'VESSEL'] ,
											['1085', '귤회사', 'FD-O02SP', '1 ', 'SET', '100-30-CASH', '100', '0', '             2,465.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1086', '귤회사', 'FD-O02', '4 ', 'SET', '100-30-CASH', '100', '0', '          935,000.00 ', '2010-01-21', 'MIST SEPARATOR', 'FOT', 'KWON', 'VESSEL'] ,
											['1087', '마음기업', 'FNN-S01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '            36,975.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1088', '마음기업', 'FNN-S01', '35 ', 'SET', '100-30-CASH', '100', '0', '        2,465,000.00 ', '2010-01-28', 'SUS VESSELS', 'FOT', 'KWON', 'VESSEL'] ,
											['1089', '마음기업', 'ENN-L01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '            18,275.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1090', '마음기업', 'ENN-L01', '4 ', 'SET', '100-30-CASH', '100', '0', '        1,672,800.00 ', '2010-01-12', 'CS H/EX', 'FOT', 'KWON', 'VESSEL'] ,
											['1091', '여름회사', 'FD-O01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '          316,727.00 ', '2011-02-13', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1092', '여름회사', 'FD-O01', '8 ', 'SET', '100-30-CASH', '100', '0', '          578,000.00 ', '2010-01-20', 'FILTER', 'FOT', 'KWON', 'VESSEL'] ,
											['1093', '봄회사', 'FNN-L01zSP', '1 ', 'SET', '100-30-CASH', '100', '0', '            11,900.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1094', '봄회사', 'FNN-L01z', '1 ', 'SET', '100-30-CASH', '100', '0', '        1,572,500.00 ', '2010-01-12', 'CS PRESSURE VESSELS', 'FOT', 'KWON', 'VESSEL'] ,
											['1095', '봄회사', 'DNN-S01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '            41,650.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1096', '봄회사', 'DNN-S01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '             3,570.00 ', '2011-01-31', 'ANALYZER', 'FOT', 'KWON', 'VESSEL'] ,
											['1097', '봄회사', 'DNN-S01', '5 ', 'SET', '100-30-CASH', '100', '0', '        6,200,750.27 ', '2017-12-24', 'TOWER', 'FOT', 'KWON', 'VESSEL'] ,
											['1098', '최고당', 'ENN-P02', '45786 ', 'SET', '100-30-CASH', '100', '0', '          410,688.45 ', '2017-12-24', 'PLATE TYPE H/EX', 'FOB', 'JPY', 'VESSEL'] ,
											['1099', '최고당', 'NNN-01', '37 ', 'SETS', '100-30-CASH', '100', '0', '            14,875.00 ', '2010-05-10', 'CONTROL VALVE', 'FOB', 'JPY', 'PIPING'] ,
											['1100', '최고당', 'ENN-F01', '1 ', 'SET', '100-30-CASH', '100', '0', '          412,675.00 ', '2010-01-12', 'HEATER (FIN TUBE)', 'FOB', 'JPY', 'VESSEL'] ,
											['1101', '무한상사', 'DL-L-01', '3 ', 'SET', '100-30-CASH', '100', '0', '          654,500.00 ', '2010-03-24', 'REACTOR', 'FOT', 'KWON', 'VESSEL'] ,
											['1102', '여기물산', 'GzL-02', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '        1,032,750.00 ', '2010-02-08', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1103', '여기물산', 'GzL-02', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '          114,750.00 ', '2010-02-08', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1104', '여기물산', 'GzL-02', '2 ', 'SETS', '100-30-CASH', 'PAR', '0', '             1,836.00 ', '2010-02-08', 'MMA', 'FOB', 'USD', 'PIPING'] ,
											['1105', '여기물산', 'GzL-02', '2 ', 'SETS', '100-30-CASH', '100', '1', '        1,149,336.00 ', '2010-04-20', 'Battery Charge', 'FOT', 'KWON', 'PIPING'] ,
											['1106', '거기', 'EF-L01', '2 ', 'SET', '100-30-CASH', '100', '0', '        1,616,190.00 ', '2010-02-08', 'COOLING TOWER', 'FOT', 'KWON', 'VESSEL'] ,
											['1107', '갑회사', 'GDL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '1', '          319,149.50 ', '2010-10-20', 'AGITATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1108', '갑회사', 'GDL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '1', '          112,931.00 ', '2010-10-20', 'AGITATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1109', '갑회사', 'GDL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '1', '            35,419.50 ', '2010-10-20', 'AGITATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1110', '갑회사', 'GDL-01', '12 ', 'SETS', '100-30-CASH', 'PAR', '1', '             9,197.00 ', '2010-10-20', 'SPARE PARTS', 'FOT', 'KWON', 'PIPING'] ,
											['1111', '갑회사', 'GDL-01', '12 ', 'SETS', '100-30-CASH', '100', '1', '          476,697.00 ', '2010-04-20', 'AGITATOR', 'FOT', 'KWON', 'PIPING'] ,
											['1112', '사과', 'LP-01', '1 ', 'SET', '100-30-CASH', '100', '0', '             2,635.00 ', '2010-10-20', 'ANALYZER', 'FOT', 'JPY', 'PIPING'] ,
											['1113', '바나나기업', 'LP-02', '1 ', 'LOT', '100-30-CASH', '100', '0', '             3,570.00 ', '2011-02-09', 'PROGRAMMING', 'FOT', 'JPY', 'PIPING'] ,
											['1114', '홍길동', 'ME-02', '1 ', 'SET', '100-30-30', '100', '0', '            35,530.00 ', '2011-12-12', 'MODIFICATION Charge', 'SITE', 'KWON', 'VESSEL'] ,
											['1115', '홍길동', 'ENN-G02z', '3 ', 'SET', '100-30-CASH', '100', '0', '        3,740,000.00 ', '2010-01-12', 'SUS H/EX', 'FOT', 'KWON', 'VESSEL'] ,
											['1116', '홍길동', 'ENN-G01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '          152,065.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1117', '홍길동', 'ENN-G01', '5 ', 'SET', '100-30-CASH', '100', '0', '        2,082,500.00 ', '2010-01-12', 'SUS H/EX', 'FOT', 'KWON', 'VESSEL'] ,
											['1118', '홍길동', 'DL-L-01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '               935.00 ', '2011-01-31', '1YSP', 'FOB', 'USD', 'VESSEL'] ,
											['1119', '무능일지', 'ME-10', '1 ', 'LOT', '100-30-CASH', '100', '0', '          361,165.00 ', '2011-01-05', 'MECHANICAL SEAL', 'FOT', 'KWON', 'PIPING'] ,
											['1120', '가나상사', 'JP-01', '1 ', 'LOT', '100-30-CASH', '100', '0', '          784,125.00 ', '2010-04-07', 'PLATFORM & LADDER', 'FOT', 'KWON', 'VESSEL'] ,
											['1121', '가나상사', 'JP-01', '1 ', 'LOT', '100-30-CASH', '100', '0', '            65,875.00 ', '2010-04-07', 'INTER CONN. PIPING', 'FOT', 'KWON', 'VESSEL'] ,
											['1122', '회상일보', 'zNN-O01SP', '1 ', 'SET', '100-30-CASH', '100', '0', '             3,740.00 ', '2011-01-31', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1123', '회상일보', 'zNN-001', '1 ', 'SET', '100-30-CASH', '100', '0', '          926,500.00 ', '2010-01-14', 'HOT OIL HEATER', 'FOT', 'KWON', 'VESSEL'] ,
											['1124', '회상일보', 'zNN-001', '1 ', 'LOT', '100-30-CASH', '100', '0', '            34,000.00 ', '2011-01-03', 'ADDITIONAL PRICE', 'FOT', 'KWON', 'VESSEL'] ,
											['1125', '아사히', 'FD-O03', '2 ', 'SET', '100-30-CASH', '100', '0', '          489,065.35 ', '2010-01-24', 'FILTER', 'FOB', 'JPY', 'VESSEL'] ,
											['1126', '아사히', 'FD-D03NN', '1 ', 'LOT', '100-30-CASH', '100', '0', '             4,320.39 ', '2010-11-27', 'SUPERVISION SERVICE', 'SITE', 'JPY', 'VESSEL'] ,
											['1127', '아산', 'ENN-G-03', '5 ', 'SET', '100-30-CASH', '100', '0', '            34,000.00 ', '2010-04-06', 'SAMPLING COOLER', 'FOT', 'KWON', 'VESSEL'] ,
											['1128', '가나다', 'DFL-01', '1 ', 'SET', '100-30-CASH', '100', '2', '        1,013,200.00 ', '2010-10-13', 'DRUM FILLING MACHINE', 'FOT', 'KWON', 'PIPING'] ,
											['1129', '쌍용', 'DD-11', '1 ', 'SET', '100-30-CASH', 'PAR', '1', '            15,725.00 ', '2011-03-05', 'Gas detector', 'FOT', 'KWON', 'PIPING'] ,
											['1130', '쌍용', 'DD-11', '1 ', 'SET', '100-30-CASH', 'PAR', '1', '             2,975.00 ', '2011-03-05', 'Gas detector', 'FOT', 'KWON', 'PIPING'] ,
											['1131', '쌍용', 'DD-11', '1 ', 'SET', '100-30-CASH', '100', '1', '            18,700.00 ', '2010-07-10', 'DP Transmitter', 'FOT', 'KWON', 'PIPING'] ,
											['1132', '현대', 'FNNL01NNSP', '1 ', 'SET', '100-30-CASH', '100', '0', '             1,923.55 ', '2011-03-05', '1YSP', 'FOT', 'KWON', 'VESSEL'] ,
											['1133', '이순신', 'ENN-L01NN', '4 ', 'SET', '100-30-CASH', '100', '0', '            11,050.00 ', '2010-06-16', 'SINENCER', 'FOT', 'JPY', 'VESSEL'] ,
											['1134', '영풍', 'GNNL-01', '22 ', 'SETS', '100-30-CASH', 'PAR', '0', '          942,446.00 ', '2010-05-04', 'CENTRIFUGAL PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1135', '영풍', 'GNNL-01', '22 ', 'SETS', '100-30-CASH', 'PAR', '0', '          203,439.00 ', '2010-05-04', 'CENTRIFUGAL PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1136', '영풍', 'GNNL-01', '22 ', 'SETS', '100-30-CASH', 'PAR', '0', '          124,032.00 ', '2010-05-04', 'CENTRIFUGAL PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1137', '영풍', 'GNNL-01', '22 ', 'SETS', '100-30-CASH', '100', '2', '        1,269,917.00 ', '2010-07-11', 'CENTRIFUGAL PUMP', 'FOT', 'KWON', 'PIPING'] ,
											['1138', '금융', 'JFL-01', '1 ', 'SET', '100-30-CASH', 'PAR', '0', '          321,767.50 ', '2010-01-31', 'Material Handling', 'FOT', 'KWON', 'PIPING'] ,
											['1139', '금융', 'JFL-01', '1 ', 'SET', '100-30-CASH', 'PAR', '0', '            35,700.00 ', '2010-01-31', 'MMA', 'FOT', 'KWON', 'PIPING'] ,
											['1140', '금융', 'JFL-01', '1 ', 'SET', '100-30-CASH', '100', '1', '          357,467.50 ', '2010-05-04', 'Material Handling', 'FOT', 'KWON', 'PIPING'] ,
											['1141', 'ABC', 'LP-702SP', '1 ', 'SET', '100-30-CASH', '100', '0', '               807.50 ', '2011-02-21', '1YSP', 'FOB', 'USD', 'VESSEL'] ,
											['1142', 'ABC', 'LP-001', '1 ', 'LOT', '100-30-CASH', '100', '0', '            39,950.00 ', '2010-07-05', 'CONTROL PANNEL', 'FOT', 'KWON', 'VESSEL'] ,
											['1143', '갑회사', 'ME-10', '61 ', 'PCS', '100-14-CASH', '100', '0', '          119,000.00 ', '2012-07-05', 'TUBE MATERIAL', 'FOT', 'KWON', 'VESSEL'] ,
											['1144', '갑회사', 'ME-10', '1 ', 'LOT', '60-40-30', '100', '0', '          297,500.00 ', '2012-07-16', 'BOILER REPLACEMENT INCLUDING BODY', 'FOT', 'KWON', 'VESSEL'] ,
											['1145', '갑회사', 'ME-10', '1 ', 'LOT', '60-40-30', 'PAR-60', '0', '          178,500.00 ', '2012-07-16', 'BOILER REPLACEMENT INCLUDING BODY', 'FOT', 'KWON', 'VESSEL'] ,
											['1146', '갑회사', 'ME-10', '1 ', 'LOT', '60-40-30', 'PAR-40', '0', '          119,000.00 ', '2012-07-16', 'BOILER REPLACEMENT INCLUDING BODY', 'FOT', 'KWON', 'VESSEL'] ]
		return result

	def t2d_nim_01(self):
		result = """한용운의 시, 님의 침묵

		님은 갔습니다. 아아, 사랑하는 나의 님은 갔습니다.  
		푸른 산빛을 깨치고 단풍나무 숲을 향하여 난 작은 길을 걸어서 차마 떨치고 갔습니다.  
		황금의 꽃같이 굳고 빛나던 옛 맹세는 차디찬 티끌이 되어서 한숨의 미풍에 날려 갔습니다.

		날카로운 첫키스의 추억은 나의 운명의 지침을 돌려 놓고 뒷걸음쳐서 사라졌습니다.  
		나는 향기로운 님의 말소리에 귀먹고, 꽃다운 님의 얼굴에 눈멀었습니다.  
		사랑도 사람의 일이라 만날 때에 미리 떠날 것을 염려하고 경계하지 아니한 것은 아니지만, 
		이별은 뜻밖의 일이 되고 놀란 가슴은 새로운 슬픔에 터집니다.

		기와 승의 표현상의 특징과 효과점층적 반복을 통해 상황의 절박감을 강조하였다.

		그러나 이별을 쓸데없는 눈물의 원천을 만들고 마는 것은 스스로 사랑을 깨치는 것인 줄 아는 까닭에 
		걷잡을 수 없는 슬픔의 힘을 옮겨서 새 희망의 정수박이에 들어부었습니다.  
		우리는 만날 때에 떠날 것을 염려하는 것과 같이 떠날 때에 다시 만날 것을 믿습니다.

		아아, 님은 갔지마는 나는 님을 보내지 아니하였습니다.  
		제 곡조를 못 이기는 사랑의 노래는 님의 침묵을 휩싸고 돕니다"""
		return result

	def t2d_123가나다_01(self):
		result = """1: 1234567890가나다라마바사아자차카파파하
		2: 1234567890가나다라마바사아자차카파파하
		3: 1234567890가나다라마바사아자차카파파하
		4: 1234567890가나다라마바사아자차카파파하
		5: 1234567890가나다라마바사아자차카파파하
		6: 1234567890가나다라마바사아자차카파파하
		7: 1234567890가나다라마바사아자차카파파하
		8: 1234567890가나다라마바사아자차카파파하
		9: 1234567890가나다라마바사아자차카파파하
		"""
		return result

	def t2d_paint_for_max_01(self):
		result = """
#선택한 영역의 가로줄에서 가장 큰값에 색칠하는 것

xyxy = excelx.read_address_for_selection()
excelx.paint_max_value_in_range_in_each_xline("", xyxy)
"""
		return result

	def t2d_paint_for_min_01(self):
		result = """
#선택한 영역의 가로줄에서 가장 큰값에 색칠하는 것

xyxy = excelx.read_address_for_selection()
excelx.paint_min_value_in_range_in_each_xline("", xyxy)
"""
		return result

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

class excel_sample:
	def __init__(self):
		self.sample = {}
		self.sample["최대값에 색칠하기(선택영역)"] = """
#선택한 영역의 가로줄에서 가장 큰값에 색칠하는 것

xyxy = excel.read_address_for_selection()
excel.paint_max_value_in_range_in_each_xline("", xyxy)
"""

		self.sample["최소값에 색칠하기(선택영역)"] = """
#선택한 영역의 가로줄에서 가장 큰값에 색칠하는 것

xyxy = excel.read_address_for_selection()
excel.paint_min_value_in_range_in_each_xline("", xyxy)
"""

