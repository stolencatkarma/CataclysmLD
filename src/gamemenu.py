#! /usr/bin/env python
#
#    Various Menu interaces for use with Pygame
#    Copyright (C) 2001  Michael Urman
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
gamemenu:  baseclass and implementation for various game "menus."

Menu will allow you to add a graphical context menu to your games with
relative ease.  Examples of support types include:

    - Rotating Icons (like Secret of Mana) in class RotatingIconMenu
    - Circling Text (like The Sims) in class CircleTextMenu

Running this program instead of using it as a library will let you examine
several examples.

If you want more menu styles, implement a derived class (or tree) from
GameMenu or RadialMenu, and see the RotatingIconMenu and CircleTextMenu for
example code.

If you like the style of menu but want to change how icons/text/desc are
rendered, derive a class from the Icon, Text, or Desc with your own
render_str().  Then to use these, instead of
    menu.add_item(..., icon='file.png', ...)
    use menu.add_item(..., icon=MyIcon('file.png'), ...)
and similarly for text= and desc=
Example render_str() functions are available in Icon, Text, and Desc
classes.
"""

__version__ = '0.2'
__date__ = '2002/06/05'
__author__ = 'Michael Urman (mu on irc.openprojects.net)'

# watch me go out of my way to avoid needing the pygame.locals.* so as not to
# clutter the pydoc info :)
import pygame
import copy
try:
    import Numeric as _N
except ImportError:
    _N = None

class MenuAttribute:
    """MenuAttribute is the base of drawn menu attributes"""
    def __init__(self, *args):
        """MenuAttribute(*args) -> MenuAttribute

        Instantiates a MenuAttribute (or derived class) according to arguments.
        Currently the only accepted format is:

            - MenuAttribute(string) (meaning depends on the subclass)"""
        if len(args) == 1 and isinstance(args[0], type('')):
            self.render_str(args[0])
            self.dim = self.images[0].get_width(), self.images[0].get_height()
        elif len(args) == 1 and args[0] is None:
            self.dim = None
            self.images = None
        else:
            print( "args", args)
            raise ValueError("MenuAttribute initialization requires a string")

    def __getattr__(self, attr):
        """Quick access functionality to width, height, size, and rect"""
        if attr in ('width', 'height', 'size', 'rect'):
            return getattr(self, 'get_'+attr)()
        else:
            raise AttributeError("MenuAttribute instance has no attribute '%s'"%attr)

    def get_size(self):
        """get_size(self) -> width, height

        Return tuple of width and height of image"""
        return self.dim[:]

    def get_width(self):
        """get_width(self) -> width

        Return the width of image"""
        return self.dim[0]

    def get_height(self):
        """get_height(self) -> height

        Return the height of image"""
        return self.dim[1]

    def get_rect(self):
        """get_rect(self) -> rect

        Return the image's rect"""
        return self.images[0].get_rect()

    def get_image(self, image=0):
        """get_image(self, image=0) -> surf

        Return the image indexed by argument image"""
        return self.images[image]

    def render_str(self, str):
        raise NotImplementedError("render_str() was not implemented in the derived class")

    def desaturate(self, surf):
        """desaturate(self, surf) -> surf

        Creates a new surface and fills it with the greyscale according to the
        Gimp's Y = 0.3R + 0.59G + 0.11B"""

        if 0 and pygame.surfarray:
            rgbimg = pygame.surfarray.array3d(surf)
            rgbarray = _N.array(rgbimg)
            rgbarray[:] *= (0.3, 0.59, 0.11)
            return pygame.surfarray.make_surface(rgbarray)

        w, h = surf.get_size()
        desat = pygame.Surface((w,h), surf.get_flags(), surf)
        if desat.get_flags() & pygame.SRCALPHA:
            for y in range(h):
                for x in range(w):
                    r,g,b,a = surf.get_at((x,y))
                    lum = int(0.3*r + 0.59*g + 0.11*b)
                    desat.set_at((x,y), (lum,lum,lum, a))
        else:
            for y in range(h):
                for x in range(w):
                    r,g,b = surf.get_at((x,y))
                    lum = int(0.3*r + 0.59*g + 0.11*b)
                    desat.set_at((x,y), (lum,lum,lum))
        return desat

    def hilight(self, surf, color=(255,255,255), percent=0.33):
        """hilight(self, surf) -> surf

        Creates a new surface and fills it with a highlighted version by
        blitting a 33% white on top."""

        if 0 and pygame.surfarray:
            rgbimg = pygame.surfarray.array3d(surf)
            rgbarray = _N.array(rgbimg)
            diff = _N.zeros(rgbarray.shape)
            diff[:] = color
            diff = (diff - rgbarray) * percent
            return pygame.surfarray.make_surface(rgbarray + diff.astype(_N.Int))

        w, h = surf.get_size()
        srcp = 1-percent;
        hr, hb, hg = [chan * percent for chan in color]
        hilight = pygame.Surface((w,h), surf.get_flags(), surf)
        if hilight.get_flags() & pygame.SRCALPHA:
            for y in range(h):
                for x in range(w):
                    r,g,b,a = surf.get_at((x,y))
                    r = srcp*r + hr
                    g = srcp*g + hb
                    b = srcp*b + hg
                    hilight.set_at((x,y), (r,g,b,a))
        else:
            for y in range(h):
                for x in range(w):
                    r,g,b = surf.get_at((x,y))
                    r = srcp*r + hr
                    g = srcp*g + hg
                    b = srcp*b + hb
                    hilight.set_at((x,y), (r,g,b))
        return hilight

class Icon(MenuAttribute):
    """Icon abstracts the icons used in the RotatingIconMenu"""

    rendered = {}

    def render_str(self, str):
        """render_str(self, str) -> None

        Render a set of images for the icon, treating str as an icon file"""

        self.iconfile = str
        if str in Icon.rendered.keys():
            self.images = Icon.rendered[str]
        else:
            image = pygame.image.load(str)
            image_sel = self.hilight(image, (255,255,100), 0.4)
            image_disable = self.desaturate(image)
            self.images = (image, image_sel, image_disable)
            Icon.rendered[str] = self.images

class Desc(MenuAttribute):
    """Desc abstracts the description information"""

    FONT = None
    SIZE = 24
    COLOR = (255,255,255)

    rendered = {}

    def render_str(self, str):
        """render_str(self, str) -> None

        Render a set of images for the description, treating str as a title"""

        self.desc = str
        if str in Desc.rendered.keys():
            self.images = Desc.rendered[str]
        else:
            font = pygame.font.Font(Desc.FONT, Desc.SIZE)
            image = font.render(str, 1, Desc.COLOR)
            #image_sel = self.hilight(image)
            #image_disable = self.desaturate(image)
            #self.images = (image, image_sel, image_disable)
            self.images = (image, image, image)
            Desc.rendered[str] = self.images

class Text(MenuAttribute):
    """Text abstracts the text used in the CircleTextMenu"""

    FONT = None
    SIZE = 18
    COLOR = (255,255,255)
    BGCOLOR = (40,40,120)

    rendered = {}

    def render_str(self, str):
        """render_str(self, str) -> None

        Render a set of images for the text, treating str as a label"""

        self.text = str
        if str in Text.rendered.keys():
            self.images = Text.rendered[str]
        else:
            font = pygame.font.Font(Text.FONT, Text.SIZE)
            img = font.render(str, 1, Text.COLOR)
            w, h = img.get_size()
            # BUG?: following doesn't work without ", 32"
            textbg = pygame.Surface((w+h, h), pygame.SRCALPHA, 32)
            r = int(h/2.0)
            pygame.draw.circle(textbg, Text.BGCOLOR, (r,r), r, 0)
            pygame.draw.circle(textbg, Text.BGCOLOR, (w+r,r), r, 0)
            pygame.draw.rect(textbg, Text.BGCOLOR, (r, 0, w, h), 0)
            textbg.blit(img, (r,0))
            text_sel = self.hilight(textbg, (230, 230, 255), 0.2)
            text_dis = self.desaturate(textbg)
            self.images = (textbg, text_sel, text_dis)
            Text.rendered[str] = self.images

class Item:
    """Item abstracts the menu items with some convenience 'functions.'  In
    particular, accessing icon, title, and desc are merely item.icon, etc."""

    def __init__(self, kwargs):
        self.__dict__['_attr'] = kwargs

    def __getattr__(self, attr):
        try:
            return self.__dict__['_attr'][attr]
        except KeyError:
            raise AttributeError("Item instance has no attribute '%s'"%attr)

    def __setattr__(self, attr, val):
        if attr in self._attr.keys():
            orig = self.__dict__['_attr'][attr]
            if orig is None or isinstance(val, type(orig)):
                self.__dict__['_attr'][attr] = val
            else:
                raise ValueError("Item attribute '%s' must be of type '%s'"
                    % (attr,type(orig)))
        else:
            raise AttributeError("Item instance has no attribute '%s'"%attr)

class GameMenu:
    """GameMenu is the base which holds the common data for all menus"""

    def __init__(self, copyMenu=None):
        if copyMenu:
            self.items = copyMenu.items[:]
            self.ids = copyMenu.ids

            self.selectstyle = copyMenu.selectstyle
            self.selectevents = copy.copy(copyMenu.selectevents)
            self.eventtypecache = copy.copy(copyMenu.eventtypecache)
        else:
            self.items = []
            self.ids = {}

            self.selectstyle = None
            self.selectevents = {}
            self.eventtypecache = []

    def add_item(self, id, **kwargs):
        """add_item(self, id, **kwargs) -> None

        Add a menu item.  Suggested keywords include:
            icon, text, desc, submenu, visible, enabled"""

        if id in self.ids.keys():
            raise KeyError("Menu already has item with id '%s'"%id)

        kwargs['id'] = id
        # apply defaults to any missing standard arguments
        for kw in 'visible', 'enabled':
            if not kw in kwargs.keys():
                kwargs[kw] = 1
        for kw in 'submenu', 'icon':
            if not kw in kwargs.keys():
                kwargs[kw] = None
        for kw in 'text', 'desc':
            if not kw in kwargs.keys():
                kwargs[kw] = '[no %s]'%kw

        # convert desc if it's not a Desc
        if not isinstance(kwargs['desc'], Desc):
            kwargs['desc'] = Desc(kwargs['desc'])

        # convert icon if not an Icon
        if not isinstance(kwargs['icon'], Icon):
            kwargs['icon'] = Icon(kwargs['icon'])

        # convert text if it's passed in as a string
        if not isinstance(kwargs['text'], Text):
            kwargs['text'] = Text(kwargs['text'])

        self.items.append(Item(kwargs))
        self.ids[id] = self.items[-1]

    def del_item(self, *ids):
        """del_item(self, *ids) -> None

        Remove a menu item(s)"""

        self.items = [item for item in self.items if item.id not in ids]
        for id in ids:
            del self.ids[id]

    def item(self, id):
        """item(self, id) -> menu item

        Return a reference to menu item matching id"""

        return self.ids[id]

    def run(self):
        raise NotImplementedError

    def get_event(self):
        """get_event(self) -> menu event

        Return a menu event based on handlers set in set_events.  This will
        be one of 'select', 'cancel', 'next', 'prev', or None if a QUIT
        event is received."""

        if not self.eventtypecache:
            typecache = {}
            for menuevent in self.selectevents.values():
                for handle in menuevent:
                    typecache[handle[0]] = handle[0]
            types = typecache.keys()
            del typecache
            self.eventtypecache = types
        else:
            types = self.eventtypecache

        menuevent = None
        eventhandlers = self.selectevents.items()
        if self.selectstyle == 'hover':
            while not menuevent:
                event = pygame.event.wait()
                if event.type == pygame.MOUSEMOTION:
                    self.hoverpos = copy.copy(event.pos)
                    menuevent = 'hover'
                elif event.type in types:
                    for mevent, handlers in eventhandlers:
                        for type, attr, val in handlers:
                            if event.type==type and getattr(event, attr)==val:
                                menuevent = mevent

        else:
            while not menuevent:
                event = pygame.event.wait()
                if event.type in types:
                    for mevent, handlers in eventhandlers:
                        for type, attr, val in handlers:
                            if event.type==type and getattr(event, attr)==val:
                                menuevent = mevent
        return menuevent

    def get_hover_coords(self):
        """get_hover_coords(self) -> (x,y)

        return the current hover position, valid only after a get_event()
        returns 'hover'"""

        return self.hoverpos

    def set_style(self, style, params=None):
        """set_style(self, style, params=None) -> None

        sets the select style for the menu to one of: hover, event.  the
        default is a mouse hover with a left-click release over the drawn
        image.  params is an optional dictionary containing elements
        described in set_select_params()"""

        self.selectstyle = style
        if params: self.params = params

    def set_events(self, menuevent, *events):
        """set_events(self, menuevent, *events) -> None

        sets the events that generate a given menu event.  if *events is
        None, the menuevent is disabled.  otherwise each event should be a
        tuple of the form: (<EventType>, <keyword>, <val>).  an example
        tuple (MOUSEBUTTONUP, 'button', 1) describes a menuevent generation
        on the release of the left mouse button.

        valid menuevent values are the strings:
            select, cancel, next, prev"""

        if menuevent not in ('select', 'cancel', 'next', 'prev'):
            raise KeyError("menuevent '%s' is not valid"%menuevent)

        if not events:
            del self.selectevents[menuevent]
        else:
            self.selectevents[menuevent] = list(events)

    def set_items_enable(self, enable, *ids):
        """set_items_enable(self, enable, *ids) -> None

        sets 'enabled' to enable for all ids.  enabled items (enable=1)
        should be selectable; disabled items (enable=0) should be visible
        but cannot be selected"""

        for id in ids:
            try:
                self.ids[id].enabled = enable
            except KeyError:
                pass    # allow None as a valid id

    def set_items_visible(self, visible, *ids):
        """set_items_visible(self, visible, *ids) -> None

        sets 'visible' to visible for all ids.  visible items (visible=1)
        should be drawn; invisible items (visible=0) should not be drawn and
        hence skipped over in the selection process as well"""

        for id in ids:
            try:
                self.ids[id].visible = visible
            except KeyError:
                pass    # allow None as a valid id

    def set_item_icon(self, id, icon):
        """set_item_icon(self, id, icon) -> None

        sets item's icon for the given id.  icon should be an Icon or a string
        holding the path to an icon file."""

        if not isinstance(icon, Icon):
            icon = Icon(icon)
        self.ids[id].icon = icon

    def set_item_desc(self, id, desc):
        """set_item_desc(self, id, desc) -> None

        sets item's title for the given id.  desc should be a Desc or a
        string"""

        if not isinstance(desc, Desc):
            desc = Desc(desc)
        self.ids[id].desc = desc

class RadialMenu(GameMenu):
    """Base class for radial menus; not a functional menu itself"""

    def __init__(self, copyMenu=None):
        GameMenu.__init__(self, copyMenu)
        if not copyMenu:
            self.rotatecount = 0
            self.rotateradius = (100, 100)
            self.skewalongaxis = (0, 0)
        else:
            self.rotatecount = copyMenu.rotatecount
            self.rotateradius = copyMenu.rotateradius
            self.skewalongaxis = copyMenu.skewalongaxis

    def set_radius(self, radius):
        """set_radius(self, radius) -> none

        Choose the radius in pixels for the rotating menu.  radius can
        either be a single number, or a tuple of (x,y) radii for an axially
        aligned ellipse."""

        if isinstance(radius, type(0.0)) or isinstance(radius, type(0)):
            self.rotateradius = (radius, radius)
        elif isinstance(radius, type(())) or isinstance(radius, type([])):
            if len(radius) == 2:
                self.rotateradius = tuple(radius)
            else:
                raise ValueError("set_radius requires a tuple of length 2")
        else:
            raise ValueError("set_radius requires a number or a length 2 tuple")

    def set_rotatecount(self, count):
        """set_rotatecount(self, count) -> None

        Set the selected item location in counter-clockwise spots from the
        top center"""

        self.rotatecount = float(count)

    def set_skew(self, axis):
        """set_skew(self, axis) -> None

        Choose the radius in pixels for the rotating menu.  radius is a
        tuple of (x,y) skew factors."""

        if isinstance(axis, type(())) or isinstance(axis, type([])) and len(axis)==2:
            self.skewalongaxis = tuple(axis)
        else:
            raise ValueError("set_skew requires a length 2 tuple")


class RotatingIconMenu(RadialMenu):
    """RotatingIconMenu implements a menu system like Secret of Mana's"""

    def __init__(self, copyMenu=None):
        RadialMenu.__init__(self, copyMenu)
        if not copyMenu:
            self.set_style('event')
            KBD = pygame.KEYDOWN
            self.set_events('select', (KBD, 'key', pygame.K_RETURN))
            self.set_events('next', (KBD, 'key', pygame.K_RIGHT))
            self.set_events('prev', (KBD, 'key', pygame.K_LEFT))
            self.set_events('cancel', (KBD, 'key', pygame.K_ESCAPE))

    def run(self, center, screen):
        """run(self, center, screen) -> Selection

        Display the Rotating Icon Menu centered around center and handle
        events until the menu is cancelled or an item is selected.  Return
        None or the Item correspondingly"""

        from math import pi, sin, cos

        try:
            cx, cy = center
        except ValueError:
            raise ValueError("center must be a tuple of (x, y)")
        except TypeError:
            raise ValueError("center must be a tuple of (x, y)")

        try:
            screencopy = pygame.Surface(
                (screen.get_width(), screen.get_height()),
                pygame.HWSURFACE, screen)
            screencopy.blit(screen, (0,0))
        except AttributeError:
            raise ValueError("screen must be a surface")

        if screen.get_flags() & pygame.DOUBLEBUF:
            draw = self._drawdoublebuf
        else:
            draw = self._drawsinglebuf

        items = [item for item in self.items if item.visible ]
        nitems = len(items)

        incr = 1/100.0
        rx, ry = self.rotateradius
        sx, sy = self.skewalongaxis
        rot = self.rotatecount
        try:
            angle = 2*pi/nitems
        except ZeroDivisionError:
            raise ValueError("No menu items defined")
        sel = 0
        osel = 0
        cur = sel - incr
        opos = None

        do_exit = 0
        chose = None
        while not do_exit:
            while abs(sel-cur)>=incr:
                if cur < sel: cur += incr
                if cur > sel: cur -= incr
                angles = [angle*(i-cur-rot) for i in range(nitems)]
                pos = [(cx + rx*sin(t) + sx*cos(t),
                        cy - ry*cos(t) + sy*sin(t))
                        for t in angles]
                draw(screen, screencopy, items, pos, opos, sel, osel)
                opos = pos[:]
                osel = sel

            event = self.get_event()
            if event == 'next':
                sel = (sel + 1) % nitems
                if sel < cur: cur -= nitems
            elif event == 'prev':
                sel = (sel + nitems - 1) % nitems
                if sel > cur: cur += nitems
            elif event == 'cancel' or event == None:
                do_exit = 1
            elif event == 'select':
                if items[sel].enabled:
                    try:
                        chose = items[sel]
                    except IndexError:
                        chose = None
                    do_exit = 1

        if opos:
            draw(screen, screencopy, items, None, opos, sel, osel)

        try:
            return chose.id
        except AttributeError:
            return None

    def _drawsinglebuf(self, screen, back, items, pos, opos, sel, osel):
        """_drawsinglebuf(self, screen, back, items, pos, opos, sel, osel) -> None

        Draws items to a single-buffer screen with corresponding positions
        (if passed), erasing old positions (if passed)."""

        dirtyrects = []
        # remove all old stuff if positions passed
        if opos:
            # clear all icons
            for item, op in zip(items, opos):
                w, h = item.icon.size
                rect = (op[0]-w/2, op[1]-h/2, w, h)
                screen.blit(back, op, rect)
                dirtyrects.append(rect)

            # clear description
            rect = items[osel].desc.rect
            screen.blit(back, rect)
            dirtyrects.append(rect)

        # draw all new stuff if posistions passed
        if pos:
            # draw a hilight around the selected item
            #p = pos[sel]
            #w, h = items[sel].icon.size
            #pygame.draw.rect(screen, (100,255,100), (p[0]-w/2, p[1]-h/2, w, h), 1)
            # draw all items
            for item, p, k in zip(items, pos, range(len(items))):
                icon = item.icon
                # center the icon around pos
                w, h = icon.size
                p = (p[0]-w/2, p[1]-h/2)
                image = (item.enabled and [k==sel] or [2])[0]
                screen.blit(icon.get_image(image), p, icon.rect)
                dirtyrects.append((p[0], p[1], w, h))
            screen.blit(items[sel].desc.get_image(), (0,0))
            dirtyrects.append(items[sel].desc.rect)

        pygame.display.update(dirtyrects)

    def _drawdoublebuf(self, screen, back, items, pos, opos, sel, osel):
        """_drawdoublebuf(sel, screen, back, items, pos, opos, sel, osel) -> None

        Draws items to a double-buffer screen with corresponding positions
        (if passed), erasing old positions (if passed)."""

        if opos:
            screen.blit(back, (0,0))

        if pos:
            # draw all icons
            for item, p, k in zip(items, pos, range(len(items))):
                icon = item.icon
                # center the icon around pos
                w, h = icon.size
                p = (p[0]-w/2, p[1]-h/2)
                image = (item.enabled and [k==sel] or [2])[0]
                screen.blit(icon.get_image(image), p, icon.rect)
            # draw selected item's description
            screen.blit(items[sel].desc, (0,0))

        pygame.display.flip()

class CircleTextMenu(RadialMenu):
    """CircleTextMenu implements a menu system like The Sims uses (minus the
    floating head)"""

    def __init__(self, copyMenu=None):
        RadialMenu.__init__(self, copyMenu)
        if not copyMenu:
            self.set_style('hover')
            KBD = pygame.KEYDOWN
            self.set_events('select', (pygame.MOUSEBUTTONUP, 'button', 1))
            self.set_events('cancel', (KBD, 'key', pygame.K_ESCAPE),
                            (pygame.MOUSEBUTTONDOWN,'button',3))

    def run(self, center, screen):
        """run(self, center, screen) -> Selection

        Display the Circle Text Menu centered around center and handle
        events until the menu is cancelled or an item is selected.  Return
        None or the Item correspondingly"""

        from math import pi, sin, cos

        try:
            cx, cy = center
        except ValueError:
            raise ValueError("center must be a tuple of (x, y)")
        except TypeError:
            raise ValueError("center must be a tuple of (x, y)")

        try:
            screencopy = pygame.Surface(
                (screen.get_width(), screen.get_height()),
                pygame.HWSURFACE, screen)
            screencopy.blit(screen, (0,0))
        except AttributeError:
            raise ValueError("screen must be a surface")

        if screen.get_flags() & pygame.DOUBLEBUF:
            draw = self._drawdoublebuf
        else:
            draw = self._drawsinglebuf

        items = [item for item in self.items if item.visible]
        nitems = len(items)

        incr = 1/16.0
        rx, ry = self.rotateradius
        sx, sy = self.skewalongaxis
        rot = self.rotatecount
        try:
            angle = 2*pi/nitems
        except ZeroDivisionError:
            raise ValueError("No menu items defined")

        sel = None
        osel = None
        do_exit = 0
        chose = None
        angles = [angle*(i-rot) for i in range(nitems)]
        pos = [(cx + rx*sin(t) + sx*cos(t) - s[0]/2,
                cy - ry*cos(t) + sy*sin(t) - s[1]/2)
                for t, s in zip(angles, [i.text.size for i in items])]

        trect = [pygame.Rect(p[0], p[1], t[0], t[1])
                    for p, t in zip(pos, [i.text.size for i in items])]

        while not do_exit:
            draw(screen, screencopy, items, pos, sel, osel)
            osel = sel

            event = self.get_event()
            if event == 'cancel' or event == None:
                do_exit = 1
            elif event == 'hover':
                x,y = self.get_hover_coords()
                for i, rect in zip(range(nitems), trect):
                    if rect.collidepoint(x,y):
                        sel = i
                        break
                else:
                    sel = None

            elif event == 'select' and sel is not None:
                if items[sel].enabled:
                    try:
                        chose = items[sel]
                    except IndexError:
                        chose = None
                    do_exit = 1

        draw(screen, screencopy, items, pos, sel, osel, clear=1)

        try:
            return chose.id
        except AttributeError:
            return None

    def _drawsinglebuf(self, screen, back, items, pos, sel, osel, clear=0):
        """_drawsinglebuf(self, screen, back, items, pos, sel, osel, clear=0) -> None

        Draws items to a single-buffer screen with corresponding positions
        or erase if clear=1."""

        dirtyrects = []
        # remove all old stuff if clear
        if clear:
            for item, op in zip(items, pos):
                text = item.text
                rect = (op[0], op[1], text.width, text.height)
                screen.blit(back, op, rect)
                dirtyrects.append(rect)
            if osel is not None:
                rect = items[osel].desc.rect
                screen.blit(back, rect)
                dirtyrects.append(rect)

        # draw all new stuff if not clear
        else:
            for item, p, k in zip(items, pos, range(len(items))):
                image = (item.enabled and [k==sel] or [2])[0]
                text = item.text
                screen.blit(text.get_image(image), p, text.rect)
                dirtyrects.append((p[0], p[1], text.width, text.height))

            if sel != osel:
                if osel is not None and items[osel].enabled:
                    rect = items[osel].desc.rect
                    screen.blit(back, (0,0), rect)
                    dirtyrects.append(rect)
                if sel is not None and items[sel].enabled:
                    screen.blit(items[sel].desc.get_image(), (0,0))
                    dirtyrects.append(items[sel].desc.rect)

        pygame.display.update(dirtyrects)

    def _drawdoublebuf(self, screen, back, items, pos, sel, osel, clear=0):
        """_drawdoublebuf(self, screen, back, items, pos, sel, osel, clear=0) -> None

        Draws items to a double-buffer screen with corresponding positions
        or erase if clear=1."""

        if clear:
            screen.blit(back, (0,0))
        else:
            for item, p, k in zip(items, pos, range(len(items))):
                image = (item.enabled and [k==sel] or [2])[0]
                screen.blit(item.text.get_image(image), p, item.text.rect)
            screen.blit(items[sel].desc.get_image(), (0,0))

        pygame.display.flip()


def _main():
    """Test the functionality of the menus if run as a program"""

    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
    pygame.display.flip()

        # test the rotating Icon menu (Secret of Mana style)
    rmenu = RotatingIconMenu()
    rmenu.set_radius((150,100))
    rmenu.set_skew((0,0))
    try:
        rmenu.add_item('Craft', icon='./tilemap/1178.png', desc='Craft')
        rmenu.add_item('Construct', icon='./tilemap/1179.png', desc='Construct')
        rmenu.add_item('Settings', icon='./tilemap/1177.png', desc='Settings')
        rmenu.add_item('Examine', icon='./tilemap/1176.png', desc='Examine')
        rmenu.add_item('Inventory', icon='./tilemap/1175.png', desc='Inventory')
        rmenu.add_item('World Map', icon='./tilemap/1174.png', desc='World Map')
    except pygame.error:
        print ("""
        Chances are one or more of the icons in the menu.add_item() lines
        aren't available.  Try changing them to icons that exist on your
        system and/or commenting some of them out.
        """)
        raise SystemExit("Probably Missing Icons")

    rmenu.set_items_enable(0, 'paintbrush', 'a', 'c', 'e')
    rmenu.run((320,240), screen)


if __name__ == '__main__': _main()
