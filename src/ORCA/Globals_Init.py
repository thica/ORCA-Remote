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

from kivy.config                           import ConfigParser as OrcaConfigParser

from ORCA.action.Actions                   import cActions
from ORCA.action.Events import cEvents
from ORCA.Globals                          import Globals
from ORCA.International                    import cLanguage
from ORCA.utils.Notifications import cNotifications
from ORCA.Parameter                        import cParameter
from ORCA.utils.Persistence import cPersistence
from ORCA.Sound                            import cSound
from ORCA.definition.Definitions           import cDefinitions
from ORCA.download.DownLoadSettings        import cDownLoad_Settings
from ORCA.interfaces.Interfaces            import cInterFaces
from ORCA.scripts.Scripts                  import cScripts
from ORCA.utils.CheckPermissions           import cCheckPermissions
from ORCA.utils.ModuleLoader               import cModuleLoader
from ORCA.utils.Network                    import cWaitForConnectivity
from ORCA.utils.Platform                   import OS_Platform
from ORCA.utils.Rotation                   import cRotationLayer
from ORCA.utils.TypeConvert                import ToIntVersion


def Globals_Init(*,oApp):
    Globals.oApp                                       = oApp
    Globals.uVersion                                   = Globals.oApp.sVersion
    Globals.iVersion                                   = ToIntVersion(Globals.uVersion)      # string of App Version
    Globals.uBranch                                    = Globals.oApp.sBranch
    Globals.uPlatform                                  = OS_Platform()  # The used Platform
    Globals.oParameter                                 = cParameter()             # Object for Commandline and Environment Parameter
    Globals.aRepNames                                  = [  ('$lvar(683)', 'definitions'),
                                                            ('$lvar(690)', 'wizard templates'),
                                                            ('$lvar(684)', 'codesets'),
                                                            ('$lvar(685)', 'skins'),
                                                            ('$lvar(686)', 'interfaces'),
                                                            ('$lvar(730)', 'scripts'),
                                                            ('$lvar(687)', 'languages'),
                                                            ('$lvar(689)', 'sounds'),
                                                            ('$lvar(691)', 'fonts'),
                                                            ('$lvar(688)', 'others')]


    Globals.oModuleLoader = cModuleLoader()
    Globals.oOrcaConfigParser = OrcaConfigParser()
    Globals.oActions = cActions()
    Globals.oCheckPermissions = cCheckPermissions()  # Object for checking, if we have permissions
    Globals.oDefinitions = cDefinitions()  # Object which holds all loaded definitions
    Globals.oDownLoadSettings = cDownLoad_Settings()  # Object, for managing the settings dialog for download repositories
    Globals.oNotifications = cNotifications()
    Globals.oPersistence = cPersistence()
    Globals.oRotation = cRotationLayer()
    Globals.oLanguage = cLanguage()
    Globals.oScripts = cScripts()  # Object which holds all scripts
    Globals.oSound = cSound()
    Globals.oInterFaces = cInterFaces()  # Object which holds all Interfaces
    Globals.oWaitForConnectivity = cWaitForConnectivity()  # Object for checking, if we have network access
    Globals.oEvents = cEvents()