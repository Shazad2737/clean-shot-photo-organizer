"""
Modern styling and themes for the CLEAN SHOT application.
"""

# Modern color palette
COLORS = {
    'primary': '#2c3e50',      # Dark blue-gray
    'secondary': '#3498db',    # Blue
    'success': '#27ae60',      # Green
    'warning': '#f39c12',      # Orange
    'danger': '#e74c3c',       # Red
    'light': '#ecf0f1',        # Light gray
    'dark': '#2c3e50',         # Dark gray
    'white': '#ffffff',        # White
    'text': '#2c3e50',         # Text color
    'text_light': '#7f8c8d',   # Light text
    'border': '#bdc3c7',       # Border color
    'background': '#ffffff',   # Background
    'surface': '#f8f9fa'       # Surface color
}

# Modern button styles
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: {COLORS['white']};
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: #2980b9;
            transform: translateY(-1px);
        }}
        QPushButton:pressed {{
            background-color: #21618c;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_light']};
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['white']};
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: #229954;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_light']};
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['white']};
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: #c0392b;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_light']};
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['light']};
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            padding: 10px 22px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['surface']};
            border-color: {COLORS['secondary']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['light']};
            color: {COLORS['text_light']};
            border-color: {COLORS['border']};
        }}
    """
}

# Modern widget styles
WIDGET_STYLES = {
    'group_box': f"""
        QGroupBox {{
            font-weight: 600;
            font-size: 16px;
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: {COLORS['background']};
        }}
    """,
    
    'progress_bar': f"""
        QProgressBar {{
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            background-color: {COLORS['light']};
        }}
        QProgressBar::chunk {{
            background-color: {COLORS['success']};
            border-radius: 6px;
        }}
    """,
    
    'label': f"""
        QLabel {{
            color: {COLORS['text']};
            font-size: 14px;
        }}
    """,
    
    'spin_box': f"""
        QSpinBox {{
            border: 2px solid {COLORS['border']};
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            background-color: {COLORS['white']};
        }}
        QSpinBox:focus {{
            border-color: {COLORS['secondary']};
        }}
    """,
    
    'check_box': f"""
        QCheckBox {{
            color: {COLORS['text']};
            font-size: 14px;
            font-weight: 500;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {COLORS['border']};
            border-radius: 4px;
            background-color: {COLORS['white']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['success']};
            border-color: {COLORS['success']};
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORS['secondary']};
        }}
    """
}

# Application-wide styles
APPLICATION_STYLE = f"""
    QMainWindow {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
    
    QWidget {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    QGroupBox {{
        {WIDGET_STYLES['group_box']}
    }}
    
    QProgressBar {{
        {WIDGET_STYLES['progress_bar']}
    }}
    
    QLabel {{
        {WIDGET_STYLES['label']}
    }}
    
    QSpinBox {{
        {WIDGET_STYLES['spin_box']}
    }}
    
    QCheckBox {{
        {WIDGET_STYLES['check_box']}
    }}
"""
