from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import groupdocs.watermark
import groupdocs.watermark.common
import groupdocs.watermark.contents
import groupdocs.watermark.contents.diagram
import groupdocs.watermark.contents.email
import groupdocs.watermark.contents.image
import groupdocs.watermark.contents.pdf
import groupdocs.watermark.contents.presentation
import groupdocs.watermark.contents.spreadsheet
import groupdocs.watermark.contents.wordprocessing
import groupdocs.watermark.exceptions
import groupdocs.watermark.internal
import groupdocs.watermark.options
import groupdocs.watermark.options.diagram
import groupdocs.watermark.options.email
import groupdocs.watermark.options.image
import groupdocs.watermark.options.pdf
import groupdocs.watermark.options.presentation
import groupdocs.watermark.options.spreadsheet
import groupdocs.watermark.options.wordprocessing
import groupdocs.watermark.search
import groupdocs.watermark.search.objects
import groupdocs.watermark.search.searchcriteria
import groupdocs.watermark.search.watermarks
import groupdocs.watermark.watermarks
import groupdocs.watermark.watermarks.results

class Color:
    '''Structure representing a color.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_argb(argb : int) -> groupdocs.watermark.watermarks.Color:
        '''Creates a :py:class:`groupdocs.watermark.watermarks.Color` structure from a 32-bit ARGB value.
        
        :param argb: A value specifying the 32-bit ARGB value.
        :returns: The :py:class:`groupdocs.watermark.watermarks.Color` structure that this method creates.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_argb(alpha : int, base_color : groupdocs.watermark.watermarks.Color) -> groupdocs.watermark.watermarks.Color:
        '''Creates a :py:class:`groupdocs.watermark.watermarks.Color` structure from the specified :py:class:`groupdocs.watermark.watermarks.Color` structure,
        but with the new specified alpha value.
        
        :param alpha: The alpha value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param base_color: The :py:class:`groupdocs.watermark.watermarks.Color` from which to create the new :py:class:`groupdocs.watermark.watermarks.Color`.
        :returns: The :py:class:`groupdocs.watermark.watermarks.Color` that this method creates.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_argb(red : int, green : int, blue : int) -> groupdocs.watermark.watermarks.Color:
        '''Creates a :py:class:`groupdocs.watermark.watermarks.Color` structure from the specified 8-bit color values (red, green, and blue) and
        the alpha value is implicitly 255 (fully opaque).
        
        :param red: The red component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param green: The green component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param blue: The blue component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :returns: The :py:class:`groupdocs.watermark.watermarks.Color` that this method creates.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_argb(alpha : int, red : int, green : int, blue : int) -> groupdocs.watermark.watermarks.Color:
        '''Creates a :py:class:`groupdocs.watermark.watermarks.Color` structure from the four ARGB component  (alpha, red, green, and blue) values.
        
        :param alpha: The alpha component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param red: The red component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param green: The green component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :param blue: The blue component value for the new :py:class:`groupdocs.watermark.watermarks.Color`. Valid values are 0 through 255.
        :returns: The :py:class:`groupdocs.watermark.watermarks.Color` that this method creates.'''
        raise NotImplementedError()
    
    def to_argb(self) -> int:
        '''Gets the 32-bit ARGB value of this :py:class:`groupdocs.watermark.watermarks.Color` structure.
        
        :returns: The 32-bit ARGB value of this :py:class:`groupdocs.watermark.watermarks.Color` structure.'''
        raise NotImplementedError()
    
    def get_hue(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) hue value, in degrees, for this :py:class:`groupdocs.watermark.watermarks.Color` structure.
        
        :returns: The hue, in degrees, of this :py:class:`groupdocs.watermark.watermarks.Color`. The hue is measured in degrees, ranging from 0.0
        through 360.0, in HSB color space.'''
        raise NotImplementedError()
    
    def get_saturation(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) saturation value for this :py:class:`groupdocs.watermark.watermarks.Color` structure.
        
        :returns: The saturation of this :py:class:`groupdocs.watermark.watermarks.Color`. The saturation ranges from 0.0 through 1.0,
        where 0.0 is grayscale and 1.0 is the most saturated.'''
        raise NotImplementedError()
    
    def get_brightness(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) brightness value for this :py:class:`groupdocs.watermark.watermarks.Color` structure.
        
        :returns: The brightness of this :py:class:`groupdocs.watermark.watermarks.Color`. The brightness ranges from 0.0 through 1.0,
        where 0.0 represents black and 1.0 represents white.'''
        raise NotImplementedError()
    
    def equals(self, other : groupdocs.watermark.watermarks.Color) -> bool:
        '''Determines whether the specified :py:class:`groupdocs.watermark.watermarks.Color` structure is equivalent to this :py:class:`groupdocs.watermark.watermarks.Color` structure.
        
        :param other: The color to test.
        :returns: True if other is equivalent to this :py:class:`groupdocs.watermark.watermarks.Color` structure; otherwise, false.'''
        raise NotImplementedError()
    
    @property
    def empty(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def transparent(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def alice_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def antique_white(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def aqua(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def aquamarine(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def azure(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def beige(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def bisque(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def black(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def blanched_almond(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def blue_violet(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def brown(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def burly_wood(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def cadet_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def chartreuse(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def chocolate(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def coral(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def cornflower_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def cornsilk(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def crimson(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def cyan(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_cyan(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_goldenrod(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_khaki(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_magenta(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_olive_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_orange(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_orchid(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_salmon(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_sea_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_slate_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_slate_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_turquoise(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dark_violet(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def deep_pink(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def deep_sky_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dim_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def dodger_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def firebrick(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def floral_white(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def forest_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def fuchsia(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def gainsboro(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def ghost_white(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def gold(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def goldenrod(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def green_yellow(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def honeydew(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def hot_pink(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def indian_red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def indigo(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def ivory(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def khaki(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lavender(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lavender_blush(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lawn_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lemon_chiffon(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_coral(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_cyan(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_goldenrod_yellow(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_pink(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_salmon(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_sea_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_sky_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_slate_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_steel_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def light_yellow(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lime(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def lime_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def linen(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def magenta(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def maroon(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_aquamarine(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_orchid(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_purple(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_sea_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_slate_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_spring_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_turquoise(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def medium_violet_red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def midnight_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def mint_cream(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def misty_rose(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def moccasin(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def navajo_white(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def navy(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def old_lace(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def olive(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def olive_drab(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def orange(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def orange_red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def orchid(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def pale_goldenrod(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def pale_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def pale_turquoise(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def pale_violet_red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def papaya_whip(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def peach_puff(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def peru(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def pink(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def plum(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def powder_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def purple(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def red(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def rosy_brown(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def royal_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def saddle_brown(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def salmon(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def sandy_brown(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def sea_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def sea_shell(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def sienna(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def silver(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def sky_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def slate_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def slate_gray(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def snow(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def spring_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def steel_blue(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def tan(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def teal(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def thistle(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def tomato(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def turquoise(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def violet(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def wheat(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def white(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def white_smoke(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def yellow(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def yellow_green(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets a system-defined color.'''
        raise NotImplementedError()

    @property
    def r(self) -> int:
        '''Gets the red component value of the color.'''
        raise NotImplementedError()
    
    @property
    def g(self) -> int:
        '''Gets the green component value of the color.'''
        raise NotImplementedError()
    
    @property
    def b(self) -> int:
        '''Gets the blue component value of the color.'''
        raise NotImplementedError()
    
    @property
    def a(self) -> int:
        '''Gets the alpha component value of the color.'''
        raise NotImplementedError()
    
    @property
    def is_empty(self) -> bool:
        '''Gets a value indicating whether this :py:class:`groupdocs.watermark.watermarks.Color` structure is uninitialized.'''
        raise NotImplementedError()
    

class Font:
    '''Class representing a font.'''
    
    @overload
    def __init__(self, font_family_name : str, size : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Font` class with a specified font family name and a size.
        
        :param font_family_name: The font family name.
        :param size: The size of the new font.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, font_family_name : str, size : float, style : groupdocs.watermark.watermarks.FontStyle) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Font` class with a specified font family name, a size and a style.
        
        :param font_family_name: The font family name.
        :param size: The size of the new font.
        :param style: The style of the new font.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, font_family_name : str, folder_path : str, size : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Font` class with a specified custom font family name, folder path with a font and a size.
        
        :param font_family_name: The font family name.
        :param folder_path: Folder path which contains TrueType font files
        :param size: The size of the new font.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, font_family_name : str, folder_path : str, size : float, style : groupdocs.watermark.watermarks.FontStyle) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Font` class with a specified custom font family name, folder path with a font and a size.
        
        :param font_family_name: The font family name.
        :param folder_path: Folder path which contains TrueType font files
        :param size: The size of the new font.'''
        raise NotImplementedError()
    
    @property
    def family_name(self) -> str:
        '''Gets the family name of this :py:class:`groupdocs.watermark.watermarks.Font`.'''
        raise NotImplementedError()
    
    @property
    def folder_path(self) -> str:
        '''Represents the folder that contains TrueType font files.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> float:
        '''Gets the size of this :py:class:`groupdocs.watermark.watermarks.Font`.'''
        raise NotImplementedError()
    
    @property
    def style(self) -> groupdocs.watermark.watermarks.FontStyle:
        '''Gets the style information for this :py:class:`groupdocs.watermark.watermarks.Font`.'''
        raise NotImplementedError()
    
    @property
    def bold(self) -> bool:
        '''Gets a value indicating whether the font is bold.'''
        raise NotImplementedError()
    
    @property
    def italic(self) -> bool:
        '''Gets a value indicating whether the font is italic.'''
        raise NotImplementedError()
    
    @property
    def strikeout(self) -> bool:
        '''Gets a value indicating whether the font specifies a horizontal line through the font.'''
        raise NotImplementedError()
    
    @property
    def underline(self) -> bool:
        '''Gets a value indicating whether the font is underlined.'''
        raise NotImplementedError()
    

class ImageWatermark(groupdocs.watermark.Watermark):
    '''Represents an image watermark.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.ImageWatermark` class with a specified file path.
        
        :param file_path: The path to the image that will be used as watermark.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, stream : io._IOBase) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.ImageWatermark` class with a specified stream.
        
        :param stream: The stream containing the image that will be used as watermark.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Sets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def vertical_alignment(self) -> groupdocs.watermark.common.VerticalAlignment:
        '''Gets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @vertical_alignment.setter
    def vertical_alignment(self, value : groupdocs.watermark.common.VerticalAlignment) -> None:
        '''Sets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def horizontal_alignment(self) -> groupdocs.watermark.common.HorizontalAlignment:
        '''Gets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value : groupdocs.watermark.common.HorizontalAlignment) -> None:
        '''Sets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def is_background(self) -> bool:
        '''Gets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @is_background.setter
    def is_background(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @property
    def margins(self) -> groupdocs.watermark.watermarks.Margins:
        '''Gets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @margins.setter
    def margins(self, value : groupdocs.watermark.watermarks.Margins) -> None:
        '''Sets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def pages_setup(self) -> groupdocs.watermark.watermarks.PagesSetup:
        '''Gets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @pages_setup.setter
    def pages_setup(self, value : groupdocs.watermark.watermarks.PagesSetup) -> None:
        '''Sets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def scale_factor(self) -> float:
        '''Gets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @scale_factor.setter
    def scale_factor(self, value : float) -> None:
        '''Sets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @property
    def sizing_type(self) -> groupdocs.watermark.watermarks.SizingType:
        '''Gets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @sizing_type.setter
    def sizing_type(self, value : groupdocs.watermark.watermarks.SizingType) -> None:
        '''Sets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @property
    def consider_parent_margins(self) -> bool:
        '''Gets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @consider_parent_margins.setter
    def consider_parent_margins(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @property
    def save_result_in_metadata(self) -> bool:
        '''Gets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @save_result_in_metadata.setter
    def save_result_in_metadata(self, value : bool) -> None:
        '''Sets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @property
    def tile_options(self) -> groupdocs.watermark.watermarks.TileOptions:
        '''Get options to define repeated watermark'''
        raise NotImplementedError()
    
    @tile_options.setter
    def tile_options(self, value : groupdocs.watermark.watermarks.TileOptions) -> None:
        '''Get or sets options to define repeated watermark'''
        raise NotImplementedError()
    

class Margins:
    '''Represents margin settings for each edge of an object.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Margins` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, margin_type : groupdocs.watermark.watermarks.MarginType, left : float, right : float, top : float, bottom : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Margins` class with the specified type, location and size.
        
        :param margin_type: The margin type. Specifies how margin values should be interpreted.
        :param left: The left margin value.
        :param right: The right margin value.
        :param top: The top margin value.
        :param bottom: The bottom margin value.'''
        raise NotImplementedError()
    
    @property
    def margin_type(self) -> groupdocs.watermark.watermarks.MarginType:
        '''Gets margin type. Setting a new value to this property
        automatically returns all margins to their default values (zero).'''
        raise NotImplementedError()
    
    @margin_type.setter
    def margin_type(self, value : groupdocs.watermark.watermarks.MarginType) -> None:
        '''Sets margin type. Setting a new value to this property
        automatically returns all margins to their default values (zero).'''
        raise NotImplementedError()
    
    @property
    def left(self) -> float:
        '''Gets the left margin.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : float) -> None:
        '''Sets the left margin.'''
        raise NotImplementedError()
    
    @property
    def right(self) -> float:
        '''Gets the right margin.'''
        raise NotImplementedError()
    
    @right.setter
    def right(self, value : float) -> None:
        '''Sets the right margin.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> float:
        '''Gets the top margin.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : float) -> None:
        '''Sets the top margin.'''
        raise NotImplementedError()
    
    @property
    def bottom(self) -> float:
        '''Gets the bottom margin.'''
        raise NotImplementedError()
    
    @bottom.setter
    def bottom(self, value : float) -> None:
        '''Sets the bottom margin.'''
        raise NotImplementedError()
    

class MeasureValue:
    '''Represents a measurement value with a specific type and numerical value.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def measure_type(self) -> groupdocs.watermark.watermarks.TileMeasureType:
        '''Gets the type of measurement.'''
        raise NotImplementedError()
    
    @measure_type.setter
    def measure_type(self, value : groupdocs.watermark.watermarks.TileMeasureType) -> None:
        '''Sets the type of measurement.'''
        raise NotImplementedError()
    
    @property
    def value(self) -> float:
        '''Gets the numerical value of the measurement.
        Value must be greater than 0.'''
        raise NotImplementedError()
    
    @value.setter
    def value(self, value : float) -> None:
        '''Sets the numerical value of the measurement.
        Value must be greater than 0.'''
        raise NotImplementedError()
    

class PagesSetup:
    '''Represents the setup for pages.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.PagesSetup` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, all_pages : bool, first_page : bool, last_page : bool, odd_pages : bool, even_pages : bool, pages : System.Collections.Generic.List`1[[System.Int32]], page_number : System.Nullable`1[[System.Int32]]) -> None:
        raise NotImplementedError()
    
    @property
    def all_pages(self) -> bool:
        '''Gets a value indicating whether to include all pages.'''
        raise NotImplementedError()
    
    @all_pages.setter
    def all_pages(self, value : bool) -> None:
        '''Sets a value indicating whether to include all pages.'''
        raise NotImplementedError()
    
    @property
    def first_page(self) -> bool:
        '''Gets a value indicating whether to include the first page.'''
        raise NotImplementedError()
    
    @first_page.setter
    def first_page(self, value : bool) -> None:
        '''Sets a value indicating whether to include the first page.'''
        raise NotImplementedError()
    
    @property
    def last_page(self) -> bool:
        '''Gets a value indicating whether to include the last page.'''
        raise NotImplementedError()
    
    @last_page.setter
    def last_page(self, value : bool) -> None:
        '''Sets a value indicating whether to include the last page.'''
        raise NotImplementedError()
    
    @property
    def odd_pages(self) -> bool:
        '''Gets a value indicating whether to include odd pages.'''
        raise NotImplementedError()
    
    @odd_pages.setter
    def odd_pages(self, value : bool) -> None:
        '''Sets a value indicating whether to include odd pages.'''
        raise NotImplementedError()
    
    @property
    def even_pages(self) -> bool:
        '''Gets a value indicating whether to include even pages.'''
        raise NotImplementedError()
    
    @even_pages.setter
    def even_pages(self, value : bool) -> None:
        '''Sets a value indicating whether to include even pages.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers to include.'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers to include.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page number when considering only specified pages.'''
        raise NotImplementedError()
    
    @page_number.setter
    def page_number(self, value : System.Nullable`1[[System.Int32]]) -> None:
        '''Sets the page number when considering only specified pages.'''
        raise NotImplementedError()
    
    @property
    def specified(self) -> bool:
        '''Gets a value indicating whether any specific pages are specified.'''
        raise NotImplementedError()
    

class TextWatermark(groupdocs.watermark.Watermark):
    '''Represents a text watermark.'''
    
    def __init__(self, text : str, font : groupdocs.watermark.watermarks.Font) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.TextWatermark` class with a specified text and a font.
        
        :param text: The text to be used as watermark.
        :param font: The font of the text.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Sets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def vertical_alignment(self) -> groupdocs.watermark.common.VerticalAlignment:
        '''Gets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @vertical_alignment.setter
    def vertical_alignment(self, value : groupdocs.watermark.common.VerticalAlignment) -> None:
        '''Sets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def horizontal_alignment(self) -> groupdocs.watermark.common.HorizontalAlignment:
        '''Gets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value : groupdocs.watermark.common.HorizontalAlignment) -> None:
        '''Sets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def is_background(self) -> bool:
        '''Gets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @is_background.setter
    def is_background(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @property
    def margins(self) -> groupdocs.watermark.watermarks.Margins:
        '''Gets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @margins.setter
    def margins(self, value : groupdocs.watermark.watermarks.Margins) -> None:
        '''Sets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def pages_setup(self) -> groupdocs.watermark.watermarks.PagesSetup:
        '''Gets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @pages_setup.setter
    def pages_setup(self, value : groupdocs.watermark.watermarks.PagesSetup) -> None:
        '''Sets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def scale_factor(self) -> float:
        '''Gets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @scale_factor.setter
    def scale_factor(self, value : float) -> None:
        '''Sets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @property
    def sizing_type(self) -> groupdocs.watermark.watermarks.SizingType:
        '''Gets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @sizing_type.setter
    def sizing_type(self, value : groupdocs.watermark.watermarks.SizingType) -> None:
        '''Sets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @property
    def consider_parent_margins(self) -> bool:
        '''Gets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @consider_parent_margins.setter
    def consider_parent_margins(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @property
    def save_result_in_metadata(self) -> bool:
        '''Gets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @save_result_in_metadata.setter
    def save_result_in_metadata(self, value : bool) -> None:
        '''Sets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @property
    def tile_options(self) -> groupdocs.watermark.watermarks.TileOptions:
        '''Get options to define repeated watermark'''
        raise NotImplementedError()
    
    @tile_options.setter
    def tile_options(self, value : groupdocs.watermark.watermarks.TileOptions) -> None:
        '''Get or sets options to define repeated watermark'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text to be used as watermark.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text to be used as watermark.'''
        raise NotImplementedError()
    
    @property
    def font(self) -> groupdocs.watermark.watermarks.Font:
        '''Gets the font of the text.'''
        raise NotImplementedError()
    
    @font.setter
    def font(self, value : groupdocs.watermark.watermarks.Font) -> None:
        '''Sets the font of the text.'''
        raise NotImplementedError()
    
    @property
    def foreground_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the foreground color of the text.'''
        raise NotImplementedError()
    
    @foreground_color.setter
    def foreground_color(self, value : groupdocs.watermark.watermarks.Color) -> None:
        '''Sets the foreground color of the text.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the background color of the text.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : groupdocs.watermark.watermarks.Color) -> None:
        '''Sets the background color of the text.'''
        raise NotImplementedError()
    
    @property
    def text_alignment(self) -> groupdocs.watermark.watermarks.TextAlignment:
        '''Gets the watermark text alignment.'''
        raise NotImplementedError()
    
    @text_alignment.setter
    def text_alignment(self, value : groupdocs.watermark.watermarks.TextAlignment) -> None:
        '''Sets the watermark text alignment.'''
        raise NotImplementedError()
    
    @property
    def padding(self) -> groupdocs.watermark.watermarks.Thickness:
        '''Gets the padding settings of this :py:class:`groupdocs.watermark.watermarks.TextWatermark`.
        This property is applicable only to image files.'''
        raise NotImplementedError()
    
    @padding.setter
    def padding(self, value : groupdocs.watermark.watermarks.Thickness) -> None:
        '''Sets the padding settings of this :py:class:`groupdocs.watermark.watermarks.TextWatermark`.
        This property is applicable only to image files.'''
        raise NotImplementedError()
    

class Thickness:
    '''Describes the thickness of a frame around a rectangle.'''
    
    @overload
    def __init__(self, left : float, right : float, top : float, bottom : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Thickness` class
        that has specific lengths applied to each side of the rectangle.
        
        :param left: The thickness for the left side of the rectangle.
        :param right: The thickness for the right side of the rectangle.
        :param top: The thickness for the top side of the rectangle.
        :param bottom: The thickness for the bottom side of the rectangle.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, uniform_length : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.watermarks.Thickness` class
        that has the specified uniform length on each side.
        
        :param uniform_length: The uniform length applied to all four sides of the bounding rectangle.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> float:
        '''Gets the width of the left side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : float) -> None:
        '''Sets the width of the left side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> float:
        '''Gets the width of the top side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : float) -> None:
        '''Sets the width of the top side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @property
    def right(self) -> float:
        '''Gets the width of the right side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @right.setter
    def right(self, value : float) -> None:
        '''Sets the width of the right side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @property
    def bottom(self) -> float:
        '''Gets the width of the bottom side of the bounding rectangle.'''
        raise NotImplementedError()
    
    @bottom.setter
    def bottom(self, value : float) -> None:
        '''Sets the width of the bottom side of the bounding rectangle.'''
        raise NotImplementedError()
    

class TileOptions:
    '''Represents options for configuring watermarks in tile mode.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def tile_type(self) -> groupdocs.watermark.watermarks.TileType:
        '''Gets the type of tile alignment for watermarks.'''
        raise NotImplementedError()
    
    @tile_type.setter
    def tile_type(self, value : groupdocs.watermark.watermarks.TileType) -> None:
        '''Sets the type of tile alignment for watermarks.'''
        raise NotImplementedError()
    
    @property
    def line_spacing(self) -> groupdocs.watermark.watermarks.MeasureValue:
        '''Gets the spacing between lines for watermarks in tile mode.'''
        raise NotImplementedError()
    
    @line_spacing.setter
    def line_spacing(self, value : groupdocs.watermark.watermarks.MeasureValue) -> None:
        '''Sets the spacing between lines for watermarks in tile mode.'''
        raise NotImplementedError()
    
    @property
    def watermark_spacing(self) -> groupdocs.watermark.watermarks.MeasureValue:
        '''Gets the spacing between serials for watermarks in tile mode.'''
        raise NotImplementedError()
    
    @watermark_spacing.setter
    def watermark_spacing(self, value : groupdocs.watermark.watermarks.MeasureValue) -> None:
        '''Sets the spacing between serials for watermarks in tile mode.'''
        raise NotImplementedError()
    
    @property
    def rotate_around_origin(self) -> bool:
        '''Gets a value indicating whether the repeated watermarks should be rotated around the center of the document.'''
        raise NotImplementedError()
    
    @rotate_around_origin.setter
    def rotate_around_origin(self, value : bool) -> None:
        '''Sets a value indicating whether the repeated watermarks should be rotated around the center of the document.'''
        raise NotImplementedError()
    

class FontStyle:
    '''Represents a font style.'''
    
    REGULAR : FontStyle
    '''Normal text.'''
    BOLD : FontStyle
    '''Bold text.'''
    ITALIC : FontStyle
    '''Italic text.'''
    UNDERLINE : FontStyle
    '''Underlined text.'''
    STRIKEOUT : FontStyle
    '''Text with a line through the middle.'''

class MarginType:
    '''Specifies how margin values should be interpreted.'''
    
    ABSOLUTE : MarginType
    '''Margin value measured in content units.'''
    RELATIVE_TO_PARENT_DIMENSIONS : MarginType
    '''Margin value should be interpreted as a portion of appropriate parent dimension.'''
    RELATIVE_TO_PARENT_MIN_DIMENSION : MarginType
    '''Margin value should be interpreted as a portion of parent minimum dimension.'''

class SizingType:
    '''Specifies how watermark size should be calculated.'''
    
    AUTO : SizingType
    '''Watermark should be sized automatically according to its content.'''
    ABSOLUTE : SizingType
    '''Watermark should be sized to an exact :py:attr:`groupdocs.watermark.Watermark.width` and :py:attr:`groupdocs.watermark.Watermark.height`'''
    SCALE_TO_PARENT_DIMENSIONS : SizingType
    '''Watermark should be scaled relative to parent dimensions using
    specified :py:attr:`groupdocs.watermark.Watermark.scale_factor`.'''
    SCALE_TO_PARENT_AREA : SizingType
    '''Watermark should be scaled relative to parent area using specified :py:attr:`groupdocs.watermark.Watermark.scale_factor`'''

class TextAlignment:
    '''Enumeration of possible text alignment values.'''
    
    LEFT : TextAlignment
    '''Align to left.'''
    CENTER : TextAlignment
    '''Center alignment.'''
    RIGHT : TextAlignment
    '''Align to right.'''
    JUSTIFY : TextAlignment
    '''Justify alignment. Text will be aligned on both left and right margins.'''

class TileMeasureType:
    '''Represents measure types'''
    
    PIXEL : TileMeasureType
    '''Specifies that the unit of measurement is pixel.'''
    PERCENT : TileMeasureType
    '''Specifies that the unit of measurement is percent.'''
    POINTS : TileMeasureType
    '''Specifies that the unit of measurement is point.'''

class TileType:
    '''Enumeration representing different visual templates for arranging watermark tiles.'''
    
    STRAIGHT : TileType
    '''Represents straight tile alignment.'''
    OFFSET : TileType
    '''Represents offset tile alignment.'''
    ONE_THIRD_OFFSET : TileType
    '''Represents 1/3 offset tile alignment.'''
    BASKET_WEAVE : TileType
    '''Represents basket weave tile pattern'''

