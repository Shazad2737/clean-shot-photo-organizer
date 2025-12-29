# ========== GUI Module ==========
"""
GUI modules for the CLEAN SHOT Photo Organizer application.

This package provides:
- theme: Unified theming system with dark/light modes and animated widgets
- components: Reusable UI components (settings, progress, results)
- icons: SVG icon system with IconManager
"""

# Theme system
from gui.theme import (
    # Theme definitions
    DARK_THEME,
    LIGHT_THEME,
    ThemeManager,
    get_theme,
    get_theme_css,
    get_gradients,
    
    # Animated widgets
    AnimatedButton,
    GlowCard,
    FadeLabel,
    PulseWidget,
    
    # Helper functions
    apply_modern_card_style,
    create_threshold_button,
    create_gradient_label,
    create_status_badge,
)

# Components
from gui.components import (
    SettingsWidget,
    ProgressWidget,
    ResultsWidget,
    StatCard,
    ActionButton,
)

# Icons
from gui.icons import (
    IconManager,
    get_icon,
    get_pixmap,
    ICONS,
)

# Modern UI
from gui.modern_main_window import (
    ModernMainWindow,
    Sidebar,
    DropZone,
    PhotoPreviewGrid,
    StatsPanel,
    DashboardPage,
    SettingsPage,
    FaceSearchPage,
)

__all__ = [
    # Theme
    'DARK_THEME',
    'LIGHT_THEME', 
    'ThemeManager',
    'get_theme',
    'get_theme_css',
    'get_gradients',
    
    # Animated Widgets
    'AnimatedButton',
    'GlowCard',
    'FadeLabel',
    'PulseWidget',
    
    # Helper Functions
    'apply_modern_card_style',
    'create_threshold_button',
    'create_gradient_label',
    'create_status_badge',
    
    # Components
    'SettingsWidget',
    'ProgressWidget',
    'ResultsWidget',
    'StatCard',
    'ActionButton',
    
    # Icons
    'IconManager',
    'get_icon',
    'get_pixmap',
    'ICONS',
    
    # Modern UI
    'ModernMainWindow',
    'Sidebar',
    'DropZone',
    'PhotoPreviewGrid',
    'StatsPanel',
    'DashboardPage',
    'SettingsPage',
    'FaceSearchPage',
]
