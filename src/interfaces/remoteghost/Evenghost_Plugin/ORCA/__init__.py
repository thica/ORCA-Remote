'''
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
'''

# Parts of the code are based on eventghost plugins code

# noinspection PyUnresolvedReferences
import eg

eg.RegisterPlugin(
    name = 'ORCA',
    description = 'Receives events from the Orca over Network.',
    version = '1.0.1',
    author = 'miljbee, adjustments from thica',
    canMultiLoad = True,
    createMacrosOnAdd = True,
    icon = (
        'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/'
        'AAAACXBIWXMAAAsSAAALEgHS3X78AAAAB3RJTUUH1gIQFgQb1MiCRwAAAVVJREFUOMud'
        'kjFLw2AQhp8vif0fUlPoIgVx6+AgopNI3fwBViiIoOAgFaugIDhUtP4BxWDs4CI4d3MR'
        'cSyIQ1tDbcHWtjFI4tAWG5pE8ca7997vnrtP4BOZvW0dSBAcZ0pAMTEzPUs4GvMsVkvP'
        '6HktGWRAOBpjIXVNKOSWWdYXN7lFAAINhBCEQgqxyTHAAQQAD/dFbLurUYJYT7P7TI2C'
        'VavwIiZodyyaH6ZLo/RZVTXiOYVhGOh5jcpbq5eRAXAc5wdBVSPMLR16GtxdbgJgN95d'
        'OxicACG6bPH4uIu1UHjE7sFqR/NDVxhaoixLvFYbtDufNFtu1tzxgdeAaZfBU7ECTvd1'
        'WRlxsa4sp1ydkiRxkstmlEFRrWT4nrRer3vmlf6mb883fK8AoF1d+Bqc6Xkt+cufT6e3'
        'dnb9DJJrq+uYpunZ2WcFfA0ol8v8N5Qgvr/EN8Lzfbs+L0goAAAAAElFTkSuQmCC'
    ),
)

# noinspection PyUnresolvedReferences
import wx
import asynchat
import asyncore
import socket
import win32api
import win32con

class Text:
    '''
    Helper class for receivin remote ghost commands
    '''
    def __init__(self):
        pass

    port = 'TCP/IP Port:'
    eventPrefix = 'Event Prefix:'
    tcpBox = 'TCP/IP Settings'
    eventGenerationBox = 'Event generation'


DEBUG = False
if DEBUG:
    log = eg.Print
else:
    # noinspection PyUnusedLocal
    def log(dummyMesg):
        pass


class ServerHandler(asynchat.async_chat):
    '''Telnet engine class. Implements command line user interface.'''

    # noinspection PyUnusedLocal
    def __init__(self, sock, addr, plugin, server):
        log('Server Handler inited')
        self.plugin = plugin

        # Call constructor of the parent class
        asynchat.async_chat.__init__(self, sock)

        # Set up input line terminator
        self.set_terminator('\n')

        # Initialize input data buffer
        self.data = ''
        self.state = self.state1
        self.ip = addr[0]
        self.aTreeMacros={}
        self.aRawMacros={}


    def handle_close(self):
        '''
        Closes the connection
        '''
        self.plugin.EndLastEvent()
        asynchat.async_chat.handle_close(self)


    def collect_incoming_data(self, data):
        '''Put data read from socket to a buffer
        '''
        # Collect data in input buffer
        log('<<' + repr(data))
        self.data = self.data + data


    if DEBUG:
        def push(self, data):
            log('>>' + repr(data))
            asynchat.async_chat.push(self, data)


    def found_terminator(self):
        '''
        This method is called by asynchronous engine when it finds
        command terminator in the input stream
        '''
        # Take the complete line
        line = self.data

        # Reset input buffer
        self.data = ''

        #call state handler
        self.state(line)


    def initiate_close(self):
        '''
        Closes the connection
        '''
        self.state = self.state1
        self.close()

    def respond_ok(self):
        '''
        Give a OK response
        '''
        self.respond('RemoteGhost.OK')
    def respond_error(self):
        '''
        Give an ERROR Response
        '''
        self.respond('RemoteGhost.ERROR')
    def respond(self, sMsg):
        '''
        Give a the sMsg as a response
        :param sMsg:
        '''
        try:
            sMsg += '[EOL]'
            #print u'ORCA:',type(sMsg),':',sMsg
            #print 'ORCA:',eg.systemEncoding
            #asynchat.async_chat.push(self,sMsg.encode(eg.systemEncoding))
            asynchat.async_chat.push(self,sMsg.encode('utf-8','replace'))
            #synchat.async_chat.push(self,sMsg.decode('utf-8','replace'))
#            asynchat.async_chat.push(self,u'\xc3\x84\xc3\xa4')
            #asynchat.async_chat.push(self,sMsg)
        except Exception as inst:
            print ('ORCA:error send to Orca:'+str(inst))
            pass

    def state1(self, line):
        if line.startswith('c'):
            self.respond('RemoteGhost.Pong')
            return
        if line.startswith('e'):
            self.plugin.TriggerEvent(line[1:].strip())
            self.respond_ok()
            #self.initiate_close()
            return
        if line.startswith('a'):
            sRet=self.ExecuteMacro(line[1:].strip())
            self.respond('RemoteGhost.'+sRet)
            return
        if line.startswith('k'):
            hwnds = eg.lastFoundWindows
            if not hwnds:
                hwnd = None
            else:
                hwnd = hwnds[0]
            sCmd=line[1:]
            print ('ORCA: Sending Keystroke:'+sCmd)
            eg.SendKeys(hwnd, sCmd, False)
            self.respond_ok()
            return
        if line.startswith('m'):
            sCmd=line[1:]
            if sCmd=='{Mouse_Left_Click}':
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                self.respond_ok()
                return
            if sCmd=='{Mouse_Right_Click}':
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                self.respond_ok()
                return

        self.respond_error()
        print ('ORCA:Received invalid statement:'+line)

    # noinspection PyUnusedLocal
    def ProcessMsg(self, sMsg, icon):
        self.respond(sMsg)

    def ExecuteMacro(self,sMacro):
        sRet='Command not found...:'+sMacro
        if len(self.aTreeMacros)==0:
            self.BrowseTree()
        oMacro=self.aTreeMacros.get(sMacro)
        if oMacro is None:
            oMacro=self.aRawMacros.get(sMacro)
        if oMacro is not None:
            sRet= oMacro.Execute

            if isinstance(oMacro, eg.MacroItem):
                eg.programCounter = (oMacro, 0)
                sRet=eg.RunProgram()
            elif isinstance(oMacro, eg.ActionItem):
                sRet=oMacro.Execute()


            #def ExecuteTreeItem(obj, event):
        if sRet is None:
            sRet=''
        if not isinstance(sRet, str):
            print ('ORCA: ErrorExecute:',type(sRet))
            sRet=str(sRet)
            return sRet

        return 'Error'

    def BrowseTree(self,oRoot=None, sContext=''):

        filterClassesNodes=(eg.FolderItem, eg.MacroItem)
        filterClassesTargets=(eg.MacroItem,eg.ActionItem)

        def filterFuncNodes(oObj):
            return isinstance(oObj, filterClassesNodes)
        def filterFuncTargets(oObj):
            return isinstance(oObj, filterClassesTargets)

        if oRoot is None:
            srcTree = eg.document.frame.treeCtrl
            srcRoot = srcTree.GetRootItem()
            obj = srcTree.GetPyData(srcRoot)
            oRoot=obj

        for child in oRoot.childs:
            sText=child.GetLabel()
            #print 'ORCA:5:',type(child)
            #print 'ORCA:6:',child.GetLabel()

            if filterFuncTargets(child):
                sLabel=child.GetLabel()
                if sContext=='':
                    sQlName=sLabel
                else:
                    sQlName=sContext+'.'+sLabel
                #print 'ORCA:6:',sQlName
                self.aTreeMacros[sQlName]=child
                self.aRawMacros[sLabel]=child
            if filterFuncNodes(child):
                self.BrowseTree(child,sContext+'.'+sText)


class Server(asyncore.dispatcher):

    def __init__ (self, port, handler):
        self.handler        = handler
        self.oServerHandler = None

        # Call parent class constructor explicitly
        asyncore.dispatcher.__init__(self)

        # Create socket of requested type
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        # restart the asyncore loop, so it notices the new socket
        eg.RestartAsyncore()

        # Set it to re-use address
        #self.set_reuse_addr()

        # Bind to all interfaces of this host at specified port
        self.bind(('', port))

        # Start listening for incoming requests
        #self.listen (1024)
        self.listen(5)



    def handle_accept (self):
        '''Called by asyncore engine when new connection arrives'''
        # Accept new connection
        log('handle_accept')
        #self.handler.TriggerEvent('ORCA Connecting...')
        (sock, addr) = self.accept()
        self.oServerHandler=ServerHandler(sock, addr, self.handler, self)
        self.handler.logWrapper.AddLogListener(self.oServerHandler)


    def SendMsg(self, sMsg):
        if self.oServerHandler:
            self.oServerHandler.respond(sMsg)

class NetworkReceiver(eg.PluginBase):
    text = Text

    def __init__(self):
        pass
    def __start__(self, port, prefix):
        self.port = port
        self.info.eventPrefix = prefix
        self.logWrapper = LogWrapper(self)
        self.server = Server(self.port, self)

    def __stop__(self):
        if self.server:
            self.server.close()
        self.server = None
        self.logWrapper.StopAllLogListeners()


    def Configure(self, port=1024, prefix='ORCA'):
        text = self.text
        panel = eg.ConfigPanel()

        portCtrl = panel.SpinIntCtrl(port, max=65535)
        eventPrefixCtrl = panel.TextCtrl(prefix)
        st1 = panel.StaticText(text.port)
        st3 = panel.StaticText(text.eventPrefix)
        eg.EqualizeWidths((st1, st3))
        box1 = panel.BoxedGroup(text.tcpBox, (st1, portCtrl))
        box3 = panel.BoxedGroup(text.eventGenerationBox, (st3, eventPrefixCtrl))
        panel.sizer.AddMany([
            (box1, 0, wx.EXPAND),
            (box3, 0, wx.EXPAND|wx.TOP, 10),
        ])

        while panel.Affirmed():
            panel.SetResult(portCtrl.GetValue(), eventPrefixCtrl.GetValue())

class LogWrapper:

    # noinspection PyUnusedLocal
    def __init__(self, oPlugin):
        self.aLogListener = []

    @eg.LogIt
    def AddLogListener(self, oListener):
        if len(self.aLogListener) == 0:
            eg.log.AddLogListener(self)
        if oListener not in self.aLogListener:
            self.aLogListener.append(oListener)

    # noinspection PyUnusedLocal
    def WriteLine(self, sLine, oIcon, wRef, when, indent):
        for oListener in self.aLogListener:
            if not sLine.startswith('ORCA:'):
                oListener.ProcessMsg(sLine, oIcon)

    @eg.LogIt
    def StopAllLogListeners(self):
        if len(self.aLogListener) > 0:
            eg.log.RemoveLogListener(self)
            self.aLogListener = []
