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


from xml.etree.ElementTree  import ElementTree,tostring, ParseError,Comment


# XMLTreeBuilder has been renamed TreeBuilder, and the API has undergone several changes.

from kivy.uix.boxlayout              import BoxLayout
from kivy.uix.button                 import Button
from kivy.uix.label                  import Label
from kivy.uix.textinput              import TextInput
from kivy.uix.popup                  import Popup
from kivy.uix.screenmanager          import FadeTransition

from ORCA.ui.BasePopup               import SettingSpacer
from ORCA.vars.Replace               import ReplaceVars
from ORCA.widgets.core.FileBrowser   import FileBrowser
from ORCA.utils.RemoveNoClassArgs    import RemoveNoClassArgs
from ORCA.utils.XML                  import CommentedTreeBuilder
import ORCA.Globals as Globals


#__all__ = ['cITachToKeene']

def ToHex(iNumber):
    sTmp="0000"+hex(iNumber)
    sTmp=sTmp.replace('x', '0')
    sTmp=sTmp[-4:]
    return sTmp

def GlobalCacheToCCF(sGCString):

    strArray        = []
    sDelimiter      = ','
    sFinalString    = "0000 "    #0000 denotes CCF type
    iFreqNum        = 0
    iFreq           = 0
    iPairData       = 0
    sTmpString      = ""

    iTransCount     = 0
    sTransCount     = ""
    sRepeatCount    = "0000"

    if sGCString=='':
        return sGCString,1
    if sGCString[0]=='{':
        return sGCString,1

    strArray = sGCString.split(sDelimiter,1024)

    if sGCString=='':
        return '',0
        #("Error: Please enter a valid " + GC2CCF.Properties.Resources.Company + " sendir command.");

    if len(strArray) < 6:
        return '',0
        #return ("Error: Please enter a valid " + GC2CCF.Properties.Resources.Company + " sendir command.");

    if strArray[3]=="":
        return '',0
        #return ("Error: Error parsing data. Please try again.");

    iFreqNum = int(strArray[3])
    iRepeatCount=int(strArray[4])
    #if iRepeatCount>0:
    #    sRepeatCount=ToHex(iRepeatCount)

    if iFreqNum == 0:
        return '',0
        #return ("Error: Error parsing data. Please try again.");

    iFreq = (41450 / (iFreqNum / 100))

    #MessageBox.Show("iFreqNum = " + iFreqNum.ToString() + " iFreq = " + iFreq.ToString());

    sTmpString  = ToHex(iFreq)
    iTransCount = ((len(strArray) - 6) / 2)

    sTransCount = ToHex(iTransCount)

    sFinalString = sFinalString + sTmpString + " " + sRepeatCount + " " + sTransCount

    i=6
    iEnd=len(strArray)
    while i<iEnd:
        if strArray[i]=='':
            return '',0
            #return ("Error: Error parsing data. Please try again.");
        iPairData = int(strArray[i])
        sTmpString = ToHex(iPairData)
        sFinalString = sFinalString + " " + sTmpString
        i=i+1
    return sFinalString,iRepeatCount

def CCfToKeene(sCCFString,iRepeatCount):
    iX          = 0
    iy          = 0
    sTmpStr     = ''
    iFreq       = 0
    iPair_Count = 0
    iLead_in    = 0
    iMyInt      = []
    iTint       = 0
    aBurst_Time = []
    iCycle_time = 0

    if sCCFString=='':
        return sCCFString
    if sCCFString[0]=='{':
        return sCCFString

    sData       = sCCFString.strip()
    iCodeLength = len(sData)
    bError      = True
    try:

        while iX<255:
            aBurst_Time.append(0)
            iX=iX+1

        iX=0
        while iX<iCodeLength:
            sTmpStr = sData[iX: iX + 4]
            aBurst_Time[iy]=int(sTmpStr,16)
            iy=iy+1
            iX=iX+5

        iLast_code = iy / 2
        iFreq = int (4145 / aBurst_Time[1])

        iPair_Count = aBurst_Time[2]
        if iPair_Count == 0:
            iPair_Count = aBurst_Time[3]

        #print "Frequency = " , iFreq
        #print "Pair_count = " , iPair_Count

        iX=0
        while iX<iy:
            iMyInt.append(0)
            iX=iX+1

        iMyInt[0]       = int(iFreq * 256 + iPair_Count)
        iCycle_time     = 1000 / iFreq
        iLead_in        = aBurst_Time[4] * iCycle_time
        iMyInt[1]       = iLead_in
        iMyInt[2]       = aBurst_Time[5] * iCycle_time # lead space
        iPair_Count     = iPair_Count - 1  # only loop data pairs
        iX              = 0
        iEnd            = iPair_Count * 2

        while iX<iEnd:
            iTint = int(aBurst_Time[iX + 6] * iCycle_time)
            iMyInt[iX + 3] = iTint
            iX=iX+1

        iMyInt[iX + 2] = 8192   # over write the lead out space with 2000 X is one over when exits from for loop
        sData = ""

        iX              = 0
        iEnd            = (iPair_Count * 2) + 3
        while iX<iEnd:
            sData = sData + ToHex(iMyInt[iX]) + " "
            iX=iX+1
        bError = False
    except Exception as e:
        sMsg='CCfToKeene:Can''t Convert:'+str(e)
        print (sMsg)
        print (sCCFString)

    if bError:
        return ""
    else:
        sRet="K "+ sData.strip().upper()
        if iRepeatCount>1:
            sRet=sRet+' 4000 '+str(iRepeatCount)
        return sRet


def GlobalCacheToKeene(sGCString):
    sTmp,iRepeatCount=GlobalCacheToCCF(sGCString)
    if sTmp=='' or iRepeatCount==0:
        print ("wrong string:"+sGCString)
    return CCfToKeene(sTmp,iRepeatCount)

class cITachToKeene(BoxLayout):

    def __init__(self, **kwargs):
        kwargs['orientation']='vertical'
        super(cITachToKeene, self).__init__(**RemoveNoClassArgs(kwargs,BoxLayout))
        self.uCodesetFileName    = ''

        self.oContent           = None
        self.oLayoutHeaders     = BoxLayout(size_hint_y= None , height= 30)
        self.oLayoutButtons     = BoxLayout(size_hint_y= None , height= 30)
        self.oLayoutPanels      = BoxLayout()
        self.add_widget(self.oLayoutHeaders)
        self.add_widget(SettingSpacer())
        self.add_widget(self.oLayoutPanels)
        self.add_widget(SettingSpacer())
        self.add_widget(self.oLayoutButtons)

        self.oTextInput=TextInput()
        self.oTextInput2=TextInput()
        self.oLayoutPanels.add_widget(self.oTextInput)
        self.oLayoutPanels.add_widget(self.oTextInput2)

        self.oButtonLoad=Button(text = ReplaceVars('$lvar(563)'))
        self.oButtonSave=Button(text = ReplaceVars('$lvar(5025)'))
        self.oButtonLoad.bind(on_release = self.show_load)
        self.oButtonSave.bind(on_release = self.show_save)
        self.oLayoutButtons.add_widget(self.oButtonLoad)
        self.oLayoutButtons.add_widget(self.oButtonSave)

        self.oLabelITach=Label(text = "ITach", halign='center')
        self.oLabelKeene=Label(text = "Keene Kira", halign='center')
        self.oLayoutHeaders.add_widget(self.oLabelITach)
        self.oLayoutHeaders.add_widget(self.oLabelKeene)


    def show_load(self,*largs):

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

    def MyFilter(self,uFolder,uFile):
        if "CODESET_iTach" in uFile:
            return True
        return False


    def dismiss_popup(self,*largs):
        self._popup.dismiss()

    def load(self,instance):

        if len(instance.selection)!=0:
            self.uCodesetFileName=instance.selection[0]

        try:
            self.oXMLCodeset = ElementTree()
            self.oXMLCodeset.parse(self.uCodesetFileName, CommentedTreeBuilder())

            if self.oXMLCodeset is not None:
                self.oXMLRoot = self.oXMLCodeset.getroot()
                self.oTextInput.text=tostring(self.oXMLRoot)
                for oCode in self.oXMLRoot:
                    sCmd=oCode.get('cmd')
                    if sCmd is not None:
                        oCode.set('cmd',GlobalCacheToKeene(sCmd))
                self.AdjustRepManagerITachToKeene(self.oXMLRoot)
                self.oTextInput2.text=tostring(self.oXMLRoot)
        except ParseError as sErrMsg:
            sMsg='Error '+str(sErrMsg)
            print (sMsg)
        except Exception as e:
            sMsg='Error '+str(e)
            print (sMsg)

        self.dismiss_popup()

    def AdjustRepManagerITachToKeene(self,oXMLRoot):
        oXMLRepMgr=oXMLRoot.find("repositorymanager")
        if oXMLRepMgr is not None:
            oXMLRepMgrEntry=oXMLRepMgr.find("entry")
            if oXMLRepMgrEntry is not None:
                oXMLRepMgrDescriptions=oXMLRepMgrEntry.findall("description")
                if oXMLRepMgrDescriptions is not None:
                    for oDes in oXMLRepMgrDescriptions:
                        oDes.text=oDes.text.replace("iTach IR","Keene Kira IR")
                oXMLRepMgrName=oXMLRepMgrEntry.find("name")
                if oXMLRepMgrName is not None:
                    oXMLRepMgrName.text=oXMLRepMgrName.text.replace("iTach","Keene Kira")
                oXMLRepMgrDependencies=oXMLRepMgrEntry.findall("dependencies")
                if oXMLRepMgrDependencies is not None:
                    for oDep in oXMLRepMgrDependencies:
                        oDEDep=oDep.find("dependency")
                        if oDEDep is not None:
                            oName=oDEDep.find("name")
                            if oName is not None:
                                oName.text=oName.text.replace("iTach IR Control","Keene Kira IR Control")
                oXMLRepMgSources=oXMLRepMgrEntry.findall("sources")
                if oXMLRepMgSources is not None:
                    oXMLRepMgSource=oXMLRepMgSources.find("source")
                    if oXMLRepMgSource is not None:
                        for oSource in oXMLRepMgSource:
                            oSource.text=oSource.text.replace("_iTach_","_Keene_Kira_")

    def AdjustRepManagerITachToCCF(self,oXMLRoot):
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


    def show_save(self,*largs):
        if self.oTextInput2.text!="":
            sOutput=self.uCodesetFileName+"3"
            sOutput=sOutput.replace("_iTach_","_Keene_Kira_")
            self.oXMLCodeset.write(sOutput, encoding="UTF-8",xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')
        self.oTextInput.text=""
        self.oTextInput2.text=""

