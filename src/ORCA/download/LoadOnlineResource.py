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

from typing import Union

import urllib

from xml.etree.ElementTree      import ElementTree
from xml.etree.ElementTree      import Element

from kivy.logger                import Logger
from kivy.event                 import EventDispatcher
from kivy.network.urlrequest    import UrlRequest
from ORCA.ui.ProgressBar        import cProgressBar
from ORCA.utils.Zip             import cZipFile
from ORCA.utils.LogError        import LogError
from ORCA.utils.wait.StartWait  import StartWait
from ORCA.utils.wait.StopWait   import StopWait
from ORCA.vars.Access           import SetVar
from ORCA.utils.TypeConvert     import ToInt
from ORCA.utils.FileName        import cFileName
from ORCA.utils.Path            import cPath
import ORCA.Globals as Globals

from ORCA.download.DownloadObject   import cDownLoadObject
from ORCA.download.RegisterDownload import  RegisterDownLoad

__all__ = ['cLoadOnlineResource']

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ORCA.download.Repository import cRepository
else:
    from typing import TypeVar
    cRepository     = TypeVar("cRepository")


# class to load a web based resource by url (not ftp)
# noinspection PyUnusedLocal
class cLoadOnlineResource(EventDispatcher):
    """ Class for loading a single online resource """
    def __init__(self, *args, **kwargs):
        self.oRepository:cRepository                = kwargs["oRepository"]
        kwargs.pop("oRepository")

        super(cLoadOnlineResource, self).__init__(*args, **kwargs)
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_download_finished')

        self.bIsLoading:bool                        = False
        self.oRef:Union[cDownLoadObject,None]       = None
        self.uDest:str                              = ""
        self.uTarget:str                            = ""
        self.uType:str                              = ""
        self.uName:str                              = ""
        self.uVersion:str                           = ""
        self.oWeb                                   = None
        self.oProgressBar:Union[cProgressBar,None]  = None
        self.bFinished:bool                         = False
        self.bOnError:bool                          = False
        self.bIsLoading:bool                        = True
        self.bFirstMessage:bool                     = True
        self.uUrl:str                               = ''


    def LoadSingleFile(self, sRef:str,oProgressBar:cProgressBar) -> bool:
        """
        Loads a single resource by web
        dispatches on_download_finished when finished
        """

        self.oRef           = cDownLoadObject()
        self.oRef.FromString(sRef)

        uUrl                 = self.oRef.dPars["Url"]
        self.uDest           = self.oRef.dPars["Dest"]
        self.uTarget         = self.oRef.dPars["Target"]
        self.uType           = self.oRef.dPars["Type"]
        self.uName           = self.oRef.dPars["Name"]
        self.uVersion        = self.oRef.dPars["Version"]

        self.oWeb            = None
        self.oProgressBar    = oProgressBar
        self.bFinished       = False
        self.bOnError        = False
        self.bIsLoading      = True
        self.bFirstMessage   = True

        StartWait()

        try:
            Logger.debug("LoadOnlineResource: Downloading [%s] to [%s]" % (uUrl,self.uDest))
            # noinspection PyUnresolvedReferences
            self.uUrl = urllib.parse.quote(uUrl, safe="%/:=&?~#+!$,;'@()*[]")

            #self.uUrl         = urllib.quote(uUrl,safe="%:=&?~#+!$,;'@()*[]")
            #todo: fix ocaremote ssl problem and remove verify=false
            self.oWeb         = UrlRequest(self.uUrl, verify=False, on_success=self.OnSuccess,on_failure=self.OnFailure,on_error=self.OnError,on_progress=self.OnProgress, decode=False,file_path=self.uDest, debug=False)

            return True
        except Exception as e:
            LogError(uMsg=u'can\'t load online resource: %s to %s' % (self.uUrl,self.uDest),oException=e)
            self.bFinished  = True
            self.bOnError   = True
            self.bIsLoading = False
            StopWait()
            SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")
            # noinspection PyUnresolvedReferences
            self.dispatch('on_download_finished')
            return False

    def OnError(self,request,result) -> None:
        """ Handle an FTP error event """
        self.OnFailure(request,result)

    def OnFailure(self,request,result) -> None:
        """ Handle an FTP Failure event """
        self.bFinished = True
        self.bOnError  = True
        cFileName('').ImportFullPath(self.uDest).Delete()
        LogError(uMsg=u'can\'t load online resource: %s to %s [%s]' % (self.uUrl,self.uDest,result))
        self.OnSuccess(None,None)
        self.bIsLoading=False
        SetVar(uVarName = "DOWNLOADERROR", oVarValue = "1")
        StopWait()
        return

    def OnProgress(self,request,iCurrentSize,iTotalSize) -> None:
        """ Updates the progressbar  """
        if not self.oProgressBar is None:
            if self.bFirstMessage:
                self.bFirstMessage=False
                self.oProgressBar.SetMax(iTotalSize)

            if self.oProgressBar.bCancel:
                self.bFinished = True
                self.bOnError  = True
                cFileName('').ImportFullPath(self.uDest).Delete()
                self.OnSuccess(None,None)
                return

            self.oProgressBar.Update(iCurrentSize)

    def OnSuccess(self,request,result) -> None:
        """ Handles when the download of a single file finishes  """
        self.bIsLoading=False
        # noinspection PyUnresolvedReferences
        self.dispatch('on_download_finished')
        self.bFinished = True

        oFileName = cFileName().ImportFullPath(self.uDest)
        if not oFileName.Exists():
            Logger.error("Target File not found:" + oFileName.string)
            self.bOnError = True

        if not self.bOnError:
            self.Finish()
        StopWait()

    def on_download_finished(self) -> None:
        """ blank function for dispatcher """
        pass

    def Finish(self) -> bool:
        """ Finish loading """

        oET_Root:Element

        if self.oRef.dPars["Finalize"]=="REPOSITORY XML":
            try:
                oET_Root = ElementTree(file=self.uDest).getroot()
                if not oET_Root is None:
                    self.oRepository.ParseFromXMLNode(oET_Root)
            except Exception as e:
                LogError(uMsg=u'can\'t parse repository:'+self.uUrl,oException=e)
                return True
        if self.oRef.dPars["Finalize"]=="FILE ZIP":
            try:
                if not self.bOnError:
                    if self.uTarget.startswith('.' or '..' in self.uTarget):
                        LogError(uMsg='All destination pathes must be inside the ORCA directory, absolute pathes are not allowed!:'+self.uTarget)
                    else:
                        oZipFile:cZipFile = cZipFile('').ImportFullPath(self.uDest)
                        if oZipFile.IsZipFile():
                            if not Globals.bProtected:
                                oZipFile.Unzip(cPath('$var(APPLICATIONPATH)/'+self.uTarget))
                            else:
                                LogError(uMsg="Protected: Nothing will be unzipped")
                        else:
                            if oZipFile.Exists():
                                Logger.error("Failed to unzip:"+oZipFile.string)
                            else:
                                Logger.error("Failed to download zip:" + oZipFile.string)
                                #todo: handle unzipped files
                        oZipFile.Delete()
                Logger.debug('LoadOnlineResource: Finished download Resource  [%s][%s]' % (self.uType,self.uName))
                RegisterDownLoad(self.uType,self.uName,ToInt(self.uVersion))
            except Exception as e:
                LogError(uMsg=u'can\'t unpack resources:'+self.uUrl,oException=e)
