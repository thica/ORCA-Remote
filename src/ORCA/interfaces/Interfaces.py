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

from typing import List
from typing import Dict
from typing import Union

from kivy.logger            import Logger

from ORCA.ui.ShowErrorPopUp import ShowErrorPopUp
from ORCA.utils.FileName    import cFileName
from ORCA.utils.LogError    import LogError
from ORCA.vars.Replace      import ReplaceVars
from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.utils.ModuleLoader import cModule
from ORCA.actions.ReturnCode import eReturnCode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
    from ORCA.Action import cAction
else:
    from typing import TypeVar
    cBaseInterFaceSettings = TypeVar("cBaseInterFaceSettings")
    cAction = TypeVar("cAction")

import ORCA.Globals as Globals

class cInterFaces:
    """ A container class for all interfaces """
    def __init__(self):
        #list of all Interfaces
        self.aInterfaceList:List[str]               = []
        self.dInterfaces:Dict[str,cBaseInterFace]   = {}
        self.dModules:[str,cModule]                 = {}
        self.uInterFaceListSettingString:str        = u''
        self.dUsedInterfaces:[str,bool]             = {}

    def InitVars(self) -> None:
        """ Clears the list of interfaces """
        self.dUsedInterfaces.clear()

    def Init(self) -> None:
        """ dummy """
        pass
    def DeInit(self) -> None:
        """ deinits the interfaces object """
        uInterfaceName:str
        for uInterfaceName in self.dInterfaces:
            self.dInterfaces[uInterfaceName].DeInit()

    def Clear(self) -> None:
        """ clears the lst of interfaces """
        self.DeInit()
        del self.aInterfaceList[:]
        self.dInterfaces.clear()

    def LoadInterfaceList(self) -> None:
        """ loads the list of all inerfaces """
        Logger.debug (u'Interfaces: Loading Interface List')
        uInterFaceName:str
        self.uInterFaceListSettingString = u''
        self.aInterfaceList = Globals.oPathInterface.GetFolderList()
        self.aInterfaceList.sort(key = lambda x: x)

        for uInterFaceName in self.aInterfaceList:
            self.uInterFaceListSettingString+=u'"{0}",'.format(uInterFaceName)
        self.uInterFaceListSettingString=self.uInterFaceListSettingString[:-1]

    def GetInterface(self,uInterFaceName:str) -> cBaseInterFace:
        """
        Returns an cInterface class

        :param str uInterFaceName: The name of the interface
        :return: The interface class (cBaseInterface)
        """
        return self.dInterfaces.get(uInterFaceName)


    def LoadInterface(self,uInterFaceName:str) -> Union[cModule,None]:
        """
        Loads an interface

        :param str uInterFaceName: The name of the interface
        :return: The interface module (not cBaseInterface)
        """

        uInterFaceName:str
        if uInterFaceName in self.dInterfaces:
            return self.dModules.get(uInterFaceName)

        if uInterFaceName=="":
            return None
        Logger.info (u'Interfaces: Loading Interface: '+uInterFaceName)
        oFnInterfacePy:cFileName  = cFileName(Globals.oPathInterface + uInterFaceName) + u'interface.py'
        oFnInterface:cFileName    = cFileName(oFnInterfacePy)

        if not oFnInterface.Exists():
            LogError(uMsg=u'Interfaces: Fatal Error Loading Interface,  Interface not found: '+uInterFaceName)
            return None

        try:
            # noinspection PyDeprecation
            oModule=Globals.oModuleLoader.LoadModule(oFnInterface,'cInterface' + "_" + uInterFaceName)
            self.dModules[uInterFaceName] = oModule
            oInterface: cBaseInterFace=oModule.GetClass('cInterface')()
            oInterface.Init(uInterFaceName, oFnInterface)
            self.dInterfaces[uInterFaceName]=oInterface
            return oModule
        except Exception as e:
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=LogError(uMsg=u'Interfaces: Fatal Error Loading Interface: '+uInterFaceName+ u' :',oException=e), bAbort=True)
            return None

    def OnPause(self) -> None:
        """ Entry for on Pause """
        uInterfaceName:str
        for uInterfaceName in self.dInterfaces:
            self.dInterfaces[uInterfaceName].OnPause()

    def OnResume(self) -> None:
        """ Entry for on resume """
        uInterfaceName:str
        for uInterfaceName in self.dInterfaces:
            self.dInterfaces[uInterfaceName].OnResume()

    def RegisterInterFaces(self,uInterFaceName:str,fSplashScreenPercentageStartValue:float) -> None:

        """ we do it here, as we load only used interfaces, which we know after loading the definition """
        Logger.debug ('TheScreen: Register Interfaces')

        fSplashScreenPercentageRange:float=10.0

        if not uInterFaceName:
            fPercentage:float=fSplashScreenPercentageStartValue
            fPercentageStep:float=fSplashScreenPercentageRange/len(self.dUsedInterfaces)

            # Scheduling Register Interface
            aActions:List[cAction]=Globals.oEvents.CreateSimpleActionList([{'name':'Show Message the we register the interfaces','string':'showsplashtext','maintext':'$lvar(409)'}])

            #for Interface
            for uInterFaceName in self.aInterfaceList:
                for uKey in self.dUsedInterfaces:
                    uKey2=ReplaceVars(uKey)
                    if uKey2==uInterFaceName and uInterFaceName!=u'':
                        fPercentage=fPercentage+fPercentageStep
                        Globals.oEvents.AddToSimpleActionList(aActions,[{'name':'Update Percentage and Interface Name','string':'showsplashtext','subtext':uKey2,'percentage':str(fPercentage)},
                                                                        {'name':'Register the Interface','string':'registerinterfaces','interfacename':uKey2}
                                                                       ])


                        break
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
        else:
            self.LoadInterface(uInterFaceName)


    def DiscoverAll(self,uInterFaceName:str=u'', uConfigName:str=u'', bGui:bool = False, bForce:bool = False) -> eReturnCode:
        # bForce not used (by now)
        aActions: List[Dict]
        oInterFace: cBaseInterFace
        oSetting: cBaseInterFaceSettings
        if uInterFaceName == u'':
            aActions=[]
            for uInterFaceName in self.dInterfaces:
                oInterFace=self.dInterfaces[uInterFaceName]
                if oInterFace.oObjectConfig.oConfigParser.filename =='':
                    oInterFace.oObjectConfig.LoadConfig()
                for uConfigName in oInterFace.oObjectConfig.oConfigParser.sections():
                    if uConfigName != "DEVICE_DEFAULT":
                        oSetting=oInterFace.GetSettingObjectForConfigName(uConfigName)
                        if bForce:
                            oSetting.aIniSettings.uOldDiscoveredIP = ""
                        if oSetting.aIniSettings.uHost=="discover" and oSetting.aIniSettings.uOldDiscoveredIP  == "":
                            Globals.oEvents.AddToSimpleActionList(aActions, [{'name': 'Discover single with gui', 'string': 'discover', 'interface': uInterFaceName, 'configname': uConfigName, 'gui': '1'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            return eReturnCode.Success
        elif bGui:
            aActions=[]
            uAlias = Globals.oDefinitions.FindDefinitionAliasForInterfaceConfiguration(uInterFaceName=uInterFaceName, uConfigName=uConfigName)
            uDetail = "\n\n%s\n%s:%s" % (uAlias, uInterFaceName, uConfigName)
            Globals.oEvents.AddToSimpleActionList(aActions, [{'name': 'And Discover', 'string': 'call DiscoverSingle', 'DISCOVERINTERFACE': uInterFaceName, 'DISCOVERCONFIG': uConfigName, 'DISCOVERDETAILS': uDetail, 'gui':'0'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None)
            return eReturnCode.Success
        else:
            oInterFace = self.dInterfaces.get(uInterFaceName)
            if oInterFace:
                oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName)
                if oSetting:
                    if oSetting.Discover():
                        return eReturnCode.Success
        return eReturnCode.Error

