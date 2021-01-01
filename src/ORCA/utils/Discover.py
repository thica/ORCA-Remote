# -*- coding: utf-8 -*-
"""
    ORCA Open Remote Control Application
    Copyright (C) 2013-2020  Carsten Thielepape
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

from typing import List
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

import threading

from dataclasses            import dataclass
from dataclasses            import field

from kivy.uix.popup         import Popup
from kivy.uix.gridlayout    import GridLayout
from kivy.uix.stacklayout   import StackLayout
from kivy.uix.button        import Button
from kivy.uix.widget        import Widget
from kivy.uix.scrollview    import ScrollView
from kivy.metrics           import dp
from kivy.clock             import Clock
from ORCA.vars.Replace      import ReplaceVars
from ORCA.widgets.core.Label import cLabel
from ORCA.ui.BasePopup      import cBasePopup,SettingSpacer
from ORCA.utils.LogError    import LogError
from ORCA.vars.QueryDict    import TypedQueryDict


import ORCA.Globals as Globals

if TYPE_CHECKING:
    from ORCA.scripttemplates.Template_Discover import cDiscoverScriptTemplate
else:
    from typing import TypeVar
    cDiscoverScriptTemplate = TypeVar("cDiscoverScriptTemplate")

__all__ = ['cDiscover_List']

class cDiscoverScriptStatus():
    def __init__(self):
        self.uScriptName:str                            = u""
        self.uScriptTitle:str                           = u""
        self.uScriptStatus:str                          = u""
        self.oScript:Optional[cDiscoverScriptTemplate]  = None
        self.oGrid:Optional[GridLayout]                 = None
        self.aScriptContentLineText:List[List[str]]     = []
        self.aScriptContentLineDevice:List[TypedQueryDict] = []

class cDiscover_List(cBasePopup):
    """ creates a list of all discover results from all scripts """

    def __init__(self):
        self.oScrollContent:StackLayout                 = StackLayout(size_hint=(None, None))
        self.dScripts:Dict[str,cDiscoverScriptStatus]   = {}
        self.iHashStarted:int                           = 0
        self.iHashEnded:int                             = 0
        self.iHashFound:int                             = 0
        self.aThreads:List[threading.Thread]            = []
        self.oDiscoverListWaitLock:Lock                 = threading.Lock()
        self.uScriptTitle:str                           = u""
        self.oTimerUpdate:Optional[Clock.TimerEvent]    = None
        super().__init__()

    def ShowList(self):
        """ Shows the discover results """
        try:
            # create the popup
            oScrollContentSingle:GridLayout
            oContent:GridLayout
            oScrollview:ScrollView
            uDiscoverScriptName:str
            aDiscoverScripts:List[str]
            uDiscoverScriptName:str
            oThread:cThread_Discover

            self.iHashStarted   = Globals.oNotifications.RegisterNotification(uNotification="DISCOVER_SCRIPTSTARTED",   fNotifyFunction=self.NotificationHandler_ScriptStarted,   uDescription="Notification list discovery started")
            self.iHashEnded     = Globals.oNotifications.RegisterNotification(uNotification="DISCOVER_SCRIPTENDED",     fNotifyFunction=self.NotificationHandler_ScriptEnded,     uDescription="Notification list discovery ended")
            self.iHashFound     = Globals.oNotifications.RegisterNotification(uNotification="DISCOVER_SCRIPTFOUND",     fNotifyFunction=self.NotificationHandler_ScriptFoundItem, uDescription="Notification list discovery found item")

            oContent               = GridLayout(cols=1, spacing='5dp')
            oScrollview            = ScrollView( do_scroll_x=False)
            self.oPopup:Popup      = Popup(content=oContent, title=ReplaceVars('$lvar(5028)'), size_hint=(0.9, 0.9),  auto_dismiss=False)

            #we need to open the popup first to get the metrics
            self.oPopup.open()
            #Add some space on top
            oContent.add_widget(Widget(size_hint_y=None, height=dp(2)))
            aDiscoverScripts = Globals.oScripts.GetScriptListForScriptType("DEVICE_DISCOVER")
            for uDiscoverScriptName in aDiscoverScripts:
                # if uDiscoverScriptName == u"discover_eiscp" or uDiscoverScriptName == u"discover_kira" or uDiscoverScriptName == u"discover_elvmax" or uDiscoverScriptName == u"discover_enigma" or uDiscoverScriptName==u"discover_upnp":
                #if uDiscoverScriptName == u"discover_kira":
                if True:
                    oScrollContentSingle= GridLayout(size_hint=(None, None),size=(self.oPopup.width, dp(10)))
                    oScrollContentSingle.bind(minimum_height=oScrollContentSingle.setter('height'))
                    oThread = cThread_Discover(uScriptName=uDiscoverScriptName,dParKwArgs={'createlist':1,'oGrid':oScrollContentSingle})
                    self.aThreads.append(oThread)
                    self.aThreads[-1].start()

            # finally, add a cancel button to return on the previous panel
            oScrollview.add_widget(self.oScrollContent)
            oContent.add_widget(oScrollview)
            oContent.add_widget(SettingSpacer())

            oBtn: Button = Button(text=ReplaceVars('$lvar(5000)'), size=(self.oPopup.width, dp(50)),size_hint=(1, None))
            oBtn.bind(on_release=self.On_Cancel)
            oContent.add_widget(oBtn)

            #resize the Scrollcontent to fit to all childs. Needs to be done, after the popup has been shown
            Clock.schedule_once(self.SetScrollSize, 0)
            self.oTimerUpdate = Clock.schedule_interval(self.UpdateResults, 2)
        except Exception as e:
            LogError(uMsg="Critical error string discover scripts",oException=e)


     # noinspection PyUnusedLocal
    def SetScrollSize(self, *args):
        """  Sets the size of the scroll window of the results """
        iHeight: int = 0
        for oChild in self.oScrollContent.children:
            if hasattr(oChild,"minimum_height"):
                iHeight = iHeight+oChild.minimum_height
            else:
                iHeight = iHeight+oChild.height
        self.oScrollContent.size=(self.oPopup.width,iHeight)

    # noinspection PyUnusedLocal
    def On_Cancel(self,oButton):
        """ call handler for abort """
        Globals.oNotifications.UnRegisterNotification_ByHash(iHash=self.iHashStarted)
        Globals.oNotifications.UnRegisterNotification_ByHash(iHash=self.iHashEnded)
        Globals.oNotifications.UnRegisterNotification_ByHash(iHash=self.iHashFound)
        cBasePopup.ClosePopup(self)

    def ClosePopup(self):
        """ will be called by keyhandler, if esc has been pressed """
        self.On_Cancel(self)

    def NotificationHandler_ScriptStarted(self,*args,**kwargs) -> None:
        try:
            self.oDiscoverListWaitLock.acquire()
            oDiscoverScriptStatus:cDiscoverScriptStatus = cDiscoverScriptStatus()
            oDiscoverScriptStatus.uScriptName   = kwargs.get("scriptname")
            oDiscoverScriptStatus.uScriptTitle  = kwargs.get("scripttitle")
            oDiscoverScriptStatus.uScriptStatus = kwargs.get("scriptstatus")
            oDiscoverScriptStatus.oScript       = kwargs.get("script")
            oDiscoverScriptStatus.oGrid         = kwargs.get("grid")
            self.dScripts[oDiscoverScriptStatus.uScriptName] = oDiscoverScriptStatus
            self.oDiscoverListWaitLock.release()
            self.UpdateResults()
        except Exception as e:
            LogError(uMsg="Error on Script started message handler",oException=e)
        return

    def NotificationHandler_ScriptEnded(self,*args,**kwargs) -> None:
        oDiscoverScriptStatus:cDiscoverScriptStatus
        uScriptname:str
        try:
            self.oDiscoverListWaitLock.acquire()
            uScriptName                         = kwargs.get("scriptname")
            oDiscoverScriptStatus               = self.dScripts[uScriptName]
            oDiscoverScriptStatus.uScriptStatus = kwargs.get("scriptstatus")
            self.oDiscoverListWaitLock.release()
            self.UpdateResults()
        except Exception as e:
            LogError(uMsg="Error on Script ended message handler",oException=e)
        return

    def NotificationHandler_ScriptFoundItem(self,*args,**kwargs) -> None:
        oDiscoverScriptStatus:cDiscoverScriptStatus
        uScriptname:str
        try:
            self.oDiscoverListWaitLock.acquire()
            uScriptName                         = kwargs.get("scriptname")
            oDiscoverScriptStatus               = self.dScripts[uScriptName]
            oDiscoverScriptStatus.aScriptContentLineText.append(kwargs.get("line"))
            oDiscoverScriptStatus.aScriptContentLineDevice.append(kwargs.get("device"))
            self.oDiscoverListWaitLock.release()
        except Exception as e:
            LogError(uMsg="Error on Script found message handler",oException=e)
        return

    def UpdateResults(self, *args):
        oDiscoverScriptStatus:cDiscoverScriptStatus
        tColor:Tuple=[]
        bFinished:bool = True
        try:
            self.oDiscoverListWaitLock.acquire()
            self.oScrollContent.clear_widgets()
            for oDiscoverScriptStatus in self.dScripts.values():
                oDiscoverScriptStatus.oGrid.clear_widgets()
                if oDiscoverScriptStatus.uScriptStatus=="$lvar(6039)":
                    tColor=[0.2, 0.9, 0.9, 1.0]
                    bFinished = False
                else:
                    tColor=[0.9, 0.9, 0.9, 1.0]

                self.oScrollContent.add_widget(cLabel(text="%s [%s]" % (oDiscoverScriptStatus.uScriptTitle, ReplaceVars(oDiscoverScriptStatus.uScriptStatus)), background_color=[0.2, 0.2, 0.2, 1.0], color=tColor, size=(self.oPopup.width, dp(30)),size_hint=(None, None), halign='center'))
                self.oScrollContent.add_widget(oDiscoverScriptStatus.oGrid)
                self.oScrollContent.add_widget(SettingSpacer())
                if len(oDiscoverScriptStatus.aScriptContentLineText)>0:
                    oDiscoverScriptStatus.oScript.AddHeaders()
                    for i in range(len(oDiscoverScriptStatus.aScriptContentLineText)):
                        oDiscoverScriptStatus.oScript.AddLine(aLine=oDiscoverScriptStatus.aScriptContentLineText[i],dDevice=oDiscoverScriptStatus.aScriptContentLineDevice[i])

            Clock.schedule_once(self.SetScrollSize, 0)
            self.oDiscoverListWaitLock.release()
            if bFinished:
                Clock.unschedule(self.oTimerUpdate)

        except Exception as e:
            LogError(uMsg="Error on update message handler",oException=e)
        return

class cThread_Discover(threading.Thread):
    def __init__(self, uScriptName:str,dParKwArgs:dict):
        threading.Thread.__init__(self)
        self.uScriptName:str    = uScriptName
        self.dKwArgs:dict       = dParKwArgs
    def run(self) -> None:
        try:
            Globals.oScripts.RunScript(self.uScriptName,**self.dKwArgs)
        except Exception as e:
            LogError(uMsg="Critical error string discover script "+self.uScriptName,oException=e)