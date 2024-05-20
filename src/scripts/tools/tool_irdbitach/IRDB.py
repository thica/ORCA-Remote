# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2024  Carsten Thielepape
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

from __future__             import annotations
from typing                 import Callable
from typing                 import Union
from typing                 import List
from typing                 import Tuple
from typing                 import Dict

from xml.etree.ElementTree  import ParseError
from xml.etree.ElementTree  import Element

from xml.etree.ElementTree  import SubElement

from time import sleep
import codecs

from kivy.uix.widget        import Widget
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.popup         import Popup
from kivy.uix.button        import Button
from kivy.uix.checkbox      import CheckBox
from kivy.uix.label         import Label
from kivy.uix.textinput     import TextInput
from kivy.uix.scrollview    import ScrollView
from kivy.uix.gridlayout    import GridLayout
from kivy.metrics           import dp
from kivy.clock             import Clock
from kivy.logger            import Logger
from kivy.network.urlrequest import UrlRequest

from ORCA.vars.Replace      import ReplaceVars
from ORCA.vars.Access       import SetVar
from ORCA.ui.ProgressBar    import cProgressBar
from ORCA.utils.LogError    import LogError
from ORCA.utils.TypeConvert import ToInt
from ORCA.utils.TypeConvert import ToUnicode
from ORCA.utils.FileName    import cFileName
from ORCA.utils.XML         import GetXMLTextAttribute
from ORCA.utils.XML         import XMLPrettify
from ORCA.utils.XML         import LoadXMLString
from ORCA.utils.XML         import LoadXMLFile
from ORCA.utils.XML         import WriteXMLFile
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.ui.BasePopup      import cBasePopup,SettingSpacer
from ORCA.Globals import Globals

import urllib

__all__ = ['ShowITachIRDB', 'ITach2CCF']

class cITachIRDB_Editor(cBasePopup):
    """ Editor Class for the IRDB Data """
    ''' Currently unused '''
    def __init__(self):
        super(cITachIRDB_Editor,self).__init__()
        self.oXMLText=None
    def Start(self):
        """ create the popup """
        oContent      = BoxLayout( spacing='5dp' , orientation='vertical')
        self.oPopup   = popup = Popup(content=oContent, title=ReplaceVars('$lvar(666)'), size_hint=(0.95, 0.95),  auto_dismiss=False)

        #we need to open the popup first to get the metrics
        popup.open()
        #todo: check sXML reference
        #self.oXMLText=TextInput(text=oDBSelector.sXML)
        oContent.add_widget(self.oXMLText)
        oContent.add_widget(SettingSpacer())

        # 2 buttons are created for save or cancel the current file
        oBtnlayout      = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        oBtn            = Button(text=ReplaceVars('$lvar(5025)'))
        oBtn.bind (on_release=self.On_Save)
        oBtnlayout.add_widget(oBtn)
        oBtn             = Button(text=ReplaceVars('$lvar(5009)'))
        oBtn.bind(on_release=self.oPopup.dismiss)
        oBtnlayout.add_widget(oBtn)
        oContent.add_widget(oBtnlayout)
        self.oXMLText.cursor=(0,0)

    def Show(self):
        """ Shows the main popup """
        self.oPopup.open()

    # noinspection PyUnusedLocal
    def On_Save(self, oButton:Button):
        """ saves the Codeset file """
        try:
            oRoot:Element = LoadXMLString(uXML=self.oXMLText.text)
            oFilename=cFileName(Globals.oPathCodesets) +  oDBSelector.oCodesetName.text
            WriteXMLFile(oFile=oFilename,oElem=oRoot)
        except Exception as e:
            uMsg=LogError(uMsg='IRDB: Error Writing iTach codeset file',oException=e)
            ShowErrorPopUp(uMessage=uMsg)
        self.oPopup.dismiss()

class cITachIRDB_Selector(cBasePopup):
    """ Class to select an IRDb item """

    def __init__(self):
        super(cITachIRDB_Selector,self).__init__()
        self.fktCallBack:Union[Callable,None] = None
        self.oPopup:Union[Popup,None]         = None

    def Start(self,uTitle:str,aOptions:List,fktCallBack:Callable):
        """ starts selection """

        self.fktCallBack = fktCallBack
        oButton:Button
        uName:str
        # create the popup
        oContent:GridLayout         = GridLayout(cols=1, spacing='5dp')
        oScrollview:ScrollView      = ScrollView( do_scroll_x=False, bar_width='10dp',scroll_type=['bars','content'] )
        oScrollcontent:GridLayout   = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
        oScrollcontent.bind(minimum_height=oScrollcontent.setter('height'))
        self.oPopup                 = Popup(content=oContent, title=ReplaceVars(uTitle), size_hint=(0.5, 0.9),  auto_dismiss=False)

        #we need to open the popup first to get the metrics
        self.oPopup.open()
        #Add some space on top
        oContent.add_widget(Widget(size_hint_y=None, height=dp(2)))
        # add all the options
        for option in aOptions:
            if hasattr(option,"uName"):
                uName=option.uName
            else:
                uName=option.uType
            oButton = Button(text=uName, size=(self.oPopup.width, dp(30)), size_hint=(None, None))
            oButton.bind(on_release=self.On_Value)
            oButton.oDBRef=option
            oScrollcontent.add_widget(oButton)

        # finally, add a cancel button
        oScrollview.add_widget(oScrollcontent)
        oContent.add_widget(oScrollview)
        oContent.add_widget(SettingSpacer())
        oButton = Button(text=ReplaceVars('$lvar(5009)'), size=(self.oPopup.width, dp(50)),size_hint=(0.9, None))
        oButton.bind(on_release=self.oPopup.dismiss)
        oContent.add_widget(oButton)

    def Show(self):
        """ Opens the popop """
        self.oPopup.open()

    def On_Value(self, instance):
        """ internal function, called , after a selection has benn made """
        self.oPopup.dismiss()
        self.fktCallBack(instance)

class ITachIRDB(cBasePopup):
    """ The IRDb abstraction """
    def __init__(self):
        super(ITachIRDB,self).__init__()

        self.aBrands:List[cBrand]                               = []
        self.aModels:List[cModel]                                = []
        self.aTypes:List[cType]                                 = []
        self.bStopWait:bool                                     = False
        self.bStopWait:bool                                     = False
        self.dTranslations:Dict                                 = {}
        self.IRDBInterface:Union[IRDBInterface,None]            = None
        self.oBrandsSelector:Union[cITachIRDB_Selector,None]    = None
        self.oBtnBrands:Union[Button,None]                      = None
        self.oBtnModels:Union[Button,None]                      = None
        self.oBtnTypes:Union[Button,None]                       = None
        self.oCodesetName:Union[TextInput,None]                 = None
        self.oOptionOptimizeChannelSelect:Union[CheckBox,None]  = None
        self.oOptionWriteCCF:Union[CheckBox,None]               = None
        self.oOptionWriteITach:Union[CheckBox,None]             = None
        self.oProgressBar:Union[cProgressBar,None]              = None
        self.oSelector:Union[cITachIRDB_Selector,None]          = None
        self.oTextBrands:Union[Label,None]                      = None
        self.oTextModels:Union[Label,None]                      = None
        self.oTextTypes:Union[Label,None]                       = None
        self.uHost:str                                          = ''
        self.uOldBrand:str                                      = ''
        self.uOldModel:str                                      = ''
        self.uOldType:str                                       = ''
        self.uPassword:str                                      = ''
        self.uUser:str                                          = ''

    # noinspection PyMethodMayBeStatic
    def ConvertItach2CCF(self) -> None:
        #todo : remove when we know, it is not used anymore
        oXMLCode:Element
        uFile:str
        uCmd:str
        uRepeat:str
        uFileName: str
        uFinal:str
        aFiles:List[str]  = Globals.oPathCodesets.GetFolderList()
        aFiles2:List[str] = []
        for uFile in aFiles:
            if uFile.startswith('CODESET_iTach_'):
                aFiles2.append(uFile)

        for uFile in aFiles2:
            oFile:cFileName = cFileName(Globals.oPathCodesets) + uFile
            oXMLCodeset:Element = LoadXMLFile(oFile=oFile)
            oXMLCodes:List[Element] = oXMLCodeset.findall('code')
            for oXMLCode in oXMLCodes:
                uCmd = GetXMLTextAttribute(oXMLNode=oXMLCode,uTag='cmd',bMandatory=False,vDefault='')
                if uCmd.startswith('sendir,'):
                    uRepeat,uCmd=ITach2CCF(uCmd)
                    oXMLCode.set('cmd_ccf', uCmd)
                    oXMLCode.set('repeatcount', uRepeat)
                    del oXMLCode.attrib['cmd']
            uFileName=str(oFile).replace('_iTach_','_infrared_ccf_')
            uFinal=ToUnicode(XMLPrettify(oElem=oXMLCodeset))
            uFinal=uFinal.replace('<?xml version="1.0"?>','<?xml version="1.0" encoding="UTF-8"?>')
            with codecs.open(uFileName, 'w', 'utf-8') as oOutfile:
                oOutfile.write(uFinal)

    def Start(self,uHost:str,uUser:str,uPassword:str) -> None:

        """ starts the selection of an IRDB item """
        self.uPassword  = uPassword
        self.uUser      = uUser
        self.uHost      = uHost

        oContent = BoxLayout(orientation='vertical', spacing='5dp')
        self.oPopup =  Popup(title=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_4)'),content=oContent, size_hint=(0.9, 0.9),auto_dismiss=False)

        self.oBtnBrands        = Button(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_6)'))
        self.oBtnTypes         = Button(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_7)'))
        self.oBtnModels        = Button(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_8)'))
        self.oTextBrands       = Label()
        self.oTextTypes        = Label()
        self.oTextModels       = Label()
        self.oProgressBar      = cProgressBar()

        self.oBtnBrands.bind(on_release=self.On_BtnBrands)
        self.oBtnTypes.bind(on_release=self.On_BtnTypes)
        self.oBtnModels.bind(on_release=self.On_BtnModels)

        # construct the content, widget are used as a spacer
        #Gridlayout is working properly after adding into a box layout
        oContent.add_widget(Widget(height='2dp', size_hint_y=None))
        oContentBrands = BoxLayout(orientation='horizontal', spacing='5dp', height='40dp',size_hint_y=None)
        oContentBrands.add_widget(self.oBtnBrands)
        oContentBrands.add_widget(self.oTextBrands)
        oContentTypes = BoxLayout(orientation='horizontal', spacing='5dp' , height='40dp',size_hint_y=None)
        oContentTypes.add_widget(self.oBtnTypes)
        oContentTypes.add_widget(self.oTextTypes)
        oContentModels = BoxLayout(orientation='horizontal', spacing='5dp' , height='40dp',size_hint_y=None)
        oContentModels.add_widget(self.oBtnModels)
        oContentModels.add_widget(self.oTextModels)
        oContent.add_widget(oContentBrands)
        oContent.add_widget(oContentTypes)
        oContent.add_widget(oContentModels)

        if self.uUser == '' or self.uPassword == '':
            oContent.add_widget(SettingSpacer())
            oContent.add_widget(Label(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_5)'),height='20dp', size_hint_y=None))

        oContent.add_widget(SettingSpacer())
        self.oCodesetName = TextInput(height='20dp')
        oContent.add_widget(self.oCodesetName)
        oContent.add_widget(SettingSpacer())

        oContentWriteCCF = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionWriteCCF = CheckBox(active=True)
        oContentWriteCCF.add_widget(Label(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_9)'),height='20dp', size_hint_y=None, halign='left'))
        oContentWriteCCF.add_widget(self.oOptionWriteCCF)
        oContent.add_widget(oContentWriteCCF)

        oContentWriteITach = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionWriteITach = CheckBox()
        oContentWriteITach.add_widget(Label(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_10)'),height='20dp', size_hint_y=None, halign='left'))
        oContentWriteITach.add_widget(self.oOptionWriteITach)
        oContent.add_widget(oContentWriteITach)

        oContentOptimizeChannelSelect = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionOptimizeChannelSelect = CheckBox()
        oContentOptimizeChannelSelect.add_widget(Label(text=ReplaceVars('$lvar(SCRIPT_TOOLS_IRDBITACH_11)'),height='20dp', size_hint_y=None, halign='left'))
        oContentOptimizeChannelSelect.add_widget(self.oOptionOptimizeChannelSelect)
        oContent.add_widget(oContentOptimizeChannelSelect)
        oContent.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        oBtnButtons      = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        oBtn            = Button(text=ReplaceVars('$lvar(5008)'))
        oBtn.bind (on_release=self.On_BtnLoad)
        oBtnButtons.add_widget(oBtn)
        oBtn             = Button(text=ReplaceVars('$lvar(5009)'))
        oBtn.bind(on_release=self.oPopup.dismiss)
        oBtnButtons.add_widget(oBtn)
        oContent.add_widget(oBtnButtons)
        self.oPopup.open()
        self.CreateCodesetFileName()

    def CreateCodesetFileName(self) -> None:
        """ Creates the filename of a codset file """
        uInterface='XXXXX'
        uText='CODESET_%s_%s_%s_%s.xml' %(uInterface,self.oTextBrands.text,self.oTextTypes.text,self.oTextModels.text)
        uText=self.Remove(uValue=uText, uDeleteChars='\\/:*?"<>|')
        self.oCodesetName.text=uText

    # noinspection PyMethodMayBeStatic
    def Remove(self,uValue, uDeleteChars:str) -> str:
        """ deletes invalid characters from a filename """
        for c in uDeleteChars:
            uValue = uValue.replace(c,'-')
        return uValue

    # noinspection PyMethodMayBeStatic
    def GetProperName(self,uURL:Dict) -> str:
        """ adjust url to valid characters used by irdb """
        uRet:str=uURL['Href']
        iPos:int=uRet.rfind('/')
        if not iPos==-1:
            uRet=uRet[iPos+1:]
            uRet=uRet.replace('%20',' ')
        return uRet

    # noinspection PyUnusedLocal
    def On_BtnBrands(self,oButton:Button) -> None:
        """ After the brands button has been pressed """
        if self.oBrandsSelector is None:
            self.oProgressBar.Show(uTitle='$lvar(SCRIPT_TOOLS_IRDBITACH_6)',uMessage='$lvar(SCRIPT_TOOLS_IRDBITACH_12)',iMax=0)
        Clock.schedule_once(self.On_BtnBrands_Load,0)

    # noinspection PyUnusedLocal
    def On_BtnBrands_Load(self,*largs) -> None:
        """ Loads all brands """
        try:
            if len(self.aBrands)==0:
                self.IRDBInterface = IRDBInterface()
                self.IRDBInterface.Login()
                self.aBrands = self.IRDBInterface.GetBrands()
                self.IRDBInterface.Logout()

            if self.oBrandsSelector is None:
                self.oBrandsSelector=cITachIRDB_Selector()
                self.oProgressBar.ClosePopup()
                self.oBrandsSelector.Start('$lvar(SCRIPT_TOOLS_IRDBITACH_7)',self.aBrands,self.On_BtnBrandsSelected)
            else:
                self.oBrandsSelector.Show()
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='Can\'t load brands',oException=e))
            self.aBrands = []
            self.oProgressBar.ClosePopup()

    def On_BtnBrandsSelected(self,oButton:Button) -> None:
        """ handles, if the user has selected a brand """
        self.oTextBrands.text=oButton.text
        self.oTextTypes.text=''
        self.oTextModels.text=''
        self.CreateCodesetFileName()
        self.oBtnBrands.oDBRef=oButton.oDBRef

    # noinspection PyUnusedLocal
    def On_BtnTypes(self,oButton:Button) -> None:
        """ After the types button has been pressed """
        try:
            if self.oTextBrands.text!='':
                if self.uOldBrand!=self.oTextBrands.text:
                    uBrand:str =self.GetProperName(self.oBtnBrands.oDBRef.uLinks[0])
                    self.IRDBInterface.Login()
                    self.aTypes = self.IRDBInterface.GetTypes(uBrand)
                    self.IRDBInterface.Logout()
                    self.uOldBrand=self.oTextBrands.text

                self.oSelector=cITachIRDB_Selector()
                self.oSelector.Start('$lvar(SCRIPT_TOOLS_IRDBITACH_8)',self.aTypes,self.On_BtnTypesSelected)
        except Exception as e:
            uMsg=LogError(uMsg='Can\'t load types',oException=e)
            ShowErrorPopUp(uMessage=uMsg)
            self.aTypes = []

    def On_BtnTypesSelected(self,oButton:Button) -> None:
        """ handles, if the user has selected a Type """
        self.oTextTypes.text=oButton.text
        self.oTextModels.text=''
        self.oBtnTypes.oDBRef=oButton.oDBRef
        self.CreateCodesetFileName()

    # noinspection PyUnusedLocal
    def On_BtnModels(self,oButton:Button) -> None:
        """ After the Models button has been pressed """
        try:
            if self.oTextTypes.text!='':
                if self.uOldType!=self.oTextTypes.text:
                    uBrand:str=self.GetProperName(self.oBtnBrands.oDBRef.uLinks[0])
                    uType:str=self.GetProperName(self.oBtnTypes.oDBRef.uLinks[0])
                    self.IRDBInterface.Login()
                    self.aModels = self.IRDBInterface.GetModels(uBrand,uType)
                    self.IRDBInterface.Logout()
                    self.uOldType = self.oTextTypes.text
                self.oSelector = cITachIRDB_Selector()
                self.oSelector.Start('$lvar(SCRIPT_TOOLS_IRDBITACH_8)',self.aModels,self.On_BtnModelsSelected)
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='Can\'t load models',oException=e))
            self.aModels = []


    def On_BtnModelsSelected(self,oButton:Button) -> None:
        """ handles, if the user has selected a Model """
        self.oBtnModels.oDBRef=oButton.oDBRef
        self.oTextModels.text=oButton.text
        self.CreateCodesetFileName()

    # noinspection PyUnusedLocal
    def On_BtnLoad(self,oButton:Button):
        """ Loads the IRDB commands from the current selection """
        if self.oTextModels.text!='':

            try:
                self.ReadItachFunctionTranslation()
                uID:str = self.oBtnModels.oDBRef.uID
                self.IRDBInterface.Login()
                aCodeSets:List[cIRCode] =self.IRDBInterface.GetCodeSet(uID)
                self.IRDBInterface.Logout()
                for oCodeSet in aCodeSets:
                    oCodeSet.uString=oCodeSet.uString
                    uTransName:str=self.dTranslations.get(oCodeSet.uFunction)
                    if uTransName is not None:
                        oCodeSet.uFunction=uTransName
                    else:
                        Logger.debug('Unmatch IR Command:'+oCodeSet.uFunction)
                self.AddStandardCodes(aCodeSets)
                if self.oOptionWriteITach.active:
                    self.Save_As_iTach(aCodeSets)
                if self.oOptionWriteCCF.active:
                    self.Save_As_CCF(aCodeSets)
                self.oPopup.dismiss()
            except Exception as e:
                ShowErrorPopUp(uMessage=LogError(uMsg='Can\'t load functions',oException=e))

    def AddStandardCodes(self,oSet:List[cIRCode]) -> None:

        oFunction:cIRCode
        oSingleSet:cIRCode
        bHasPowerOn:bool      = False
        bHasPowerOff:bool     = False
        bHasPowerToggle:bool  = False
        bHasKey:bool          = False

        for oFunction in oSet:
            if oFunction.uFunction=='power_on':
                bHasPowerOn      = True
            if oFunction.uFunction=='power_off':
                bHasPowerOff      = True
            if oFunction.uFunction=='power_toggle':
                bHasPowerToggle      = True
            if oFunction.uFunction.startswith('key_'):
                bHasKey=True

        if bHasKey:
            if self.oOptionOptimizeChannelSelect.active==False or True:
                oSingleSet=cIRCode()
                oSingleSet.uCode1='{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}'
                oSingleSet.uFunction = 'channel_select'
                oSet.append(oSingleSet)
            else:
                # todo: set the optimisation substructure
                oSingleSet=cIRCode()
                oSingleSet.uCode1='NEWCHILD'
                oSet.append(oSingleSet)
                oSingleSet=cIRCode()
                oSingleSet.uCode1='{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}'
                oSingleSet.uFunction = 'channel_select_pre'
                oSet.append(oSingleSet)
                oSingleSet=cIRCode()
                oSingleSet.uCode1='key_ok'
                oSingleSet.uType='alias'
                oSingleSet.uString=''
                oSingleSet.uPreAction='channel_select_pre'
                oSingleSet.uFunction = 'channel_select'
                oSet.append(oSingleSet)
                oSingleSet=cIRCode()
                oSingleSet.uCode1='LEAVECHILD'

        if not bHasPowerOn and bHasPowerToggle:
            oSingleSet=cIRCode()
            oSingleSet.uFunction = 'power_on'
            oSingleSet.uCode1='power_toggle'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)

        if not bHasPowerOff and bHasPowerToggle:
            oSingleSet=cIRCode()
            oSingleSet.uFunction = 'power_off'
            oSingleSet.uCode1='power_toggle'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)

        if not bHasPowerToggle and bHasPowerOn:
            oSingleSet=cIRCode()
            oSingleSet.uFunction = 'power_toggle'
            oSingleSet.uCode1='power_on'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)


    def ReadItachFunctionTranslation(self) -> None:
        """ Reads the translation set from IRDB to ORCA """
        oSet:Element
        oCommand:Element
        if len(self.dTranslations)==0:
            oFnTranslation:cFileName = cFileName(Globals.oPathResources + 'irdbtranslation') + 'itach2orca.xml'
            try:
                Logger.debug (f'IRDB: Loading Translation Table: {oFnTranslation}')
                oET_Root:Element = LoadXMLFile(oFile=oFnTranslation)
                #oSets=oET_Root.findall('set')
                for oSet in oET_Root:
                    for oCommand in oSet.findall('action'):
                        uFrom:str = GetXMLTextAttribute(oXMLNode=oCommand,uTag='from',bMandatory=True,vDefault='')
                        uTo:str    = GetXMLTextAttribute(oXMLNode=oCommand,uTag='to',bMandatory=True,vDefault='')
                        self.dTranslations[uFrom]=uTo
            except ParseError as e:
                ShowErrorPopUp(uMessage=LogError(uMsg='IRDB: Error:Loading Translations file',oException=e))

    ''' Todo : check / remove '''
    def Save_As_iTach(self,oSet:List[cIRCode]) -> None:
        oRoot:Element
        oCodesetCode:Element
        oFunction:cIRCode
        uFilename:str       = f'{Globals.oPathCodesets}/iTach/{self.oCodesetName.text}'
        oFilename:cFileName = cFileName().ImportFullPath(uFnFullName=uFilename.replace('_XXXXX_','_iTach_'))
        try:
            oRoot = Element('codeset')
            for oFunction in oSet:
                oCodesetCode = SubElement(oRoot, 'action')
                oCodesetCode.set('string', 'codeset')
                oCodesetCode.set('name', oFunction.uFunction)
                oCodesetCode.set('type', oFunction.uType)
                uString:str=oFunction.uCode1.replace('sendir,1:1,','sendir,$cvar(CONFIG_MODULE):$cvar(CONFIG_CONNECTOR),')
                uString=uString.replace('\n','')
                uString=uString.replace('\r','')
                oCodesetCode.set('cmd', uString)
            uFinal:str=XMLPrettify(oElem=oRoot)
            uFinal=uFinal.replace('<?xml version="1.0"?>','<?xml version="1.0" encoding="UTF-8"?>')
            oFile = open(str(oFilename), 'w')
            oFile.write(uFinal)
            oFile.close()
            #oTree = ElementTree(oRoot)
            #oTree.write(uFilename, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='IRDB: Error Writing iTach codeset file',oException=e))

    def Save_As_CCF(self,oSet):
        oRoot:Element
        oRootToUse:Element
        oCodesetCode:SubElement
        oFunction:cIRCode
        uRepeat:str
        uString:str

        uFilename:str = f'{Globals.oPathCodesets}/infrared_ccf/{self.oCodesetName.text}'
        oFn:cFileName = cFileName().ImportFullPath(uFnFullName=uFilename.replace('_XXXXX_','_infrared_ccf_'))
        try:
            oRoot = Element('codeset')
            oRootToUse=oRoot
            for oFunction in oSet:
                if oFunction.uCode1=='NEWCHILD':
                    oCodesetCode = SubElement(oRootToUse, 'action')
                    oCodesetCode.set('name', oFunction.uFunction)
                    oRootToUse=oCodesetCode
                elif oFunction.uCode1=='LEAVECHILD':
                    oRootToUse=oRoot
                else:
                    oCodesetCode = SubElement(oRootToUse, 'action')
                    oCodesetCode.set('name', oFunction.uFunction)
                    if oFunction.uType!='alias':
                        if oFunction.uString!='':
                            oCodesetCode.set('string', oFunction.uString)
                    if oFunction.uType!='':
                        oCodesetCode.set('type', oFunction.uType)
                    if oFunction.uType=='cmd' and not 'REPEAT' in oFunction.uCode1:
                        uRepeat,uString=ITach2CCF(oFunction.uCode1)
                        uString=uString.replace('\n','')
                        uString=uString.replace('\r','')
                        oCodesetCode.set('cmd_ccf', uString)
                        oCodesetCode.set('repeatcount',uRepeat)
                    else:
                        if oFunction.uCode1!='':
                            oCodesetCode.set('cmd', oFunction.uCode1)
            uFinal:str = XMLPrettify(oElem=oRoot)
            uFinal=uFinal.replace('<?xml version="1.0"? >','<?xml version="1.0" encoding="UTF-8"?>')
            uFinal=uFinal.replace('{&amp;REPEAT&amp;:{&amp;REPEATCMD&amp;:&amp;key_&amp;,&amp;REPEATVAR&amp;:&amp;$cvar(CHANNELNUM)&amp;}}','{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}')
            oFile = open(str(oFn), 'w')
            oFile.write(uFinal)
            oFile.close()
            #oTree = ElementTree(oRoot)
            #oTree.write(uFilename, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        except Exception as e:
            ShowErrorPopUp(uMessage=LogError(uMsg='IRDB: Error Writing CCF codeset file',oException=e))

oDBSelector      = ITachIRDB()

def ShowITachIRDB(uHost:str,uUser:str,uPassword:str) -> ITachIRDB:
    """ Main class to get the Itach IR database codes """
    oDBSelector.Start(uHost,uUser,uPassword)
    return oDBSelector

CONTENT_TYPE = 'application/json;charset=utf-8'

# API Paths
BRANDS_PATH    = 'api/brands'
TYPES_PATH     = 'api/brands/{0}/types'
MODELS_PATH    = 'api/brands/{0}/types/{1}/models'
LOGIN_PATH     = 'api/account/login'
LOGOUT_PATH    = 'api/account/logout'
CODESET_PATH   = 'api/codesets/{0}'
FUNCTIONS_PATH = 'api/codesets/{0}/functions'
CODE_PATH      = 'api/codesets/{0}/functions/{1}/codes'
HEADERS        = {'Content-type': 'application/x-www-form-urlencoded',  'Accept': 'text/plain'}

class IRDBInterface:
    def __init__(self):
        self.oReq:Union[UrlRequest,None]  = None
        self.oAccount:Union[Account,None] = None
        self.bStopWait:bool = False

    # Call to add an api key to a url, as well as other params if they are provided
    def PrepareUrl(self, uPath:str, dParams:Dict = None) -> str:
        uUrl:str
        if self.oAccount:
            uUrl = oDBSelector.uHost + uPath + '?apikey=' + self.oAccount.uApiKey
            if dParams:
                for key, value in dParams.items():
                    uUrl += '&{}={}'.format(key, value)
            return uUrl
        return ''
    # Login, and save the account information provided (the api key particularly)
    # This must be called first.
    def Login(self) -> None:
        uUrl:str                = oDBSelector.uHost + LOGIN_PATH
        SetVar(uVarName         = 'ITach_Mail', oVarValue = oDBSelector.uUser)
        SetVar(uVarName         = 'ITach_Password', oVarValue = oDBSelector.uPassword)
        oLoginAccount:Account   = Account()
        oLoginAccount.uEmail    = oDBSelector.uUser
        oLoginAccount.uPassword = oDBSelector.uPassword

        self.oReq = UrlRequest(uUrl,  req_body=oLoginAccount.ToData(), req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        dResponse:Dict = self.oReq.result
        if dResponse:
            self.oAccount = Account(dResponse['Account'])

    # noinspection PyUnusedLocal,PyUnusedLocal
    def OnError(self,request,error):
        self.bStopWait      = True

    # noinspection PyProtectedMember
    def NewWait(self,fDelay:float) -> None:
        self.bStopWait=False

        while self.oReq.resp_status is None:
            self.oReq._dispatch_result(fDelay)
            sleep(fDelay)
            if self.bStopWait:
                self.bStopWait=False
                break

    # Logout.  The apikey is used to identify the account, which is added by PrepareUrl
    def Logout(self) -> None:
        uUrl:str = self.PrepareUrl(LOGOUT_PATH)
        UrlRequest(uUrl, req_headers=HEADERS)
        self.oAccount = None
    # Get a list of all available brands
    def GetBrands(self) -> List[cBrand]:
        uUrl:str = self.PrepareUrl(BRANDS_PATH)
        return self.GetClassListFromUrl(uUrl,cBrand)

    # Get a list of all device types available for the given brand
    def GetTypes(self, uBrandName:str) -> List[cType]:
        uUrl:str = self.PrepareUrl(TYPES_PATH.format(uBrandName))
        return self.GetClassListFromUrl(uUrl,cType)

    # Get a list of all models for the given brand and type

    def GetModels(self, uBrandName:str, uTypeName:str) -> List[cModel]:
        uBrandName = urllib.parse.quote(uBrandName,safe='')
        uTypeName =  urllib.parse.quote(uTypeName,safe='')
        uUrl:str = self.PrepareUrl(MODELS_PATH.format(uBrandName, uTypeName))
        return self.GetClassListFromUrl(uUrl,cModel)

    # Get a full set of codes for devices with the provided set id.
    # This will use one of a limited number of code requests available for an account in a day.
    def GetCodeSet(self, uSetId:str) -> List[cIRCode]:
        uUrl = self.PrepareUrl(CODESET_PATH.format(uSetId), {'output':'direct'})
        return self.GetClassListFromUrl(uUrl,cIRCode)

    # Get a list of functions available for devices with the provided set id.
    def GetFunctions(self, uSetId:str) -> List[cFunction]:
        uUrl:str = self.PrepareUrl(FUNCTIONS_PATH.format(uSetId))
        return self.GetClassListFromUrl(uUrl,cFunction)

    def GetClassListFromUrl(self,uUrl:str,oClass) -> List:
        self.oReq = UrlRequest(uUrl, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        dResponse:Dict = self.oReq.result
        if dResponse:
            return [oClass(dItem) for dItem in dResponse]
        return []

    '''
    # Get a code, for the provided function and device (set id)
    # This will use one of a limited number of code requests available for an account in a day.
    def get_code(self, setid, functionname):
        url = self.PrepareUrl(CODE_PATH.format(setid, functionname), {'output':'direct'})
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return IRCode(response_dict)
        return ""
    '''

# Models of objects used/returned by the API.
class cIRDB_Object:
    def __init__(self, dDict:dict = None):
        if dDict:
            for uKey in dDict:
                self.__dict__['u'+uKey]=dDict[uKey]

class cBrand(cIRDB_Object):
    uName:str = '' # Brand Name
    uLinks:List[str] = [] # This is a List, even if it HAS to start with 'u'

    def __str__(self):
        return 'Name:{0:10}'.format(self.uName)

class cType(cIRDB_Object):
    uBrand:str = '' # Brand Name
    uType:str = '' # Device Type

    def __str__(self):
        return 'Brand:{0:10} Type:{1:10}'.format(self.uBrand, self.uType)

class cModel(cIRDB_Object):
    uID:str    = '' # Set ID (this is the setid value to be passed to GetCodeSet, GetFunctions and get_code)
    uBrand:str = '' # Brand Name
    uType:str  = '' # Device Type
    uName:str  = '' # Model Name
    uNotes:str = ''

    def __str__(self):
        return 'Brand:{0:10} Type:{1:10} Name:{2:10} SetID:{3:10} Notes:{4}'.format(self.uBrand, self.uType, self.uName, self.uID, self.uNotes)

class cFunction(cIRDB_Object):
    uSetID:str    = ''
    uFunction:str = '' # Function Name

    def __str__(self):
        return 'SetID:{0:10} Function:{1:10}'.format(self.uSetID, self.uFunction)

class cIRCode(cIRDB_Object):
    uSetID:str    = ''
    uFunction:str = '' # Function Name
    uCode1:str    = '' # First code, in GC format
    uHexCode1:str = '' # First code, in Hexadecimal format (equivalent to Code1 otherwise)
    uCode2:str    = '' # Second code, in GC format, often null
    uHexCode2:str = '' # Second code, in Hexadecimal format, often null
    uType:str     = 'cmd'
    uString:str   = ''

    def __str__(self):
        return 'SetID:{0:10} Function:{1:10}\nCode1:{2}\nCode1(Hex):{3}\nCode2:{4}\nCode2(Hex):{5}'.format(self.uSetID, self.uFunction, self.uCode1, self.uHexCode1, self.uCode2, self.uHexCode2)

class Account(cIRDB_Object):
    uEmail:str = '' # Account email address, must be provided to login
    uPassword:str = '' # Account password, must be provided to login
    uApiKey:str = '' # Api key, used to identify the account on subsequent calls, after having already logged in.

    def __str__(self):
        return 'Email:{0:20} Password:{1:20} ApiKey:{2:20}'.format(self.uEmail, self.uPassword, self.uApiKey)
    def ToData(self)->str:
        return urllib.parse.urlencode({'Email':self.uEmail, 'Password':self.uPassword})

def ITach2CCF(uITACHString:str) -> Tuple[str,str]:
    aArray:List[str]
    uDelimiter:str        = ','
    uFinalString:str      = '0000 ' #0000 denotes CCF type
    iFreqNum:int
    iFreq:int
    iPairData:int
    uTmpString:str
    iTransCount:int
    uTransCount:str
    uRepeatCount      = '0000'
    uITachRepeatCount:str

    aArray = uITACHString.split(uDelimiter)

    if len(aArray) < 6:
        Logger.error ('ITach2CCF: Invalid String (#1)')
        return '',''

    if aArray[3]=='':
        Logger.error ('ITach2CCF: Invalid String (#2)')
        return '',''

    iFreqNum = ToInt(aArray[3])
    if iFreqNum==0:
        Logger.error ('ITach2CCF: Invalid String (#3)')
        return '',''

    #todo Check if iFreq and Itranscount needs to converted to int
    iFreq = int(41450 / (iFreqNum / 100))
    uTmpString='{0:0>4X}'.format(iFreq)             # tmpString = iFreq.ToString('X04')
    iTransCount = int((len(aArray) - 6) / 2)
    uTransCount = '{0:0>4X}'.format(iTransCount)    #iTransCount.ToString('X04');
    uITachRepeatCount = aArray[4]

    uFinalString = uFinalString + uTmpString + ' ' + uRepeatCount + ' ' + uTransCount

    for uElement in aArray[6:]:
        if uElement=='':
            Logger.error ('ITach2CCF: Invalid String (#4)')
            return '',''
        iPairData = ToInt(uElement)
        uTmpString='{0:0>4X}'.format(iPairData)             #iPairData.ToString('X04');
        uFinalString = uFinalString + ' '+ uTmpString

    return uITachRepeatCount,uFinalString

'''
# A simple demonstration run,
class Runner:
    def run(self):
        interface = IRDBInterface()
        interface.login()
        oTypes=interface.GetTypes('Onkyo')
        for oType in oTypes:
            interface.GetModels(oType.Brand, oType.Type)
        interface.logout()
        return
'''


