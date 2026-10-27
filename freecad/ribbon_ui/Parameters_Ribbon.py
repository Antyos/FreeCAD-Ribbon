# *************************************************************************
# *                                                                       *
# * Copyright (c) 2019-2024 Hakan Seven, Geolta, Paul Ebbers              *
# *                                                                       *
# * This program is free software; you can redistribute it and/or modify  *
# * it under the terms of the GNU Lesser General Public License (LGPL)    *
# * as published by the Free Software Foundation; either version 3 of     *
# * the License, or (at your option) any later version.                   *
# * for detail see the LICENCE text file.                                 *
# *                                                                       *
# * This program is distributed in the hope that it will be useful,       *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# * GNU Library General Public License for more details.                  *
# *                                                                       *
# * You should have received a copy of the GNU Library General Public     *
# * License along with this program; if not, write to the Free Software   *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# * USA                                                                   *
# *                                                                       *
# *************************************************************************

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Self, Type, TypeVar, overload

from PySide.QtGui import QColor

import FreeCAD as App

# Set the AdvancesSizeSettingsReset version number
AdvancedSizeReset = "1.0"
T = TypeVar("T")
ValueType = TypeVar("ValueType", str, int, float, bool, Path)


class Setting(Generic[ValueType]):
    def __init__(
        self,
        default: ValueType,
        getter: Callable[[str, ValueType], ValueType],
        setter: Callable[[str, ValueType], None],
        name: str | None = None,
    ):
        self.default = default
        self.getter = getter
        self.setter = setter
        self.name_alias = name

    def __set_name__(self, owner: object, name: str):
        if self.name_alias is not None:
            self.name = self.name_alias
        else:
            self.name = name

    @overload
    def __get__(self, instance: None, owner: None) -> Self: ...

    @overload
    def __get__(self, instance: T, owner: Type[T]) -> ValueType: ...

    def __get__(self, instance: T | None, owner: Type[T] | None = None) -> ValueType | Self:
        if instance is None:
            return self
        return self.getter(self.name, self.default)

    def __set__(self, instance, value: ValueType):
        self.setter(self.name, value)
        App.saveParameter()


class StringSetting(Setting[str]):
    def __init__(self, default: str, name: str | None = None):
        super().__init__(default, getter=self._get, setter=preferences.SetString, name=name)

    @staticmethod
    def _get(name: str, default: str) -> str:
        value = preferences.GetString(name, default)
        return "" if value.lower() == "none" else value


class IntSetting(Setting[int]):
    def __init__(self, default: int, name: str | None = None):
        super().__init__(default, getter=preferences.GetInt, setter=preferences.SetInt, name=name)


class FloatSetting(Setting[float]):
    def __init__(self, default: float, name: str | None = None):
        super().__init__(
            default, getter=preferences.GetFloat, setter=preferences.SetFloat, name=name
        )


class BoolSetting(Setting[bool]):
    def __init__(self, default: bool, name: str | None = None):
        super().__init__(default, getter=preferences.GetBool, setter=preferences.SetBool, name=name)


class PathSetting(Setting[Path]):
    def __init__(self, default: Path | str, name: str | None = None):
        super().__init__(
            Path(default),
            getter=self._getter,
            setter=lambda name, value: preferences.SetString(name, str(value)),
            name=name,
        )

    def _getter(self, name, default: Path) -> Path:
        value = preferences.GetString(name, str(default))
        return Path(value)


@dataclass
class SettingsDC: ...


preferences = App.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeCAD-Ribbon")

resources_dir = Path(__file__).parent / "resources"

STYLESHEET_LOCATION = resources_dir / "stylesheets"


class Settings:
    # region -- Functions to read the settings from the FreeCAD Parameters
    # and make sure that a None type result is ""
    def GetStringSetting(settingName) -> str:
        result = preferences.GetString(settingName)

        if result.lower() == "none":
            result = ""
        return result

    def GetIntSetting(settingName) -> int:
        result = preferences.GetInt(settingName)
        if result == "":
            result = None
        return result

    def GetFloatSetting(settingName) -> float:
        result = preferences.GetFloat(settingName)
        if result == "":
            result = None
        return result

    def GetBoolSetting(settingName) -> bool:
        result = None
        settings = preferences.GetContents()
        exists = False
        if settings is not None:
            for setting in settings:
                if setting[0] == "Boolean" and setting[1] == settingName:
                    exists = True
                    break
            if exists is True:
                result = preferences.GetBool(settingName)
        return result

    def GetColorSetting(self, settingName: str) -> object:
        # Create a tuple from the int value of the color
        result = QColor.fromRgba(preferences.GetUnsigned(settingName)).toTuple()

        # correct the order of the tuple and divide them by 255
        result = (result[3] / 255, result[0] / 255, result[1] / 255, result[2] / 255)

        return tuple(result)

    # endregion

    # region - Functions to write settings to the FreeCAD Parameters
    #
    #
    @staticmethod
    def SetStringSetting(settingName, value: str):
        if value.lower() == "none":
            value = ""
        if value == "":
            for setting in _Parameters.__class__.__dict__.values():
                if (
                    isinstance(setting, (StringSetting, PathSetting))
                    and setting.name == settingName
                ):
                    value = str(setting.default)
                    break
        preferences.SetString(settingName, value)
        App.saveParameter()
        return

    @staticmethod
    def SetBoolSetting(settingName, value: bool):
        preferences.SetBool(settingName, value)
        App.saveParameter()
        return

    @staticmethod
    def SetIntSetting(settingName, value: int):
        preferences.SetInt(settingName, value)
        App.saveParameter()
        return

    @staticmethod
    def SetFloatSetting(settingName, value: float):
        preferences.SetFloat(settingName, value)
        App.saveParameter()
        return

    # endregion


class _Parameters:
    FreeCAD_Version = {
        "mainVersion": 1,
        "subVersion": 1,
        "patchVersion": 0,
        "gitVersion": 14555,
    }

    ICON_LOCATION = Path(__file__).parent / "resources" / "icons"
    STYLESHEET_LOCATION = Path(__file__).parent / "resources" / "stylesheets"
    UI_LOCATION = Path(__file__).parent / "resources" / "ui"
    AppDir = Path(App.getUserAppDataDir().split("FreeCAD")[0]) / "FreeCAD"
    OldModDir = AppDir / "Mod"
    CurrentModDir = Path(App.getUserAppDataDir()) / "Mod"

    DOCKED_DIALOGS = BoolSetting(False, "Docked_Dialogs")
    CONFIG_DIR = PathSetting(Path(App.getUserAppDataDir()) / "RibbonUI_Data", "ConfigDir")
    IMPORT_LOCATION = PathSetting(Path(App.getUserAppDataDir()) / "RibbonUI_Data", "ImportLocation")
    EXPORT_LOCATION = PathSetting(Path(App.getUserAppDataDir()) / "RibbonUI_Data", "ExportLocation")
    RIBBON_STRUCTURE_JSON = PathSetting(
        Path(App.getUserAppDataDir()) / "RibbonUI_Data" / "RibbonStructure.json",
        "RibbonStructure",
    )
    DEFAULT_PANEL_POSITION_CUSTOM = StringSetting("Right", "CustomPanelPosition")
    TABBAR_STYLE = IntSetting(0, "TabBar_Style")
    TOOLBAR_POSITION = IntSetting(0, "Toolbar_Position")
    HIDE_TITLEBAR_FC = BoolSetting(True, "Hide_Titlebar_FC")
    LINK_ICON_SIZES = BoolSetting(True, "Link_IconSizes")
    ICON_SIZE_SMALL = IntSetting(24, "IconSize_Small")
    ICON_SIZE_MEDIUM = IntSetting(36, "IconSize_Medium")
    ICON_SIZE_LARGE = IntSetting(72, "IconSize_Large")
    APP_ICON_SIZE = IntSetting(40, "ApplicationButtonSize")
    QUICK_ICON_SIZE = IntSetting(24, "QuickAccessButtonSize")
    TABBAR_SIZE = IntSetting(24, "TabBarSize")
    RIGHT_ICON_SIZE = IntSetting(24, "RightToolbarButtonSize")
    ENABLE_BACKUP = BoolSetting(True, "BackupEnabled")
    BACKUP_LOCATION = PathSetting(
        Path(App.getUserAppDataDir()) / "RibbonUI_Data" / "Backups", "BackupFolder"
    )
    TAB_ORDER = StringSetting(
        App.ParamGet("User parameter:BaseApp/Preferences/Workbenches/").GetString("Ordered"),
        "TabOrder",
    )
    AUTOHIDE_RIBBON = BoolSetting(False, "AutoHideRibbon")
    STYLESHEET = PathSetting(STYLESHEET_LOCATION / "default.qss", "Stylesheet")
    SHOW_ICON_TEXT_SMALL = BoolSetting(False, "ShowIconText_Small")
    SHOW_ICON_TEXT_MEDIUM = BoolSetting(False, "ShowIconText_Medium")
    SHOW_ICON_TEXT_LARGE = BoolSetting(True, "ShowIconText_Large")
    MAX_COLUMN_PANELS = IntSetting(0, "MaxColumnsPerPanel")
    WRAPTEXT_MEDIUM = BoolSetting(True, "WrapText_Medium")
    WRAPTEXT_LARGE = BoolSetting(True, "WrapText_Large")
    FONTSIZE_MENUS = IntSetting(11, "FontSize_Menus")
    FONTSIZE_BUTTONS = IntSetting(11, "FontSize_Buttons")
    FONTSIZE_TABS = IntSetting(14, "FontSize_Tabs")
    FONTSIZE_PANELS = IntSetting(11, "FontSize_Panels")
    DEBUG_MODE = BoolSetting(False, "DebugMode")
    SHOW_ON_HOVER = BoolSetting(False, "ShowOnHover")
    TABBAR_SCROLLSPEED = IntSetting(1, "TabBar_Scroll")
    RIBBON_SCROLLSPEED = IntSetting(1, "Ribbon_Scroll")
    TABBAR_CLICKSPEED = IntSetting(1, "TabBar_Click")
    RIBBON_CLICKSPEED = IntSetting(1, "Ribbon_Click")
    SHORTCUT_APPLICATION = StringSetting("Alt+A", "Shortcut_Application")
    PREFERRED_VIEW = IntSetting(2, "Preferred_view")
    USE_TOOLSPANEL = BoolSetting(True, "UseToolsPanel")
    USE_OVERLAY = BoolSetting(True, "UseOverlay")
    OVERLAYSTATE = IntSetting(0, "OverlayState")
    BUTTON_BACKGROUND_ENABLED = BoolSetting(False, "UseButtonBackGround")
    CUSTOM_ICONS_ENABLED = BoolSetting(False, "CustomIcons")
    SCROLL_LEFT_BUTTON_TAB = StringSetting("", "ScrollLeftButton_Tab")
    SCROLL_RIGHT_BUTTON_TAB = StringSetting("", "ScrollRightButton_Tab")
    SCROLL_LEFT_BUTTON_CATEGORY = StringSetting("", "ScrollLeftButton_Category")
    SCROLL_RIGHT_BUTTON_CATEGORY = StringSetting("", "ScrollRightButton_Category")
    OPTION_BUTTON = StringSetting("", "OptionButton")
    PIN_BUTTON_OPEN = StringSetting("", "PinButton_open")
    PIN_BUTTON_CLOSED = StringSetting("", "PinButton_closed")
    CUSTOM_COLORS_ENABLED = BoolSetting(False, "CustomColors")
    BORDER_TRANSPARANT = BoolSetting(True, "BorderTransparant")
    COLOR_BORDERS = StringSetting("", "Color_Borders")
    COLOR_BACKGROUND_HOVER = StringSetting("", "Color_Background_Hover")
    COLOR_APPLICATION_BUTTON_BACKGROUND = StringSetting("", "Color_Background_App")
    COLOR_BACKGROUND_TABS = StringSetting("", "Color_Background_Tabs")
    COLOR_BACKGROUND_TITLEBAR = StringSetting("", "Color_Background_TitleBar")
    COLOR_FONT = StringSetting("", "Color_Font")
    BETA_FUNCTIONS_ENABLED = BoolSetting(True, "BetaFunctions")
    SIZE_FACTOR = FloatSetting(1.3, "SizeFactor")
    PANEL_HEIGHT_OFFSET = IntSetting(24, "PanelHeightOffset")
    RIBBON_HEIGHT_OFFSET = IntSetting(0, "RibbonHeightOffset")
    RIBBON_MINIMUM_HEIGHT = IntSetting(16, "RibbonMinimumHeight")
    BUTTON_SPACING = IntSetting(3, "ButtonSpacing")
    ADVANCED_SIZE_RESET = StringSetting(AdvancedSizeReset, "AdvancedSizeReset")
    STORED_OVERLAY_STATE = StringSetting("", "StoredOverlayState")

    def __init__(self):
        reset_required = self.ADVANCED_SIZE_RESET != AdvancedSizeReset
        if reset_required:
            for name in (
                "SIZE_FACTOR",
                "PANEL_HEIGHT_OFFSET",
                "RIBBON_HEIGHT_OFFSET",
                "RIBBON_MINIMUM_HEIGHT",
                "BUTTON_SPACING",
            ):
                setting = self.__class__.__dict__[name]
                setattr(self, name, setting.default)
            self.ADVANCED_SIZE_RESET = AdvancedSizeReset

        self._validate_settings()

        if not self.CONFIG_DIR.is_file():
            self.CONFIG_DIR = self.__class__.__dict__["CONFIG_DIR"].default
            self.IMPORT_LOCATION = self.__class__.__dict__["IMPORT_LOCATION"].default
            self.EXPORT_LOCATION = self.__class__.__dict__["EXPORT_LOCATION"].default
        if not self.BACKUP_LOCATION.is_file():
            self.BACKUP_LOCATION = self.__class__.__dict__["BACKUP_LOCATION"].default
        if not self.STYLESHEET.is_file():
            self.STYLESHEET = self.__class__.__dict__["STYLESHEET"].default
        self.TAB_ORDER = App.ParamGet("User parameter:BaseApp/Preferences/Workbenches/").GetString(
            "Ordered"
        )
        App.saveParameter()

    def _validate_settings(self):
        for name in (
            "TABBAR_STYLE",
            "TOOLBAR_POSITION",
        ):
            setting = self.__class__.__dict__[name]
            if getattr(self, name) > (2 if name == "TABBAR_STYLE" else 1):
                setattr(self, name, setting.default)

        for name in (
            "ICON_SIZE_SMALL",
            "ICON_SIZE_MEDIUM",
            "ICON_SIZE_LARGE",
            "APP_ICON_SIZE",
            "QUICK_ICON_SIZE",
            "TABBAR_SIZE",
            "RIGHT_ICON_SIZE",
            "TABBAR_SCROLLSPEED",
            "RIBBON_SCROLLSPEED",
            "TABBAR_CLICKSPEED",
            "RIBBON_CLICKSPEED",
            "MAX_COLUMN_PANELS",
            "FONTSIZE_MENUS",
            "FONTSIZE_BUTTONS",
            "FONTSIZE_TABS",
            "FONTSIZE_PANELS",
            "RIBBON_MINIMUM_HEIGHT",
            "SIZE_FACTOR",
        ):
            if getattr(self, name) == 0:
                setattr(self, name, self.__class__.__dict__[name].default)

    def WriteMissingSettings(self):
        for name, setting in self.__class__.__dict__.items():
            if (
                isinstance(setting, Setting)
                and setting.__get__(self, self.__class__) != setting.default
            ):
                setting.__set__(self, setting.default)
        App.saveParameter()


Parameters = _Parameters()
