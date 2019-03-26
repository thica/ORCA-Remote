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

import traceback

from kivy.logger            import Logger
from ORCA.Compat            import PY2

__all__ =['LogError','LogErrorSmall']


def LogErrorSmall(uMsg, oException=None):
    LogError(uMsg, oException, False)

def LogError(uMsg, oException=None, bTrackStack = False):

    """ Logging an error with traceback """

    uStackText = u''
    if uMsg is None:
        uMsg = ""

    if bTrackStack:
        if oException is not None:
            uStackText = traceback.format_exc()
        else:
            uStackText = ''.join(traceback.format_list(traceback.extract_stack())[:-2])
        if PY2:
            try:
                uStackText=unicode(string=uStackText,errors='replace')
            except Exception as e:
                pass

    if oException is None:
        uRet=uMsg
        uRet2=uMsg
    else:
        ErrText= str(oException)
        uRet=uMsg+u' : '+ErrText

    if bTrackStack:
        uRet2=uRet+ u"\n\n"+uStackText
    else:
        uRet2 = uRet

    Logger.error (uRet2)
    return uRet
