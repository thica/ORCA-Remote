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


__all__ = ['MatchWildCard']


# The main function that checks if two given strings match.
# The uMatchWithWildCard string may contain wildcard characters
def MatchWildCard(*,uValue:str,uMatchWithWildCard:str):
    # If we reach at the end of both strings, we are done
    if len(uMatchWithWildCard) == 0 and len(uValue) == 0:
        return True

    # Make sure that the characters after '*' are present
    # in uValue string. This function assumes that the uMatchWithWildCard
    # string will not contain two consecutive '*'
    if len(uMatchWithWildCard) > 1 and uMatchWithWildCard[0] == '*' and len(uValue) == 0:
        return False

    # If the uMatchWithWildCard string contains '?', or current characters
    # of both strings match
    if (len(uMatchWithWildCard) > 1 and uMatchWithWildCard[0] == '?') or (len(uMatchWithWildCard) != 0 and len(uValue) != 0 and uMatchWithWildCard[0] == uValue[0]):
        return MatchWildCard(uMatchWithWildCard=uMatchWithWildCard[1:], uValue=uValue[1:])

        # If there is *, then there are two possibilities
    # a) We consider current character of uValue string
    # b) We ignore current character of uValue string.
    if len(uMatchWithWildCard) != 0 and uMatchWithWildCard[0] == '*':
        return MatchWildCard(uMatchWithWildCard=uMatchWithWildCard[1:], uValue=uValue) or MatchWildCard(uMatchWithWildCard=uMatchWithWildCard, uValue=uValue[1:])

    return False

