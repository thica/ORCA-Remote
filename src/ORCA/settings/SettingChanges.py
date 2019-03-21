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

from kivy.config                        import Config as kivyConfig
from kivy.clock                         import Clock

from ORCA.Cookies                       import Var_DeleteCookie
from ORCA.ui.RaiseQuestion              import ShowQuestionPopUp
from ORCA.ui.ShowErrorPopUp             import ShowMessagePopUp
from ORCA.utils.Atlas                   import ClearAtlas
from ORCA.utils.TypeConvert             import ToInt
from ORCA.utils.TypeConvert             import ToUnicode
from ORCA.vars.Access                   import SetVar
from ORCA.vars.Replace                  import ReplaceVars

import ORCA.Globals as Globals

__all__ = ['OrcaConfigParser_On_Setting_Change']

def OrcaConfigParser_On_Setting_Change(config, section, key, value):

    uValue = ToUnicode(value)

    if section == "ORCA":
        if   key == u'button_clear_atlas':
            ClearAtlas()
        elif key == u"button_notification":
            uNotification = value.split("_")[-1]
            Globals.oNotifications.SendNotification(uNotification,**{"key":key,"value":value})
        elif key == u'button_discover_rediscover':
            if uValue == u'button_discover_rediscover':
                Globals.oInterFaces.DiscoverAll()
            else:
                Globals.oInterFaces.DiscoverAll(bForce=True)
        elif key == u'button_discover_results':
            from ORCA.utils.Discover import cDiscover_List
            Globals.oApp.oDiscoverList = cDiscover_List()
            Globals.oApp.oDiscoverList.ShowList()
        elif key == u'button_getonline':
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_Settings_Download')
        elif key == u'button_installed_reps':
            Globals.oDownLoadSettings.LoadDirect(uValue, True)
        elif key == u'button_show_installationhint':
            Var_DeleteCookie('SHOWINSTALLATIONHINT', Globals.uDefinitionName)
            Globals.oTheScreen.AddActionToQueue([{'string': 'call', 'actionname': 'Fkt ShowInstallationHint'}])
        elif key == u'button_show_licensefile':
            SetVar(uVarName="SHOWFILE", oVarValue=ReplaceVars("$var(LICENSEFILE)"))
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_ShowFile')
        elif key == u'button_show_credits':
            SetVar(uVarName="SHOWFILE", oVarValue=ReplaceVars("$var(CREDITSFILE)"))
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_ShowFile')
        elif key == u'button_show_logfile':
            SetVar(uVarName="SHOWFILE", oVarValue=ReplaceVars("$var(LOGFILE)"))
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_ShowFile')
        elif key == u'button_show_powerstati':
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_PowerStati')
        elif key == u'button_updateallreps':
            Globals.oDownLoadSettings.UpdateAllInstalledRepositories(True)
        elif key == u'language':
            # Changes the languages, reloads all strings and reloads the settings dialog
            Globals.uLanguage = uValue
            Globals.oApp.InitPathes()
            Globals.oNotifications.SendNotification("on_language_change")
        elif key == u'locales':
            Globals.uLocalesName = uValue
            Globals.oTheScreen.LoadLocales()
        elif key == u'startrepeatdelay':
            Globals.fStartRepeatDelay = float(uValue)
        elif key == u'longpresstime':
            Globals.fLongPressTime = float(uValue)
        elif key == u'contrepeatdelay':
            Globals.fContRepeatDelay = float(uValue)
        elif key == u'clockwithseconds':
            Globals.bClockWithSeconds = (uValue == '1')
        elif key == u'longdate':
            Globals.bLongDate = (uValue == '1')
        elif key == u'longday':
            Globals.bLongDay = (uValue == '1')
        elif key == u'longmonth':
            Globals.bLongMonth = (uValue == '1')
        elif key == u'checkfornetwork':
            Globals.bConfigCheckForNetwork = (uValue == '1')
        elif key == u'vibrate':
            Globals.bVibrate = (uValue == '1')
        elif key == u'interface':
            if uValue == 'select':
                return
            Globals.oTheScreen.uInterFaceToConfig = uValue
            if Globals.oInterFaces.dInterfaces.get(uValue) is None:
                Globals.oInterFaces.LoadInterface(uValue)
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_InterfaceSettings')
            Globals.oOrcaConfigParser.set(u'ORCA', key, u'select')
            Globals.oOrcaConfigParser.write()
        elif key == u'script':
            if uValue == 'select':
                return
            uScript = u''
            Globals.oOrcaConfigParser.set(u'ORCA', key, 'select')
            Globals.oOrcaConfigParser.write()

            tValue = uValue.split(':')
            uValue = tValue[0]
            if len(tValue) > 1:
                uScript = tValue[1]

            # Configure
            if uValue == ReplaceVars('$lvar(516)'):
                Globals.oTheScreen.uScriptToConfig = uScript
                Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_ScriptSettings')

            # Run
            if uValue == ReplaceVars('$lvar(517)'):
                kwargs = {"caller": "settings"}
                Globals.oScripts.RunScript(uScript,**kwargs)
            Globals.oOrcaConfigParser.set(u'ORCA', key, u'select')
            Globals.oOrcaConfigParser.write()

        elif key == u'definition':
            ShowQuestionPopUp(uTitle='$lvar(599)', uMessage='$lvar(5026)', fktYes=Globals.oApp.on_config_change_change_definition, uStringYes='$lvar(5001)', uStringNo='$lvar(5002)')
        elif key == u'skin':
            Globals.oApp.ReStart()
        elif key == u'rootpath':
            if not Globals.bInit:
                Globals.oApp.close_settings()
                Globals.oApp._app_settings = None
                kivyConfig.write()
                Clock.schedule_once(Globals.oApp.Init_ReadConfig, 0)
            else:
                ShowMessagePopUp(uMessage=u'$lvar(5011)')
        elif key.startswith(u'soundvolume_'):
            uSoundName = key[12:]
            Globals.oSound.SetSoundVolume(uSoundName, ToInt(uValue))
            Globals.oSound.PlaySound(uSoundName)
        elif key == u'button_changedefinitionsetting':
            Globals.uDefinitionToConfigure = uValue[7:]
            Globals.oTheScreen.AddActionShowPageToQueue(uPageName=u'Page_DefinitionSettings')
        else:
            ShowMessagePopUp(uMessage=u'$lvar(5011)')

        # todo: check , if this required anymore
    elif section == Globals.uDefinitionName:
        if key in Globals.oDefinitions.aDefinitionSettingVars:
            SetVar(uVarName = key, oVarValue = value)
        ShowMessagePopUp(uMessage=u'$lvar(5011)')




