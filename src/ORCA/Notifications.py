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

from typing             import Dict
from typing             import List
from typing             import Callable
from typing             import Optional

from copy               import copy
from kivy.logger        import Logger
import ORCA.Globals as Globals


__all__ = ['cNotifications']

class cNotifications:
    """ Class for in App communication """
    def __init__(self):
        self.dNotifications:Dict[str,List]     = {}
        self.dNotificationsHash:Dict[int,Dict] = {}
        self.dFilterPageNames:Dict[str,int]    = {}

    def RegisterNotification(self,*, uNotification:str, fNotifyFunction:Callable, uDescription:str="", bQuiet:bool=False, aValueLinks:Optional[List[Dict]]=None, **kwargs) -> int:
        """
        Registers a notification

        :param uNotification: The notification name
        :param fNotifyFunction: The function to be called, if the notification is triggered
        :param uDescription: A notification description(for debugging purposes)
        :param bQuiet: Flag, if true, no debug message will be triggered on notification
        :param aValueLinks: Dict of chained values to passed through chained notification, format "in:name / out:name"
        :param kwargs: args to pass through the notification
        :return:
        """
        if aValueLinks is None:
            aValueLinks = []

        dArgs:Dict                       = copy(kwargs)
        dArgs["notificationdescription"] = uDescription
        dArgs["notification"]            = uNotification
        iHash:int                        = hash(repr(dArgs)+repr(fNotifyFunction))
        uFilterPageName:str              = kwargs.get("filterpagename","")

        aNotificationFunctions:List      = self.dNotifications.get(uNotification, [])

        if iHash in self.dNotificationsHash:
            Logger.warning("Duplicate notification registration %s:%s, replacing old one" % (uNotification,dArgs["notificationdescription"]))

        dEntry:Dict = {"function":fNotifyFunction,"args":dArgs,"hash":iHash,"quiet":bQuiet,"valuelinks": aValueLinks}
        aNotificationFunctions.append(dEntry)
        self.dNotifications[uNotification]  = aNotificationFunctions
        self.dNotificationsHash[iHash]      = dEntry
        if uFilterPageName:
            self.dFilterPageNames[uNotification+"_"+uFilterPageName] = iHash

        return iHash

    def UnRegisterNotification_ByHash(self,*,iHash:int) -> None:
        """
        Unregisters an registered notification. The notification needs to be identified by the hash, when it has been created
        :param int iHash: The hash to identify the notification
        :return: Nothing
        """
        dEntry:Optional[Dict] = self.dNotificationsHash.get(iHash,None)

        if dEntry is not None:
            uNotification:str            = dEntry["args"]["notification"]
            aNotificationFunctions:List  = self.dNotifications.get(uNotification, [])
            aNotificationFunctions.remove(dEntry)
            del self.dNotificationsHash[iHash]
            uFilterPageName:str = dEntry["args"].get("filterpagename","")
            uFilterKey:str = uNotification+"_"+uFilterPageName
            if uFilterKey in self.dFilterPageNames:
                del self.dFilterPageNames[uFilterKey]
        else:
            Logger.error("Tried to Degister notification with wrong hash")

    def SendNotification(self,*,uNotification:str, **kwargs) -> Dict:
        """
        Calls the function of all registered notifications for the notification name
        If valuelinks are given, the results of a call are passed to the next called function
        :param str uNotification: The notification
        :param kwargs: The args to be passed to the called function
        :return: A dict of function results
        """
        dRet:Dict = {}

        # Format for dValueLinks
        # [{"out":"name","in":"name"}]

        aNotificationFunctions:List = self.dNotifications.get(uNotification, []) + self.dNotifications.get("*", [])

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
