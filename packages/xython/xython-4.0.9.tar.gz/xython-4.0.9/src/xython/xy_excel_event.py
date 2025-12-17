# -*- coding: utf-8 -*-
import time  #내장모듈

import pythoncom #pywin32의 모듈
import win32com.client as win32 #pywin32의 모듈

class ApplicationEvents:
    def OnNewWorkbook(self, workbook_obj):
        """
        print("Application Event => OnNewWorkbook, 엑셀->새로운 워크북")

        :param workbook_obj:
        :return:
        """
        pass

    def OnSheetActivate(self, sheet_obj):
        """
        print("Application Event => OnSheetActivate, 엑셀->다른 시트로 이동")

        :param sheet_obj:
        :return:
        """
        pass

    def OnActivate(self, workbook_obj):
        """
        print("Application Event => OnActivate, 엑셀->실행")
        
        :param workbook_obj: 
        :return: 
        """
        pass

    def OnSheetBeforeDoubleClick(self, sheet_obj, range_obj, tf_cancel):
        """
        print("Application Event => OnSheetBeforeDoubleClick, 엑셀->더블클릭 전에")
        
        :param sheet_obj: 
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnSheetBeforeRightClick(self, sheet_obj, range_obj, tf_cancel):
        """
        
        :param sheet_obj: 
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass
        #print("Application Event => OnSheetBeforeRightClick, 엑셀->오른쪽 클릭전에")

    def OnSheetCalculate(self, sheet_obj):
        """
        #print("Application Event => OnSheetCalculate 엑셀->시트계산하고나서")
        
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnSheetChange(self, sheet_obj, range_obj):
        """
        #print("Application Event => OnSheetChange, 엑셀->시트->셀값변경")
        
        :param sheet_obj: 
        :param range_obj: 
        :return: 
        """
        
        pass

    def OnSheetDeactivate(self, sheet_obj):
        """
        #print("Application Event => OnSheetDeactivate,  엑셀->시트->비활성화")
        
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnSheetSelectionChange(self, sheet_obj, range_obj):
        """
        #print("Application Event => OnSheetSelectionChange, 엑셀->시트->선택영역변경")
        
        :param sheet_obj: 
        :param range_obj: 
        :return: 
        """
        pass

    def OnWindowActivate(self, workbook_obj, window_obj):
        """
        #print("Application Event => OnWindowActivate, 엑셀->실행")
        
        :param workbook_obj: 
        :param window_obj: 
        :return: 
        """
        pass

    def OnWindowDeactivate(self, workbook_obj, window_obj):
        """
        #print("Application Event => OnWindowDeactivate, 엑셀->종료")
        
        :param workbook_obj: 
        :param window_obj: 
        :return: 
        """
        pass

    def OnWindowResize(self, workbook_obj, window_obj):
        """
        #print("Application Event => OnWindowResize, 엑셀->크기변경")
        
        :param workbook_obj: 
        :param window_obj: 
        :return: 
        """
        pass

    def OnWorkbookActivate(self, workbook_obj):
        """
        #print("Application Event => OnWorkbookActivate, 엑셀->워크북->활성화")
        
        :param workbook_obj: 
        :return: 
        """
        pass

    def OnWorkbookBeforeClose(self, workbook_obj, tf_cancel):
        """
        #print("Application Event => OnWorkbookBeforeClose, 엑셀->워크북->비활성화")
        
        :param workbook_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnWorkbookBeforSave(self,  workbook_obj, tf_save_as, tf_cancel):
        """
        #print("Application Event => OnWorkbookBeforSave, 엑셀->워크북->저장되기전")
        
        :param workbook_obj: 
        :param tf_save_as: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnWorkbookDeactivate(self, workbook_obj):
        """
        #print("Application Event => OnWorkbookDeactivate, 엑셀->워크북->비활성화")
        
        :param workbook_obj: 
        :return: 
        """
        pass

    def OnWorkbookNewSheet(self, workbook_obj, sheet_obj):
        """
        #print("Application Event => OnWorkbookNewSheet, 엑셀->워크북->새로운시트")
        
        :param workbook_obj: 
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnWorkbookOpen(self, workbook_obj):
        """
        #print("Application Event => OnWorkbookOpen, 엑셀->워크북->열때")
        
        :param workbook_obj: 
        :return: 
        """
        pass

class WorkbookEvents:
    def OnActivate(self):
        """
        #print("Workbook Event => OnActivate, 워크북->활성화")
        
        :return: 
        """
        pass

    def OnBeforeClose(self, tf_cancel):
        """
        
        :param tf_cancel: 
        :return: 
        """
        pass
        #print("Workbook Event => OnBeforeClose, 워크북->꺼지기 전에 실행")

    def OnBeforSave(self, tf_save_as, tf_cancel):
        """
        #print("Workbook Event => OnBeforSave, 워크북->저장되기 전")
        
        :param tf_save_as: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnDeactivate(self):
        """
        #print("Workbook Event => OnDeactivate, 워크북->비활성화")
        
        :return: 
        """
        pass

    def OnNewSheet(self, sheet_obj):
        """
        #print("Workbook Event => OnNewSheet, 워크북->새로운시트 만들때")
        
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnOpen(self, sheet_obj, range_obj, tf_cancel):
        """
        #print("Workbook Event => OnOpen, 워크북->새로운 워크북 열때")
        
        :param sheet_obj: 
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnSheetActivate(self, sheet_obj, range_obj, tf_cancel):
        """
        #print("Workbook Event => OnSheetActivate, 워크북->시트활성화")
        
        :param sheet_obj: 
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        
        pass

    def OnSheetBeforeDoubleClick(self, sheet_obj):
        """
        #print("Workbook Event => OnSheetBeforeDoubleClick, 워크북->더블클릭 전에")
        
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnSheetBeforeRightClick(self, sheet_obj, range_obj):
        """
        #print("Workbook Event => OnSheetBeforeRightClick, 워크북->오른쪽 클릭전에")
        
        :param sheet_obj: 
        :param range_obj: 
        :return: 
        """
        
        pass

    def OnSheetCalculate(self, sheet_obj):
        """
        #print("Workbook Event => OnSheetCalculate, 워크북->계산후에")
        
        :param sheet_obj: 
        :return: 
        """
        pass

    def OnSheetChange(self, sheet_obj, range_obj):
        """
        #print("Workbook Event => OnSheetChange, 워크북->시트변경")
        
        :param sheet_obj: 
        :param range_obj: 
        :return: 
        """
        pass

    def OnSheetDeactivate(self, sheet_obj):
        """
        #print("Workbook Event => OnSheetDeactivate, 워크북->워크시트 비활성화")
        
        :param sheet_obj: 
        :return: 
        """

        pass

    def OnSheetSelectionChange(self, sheet_obj, range_obj):
        """
        #print("Workbook Event => OnSheetSelectionChange, 워크북->시트->Selection변경")
        
        :param sheet_obj: 
        :param range_obj: 
        :return: 
        """
        pass

    def OnWindowActivate(self, *args):
        """
        #print("Workbook Event => OnWindowActivate, 워크북->엑셀-> 실행")
        
        :param args: 
        :return: 
        """
        pass

    def OnWindowDeactivate(self, window_obj):
        """
        #print("Workbook Event => OnWindowDeactivate, 워크북->엑셀->종료")
        
        :param window_obj: 
        :return: 
        """
        pass

    def OnWindowResize(self, window_obj):
        """
        #print("Workbook Event => OnWindowResize, 워크북->엑셀->창크기변경")
        
        :param window_obj: 
        :return: 
        """
        pass

class SheetEvents:
    def OnActivate(self):
        """
        #print("Sheet Event => OnActivate, 시트->활성화")
        
        :return: 
        """
        pass

    def OnSheetBeforeDoubleClick(self, range_obj, tf_cancel):
        """
        #print("Sheet Event => OnSheetBeforeDoubleClick, 시트->더블클릭 전")
        
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnBeforeRightClick(self, range_obj, tf_cancel):
        """
        #print("Sheet Event => OnBeforeRightClick, 시트->오른쪽 클릭전에")
        
        :param range_obj: 
        :param tf_cancel: 
        :return: 
        """
        pass

    def OnCalculate(self):
        """
        #print("Sheet Event => OnCalculate, 시트->계산하고나서")
        
        :return: 
        """
        pass

    def OnChange(self, range_obj):
        """
        #print("Sheet Event => OnChange, 시트->셀의 뭔가가 변경")
        
        :param range_obj: 
        :return: 
        """
        pass

    def OnDeactivate(self):
        """
        #print("Sheet Event => OnDeactivate, 시트->비활성화")
        
        :return: 
        """
        pass

    def OnSelectionChange(self, range_obj):
        """
        #print("Sheet Event => OnSelectionChange, 시트->Selection변경")
        
        :param range_obj: 
        :return: 
        """
        pass

#sphinix를 만들때는 아랫부분의 글을 삭제해야 합니다
excel = win32.dynamic.Dispatch("Excel.Application")
excel.Visible = 1
workbook = excel.ActiveWorkbook
sheet = excel.ActiveSheet
excel_application_event = win32.WithEvents(excel, ApplicationEvents)
excel_workbook_event = win32.WithEvents(workbook, WorkbookEvents)
excel_sheet_event = win32.WithEvents(sheet, SheetEvents)

while True:
    pythoncom.PumpWaitingMessages()
    time.sleep(0.01)