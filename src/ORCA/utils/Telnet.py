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

import asyncio
import re


from collections            import OrderedDict
from telnetlib3             import open_connection
from telnetlib3             import TelnetReader
from telnetlib3             import TelnetWriter
from telnetlib3             import WILL, WONT, DO, DONT, ECHO, SGA
from kivy.logger            import Logger


__all__ = ['cTelnet']

'''
        "encoding": args.encoding,
        "tspeed": (args.speed, args.speed),
        "shell": accessories.function_lookup(args.shell),
        "term": args.term,
        "force_binary": args.force_binary,
        "encoding_errors": args.encoding_errors,
        "connect_minwait": args.connect_minwait,
        
        client.writer.iac(WONT, ECHO)
        client.writer.iac(WONT, SGA)
        readline = asyncio.ensure_future(client.reader.readline())
        recv_msg = asyncio.ensure_future(client.notify_queue.get())
        client.writer.write("КОСМОС/300: READY\r\n")
        wait_for = set([readline, recv_msg])
        try:
            while True:
                client.writer.write("? ")

                # await (1) client input or (2) system notification
                done, pending = await asyncio.wait(
                    wait_for, return_when=asyncio.FIRST_COMPLETED
                )

       All Telnet options:

Decimal Code	Option Name	RFC
0	Transmit Binary	856
1	Echo	857
2	Reconnection	 
3	Suppress Go Ahead	858
4	Approx Message Size Negotiation.	 
5	Status	859
6	Timing Mark	860
7	Remote Controlled Trans and Echo	563, 726
8	Output Line Width	 
9	Output Page Size	 
10	Negotiate About Output Carriage-Return Disposition	652
11	Negotiate About Output Horizontal Tabstops	653
12	NAOHTD, Negotiate About Output Horizontal Tab Disposition	654
13	Negotiate About Output Formfeed Disposition	655
14	Negotiate About Vertical Tabstops	656
15	Negotiate About Output Vertcial Tab Disposition	657
16	Negotiate About Output Linefeed Disposition	658
17	Extended ASCII.	698
18	Logout.	727
19	Byte Macro	735
20	Data Entry Terminal	732,1043
21	SUPDUP	734, 736
22	SUPDUP Output	749
23	Send Location	779
24	Terminal Type	1091
25	End of Record	885
26	TACACS User Identification	927
27	Output Marking	933
28	TTYLOC, Terminal Location Number.	946
29	Telnet 3270 Regime	1041
30	X.3 PAD.	1053
31	NAWS, Negotiate About Window Size.	1073
32	Terminal Speed	1079
33	Remote Flow Control	1372
34	Linemode	1184
35	X Display Location.	1096
36	Environment	1408
37	Authentication	1416, 2941, 2942, 2943,2951
38	Encryption Option	2946
39	New Environment	1572
40	TN3270E	2355
41	XAUTH	 
42	CHARSET	2066
43	RSP, Telnet Remote Serial Port	 
44	Com Port Control	2217
45	Telnet Suppress Local Echo	 
46	Telnet Start TLS	 
47	KERMIT	2840
48	SEND-URL	 
49	FORWARD_X	 
50
-
137	 	 
138	TELOPT PRAGMA LOGON	 
139	TELOPT SSPI LOGON	 
140	TELOPT PRAGMA HEARTBEAT	 
141
-
254	 	 
255	Extended-Options-List	RFC 861


https://telnetlib3.readthedocs.io/en/latest/_modules/telnetlib3/client.html 
        
'''

class cTelnet:
    """ Very simple Telnet Client to send telnet commands
        supports login and sending commands
    """

    def __init__(self, *,uHost:str, iPort:int=23) ->None:
        self.aCommands:List                     = []
        self.uReturn:str                        = ''
        self.uHost:str                          = uHost
        self.iPort:int                          = iPort
        self.uUserQuestionIdentifier:str        = "login"
        self.uPasswordQuestionIdentifier:str    = "assword"
        self.uTermStringForCredentials:str      = '\n'
        self.uTermStringForCommands: str        = '\n'
        self.oWriter:Union[TelnetWriter,None]   = None
        self.oReader: Union[TelnetReader, None] = None
        self.dKwArgs:Dict                       = {}
        self.fWaitTimeForAfter                  = 0   # if you have problems to get return values, increase it
        self.fWaitTimeForAfterLast              = 0   # if you have problems to get return values, increase it

    def SetCredentionals(self,*,uUser:str='',uPassword:str='',fWaitTime:float=-1) -> None:
        """
        Sets Credentials for login purposes. Linefeed or Carriage Return will be added as defined in the self.uTermStringForCredentials string
        This will be executed in the order of messages defined for the module, usual this should be added first, if required

        :param str uUser: The username
        :param str uPassword: The password

        :return: None
        """

        if uPassword: self.aCommands.append(OrderedDict({self.uPasswordQuestionIdentifier: uPassword+self.uTermStringForCredentials, "unmanaged":False,'waittime':fWaitTime}))
        if uUser: self.aCommands.append(OrderedDict({self.uUserQuestionIdentifier:uUser+self.uTermStringForCredentials,"unmanaged":False,'waittime':fWaitTime}))

    def SetArgs(self,dKwArgs:Dict):
        # If you want to pass further args to telnetlib , this is the place
        self.dKwArgs["tspeed"]=(32000*20, 32000*20)
        self.dKwArgs.update(dKwArgs)
        pass

    def AdjustWriter(self):
        # if you want to set Telnet Options, override this function
        # self.oWriter.iac(DO,ECHO)
        pass

    def AddCommand(self,*, uCommand:str, fWaitTime:float=-1) -> None:
        """
        Adds a command to the command queue, several command can be added. Which values will be returned depends on the telnet Server settings.
        Commands will be executed as part of the Send() command

        :param str uCommand: The telnet command to be sent to the server
        :param float: Optional: The wait time after the command
        :return: None
        """

        self.aCommands.append(OrderedDict({'':uCommand+self.uTermStringForCommands,"unmanaged":True,'waittime':fWaitTime}))

    async def _listen(self):
        """
        Internal function (the core function), who sends all defined commands to the server
        Closes the connection after the last command has been processed
        :return: None
        """

        bManaged: bool  = False
        iFailCount:int  = 0
        uResponse:str = ""
        uCommand: str = ""
        uLastCommand: str = ""
        dItem:OrderedDict = OrderedDict({})
        fWaitTime:float = 0.0

        if self.aCommands[-1]['waittime']==-1:
            self.aCommands[-1]['waittime']=self.fWaitTimeForAfterLast
        self.oReader, self.oWriter  = await open_connection(self.uHost, self.iPort,**self.dKwArgs)
        self.AdjustWriter()

        while True:
            try:
                async with asyncio.timeout(5):
                    uResponse = await self.oReader.read(4096)
            # Logger.debug(f'Telnet: Returned value {RMSC(uResponse)}:')
            except TimeoutError:
                Logger.error(f'Telnet: Timed out: {uLastCommand }')
                break

            if uResponse.rstrip() == "":
                # pass
                continue

            if len(self.aCommands)==0:
                if uResponse.rstrip() != uLastCommand.rstrip() :
                    Logger.debug(f'Telnet: No Commands left, exiting:')
                    break

            bManaged = False
            for dItem in self.aCommands:
                uWaitFor= list(dItem.keys())[0]
                uCommand= dItem[uWaitFor]
                fWaitTime=dItem['waittime']
                if fWaitTime==-1:
                    fWaitTime=self.fWaitTimeForAfter

                if uResponse.rstrip() != uLastCommand.rstrip() and uWaitFor.rstrip() !='':
                    #Logger.debug(f'Telnet: Response: "{RMSC(uResponse)}", Waiting for: "{RMSC(uWaitFor)}"')
                    pass

                if uWaitFor in uResponse and uWaitFor:
                    bManaged = True
                    Logger.debug(f'Telnet: Writing: {RMSC(uResponse)}{RMSC(uCommand)}')
                    self.oWriter.write(uCommand)
                    uLastCommand=uCommand
                    break

                if self._CountManaged(bUnmangaged=False)==0:
                    bManaged = True
                    Logger.debug(f'Telnet: Writing (unconditioned): {RMSC(uCommand)}')
                    self.oWriter.write(uCommand)
                    uLastCommand = uCommand
                    break

            if bManaged:
                self.aCommands.remove(dItem)
                await asyncio.sleep(fWaitTime)
            else:
                    if uResponse.rstrip() != uLastCommand.rstrip() and uResponse!=uCommand:
                        Logger.debug(f'Telnet: Dicarding unmanaged response: {RMSC(uResponse)}')
                        iFailCount=iFailCount+1
                        if iFailCount>10:
                            Logger.error(f'Telnet: Too many unmanaged responses, exiting: {RMSC(uResponse)}')
                            break
        Logger.info(f'Telnet: Returning: {RMSC(uResponse)}')
        self.uReturn=uResponse
        self.oWriter.close()

    def _CountManaged(self,*, bUnmangaged:bool) -> int:
        """
        Internal function, who counts the number of managed or unmaanged commands in the command queue
        Managed Commands arte commands, where we wait for a specific response from the telnet server
        Unmanaged commands will be sent as soon all unmanaged commands have been sent

        :param bool bUnmangaged: Flag if unmanaged or managed commands could be counted

        :return: int: the number of managed or unmanaged commands
        """

        iRet:int=0
        for dItem in self.aCommands:
            if dItem['unmanaged']:
                iRet=iRet+1
        if not bUnmangaged:
            iRet=len(self.aCommands)-iRet
        return iRet

    def Send(self) -> str:
        """
        Main Entry point to send all defined commands to the telnet server
        The return value depends on the telnet server settings, in best case the output of the last unmanaged commands
        :return: str: undefined, in best case the output of the last unmanaged commands
        """
        asyncio.run(self._listen())
        return self.uReturn


def RMSC(uInput:str)->str:
    return uInput.replace('\n','[LF]').replace('\r','[CR]')


