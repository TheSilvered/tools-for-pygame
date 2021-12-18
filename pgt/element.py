import pygame
import time
from .pos_size import Pos, Size
from .exceptions import InvalidPosError
from .mathf import clamp
from typing import Union, Optional
pygame.init()


class Anc:
    UL = "ul"
    UC = "uc"
    UR = "ur"
    CL = "cl"
    CC = "cc"
    CR = "cr"
    DL = "dl"
    DC = "dc"
    DR = "dr"


attr_correspondence = {
    "ul": "topleft",
    "uc": "midtop",
    "ur": "topright",
    "cl": "midleft",
    "cc": "center",
    "cr": "midright",
    "dl": "bottomleft",
    "dc": "midbottom",
    "dr": "bottomright"
}


class Element(pygame.sprite.Sprite):
    """
    Element(pygame.sprite.Sprite)

    Type: class

    Description: base class that supports a position, an image, a size,
        a rotation and an alpha

    Args:
        'pos' (pgt.Pos): the position of the element
        'size' (pgt.Size): the size of the element, defaults to (0, 0)
        'image' (pygame.Surface): the image of the element, if set to
            None the element won't be displayed
        'pos_point' (pgt.Anc): the point the position refers to, check
            help(pgt.Anc) to all the valid values
        'anchor_element' (pgt.Element): element to witch this element is
            anchored to, if set there is no need to set the 'pos'
            argument
        'anchor_point' (pgt.Anc): the point of the 'anchor_element' that
            this element anchors to, defaults to pgt.Anc.UL
        'offset' (pgt.Pos): the offset of the element from 'pos' or the
            point of the 'anchor_element'
        'img_offset' (pgt.Pos): offset of the image from the top-left
            corner of the element
        'alpha' (int): transparency of the element (from 0 to 255),
            doesn't rise errors, the value is camped
        'rotation' (int): rotation in degrees of the element
        'hidden' (boon): if the element is hidden

    Attrs:
        'rect' (pygame.Rect): rect of the element with position and size
        'image' (pygame.Surface?): see 'image' in arguments
        '__backup_image' (pygame.Surface?): if the element is rotated,
            is a copy of 'image' not rotated, to not lose quality
        '_pos_point' (pgt.Anc): see 'pos_point' in arguments
        '__a_element' (pgt.Element?): see 'anchor_element' in arguments
        '_a_point' (pgt.Anc?): see 'anchor_point' in arguments
        'offset' (pgt.Pos): see 'offset' in arguments
        'img_offset' (pgt.Pos): see 'img_offset' in arguments
        'alpha' (int): see 'alpha in arguments'
        '_rot' (int): the current rotation of the element in degrees
        'hidden' (bool): if the element is currently hidden
        'u' (int): up
        'd' (int): down
        'l' (int): left
        'r' (int): right
        'ul' (pgt.Pos): up-left
        'uc' (pgt.Pos): up-centre
        'ur' (pgt.Pos): up-right
        'cl' (pgt.Pos): centre-left
        'cc' (pgt.Pos): centre-centre
        'cr' (pgt.Pos): centre-right
        'dl' (pgt.Pos): down-left
        'dc' (pgt.Pos): down-centre
        'dr' (pgt.Pos): down-right
        'pos' (pgt.Pos): position of the '_pos_point' of the element
        'size' (pgt.Size): size of the element

    Methods:
        'rotate(angle, abs_=False, colorkey=pgt.BLACK)' (None):
            rotates the element around '_pos_point'
            'angle' (int): angle of the rotation in degrees
            'abs_' (bool): if the rotation should be absolute
            'colorkey' (iterable): the colorkey set to the image of the
                element after it's been rotated
        'scale(size, smooth=False, point=None)' (None): scales the
            element relative to 'point', if 'point' is None, is relative
            to 'pos_point'
            'smooth' (bool): if the function should use
                'pygame.transform.smoothscale' instead of
                'pygame.transform.scale'
            'point' (Pos): point
        'collide(other)' (bool): returns if this element is colliding
            with another element
            'other' (pygame.Rect, pygame.sprite.Sprite): the object to
                check the collision against
        'collide_point(point)' (bool): returns if a point is colliding
            with this element
            'point' (pgt.Pos): the point to check
        'show()' (None): shows the element
        'hide()' (None): hides the element
        'draw(surface, pos=None, point=pgt.Anc.UL, offset=None, flags=0
              show_rect=False, rect_color=pgt.MAGENTA)': draws the
            element's image on 'surface'
            'surface' (pygame.Surface): the surface to draw the image on
            'pos' (pgt.Pos): a position that overwrites the element's
                pos
            'point' (pgt.Anc): used only when 'pos' is not None, the
                point the position refers to
            'offset' (pgt.Pos): offset from the actual position, if
                set to None the element's offset is used, if set it's
                overwritten
            'flags' (int): special flags for pygame.Surface.blit,
                see the documentation at
                www.pygame.org/docs/ref/surface.html#pygame.Surface.blit
            'show_rect' (bool): if the rect of the element should be
                shown
            'rect_color' (tuple): the color of the rect if shown
    """
    def __init__(self,
       pos=None,
       size=Size(0),
       image=None,
       pos_point=Anc.UL,
       anchor_element=None,
       anchor_point=Anc.UL,
       offset=Pos(0),
       img_offset=Pos(0),
       alpha=255,
       rotation=0,
       hidden=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((0, 0), size)
        self.image = image
        self.__backup_image = None if rotation == 0 else image

        if self.image: self.image.set_alpha(clamp(alpha, 0, 255))
        self._alpha = alpha

        self.__offset = Pos(offset)
        self.img_offset = Pos(img_offset)

        if pos is not None:
            setattr(self, pos_point, pos + self.__offset)
            self.__a_element = None
            self._a_point = None
        elif anchor_element is not None:
            self.__a_element = anchor_element
            self._a_point = anchor_point
            setattr(self, pos_point,
                    getattr(self.__a_element, self._a_point) + self.__offset
            )
        else:
            raise InvalidPosError(f"Element {id(self)} needs a position")\
                  from None

        self.hidden = hidden

        self._pos_point = pos_point
        self._rot = 0
        if rotation != 0:
            if self.image is not None:
                self.rotate(rotation)
            else:
                self._rot = rotation

    def __eq__(self, other):
        return self.size == other.size \
               and self.image == other.image \
               and self._rot == other._rot \
               and self._alpha == other._alpha

    @property
    def u(self): return self.rect.top
    @property
    def d(self): return self.rect.bottom
    @property
    def l(self): return self.rect.left
    @property
    def r(self): return self.rect.right
    @property
    def ul(self): return Pos(self.rect.topleft)
    @property
    def uc(self): return Pos(self.rect.midtop)
    @property
    def ur(self): return Pos(self.rect.topright)
    @property
    def cl(self): return Pos(self.rect.midleft)
    @property
    def cc(self): return Pos(self.rect.center)
    @property
    def cr(self): return Pos(self.rect.midright)
    @property
    def dl(self): return Pos(self.rect.bottomleft)
    @property
    def dc(self): return Pos(self.rect.midbottom)
    @property
    def dr(self): return Pos(self.rect.bottomright)

    @u.setter
    def u(self, value): self.rect.top = round(value)
    @d.setter
    def d(self, value): self.rect.bottom = round(value)
    @l.setter
    def l(self, value): self.rect.left = round(value)
    @r.setter
    def r(self, value): self.rect.right = round(value)
    @ul.setter
    def ul(self, value): self.rect.topleft = round(Pos(value))
    @uc.setter
    def uc(self, value): self.rect.midtop = round(Pos(value))
    @ur.setter
    def ur(self, value): self.rect.topright = round(Pos(value))
    @cl.setter
    def cl(self, value): self.rect.midleft = round(Pos(value))
    @cc.setter
    def cc(self, value): self.rect.center = round(Pos(value))
    @cr.setter
    def cr(self, value): self.rect.midright = round(Pos(value))
    @dl.setter
    def dl(self, value): self.rect.bottomleft = round(Pos(value))
    @dc.setter
    def dc(self, value): self.rect.midbottom = round(Pos(value))
    @dr.setter
    def dr(self, value): self.rect.bottomright = round(Pos(value))

    @property
    def pos(self):
        return getattr(self, self._pos_point)

    @pos.setter
    def pos(self, value):
        setattr(self, self._pos_point, value)

    @property
    def size(self):
        return Size(self.rect.size)

    @size.setter
    def size(self, value):
        self.rect.size = round(Size(value))

    @property
    def offset(self):
        return self.__offset

    @offset.setter
    def offset(self, value):
        value = Pos(value)
        self.pos -= self.__offset
        self.pos += value
        self.__offset = value

    @property
    def alpha(self):
        if self.image: return self.image.get_alpha()
        else: return 0

    @alpha.setter
    def alpha(self, value):
        if self.image: self.image.set_alpha(clamp(value, 0, 255))
        self._alpha = value

    def rotate(self, angle, abs_=False, colorkey=(0, 0, 0)):
        prev_pos = self.pos.copy()

        if self.__backup_image is None:
            self.__backup_image = self.image.copy()
        elif self.__backup_image is not None:
            self.image = self.__backup_image.copy()

        self.image.set_colorkey(colorkey)

        if abs_:
            self.image = pygame.transform.rotate(self.image, angle)
            self._rot = angle
        else:
            self.image = pygame.transform.rotate(self.image, self._rot + angle)
            self._rot += angle

        self._rot %= 360

        self.size = self.image.get_size()
        self.image.set_colorkey(colorkey)

        self.pos = prev_pos

    def scale(self, size, smooth=False, point=None):
        if self.__backup_image is None:
            self.__backup_image = self.image.copy()
        else:
            self.image = self.__backup_image.copy()
        size = Size(size)
        prev_pos = self.pos.copy() if point is None else getattr(self, point)
        if smooth:
            self.image = pygame.transform.smoothscale(self.image, size)
        else:
            self.image = pygame.transform.scale(self.image, size)
        self.size = size
        if point is None:
            self.pos = prev_pos
        else:
            setattr(self, point, prev_pos)

    def change_image(self, surface):
        self.image = surface
        self.image.set_alpha(self._alpha)
        if self.__backup_image is not None:
            self.__backup_image = self.image.copy()
        self.rotate(self._rot, True)

    def collide(self, other):
        if self.hidden: return False

        if isinstance(other, pygame.sprite.Sprite):
            return self.rect.colliderect(other.rect)
        elif isinstance(other, pygame.Rect):
            return self.rect.colliderect(other)
        else:
            raise TypeError("Expected 'other' to be pygame.Rect or "
                           f"pygame.sprite.Sprite, got '{type(other)}'"
                            " instead") from None

    def collide_point(self, point):
        if self.hidden: return False
        return self.rect.collidepoint(point)

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True

    def draw(self,
       surface,
       pos=None,
       point=Anc.UL,
       offset=None,
       flags=0,
       show_rect=False,
       rect_color=(255, 0, 255)):

        if self.hidden or self.image is None: return

        if pos is None and self.__a_element is not None:
            self.pos = getattr(self.__a_element, self._a_point) + self.__offset

        if pos is None:
            pos = self.ul
        elif isinstance(pos, pygame.Rect):
            pos = pos.topleft

        if offset is not None: pos += offset
        else: pos += self.img_offset

        surface.blit(self.image, pos, special_flags=flags)

        if show_rect: pygame.draw.rect(surface, rect_color, self.rect, 1)


class AniElement(Element):
    """
    AniElement(Element)

    Type: class

    Description: Element that supports animations, for more about the
        elements see 'help(pgt.Element)' for more about animations,
        see 'help(pgt.animations)'

    Args:
        'animations' (list): a list that contains all the animations of
            the element (the 'element' argument of the animations is
            set automatically)

        *args, **kwargs: see help(pgt.Element)

    Attrs:
        'current_ani' (list[str]): the names of the animations that are
            currently running
        any animation can be accessed as an attribute named after the
        name of the animation (to access an animation called "jump" of
        'player_sprite' you write 'player_sprite.jump')

    Methods:
        'add_ani(ani)' (None): adds 'ani' to the element's animations
            'ani' (pgt.animations.AniBase): the animation you are adding
        'update_ani(global_time=None)' (None): calls update() on all
            the animations currently running
            'global_time' (float): the time at which the update takes
                place, if set to None is the current computer time
        'draw(update_ani=False, *args, **kwargs)' (None): if the
            animations should be updated, 'update_ani', in order, comes
            after 'rect_color'

    Notes:
        - if the element is hidden all the animations are still updated
    """
    def __init__(self,
       animations=None,
       *args, **kwargs):
        super().__init__(*args, **kwargs)

        if animations is None: animations = ()

        for i in animations:
            setattr(self, i.name, i)
            i.e = self

        self.current_ani = []

    def add_ani(self, ani):
        setattr(self, ani.name, ani)
        ani.e = self

    def update_ani(self, global_time=None):
        if global_time is None:
            global_time = time.time()
        for i in self.current_ani:
            getattr(self, i[0]).update(global_time)

        # Doesn't run if the update method stops the animation
        for i in self.current_ani:
            getattr(self, i[0]).set_element()

    def draw(self, *args, **kwargs):
        if "update_ani" in kwargs:
            if kwargs["update_ani"]: self.update_ani()
            del kwargs["update_ani"]
        elif len(args) == 8:
            if args[7]: self.update_ani()
            args = args[:7]
        else:
            self.update_ani()
        super().draw(*args, **kwargs)


class MouseInteractionElement(Element):
    """
    MouseInteractionElement(Element)

    Type: class

    Description: element that keeps track of the interactions it has
        with the mouse cursor

    Attrs:
        'hovered' (bool): if the mouse is over the rect of the element
        'clicked' (tuple[bool]): returns a tuple with the buttons
            that are clicking the element, at index 0 is the leftmost
            button, at index 1 the middlemost one ant at index 2 the
            rightmost one
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # These prevent that the element is considered clicked when
        # the mouse enters already clicking
        self.__prev_hovered = False
        self.__keep_clicked = False

    @property
    def hovered(self):
        if self.hidden: return False

        in_area = self.collide_point(pygame.mouse.get_pos())

        if not any(pygame.mouse.get_pressed()) and in_area:
            self.__prev_hovered = True
            self.__keep_clicked = False
        elif not in_area:
            self.__prev_hovered = False
            self.__keep_clicked = False

        return in_area

    @property
    def clicked(self):
        if not self.hovered: return False, False, False

        if not self.ul < Pos(pygame.mouse.get_pos()) < self.dr:
            return False, False, False

        if not (self.__prev_hovered or self.__keep_clicked):
            return False, False, False

        self.__prev_hovered = False
        self.__keep_clicked = True

        return pygame.mouse.get_pressed()


class MouseInteractionAniElement(MouseInteractionElement, AniElement):
    """
    MouseInteractionAniElement(MouseInteractionElement, AniElement)

    Type: class

    Description: a MouseInteractionElement that supports animations
    """
    pass