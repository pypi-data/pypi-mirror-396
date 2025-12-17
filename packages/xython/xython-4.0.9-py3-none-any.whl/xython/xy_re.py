# -*- coding: utf-8 -*-
import re #내장모듈

class xy_re:
    """
    정규표현식을 쉽게 사용이 가능하도록 만든 모듈
    
	파일이름 : xy_re
	코드안에서 사용할때의 이름 : xre
	객체로 만들었을때의 이름 : rex
	xsql : xy_re에서 사용하는 정규표현식
    
    """

    def __init__(self):
        self.varx = {}  # 패키지내에서 공통으로 사용되는 변수
        self.setup_is_on = False
        self.setup = {}

    def _change_xsql_to_resql(self, input_text=""):
        """
		기본저긴 xsql -> resql형식으로 만들어 주는것

		:param input_text: 입력되는 text문장
		:return:
		"""
        if self.setup_is_on:
            setup_text = self.setup_for_maxsearch_ignorecase_multiline_dotall()
            input_text = setup_text + input_text

        if self.setup:
            for one in self.setup.keys():
                if one == "ignorecase":
                    input_text = "(대소문자무시)" + input_text
                elif one == "multiline":
                    input_text = "(여러줄)" + input_text
                elif one == "dotall":
                    input_text = "(개행문자포함)" + input_text
                elif one == "min_search":
                    input_text = "(최소찾기)" + input_text
                elif one == "begin":
                    input_text = "[begin]" + input_text
                elif one == "end":
                    input_text = input_text + "[end]"

        resql = input_text.replace(" ", "")

        setup_list = [
            ["(대소문자무시)", "(?!)"],  # re.IGNORECASE 대소문자 무시
            ["(여러줄)", "(?m)"],  # re.MULITILINE 여러줄도 실행
            ["(개행문자포함)", "(?s)"],  # re.DOTALL 개행문자도 포함
        ]

        for one in setup_list:
            resql = resql.replace(one[0], one[1])

        basic_list = [
            ["[\[](\d+)[~](\d*)[\]]", "{\\1,\\2}"],  # [3~4] ==> {3,4}
            [":(\d+)[~](\d*)[\]]", "]{\\1,\\2}"],  # :3~4] ==> ]{3,4}

            ["\(back_ok(.*)\)", "(?=\\1)"],  # (뒤에있음(abc)) => (?=abc)
            ["\(back_no(.*)\)", "(?!\\1)"],  # (뒤에없음(abc)) => (?!abc)
            ["\(front_ok(.*)\)", "(?<=\\1)"],  # (앞에있음(abc)) => (?<=abc)
            ["\(front_no(.*)\)", "(?<!\\1)"],  # (앞에없음(abc)) => (?<!abc)

            ["\(뒤에있음(.*)\)", "(?=\\1)"],  # (뒤에있음(abc)) => (?=abc) ,2024-08-08 (:을 제거)
            ["\(뒤에없음(.*)\)", "(?!\\1)"],  # (뒤에없음(abc)) => (?!abc),2024-08-08 (:을 제거)
            ["\(앞에있음(.*)\)", "(?<=\\1)"],  # (앞에있음(abc)) => (?<=abc),2024-08-08 (:을 제거)
            ["\(앞에없음(.*)\)", "(?<!\\1)"],  # (앞에없음(abc)) => (?<!abc),2024-08-08 (:을 제거)

            ["([\[]?)[&]?영어대문자[&]?([\]]?)", "\\1A-Z\\2"],
            ["([\[]?)[&]?영어소문자[&]?([\]]?)", "\\1a-z\\2"],
            ["([\[]?)[&]?특수문자[&]?([\]]?)", "\\1~!@#\$%\^&\*\(\)_\+{}|:\"<>\?\`\-=\[\]\\;',\./\\2"],
            ["([\[]?)[&]?한글모음[&]?([\]]?)", "\\1ㅏ-ㅣ\\2"],  # [ㅏ-ㅣ]
            ["([\[]?)[&]?모든문자[&]?([\]]?)", "\\1\\\s\\\S\\2"], #약간 수정
            ["([\[]?)[&]?일본어[&]?([\]]?)", "\\1ぁ-ゔ|ァ-ヴー|々〆〤\\2"],
            ["([\[]?)[&]?한글[&]?([\]]?)", "\\1ㄱ-ㅎ|ㅏ-ㅣ|가-힣\\2"],
            ["([\[]?)[&]?숫자[&]?([\]]?)", "\\1\\\d\\2"],
            ["([\[]?)[&]?영어[&]?([\]]?)", "\\1a-zA-Z\\2"],
            ["([\[]?)[&]?한자[&]?([\]]?)", "\\1一-龥\\2"],
            ["([\[]?)[&]?문자[&]?([\]]?)", "\\1.\\2"],
            ["([\[]?)[&]?공백[&]?([\]]?)", "\\1\\\s\\2"],

            ["([\[]?)[&]?eng_big[&]?([\]]?)", "\\1A-Z\\2"],
            ["([\[]?)[&]?eng_sma[&]?([\]]?)", "\\1a-z\\2"],
            ["([\[]?)[&]?special[&]?([\]]?)", "\\1~!@#\$%\^&\*\(\)_\+{}|:\"<>\?\`\-=\[\]\\;',\./\\2"],
            ["([\[]?)[&]?moum[&]?([\]]?)", "\\1ㅏ-ㅣ\\2"],  # [ㅏ-ㅣ] 머음인데, 원래 mo인것을 바꿈
            ["([\[]?)[&]?all_char[&]?([\]]?)", "\\1.\n\\2"],
            ["([\[]?)[&]?jpn[&]?([\]]?)", "\\1ぁ-ゔ|ァ-ヴー|々〆〤\\2"],
            ["([\[]?)[&]?kor[&]?([\]]?)", "\\1ㄱ-ㅎ|ㅏ-ㅣ|가-힣\\2"],
            ["([\[]?)[&]?num[&]?([\]]?)", "\\1\\\d\\2"],
            ["([\[]?)[&]?eng[&]?([\]]?)", "\\1a-zA-Z\\2"],
            ["([\[]?)[&]?chi[&]?([\]]?)", "\\1一-龥\\2"],
            ["([\[]?)[&]?cha[&]?([\]]?)", "\\1.\\2"],
            ["([\[]?)[&]?space[&]?([\]]?)", "\\1\\\s\\2"],

            ["[\[]단어([(].*?[)])([\]]?)", "\\1"],
            ["[\(]이름<(.+?)>(.+?)[\)]", "?P<\\1>\\2"],  # [이름<abc>표현식]
        ]

        #[또는:가나다, 마바사, 자차카]
        #,를 |로 바꾸는것
        # "\[또는.*?\]"

        for one in basic_list:
            resql = re.sub(one[0], one[1], resql)
            resql = resql.replace(" ", "")


        or_sql  =r"[\[]?또는\((.*?)\)[\]]?"
        bbb = self.search_with_resql(or_sql, resql)
        bbb.reverse()
        if bbb:
            for aaa in bbb:
                changed_text = aaa[0].replace(",", "|")
                changed_text = changed_text.replace("또는", "")
                changed_text = changed_text.replace("[", "")
                changed_text = changed_text.replace("]", "")
                resql = self.replace_substring(resql, aaa[1], aaa[2], changed_text)

        simple_list = [
            ['[begin]', '^'],
            ['[처음]', '^'], ['[맨앞]', '^'], ['[시작]', '^'],
            ['[맨뒤]', '$'], ['[맨끝]', '$'], ['[끝]', '$'],
            ['[end]', '$'],
            ['[또는]', '|'], ['또는', '|'], ['or', '|'],
            ['not', '^'], ['[최소찾기]', '(최소찾기)'],
        ]

        for one in simple_list:
            resql = resql.replace(one[0], one[1])

        # 최대탐색을 할것인지 최소탐색을 할것인지 설정하는 것이다
        if "(최소찾기)" in resql:
            resql = resql.replace("{1,}", "+")
            resql = resql.replace("{0,}", "*")

            resql = resql.replace("+", "+?")
            resql = resql.replace("*", "*?")
            resql = resql.replace("(최소찾기)", "")

        # 이단계를 지워도 실행되는데는 문제 없으며, 실행 시키지 않았을때가 약간 더 읽기는 편하다
        high_list = [
            ['[^a-zA-Z0-9]', '\W'],
            ['[^0-9a-zA-Z]', '\W'],
            ['[a-zA-Z0-9]', '\w'],
            ['[0-9a-zA-Z]', '\w'],
            ['[^0-9]', '\D'],
            ['[0-9]', '\d'],
            ['{0,}', '*'],
            ['{1,}', '+'],
        ]

        for one in high_list:
            resql = resql.replace(one[0], one[1])

        # print ("result ==> ", result)

        if "[.]" in resql:
            resql = resql.replace("[.]", ".")
        self.setup_is_on = False
        return resql

    def replace_substring(self, original, start, end, replacement):
        if start == 0:
            new_string = replacement + original[end:]
        else:
            new_string = original[:start] + replacement + original[end:]
        return new_string

    def change_as_simple(self, input_xsql, input_text, changed_text=""):
        """
        삭제한것만 제외하고 결과만 돌려주는 것

        :param input_xsql:
        :param input_text:
        :param changed_text:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        result = re.sub(resql, changed_text, input_text)
        return result

    def change(self, input_xsql, input_text, changed_text=""):
        """
        삭제한것만 제외하고 결과만 돌려주는 것

        :param input_xsql:
        :param input_text:
        :param changed_text:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        result = re.sub(resql, changed_text, input_text)
        return result

    def change_with_l1d(self, input_xsql, l1d, changed_text=""):
        """
        여러자료를 한번에 전부 xsql에 해당되는 부분을 바꾸는 것

        :param input_xsql:
        :param l1d:
        :param changed_text:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        result = []
        for one_text in l1d:
            temp = re.sub(resql, changed_text, one_text)
            result.append(temp)
        return result

    def change_comma_for_commaed_number(self, input_text):
        """
		숫자중에서 콤마(,)가 있는 것 중에서 콤마(,)만 없애는것
		1,234,567 => 1234567

		:param input_text: 입력되는 text문장
		:return:
		"""
        re_com = re.compile("[0-9,]*\.?[0-9]*")
        new_text = re_com.sub("", input_text)
        return new_text

    def change_html_tag_to_resql(self, one_tag, option_tag_show=False):
        """
        htm태그안의 값을 갖고오는 것

        :param one_tag:
        :param option_tag_show:
        :return:
        """
        new_tag = ""
        for one in one_tag:
            new_tag = new_tag + "[" + str(one).upper() + str(one).lower() + "]"
        if option_tag_show:
            change_sql = "<" + new_tag + ">.*<\\/" + new_tag + ">"
        else:
            change_sql = "(?<=<" + new_tag + ">).*(?= <\\/" + new_tag + ">)"
        result = change_sql
        return result

    def change_xsql_to_resql (self, input_xsql):
        """
        input_xsql을 regex스타일로 바꾸는것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :return:
        """
        result = self._change_xsql_to_resql(input_xsql)
        return result

    def change_number_to_tel_style(self, input_value):
       """
       전화번호나 핸드폰 번호 스타일을 바꿔주는것
       전화번호를 21345678 =>02-134-5678 로 변경하는 것

       :param input_value:
       :return:
       """

       result = input_value
       value = str(int(input_value))
       if len(value) == 8 and value[0] == "2":
          # 22345678 => 02-234-5678
          result = "0" + value[0:1] + "-" + value[1:4] + "-" + value[4:]
       elif len(value) == 9:
          if value[0:2] == "2":
             # 223456789 => 02-2345-6789
             result = "0" + value[0:1] + "-" + value[1:5] + "-" + value[5:]
          elif value[0:2] == "11":
             # 113456789 => 011-345-6789
             result = "0" + value[0:2] + "-" + value[2:5] + "-" + value[5:]
          else:
             # 523456789 => 052-345-6789
             result = "0" + value[0:2] + "-" + value[2:5] + "-" + value[5:]
       elif len(value) == 10:
          # 5234567890 => 052-3456-7890
          # 1034567890 => 010-3456-7890
          result = "0" + value[0:2] + "-" + value[2:6] + "-" + value[6:]
       return result

    def check_or(self, input_text):
        """
        or의 개념으로 또는을 처리하는 코드
        
        input_text = "[또는:가나다, 마바사]"
        aaa = check_or(input_text)
        
        :param input_text: 입력되는 text문장
        :return: 
        """
        result = []
        resql = "\[또는:(.*?)\]"
        temp = self.search_with_resql(resql, input_text)

        if not temp:
            resql = "\[or:(.*?)\]"
            temp = self.search_with_resql(resql, input_text)

        if temp:
            find_text = temp[0][3][0]
            changed_text = "("
            for one in find_text.split(","):
                changed_text = changed_text + str(one).strip() + "|"

            changed_text = changed_text[:-1] + ")"

            result.append(temp[0][1])
            result.append(temp[0][2])
            result.append(changed_text)
        return result

    def concate_xyre_result(self, input_l2d, chain_word=": "):
        """
        finder에서 찾은 여러개의 자료를 하나의 텍스트로 만들어서 연결하는것

        :param input_l2d:
        :param chain_word:
        :return:
        """
        result =""
        if input_l2d:
            for l1d in input_l2d:
                result = result + l1d[0] +chain_word
            result = result[:-1*len(chain_word)]
        return result

    def data_for_example_set_001(self):
        """
        잘 사용하는 re코드들의 샘플을 보여주기 위한것
        data로 시작하는 것은 다른것에 사용을위한 자료라는 뜻이다
        """
        result = {
            "1개이상의 공백없애기": "[공백:2~10]",
            "괄호안의 글자만 추출": "([문자:1~20])",
            "숫자만 추출": "[공백:1~3][영어:1~10]-[숫자:1~10][영어:0~10][공백:1~5]",
            "핸드폰번호": "[시작][숫자:4~4]-[숫자:1~2]-[숫자:1~2][끝]",  # "^\d{4}-\d{1,2}-\d{1,2}$"]
            "복잡한 생년월일": "([0-9]{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[1,2][0-9]|3[0,1]))-[1-4][0-9]{6}",
            "이메일": "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$",
            "영어와 숫자만 추출": "실시간시세",
            "~~용으로 끝나는 단어": "실시간시세",
            "한글만": "[한글:1~20]",
            "abc중 c만 1번이상 반복되는것 찾기": "abc[1~]",
            "abc중 bc만 1번이상 반복되는것 찾기": "a(bc)[1~]",
            "a와 b와 c를 제외한 모든 문자와 매치": "[^abc]",
            "한글로 3~5개의 글자로 된것을 그룹명 짖기": "(?P<그룹명>[한글:3~5])",
            "a와 b사이의 모든문자 찾기": "a[문자:1~]b",
            "a또는b또는c": "a[또는]b[또는]c",
            "전방탐색 : .+(?=:) => :앞의 모든 문자": ".+(?=:)",
            "후방탐색 : (?<=\$)[0-9.]+ => $뒤의 숫자": "(?<=\$)[0-9.]+",
            "Html태그중 <H숫자>찾을문자<\H숫자>안의 글자": "<H(0-30])>.*?</H\\1>",
            "문장중 핸드폰번호 찾기": "0[1~1][숫자:2~2]-[0~1][숫자:3~4]-[0~1][숫자:4~4]",
            "2022-01-01형식의 날짜찾기": "[0-9]{4})-([0-9]{2})-([0-9]{2}",
            "이메일찾기": "[\w\.-]+@[\w\.-]+",
            "괄호안의 숫자 찾기": "([모든문자:0~])",
            "지역 전화번호 찾기": "0(2|31|32|33|41|42|43|44|51|52|53|54|55|61|62|63|64)\-{0,1}\d{3,4}\-{0,1}\d{4}",
            "주민등록번호": "[0-9]{2}0[1-9]|1[0-2]0[1-9]|[1,2][0-9]|3[0,1]-[1-4][0-9]{6}",
            "금액": "[숫자,][1~][원:0~1]",
            "중복된 단어 찾기": "\\b(\\w+)\\s+\\1\\b", }

        return result

    def data_for_special_char_set(self):
        """
        특수문자들을 돌려준다

        :return:
        """
        result = ".^$*+?{}[]\\|()"
        return result

    def delete_as_simple(self, input_xsql, input_text):
        """
        삭제한것만 제외하고 결과만 돌려주는 것

        :param input_xsql:
        :param input_text:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        print(resql)
        result = re.sub(resql, "", input_text)
        return result

    def delete(self, input_xsql, input_text):
        """
        삭제한것만 제외하고 결과만 돌려주는 것

        :param input_xsql:
        :param input_text:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        #result = self.search_with_resql(resql, input_text)
        result = re.sub(resql, "", input_text)
        return result

    def delete_templete(self, input_xsql, input_text):
        """
        삭제용 자료를 만들기위한 기본 자료로 만든 것입니다

        :param input_xsql:
        :param input_text:
        :return:
        """
        re_com = re.compile(input_xsql)
        if re_com.search(input_text) == None:
            new_text = input_text
        else:
            new_text = re_com.sub("", input_text)
        return new_text

    def delete_with_l1d(self, input_xsql, l1d):
        """
        여러자료를 한번에 전부 xsql에 해당되는 부분을 삭제하는것

        :param input_xsql:
        :param l1d:
        :return:
        """
        resql = self.change_xsql_to_resql(input_xsql)
        result = []
        for one_text in l1d:
            temp = re.sub(resql, "", one_text)
            result.append(temp)
        return result

    def delete_all_except_num_n_eng_n_underbar(self, input_text):
        """
        영문과 숫자와 공백을 제외하고 다 제거를 하는것

        :param input_text: 입력되는 text문장
        :return:
        """
        result = []
        for one_data in input_text:
            temp = ""
            for one in one_data:
                if str(one) in ' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
                    temp = temp + str(one)
            result.append(temp)
        return result

    def delete_all_explanation_in_python_code(self, input_text):
        """
		py화일의 설명문의 줄들을 제거하는 코드

        :param input_text: 입력되는 text문장
        :return:
		"""
        input_text = re.sub(re.compile(r"[\s]*#.*[\n]"), "\\n", input_text)
        input_text = re.sub(re.compile(r"[\s]*'''.*?'''", re.DOTALL | re.MULTILINE), "\n", input_text)
        input_text = re.sub(re.compile(r'[\s]*""".*?"""', re.DOTALL | re.MULTILINE), "\n", input_text)
        input_text = re.sub(re.compile(r'^[\s]*[\n]'), "", input_text)
        return input_text

    def delete_eng(self, input_text):
        """
        알파벳과 숫자만 삭제하는것

        :param input_text: 입력되는 text문장
        :return:
		"""
        xsql = "[A-Za-z]*"
        result = self.delete_templete(xsql, input_text)
        return result

    def delete_eng_n_num(self, input_text):
        """
        알파벳과 숫자만 삭제하는것

        :param input_text: 입력되는 text문장
        :return:
		"""
        xsql = "[A-Za-z0-9]*"
        result = self.delete_templete(xsql, input_text)
        return result

    def delete_except_special_char(self, input_text):
        """
		특수문자를 제외하고 다 지우는 것

        :param input_text: 입력되는 text문장
        :return:
		"""
        xsql = "[^\s!@#$%^*()\-_=+\\\|\[\]{};:'\",.<>\/?]*"
        result = self.delete_templete(xsql, input_text)
        return result

    def delete_from_0_to_start_of_searched_value(self, input_xsql, input_text, include_serarched_value=True):
        """
        찾는자료 앞의 모든 자료를 삭제하기
        옵션으로 찾은 자료를 포함할지 아닐지를 선택한다

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :param include_serarched_value:
        :return:
        """
        found_data = self.search_with_xsql(input_xsql, input_text)
        start_x= 0
        if found_data:
            if include_serarched_value:
                start_x = found_data[0][1]
            else:
                start_x = found_data[0][2]
        result = input_text[start_x:]
        return result

    def delete_from_end_of_searched_value_to_end_of_text(self, input_xsql, input_text, include_serarched_value=True):
        """
        찾는 자료뒤의 모든 자료를 삭제하기
        옵션으로 찾은 자료를 포함할지 아닐지를 선택한다

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :param include_serarched_value:
        :return:
        """
        found_data = self.search_with_xsql(input_xsql, input_text)
        start_x=0
        if found_data:
            if include_serarched_value:
                start_x = found_data[0][2]
            else:
                start_x = found_data[0][1]
        result = input_text[:start_x]
        return result

    def delete_kor_eng_num(self, input_text):
        """
        한글, 영어, 숫자만 지우는 것

        :param input_text: 입력되는 text문장
        :return:
		"""
        xsql = "[A-Za-z0-9ㄱ-ㅎㅏ-ㅣ가-힣]*"
        result = self.delete_templete(xsql, input_text)
        return result

    def delete_no_meaning_words(self, input_list, change_word_dic):
        """
        문장에서 자주 사용하는 삭제해도 되는 일반적인 것들을 삭제하는 기능이다

        :param input_list:
        :param change_word_dic:
        :return:
        """
        sql_1 = "[시작][숫자&특수문자:1~][끝]"  # 숫자만 있는 것을 삭제
        sql_2 = "[시작][숫자:1:5][영어&한글:1:1][끝]"  # 1223개 와 같은것 삭제
        sql_3 = "[시작][한글:1~][끝]"  #
        sql_4 = "[\(][문자:1~][\)]"  # 괄호안의 글자

        result = []
        for one in input_list:
            one = str(one).strip()
            if self.is_fullmatch_with_xsql(sql_3, one):
                if one in list(change_word_dic.keys()):
                    one = change_word_dic[one]

            if self.is_fullmatch_with_xsql(sql_4, one):
                one = self.delete_with_xsql(sql_4, one)

            if len(one) <= 1:
                one = ""
            elif self.is_fullmatch_with_xsql(sql_1, one):
                one = ""
            elif self.is_fullmatch_with_xsql(sql_2, one):
                one = ""

            if one != "":
                result.append(one)

            result_unique = list(set(result))
        return result_unique

    def delete_number_n_comma(self, input_text):
        """
		숫자중에서 콤마(,)를 포함해서 모두 삭제하는것
		2번으로 나누어서 처리를 한다
		- 숫자안의 콤마만 삭제 : 1,234,567 => 1234567
		- 숫자 삭제

        :param input_text: 입력되는 text문장
        :return:
        """
        re_com = re.compile("[0-9,]*\.?[0-9]*")
        new_text = re_com.sub("", input_text)
        result = re.sub(r'\d', '', new_text)
        return result

    def delete_over_2_empty_lines(self, input_text):
        """
        줄이 2줄이상 떨어진것을 2줄만 남기고 나머지는 삭제하는것
        여러줄의 빈줄을 삭제하는게 목적이다

        :param input_text: 입력되는 text문장
        :return:
        """
        input_text = re.sub(re.compile(r"([\s]*\\n){2,}"), "\\n", input_text)
        return input_text

    def delete_searched_value_by_xsql (self, input_xsql, input_text):
        """
        xsql로 찾은것을 삭제하는 코드
        
        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return: 
        """
        result = self.delete_with_xsql(input_xsql, input_text)
        return result

    def delete_special_char_for_input_text(self, input_text):
        """
        공백과 특수문자등을 제외하고 같으면 새로운 y열에 1을 넣는 함수
        리스트의 사이즈를 조정한다

        :param input_text: 입력되는 text문장
        :return:
		"""

        xsql = "[\s!@#$%^*()\-_=+\\\|\[\]{};:'\",.<>\/?]*"
        result = self.delete_templete(xsql, input_text)
        return result

    def delete_special_letter_for_input_list(self, input_list):
        """
        입력받은 텍스트로된 리스트의 자료를 전부 특수문자를 없앤후 돌려주는 것이다
        입력된 자료가 1차원 리스트인지 판단한다

        :param input_list:
        :return:
		"""
        result = []
        if type(input_list) == type([]) and type(input_list[0]) != type([]):
            for one in input_list:
                if one != "" or one != None:
                    temp = self.delete_special_char_for_input_text(one)
                    result.append(temp)
        return result

    def delete_with_xsql (self, input_xsql, input_text):
        """
        입력자료중 input_xsql에 맞는 형식을 삭제하는것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        re.sub(resql, "", input_text)
        result = self.search_with_xsql(resql, input_text)
        return result

    def get_first_match_position(self, input_xsql, input_text):
        """
        맨처음에 찾은 문자의 위치를 돌려주는 것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        resql = self.change_xsql_to_resql(input_xsql)
        pattern = re.compile(resql)
        match = pattern.search(input_text)
        result = match.start()
        return result

    def get_nth_matched_text_for_resql(self, input_resgl, text, n):
        """
        정규표현식을 컴파일합니다

        :param input_resgl:
        :param text:
        :param n:
        :return:
        """
        regex = re.compile(input_resgl)
        # finditer 를 사용하여 매칭 결과를 순회합니다.
        matches = regex.finditer(text)
        # n번째 매칭 결과를 찾습니다.
        for i, match in enumerate(matches, start=1):
            if i == n:
                return match.group()

    def get_nth_result_with_resql(self, input_resgl, input_no, input_text):
        """
        입력자료중에서 정규표현식과 맞는것중에서 n번째의 위치와 값을 돌료주는 것

        :param input_resgl:
        :param input_no:
        :param input_text: 입력되는 text문장
        :return:
        """
        re_com = re.compile(input_resgl)
        result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)
        final_result = []
        num = 0
        for index, one_iter in enumerate(result_finditer):
            if index + 1 == input_no:
                temp = []
                # 찾은 결과값과 시작과 끝의 번호를 넣는다
                temp.append(one_iter.group())
                temp.append(one_iter.start())
                temp.append(one_iter.end())

                # 그룹으로 된것을 넣는것이다
                temp_sub = []
                if len(one_iter.group()):
                    for one in one_iter.groups():
                        temp_sub.append(one)
                        temp.append(temp_sub)
                else:
                    temp.append(temp_sub)
                # 제일 첫번째 결과값에 match 랑 같은 결과인지 넣는것
                if num == 0: temp.append(result_match)
                final_result.append(temp)
                num += 1
        return final_result

    def is_fullmatch(self,input_xsql,input_text):
        """
        입력으로 들어온 텍스트 전체가 입력으로온 정규표현식과 전체가 다 맞는지 확인하는 것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.is_fullmatch_with_xsql(input_xsql,input_text)
        return result

    def is_fullmatch_with_xsql(self,input_xsql,input_text):
        """
        입력값이 정규표현식과 전체 입력값이 같을때 True를 돌려줌

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = False
        resql = self._change_xsql_to_resql(input_xsql)
        re_com = re.compile(resql)
        result_match = re_com.fullmatch(input_text)
        if result_match:
            result = True
        return result

    def is_handphone_num(self, input_text):
        """
		특수문자가들어가있는지

        :param input_text: 입력되는 text문장
        :return:
    	"""
        re_basic = "^(010|019|011)-\d{4}-\d{4}+$"
        result = False
        temp = re.match(re_basic, input_text)
        if temp : result = True
        return result

    def is_have_special_char(self, input_text):
        """
		특수문자가들어가있는지

        :param input_text: 입력되는 text문장
        :return:
		"""
        re_basic = "^[a-zA-Z0-9]+$"
        result = False
        temp = re.match(re_basic, input_text)
        if temp : result = True
        return result

    def is_korean_only(self, input_text):
        """
		모두 한글인지

        :param input_text: 입력되는 text문장
        :return:
		"""
        re_basic = "^[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+$"
        result = False
        temp = re.match(re_basic, input_text)
        if temp : result = True
        return result

    def is_match(self, input_xsql, input_text):
        """
        입력으로 들어온 text가 input_xsql에 맞는것이 있는가?

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.search_with_xsql(input_xsql, input_text)
        return result

    def is_match_all(self,input_xsql,input_text):
        """
        입력으로 들어온 전체text가 input_xsql에 전체가 맞을때

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.is_fullmatch_with_xsql(input_xsql,input_text)
        return result

    def is_match_with_xsql (self,input_xsql, input_text):
        """
        정규표현식의 결과물이 있을때 True를 돌려준다

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result= False
        resql = self._change_xsql_to_resql(input_xsql)
        re_com = re.compile(resql)

        result_match = re_com.match(input_text)
        if result_match:
            result = result_match
        return result

    def is_number_only(self, input_text):
        """
        소슷점까지는 포함한것이다

        :param input_text: 입력되는 text문장
        :return:
		"""
        result = False
        temp = re.match("^[0-9.]+$", input_text)
        if temp:
            result = True
        return result

    def match (self, input_xsql, input_text):
        """
        결과가 여러개 일때는 2차원의 결과가 나타난다
        [[찾은글자, 찾은글자의 처음 위치 번호, 끝위치 번호, [그룹1, 그룹2], .........]

        :param input_xsql: 찾을 구문
        :param input_text: 찾고자하는 문장
        :return:
        """

        resql = self._change_xsql_to_resql(input_xsql)
        re_com = re.compile(resql)
        result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)

        final_result = []
        num=0
        for one_iter in result_finditer:
            temp=[]
            #찾은 결과값과 시작과 끝의 번호를 넣는다
            temp.append(one_iter.group())
            temp.append(one_iter.start())
            temp.append(one_iter.end())

            #그룹으로 된것을 넣는것이다
            temp_sub = []
            if len(one_iter.group()):
                for one in one_iter.groups():
                    temp_sub.append(one)
                temp.append(temp_sub)
            else:
                temp.append(temp_sub)

            #제일 첫번째 결과값에 match랑 같은 결과인지 넣는것
            if num == 0: temp.append(result_match)
            final_result.append(temp)
            num+=1
        return final_result

    def match_for_l2d_by_xsql(self, input_xsql,input_l2d):
        """
        2차원리스트의 모든 값중에서 정규표현식과 일치하는 것만 돌려주는 것
        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_l2d:
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        result = []
        for ix, l1d in enumerate(input_l2d):
            temp_l1d = []
            for iy, value in enumerate(l1d):
                one_result = self.search_with_resql(resql, value)
                temp_l1d.append(one_result[0][0])
            result.append(temp_l1d)
        return result

    def replace_many_times_with_xsql(self, xsql_list, replace_word_list, input_text):
        """
        하나의 값을 여러 sql로 계속 값을 변경하는 것

        :param xsql_list:
        :param replace_word_list:
        :param input_text: 입력되는 text문장
        :return:
        """
        resql_list = []
        for one in xsql_list:
            resql_list.append(self.inder(one))
            for index, one_resql in enumerate(resql_list):
                input_text = re.sub(one_resql, replace_word_list[index], input_text, flags=re.MULTILINE)
        return input_text

    def replace_as_simple (self, input_xsql, replace_word, input_text):
        """
        바꾸기

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param replace_word:
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.replace_with_xsql(input_xsql, replace_word, input_text)
        return result[0][0]

    def replace (self, input_xsql, replace_word, input_text):
        """
        바꾸기

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param replace_word:
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.replace_with_xsql(input_xsql, replace_word, input_text)
        return result

    def replace_with_xsql (self, input_xsql, replace_word, input_text):
        """
        입력자료를 원하는 문자로 바꾸는것

        :param input_xsql: 정규표현식으로 만들어진 형태
        :param replace_word:
        :param input_text: 입력되는 text문장
        :return:
        """
        resql = self._change_xsql_to_resql(input_xsql)
        result = re.sub(resql, replace_word, input_text, flags=re.MULTILINE)
        return result

    def run_with_xsql(self, input_xsql, input_text):
        """
        일반적인 메소드이며, 결과를 돌려주는 것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """

        resql = self._change_xsql_to_resql(input_xsql)
        result = self.search_with_resql(resql, input_text)
        return result

    def run_with_resql (self, resql, input_text):
        """
        결과값을 얻는것이 여러조건들이 있어서 이것을 하나로 만듦
        [[결과값, 시작순서, 끝순서, [그룹1, 그룹2...], match한 객체].....]

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
		"""

        re_com = re.compile(resql)
        result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)

        final_result = []
        num=0
        for one_iter in result_finditer:
            temp=[]
            #찾은 결과값과 시작과 끝의 번호를 넣는다
            temp.append(one_iter.group())
            temp.append(one_iter.start())
            temp.append(one_iter.end())

            #그룹으로 된것을 넣는것이다
            temp_sub = []
            if len(one_iter.group()):
                for one in one_iter.groups():
                    temp_sub.append(one)
                temp.append(temp_sub)
            else:
                temp.append(temp_sub)

            #제일 첫번째 결과값에 match랑 같은 결과인지 넣는것
            if num == 0: temp.append(result_match)
            final_result.append(temp)
            num+=1
        return final_result

    def search_as_simple (self, input_xsql, input_text):
        """
        입력으로 들어온 정규표현시과 값중에 맞는것을 찾는 것
        결과값만 갖고오는 것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = []
        resql = self._change_xsql_to_resql(input_xsql)
        l2d = self.search_with_resql(resql, input_text) #[[결과값, 시작순서, 끝순서, [그룹1, 그룹2...], match한 객체].....]
        for l1d in l2d:
            result.append(l1d[0])
        return result

    def search (self, input_xsql, input_text):
        """
        입력으로 들어온 정규표현시과 값중에 맞는것을 찾는 것

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """
        result = self.search_with_xsql(input_xsql, input_text)
        return result

    def search_again_for_searched_result(self, result_l2d, input_xsql):
        """
        결과값으로 넘어온 자료를 다시 검색하해서 결과를 알려주는 것

        :param result_l2d:
        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :return:
        """
        result = []
        for l1d in result_l2d:
            start_no = l1d[1]
            temp_2d = self.search_with_xsql(input_xsql, l1d[0])
            if temp_2d:
                for l1d in temp_2d:
                    l1d[1] = l1d[1] + start_no
                    l1d[2] = l1d[2] + start_no
                    result.append(l1d)
        return result

    def search_all_by_xsql(self, input_xsql, input_text):
        """
        xsql로 찾은 모든것을 돌려주는 것
        
        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return: 
        """
        result = self.search_with_xsql(input_xsql, input_text)
        return result

    def search_all_by_resql (self, resql, input_text):
        """
        resql로 찾은 모든것을 돌려주는 것
        
        :param resql: 
        :param input_text: 입력되는 text문장
        :return: 
        """
        result = self.search_with_resql(resql, input_text)
        return result

    def search_between_bracket1_and_bracket2(self, input_text):
        """
        괄호안의 문자 갖고오기
        괄호 내부 내용만 추출 : '\(([^)]+)'
        앞 뒤 괄호까지 포함 : '\([^)]+\)'

        :param input_text: 입력되는 text문장
        :return:
        """

        resql = "(?<=\\()(.*?)(?=\\))"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_between_char1_and_char2(self, input_text, start_char, end_char):
        """
        첫글자와 마지막글자인 것을 찾아내는 것

        :param input_text: 입력되는 text문장
        :param start_char:
        :param end_char:
        :return:
        """
        start_found = 0
        end_found = 0
        temp = ""
        result = []
        ""
        temp_list = ["", 0]
        for index, one in enumerate(input_text):
            if one == start_char:
                start_found = 1
                temp_list[1] = index
            elif one == end_char:
                end_found = 1
            if start_found and not end_found:
                temp = temp + one
            elif start_found and end_found:
                temp_list[0] = temp + one
                result.append(temp_list)
                temp_list = ["", 0]
                temp = ""
                start_found = 0
                end_found = 0
        return result

    def search_between_text1_and_text2(self, input_data, text_a, text_b):
        """
        입력된 자료에서 두개문자사이의 글자를 갖고오는것

        :param input_data:
        :param text_a:
        :param text_b:
        :return:
        """
        replace_lists=[
            ["(","\("],
            [")", "\)"],
        ]
        origin_a = text_a
        origin_b = text_b

        for one_list in replace_lists:
            text_a = text_a.replace(one_list[0], one_list[1])
            text_b = text_b.replace(one_list[0], one_list[1])
        re_basic =text_a+"[^"+str(origin_b)+"]*"+text_b
        result = re.findall(re_basic, input_data)
        return result

    def search_between_word1_and_word2(self, input_text, word_a, word_b):
        """
        두 단어사이의 글자를 갖고오는 것

        :param word_a:
        :param word_b:
        :param input_text: 입력되는 text문장
        :return:
        """
        re_basic = "(?<=\\" + str(word_a) + ")(.*?)(?="+str(word_b) + ")"
        resql = self._change_xsql_to_resql(re_basic)
        result = self.search_with_xsql(resql, input_text)
        return result

    def search_by_resql_for_file(self, resql, file_name):
        """
		텍스트화일을 읽어서 re에 맞도록 한것을 리스트로 만드는 것이다
		함수인 def를 기준으로 저장을 하며, [[공백을없앤자료, 원래자료, 시작줄번호].....]

		:param resql: 정규표현식으로 만들어진 형태
		:param file_name:
		:return:
		"""
        re_com = re.compile(resql)
        f = open(file_name, 'r', encoding='UTF8')
        lines = f.readlines()
        num = 0
        temp = ""
        temp_original = ""
        result = []
        for one_line in lines:
            aaa = re.findall(re_com, str(one_line))
            original_line = one_line
            changed_line = one_line.replace(" ", "")
            changed_line = changed_line.replace("\n", "")

            if aaa:
                result.append([temp, temp_original, num])
                temp = changed_line
                temp_original = original_line
            else:
                temp = temp + changed_line
                temp_original = temp_original + one_line
        return result

    def search_for_capital_text(self, input_text):
        """
        모두 알파벳대문자를 찾아내는 것

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^[A-Z]+$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_dashed_date(self, input_text):
        """
        입력된값 전체가 -로 연결된 날짜의 자료를 찾아내는 것입니다

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^\d{4}-\d{1,2}-\d{1,2}$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_email_address(self, input_text):
        """
        입력된값 전체가 이메일주소 입력

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_eng(self, input_text):
        """
        입력된값 전체가 모두 영문인것을 찾아내는 것입니다

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^[a-zA-Z]+$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_handphone_num(self, input_text):
        """
        입력된값 전체가 핸드폰의 형식인것을 찾아내는것
        예: 010-1234-5678

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^(010|019|011)-\d{4}-\d{4}"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_ip_address(self, input_text):
        """
        IP주소를 찾아내는 것

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_korean(self, input_text):
        """
        한글인것만 찾아내는 것

        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "[ㄱ-ㅣ가-힣]"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_for_num(self, input_text):
        """
		단어중에 나와있는 숫자만 분리하는기능

        :param input_text: 입력되는 text문장
        :return:
		"""
        re_compile = re.compile(r"([0-9]+)")
        result = re_compile.findall(input_text)
        new_result = []
        for dim1_data in result:
            for dim2_data in dim1_data:
                new_result.append(dim2_data)
        return new_result

    def search_for_special_char(self, input_text):
        """
		특수문자가들어가있는지

		:param input_text: 입력되는 text문장
		:return:
		"""
        resql = "^[a-zA-Z0-9]"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_nth_result_with_resql(self, resql, input_no, input_text):
        """
        정규표현식으로 찾은 n개의 결과값을 갖고오는 것

        :param resql:
        :param input_no:
        :param input_text: 입력되는 text문장
        :return:
        """
        re_com = re.compile(resql)
        result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)
        final_result = []
        num = 0
        for index, one_iter in enumerate(result_finditer):
            if index + 1 == input_no:
                temp = []
                # 찾은 결과값과 시작과 끝의 번호를 넣는다
                temp.append(one_iter.group())
                temp.append(one_iter.start())
                temp.append(one_iter.end())

                # 그룹으로 된것을 넣는것이다
                temp_sub = []
                if len(one_iter.group()):
                    for one in one_iter.groups():
                        temp_sub.append(one)
                        temp.append(temp_sub)
                else:
                    temp.append(temp_sub)
                # 제일 첫번째 결과값에 match 랑 같은 결과인지 넣는것
                if num == 0: temp.append(result_match)
                final_result.append(temp)
                num += 1
        return final_result

    def search_num_between_len1_and_len2(self, len1, len2, input_text):
        """
		m,n개사이인 것만 추출

		:param len1:
		:param len2:
		:param input_text: 입력되는 text문장
		:return:
		"""
        resql = "^\d{" + str(len1) + "," + str(len2) + "}$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_num_from_begin(self, input_text):
        """
        맨앞에서부터 숫자를 검사하는 것
        :param input_text: 입력되는 text문장
        :return:
        """
        input_xsql = "[시작][숫자:1~]"
        searched_data = self.search_all_by_xsql(input_xsql, input_text)
        if searched_data:
            result = searched_data[0][0]
        else:
            result = False
        return result

    def search_text_between_len1_and_len2(self, m, n , input_text):
        """
        문자수제한 : m다 크고 n보다 작은 문자

        :param m:
        :param n:
        :param input_text: 입력되는 text문장
        :return:
		"""
        resql = "^.{" + str(m) + "," + str(n) + "}$"
        result = self.search_with_resql(resql, input_text)
        return result

    def search_with_xsql(self, input_xsql, input_text):
        """
        결과값을 얻는것이 여러조건들이 있어서 이것을 하나로 만듦
        [[결과값, 시작순서, 끝순서, [그룹1, 그룹2...], match한 객체].....]

        :param input_xsql: 정규표현식을 쉽게 만들도록 변경한 형태의 문장, 예: [한글:3~4]
        :param input_text: 입력되는 text문장
        :return:
        """

        resql = self._change_xsql_to_resql(input_xsql)
        result = self.search_with_resql(resql, input_text)
        return result

    def search_with_resql (self, resql, input_text):
        """
        결과값을 얻는 것이 여러조건들이 있어서 이것을 하나로 만듦
        [[결과값, 시작순서, 끝순서, [그룹1, 그룹2...], match한 객체].....]

        :param resql: 정규표현식으로 만들어진 형태
        :param input_text: 입력되는 text문장
        :return:
        """
        re_com = re.compile(resql)
        result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)

        final_result = []
        num=0
        for one_iter in result_finditer:
            temp=[]
            #찾은 결과값과 시작과 끝의 번호를 넣는다
            temp.append(one_iter.group())
            temp.append(one_iter.start())
            temp.append(one_iter.end())

            #그룹으로 된것을 넣는것이다
            temp_sub = []
            if len(one_iter.group()):
                for one in one_iter.groups():
                    temp_sub.append(one)
                temp.append(temp_sub)
            else:
                temp.append(temp_sub)

            #제일 첫번째 결과값에 match랑 같은 결과인지 넣는것
            if num == 0: temp.append(result_match)
            final_result.append(temp)
            num+=1
        return final_result

    def setup_for_maxsearch_ignorecase_multiline_dotall(self, min_search = False, ignorecase = False, multiline=False, dotall=False):
        """
        이렇게 설정부분을 아예 이름안에 넣어서 하면 더 편하지 않을까??
        글로쓰기 힘든부분을 설정으로 만드는것

        :param min_search:
        :param ignorecase:
        :param multiline:
        :param dotall:
        :return:
        """
        self.setup = {}

        self.setup["ignorecase"] = ignorecase
        self.setup["multiline"] = multiline
        self.setup["dotall"] = dotall
        self.setup["min_search"] = min_search

    def split_text_by_input_text(self, main_text, input_text):
        """
        첫번째로 찾은것을 기준으로 자료를 분리하는 것
        여러개를 찾을수있지만, 제일 처음것을 기준으로 분리한다
        결과 : [찾은 문자의 시작까지의 문자, 찾을 문자, 찾은 문자의 끝에서부터 문자 끝까지]
        
        :param main_text: 
        :param input_text: 입력되는 text문장
        :return: 
        """
        searched_data = self.search_all_by_xsql(input_text, main_text)
        if searched_data:
            start_idx = searched_data[0][1]
            end_idx = searched_data[0][2]
            result = [input_text[0:start_idx], input_text, input_text[end_idx:]]
        else:
            result = False

        return result

    def search_with_xsql_as_dic (self, input_xsql, input_text):
        resql = self._change_xsql_to_resql(input_xsql)
        re_com = re.compile(resql)
        #result_match = re_com.match(input_text)
        result_finditer = re_com.finditer(input_text)
        final_result = []
        for one_iter in result_finditer:
            temp= {}
            temp["found"] = one_iter.group()
            temp["no1"] = one_iter.start()
            temp["no2"] = one_iter.end()
            if temp["no1"] == 0:
                temp["remain"] = input_text[temp["no2"]:]
            else:
                temp["remain"] = input_text[:temp["no1"]] + input_text[temp["no2"]+1:]
            temp["original"] = input_text
            temp_sub = []
            if len(one_iter.group()):
                for one in one_iter.groups():
                    temp_sub.append(one)
                    temp["group"]= temp_sub
            final_result.append(temp)
        return final_result

    def search_with_l2d(self, input_l2d, input_xsql):
        result =[]
        print(len(input_l2d))
        for l1d in input_l2d:
            temp = self.search_with_xsql_as_dic(input_xsql, l1d[0])
            #print(lld[0], temp)
            result.append(temp)
        return result

    def search_with_l1d(self, input_lld, input_xsql):
        result = []
        for one_text in input_lld:
            temp = self.search_with_xsql(input_xsql, one_text)
            result.append(temp)
        return result

    def delete_with_resql(self, input_resql, input_text, nea_change=0):
        """
        xsql형식으로 넘어온 자료와 삭제한것만 제외하고 결과만 돌려주는 것


        :param input_resql:
        :param input_text:
        :param nea_change: 0이면 모든것을 다 바꾸며, 1처럼 정수이면 그만큼만 바꾸는 것이다
        :return:
        """
        result = re.sub(input_resql, "", input_text, count=nea_change)
        return result

    def change_with_resql(self, input_resql, original_text, changed_text, nea_change=0):
        """
        xsql형식으로 넘어온 자료와 변경하는 것


        :param input_resql:
        :param input_text:
        :param nea_change: 0이면 모든것을 다 바꾸며, 1처럼 정수이면 그만큼만 바꾸는 것이다
        :return:
        """
        result = re.sub(input_resql, changed_text, original_text, count=nea_change)
        return result


    def delete_with_xsql_result_only (self, input_xsql, input_text):
        resql = self.change_xsql_to_resql(input_xsql)
        result = re.sub(resql, "", input_text)
        return result