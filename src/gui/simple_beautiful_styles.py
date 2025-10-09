"""
Simple but beautiful styling system that works with Qt.
"""

# Beautiful color palette
COLORS = {
    'primary': '#667eea',        # Beautiful purple-blue
    'primary_dark': '#5a67d8',   # Darker purple
    'primary_light': '#a8b4f5',  # Light purple
    
    'secondary': '#764ba2',      # Deep purple
    'accent': '#f093fb',         # Pink accent
    
    'success': '#48bb78',        # Modern green
    'success_light': '#c6f6d5', # Light green
    'warning': '#ed8936',        # Modern orange
    'warning_light': '#fef5e7', # Light orange
    'danger': '#f56565',         # Modern red
    'danger_light': '#fed7d7',   # Light red
    'info': '#4299e1',           # Modern blue
    'info_light': '#bee3f8',    # Light blue
    
    'dark': '#2d3748',           # Dark gray
    'gray': '#718096',          # Medium gray
    'gray_light': '#a0aec0',    # Light gray
    'light': '#f7fafc',         # Very light gray
    'white': '#ffffff',         # Pure white
    
    'text_primary': '#2d3748',   # Primary text
    'text_secondary': '#4a5568', # Secondary text
    'text_tertiary': '#718096',  # Tertiary text
}

# Simple but beautiful button styles
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_dark']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #38a169;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['white']};
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #e53e3e;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_light']};
            color: {COLORS['text_tertiary']};
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['white']};
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            padding: 12px 26px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['white']};
            color: {COLORS['text_tertiary']};
            border-color: {COLORS['gray_light']};
        }}
    """
}

# Simple but beautiful widget styles
WIDGET_STYLES = {
    'main_window': f"""
        QMainWindow {{
            background-color: {COLORS['light']};
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
            background-color: {COLORS['white']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 12px 0 12px;
            background-color: {COLORS['white']};
            color: {COLORS['primary']};
        }}
    """,
    
    'card': f"""
        QFrame {{
            background-color: {COLORS['white']};
            border: 1px solid {COLORS['gray_light']};
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
            background-color: {COLORS['gray_light']};
            min-height: 24px;
        }}
        QProgressBar::chunk {{
            background-color: {COLORS['primary']};
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
            background-color: {COLORS['white']};
            color: {COLORS['text_primary']};
        }}
        QSpinBox:focus {{
            border-color: {COLORS['primary']};
        }}
        QSpinBox:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """,
    
    'slider': f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background-color: {COLORS['gray_light']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background-color: {COLORS['primary']};
            border: none;
            width: 20px;
            height: 20px;
            border-radius: 10px;
            margin: -7px 0;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: {COLORS['primary_dark']};
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
            background-color: {COLORS['white']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
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
            background-color: {COLORS['light']};
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
            background-color: {COLORS['success_light']};
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
            background-color: {COLORS['white']};
            border-radius: 12px;
            border: 1px solid {COLORS['gray_light']};
        }}
    """
}

# Simple but beautiful application-wide styles
APPLICATION_STYLE = f"""
    QMainWindow {{
        {WIDGET_STYLES['main_window']}
    }}
    
    QWidget {{
        background-color: transparent;
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
        background-color: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QMenuBar {{
        background-color: {COLORS['white']};
        border-bottom: 1px solid {COLORS['gray_light']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 16px;
        border-radius: 6px;
        color: {COLORS['text_primary']};
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['primary_light']};
        color: {COLORS['primary']};
    }}
    
    QStatusBar {{
        background-color: {COLORS['white']};
        border-top: 1px solid {COLORS['gray_light']};
        color: {COLORS['text_secondary']};
        font-size: 13px;
    }}
    
    QSplitter::handle {{
        background-color: {COLORS['gray_light']};
        width: 2px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['primary_light']};
    }}
"""
