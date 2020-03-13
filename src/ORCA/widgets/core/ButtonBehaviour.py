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
from typing                 import Union
from typing                 import Tuple
from typing                 import List
from typing                 import Dict
from typing                 import Callable

from functools              import  partial
from copy                   import  copy

from kivy.logger            import  Logger
from kivy.graphics          import  Line
from kivy.gesture           import  Gesture
from kivy.clock             import  Clock

from ORCA.utils.LogError    import  LogError

import ORCA.Globals as Globals

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kivy.uix.widget        import Widget
    from ORCA.widgets.base.Base import cWidgetBase
    from ORCA.Action            import cAction
else:
    from typing import TypeVar
    Widget  = TypeVar("Widget")
    cAction = TypeVar("cAction")
    cWidgetBase = TypeVar("cWidgetBase")




__all__ = ['simplegesture','cOrcaButtonBehaviour']

bStopRepeat:bool               = False
oDownWidget:Union[Widget,None] = None

def simplegesture(uName:str, point_list) -> Gesture:
    """
    A simple helper function
    Taken from original Kivy examples
    """
    g = Gesture()
    g.add_stroke(list(point_list))
    g.normalize()
    g.name = uName
    return g

def GetTouchActions(touch,dGestures:Dict[str,Tuple]) -> Union[List,None]:
    """ gets the actions for a touch """

    uAction:str
    uInterFace:str
    uConfigName:str
    oAction:cAction

    try:
        oGesture:Gesture = simplegesture('',zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
        # use database to find the more alike gesture, if any
        tGesture:Tuple[float,Gesture] = Globals.oTheScreen.oGdb.find(oGesture, minscore=0.70)

        if tGesture:
            # name is added by kivy pickler but not in kivy init
            # noinspection PyUnresolvedReferences
            Logger.debug (u'Gesturewidget: Identified Gesture:'+ tGesture[1].name)
            for key in Globals.oTheScreen.dGestures.keys():
                if tGesture[1] == Globals.oTheScreen.dGestures[key].oGesture:
                    if key in dGestures:
                        uAction, uInterFace, uConfigName = dGestures[key]
                        Logger.debug (u'Gesturewidget: Calling Gesture Actions')
                        aActions:List[cAction]=Globals.oActions.GetActionList(uActionName = uAction, bNoCopy=False)
                        if aActions:
                            for oAction in aActions:
                                if uInterFace!='':
                                    oAction.dActionPars['interface']=uInterFace
                                if uConfigName!='':
                                    oAction.dActionPars['configname']=uConfigName
                            return aActions
                        else:
                            LogError (uMsg=u'Gesturewidget: Action Not Found:' + uAction)
        return None
    except Exception as e:
        LogError(uMsg=u'Gesturewidget: f_on_touch_up: Runtime Error:',oException=e)
        return None

# We don't use grab()/ungrab() as it didn't show reliable and we had to
# deal with duplicate messages

# noinspection PyUnresolvedReferences,PyUnusedLocal
class cOrcaButtonBehaviour:
    """ a buttonbehaviour addon class """
    def __init__(self,**kwargs):
        # for gestures stuff
        self.dGestures:Dict[str,Tuple]      = {}
        self.oOldTouch                      = None

        # flag to show , if we are on touchdown state
        # Not all widgets have state flag, so we can't use it
        self.bIsDown:bool                  = False

        # Flag if we wait for a double touch event check
        # to avoid to trigger an action on the first touch
        self.bWaitForDouble:bool           = False

        # Flag, if we missed the double touch timer
        #so that we trigger a normal up event
        self.bProcessed:bool               = False

        # Flag, if we have to schedule the first Repeat time, or the repeating time
        self.bFirstRepeat:bool             = True
        # Flag, to force fire a event on touch up
        self.bForceUp:bool                = False
        self.uTapType:str                 = u''
        # Flag, to execute up event by the current down widget
        self.bProcessUp:bool              = False

        # noinspection PyUnresolvedReferences
        self.register_event_type('on_q_press')
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_q_release')
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_gesture')

        self.fktCallBackLong:Union[Callable,None]   = None
        self.fktCallBackRepeat:Union[Callable,None] = None
        self.fktCallBackDouble:Union[Callable,None] = None

        if 'forceup' in kwargs:
            self.bForceUp=bool(kwargs['forceup'])

        self.aActions:Union[List[Dict],None] = None

    def AddGesture(self,uGestureName:str, uActionName:str,uInterFace:str,uConfigName:str) -> None:
        """ adds a gesture to the widget """
        self.dGestures[uGestureName]=(uActionName,uInterFace,uConfigName)

    def Create_LongPressClock(self, touch, *args) -> None:
        """ starts a clock to detect a long press button press """
        self.fktCallBackLong = partial(self.fLongPress, touch)
        FktTrigger=Clock.create_trigger(self.fktCallBackLong, Globals.fLongPressTime)
        FktTrigger()

    def Delete_LongPressClock(self,touch, *args)  -> None:
        """ deletes a clock to detect a long press button press"""
        Clock.unschedule(self.fktCallBackLong)

    def fLongPress(self, touch, *args)  -> bool:
        """ we detected a long button press """
        self.uTapType       = u"long_up"
        # noinspection PyUnresolvedReferences
        self.dispatch('on_q_release')
        self.bProcessed     = True
        return True

    def Create_RepeatClock(self, touch, *args) -> None:
        """ create a clock to detect repeating press (only, if we havnen't define a long press)"""

        FktTrigger:Union[Callable,None]

        if not hasattr(self,'oOrcaWidget'):
            return

        # noinspection PyUnresolvedReferences
        oOrcaWidget:cWidgetBase = self.oOrcaWidget
        if hasattr(self,'uActionNameLongTap'):
            if oOrcaWidget.uActionNameLongTap!=u'':
                return

        if Globals.fStartRepeatDelay>0:
            self.fktCallBackRepeat = partial(self.fRepeat, touch)
            FktTrigger = None
            if self.bFirstRepeat:
                FktTrigger=Clock.create_trigger(self.fktCallBackRepeat, Globals.fStartRepeatDelay)
            else:
                if Globals.oTheScreen.uLastTouchType != "end":
                    FktTrigger=Clock.create_trigger(self.fktCallBackRepeat, Globals.fContRepeatDelay)
            if FktTrigger:
                FktTrigger()

    def Delete_RepeatClock(self,touch, *args) -> None:
        """ Deletes the repeating clock """
        Clock.unschedule(self.fktCallBackRepeat)

    def fRepeat(self, touch, *args) -> None:
        """ we detected a repeat and call the assigned function """
        self.bFirstRepeat = False
        self.fRepeatPress(touch)
        self.Create_RepeatClock(touch)

    def Create_DoublePressClock(self, touch, *args) -> None:
        """ create a clock to detect double press """
        if not self.bWaitForDouble:
            self.bWaitForDouble = True
            self.fktCallBackDouble = partial(self.fDoublePress, touch)
            FktTrigger=Clock.create_trigger(self.fktCallBackDouble , Globals.fDoubleTapTime+0.005)
            FktTrigger()

    def Delete_DoublePressClock(self,touch, *args) -> None:
        """ Deletes the double press clock """
        Clock.unschedule(self.fktCallBackDouble )
        self.bWaitForDouble = False

    def fRepeatPress(self, touch, *args) -> bool:
        """ we detected a repeat and call the assigned function """
        self.uTapType = u'repeat_down'
        self.dispatch('on_q_release')
        self.bProcessed     = True
        return True

    def fDoublePress(self, touch, *args) -> bool:
        """ we detected a double press and call the assigned function """
        # Logger.debug("fDoublePress")
        # Logger.debug("fDoublePress: IsDown:"+str(self.bIsDown))
        # Logger.debug("fDoublePress: Double:"+str(touch.is_double_tap))

        if not self.bIsDown:
            if touch.is_double_tap:
                self.uTapType = u"double_up"
            self.dispatch('on_q_release')
            self.bProcessed     = True
        self.bWaitForDouble = False
        return False

    def IsMyTouch(self, touch) -> bool:
        """ Detect, if the touch belongs to this widget """
        # Hacky to work with widgets inside a scrollview, eg dropdown buttons
        if hasattr(self,'oOrcaWidget'):
            if self.oOrcaWidget is not None:
                if self.oOrcaWidget.uName.startswith('*DROPDOWNBUTTON*'):
                    x2, y2 = self.parent.to_local(touch.x, touch.y)
                    return self.collide_point(x2, y2)
                else:
                    if self.oOrcaWidget.bIsEnabled:
                        return self.collide_point(*touch.pos)
                    else:
                        return False
        return self.collide_point(*touch.pos)

    def on_touch_down(self, touch) -> bool:
        """ called by the framework, if a widget is touched """
        global oDownWidget

        uButton:str = "left"
        if hasattr(touch,"button"):
            uButton = touch.button

        if self.IsMyTouch(touch) and uButton=="left":
            # Logger.debug("on_touch_down")
            for child in self.children[:]:
                if child.dispatch('on_touch_down', touch):
                    return True
            if touch.is_double_tap:
                self.Delete_LongPressClock(touch)
                self.Delete_RepeatClock(touch)
                self.Delete_DoublePressClock(touch)
                # rest will be managed by the up event
                return True

            self.uTapType          = u"down"
            self.bProcessed        = False
            self.bFirstRepeat      = True
            oDownWidget            = self
            oDownWidget.bProcessUp = False
            userdata = touch.ud
            userdata['line'] = Line(points=(touch.x, touch.y))
            if not self.bWaitForDouble:
                self.dispatch('on_q_press')
            self.bIsDown = True
            # we start the clocks after the first triggered action, to make sure, that we don't miss
            # timing on lenghly actions
            # but not on right klick to bypass kivy bug
            if uButton=="left":
                self.Create_DoublePressClock(touch)
                self.Create_LongPressClock(touch)
                self.Create_RepeatClock(touch)
            return True
        return False

    def on_touch_up(self, touch) -> bool:
        """ called by the framework, if the touch ends """
        bRet:bool = False

        if oDownWidget is not None:
            if not oDownWidget.bProcessUp:
                oDownWidget.bProcessUp = True
                return oDownWidget.on_touch_up(touch)
        else:
            if hasattr(self,"oOrcaWidget"):
                if self.oOrcaWidget is not None:
                    Logger.error ("on_touch_up: Up without Down on Widget:"+self.oOrcaWidget.uName)
                else:
                    Logger.error ("on_touch_up: Up without Down")
        if self.bProcessUp:
            #Logger.info("on_touch_up")
            #Logger.debug("on_touch_up: Process:"+str(self.bProcessed))
            #Logger.debug("on_touch_up: WaitforDouble:"+str(self.bWaitForDouble))
            self.bIsDown = False
            self.Delete_LongPressClock(touch)
            self.Delete_RepeatClock(touch)

            if self.bForceUp:
                self.bProcessed = False
                touch.is_double_tap = False

            if self.uTapType == u'' or self.uTapType == u'down' or self.uTapType == u'long_up' or self.uTapType == u'repeat_down':
                self.uTapType ="up"

            if not self.bProcessed and not self.bWaitForDouble:
                if self.fDoublePress(touch):
                    return True

            if 'line' in touch.ud:
                self.aActions=GetTouchActions(touch,self.dGestures)
                if self.aActions:
                    self.dispatch('on_gesture')

            return bRet
        return bRet

    def on_touch_move(self, touch) -> bool:

        """ gesture handling """

        if self.collide_point(*touch.pos):
            bNewMove=False
            if self.oOldTouch is not None:
                if not self.oOldTouch.pos==touch.pos:
                    bNewMove=True
            else:
                bNewMove=True
            self.oOldTouch=copy(touch)

            if bNewMove:
                try:
                    touch.ud['line'].points += [touch.x, touch.y]
                except KeyError:
                    pass
            return True
        return False

    def on_gesture(self) -> None:
        """ placeholder """
        #print ("default move for ",self.oMainWidget.oOrcaWidget.uName)
        pass
    def on_q_press(self)  -> None:
        """ placeholder """
        #print ("default down for" ,self.oMainWidget.oOrcaWidget.uName)
        pass
    def on_q_release(self)  -> None:
        """ placeholder """
        # print ("default up for " ,self.oMainWidget.oOrcaWidget.uName)
        pass
