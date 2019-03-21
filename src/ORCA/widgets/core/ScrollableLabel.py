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


from kivy.uix.scrollview                import ScrollView
from kivy.uix.label                     import Label
from kivy.effects.scroll                import ScrollEffect
from kivy.properties                    import StringProperty
from kivy.clock                         import Clock
from functools                          import partial

from ORCA.widgets.core.TouchRectangle   import cTouchRectangle
from ORCA.widgets.core.Label            import cLabel
from kivy.metrics                       import dp


__all__ = ['cScrollableLabel']


class ScrollEffectLoader(ScrollEffect):

    def __init__(self,**kwargs):
        ScrollEffect.__init__(self,**kwargs)
        self.iMax=0
        self.iScrollHeight = 0

    def on_value(self, *args):

        scroll_min = self.min
        scroll_max = self.max

        oScrollView=self.target_widget.oScrollView

        if oScrollView.iScrollHeight == 0:
            oScrollView.iScrollHeight=scroll_min*-1

        if self.iMax==0:
            self.iMax = 1

        if scroll_min > scroll_max:
            scroll_min, scroll_max = scroll_max, scroll_min
        if self.value < scroll_min:
            self.overscroll = self.value - scroll_min
            self.reset(scroll_min)
        elif self.value > scroll_max:
            self.overscroll = self.value - scroll_max
            self.reset(scroll_max)
        else:
            iScroll=self.value
            iRet = oScrollView.iNoScroll
            if args[1]==args[0].max:
                iRet=oScrollView.PageDown()
            if args[1]==args[0].min:
                iRet=oScrollView.PageUp()

            if iRet==oScrollView.iPageDown:
                iScroll=oScrollView.iScrollHeight
            if iRet==oScrollView.iPageUp:
                iScroll=scroll_min-oScrollView.iScrollHeight
            if iRet==oScrollView.iTop:
                iScroll=oScrollView.iScrollLines*oScrollView.iLineHeight

            #print "iScroll:",iScroll," ",args[0].max," ",args[0].min

            self.scroll = iScroll

class cScrollableLabel(cTouchRectangle):

    text = StringProperty('')
    def __init__(self,**kwargs):

        self.oScrollView    = self
        self.oLabel         = None
        self.aKwArgs        = kwargs
        self.iLineHeight    = 0

        cTouchRectangle.__init__(self,**self.aKwArgs)

        self.aKwArgs['bar_width']=0
        self.oScrollView=ScrollView(**kwargs)
        self.add_widget(self.oScrollView)

        #if self.aKwArgs.has_key('pos'):
        #    del self.aKwArgs['pos']

        #if self.aKwArgs.has_key('size'):
        #    del self.aKwArgs['size']

        self.aKwArgs['text_size']     = (self.aKwArgs['size'][0],None)

        self.aKwArgs['size_hint_y']     = None
        self.aKwArgs['size_hint_x']     = None

        #test
        #self.aKwArgs['text_size']     = self.size
        #self.aKwArgs['valign']     = 'top'


        self.oLabel = Label(**self.aKwArgs)
        self.oLabel.oScrollView=self
        self.oLabel.bind(texture_size=self._set_height)
        self.oScrollView.add_widget(self.oLabel)

        self.oLabel.bind(texture_size=self._set_height)

    def on_pos(self,instance,pos):
        if self.oScrollView is not None:
            self.oScrollView.pos=pos

    def _set_height(self, instance, size):
        instance.height = size[1]
        instance.width = size[0]
        if self.iLineHeight==0:
            self.iLineHeight=instance.height
            if self.iLineHeight>instance.font_size*2:
                self.iLineHeight=instance.font_size**1.128

    def on_text(self, instance, value):
        if self.oLabel is not None:
            self.oLabel.text=value

from kivy.uix.recycleview               import RecycleView
from kivy.uix.boxlayout                 import BoxLayout
from kivy.properties                    import StringProperty
from kivy.lang                          import Builder

from ORCA.utils.LoadFile                import         LoadFile

Builder.load_string('''
<cScrollableLabelLarge>:
    RecycleBoxLayout:
        default_size_hint: 1, None
        size_hint: None,None
        height: self.minimum_height
''')

class cScrollableLabelLarge(RecycleView):

    class cLineLayout(BoxLayout):
        text = StringProperty("")
        def __init__(self, **kwargs):
            super(self.__class__,self).__init__(**kwargs)
            self.oLabel         = cLabel(**self.oRecycleView.kwFontArgs)
            self.oLabel.oOrcaWidget = self.oRecycleView.oOrcaWidget
            self.add_widget(self.oLabel)
        def on_size(self,*largs):
            self.oLabel.height      =  self.height
            self.oLabel.text_size   =  self.size
        def on_text(self,instance,value):
            self.oLabel.text=value

    font_size =  StringProperty('')
    text = StringProperty('')

    def __init__(self, **kwargs):
        self.oOrcaWidget = kwargs.get('ORCAWIDGET',None)
        self.cLineLayout.oRecycleView=self
        self.iMaxLen                = 0
        self.scroll_type            = ['bars', 'content']
        self.scroll_wheel_distance  = dp(114)
        self.bar_width              = dp(10)
        super(self.__class__, self).__init__(**kwargs)


        self.layout_manager.default_size= (None, self.font_size*1.1)
        self.layout_manager.orientation= 'vertical'
        self.aFontProperties=Label._font_properties+("background_color",)
        self.kwFontArgs={"halign" : "left","valign": "top", "max_lines":1,"font_size":20}
        for k in kwargs:
            if k in self.aFontProperties:
                self.kwFontArgs[k]=kwargs[k]
        if "text" in self.kwFontArgs:
            self.SetText(self.kwFontArgs["text"])
        elif "filename" in kwargs:
            self.ReadFromFile(kwargs["filename"])
        else:
            pass

    def on_font_size(self, instance, value):
        if self.layout_manager is not None:
            self.kwFontArgs["font_size"]=self.font_size
            self.layout_manager.default_size= (None, self.font_size*1.1)
            #self.layout_manager.invalidate()
            self.refresh_from_layout()
    def IncreaseFontSize(self,*args):
        self.font_size        +=1
    def DecreaseFontSize(self,*args):
        self.font_size        -=1
    def ReadFromFile(self,uFileName):
        self.SetText(LoadFile(uFileName))
    def SetText(self,uText):
        aData = uText.split('\n')
        self.SetData(aData)
    def SetData(self,aData):
        self.data = [{'text': str(x)} for x in aData]
        self.iMaxLen=len(max(aData,key=len))
        self.layout_manager.width=(self.font_size/2.2)*self.iMaxLen
        self.viewclass              = self.cLineLayout
    def on_text(self, instance, value):
        if self.layout_manager is not None:
            self.SetText(value)











class cScrollableLabelLargeOld(cScrollableLabel):

    def __init__(self,**kwargs):
        self.ReInit()

        cScrollableLabel.__init__(self,**kwargs)

        self.oScrollView.effect_cls  = ScrollEffectLoader
        self.oScrollView.effect_x = ScrollEffect(target_widget=self.oScrollView._viewport)
        self.oScrollView.effect_x.bind(scroll=self.oScrollView._update_effect_x)
        # not working, Kivy Bug?
        #self.oScrollView.effect_y  = ScrollEffectLoader



    def ReInit(self):
        # Number of textlines for Texture (max)
        self.iMaxLines      = 1
        # Number of textlines for Texture (real)
        self.iRealLines     = 1
        # startline to show
        self.iStart         =  0
        # number of textlines that fit in 'size'
        self.iWindowLines   = 0
        self.aText          = ''
        #number of lines on text
        self.iCntLines      =  0

        # factor from windows size to texture size, should not be less than 2
        self.iOverSizeFactor    = 2
        # enum
        self.iTop               = 1
        # enum
        self.iPageDown          = 2
        # enum
        self.iPageUp            = 3
        # enum
        self.iBottom            = 4
        # enum
        self.iNoScroll          = 0
        # pixels to scroll, if full window to scroll
        self.iScrollHeight      = 0
        # flag, if text has changed
        self.bNewText = True
        # number of lines to scroll incaes we have over/underscroll
        self.iScrollLines       = 0
        #number of max chars per line before beark will be added
        self.iMaxCharsPerLine =  20


    def on_text(self, instance, value):
        self.ReInit()
        self.aText=value.split('\n')

        if self.oLabel is not None:
            iMaxCharwidth=self.oLabel._label.get_extents('1')[0]
            self.iMaxCharsPerLine=int(self.width/iMaxCharwidth)
            i=0
            iEnd=len(self.aText)

            while i<iEnd:
                if len(self.aText[i])>self.iMaxCharsPerLine:
                    self.aText.insert(i+1,self.aText[i][self.iMaxCharsPerLine:])
                    self.aText[i]=self.aText[i][:self.iMaxCharsPerLine]
                    iEnd+=1
                i+=1

        self.iCntLines=len(self.aText)
        self.SetStart(self.iStart)

    def CalcLines(self):
        self.iWindowLines=int(self.height/self.iLineHeight)
        if self.iMaxLines==1:
            self.iMaxLines= int(self.iWindowLines*self.iOverSizeFactor)

    def SetStart(self,iNewStart,instance=None):

        iRet = self.iNoScroll
        self.iScrollLines = 0

        if len(self.aText)==0:
            return iRet

        if self.iLineHeight==0:
            uText= self.aText[0]
            cScrollableLabel.on_text(self,self.oLabel,uText)
            Clock.schedule_once(partial(self.SetStart,iNewStart),0)
            return iRet

        self.CalcLines()
        if iNewStart<0:
            iNewStart=0

        iOldStart=self.iStart
        self.iStart=iNewStart
        self.iEnd    = self.iStart+self.iMaxLines

        if self.iEnd > self.iCntLines:
            self.iEnd = self.iCntLines
            iRet = self.iBottom
        self.iStart = self.iEnd-self.iMaxLines
        if self.iStart<0:
            self.iStart=0
            iRet = self.iTop
        if (iOldStart==self.iStart) and not self.bNewText:
            return self.iNoScroll

        self.bNewText=False
        self.iRealLines=self.iEnd-self.iStart

        uText= '\n'.join(self.aText[self.iStart:self.iEnd])

        cScrollableLabel.on_text(self,self.oLabel,uText)

        if iRet != self.iNoScroll:
            return iRet

        if iOldStart<self.iStart:
            iLines=iOldStart-self.iStart
            if abs(iLines)==self.iWindowLines:
                iRet=self.iPageDown
            else:
                iRet= self.iEnd
                self.iScrollLines = iOldStart
        else:
            iLines=iOldStart-self.iStart
            if iLines==self.iWindowLines:
                iRet=self.iPageUp
            else:
                iRet= self.iTop
                self.iScrollLines = iOldStart

        '''
        print "********************"
        print "iRet:",iRet
        print "iLineheight:",self.iLineHeight
        print "iMaxlines:",self.iMaxLines
        print "iReallines:",self.iRealLines
        print "windowlines",self.iWindowLines
        print "start:", self.iStart
        print "end:", self.iEnd
        print "oldstart:", iOldStart
        print "ScrollLines:",self.iScrollLines
        '''

        return iRet

    def PageUp(self):
        return self.SetStart(self.iStart-self.iWindowLines)

    def PageDown(self):
        return self.SetStart(self.iStart+self.iWindowLines)

    def _set_height(self, instance, size):
        #self.iLineHeight=size[1]/self.iRealLines
        cScrollableLabel._set_height(self,instance,size)
        self.CalcLines()
        #Logger.debug("ScrollableLabelLarge used texture size:%d" %(self.iLineHeight*self.iMaxLines))

