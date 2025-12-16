from dataclasses import dataclass, fields, MISSING
from enum import Enum
from typing import List, Optional, get_origin, get_args, Any
from pathlib import Path
from configobj import ConfigObj
from ._internal import _zelesis_utils
from ._internal._windows_utils import _ensure_admin

class CaptureMethod(Enum):
    WINRT = "winrt"
    DUPLICATION_API = "duplication_api"
    GDI = "gdi"

class Backend(Enum):
    TRT = "TRT"
    DML = "DML"

class InputMethod(Enum):
    WIN32 = "WIN32"
    GHUB = "GHUB"
    ARDUINO = "ARDUINO"
    KMBOX_B = "KMBOX_B"

@dataclass
class ConfigModel:
    # Capture
    capture_method: CaptureMethod
    detection_resolution: int
    normal_fov_circle_size: int
    ads_fov_circle_size: int
    use_seperate_ads_fov: bool
    capture_fps: int
    capture_use_cuda: bool
    monitor_idx: int
    circle_mask: bool
    custom_detection_area: str
    show_custom_area: bool
    custom_area_extra_width: int
    export_masks: bool

    # Target
    disable_headshot: bool
    body_y_offset: float
    head_y_offset: float
    ignore_third_person: bool
    shooting_range_targets: bool
    auto_aim: bool

    # Mouse
    aimbot_enabled: bool
    dpi: int
    sensitivity: float
    sensitivity_x: float
    sensitivity_y: float
    fovX: int
    fovY: int
    zoomFovX: int
    zoomFovY: int
    mouseSpeedRandomness: float
    mouse_speed_profile: int
    predictionInterval: float
    prediction_futurePositions: int
    draw_futurePositions: bool
    easynorecoil: bool
    easynorecoil_always_active: bool
    easynorecoilstrength: float
    input_method: InputMethod

    # Auto Pause
    auto_pause_enabled: bool
    auto_pause_sensitivity: bool

    # Arduino
    arduino_baudrate: int
    
    # Kmbox_B
    kmbox_baudrate: int

    # Mouse shooting
    auto_shoot: bool
    spam_click: bool
    spam_cps: int
    bScope_multiplier_x: float
    bScope_multiplier_y: float
    trigger_delay_ms: int

    # AI
    backend: Backend
    dml_device_id: int
    ai_model: str
    confidence_threshold: float
    nms_threshold: float
    max_detections: int
    postprocess: str
    export_enable_fp8: bool
    export_enable_fp16: bool

    # CUDA
    use_cuda_graph: bool
    use_pinned_memory: bool

    # Buttons
    button_targeting: List[str]
    button_shoot: str
    button_zoom: str
    button_exit: List[str]
    button_pause: str
    button_reload_config: str
    button_open_overlay: str
    enable_arrows_settings: bool

    # Overlay
    ui_color_hue: int
    ui_color_saturation: int
    ui_color_brightness: int
    show_boxes: bool
    show_tracer_lines: bool
    show_detection_window: bool
    show_fps: bool
    fps_top_left: bool
    line_thickness: int
    zelesis_stays_on_top: bool
    box_style: int

    # Target Highlighting
    show_target_highlight: bool
    target_color_r: int
    target_color_g: int
    target_color_b: int

    # Crosshair System
    show_crosshair: bool
    crosshair_color_r: int
    crosshair_color_g: int
    crosshair_color_b: int
    crosshair_length: int
    crosshair_thickness: int
    crosshair_spacing: int

    # Overlay Opacity
    overlay_opacity: int

    # Visual Overlay Colors (RGB)
    box_color_r: int
    box_color_g: int
    box_color_b: int
    tracer_color_r: int
    tracer_color_g: int
    tracer_color_b: int
    detection_window_color_r: int
    detection_window_color_g: int
    detection_window_color_b: int

    # Custom Classes
    class_player: int
    class_bot: int
    class_weapon: int
    class_outline: int
    class_dead_body: int
    class_hideout_target_human: int
    class_hideout_target_balls: int
    class_head: int
    class_smoke: int
    class_fire: int
    class_third_person: int

    # PID Control
    use_pid: bool
    proportional: float
    integral: float
    derivative: float

    # Advanced Mode
    advanced_mode: bool

    # UI Mode
    use_unified_interface: bool

    # Visual Overlay State Persistence
    previous_show_boxes: bool
    previous_show_tracers: bool
    previous_show_detection_window: bool
    previous_show_fps: bool
    previous_show_crosshair: bool

    # Optional fields (must come after all required fields)
    # Arduino (optional fields)
    arduino_port: Optional[str] = None
    arduino_16_bit_mouse: bool = False
    arduino_enable_keys: bool = False
    virtual_hostshield: bool = False
    
    # Kmbox_B (optional fields)
    kmbox_port: Optional[str] = None

    # Presets (optional fields)
    preset_hotkeys: List[Optional[str]] = None
    preset_names: List[Optional[str]] = None


def create_config_from_default_config_file() -> ConfigModel:
    """
    Create a config class object from the default config file
    """
    config_path = Path(_zelesis_utils._find_zelesis_installation()) / "config.ini"
    cfg = ConfigObj(str(config_path), list_values=False)
    return _load_dataclass_from_config(ConfigModel, cfg)


def create_config_from_preset(preset_name: str) -> ConfigModel:
    """
    Create a config class object from a preset file
    
    :param preset_name: Description
    :type preset_name: str
    :return: Description
    :rtype: ConfigModel
    """
    # find file
    config_path = Path(_zelesis_utils._find_zelesis_installation()) / "presets" / (preset_name + ".ini")
    cfg = ConfigObj(str(config_path), list_values=False)
    
    return _load_dataclass_from_config(ConfigModel, cfg)

def _convert_value(value: str, target_type: type) -> Any:
    """
    Convert INI strings to actual Python values based on type annotation.
    """

    # Optional[T] -> treat None or empty string
    origin = get_origin(target_type)
    if origin is Optional:
        inner_type = get_args(target_type)[0]
        if value in ("", "none", "null", None):
            return None
        return _convert_value(value, inner_type)

    # List[T]
    if origin is list:
        inner_type = get_args(target_type)[0]
        return [_convert_value(x.strip(), inner_type) for x in value.split(",")]

    # bool
    if target_type is bool:
        return value.lower() == "true"

    # int
    if target_type is int:
        return int(value)

    # float
    if target_type is float:
        return float(value)

    # String
    if target_type is str:
        return value

    # Enum
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        return target_type(value.lower() if value.lower() in target_type._value2member_map_ else value)

    # fallback
    return value

def _load_dataclass_from_config(cls: type[ConfigModel], config_dict: dict) -> ConfigModel:
    kwargs = {}

    for f in fields(cls):
        name = f.name

        if name not in config_dict:
            # Missing field -> use default if exists
            if f.default is not MISSING:
                kwargs[name] = f.default
                continue
            elif f.default_factory is not MISSING:
                kwargs[name] = f.default_factory()
                continue
            else:
                raise KeyError(f"Missing config value: {name}")

        raw_value = config_dict[name]
        kwargs[name] = _convert_value(raw_value, f.type)

    return cls(**kwargs)

def write_config_to_default_file(config: ConfigModel) -> None:
    """
    Write a ConfigModel object to the default configuration file in the base zelesis neo directory.
    
    Requires admin privileges to write to the Zelesis installation directory.
    
    :param config: The ConfigModel instance to write
    :type config: ConfigModel
    """
    # Ensure admin privileges
    _ensure_admin()
    
    config_path = Path(_zelesis_utils._find_zelesis_installation()) / "config.ini"

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Config file not found at: {config_path}"
        )
    
    # Convert ConfigModel to dictionary
    config_dict = _convert_config_to_dict(config)
    
    # Create ConfigObj and write to file
    cfg = ConfigObj()
    cfg.update(config_dict)
    cfg.filename = str(config_path)
    cfg.write()

def write_config_to_preset(config: ConfigModel, preset_name: str) -> None:
    """
    Write a ConfigModel object to a preset file.
    
    Requires admin privileges to write to the Zelesis installation directory.
    
    :param config: The ConfigModel instance to write
    :type config: ConfigModel
    :param preset_name: Name of the preset (without .ini extension)
    :type preset_name: str
    """
    # Ensure admin privileges
    _ensure_admin()
    
    # Find the presets directory
    presets_dir = Path(_zelesis_utils._find_zelesis_installation()) / "presets"
    config_path = presets_dir / (preset_name + ".ini")
    
    if not presets_dir.is_dir():
        raise FileNotFoundError(
            f"Presets directory not found at: {presets_dir}"
        )
    
    # Convert ConfigModel to dictionary
    config_dict = _convert_config_to_dict(config)
    
    # Create ConfigObj and write to file
    cfg = ConfigObj()
    cfg.update(config_dict)
    cfg.filename = str(config_path)
    cfg.write()


def _convert_config_to_dict(config: ConfigModel) -> dict:
    """
    Convert a ConfigModel instance to a dictionary suitable for ConfigObj.
    
    :param config: The ConfigModel instance
    :type config: ConfigModel
    :return: Dictionary representation of the config
    :rtype: dict
    """
    config_dict = {}
    model_fields = fields(ConfigModel)
    
    for field in model_fields:
        value = getattr(config, field.name)
        
        # Convert enum to its string value
        if isinstance(value, Enum):
            config_dict[field.name] = value.value
        # Convert list to comma-separated string
        elif isinstance(value, list):
            config_dict[field.name] = ", ".join(str(item) for item in value)
        # Convert None to empty string for optional fields
        elif value is None:
            config_dict[field.name] = ""
        # Convert bool to lowercase string
        elif isinstance(value, bool):
            config_dict[field.name] = "true" if value else "false"
        # Convert everything else to string
        else:
            config_dict[field.name] = str(value)
    
    return config_dict