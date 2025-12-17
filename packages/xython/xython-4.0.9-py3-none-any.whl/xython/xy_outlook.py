# -*- coding: utf-8 -*-
import os, datetime  # 내장모듈
import win32com.client  # pywin32의 모듈
import pywintypes
import xy_util, xy_time, xy_re, xy_common  # xython 모듈

class xy_outlook:
	"""
	아웃룩프로그램을 쉽게 사용가능하도록 만든 모듈
	"""
	def __init__(self):
		self.varx = xy_common.xy_common().varx
		self.varx["default_inbox_folder"] = 10
		self.top_folder_obj = ""
		self.sub_folder_obj = ""
		self.mail_properties = [
			'Subject', 'SenderName', 'Recipients', 'ReceivedTime', 'Body',
			'Importance', 'Categories', 'Attachments', 'HTMLBody', 'SentOn',
			'ConversationTopic', 'Importance', 'Sensitivity', 'Size', ]  # ... 기타 원하는 속성 추가

		self.outlook_program = win32com.client.dynamic.Dispatch('Outlook.Application')
		self.outlook = self.outlook_program.GetNamespace("MAPI")

	def __history(self):
		"""
		2023-04-10 : 이름을 포함한, 많은 부분을 고침
	    default folder: outlook 에서 기본으로 설정되고 관리되는 기준의 폴더들
	    아웃룩의 메일은 item 과 folder 로 구성이 되어있다
	    2025-03-29 : 받은편지함을 띁하는 input_folder와 xython에서 사용하는 input_이라는 인수를위한 접두어가 혼돈이 일어나서
	    outlook에서는 inbox라는 기본용어로 사용함
        """
		pass


	def attach_files_in_mail(self, input_one_mail, file_full_list):
		"""
		메일에 첨부화일을 추가하는 것
		:param input_one_mail:
		:param file_full_list:
		:return:
		"""
		for one_file in file_full_list:
			input_one_mail.Attachments.Add(one_file)
		return input_one_mail

	def autoreply_for_mail(self, input_one_mail, input_text):
		"""
		자동응답 기능을 만드는 것

		:param input_one_mail:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(16)
		reply = input_one_mail.ReplyAll()
		reply.Body = input_text + reply.Body
		reply.Move(folder_obj)

	def change_mail_set_to_mail_list(self, input_mails):
		"""
		mail_set에는 두가지가 있다, 하나는 list형식의 자료와 다른하나는 maillitems형식이 있다

		:param input_mails:
		:return:
		"""
		if type(input_mails) == type([]):
			result = input_mails
		else:
			result = []
			# 맨먼저 GetFirst부터 해야 한다
			result.append(input_mails.GetFirst())
			for no in range(input_mails.count - 1):
				result.append(input_mails.GetNext())
		return result

	def check_folder_no(self, input_value):
		"""
		기본적으로 check_로 시작되는 함수이름은 무엇인가를 내부적으로 확인하는 기능을 위한 것이다

		폴더이름으로 번호를 갖고오는 것
		:param input_value:
		:return:
		"""
		if input_value in [6, "", "input", "received", "receive", "받은편지함", "받은 편지함", "받은"]:
			folder_no = 6
		elif input_value in [5, "send", "sent", "보낸편지함", "보낸"]:
			folder_no = 5
		elif input_value in [9, "promise", "예약", "임시", "보관함", "보관"]:
			folder_no = 9
		elif input_value in [3, "삭제", "삭제함", "delete", "보관함", "보관"]:
			folder_no = 3
		elif input_value in [16, "임시", "draft", "임시보관함", "temp"]:
			folder_no = 16
		else:
			folder_no = None
		return folder_no

	def check_folder_obj(self, input_value=""):
		"""
		폴더가 번호로 오는지 아니면 이름으로 입력값이 오는지에 따라서 폴더객체를 돌려준다
		:param input_value:
		:return:
		"""
		folder_obj = None

		# 숫자가 들어왔을때는 폴더의 숫자로 인식
		if input_value == "":
			folder_obj = self.outlook.GetDefaultFolder(6)  # 6 : 받은편지함
		elif type(input_value) == type(123):
			folder_obj = self.outlook.GetDefaultFolder(input_value)
		# 문자일때
		elif type(input_value) == type("abc"):
			folder_no = self.check_folder_no(input_value)
			folder_obj = self.outlook.GetDefaultFolder(folder_no)
		else:
			try:
				# 폴더자체가 들어왔을때
				if input_value.__class__.__name__ == 'CDispatch':  # MAPIFolder
					folder_obj = input_value
			except:
				folder_obj = input_value

		return folder_obj

	def check_sub_folder(self, input_sub_folder=""):
		"""
		sub_folder에 대한것을 선택하는것
		:param input_sub_folder:
		:return:
		"""
		if input_sub_folder == "":
			sub_folder_index = 0
			result = self.top_folder_obj.Folders[sub_folder_index]
		elif type(input_sub_folder) == type(123):
			sub_folder_index = input_sub_folder
			result = self.top_folder_obj.Folders[sub_folder_index]
		elif type(input_sub_folder) == type("abc"):
			if input_sub_folder in ["input", "default", "basic", "read"]:
				result = self.get_inbox_folder()
			elif input_sub_folder in ["write"]:
				result = self.get_promise_folder_obj()
			else:
				sub_folder_index = input_sub_folder
				for no in range(self.top_folder_obj.count):
					this_name = self.top_folder_obj[no].Name
					if input_sub_folder == this_name:
						sub_folder_index = no
						break
				result = self.top_folder_obj.Folders[sub_folder_index]
		else:
			sub_folder_index = 0
			result = self.top_folder_obj.Folders[sub_folder_index]
		self.sub_folder_obj = result
		return result

	def check_term(self, input_value):
		"""
		일반적으로 사용하는 용어들을 확인하는 것

		:param input_value:
		:return:
		"""
		input_value = input_value.lower()
		if input_value in ["send", "sender", "보낸사람"]:
			result = "SenderName"
		elif input_value in ["receivedtime", "받은시간", "임시", "보관함", "보관"]:
			result = "ReceivedTime"
		elif input_value in ["to"]:
			result = "To"
		elif input_value in ["제목", "subject", "title"]:
			result = "Subject"
		elif input_value in ["body", "본문", "내용"]:
			result = "Body"
		elif input_value in ["bcc", "숨은참조"]:
			result = "Bcc"
		elif input_value in ["cc", "참조"]:
			result = "CC"
		elif input_value in ["attachments", "attachment", "첨부"]:
			result = "Attachments"
		else:
			result = input_value
		return result

	def check_top_folder(self, input_folder=""):
		"""
		top_folder에 대한것을 선택하는것

		:param input_sub_folder:
		:return:
		"""

		if input_folder == "":
			# 기본자료는 input folder를 말한다
			result = self.outlook.Folders[0]
		elif type(input_folder) == type(123):
			top_folder_index = input_folder
			result = self.outlook.Folders[top_folder_index]
		elif type(input_folder) == type("abc"):
			if input_folder in ["default", "basic"]:
				result = self.get_inbox_folder()
			elif input_folder in ["write"]:
				result = self.get_promise_folder_obj()
			else:
				top_folder_index = input_folder
				for no in range(self.outlook.Folders.count):
					this_name = self.outlook.Folders[no].Name
					if input_folder == self.outlook.Folders[no].Name:
						top_folder_index = no
						break
				result = self.outlook.Folders[top_folder_index]
		else:
			top_folder_index = 0
			result = self.outlook.Folders[top_folder_index]
		self.top_folder_obj = result
		return result

	def count_mails_in_folder(self, input_folder_name):
		"""
		폴더이름안의 메일 갯수를 갖고온다

		:param input_folder_name:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder_name)
		result = folder_obj.Items.count
		return result

	def count_mails_in_inbox_folder(self):
		result = self.count_mails_in_folder(6)
		return result

	def count_unread_mails_in_folder(self, input_folder):
		"""
		폴더객체안의 읽지않은 메일 갯수 확인

		:param input_folder:
		:return:
		"""
		# input_folder = mail.box.Items.count
		folder_obj = self.check_folder_obj(input_folder)
		mail_set = folder_obj.Items.Restricts("[Unread] =True")
		result = mail_set.count
		return result

	def count_unread_mails_in_folder_by_folder_name_rev2(self, input_folder_name):
		"""
		 읽지않은 메일 갯수를 갖고온다

		:param input_folder_name:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder_name)
		mail_set = folder_obj.Items.Restricts("[Unread] =true")
		result = mail_set.count
		return result

	def count_unread_mails_in_folder_v2(self, folder_name):
		"""

		:param folder_name:
		:return:
		"""
		input_folder = self.outlook.Folders[folder_name].Folders.items.count
		result = input_folder.UnReadItemsCount
		return result

	def count_unread_mails_in_inbox_folder(self):
		"""
		아웃룩에서 읽지않은 메일객체들을 돌려준다

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		mail_set = folder_obj.Items.Restricts("[Unread] =true")
		result = mail_set.count
		return result

	def delete_attached_files_for_mail(self, input_mail):
		"""
		입력으로들어오는 1개의 메일의 첨부화일 모두를 삭제하는 것
		:param input_mail:
		:return:
		"""
		for attachment in input_mail.Attachments:
			attachment.Delete()
		return input_mail

	def delete_bcc_for_mail(self, input_mail):
		"""
		1개의 메일안의 모든 bcc를 삭제하는 것

		:param input_mail:
		:return:
		"""
		input_mail.BCC = None
		return input_mail

	def delete_body_for_mail(self, input_mail):
		"""
		1개의 메일안의 body를 삭제하는 것

		:param input_mail:
		:param replace_text:
		:return:
		"""
		input_mail.Body = ""
		return input_mail

	def delete_mails_for_mails(self, input_mails):
		"""
		입력으로 들어온 메일들을 삭제한다

		:param input_mails:
		:return:
		"""
		for one_mail in input_mails:
			one_mail.Delete()

	def delete_mails_in_folder_from_before_nth_days_ago(self, input_folder, days=60):
		"""
		오늘기준으로 어떤 날짜 이전의 메일은 삭제하는 것

		:param input_folder:
		:param days:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		today = datetime.datetime.now()
		cutoff_date = today - datetime.timedelta(days=days)

		folder_obj.Items.Sort("[ReceivedTime]", True)
		for one_mail in folder_obj.Items:
			received_time = one_mail.ReceivedTime
			if received_time < cutoff_date:
				one_mail.Delete()

	def delete_nth_mail_in_mails(self, input_mails, input_no):
		"""
		입력으로 들어온 메일들을 삭제한다

		:param input_mail:
		:return:
		"""
		one_mail = input_mails[input_no - 1]
		one_mail.Delete()

	def filter_mails_in_mails_by_body_with_xsql(self, input_mails, xsql):
		"""
		어떤 폴더안에 찾고자 하는 이름이 같은 메일을 찾는것

		:param input_mails:
		:param xsql:
		:return:
		"""
		rex = xy_re.xy_re()
		result = []
		# mails = input_folder.items
		# 만약 mail_set이 list인지 아닌지를 확인한다
		mail_l1d = self.change_mail_set_to_mail_list(input_mails)

		for index, one_mail in enumerate(mail_l1d):
			if rex.search_with_xsql(xsql, one_mail.Body):
				print(one_mail.Subject)
				result.append(one_mail)
		return result

	def get_10_latest_mails_in_inbox_folder(self):
		"""
		기본편지함에서 최신 10개의 메일 정보를 갖고오는 것

		:return:
		"""
		mail_list = self.get_nea_latest_mails_in_default_inbox_folder(10)
		return mail_list

	def get_all_property_for_mail(self, input_mail):
		"""
		한개의 메일에 대한 모든 정보를 돌려주는 것

		:param input_mail:
		:return:
		"""
		utilx = xy_util.xy_util()
		result = utilx.get_all_properties_for_obj(input_mail)
		return result

	def get_all_property_name_for_mail_obj(self):
		"""
		매일객체의 속성들
		:return:
		"""

		result = self.varx["all_properties_list"]
		return result

	def get_all_mails_in_folder(self, input_folder):
		"""

		:param input_folder:
		:param sort_by:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mail_objs = folder_obj.Items
		result = []
		for one_mail in mail_objs:
			result.append(one_mail)
		return result


	def get_all_sorted_mails_in_folder(self, input_folder, sort_by=""):
		"""

		:param input_folder:
		:param sort_by:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mails = folder_obj.Items
		gijun = self.check_term(sort_by)
		mails.Sort(gijun, True)

		#result = []
		#for one_mail in mails:
		#	result.append(one_mail)
		return mails



	def get_all_sub_folder_name_in_top_folder_name(self, folder_name):
		"""
		아웃룩에서 최상위 폴더이름을 넣으면, 그안의 하위폴더이름을 갖고오는 것

		:param folder_name:
		:return:
		"""
		result = []
		for no in range(self.outlook.Folders[folder_name].Folders.count):
			this_name = self.outlook.Folders[folder_name].Folders[no].name
			result.append([folder_name, no, this_name])
		return result

	def get_all_sub_folder_name_in_top_folder_name_v2(self, folder_name):
		"""
		입력폴더의 하위 폴더들의 이름을 갖고오는 것

		:param folder_name:
		:return:
		"""
		result = []
		for no in range(self.outlook.Folders[folder_name].Folders.count):
			this_name = self.outlook.Folders[folder_name].Folders[no].name
			result.append([folder_name, no, this_name])
		return result

	def get_all_subject_for_unread_mails_in_inbox_folder(self):
		"""
		받은 편치함의 자료를 읽어서 새로운것만 제목보여주기

		:return:
		"""
		mail_set = self.get_unread_mail_set_in_inbox_folder()
		item_data_list2d = self.get_information_for_mails(mail_set)
		return item_data_list2d

	def get_all_top_folder_names(self):
		"""
		가장 상위에있는 메일 폴더들의 이름

		:return:
		"""
		result = []
		for no in range(self.outlook.Folders.count):
			this_name = self.outlook.Folders[no].Name
			result.append([no, this_name])
		return result

	def get_attached_file_names_for_mail(self, input_mail):
		"""
		이메일 안에 들어있는 첨부화일의 이름들 알아보기

		:param input_mail:
		:return:
		"""
		result = []
		attachments = input_mail.Attachments
		num_attach = len([x for x in attachments])
		if num_attach > 0:
			for x in range(1, num_attach + 1):
				attachment = attachments.Item(x)
				result.append(attachment.FileName)
		return result

	def get_basic_data_for_mails_in_inbox_folder_as_l2d(self):
		"""
		입력함의 각 메일 객체의 정보를 1차원의 리스트로 만들고, 최종 모든 메일에 대해서
		2차원의 자료형태로 돌려주는 것

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		mail_objs = folder_obj.Items
		result = []
		for one_mail in mail_objs:
			result.append([one_mail.To, one_mail.Subject, one_mail.SenderName, one_mail.ReceivedTime])
		return result

	def get_basic_data_for_unread_mails_in_inbox_folder_as_l2d(self):
		"""
		입력함의 각 메일중 읽지않은 메일에 대해서 각객체의 정보를 1차원의 리스트로 만들고, 최종 모든 메일에 대해서
		2차원의 자료형태로 돌려주는 것

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		mail_objs = folder_obj.Items.Restrict("[Unread]=true")
		result = []
		for one_mail in mail_objs:
			result.append([one_mail.To, one_mail.Subject, one_mail.SenderName, one_mail.ReceivedTime])
		return result

	def get_draft_folder(self):
		"""
		임시보관함의 메일박스
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(16)
		return folder_obj

	def get_empty_mail(self):
		"""

		:return:
		"""
		l1d = self.get_all_property_name_for_mail_obj()
		mail_dic = {}
		for one in l1d:
			mail_dic[one] = None
		return mail_dic

	def get_flagged_mails_in_inbox_folder(self):
		"""
		받은편지함의 자료를 읽어서 새로운것만 제목보여주기

		:return:
		"""
		folder_obj = self.get_inbox_folder()

		result = self.get_mails_in_folder_from_today_to_nth_day_later(folder_obj, 1)
		return result

	def get_flagged_mails_in_mails(self, input_mails):
		"""
		플래그가 지정된 모든 이메일을 가져옵니다
		만약 색을 지정하고싶으면, FlagIcon의 값을 적용하면 됩니다

		:param input_mails:
		:return:
		"""

		result = []
		for one_mail in input_mails:
			if one_mail.FlagIcon != 0:
				result.append(one_mail)
		return result

	def get_folder_obj_by_any_input(self, input_value):
		"""
		어떤 값이와도 폴더객체를 돌려주는 것

		:param input_value:
		:return:
		"""
		result = self.check_folder_obj(input_value)
		return result

	def get_folder_obj_by_index(self, index_no=6):
		"""
		folder를 할지 folder_obj로 할지

		:param index_no:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(index_no)
		return folder_obj

	def get_folder_obj_by_top_n_sub_folder_index(self, top_folder_index=0, sub_folder_index=6):
		"""
		폴더의 이름으로 찾는것

		:param top_folder_index:
		:param sub_folder_index:
		:return:
		"""
		folder_obj = self.outlook.Folders[top_folder_index].Folders[sub_folder_index]
		return folder_obj

	def get_folder_obj_by_top_n_sub_folder_name(self, top_folder_name="", sub_folder_name=""):
		"""
		top 폴더와 서브폴더이름으로 폴더 객체를 갖고온다

		:param top_folder_name:
		:param sub_folder_name:
		:return:
		"""
		top_folder_index = self.get_top_folder_index_by_folder_name(top_folder_name)
		sub_folder_index = self.get_sub_folder_index_in_top_folder_name_n_sub_folder_name(top_folder_index, sub_folder_name)
		result = self.outlook.Folders[top_folder_index].Folders[sub_folder_index]
		return result

	def get_folders_information(self):
		"""
		모든 기본폴더에 대한 정보

		:return:
		"""
		result = []
		for no in range(0, 50):
			try:
				temp = self.outlook.GetDefaultFolder(no)
				result.append([no, temp.name])
			except:
				pass
		return result

	def get_information_for_default_folders(self):
		"""
		모든 기본폴더에 대한 정보

		:return:
		"""
		result = []
		for no in range(0, 50):
			try:
				temp = self.outlook.GetDefaultFolder(no)
				result.append([no, temp.name])
			except:
				pass
		return result

	def get_information_for_mail(self, input_mail):
		"""
		한개의 메일에 대한 모든 정보를 돌려주는 것

		:param input_mail:
		:return:
		"""
		result_dic = {}
		for one in self.mail_properties:
			try:
				value = getattr(input_mail, one)
				result_dic[one] = value
			except:
				result_dic[one] = None
		return result_dic

	def get_information_for_mail_v1(self, input_mail):
		"""
		한개의 메일에 대한 모든 정보를 돌려주는 것

		:param input_mail:
		:return:
		"""
		utilx = xy_util.xy_util()
		abc = utilx.get_all_properties_for_obj(input_mail)
		print(abc)

		for one in abc:
			try:
				if one[0:2] != "__":
					value = getattr(input_mail, one)
					print("one 속성", one, " ==> ", value)
			except:
				pass

	def get_information_for_mail_v2(self, one_email):
		"""
		입력으로 들어오는 1개의 메일 객체에대한 모든 정보를 갖고오는 것

		:param one_email:
		:return:
		"""
		result = {}
		result["sender"] = one_email.SenderName
		result["receiver"] = one_email.To
		result["title"] = one_email.Subject
		result["time"] = one_email.ReceivedTime
		result["body"] = one_email.Body
		return result

	def get_information_for_mails(self, input_mails):
		"""
		메일 정보에 대한것을 갖고오는 것

		:param input_mails:
		:return:
		"""
		result = []
		for one_mail in input_mails:
			temp = self.get_information_for_mail(one_mail)
			result.append(temp)
		return result

	def get_information_for_mails_for_input_elements(self, input_mail_objs, element=["to", "subject", "sender", "body", "Cc", "bcc"]):
		"""

		:param input_mail_objs:
		:param element:
		:return:
		"""
		l1d = []
		for one in element:
			if one in ["to"]:
				l1d.append("To")
			elif one in ["subject"]:
				l1d.append("Subject")
			elif one in ["receive", "receivetime"]:
				l1d.append("ReceivedTime")
			elif one in ["sender"]:
				l1d.append("SenderName")
			elif one in ["attachment", "attach", "attachments"]:
				l1d.append("Attachments")
			elif one in ["bcc"]:
				l1d.append("BCC")
			elif one in ["body"]:
				l1d.append("Body")
		result = []
		for one_mail in input_mail_objs:
			temp_dic = {}
			for ele in l1d:
				exec(f"temp_dic.{ele}= one_mail.{ele}")
				result.append(temp_dic)
		return result

	def get_inbox_folder(self):
		"""
		기본 받은편지함 객체

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		return folder_obj

	def get_mail_by_entry_id(self, entry_id):
		"""
		EntryID 를 사용하여 메일 항목 가져오기

		:param entry_id:
		:return:
		"""
		mail_item = self.outlook.GetItemFromID(entry_id)
		return mail_item

	def get_mails_between_today_to_nth_day_before_in_folder(self, input_folder, input_no, sort_by=""):
		"""
		입력폴더에서 오늘을 기준으로 몇일전까지의 메일객체를 갖고오는 것

		:param input_folder:
		:param input_no:
		:param sort_by:
		:return:
		"""
		timex = xy_time.xy_time()
		dt_to = timex.get_dt_obj_for_ymd_list_as_23h_59m_59s()
		dt_from = timex.get_dt_obj_for_ymd_list_as_0h_0m_0s()
		dt_from = timex.shift_day_for_dt_obj(dt_from, -1 * int(input_no))
		mails = self.get_all_sorted_mails_in_folder(input_folder, sort_by)
		aaa = "[ReceivedTime] >= '" + dt_from.strftime("%Y-%m-%d %H:%M") + "' AND [ReceivedTime] < '" + dt_to.strftime("%Y-%m-%d %H:%M") + "'"
		result = mails.Restrict(aaa)
		return result

	def get_mails_in_folder(self, input_folder):
		"""
		입력폴더안의 모든 메일을 메일객체들로 돌려주는 것

		:param input_folder:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mail_set = list(folder_obj.Items)
		result = []
		for one_mail in mail_set:
			result.append(one_mail)
		return result

	def get_mails_in_folder_between_date1_and_date2(self, input_folder, start_date, end_date, sort_by=""):
		"""
		두날짜 사이의 메일 갖고오기

		:param input_folder:
		:param start_date:
		:param end_date:
		:param sort_by:
		:return:
		"""
		timex = xy_time.xy_time()
		dt_obj_from = timex.change_anytime_to_dt_obj(start_date)
		dt_obj_to = timex.change_anytime_to_dt_obj(end_date)
		dt_obj_to = dt_obj_to + datetime.timedelta(days=1)
		mails = self.get_all_sorted_mails_in_folder(input_folder, sort_by)
		aaa = "[ReceivedTime] >= '" + dt_obj_from.strftime(
			"%Y-%m-%d %H:%M") + "' AND [ReceivedTime] < '" + dt_obj_to.strftime("%Y-%m-%d %H:%M") + "'"
		result = mails.Restrict(aaa)
		return result

	def get_mails_in_folder_between_dt_obj1_and_dt_obj2(self, input_folder, dt_obj_from, dt_obj_to):
		"""

		:param input_folder:
		:param dt_obj_from:
		:param dt_obj_to:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		result = folder_obj.Items.Restrict("[ReceivedTime] >= '" + dt_obj_to.strftime(
			'%Y-%m-%d %H:%M') + "' AND [ReceivedTime] < '" + dt_obj_from.strftime('%Y-%m-%d %H:%M') + "'")
		return result

	def get_mails_in_folder_by_receive_date_as_yyyymmdd(self, input_folder="", input_yyyy_mm_dd=""):
		"""
		특정 날짜의 메일을 얻는 것
		"""
		timex = xy_time.xy_time()

		folder_obj = self.check_folder_obj(input_folder)
		dt_obj_to = timex.change_anytime_to_dt_obj(input_yyyy_mm_dd)
		dt_obj_to_1 = dt_obj_to + datetime.timedelta(days=1)
		result = folder_obj.Items.Restrict("[ReceivedTime] >= '" + dt_obj_to.strftime(
			'%Y-%m-%d %H:%M') + "' AND [ReceivedTime] < '" + dt_obj_to_1.strftime('%Y-%m-%d %H:%M') + "'")
		return result

	def get_mails_in_folder_for_today(self):
		"""
		받은편지함의 자료를 읽어서 새로운것만 제목보여주기

		:return:
		"""
		timex = xy_time.xy_time()
		folder_obj = self.get_inbox_folder()
		ymd_list = timex.get_ymd_list_for_today()
		dt_to = timex.get_dt_obj_for_ymd_list_as_23h_59m_59s(ymd_list)
		dt_from = timex.get_dt_obj_for_ymd_list_as_0h_0m_0s(ymd_list)
		result = folder_obj.Items.Restrict("[ReceivedTime] >= '" + dt_from.strftime('%Y-%m-%d %H:%M') + "' AND [ReceivedTime] < '" + dt_to.strftime('%Y-%m-%d %H:%M') + "'")
		return result

	def get_mails_in_folder_by_ymd_list(self, input_folder, input_ymd_list):
		"""
		특정한 날을 기준으로 그날짜의 메일만 갖고오는 것입니다

		:return:
		"""
		result = self.get_mails_in_folder_between_ymdlist1_and_ymdlist2(input_folder, input_ymd_list, input_ymd_list)
		return result


	def get_mails_in_folder_between_ymdlist1_and_ymdlist2(self, input_folder, ymdlist1, ymdlist2):
		"""
		특정폴더에서 기간사이의 메일을 갖고오기

		:return:
		"""
		timex = xy_time.xy_time()

		folder_obj = self.check_folder_obj(input_folder)
		dt_from = timex.get_dt_obj_for_ymd_list_as_0h_0m_0s(ymdlist1)
		dt_to = timex.get_dt_obj_for_ymd_list_as_23h_59m_59s(ymdlist2)
		result = folder_obj.Items.Restrict("[ReceivedTime] >= '" + dt_from.strftime('%Y-%m-%d %H:%M') + "' AND [ReceivedTime] < '" + dt_to.strftime('%Y-%m-%d %H:%M') + "'")
		return result

	def get_mails_in_folder_from_today_to_nth_day_later(self, input_folder, input_day_no):
		"""
		오늘을 기준으로 입력한 몇일전까지의 메일을 갖고오는것

		:param input_folder: 메일박스
		:param input_day_no: 몇일전까지일지 넣는 숫자
		:return:
		"""
		timex = xy_time.xy_time()

		folder_obj = self.check_folder_obj(input_folder)
		dt_obj_to = timex.get_dt_obj_for_today()
		# 끝날포포함하려면, 1 일을 더 더해줘야한다
		# 즉, 2023-1-1 일 0 시 0 분 0 초를 넣어주는것과 같으므로, 2023-01-02 일 0 시 0 분 0 초로 하면 1 월 1 일의 모든 자료가 다 확인되는 것이다
		dt_obj_from = dt_obj_to - datetime.timedelta(days=input_day_no)
		# 폴더객체안의 받은 날짜사이에 들어온 메세지만 갖고오는것
		mails = folder_obj.Items
		# 제일 최근에 받은것, 즉, 제일 받은시간이 늦은것을 기준으로 정렬
		mails.Sort("ReceivedTime", True)
		mail_set = mails.Restrict("[ReceivedTime] >=	'" + dt_obj_from.strftime('%Y-%m-%d %H:%M') + "'")

		result = []
		for one_mail in mail_set:
			result.append(one_mail)
		return result

	def filter_input_mails_by_option(self, input_mails, option_key, option_value):
		"""
		메일set에 대해서 원하는 부분이 들어있는 메일을 골라내는 것이다

		:param input_mails:
		:param option_key:
		:param option_value:
		:return:
		"""
		result = []
		for one_mail in input_mails:
			if str(option_key).lower() in ["to", "receiver"]:
				if option_value in one_mail.To:
					result.append(one_mail)
			elif str(option_key).lower() in ["subject"]:
				if option_value in one_mail.Subject:
					result.append(one_mail)
			elif str(option_key).lower() in ["receive", "receivetime"]:
				if option_value in one_mail.ReceivedTime:
					result.append(one_mail)
			elif str(option_key).lower() in ["sender"]:
				if option_value in one_mail.SenderEmailAddress:
					result.append(one_mail)
			elif str(option_key).lower() in ["attachment", "attach", "attachments"]:
				if option_value in one_mail.Attachments:
					result.append(one_mail)
			elif str(option_key).lower() in ["bcc"]:
				if option_value in one_mail.BCC:
					result.append(one_mail)
			elif str(option_key).lower() in ["body"]:
				if option_value in one_mail.Body:
					result.append(one_mail)

		return result


	def get_mails_in_folder_obj_by_sender_or_reciver(self, input_mail_folder_obj, sender_name, receiver):
		"""
		폴더객체안의 날짜기준으로 정렬됭ㄴ자료에서, 최근에 들어온 몇개의 메세지만 갖고오는것

		:param input_mail_folder_obj:
		:param from_no:
		:param to_no:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_mail_folder_obj)
		mail_set = folder_obj.Items
		if sender_name and receiver:
			result = mail_set.Restrict("[SenderName] = '" + sender_name + "' AND [To] = '" + receiver + "'")
		elif sender_name and not receiver:
			result = mail_set.Restrict("[SenderName] = '" + sender_name + "'")
		elif not sender_name and receiver:
			result = mail_set.Restrict("[To] = '" + receiver + "'")

		return result

	def get_mails_in_inbox_folder(self):
		"""
		입력함의 모든 메일을 메일객체들로 돌려주는 것

		:return:
		"""
		result = []
		folder_obj = self.outlook.GetDefaultFolder(6)
		for one_mail in folder_obj.Items:
			result.append(one_mail)
		return result

	def get_mail_obj_in_inbox_folder(self):
		"""
		기본 받은편지함 객체

		:return:
		"""
		result = self.outlook.GetDefaultFolder(6).Items
		return result

	def get_nea_latest_mails_for_folder(self, input_no=5):
		"""

		:param input_no:
		:return:
		"""
		result = []
		input_folder = self.outlook.GetDefaultFolder(6)
		messages = input_folder.Items
		messages.Sort("ReceivedTime", True)
		message = messages.GetFirst()

		for no in range(input_no):
			print(message.Subject)
			message = messages.GetNext()
			result.append(message)
		return result

	def get_nea_latest_mails_in_default_inbox_folder(self, input_no=10):
		"""
		받은편지함에서 최신 n개메일을 갖고오는것

		:param input_no:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		mail_set = folder_obj.Items

		mail_list = []
		mail_list.append(mail_set.GetFirst())
		for no in range(input_no - 1):
			mail_list.append(mail_set.GetNext())
		return mail_list

	def get_nea_latest_mails_in_folder(self, input_folder, input_no=10):
		"""

		:param input_folder:
		:param input_no:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mails = folder_obj.Items

		mails.Sort("ReceivedTime", True)
		result = list(mails)[:input_no]
		return result

	def get_nea_latest_mails_in_inbox_folder_rev2(self, input_no=10):
		"""
		기본 입력 폴더의 최근 갯수의 메일 자료를 갖고온다

		:param input_no:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)

		result = []
		mails = folder_obj.Items
		result.append(mails.GetFirst())
		for no in range(input_no - 1):
			result.append(mails.GetNext())
		return result

	def get_nea_mails_in_folder_obj(self, folder_obj, input_no=5):
		"""

		:param folder_obj:
		:param input_no:
		:return:
		"""
		result = []
		folder_obj = self.check_folder_obj(folder_obj)
		messages = folder_obj.Items
		messages.Sort("ReceivesTime", True)
		message = messages.GetFirst()

		for no in range(input_no):
			print(message.Subject)
			message = messages.GetNext()
			result.append(message)
		return result

	def get_nea_mails_in_folder_obj_sort_by_received_time(self, folder_obj, input_no=5):
		"""

		:param folder_obj:
		:param input_no:
		:return:
		"""
		result = []
		folder_obj = self.check_folder_obj(folder_obj)
		mail_set = folder_obj.Items
		mail_set.Sort("ReceivesTime", True)
		one_mail = mail_set.GetFirst()

		for no in range(input_no):
			one_mail = mail_set.GetNext()
			result.append(one_mail)
		return result

	def get_nea_mails_in_folder_sort_by_date(self, input_folder, to_no=25, from_no=0):
		"""
		폴더객체안의 날짜기준으로 정렬됭ㄴ자료에서, 최근에 들어온 몇개의 메세지만 갖고오는것

		:param input_folder:
		:param from_no:
		:param to_no:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mails = folder_obj.Items
		mails.Sort("ReceivedTime", True)
		result = list(mails)[from_no:to_no]
		return result

	def get_nea_mails_in_inbox_folder(self, input_no=5):
		"""

		:param input_no:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_no)
		result = self.get_nea_mails_in_folder_obj_sort_by_received_time(folder_obj, input_no)
		return result

	def get_nea_mails_information_in_folder(self, input_folder, limit_no=0):
		"""
		폴더 객체안의 모든 메세지에대한 정보를 리스트+사전 형태로 만든다

		:param input_folder:
		:param limit_no:
		:return:
		"""
		result = []
		folder_obj = self.check_folder_obj(input_folder)
		mails = folder_obj.Items
		mails.Sort("ReceivedTime", True)
		one_mail = mails.GetFirst()
		total_no = 1
		for no in range(folder_obj.Items.count):
			temp = self.get_information_for_mail(one_mail)
			one_mail = mails.GetNext()
			result.append(temp)
			if limit_no:
				if limit_no == total_no:
					break
			total_no = total_no + 1
		return result

	def get_nth_latest_mail_in_folder(self, input_folder, input_no, latest_ok=True):
		"""
		특정폴더안의 메일객체를 돌려주는 것

		:param input_folder:
		:param input_no:
		:param latest_ok:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		mail_set = folder_obj.Items
		if latest_ok:
			mail_set.Sort("ReceivedTime", True)
		result = list(mail_set)[input_no - 1]
		return result

	def get_nth_mails_in_folder(self, input_folder_no, index_no=6):
		"""

		:param index_no:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder_no)
		all_items = folder_obj.Items
		result = all_items[index_no - 1]
		return result

	def get_opened_mail(self, input_no=1):
		"""
		현재 열려진 메일중에서 n번째의 메일객체를 갖고오는 것

		:param input_no:
		:return:
		"""
		mail = self.outlook_program.ActiveExplorer().Selection.Item(input_no)
		return mail

	def get_promise_folder_obj(self):
		"""
		기본적인 보관함 폴더

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(9)
		return folder_obj

	def get_selected_mails(self):
		"""
		아웃록에서 어떤때를 보면, 선택한 자료를 확인할 필요가 있다
		이럴때 사용하기 힘든 것이다
		"""
		mail_s = self.outlook_program.ActiveExplorer().Selection
		# print(mail_s.Count)

		"""
		 Set myOlExp = Application.ActiveExplorer 
		 Set myOlSel = myOlExp.Selection 

		 For x = 1 To myOlSel.Count 
		   MsgTxt = MsgTxt & myOlSel.Item(x).SenderName & ";" 
		 Next x 

		"""
		return mail_s

	def get_sub_folder_index_in_top_folder_name_n_sub_folder_name(self, top_folder_name="", sub_folder_name=""):
		"""
		폴더이름으로 폴더 객체를 만들고 확인하는 것

		:param self:
		:param top_folder_name:
		:param sub_folder_name:
		:return:
		"""
		top_folder_index = self.get_top_folder_index_by_folder_name(top_folder_name)
		result = ""
		if type(sub_folder_name) == type(123):
			result = sub_folder_name
		else:
			sub_folder_data = self.get_all_sub_folder_name_in_top_folder_name(top_folder_index)
			for sub_1 in sub_folder_data:
				if sub_1[2] == sub_folder_name:
					result = sub_1[1]
					break
		return result

	def get_sub_folder_obj_by_top_n_sub_folder_name(self, top_folder_name="", sub_folder_name=""):
		"""
		top 폴더의 index 와 원하는 폴더 번호를 넣으면 폴더 객체를 돌려준다

		:param top_folder_name:
		:param sub_folder_name:
		:return:
		"""
		top_folder_index = self.get_top_folder_index_by_folder_name(top_folder_name)
		sub_folder_index = self.get_sub_folder_index_in_top_folder_name_n_sub_folder_name(top_folder_index, sub_folder_name)
		result = self.outlook.Folders[top_folder_index].Folders[sub_folder_index]
		return result

	def get_top_folder_index_by_folder_name(self, folder_name=""):
		"""
		폴더이름을 입력하면 index 를 돌려주는것

		:param folder_name:
		:return:
		"""
		result = folder_name
		if type(folder_name) != type(123):
			top_folder_data = self.get_all_top_folder_names()
			for top_1 in top_folder_data:
				if top_1[1] == folder_name:
					result = top_1[0]
					break
		return result

	def get_top_folder_obj_by_index(self, top_folder_index=0):
		"""
		top 폴더의 index 와
		원하는 폴더 번호를 넣으면 폴더 객체를 돌려준다

		:param top_folder_index:
		:return:
		"""
		result = self.outlook.Folders[top_folder_index]
		return result

	def get_unique_id_for_mails(self, input_mails):
		"""
		입력으로 들어오는 메일객체들에대한 고유번호를 돌려주는 것
		모든 메일은 만들어질때 고유한 메일 아이디가 생성된다

		:param input_mails:
		:return:
		"""
		result = []
		for one_mail in input_mails:
			result.append(one_mail.EntryID)
		return result

	def get_unread_mails_in_folder_by_folder_index(self, input_index):
		"""

		:param input_index:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_index)
		# folder_obj = self.outlook.GetDefaultFolder(input_index)
		result = folder_obj.Items.Restrict("[Unread]=True")
		return result

	def get_unread_mails_in_folder_rev2(self, input_folder):
		"""
		입력한 폴데객체의 읽지 않은 메일을 객체로 돌려준다

		:param input_folder:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		result = folder_obj.Items.Restrict("[Unread] =true")
		return result

	def get_unread_mail_set_in_inbox_folder(self):
		"""
		기본 입력함의 읽지않은 메일을 메일객체들로 갖고오는 것

		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(6)
		result = list(folder_obj.Items.Restrict("[Unread]=true"))
		return result

	def get_unread_mails_in_inbox_folder_as_list(self):
		"""
		입력함에서 읽지않은 메일객체들을 리스트에 넣어서 돌려주는 것

		:return:
		"""
		result = []
		folder_obj = self.outlook.GetDefaultFolder(6)
		for one_mail in folder_obj.Items.Restrict("[Unread]=True"):
			result.append(one_mail)
		return result

	def get_unread_mails_in_mails(self, input_mails):
		"""
		읽지않은 메일객체를 갖고온다

		:param input_mails:
		:return:
		"""
		result = input_mails.Restrict("[Unread] =true")
		return result

	def make_html_inline_text(self, input_text, bold, size, color):
		"""

		:param input_text:
		:param bold:
		:param size:
		:param color:
		:return:
		"""
		text_style = '<p style="'
		aaa = ";"
		if bold:
			if text_style != '<p style= "': aaa = ''
			text_style = text_style + aaa + "font-weight: bold;"
		if size:
			if text_style != '<p style= "': aaa = ''
			text_style = text_style + aaa + "font-size:" + str(size) + "px;"
		if color:
			if text_style != '<p style= "': aaa = ''
			text_style = text_style + aaa + "color: " + str(color) + ";"
		text_style = text_style + '">' + input_text + "</p>"
		result = text_style
		return result

	def make_n_send_by_input_dic(self, input_dic):
		"""

		:param input_dic:
		:return:
		"""
		new_mail = self.outlook.CreateItem(0)
		new_mail.To = input_dic["to"]
		new_mail.Subject = input_dic["subject"]
		new_mail.Body = input_dic["body"]
		# attachment = "첨부화일들"
		# new_mail.Attachments.Add(attachment)
		new_mail.Send()

	def make_table(self, style, title_list, data_list2d):
		"""

		:param style:
		:param title_list:
		:param data_list2d:
		:return:
		"""
		table_style_id = ""
		if style != "":
			table_style_id = " id=" + '"' + style + '"'

		table_html = "<table" + table_style_id + ">"
		for one in title_list:
			table_html = table_html + f"<th>{one}</th>"
		for l1d in data_list2d:
			table_html = table_html + "<tr>"
			for value in l1d:
				if value == None:
					value = ""
				if isinstance(value, pywintypes.TimeType):
					value = str(value)[:10]
				table_html = table_html + f"<td>{value}</td>"
			table_html = table_html + "</tr>"
		table_html = table_html + "</table>"
		return table_html

	def move_mail_to_draft_folder(self, input_one_mail):
		"""
		어떤 메일 객체 1개가 오면, 그것을 draft메일로 이동시키는 것
		어떤 메일을 reply하는 기능을 만들어봅니다

		:param input_one_mail:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(16)
		input_one_mail.Move(folder_obj)

	def move_mail_to_target_folder(self, input_mail, target_folder):
		"""
		메일 객체를 다른 폴더로 옮기는 것

		:param input_mail:
		:param target_folder:
		:return:
		"""
		folder_obj = self.check_folder_obj(target_folder)
		input_mail.Move(folder_obj)

	def move_mails_to_target_folder(self, input_mails, target_folder):
		"""
		메일 객체를 다른 폴더로 옮기는 것

		:param input_mails:
		:param target_folder:
		:return:
		"""
		folder_obj = self.check_folder_obj(target_folder)
		for one_mail in input_mails:
			one_mail.Move(folder_obj)

	def move_spam_mail_to_folder_by_bad_words(self, input_folder, input_word_list, move_to_folder):
		"""
		스팸메일로 판단되는 메일객체들을 폴더로 이동시키는 것입니다

		:param input_folder:
		:param input_word_list:
		:param move_to_folder:
		:return:
		"""
		result = []
		mails = self.get_mails_in_inbox_folder(input_folder)
		for one_mail in mails:
			for one_word in input_word_list:
				if one_word in one_mail.Subject:
					one_mail.Move(move_to_folder)

	def new_mail_as_empty(self):
		"""
		빈 메일객체를 하나 만든것

		:return:
		"""
		new_mail = self.outlook_program.CreateItem(0)
		new_mail.To = "to"
		new_mail.Subject = "subject"
		new_mail.Body = "body"
		return new_mail

	def new_mail_by_basic_data_at_draft_folder(self, to="", subject="", body="", cc=""):
		"""

		:param to:
		:param subject:
		:param body:
		:param cc:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultFolder(16)
		new_mail = self.outlook_program.CreateItem(0)

		if to: new_mail.To = to
		if subject: new_mail.Subject = subject
		if body: new_mail.HTMLbody = body
		if cc: new_mail.CC = cc
		new_mail.Move(folder_obj)

	def new_mail_by_dic_type(self, input_dic):
		"""
		사전형식으로 들어오는 자료를 기준으로 새로운 메일객체를 만드는 것

		:param input_dic:
		:return:
		"""
		new_mail = self.outlook_program.CreateItem(0)
		new_mail.To = input_dic["To"]
		new_mail.Subject = input_dic["Subject"]
		new_mail.Body = input_dic["Body"]
		if "Attachments" in input_dic.keys():
			attachment = input_dic["Attachments"]
			new_mail.Attachments.Add(attachment)
		return new_mail

	def new_mail_with_subject_body_attachment(self, to, subject="", body="", attachments=None):
		"""
		새로운 메일 보내기

		:param to: 수신인
		:param subject: 제목
		:param body: 내용
		:param attachments: 첨부물
		:return:
		"""
		new_mail = self.outlook_program.CreateItem(0)
		new_mail.To = to
		new_mail.Subject = subject
		new_mail.Body = body
		if attachments:
			for num in range(len(attachments)):
				new_mail.Attachments.Add(attachments[num])
		return new_mail

	def new_one_mail_by_basic_data_at_draft_folder(self, to="", subject="", body="", cc=""):
		"""
		기본폴더에서 기본값을 기준으로 새로운 메일을 만드는 것입니다

		:param to:
		:param subject:
		:param body:
		:param cc:
		:return:
		"""
		folder_obj = self.outlook.GetDefaultfolder(16)
		new_mail = self.outlook_program.CreateItem(0)
		if to: new_mail.To = to
		if subject: new_mail.Subject = subject
		if body: new_mail.HTMLbody = body
		if cc: new_mail.CC = cc
		new_mail.Move(folder_obj)

	def new_sub_folder(self, parent_folder, new_sub_folder_name):
		"""

		:param parent_folder:
		:param new_sub_folder_name:
		:return:
		"""
		parent_folder.Folders.Add(new_sub_folder_name)

	def print_basic_datas_for_mails(self, input_mails):
		"""

		:param input_mails:
		:return:
		"""
		timex = xy_time.xy_time()

		try:
			for one_mail in input_mails:
				temp = []
				temp.append(one_mail.SenderName)
				to_list = (one_mail.To).split(";")
				temp.append(str(to_list[0]) + " 외 " + str(len(to_list) - 1) + "명")
				temp.append(timex.change_dt_obj_to_formatted_text_time(one_mail.ReceivedTime))
				temp.append(one_mail.Subject)
				print(temp)
		except:
			one_mail = input_mails.GetFirst()
			for no in range(input_mails.count):
				temp = []
				temp.append(one_mail.SenderName)
				to_list = (one_mail.To).split(";")
				temp.append(str(to_list[0]) + " 외 " + str(len(to_list) - 1) + "명")
				temp.append(timex.change_dt_obj_to_formatted_text_time(one_mail.ReceivedTime))
				temp.append(one_mail.Subject)
				print(temp)
				one_mail = input_mails.GetNext()

	def print_basic_datas_for_mails_one_by_one(self, input_mails):
		"""
		입력으로 들어오는 메일객체들에대해서 각 메일에대한 몇가지 정보를 프린트해서 보여주는 것

		:param input_mails:
		:return:
		"""
		for one_mail in input_mails:
			print(one_mail.SenderName, one_mail.ReceivedTime, one_mail.Subject)

	def print_basic_datas_for_mails_with_easy_format(self, input_mails):
		"""

		:param input_mails:
		:return:
		"""
		timex = xy_time.xy_time()

		try:
			for one_mail in input_mails:
				temp = []
				temp.append(one_mail.SenderName)
				to_list = (one_mail.To).split(";")
				temp.append(str(to_list[0]) + " 외 " + str(len(to_list) - 1) + "명")
				temp.append(timex.change_dt_obj_to_formatted_text_time(one_mail.ReceivedTime))
				if len(one_mail.Subject) > 20:
					temp.append(one_mail.Subject[:17] + "...")
				else:
					temp.append(one_mail.Subject)
				print(temp)
		except:
			one_mail = input_mails.GetFirst()
			for no in range(input_mails.count):
				temp = []
				temp.append(one_mail.SenderName)
				to_list = (one_mail.To).split(";")
				temp.append(str(to_list[0]) + " 외 " + str(len(to_list) - 1) + "명")
				temp.append(timex.change_dt_obj_to_formatted_text_time(one_mail.ReceivedTime))
				if len(one_mail.Subject) > 20:
					temp.append(one_mail.Subject[:17] + "...")
				else:
					temp.append(one_mail.Subject)
				print(temp)
				one_mail = input_mails.GetNext()

	def reply_mail_and_save_to_draft_folder(self, one_mail, addtional_title="Re: ", addtional_body="", no_old_title=False, no_old_body=False):
		"""

		:param old_mail:
		:param addtional_title:
		:param addtional_body:
		:param no_old_title:
		:param no_old_body:
		:return:
		"""
		#one_mail = self.get_information_for_mail(old_mail)
		reply = one_mail.Reply()
		if no_old_title:
			one_mail.Subject = ""
		if no_old_body:
			reply.Body = ""
		reply.Subject = addtional_title + one_mail.Subject
		reply.Body = addtional_body + "\n\n" + reply.Body
		self.move_mail_to_draft_folder(reply)

	def replyall_mail_and_save_to_draft_folder(self, one_mail, addtional_title="Re: ", addtional_body="", no_old_title=False, no_old_body=False):
		"""

		:param old_mail:
		:param addtional_title:
		:param addtional_body:
		:param no_old_title:
		:param no_old_body:
		:return:
		"""
		#one_mail = self.get_information_for_mail(old_mail)
		reply = one_mail.ReplyAll()
		if no_old_title:
			one_mail.Subject = ""
		if no_old_body:
			reply.Body = ""
		reply.Subject = addtional_title + one_mail.Subject
		reply.Body = addtional_body + "\n\n" + reply.Body
		self.move_mail_to_draft_folder(reply)

	def save_attached_files_for_mail(self, input_mail, path="", surname=""):
		"""
		# 이메일 안에 들어있는 첨부화일을 다른 이름으로 저장하기
		# path : 저장할 경로，없으면 현재의 위치
		# surname : 기존이름앞에 붙이는 목적，없으면 그대로
		"""
		attachments = input_mail.Attachments
		num_attach = len([x for x in attachments])
		if num_attach > 0:
			for x in range(1, num_attach + 1):
				attachment = attachments.Item(x)
				old_name_changed = surname + attachment.FileName
				attachment.SaveAsFile(os.path.join(path, old_name_changed))

	def select_folder(self, input_folder):
		"""

		:param input_folder:
		:return:
		"""
		folder_obj = self.check_folder_obj(input_folder)
		folder_obj.Select()

	def select_text_for_mail_from_1_to_2(self, input_one_mail, start_no=0, end_no=20):
		"""

		:param input_one_mail:
		:param start_no:
		:param end_no:
		:return:
		"""
		aaa = input_one_mail.Getlnspector.WordEditor.Range(Start=start_no, End=end_no).Select()

	def send_mail(self, mail_obj):
		"""

		:param mail_obj:
		:return:
		"""
		mail_obj.Send()

	def send_mail_on_datetime(self, input_one_mail, dt_obj):
		"""
		지정된 시간에 메일 보내기
		2024년 1월 1일 오후 3시
		dt obj = datetime.datetime(2024, 1, 1, 15, 0, 0)

		:param input_one_mail:
		:param dt_obj:
		:return:
		"""
		input_one_mail.DeliveryTime = dt_obj
		input_one_mail.Save()
		input_one_mail.Send()

	def set_display_on(self, input_mail):
		"""

		:param input_mail:
		:return:
		"""
		input_mail.Display(True)

	def sort_mails_by_mail_property(self, mail_list, input_property):
		"""

		:param mail_list:
		:param input_property:
		:return:
		"""
		utilx = xy_util.xy_util()
		result = []
		new_mail_list = []
		for one_mail in mail_list:
			value = getattr(one_mail, input_property)
			new_mail_list.append([value, one_mail])

		sorted_l2d = utilx.sort_l2d_by_index(new_mail_list, 0)

		for l1d in sorted_l2d:
			result.append(l1d[1])
		return result

	def sort_mail_set_by_input_property(self, mail_set, input_property, desending=True):
		"""
		입력속성을 기준으로 정렬하는 것

		:param mail_set:
		:param input_property:
		:param desending:
		:return:
		"""
		result = mail_set.Sort(input_property, desending)
		return result

	def xyprint(self, input_value, limit_no=20):
		"""
		print할때 너무 많은 글자가 나오면 않되기 때문에 글자수를 줄여주면서 끝에 ~~을 넣어서 프린트해주는 기능이다

		:param input_value:
		:param limit_no:
		:return:
		"""
		if type(input_value) == type([]):
			result = []
			for one in input_value:
				if len(str(one)) > limit_no:
					result.append(str(one))[:limit_no] + str("~~")
		elif type(input_value) == type({}):
			result = {}
			for one in input_value.keys():
				if len(str(input_value[one])) > limit_no:
					result[one] = str(input_value[one])[:limit_no] + str("~~")
		elif type(input_value) == type("abc"):
			if len(input_value) > limit_no:
				result = input_value[:limit_no] + str("~~")
		else:
			result = input_value
		return result


