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


from kivy.logger                      import Logger
from kivy.config                      import ConfigParser as KivyConfigParser

from ORCA.scripts.ScriptConfig        import cScriptConfig
from ORCA.scripts.BaseScriptSettings  import cBaseScriptSettings

from ORCA.utils.FileName              import cFileName
from ORCA.utils.LogError              import LogErrorSmall
from ORCA.utils.ParseResult           import cResultParser
from ORCA.utils.TypeConvert           import ToIntVersion
from ORCA.vars.Replace                import ReplaceVars
from ORCA.RepManagerEntry             import cRepManagerEntry
from ORCA.utils.XML                   import Orca_FromString
from ORCA.utils.CachedFile            import CachedFile


import ORCA.Globals as Globals

class cScriptResultParser(cResultParser):
    """ Resultparser object for Scripts  """
    def __init__(self,oScript):
        super(cScriptResultParser, self).__init__()
        self.oScript        = oScript
        self.uScriptName    = oScript.uScriptName
        self.uDebugContext  = "Script: % s :" % (self.uScriptName)
        self.uContext       = self.uScriptName

class cBaseScript(object):
    """ basic script class to inherit all scripts from """

    class cScriptSettings(cBaseScriptSettings):
        """ Needs to be implemented by main script class """
        pass


    def __init__(self):

        '''
        sortorder

        auto                = unspecified
        first               = begin of list in type
        last                = end of list in type
        before:scriptname   = before given script name
        after:scriptname   = after given script name

        on Logical conficts result is unspecified

        '''

        self.aSettings              = {}
        self.bIsInit                = False
        self.iMyVersion             = ToIntVersion('1.0.0')
        self.iOrcaVersion           = ToIntVersion('1.0.0')
        self.oConfigParser          = KivyConfigParser()
        self.oFnConfig              = None
        self.oFnScript              = None
        self.oPathMy                = None
        self.oPathMyCode            = None
        self.oScriptConfig          = None
        self.uConfigName            = "SCRIPTDEFAULT"
        self.uScriptName            = u''
        self.uSection               = u''
        self.uSortOrder             = u'auto'
        self.uSubType               = u'Generic'
        self.uType                  = u'Generic'
        self.oFnAction              = None

    def Init(self,uScriptName,oFnScript=None):
        """ Initializes the script """

        self.bIsInit            = True
        self.uScriptName        = uScriptName
        if oFnScript is None:
            oFnScriptPy  = cFileName(Globals.oScripts.dScriptPathList[self.uScriptName]) + u'script.py'
            oFnScript    = cFileName(oFnScriptPy)

        self.oFnScript            = cFileName(oFnScript)
        self.oPathMyCode          = Globals.oScripts.dScriptPathList[self.uScriptName]
        self.oPathMy              = Globals.oDefinitionPathes.oPathDefinitionScriptSettings+self.uScriptName
        self.oResultParser        = cScriptResultParser(self)
        self.oFnAction            = cFileName(self.oPathMyCode+"actions")+"customactions.xml"

        if not self.oPathMy.Exists():
            self.oPathMy.Create()

        self.oScriptConfig = cScriptConfig(self)
        self.oScriptConfig.Init()

        Globals.oLanguage.LoadXmlFile("SCRIPT", uScriptName)

        self.oFnConfig = cFileName(self.oPathMy) +'config.ini'
        oRepManagerEntry=cRepManagerEntry(oFnScript)
        if oRepManagerEntry.ParseFromSourceFile():
            self.iMyVersion     = oRepManagerEntry.oRepEntry.iVersion
            self.iOrcaVersion   = oRepManagerEntry.oRepEntry.iMinOrcaVersion
        Globals.oNotifications.RegisterNotification("on_stopapp",self.DeInit,"Script:"+self.uScriptName)
        Globals.oNotifications.RegisterNotification("on_pause",self.OnPause,"Script:"+self.uScriptName)
        Globals.oNotifications.RegisterNotification("on_resume",self.OnResume,"Script:"+self.uScriptName)

        self.ShowDebug(u'Init')

    def RunScript(self, *args, **kwargs):
        """ Dummy """
        pass


    def DeInit(self,**kwargs):
        """ deinitializes the ini file """
        self.ShowDebug(u'DeInit')

    def OnPause(self,**kwargs):
        """ called by system, if the device goes on pause """
        self.ShowInfo(u'OnPause')
    def OnResume(self,**kwargs):
        """ called by system, if the device resumes """
        self.ShowInfo(u'OnResume')

    def ShowWarning(self,uMsg):
        """ creates a warning debug line """
        uRet=u'Script '+self.uScriptName+u': '+ uMsg
        Logger.warning (uRet)
        return uRet

    def ShowDebug(self,uMsg):
        """ creates a debug line """
        uRet=u'Script '+self.uScriptName+u': '+ uMsg
        Logger.debug (uRet)
        return uRet

    def ShowInfo(self,uMsg):
        """ creates a info debug line """
        uRet=u'Script '+self.uScriptName+u': '+ uMsg
        Logger.info (uRet)
        return uRet

    def ShowError(self,uMsg,oException=None):
        """ creates a error debug line """
        iErrNo = 0
        if oException is not None:
            if hasattr(oException,'errno'):
                iErrNo=oException.errno
        if iErrNo is None:
            iErrNo=12345

        uRet=LogErrorSmall (u'Script '+self.uScriptName+u': '+ uMsg + " (%d) " % (iErrNo),oException)
        return uRet

    def GetSettingObjectForConfigName(self,uConfigName):
        """
        Creates/returns a config object

        :rtype: cSetting
        :param string uConfigName: The Name of the configuration
        :return: a Setting object
        """

        oSetting=self.aSettings.get(uConfigName)

        if oSetting is None:
            uConfigName=ReplaceVars(uConfigName)
            oSetting = self.aSettings.get(uConfigName)

        if oSetting is None:
            oSetting=self.cScriptSettings(self)
            self.aSettings[uConfigName]=oSetting
            oSetting.ReadConfigFromIniFile(uConfigName)
        return oSetting


    def ShowSettings(self):
        """  shows the settings dialog """
        Globals.oTheScreen.AddActionToQueue([{'string':'updatewidget','widgetname':'Scriptsettings'}])

    def GetConfigJSON(self):
        """
        Abstract function, needs to be overriden by script class

        :rtype: dict
        :return: Dummy funtion, returns empty dict
        """
        return {}

    def LoadActions(self):
        """ parses the definition specific actions """
        Logger.info (u'Loading Actions for script:'+self.uScriptName)
        if self.oFnAction.Exists():
            sET_Data = CachedFile(self.oFnAction)
            oET_Root = Orca_FromString(sET_Data, None, self.oFnAction.string)
            Globals.oActions.LoadActionsSub(oET_Root,u'actions',         u'action',          Globals.oActions.dActionsCommands,  self.oFnAction.string)

    @classmethod
    def GetConfigJSONforParameters(cls,dDefaults):
        """ Base class """
        return {}

