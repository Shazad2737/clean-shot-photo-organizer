"""
Modern, beautiful styling system for CLEAN SHOT Photo Organizer.
"""

# Beautiful color palette inspired by modern design trends
COLORS = {
    # Primary colors
    'primary': '#667eea',        # Beautiful purple-blue
    'primary_dark': '#5a67d8',   # Darker purple
    'primary_light': '#a8b4f5',  # Light purple
    
    # Secondary colors
    'secondary': '#764ba2',       # Deep purple
    'accent': '#f093fb',         # Pink accent
    'accent_light': '#f5e6ff',   # Light pink
    
    # Status colors
    'success': '#48bb78',        # Modern green
    'success_light': '#c6f6d5',  # Light green
    'warning': '#ed8936',        # Modern orange
    'warning_light': '#fef5e7', # Light orange
    'danger': '#f56565',         # Modern red
    'danger_light': '#fed7d7',   # Light red
    'info': '#4299e1',           # Modern blue
    'info_light': '#bee3f8',    # Light blue
    
    # Neutral colors
    'dark': '#2d3748',          # Dark gray
    'dark_light': '#4a5568',    # Medium dark gray
    'gray': '#718096',          # Medium gray
    'gray_light': '#a0aec0',    # Light gray
    'light': '#f7fafc',         # Very light gray
    'white': '#ffffff',         # Pure white
    
    # Background colors
    'bg_primary': '#ffffff',     # Main background
    'bg_secondary': '#f8fafc',  # Secondary background
    'bg_tertiary': '#edf2f7',   # Tertiary background
    
    # Text colors
    'text_primary': '#2d3748',   # Primary text
    'text_secondary': '#4a5568', # Secondary text
    'text_tertiary': '#718096',  # Tertiary text
    'text_light': '#a0aec0',    # Light text
}

# Beautiful gradient definitions
GRADIENTS = {
    'primary': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)',
    'success': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #48bb78, stop:1 #38a169)',
    'warning': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ed8936, stop:1 #dd6b20)',
    'danger': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f56565, stop:1 #e53e3e)',
    'info': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4299e1, stop:1 #3182ce)',
    'glass': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05))',
}

# Modern button styles with beautiful effects
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background: {GRADIENTS['primary']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
            text-align: center;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a67d8, stop:1 #6b46c1);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4c51bf, stop:1 #553c9a);
            transform: translateY(0px);
        }}
        QPushButton:disabled {{
            background: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background: {GRADIENTS['success']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
            text-align: center;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38a169, stop:1 #2f855a);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f855a, stop:1 #276749);
            transform: translateY(0px);
        }}
        QPushButton:disabled {{
            background: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background: {GRADIENTS['danger']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
            text-align: center;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e53e3e, stop:1 #c53030);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(245, 101, 101, 0.3);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c53030, stop:1 #9c2626);
            transform: translateY(0px);
        }}
        QPushButton:disabled {{
            background: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background: {COLORS['white']};
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            padding: 12px 26px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
            text-align: center;
        }}
        QPushButton:hover {{
            background: {COLORS['primary']};
            color: {COLORS['white']};
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_dark']};
            transform: translateY(0px);
        }}
        QPushButton:disabled {{
            background: {COLORS['white']};
            color: {COLORS['text_tertiary']};
            border-color: {COLORS['gray_light']};
        }}
    """,
    
    'glass': f"""
        QPushButton {{
            background: {GRADIENTS['glass']};
            color: {COLORS['text_primary']};
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 14px;
            min-height: 22px;
            text-align: center;
        }}
        QPushButton:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }}
        QPushButton:pressed {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(0px);
        }}
    """
}

# Beautiful widget styles
WIDGET_STYLES = {
    'main_window': f"""
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 {COLORS['bg_primary']}, 
                stop:1 {COLORS['bg_secondary']});
            color: {COLORS['text_primary']};
        }}
    """,
    
    'group_box': f"""
        QGroupBox {{
            font-weight: 700;
            font-size: 18px;
            color: {COLORS['text_primary']};
            border: 2px solid {COLORS['primary_light']};
            border-radius: 16px;
            margin-top: 15px;
            padding-top: 15px;
            background: {COLORS['white']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 12px 0 12px;
            background: {COLORS['white']};
            color: {COLORS['primary']};
        }}
    """,
    
    'card': f"""
        QFrame {{
            background: {COLORS['white']};
            border: 1px solid {COLORS['gray_light']};
            border-radius: 16px;
            padding: 20px;
        }}
    """,
    
    'glass_card': f"""
        QFrame {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
        }}
    """,
    
    'progress_bar': f"""
        QProgressBar {{
            border: none;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
            background: {COLORS['gray_light']};
            min-height: 24px;
        }}
        QProgressBar::chunk {{
            background: {GRADIENTS['primary']};
            border-radius: 12px;
        }}
    """,
    
    'label_title': f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 24px;
            font-weight: 700;
            margin: 10px 0;
        }}
    """,
    
    'label_subtitle': f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 16px;
            font-weight: 500;
            margin: 5px 0;
        }}
    """,
    
    'label_body': f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 400;
        }}
    """,
    
    'spin_box': f"""
        QSpinBox {{
            border: 2px solid {COLORS['gray_light']};
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: 500;
            background: {COLORS['white']};
            color: {COLORS['text_primary']};
        }}
        QSpinBox:focus {{
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        QSpinBox:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """,
    
    'slider': f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {COLORS['gray_light']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {GRADIENTS['primary']};
            border: none;
            width: 20px;
            height: 20px;
            border-radius: 10px;
            margin: -7px 0;
        }}
        QSlider::handle:horizontal:hover {{
            background: {COLORS['primary_dark']};
            transform: scale(1.1);
        }}
    """,
    
    'check_box': f"""
        QCheckBox {{
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {COLORS['gray_light']};
            border-radius: 6px;
            background: {COLORS['white']};
        }}
        QCheckBox::indicator:checked {{
            background: {GRADIENTS['primary']};
            border-color: {COLORS['primary']};
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """,
    
    'folder_display': f"""
        QLabel {{
            font-size: 16px;
            font-weight: 500;
            padding: 16px;
            background: {COLORS['light']};
            border: 2px dashed {COLORS['primary_light']};
            border-radius: 12px;
            color: {COLORS['text_secondary']};
            min-height: 24px;
        }}
    """,
    
    'folder_display_selected': f"""
        QLabel {{
            font-size: 16px;
            font-weight: 600;
            padding: 16px;
            background: {COLORS['success_light']};
            border: 2px solid {COLORS['success']};
            border-radius: 12px;
            color: {COLORS['success']};
            min-height: 24px;
        }}
    """,
    
    'results_display': f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 14px;
            line-height: 1.6;
            padding: 20px;
            background: {COLORS['white']};
            border-radius: 12px;
            border: 1px solid {COLORS['gray_light']};
        }}
    """
}

# Beautiful application-wide styles
APPLICATION_STYLE = f"""
    QMainWindow {{
        {WIDGET_STYLES['main_window']}
    }}
    
    QWidget {{
        background: transparent;
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    QGroupBox {{
        {WIDGET_STYLES['group_box']}
    }}
    
    QFrame {{
        {WIDGET_STYLES['card']}
    }}
    
    QProgressBar {{
        {WIDGET_STYLES['progress_bar']}
    }}
    
    QSpinBox {{
        {WIDGET_STYLES['spin_box']}
    }}
    
    QSlider {{
        {WIDGET_STYLES['slider']}
    }}
    
    QCheckBox {{
        {WIDGET_STYLES['check_box']}
    }}
    
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    
    QMenuBar {{
        background: {COLORS['white']};
        border-bottom: 1px solid {COLORS['gray_light']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: 8px 16px;
        border-radius: 6px;
        color: {COLORS['text_primary']};
    }}
    
    QMenuBar::item:selected {{
        background: {COLORS['primary_light']};
        color: {COLORS['primary']};
    }}
    
    QStatusBar {{
        background: {COLORS['white']};
        border-top: 1px solid {COLORS['gray_light']};
        color: {COLORS['text_secondary']};
        font-size: 13px;
    }}
    
    QSplitter::handle {{
        background: {COLORS['gray_light']};
        width: 2px;
    }}
    
    QSplitter::handle:hover {{
        background: {COLORS['primary_light']};
    }}
"""
