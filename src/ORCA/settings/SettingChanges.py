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

from kivy.config                        import Config as kivyConfig
from kivy.clock                         import Clock

from ORCA.utils.Cookies import Var_DeleteCookie
from ORCA.ui.RaiseQuestion              import ShowQuestionPopUp
from ORCA.ui.ShowErrorPopUp             import ShowMessagePopUp
from ORCA.utils.Atlas                   import ClearAtlas
from ORCA.utils.TypeConvert             import ToInt
from ORCA.utils.TypeConvert             import ToBool
from ORCA.vars.Access                   import SetVar

from ORCA.Globals import Globals

__all__ = ['OrcaConfigParser_On_Setting_Change']


# noinspection PyUnusedLocal
def OrcaConfigParser_On_Setting_Change(config:kivyConfig, section:str, key:str, value:str) -> None:

    uSection:str = section
    uKey:str     = key
    uValue:str   = value

    # uValue = ToUnicode(value)

    if uSection == 'ORCA':
        if   uKey == 'button_clear_atlas':
            ClearAtlas()
        elif uKey == 'button_notification':
            uNotification = uValue.split('_')[-1]
            Globals.oNotifications.SendNotification(uNotification=uNotification,**{'key':uKey,'value':uValue})
        elif uKey == 'button_discover_rediscover':
            if uValue == 'button_discover_rediscover':
                Globals.oInterFaces.DiscoverAll()
            else:
                Globals.oInterFaces.DiscoverAll(bForce=True)
        elif uKey == 'button_discover_results':
            from ORCA.utils.Discover import cDiscover_List
            Globals.oApp.oDiscoverList = cDiscover_List()
            Globals.oApp.oDiscoverList.ShowList()
        elif uKey == 'button_installed_reps':
            Globals.oDownLoadSettings.LoadDirect(uDirect=uValue, bForce=True)
        elif uKey == 'button_show_installationhint':
            Var_DeleteCookie(uVarName='SHOWINSTALLATIONHINT', uPrefix=Globals.uDefinitionName)
            Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'call', 'actionname': 'Fkt ShowInstallationHint'}])
        elif uKey == 'button_show_powerstati':
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName='Page_PowerStati')
        elif uKey == 'button_updateallreps':
            Globals.oDownLoadSettings.UpdateAllInstalledRepositories(bForce=True)
        elif uKey == 'showborders':
            Globals.bShowBorders=not Globals.bShowBorders
            Globals.oTheScreen.AddActionToQueue(aActions=[{'string': 'updatewidget *@*'}])
        elif uKey == 'language':
            # Changes the languages, reloads all strings and reloads the settings dialog
            Globals.uLanguage = uValue
            Globals.oApp.InitPathes()
            Globals.oNotifications.SendNotification(uNotification='on_language_change')
        elif uKey == 'locales':
            Globals.uLocalesName = uValue
            Globals.oTheScreen.LoadLocales()
        elif uKey == 'startrepeatdelay':
            Globals.fStartRepeatDelay = float(uValue)
        elif uKey == 'longpresstime':
            Globals.fLongPressTime = float(uValue)
        elif uKey == 'contrepeatdelay':
            Globals.fContRepeatDelay = float(uValue)
        elif uKey == 'clockwithseconds':
            Globals.bClockWithSeconds = (uValue == '1')
        elif uKey == 'longdate':
            Globals.bLongDate = (uValue == '1')
        elif uKey == 'longday':
            Globals.bLongDay = (uValue == '1')
        elif uKey == 'longmonth':
            Globals.bLongMonth = (uValue == '1')
        elif uKey == 'checkfornetwork':
            Globals.bConfigCheckForNetwork = (uValue == '1')
        elif uKey == 'vibrate':
            Globals.bVibrate = (uValue == '1')
        elif uKey == 'button_configureinterface':
            uButton,Globals.oTheScreen.uInterFaceToConfig,Globals.oTheScreen.uConfigToConfig=uValue.split(':')
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName='Page_InterfaceSettings')
        elif uKey == 'button_configurescripts':
            uAction:str
            uScriptName:str
            uAction,uScriptName = uValue.split(':')
            if uAction == 'button_configure':
                Globals.oTheScreen.uScriptToConfig = uScriptName
                Globals.oTheScreen.AddActionShowPageToQueue(uPageName='Page_ScriptSettings')
            elif uAction == 'button_run':
                kwargs = {'caller': 'settings'}
                Globals.oScripts.RunScript(uScriptName,**kwargs)
        elif uKey == 'persistence_sleep':
            Globals.bPersistence_OnSleep = not Globals.bPersistence_OnSleep
        elif uKey == 'persistence_persistence_pagestart':
            Globals.bPersistence_OnPageStart = not Globals.bPersistence_OnPageStart
        elif uKey == 'definition':
            ShowQuestionPopUp(uTitle='$lvar(599)', uMessage='$lvar(5026)', fktYes=Globals.oApp.on_config_change_change_definition, uStringYes='$lvar(5001)', uStringNo='$lvar(5002)')
        elif uKey == 'skin':
            Globals.oApp.ReStart()
        elif uKey == 'rootpath':
            if not Globals.bInit:
                Globals.oApp.close_settings()
                Globals.oApp._app_settings = None
                kivyConfig.write()
                Clock.schedule_once(Globals.oApp.Init_ReadConfig, 0)
            else:
                ShowMessagePopUp(uMessage='$lvar(5011)')
        elif uKey=='sound_muteall':
            Globals.oSound.bMute = ToBool(uValue)
        elif uKey.startswith('soundvolume_'):
            uSoundName = uKey[12:]
            Globals.oSound.SetSoundVolume(SoundName=uSoundName,iValue=ToInt(uValue))
            Globals.oSound.PlaySound(SoundName=uSoundName)
        elif uKey == 'button_changedefinitionsetting':
            Globals.uDefinitionToConfigure = uValue[7:]
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName='Page_DefinitionSettings')
            if uKey in Globals.oDefinitions.aDefinitionSettingVars:
                SetVar(uVarName = uKey, oVarValue = uValue)
        else:
            pass
            # ShowMessagePopUp(uMessage='$lvar(5011)')




