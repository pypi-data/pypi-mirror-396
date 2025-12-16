"""CSS styles for the unified Textual TUI."""

UNIFIED_TUI_CSS = """
Screen {
    align: center middle;
}

#menu-container {
    width: 60;
    height: auto;
    border: solid $primary;
    padding: 1;
}

#menu-title {
    text-align: center;
    width: 100%;
    margin: 1;
}

#menu-buttons {
    width: 100%;
    height: auto;
}

#menu-buttons > Button {
    width: 100%;
    margin: 1;
}

/* Common container styles */
#search-container, #list-container, #get-container,
#definition-container, #info-container,
#evaluate-container, #check-container,
#host-container, #device-container,
#get-by-phone-container, #get-by-alias-container, #list-aliases-container {
    width: 90;
    height: auto;
    border: solid $primary;
    padding: 1;
}

/* Common title styles */
#search-title, #list-title, #get-title,
#definition-title, #info-title,
#evaluate-title, #check-title,
#host-title, #device-title,
#get-by-phone-title, #get-by-alias-title, #list-aliases-title {
    text-align: center;
    width: 100%;
    margin: 1;
}

/* Common results area */
#search-results, #sp-list {
    height: 20;
    width: 100%;
}

#result-area, #info-area {
    height: 30;
    width: 100%;
    scrollbar-size: 1 1;
}

TextArea {
    scrollbar-gutter: stable;
}

/* Input fields */
#search-input, #sp-id-input, #account-id-input,
#flag-id-input, #extension-id-input, #email-domain-input,
#host-query, #device-udid, #platform-select,
#phone-input, #alias-input {
    width: 100%;
    margin: 1;
}

/* Button groups */
#search-buttons, #list-buttons, #get-buttons,
#definition-buttons, #info-buttons,
#evaluate-buttons, #check-buttons,
#host-buttons, #device-buttons,
#get-by-phone-buttons, #get-by-alias-buttons, #list-aliases-buttons {
    width: 100%;
    height: auto;
    margin-top: 1;
}

#search-buttons > Button, #list-buttons > Button,
#get-buttons > Button, #definition-buttons > Button,
#info-buttons > Button,
#evaluate-buttons > Button, #check-buttons > Button,
#host-buttons > Button, #device-buttons > Button,
#get-by-phone-buttons > Button, #get-by-alias-buttons > Button, #list-aliases-buttons > Button {
    margin: 1;
}

TabbedContent {
    height: 1fr;
}

TabPane {
    padding: 0;
    height: 1fr;
    width: 1fr;
}

ContentSwitcher {
    height: 1fr;
    width: 1fr;
    /* Make every tab/page vertically scrollable at the viewport level */
    overflow-y: auto;
    overflow-x: hidden;
}

/* Embedded Screen Styles */
/* Hide Header and Footer in embedded screens to avoid duplication */
ContentSwitcher > * Header, ContentSwitcher > * Footer {
    display: none;
    height: 0;
    margin: 0;
    padding: 0;
    border: none;
}

/* Reset embedded Screen styles */
ContentSwitcher > * {
    layer: initial;
    position: relative;
    display: block;
    /* Allow embedded pages to grow; scrolling is handled by ContentSwitcher */
    height: auto;
    min-height: 100%;
    width: 1fr;
    border: none;
    align: center top;
    padding: 1;
}

/* Ensure inner containers don't restrict height if they want to scroll */
ContentSwitcher > * > Vertical,
ContentSwitcher > * > Container {
    height: auto;
    min-height: 100%;
    overflow: auto;
}

SPMenuWidget, FFSMenuWidget, DeviceSpyMenuWidget, AccountPoolMenuWidget {
    width: 1fr;
    height: 1fr;
    align: center top;
    /* Scroll handled by VerticalScroll inheritance */
}
"""


