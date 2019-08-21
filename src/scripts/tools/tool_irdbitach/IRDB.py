# -*- coding: utf-8 -*-
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

from xml.etree.ElementTree  import ElementTree,ParseError, Element, SubElement, fromstring
from time import sleep
import urllib

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
from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.Cookies           import Var_Load, Var_Save
from ORCA.ui.BasePopup      import cBasePopup,SettingSpacer



import ORCA.Globals as Globals

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
        self.oXMLText=TextInput(text=oDBSelector.sXML)
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

    def On_Save(self, instance):
        """ saves the Codeset file """
        try:
            oRoot = ElementTree(fromstring(self.oXMLText.text))
            oFilename=cFileName(Globals.oPathCodesets) +  oDBSelector.oCodesetName.text
            oRoot.write(oFilename.string, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        except Exception as e:
            uMsg=LogError(u'IRDB: Error Writing iTach codeset file',e)
            ShowErrorPopUp(uMessage=uMsg)
        self.oPopup.dismiss()

class cITachIRDB_Selector(cBasePopup):
    """ Class to select an IRDb item """

    def __init__(self):
        super(cITachIRDB_Selector,self).__init__()
        self.fktCallBack=None
        self.oPopup=None

    def Start(self,uTitle,aOptions,fktCallBack):
        """ starts selection """
        self.fktCallBack=fktCallBack
        # create the popup
        content         = GridLayout(cols=1, spacing='5dp')
        scrollview      = ScrollView( do_scroll_x=False, bar_width='10dp',scroll_type=['bars','content'] )
        scrollcontent   = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
        scrollcontent.bind(minimum_height=scrollcontent.setter('height'))
        self.oPopup   = popup = Popup(content=content, title=ReplaceVars(uTitle), size_hint=(0.5, 0.9),  auto_dismiss=False)

        #we need to open the popup first to get the metrics
        popup.open()
        #Add some space on top
        content.add_widget(Widget(size_hint_y=None, height=dp(2)))
        # add all the options
        for option in aOptions:
            if hasattr(option,"Name"):
                name=option.Name
            else:
                name=option.Type
            btn = Button(text=name, size=(popup.width, dp(30)), size_hint=(None, None))
            btn.bind(on_release=self.On_Value)
            btn.oDBRef=option
            scrollcontent.add_widget(btn)

        # finally, add a cancel button
        scrollview.add_widget(scrollcontent)
        content.add_widget(scrollview)
        content.add_widget(SettingSpacer())
        btn = Button(text=ReplaceVars('$lvar(5009)'), size=(popup.width, dp(50)),size_hint=(0.9, None))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

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

        self.aBrands         = []
        self.aModels         = []
        self.aTypes          = []
        self.bStopWait       = False
        self.bStopWait       = False
        self.dTranslations   = {}
        self.IRDBInterface   = None
        self.oBrandsSelector = None
        self.oBtnBrands      = None
        self.oBtnModels      = None
        self.oBtnTypes       = None
        self.oCodesetName    = None
        self.oOptionOptimizeChannelSelect = None
        self.oOptionWriteCCF = None
        self.oOptionWriteITach = None
        self.oProgressBar    = None
        self.oSelector       = None
        self.oTextBrands     = None
        self.oTextModels     = None
        self.oTextModels     = None
        self.oTextTypes      = None
        self.oTextTypes      = None
        self.uHost           = u''
        self.uOldBrand       = u''
        self.uOldModel       = u''
        self.uOldType        = u''
        self.uPassword       = u''
        self.uUser           = u''

    def ConvertItach2CCF(self):
        #todo : remove when we know, it is not used anymore
        from ORCA.utils.XML import GetXMLTextAttribute
        import codecs
        aFiles=Globals.oPathCodesets.GetFolderList()
        aFiles2=[]
        for uFile in aFiles:
            if uFile.startswith("CODESET_iTach_"):
                aFiles2.append(uFile)

        for uFile in aFiles2:
            oFile= cFileName(Globals.oPathCodesets) + uFile
            oXMLCodeset = ElementTree(file=oFile.string).getroot()
            oXMLCodes=oXMLCodeset.findall('code')
            for oXMLCode in oXMLCodes:
                uCmd = GetXMLTextAttribute(oXMLCode,"cmd",False,"")
                if uCmd.startswith("sendir,"):
                    uRepeat,uCmd=ITach2CCF(uCmd)
                    oXMLCode.set("cmd_ccf", uCmd)
                    oXMLCode.set("repeatcount", uRepeat)
                    del oXMLCode.attrib["cmd"]
            uFileName=oFile.string.replace("_iTach_","_infrared_ccf_")
            uFinal=ToUnicode(XMLPrettify(oXMLCodeset))
            uFinal=uFinal.replace(u'<?xml version="1.0"?>',u'<?xml version="1.0" encoding="UTF-8"?>')
            with codecs.open(uFileName, 'w', 'utf-8') as outfile:
                outfile.write(uFinal)

    def Start(self,uHost,uUser,uPassword):

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

        if self.uUser == u'' or self.uPassword == u'':
            oContent.add_widget(SettingSpacer())
            oContent.add_widget(Label(text=ReplaceVars("$lvar(SCRIPT_TOOLS_IRDBITACH_5)"),height='20dp', size_hint_y=None))

        LOGIN_EMAIL = uUser
        PASSWORD    = uPassword

        oContent.add_widget(SettingSpacer())
        self.oCodesetName = TextInput(height='20dp')
        oContent.add_widget(self.oCodesetName)
        oContent.add_widget(SettingSpacer())

        oContentWriteCCF = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionWriteCCF = CheckBox(active=True)
        oContentWriteCCF.add_widget(Label(text=ReplaceVars("$lvar(SCRIPT_TOOLS_IRDBITACH_9)"),height='20dp', size_hint_y=None, halign='left'))
        oContentWriteCCF.add_widget(self.oOptionWriteCCF)
        oContent.add_widget(oContentWriteCCF)

        oContentWriteITach = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionWriteITach = CheckBox()
        oContentWriteITach.add_widget(Label(text=ReplaceVars("$lvar(SCRIPT_TOOLS_IRDBITACH_10)"),height='20dp', size_hint_y=None, halign='left'))
        oContentWriteITach.add_widget(self.oOptionWriteITach)
        oContent.add_widget(oContentWriteITach)

        oContentOptimizeChannelSelect = BoxLayout(orientation='horizontal', spacing='5dp', height='20dp',size_hint_y=None)
        self.oOptionOptimizeChannelSelect = CheckBox()
        oContentOptimizeChannelSelect.add_widget(Label(text=ReplaceVars("$lvar(SCRIPT_TOOLS_IRDBITACH_11)"),height='20dp', size_hint_y=None, halign='left'))
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

    def CreateCodesetFileName(self):
        """ Creates the filename of a codset file """
        sInterface="XXXXX"
        sText="CODESET_%s_%s_%s_%s.xml" %(sInterface,self.oTextBrands.text,self.oTextTypes.text,self.oTextModels.text)

        sText=self.remove(sText, '\\/:*?"<>|')
        self.oCodesetName.text=sText

    def remove(self,value, deletechars):
        """ deletes invalid characters from a filename """
        for c in deletechars:
            value = value.replace(c,'-')
        return value

    def GetProperName(self,uURL):
        """ adjust url to valid characters used by irdb """
        uRet=uURL['Href']
        iPos=uRet.rfind("/")
        if not iPos==-1:
            uRet=uRet[iPos+1:]
            uRet=uRet.replace('%20',' ')
        return uRet

    def On_BtnBrands(self,instance):
        """ After the brands button has been pressed """
        if self.oBrandsSelector is None:
            self.oProgressBar.Show("$lvar(SCRIPT_TOOLS_IRDBITACH_6)","$lvar(SCRIPT_TOOLS_IRDBITACH_12)",0)
        Clock.schedule_once(self.On_BtnBrands_Load,0)


    def On_BtnBrands_Load(self,*largs):
        """ Loads all brands """
        try:
            if len(self.aBrands)==0:
                self.IRDBInterface = IRDBInterface()
                self.IRDBInterface.login()
                self.aBrands = self.IRDBInterface.get_brands()
                self.IRDBInterface.logout()

            if self.oBrandsSelector is None:
                self.oBrandsSelector=cITachIRDB_Selector()
                self.oProgressBar.ClosePopup()
                self.oBrandsSelector.Start("$lvar(SCRIPT_TOOLS_IRDBITACH_7)",self.aBrands,self.On_BtnBrandsSelected)
            else:
                self.oBrandsSelector.Show()
        except Exception as e:
            uMsg=LogError(u"Can''t load brands",e)
            ShowErrorPopUp(uMessage=uMsg)
            self.aBrands = []
            self.oProgressBar.ClosePopup()

    def On_BtnBrandsSelected(self,instance):
        """ handles, if the user has selected a brand """
        self.oTextBrands.text=instance.text
        self.oTextTypes.text=''
        self.oTextModels.text=''
        self.CreateCodesetFileName()
        self.oBtnBrands.oDBRef=instance.oDBRef

    def On_BtnTypes(self,instance):
        """ After the types button has been pressed """
        try:
            if self.oTextBrands.text!='':
                if self.uOldBrand!=self.oTextBrands.text:
                    sBrand=self.GetProperName(self.oBtnBrands.oDBRef.Links[0])
                    self.IRDBInterface.login()
                    self.aTypes = self.IRDBInterface.get_types(sBrand)
                    self.IRDBInterface.logout()
                    self.uOldBrand=self.oTextBrands.text

                self.oSelector=cITachIRDB_Selector()
                self.oSelector.Start("$lvar(668)",self.aTypes,self.On_BtnTypesSelected)
        except Exception as e:
            uMsg=LogError(u"Can''t load types",e)
            ShowErrorPopUp(uMessage=uMsg)
            self.aTypes = []

    def On_BtnTypesSelected(self,instance):
        """ handles, if the user has selected a Type """
        self.oTextTypes.text=instance.text
        self.oTextModels.text=''
        self.oBtnTypes.oDBRef=instance.oDBRef
        self.CreateCodesetFileName()

    def On_BtnModels(self,instance):
        """ After the Models button has been pressed """
        try:
            if self.oTextTypes.text!='':
                if self.uOldType!=self.oTextTypes.text:
                    uBrand=self.GetProperName(self.oBtnBrands.oDBRef.Links[0])
                    uType=self.GetProperName(self.oBtnTypes.oDBRef.Links[0])
                    self.IRDBInterface.login()
                    self.aModels = self.IRDBInterface.get_models(uBrand,uType)
                    self.IRDBInterface.logout()
                    self.uOldType=self.oTextTypes.text
                self.oSelector=cITachIRDB_Selector()
                self.oSelector.Start("$lvar(SCRIPT_TOOLS_IRDBITACH_8)",self.aModels,self.On_BtnModelsSelected)
        except Exception as e:
            uMsg=LogError(u"Can''t load models",e)
            ShowErrorPopUp(uMessage=uMsg)
            self.aModels = []


    def On_BtnModelsSelected(self,instance):
        """ handles, if the user has selected a Model """
        self.oBtnModels.oDBRef=instance.oDBRef
        self.oTextModels.text=instance.text
        self.CreateCodesetFileName()

    def On_BtnLoad(self,instance):
        """ Loads the IRDB commands from the current selection """
        if self.oTextModels.text!='':

            try:
                self.ReadItachFunctionTranslation()
                uID=self.oBtnModels.oDBRef.ID
                self.IRDBInterface.login()
                aCodeSets=self.IRDBInterface.get_codeset(uID)
                self.IRDBInterface.logout()
                for oCodeSet in aCodeSets:
                    oCodeSet.string=oCodeSet.string
                    uTransName=self.dTranslations.get(oCodeSet.Function)
                    if uTransName is not None:
                        oCodeSet.Function=uTransName
                    else:
                        Logger.debug("Unmatch IR Command:"+oCodeSet.Function)
                self.AddStandardCodes(aCodeSets)
                if self.oOptionWriteITach.active:
                    self.Save_As_iTach(aCodeSets)
                if self.oOptionWriteCCF.active:
                    self.Save_As_CCF(aCodeSets)
                self.oPopup.dismiss()
            except Exception as e:
                uMsg=LogError(u"Can''t load functions",e)
                ShowErrorPopUp(uMessage=uMsg)

    def AddStandardCodes(self,oSet):

        bHasPowerOn      = False
        bHasPowerOff     = False
        bHasPowerToggle  = False
        bHasKey          = False

        for oFunction in oSet:
            if oFunction.Function=='power_on':
                bHasPowerOn      = True
            if oFunction.Function=='power_off':
                bHasPowerOff      = True
            if oFunction.Function=='power_toggle':
                bHasPowerToggle      = True
            if oFunction.Function.startswith('key_'):
                bHasKey=True

        if bHasKey:
            if self.oOptionOptimizeChannelSelect.active==False or True:
                oSingleSet=IRCode()
                oSingleSet.Code1='{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}'
                oSingleSet.Function = 'channel_select'
                oSet.append(oSingleSet)
            else:
                # todo: set the optimisation substructure
                oSingleSet=IRCode()
                oSingleSet.Code1="NEWCHILD"
                oSet.append(oSingleSet)
                oSingleSet=IRCode()
                oSingleSet.Code1='{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}'
                oSingleSet.Function = 'channel_select_pre'
                oSet.append(oSingleSet)
                oSingleSet=IRCode()
                oSingleSet.Code1='key_ok'
                oSingleSet.uType='alias'
                oSingleSet.uString=""
                oSingleSet.uPreAction="channel_select_pre"
                oSingleSet.Function = 'channel_select'
                oSet.append(oSingleSet)
                oSingleSet=IRCode()
                oSingleSet.Code1="LEAVECHILD"

        if not bHasPowerOn and bHasPowerToggle:
            oSingleSet=IRCode()
            oSingleSet.Function = 'power_on'
            oSingleSet.Code1='power_toggle'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)

        if not bHasPowerOff and bHasPowerToggle:
            oSingleSet=IRCode()
            oSingleSet.Function = 'power_off'
            oSingleSet.Code1='power_toggle'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)

        if not bHasPowerToggle and bHasPowerOn:
            oSingleSet=IRCode()
            oSingleSet.Function = 'power_toggle'
            oSingleSet.Code1='power_on'
            oSingleSet.uType='alias'
            oSet.append(oSingleSet)


    def ReadItachFunctionTranslation(self):
        """ Reads the translation set from IRDB to ORCA """
        if len(self.dTranslations)==0:
            oFnTranslation=cFileName(Globals.oPathResources + u"irdbtranslation") + u"itach2orca.xml"
            try:
                Logger.debug (u'IRDB: Loading Translation Table:'+oFnTranslation.string)
                oET_Root = ElementTree(file=oFnTranslation.string).getroot()
                #oSets=oET_Root.findall('set')
                for oSet in oET_Root:
                    oCommands=oSet.findall('action')
                    for oCommand in oCommands:
                        uFrom = GetXMLTextAttribute(oCommand,u'from',True,'')
                        uTo = GetXMLTextAttribute(oCommand,u'to',True,'')
                        self.dTranslations[uFrom]=uTo

            except ParseError as e:
                uMsg=LogError(u'IRDB: Error:Loading Translations file',e)
                ShowErrorPopUp(uMessage=uMsg)

    ''' Todo : check / remove '''
    def Save_As_iTach(self,oSet):
        uFilename=Globals.oPathCodesets.string + "/iTach/" + self.oCodesetName.text
        oFilename=cFileName().ImportFullPath(uFilename.replace("_XXXXX_","_iTach_"))
        try:
            oRoot = Element("codeset")
            for oFunction in oSet:
                oCodesetCode = SubElement(oRoot, "action")
                oCodesetCode.set("string", "codeset")
                oCodesetCode.set("name", oFunction.Function)
                oCodesetCode.set("type", oFunction.uType)
                uString=oFunction.Code1.replace("sendir,1:1,","sendir,$cvar(CONFIG_MODULE):$cvar(CONFIG_CONNECTOR),")
                uString=uString.replace("\n","")
                uString=uString.replace("\r","")
                oCodesetCode.set("cmd", uString)
            uFinal=XMLPrettify(oRoot)
            uFinal=uFinal.replace('<?xml version="1.0"?>','<?xml version="1.0" encoding="UTF-8"?>')
            oFile = open(oFilename.string, 'w')
            oFile.write(uFinal)
            oFile.close()
            #oTree = ElementTree(oRoot)
            #oTree.write(uFilename, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        except Exception as e:
            uMsg=LogError(u'IRDB: Error Writing iTach codeset file',e)
            ShowErrorPopUp(uMessage=uMsg)

    def Save_As_CCF(self,oSet):
        uFilename=Globals.oPathCodesets.string + "/infrared_ccf/" + self.oCodesetName.text
        oFn=cFileName().ImportFullPath(uFilename.replace("_XXXXX_","_infrared_ccf_"))
        try:
            oRoot = Element("codeset")
            oRootToUse=oRoot
            for oFunction in oSet:
                if oFunction.Code1=='NEWCHILD':
                    oCodesetCode = SubElement(oRootToUse, "action")
                    oCodesetCode.set("name", oFunction.Function)
                    oRootToUse=oCodesetCode
                elif oFunction.Code1=='LEAVECHILD':
                    oRootToUse=oRoot
                else:
                    oCodesetCode = SubElement(oRootToUse, "action")
                    oCodesetCode.set("name", oFunction.Function)
                    if oFunction.uType!="alias":
                        if oFunction.string!=u'':
                            oCodesetCode.set("string", oFunction.string)
                    if oFunction.uType!=u'':
                        oCodesetCode.set("type", oFunction.uType)
                    if oFunction.uType=="cmd" and not "REPEAT" in oFunction.Code1:
                        uRepeat,uString=ITach2CCF(oFunction.Code1)
                        uString=uString.replace("\n","")
                        uString=uString.replace("\r","")
                        oCodesetCode.set("cmd_ccf", uString)
                        oCodesetCode.set("repeatcount",uRepeat)
                    else:
                        if oFunction.Code1!='':
                            oCodesetCode.set("cmd", oFunction.Code1)
            uFinal=XMLPrettify(oRoot)
            uFinal=uFinal.replace('<?xml version="1.0"? >','<?xml version="1.0" encoding="UTF-8"?>')
            uFinal=uFinal.replace('{&amp;REPEAT&amp;:{&amp;REPEATCMD&amp;:&amp;key_&amp;,&amp;REPEATVAR&amp;:&amp;$cvar(CHANNELNUM)&amp;}}','{"REPEAT":{"REPEATCMD":"key_","REPEATVAR":"$cvar(CHANNELNUM)"}}')
            oFile = open(oFn.string, 'w')
            oFile.write(uFinal)
            oFile.close()
            #oTree = ElementTree(oRoot)
            #oTree.write(uFilename, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        except Exception as e:
            uMsg=LogError(u'IRDB: Error Writing CCF codeset file',e)
            ShowErrorPopUp(uMessage=uMsg)


    def Save_As_iTachNew(self,oSet):
        """ Saves the IRDB codes as iTach codeset file """
        ''' Unused as editor is WIP '''
        try:
            oRoot = Element("codeset")
            for oFunction in oSet:
                oCodesetCode = SubElement(oRoot, "action")
                oCodesetCode.set("name", oFunction.Function)
                if oFunction.uType!="alias":
                    oCodesetCode.set("string","codeset")
                oCodesetCode.set("type", "string")
                uString=oFunction.Code1.replace("sendir,1:1,","sendir,$cvar(CONFIG_MODULE):$cvar(CONFIG_CONNECTOR),")
                oCodesetCode.set("cmd", uString)
            self.oITachIRDB_Editor=cITachIRDB_Editor()
            self.oITachIRDB_Editor.Start()
        except Exception as e:
            uMsg=LogError(u'IRDB: Error Writing iTach codeset file',e)
            ShowErrorPopUp(uMessage=uMsg)

oDBSelector      = ITachIRDB()

def ShowITachIRDB(uHost,uUser,uPassword):
    """ Main class to get the Itach IR database codes """
    oDBSelector.Start(uHost,uUser,uPassword)
    return oDBSelector


CONTENT_TYPE = "application/json;charset=utf-8"

# API Paths
BRANDS_PATH    = "api/brands"
TYPES_PATH     = "api/brands/{0}/types"
MODELS_PATH    = "api/brands/{0}/types/{1}/models"
LOGIN_PATH     = "api/account/login"
LOGOUT_PATH    = "api/account/logout"
CODESET_PATH   = "api/codesets/{0}"
FUNCTIONS_PATH = "api/codesets/{0}/functions"
CODE_PATH      = "api/codesets/{0}/functions/{1}/codes"
HEADERS        = {'Content-type': 'application/x-www-form-urlencoded',  'Accept': 'text/plain'}

class IRDBInterface(object):
    def __init__(self):
        self.oReq = None
        self.oAccount = None

    # Call to add an api key to a url, as well as other params if they are provided
    def prepare_url(self, path, params = None):
        if self.oAccount:
            url = oDBSelector.uHost + path + '?apikey=' + self.oAccount.ApiKey
            if params:
                for key, value in params.items():
                    url += '&{}={}'.format(key, value)
            return url
        return u''
    # Login, and save the account information provided (the api key particularly)
    # This must be called first.
    def login(self):
        url                     = oDBSelector.uHost + LOGIN_PATH
        SetVar(uVarName         = 'ITach_Mail', oVarValue = oDBSelector.uUser)
        SetVar(uVarName         = 'ITach_Password', oVarValue = oDBSelector.uPassword)
        login_account           = Account()
        login_account.Email     = oDBSelector.uUser
        login_account.Password  = oDBSelector.uPassword

        self.oReq = UrlRequest(url,  req_body=login_account.ToData(), req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        aResponse = self.oReq.result
        if aResponse:
            self.oAccount = Account(aResponse['Account'])

    def OnError(self,request,error):
        self.bStopWait      = True

    def NewWait(self,delay):
        self.bStopWait=False

        while self.oReq.resp_status is None:
            self.oReq._dispatch_result(delay)
            sleep(delay)
            if self.bStopWait:
                self.bStopWait=False
                break

    # Logout.  The apikey is used to identify the account, which is added by prepare_url
    def logout(self):
        url = self.prepare_url(LOGOUT_PATH)
        UrlRequest(url, req_headers=HEADERS)
        self.oAccount = None
    # Get a list of all available brands
    def get_brands(self):
        url = self.prepare_url(BRANDS_PATH)
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return  [Brand(brand_dict) for brand_dict in response_dict]
        return []


    # Get a list of all device types available for the given brand
    def get_types(self, brandname):
        url = self.prepare_url(TYPES_PATH.format(brandname))
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return [Type(type_dict) for type_dict in response_dict]
        return []
    # Get a list of all models for the given brand and type

    def get_models(self, brandname, typename):

        brandname=urllib.quote(brandname,safe="")
        typename=urllib.quote(typename,safe="")
        url = self.prepare_url(MODELS_PATH.format(brandname, typename))
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return [Model(model_dict) for model_dict in response_dict]
        return []

    # Get a full set of codes for devices with the provided set id.
    # This will use one of a limited number of code requests available for an account in a day.
    def get_codeset(self, setid):
        url = self.prepare_url(CODESET_PATH.format(setid), {'output':'direct'})
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return [IRCode(code_dict) for code_dict in response_dict]
        return []
    # Get a list of functions available for devices with the provided set id.
    def get_functions(self, setid):
        url = self.prepare_url(FUNCTIONS_PATH.format(setid))
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return [Function(function_dict) for function_dict in response_dict]
        return []

    # Get a code, for the provided function and device (set id)
    # This will use one of a limited number of code requests available for an account in a day.
    def get_code(self, setid, functionname):
        url = self.prepare_url(CODE_PATH.format(setid, functionname), {'output':'direct'})
        self.oReq = UrlRequest(url, req_headers=HEADERS,on_failure=self.OnError,on_error=self.OnError)
        self.NewWait(0.05)
        response_dict = self.oReq.result
        if response_dict:
            return IRCode(response_dict)
        return ""

# Models of objects used/returned by the API.
class IRDB_Object(object):
    def __init__(self, object_dict = None):
        if object_dict:
            self.__dict__.update(object_dict)

class Brand(IRDB_Object):
    Name = '' # Brand Name
    def __str__(self):
        return "Name:{0:10}".format(self.Name)

class Type(IRDB_Object):
    Brand = '' # Brand Name
    Type = '' # Device Type

    def __str__(self):
        return "Brand:{0:10} Type:{1:10}".format(self.Brand, self.Type)

class Model(IRDB_Object):
    ID    = '' # Set ID (this is the setid value to be passed to get_codeset, get_functions and get_code)
    Brand = '' # Brand Name
    Type  = '' # Device Type
    Name  = '' # Model Name
    Notes = ''

    def __str__(self):
        return "Brand:{0:10} Type:{1:10} Name:{2:10} SetID:{3:10} Notes:{4}".format(self.Brand, self.Type, self.Name, self.ID, self.Notes)

class Function(IRDB_Object):
    SetID    = ''
    Function = '' # Function Name

    def __str__(self):
        return "SetID:{0:10} Function:{1:10}".format(self.SetID, self.Function)

class IRCode(IRDB_Object):
    SetID    = ''
    Function = '' # Function Name
    Code1    = '' # First code, in GC format
    HexCode1 = '' # First code, in Hexadecimal format (equivalent to Code1 otherwise)
    Code2    = '' # Second code, in GC format, often null
    HexCode2 = '' # Second code, in Hexadecimal format, often null
    uType    = 'cmd'
    string   = u''

    def __str__(self):
        return "SetID:{0:10} Function:{1:10}\nCode1:{2}\nCode1(Hex):{3}\nCode2:{4}\nCode2(Hex):{5}".format(self.SetID, self.Function, self.Code1, self.HexCode1, self.Code2, self.HexCode2)

class Account(IRDB_Object):
    Email = '' # Account email address, must be provided to login
    Password = '' # Account password, must be provided to login
    ApiKey = '' # Api key, used to identify the account on subsequent calls, after having already logged in.

    def __str__(self):
        return "Email:{0:20} Password:{1:20} ApiKey:{2:20}".format(self.Email, self.Password, self.ApiKey)
    def ToData(self):
        #uRet= urllib.urlencode({"Email":LOGIN_EMAIL, "Password":PASSWORD})
        return urllib.urlencode({"Email":self.Email, "Password":self.Password})


def ITach2CCF(uITACHString):
    aArray            = []
    uDelimiter        = u','
    uFinalString      = u"0000 " #0000 denotes CCF type
    iFreqNum          = 0
    iFreq             = 0
    iPairData         = 0
    uTmpString        = u""
    iTransCount       = 0
    uTransCount       = u""
    uRepeatCount      = u"0000"
    uITachRepeatCount = 0

    aArray = uITACHString.split(uDelimiter)

    if len(aArray) < 6:
        Logger.error (u'ITach2CCF: Invalid String (#1)')
        return u''

    if aArray[3]=="":
        Logger.error (u'ITach2CCF: Invalid String (#2)')
        return u''

    iFreqNum = ToInt(aArray[3])
    if iFreqNum==0:
        Logger.error (u'ITach2CCF: Invalid String (#3)')
        return u''

    #todo Check if iFreq and Itranscount needs to converted to int
    iFreq = (41450 / (iFreqNum / 100))
    uTmpString='{0:0>4X}'.format(iFreq)             # tmpString = iFreq.ToString("X04")
    iTransCount = int((len(aArray) - 6) / 2)
    uTransCount = '{0:0>4X}'.format(iTransCount)    #iTransCount.ToString("X04");
    uITachRepeatCount = aArray[4]

    uFinalString = uFinalString + uTmpString + " " + uRepeatCount + " " + uTransCount

    for uElement in aArray[6:]:
        if uElement=="":
            Logger.error (u'ITach2CCF: Invalid String (#4)')
            return u''
        iPairData = ToInt(uElement)
        uTmpString='{0:0>4X}'.format(iPairData)             #iPairData.ToString("X04");
        uFinalString = uFinalString + " "+ uTmpString

    return uITachRepeatCount,uFinalString

'''
# A simple demonstration run,
class Runner:
    def run(self):
        interface = IRDBInterface()
        interface.login()
        oTypes=interface.get_types('Onkyo')
        for oType in oTypes:
            interface.get_models(oType.Brand, oType.Type)
        interface.logout()
        return
'''


