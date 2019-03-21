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

from copy                import copy
from kivy.logger         import Logger
import ORCA.Globals as Globals


__all__ = ['cNotifications']

class cNotifications(object):
    """ Class for in App communication """
    def __init__(self):
        self.dNotifications     = {}
        self.dNotificationsHash = {}
        self.dFilterPageNames   = {}

    def RegisterNotification(self,uNotification,fNotifyFunction, uDescription="",bQuiet=False,aValueLinks=[],**kwargs):

        dArgs                            = copy(kwargs)
        dArgs["notificationdescription"] = uDescription
        dArgs["nofification"]            = uNotification
        iHash                            = hash(repr(dArgs)+repr(fNotifyFunction))
        bFound                           = False
        uFilterPageName                  = kwargs.get("filterpagename","")

        aNotificationFunctions           = self.dNotifications.get(uNotification, [])

        if iHash in self.dNotificationsHash:
            bFound = True

        if not bFound:
            dEntry = {"function":fNotifyFunction,"args":dArgs,"hash":iHash,"quiet":bQuiet,"valuelinks": aValueLinks}
            aNotificationFunctions.append(dEntry)
            self.dNotifications[uNotification]  = aNotificationFunctions
            self.dNotificationsHash[iHash]      = dEntry
            if uFilterPageName:
                self.dFilterPageNames[uNotification+"_"+uFilterPageName] = iHash
        else:
            Logger.warning("Skippimg duplicate notification registration %s:%s" % (uNotification,dArgs["notificationdescription"]))

        return iHash

    def UnRegisterNotification_ByHash(self,iHash):

        dEntry = self.dNotificationsHash.get(iHash,None)

        if dEntry is not None:
            uNotification          = dEntry["args"]["notification"]
            aNotificationFunctions = self.dNotifications.get(uNotification, [])
            aNotificationFunctions.remove(dEntry)
            del self.dNotificationsHash[iHash]
            uFilterPageName = dEntry["args"].get("filterpagename","")
            uFilterKey = uNotification+"_"+uFilterPageName
            if uFilterKey in self.dFilterPageNames:
                del self.dFilterPageNames[uFilterKey]
        else:
            Logger.error("Try to Degister notification with wrong hash")

    def SendNotification(self,uNotification, **kwargs):
        dRet = {}
        Ret  = None

        # Format for dValueLinks
        # [{"out":"name","in":"name"}]

        aNotificationFunctions = self.dNotifications.get(uNotification, []) + self.dNotifications.get("*", [])

        for dFunction in aNotificationFunctions:
            dArgs = copy(kwargs)
            aValueLinks=dFunction["valuelinks"]
            if dRet is not None:
                for dValueLink in aValueLinks:
                    if dValueLink["in"] in dArgs and dValueLink["out"] in dRet:
                        dArgs[dValueLink["in"]]=dRet[dValueLink["out"]]

            Globals.oEvents.CopyActionPars(dTarget=dArgs, dSource=dFunction["args"], uReplaceOption="donotreplacetarget")
            if not dFunction["quiet"]:
                Logger.debug("Sending notification %s to %s" % (uNotification,dArgs["notificationdescription"]))
            Ret = dFunction["function"](**dArgs)
            if isinstance(Ret,dict):
                dRet = Ret
        return dRet
