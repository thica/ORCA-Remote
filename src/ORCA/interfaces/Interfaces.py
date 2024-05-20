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

from typing import List
from typing import Dict
from typing import Union
from typing import cast

from kivy.logger                import Logger

from ORCA.ui.ShowErrorPopUp     import ShowErrorPopUp
from ORCA.utils.FileName        import cFileName
from ORCA.utils.LogError        import LogError
from ORCA.vars.Replace          import ReplaceVars
from ORCA.interfaces.BaseInterface import cBaseInterFace
from ORCA.utils.ModuleLoader    import cModule
from ORCA.actions.ReturnCode    import eReturnCode
from ORCA.settings.BaseObject import cBaseObjects

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.interfaces.BaseInterfaceSettings import cBaseInterFaceSettings
    from ORCA.action.Action import cAction
else:
    from typing import TypeVar
    cBaseInterFaceSettings = TypeVar('cBaseInterFaceSettings')
    cAction = TypeVar('cAction')

from ORCA.Globals import Globals

class cInterFaces(cBaseObjects):
    """ A container class for all interfaces """
    def __init__(self):
        cBaseObjects.__init__(self,uType='INTERFACES',uPrefix='INTERFACES')
        #list of all Interfaces
        self.uInterFaceListSettingString:str        = ''
        self.dUsedInterfaces:[str,bool]             = {}

    def InitVars(self) -> None:
        """ Clears the list of interfaces """
        self.dUsedInterfaces.clear()

    def LoadInterfaceList(self) -> None:
        """ loads the list of all interfaces """
        Logger.debug ('Interfaces: Loading Interface List')
        uInterFaceName:str
        self.uInterFaceListSettingString = ''
        self.aObjectNameList = Globals.oPathInterface.GetFolderList()
        self.aObjectNameList.sort(key = lambda x: x)

        for uInterFaceName in self.aObjectNameList:
            self.uInterFaceListSettingString+= f'"{uInterFaceName}",'
        self.uInterFaceListSettingString=self.uInterFaceListSettingString[:-1]

    def GetInterface(self,uInterFaceName:str) -> cBaseInterFace:
        """
        Returns an cInterface class

        :param str uInterFaceName: The name of the interface
        :return: The interface class (cBaseInterface)
        """
        return cast(cBaseInterFace,self.dObjects.get(uInterFaceName))


    def LoadInterface(self,uInterFaceName:str) -> Union[cModule,None]:
        """
        Loads an interface

        :param str uInterFaceName: The name of the interface
        :return: The interface module (not cBaseInterface)
        """

        uInterFaceName:str
        if uInterFaceName in self.dObjects:
            return self.dModules.get(uInterFaceName)

        if uInterFaceName=='':
            return None
        Logger.info ('Interfaces: Loading Interface: '+uInterFaceName)
        oFnInterfacePy:cFileName  = cFileName(Globals.oPathInterface + uInterFaceName) + 'interface.py'
        oFnInterface:cFileName    = cFileName(oFnInterfacePy)

        if not oFnInterface.Exists():
            LogError(uMsg='Interfaces: Fatal Error Loading Interface,  Interface not found: '+uInterFaceName)
            return None

        try:
            # noinspection PyDeprecation
            oModule=Globals.oModuleLoader.LoadModule(oFnModule=oFnInterface,uModuleName='cInterface' + '_' + uInterFaceName)
            self.dModules[uInterFaceName] = oModule
            oInterface: cBaseInterFace=oModule.GetClass('cInterface')()
            oInterface.Init(uInterFaceName, oFnInterface)
            self.dObjects[uInterFaceName]=oInterface
            return oModule
        except Exception as e:
            ShowErrorPopUp(uTitle='Fatal Error',uMessage=LogError(uMsg='Interfaces: Fatal Error Loading Interface: '+uInterFaceName+ ' :',oException=e), bAbort=True)
            return None

    def RegisterInterFaces(self,uInterFaceName:str,fSplashScreenPercentageStartValue:float) -> None:

        """ we do it here, as we load only used interfaces, which we know after loading the definition """
        Logger.debug ('TheScreen: Register Interfaces')

        fSplashScreenPercentageRange:float=10.0

        if not uInterFaceName:
            fPercentage:float=fSplashScreenPercentageStartValue
            fPercentageStep:float=fSplashScreenPercentageRange/len(self.dUsedInterfaces)

            # Scheduling Register Interface
            aActions:List[cAction]=Globals.oEvents.CreateSimpleActionList(aActions=[{'name':'Show Message the we register the interfaces','string':'showsplashtext','maintext':'$lvar(409)'}])

            #for Interface
            for uInterFaceName in self.aObjectNameList:
                for uKey in self.dUsedInterfaces:
                    uKey2=ReplaceVars(uKey)
                    if uKey2==uInterFaceName and uInterFaceName!='':
                        fPercentage += fPercentageStep
                        Globals.oEvents.AddToSimpleActionList(aActionList=aActions,aActions=[{'name':'Update Percentage and Interface Name','string':'showsplashtext','subtext':uKey2,'percentage':str(fPercentage)},
                                                                                             {'name':'Register the Interface','string':'registerinterfaces','interfacename':uKey2}
                                                                                            ])


                        break
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName="registerinterfaces")
        else:
            self.LoadInterface(uInterFaceName)


    def DiscoverAll(self,uInterFaceName:str='', uConfigName:str='', bGui:bool = False, bForce:bool = False) -> eReturnCode:
        # bForce not used (by now)
        aActions: List[Dict]
        oInterFace: cBaseInterFace
        oSetting: cBaseInterFaceSettings
        if uInterFaceName == '':
            aActions=[]
            for uInterFaceName in self.dObjects:
                oInterFace=cast(cBaseInterFace,self.dObjects[uInterFaceName])
                if oInterFace.oObjectConfig.oConfigParser.filename =='':
                    oInterFace.oObjectConfig.LoadConfig()
                for uConfigName in oInterFace.oObjectConfig.oConfigParser.sections():
                    if uConfigName != 'DEVICE_DEFAULT':
                        oSetting=oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
                        if bForce:
                            oSetting.aIniSettings.uOldDiscoveredIP = ''
                        if oSetting.aIniSettings.uHost=='discover' and oSetting.aIniSettings.uOldDiscoveredIP  == '':
                            Globals.oEvents.AddToSimpleActionList(aActionList=aActions, aActions=[{'name': 'Discover single with gui', 'string': 'discover', 'interface': uInterFaceName, 'configname': uConfigName, 'gui': '1'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName="discoverall")
            return eReturnCode.Success
        elif bGui:
            aActions=[]
            uAlias = Globals.oDefinitions.FindDefinitionAliasForInterfaceConfiguration(uInterFaceName=uInterFaceName, uConfigName=uConfigName)
            uDetail = f'\n\n{uAlias}\n{uInterFaceName}:{uConfigName}'
            Globals.oEvents.AddToSimpleActionList(aActionList=aActions, aActions=[{'name': 'And Discover', 'string': 'call DiscoverSingle', 'DISCOVERINTERFACE': uInterFaceName, 'DISCOVERCONFIG': uConfigName, 'DISCOVERDETAILS': uDetail, 'gui':'0'}])
            Globals.oEvents.ExecuteActionsNewQueue(aActions=aActions,oParentWidget=None,uQueueName="discoverall_gui")
            return eReturnCode.Success
        else:
            oInterFace = self.GetInterface(uInterFaceName)
            if oInterFace:
                oSetting = oInterFace.GetSettingObjectForConfigName(uConfigName=uConfigName)
                if oSetting:
                    if oSetting.Discover():
                        return eReturnCode.Success
        return eReturnCode.Error

