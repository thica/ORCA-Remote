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

import traceback
from typing import Any
from kivy.logger            import Logger

__all__ =['LogError','LogErrorSmall']


def LogErrorSmall(*,uMsg:str, oException:Any=None) ->str:
    """
    Same as LogError , but without stacktrace
    :param uMsg:
    :param oException:
    :return:
    """
    return LogError(uMsg=uMsg, oException=oException, bTrackStack=False)

def LogError(*,uMsg:str, oException:Any=None, bTrackStack:bool = False)-> str:

    """ Logging an error with traceback """

    if uMsg is None:
        uMsg = ''

    uStackText:str  = ''
    uRet:str        = uMsg
    uRet2:str

    if bTrackStack:
        if oException is not None:
            uStackText = traceback.format_exc()
        else:
            uStackText = ''.join(traceback.format_list(traceback.extract_stack())[:-2])

    if oException is not None:
        uRet=uMsg+' : '+str(oException)

    if bTrackStack:
        uRet2 = uRet+ '\n\n'+uStackText
    else:
        uRet2 = uRet

    Logger.error (uRet2)
    return uRet
