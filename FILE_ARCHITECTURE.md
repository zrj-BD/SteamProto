# Newer Structure Documentation

```
project/
├── window.pyw                 # Main entry point (simplified)
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # Window class (main application)
│   ├── settings_window.py     # Settings class
│   ├── editor_window.py       # Editor class
│   ├── library_view.py        # Library tab view
│   ├── data_view.py          # Data tab view
│   └── components/
│       ├── __init__.py
│       ├── game_card.py      # Reusable game card widget
│       └── data_table.py     # Reusable data table widget
│       └── pixmaps.py        # Reusable loaded pixmaps
├── core/
│   ├── __init__.py
│   ├── data_manager.py       # Data loading/saving logic
│   └── scan_scheduler.py     # Automatic scan logic
├── utils/
│   ├── __init__.py
│   ├── constants.py          # All constants
│   └── helpers.py            # Utility functions
├── scanner.py                # Folder Scanning Application
├── remover.py                # Marker Removing Application
├── web.py                    # SteamCMD Caller
└── theme_manager.py          # Theme Style Manager
```