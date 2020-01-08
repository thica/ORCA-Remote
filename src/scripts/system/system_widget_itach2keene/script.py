# -*- coding: utf-8 -*-
#

"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2019  Carsten Thielepape
    Please contact me by : http://www.orca-remote.org/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from typing                                 import Union
from typing                                 import List
from typing                                 import Dict
from typing                                 import Tuple


from xml.etree.ElementTree                  import ElementTree
from xml.etree.ElementTree                  import tostring
from xml.etree.ElementTree                  import ParseError
from xml.etree.ElementTree                  import Element
from xml.etree.ElementTree                  import XMLParser

from ORCA.utils.XML                         import CommentedTreeBuilder

from kivy.uix.boxlayout                     import BoxLayout
from kivy.uix.button                        import Button
from kivy.uix.label                         import Label
from kivy.uix.textinput                     import TextInput
from kivy.uix.popup                         import Popup
from kivy.uix.screenmanager                 import FadeTransition
from kivy.logger                            import Logger
from kivy.uix.widget                        import Widget

from ORCA.ui.BasePopup                      import SettingSpacer
from ORCA.vars.Replace                      import ReplaceVars
from ORCA.widgets.core.FileBrowser          import FileBrowser
from ORCA.utils.RemoveNoClassArgs           import RemoveNoClassArgs
from ORCA.scripttemplates.Template_System   import cSystemTemplate
from ORCA.widgets.base.Base                 import cWidgetBase
from ORCA.ScreenPage                        import cScreenPage

import ORCA.Globals as Globals

'''
<root>
  <repositorymanager>
    <entry>
      <name>Widget iTach2Keene</name>
      <description language='English'>Additional Widget to convert IR Files from iTach format to Kira Keene format</description>
      <description language='German'>Zusätzliches Widgets um IR Dateien vom iTach Format zum Kira Keene Format zu konvertieren</description>
      <author>Carsten Thielepape</author>
      <version>4.6.2</version>
      <minorcaversion>4.6.2</minorcaversion>
      <skip>0</skip>
      <sources>
        <source>
          <local>$var(APPLICATIONPATH)/scripts/system/system_widget_itach2keene</local>
          <sourcefile>$var(REPOSITORYWWWPATH)/scripts/system_widget_itach2keene.zip</sourcefile>
          <targetpath>scripts/system</targetpath>
        </source>
      </sources>
      <skipfiles>
      </skipfiles>
    </entry>
  </repositorymanager>
</root>
'''

def ToHex(iNumber) -> str:
    sTmp:str="0000"+hex(iNumber)
    sTmp=sTmp.replace('x', '0')
    sTmp=sTmp[-4:]
    return sTmp

def GlobalCacheToCCF(uGCString:str) -> Tuple[str,int]:

    aArray:List
    uDelimiter:str      = ','
    uFinalString        = u'0000 '    #0000 denotes CCF type
    iFreqNum:int
    iFreq:int
    iPairData:int
    uTmpString:str
    iTransCount:int
    uTransCount:str
    uRepeatCount:str   = u'0000'

    if uGCString=='':
        return uGCString,1
    if uGCString[0]=='{':
        return uGCString,1

    aArray = uGCString.split(uDelimiter,1024)

    if uGCString=='':
        return '',0
        #("Error: Please enter a valid " + GC2CCF.Properties.Resources.Company + " sendir command.");

    if len(aArray) < 6:
        return '',0
        #return ("Error: Please enter a valid " + GC2CCF.Properties.Resources.Company + " sendir command.");

    if aArray[3]=="":
        return '',0
        #return ("Error: Error parsing data. Please try again.");

    iFreqNum = int(aArray[3])
    iRepeatCount=int(aArray[4])
    #if iRepeatCount>0:
    #    sRepeatCount=ToHex(iRepeatCount)

    if iFreqNum == 0:
        return '',0
        #return ("Error: Error parsing data. Please try again.");

    iFreq = int(41450 / (iFreqNum / 100))

    uTmpString  = ToHex(iFreq)
    iTransCount = int((len(aArray) - 6) / 2)

    uTransCount = ToHex(iTransCount)

    uFinalString = uFinalString + uTmpString + " " + uRepeatCount + " " + uTransCount

    i:int    = 6
    iEnd:int = len(aArray)
    while i<iEnd:
        if aArray[i]=='':
            return '',0
            #return ("Error: Error parsing data. Please try again.");
        iPairData = int(aArray[i])
        uTmpString = ToHex(iPairData)
        uFinalString = uFinalString + " " + uTmpString
        i=i+1
    return uFinalString,iRepeatCount

def CCfToKeene(uCCFString:str,iRepeatCount:int):
    iX:int          = 0
    iy:int          = 0
    uTmpStr:str
    iFreq:int
    iPair_Count:int
    iLead_in:int
    aMyInt:List     = []
    iTint:int
    aBurst_Time:List = []
    iCycle_time:int
    uData:str
    iCodeLength:int
    bError:bool
    uRet:str

    if uCCFString=='':
        return uCCFString
    if uCCFString[0]=='{':
        return uCCFString

    uData       = uCCFString.strip()
    iCodeLength = len(uData)
    bError      = True
    try:

        while iX<255:
            aBurst_Time.append(0)
            iX=iX+1

        iX=0
        while iX<iCodeLength:
            uTmpStr = uData[iX: iX + 4]
            aBurst_Time[iy]=int(uTmpStr,16)
            iy=iy+1
            iX=iX+5

        iFreq = int (4145 / aBurst_Time[1])

        iPair_Count = aBurst_Time[2]
        if iPair_Count == 0:
            iPair_Count = aBurst_Time[3]

        #print "Frequency = " , iFreq
        #print "Pair_count = " , iPair_Count

        iX=0
        while iX<iy:
            aMyInt.append(0)
            iX=iX+1

        aMyInt[0]       = int(iFreq * 256 + iPair_Count)
        iCycle_time     = int(1000 / iFreq)
        iLead_in        = aBurst_Time[4] * iCycle_time
        aMyInt[1]       = iLead_in
        aMyInt[2]       = aBurst_Time[5] * iCycle_time # lead space
        iPair_Count     = iPair_Count - 1  # only loop data pairs
        iX              = 0
        iEnd            = iPair_Count * 2

        while iX<iEnd:
            iTint = int(aBurst_Time[iX + 6] * iCycle_time)
            aMyInt[iX + 3] = iTint
            iX=iX+1

        aMyInt[iX + 2] = 8192   # over write the lead out space with 2000 X is one over when exits from for loop
        uData = ""

        iX              = 0
        iEnd            = (iPair_Count * 2) + 3
        while iX<iEnd:
            uData = uData + ToHex(aMyInt[iX]) + " "
            iX=iX+1
        bError = False
    except Exception as e:
        uMsg:str='CCfToKeene:Can''t Convert:'+str(e)
        Logger.error (uMsg)
        Logger.error (uCCFString)

    if bError:
        return u""
    else:
        uRet="K "+ uData.strip().upper()
        if iRepeatCount>1:
            uRet=uRet+' 4000 '+str(iRepeatCount)
        return uRet


def GlobalCacheToKeene(uGCString:str) -> str:
    uTmp:str
    iRepeatCount:int
    uTmp,iRepeatCount=GlobalCacheToCCF(uGCString)
    if uTmp=='' or iRepeatCount==0:
        Logger.error ("wrong string:"+uGCString)
    return CCfToKeene(uTmp,iRepeatCount)

class cITachToKeene(BoxLayout):

    def __init__(self, **kwargs):
        kwargs['orientation']='vertical'
        super(cITachToKeene, self).__init__(**RemoveNoClassArgs(kwargs,BoxLayout))
        self.uCodesetFileName:str           = ''
        self.oLayoutHeaders:BoxLayout       = BoxLayout(size_hint_y= None , height= 30)
        self.oLayoutButtons:BoxLayout       = BoxLayout(size_hint_y= None , height= 30)
        self.oLayoutPanels:BoxLayout        = BoxLayout()
        self.add_widget(self.oLayoutHeaders)
        self.add_widget(SettingSpacer())
        self.add_widget(self.oLayoutPanels)
        self.add_widget(SettingSpacer())
        self.add_widget(self.oLayoutButtons)

        self.oTextInput:TextInput           = TextInput()
        self.oTextInput2:TextInput          = TextInput()
        self.oLayoutPanels.add_widget(self.oTextInput)
        self.oLayoutPanels.add_widget(self.oTextInput2)

        self.oButtonLoad:Button             = Button(text = ReplaceVars('$lvar(563)'))
        self.oButtonSave:Button             = Button(text = ReplaceVars('$lvar(5025)'))
        self.oButtonLoad.bind(on_release = self.show_load)
        self.oButtonSave.bind(on_release = self.show_save)
        self.oLayoutButtons.add_widget(self.oButtonLoad)
        self.oLayoutButtons.add_widget(self.oButtonSave)

        self.oLabelITach:Label              = Label(text = "ITach", halign='center')
        self.oLabelKeene:Label              = Label(text = "Keene Kira", halign='center')
        self.oLayoutHeaders.add_widget(self.oLabelITach)
        self.oLayoutHeaders.add_widget(self.oLabelKeene)

        self.oContent:Union[FileBrowser,None] = None
        self._popup:Union[Popup,None]         = None
        self.oXMLCodeset:Union[Element,None]  = None

    # noinspection PyUnusedLocal
    def show_load(self,*largs) -> None:

        alargs= {'select_string': ReplaceVars('$lvar(563)'),
                 'cancel_string': ReplaceVars('$lvar(5009)'),
                 'libraries_string': ReplaceVars('$lvar(5018)'),
                 'favorites_string': ReplaceVars('$lvar(5019)'),
                 'computer_string': ReplaceVars('$lvar(5020)'),
                 'location_string': ReplaceVars('$lvar(5021)'),
                 'listview_string': ReplaceVars('$lvar(5022)'),
                 'iconview_string': ReplaceVars('$lvar(5023)'),
                 'transition ': FadeTransition(),
                 'size_hint': (1, 1),
                 'favorites': [(Globals.oPathRoot.string, 'ORCA')],
                 'show_fileinput': False,
                 'show_filterinput': False,
                 'dirselect': False,
                 'path': Globals.oPathCodesets.string,
                 'filters': ['*.xml', ]
                 }
        #alargs['filters']=          ['CODESET_iTach_*.xml',]
        #alargs['filters']=           [self.MyFilter,]

        self.oContent=FileBrowser(**alargs)
        self.oContent.bind(on_success=self.load,on_canceled=self.dismiss_popup)
        self._popup = Popup(title=ReplaceVars("$lvar(5027)"), content=self.oContent, size_hint=(1, 1))
        self._popup.open()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def MyFilter(self,uFolder:str,uFile:str) -> bool:
        if "CODESET_iTach" in uFile:
            return True
        return False

    # noinspection PyUnusedLocal
    def dismiss_popup(self,*largs) -> None:
        self._popup.dismiss()

    def load(self,oFileBrowser:FileBrowser) -> None:

        oCode:Element
        oXMLRoot:Element
        uCmd:str

        if len(oFileBrowser.selection)!=0:
            self.uCodesetFileName=oFileBrowser.selection[0]

        try:
            self.oXMLCodeset = ElementTree()
            oParser          = XMLParser(target=CommentedTreeBuilder())
            self.oXMLCodeset.parse(source=self.uCodesetFileName,parser=oParser)
            if self.oXMLCodeset is not None:
                oXMLRoot = self.oXMLCodeset.getroot()
                self.oTextInput.text=tostring(oXMLRoot)
                for oCode in oXMLRoot:
                    uCmd=oCode.get('cmd')
                    if uCmd is not None:
                        oCode.set('cmd',GlobalCacheToKeene(uCmd))
                self.AdjustRepManagerITachToKeene(oXMLRoot)
                self.oTextInput2.text=tostring(oXMLRoot)
        except ParseError as uErrMsg:
            uMsg='Parse Error '+str(uErrMsg)
            Logger.error (uMsg)
        except Exception as e:
            uMsg='General Error '+str(e)
            Logger.error (uMsg)

        self.dismiss_popup()

    # noinspection PyMethodMayBeStatic
    def AdjustRepManagerITachToKeene(self,oXMLRoot:Element) -> None:
        oXMLRepMgr:Element
        oXMLRepMgrEntry:Element
        aXMLRepMgrDescriptions:List[Element]
        oDes:Element
        oXMLRepMgrName:Element
        aXMLRepMgrDependencies:List[Element]
        oDEDep:Element
        oName:Element
        oXMLRepMgSources:List[Element]
        oXMLRepMgSource:Element

        oXMLRepMgr=oXMLRoot.find("repositorymanager")
        if oXMLRepMgr is not None:
            oXMLRepMgrEntry=oXMLRepMgr.find("entry")
            if oXMLRepMgrEntry is not None:
                aXMLRepMgrDescriptions=oXMLRepMgrEntry.findall("description")
                if aXMLRepMgrDescriptions is not None:
                    for oDes in aXMLRepMgrDescriptions:
                        oDes.text=oDes.text.replace("iTach IR","Keene Kira IR")
                oXMLRepMgrName=oXMLRepMgrEntry.find("name")
                if oXMLRepMgrName is not None:
                    oXMLRepMgrName.text=oXMLRepMgrName.text.replace("iTach","Keene Kira")
                aXMLRepMgrDependencies=oXMLRepMgrEntry.findall("dependencies")
                if aXMLRepMgrDependencies is not None:
                    for oDep in aXMLRepMgrDependencies:
                        oDEDep=oDep.find("dependency")
                        if oDEDep is not None:
                            oName=oDEDep.find("name")
                            if oName is not None:
                                oName.text=oName.text.replace("iTach IR Control","Keene Kira IR Control")
                aXMLRepMgSources=oXMLRepMgrEntry.findall("sources")
                if aXMLRepMgSources is not None:
                    for oXMLRepMgSource in aXMLRepMgSources:
                        for oSource in oXMLRepMgSource:
                            oSource.text=oSource.text.replace("_iTach_","_Keene_Kira_")

    # noinspection PyMethodMayBeStatic
    def AdjustRepManagerITachToCCF(self,oXMLRoot:Element) -> None:
        oXMLRepMgr:Element
        oXMLRepMgr=oXMLRoot.find("repositorymanager")
        if oXMLRepMgr is not None:
            oXMLRepMgrEntry=oXMLRepMgr.find("entry")
            if oXMLRepMgrEntry is not None:
                oXMLRepMgrDescriptions=oXMLRepMgrEntry.findall("description")
                if oXMLRepMgrDescriptions is not None:
                    for oDes in oXMLRepMgrDescriptions:
                        oDes.text=oDes.text.replace("iTach IR","CCF IR Codes")
                oXMLRepMgrName=oXMLRepMgrEntry.find("name")
                if oXMLRepMgrName is not None:
                    oXMLRepMgrName.text=oXMLRepMgrName.text.replace("iTach","CCF IR Codes")
                oXMLRepMgrDependencies=oXMLRepMgrEntry.findall("dependencies")
                if oXMLRepMgrDependencies is not None:
                    for oDep in oXMLRepMgrDependencies:
                        oDEDep=oDep.find("dependency")
                        if oDEDep is not None:
                            oName=oDEDep.find("name")
                            if oName is not None:
                                oName.text=oName.text.replace("iTach IR Control","CCF IR Codes")
                oXMLRepMgSources=oXMLRepMgrEntry.findall("sources")
                if oXMLRepMgSources is not None:
                    oXMLRepMgSource=oXMLRepMgSources.find("source")
                    if oXMLRepMgSource is not None:
                        for oSource in oXMLRepMgSource:
                            oSource.text=oSource.text.replace("_iTach_","_infrared_ccf_")

    # noinspection PyUnusedLocal
    def show_save(self,*largs) -> None:
        if self.oTextInput2.text!="":
            uOutput:str=self.uCodesetFileName+"3"
            uOutput=uOutput.replace("_iTach_","_Keene_Kira_")
            self.oXMLCodeset.write(uOutput, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        self.oTextInput.text=""
        self.oTextInput2.text=""


class cWidgetITach2Keene(cWidgetBase):

    """
    WikiDoc:Doc
    WikiDoc:Context:Widgets
    WikiDoc:Page:Widgets-ITACH2KEENE
    WikiDoc:TOCTitle:ITach2Keene
    = ITACH2KEENE =

    The ITach2Keene widget converts ITach IR Codes to Keene Kira IR Codes. This is a more like internal widget

    There are no further attributes to the common widget attributes

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |type
    |fixed: needs to be "ITACH2KEENE". Capital letters!
    |}</div>

    Below you see an example for a ITAch2Keene widget
    <div style="overflow-x: auto;"><syntaxhighlight  lang="xml">
    <element name='ITACH2KEENE' type='ITACH2KEENE' posx="center" posy="middle" width="%90" height="%90" backgroundcolor='#454545ff' />
    </syntaxhighlight></div>
    WikiDoc:End
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def InitWidgetFromXml(self,oXMLNode:Element,oParentScreenPage:cScreenPage, uAnchor:str) -> bool:
        """ Reads further Widget attributes from a xml node """
        return self.ParseXMLBaseNode(oXMLNode,oParentScreenPage , uAnchor)

    def Create(self,oParent:Widget) -> bool:
        """ creates the Widget """
        if self.CreateBase(Parent=oParent,Class=cITachToKeene):
            self.oParent.add_widget(self.oObject)
            return True
        return False


class cScript(cSystemTemplate):
    """
    WikiDoc:Doc
    WikiDoc:Context:Scripts
    WikiDoc:Page:Scripts-system-widget_iTach2Keene
    WikiDoc:TOCTitle:Script Widget iTach to Keene converter
    = Widget extension for the iTach2Keene converter =

    This script provides a further widget, used by the iTech2Keene converter tool

    <div style="overflow:auto; ">
    {| class="wikitable"
    ! align="left" | Attribute
    ! align="left" | Description
    |-
    |cmd_type
    |The requested helper function: Only "Register" od "UnRegister"
    |}</div>

    WikiDoc:End
    """

    def __init__(self):
        cSystemTemplate.__init__(self)
        self.uSubType           = u'WIDGET'
        self.uSortOrder         = u'auto'
        self.uIniFileLocation   = u'none'


    def RunScript(self, *args, **kwargs) -> None:
        Globals.oNotifications.RegisterNotification("UNKNOWNWIDGET",fNotifyFunction=self.AddWidgetFromXmlNode,uDescription="Script Widget iTach2Keene")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def AddWidgetFromXmlNode(self,*args,**kwargs) -> Union[Dict,None]:
        oScreenPage:cScreenPage = kwargs.get("SCREENPAGE")
        oXMLNode:Element        = kwargs.get("XMLNODE")
        uAnchor:str             = kwargs.get("ANCHOR")
        oWidget:cWidgetBase     = kwargs.get("WIDGET")


        if uAnchor is None or oScreenPage is None or oXMLNode is None or oWidget is None:
            return None

        if oWidget.uTypeString != "ITACH2KEENE":
            return None

        Ret = oScreenPage.AddWidgetFromXmlNode_Class(oXMLNode=oXMLNode,  uAnchor=uAnchor,oClass=cWidgetITach2Keene)
        return {"ret":Ret}

