"""
Responsive CSS styles for mobile, tablet, and desktop layouts.

This module provides CSS generation functions for making the O-Zone Streamlit
application responsive across different device sizes with proper touch target
sizing for accessibility.
"""

import streamlit as st
import logging


def get_responsive_css() -> str:
    """
    Returns complete responsive CSS as a string for injection into Streamlit.
    
    Includes:
    - Mobile breakpoint (@media max-width: 768px) with single-column layout
    - Tablet breakpoint (@media min-width: 769px and max-width: 1024px) with two-column layout
    - Desktop breakpoint (@media min-width: 1025px) preserving existing layout
    - Touch target minimum sizing: 44px height, 44px width, 8px spacing
    - CSS classes: .mobile-header, .mobile-stack, .touch-target, .collapsible-section
    
    Returns:
        str: Complete CSS string ready for injection
    """
    css = """
    <style>
    /* Base styles for touch targets - applies to all screen sizes */
    .touch-target {
        min-height: 44px;
        min-width: 44px;
        margin: 8px;
        padding: 8px;
        cursor: pointer;
    }
    
    /* Ensure all buttons meet touch target requirements */
    button, .stButton > button {
        min-height: 44px;
        min-width: 44px;
        margin: 8px;
    }
    
    /* Ensure all input fields meet touch target requirements */
    input, select, textarea {
        min-height: 44px;
        padding: 8px;
        margin: 8px 0;
    }
    
    /* Mobile breakpoint: 320px to 768px */
    @media (max-width: 768px) {
        /* Single-column layout for mobile */
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        /* Compact header for mobile */
        .mobile-header {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 8px;
            background-color: #f0f2f6;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        /* Stack components vertically on mobile */
        .mobile-stack {
            display: flex;
            flex-direction: column;
            gap: 16px;
            width: 100%;
        }
        
        /* Collapsible sections for mobile navigation */
        .collapsible-section {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        
        .collapsible-section summary {
            padding: 12px;
            background-color: #f8f9fa;
            cursor: pointer;
            font-weight: 600;
            min-height: 44px;
            display: flex;
            align-items: center;
        }
        
        .collapsible-section details[open] summary {
            border-bottom: 1px solid #e0e0e0;
        }
        
        .collapsible-section .content {
            padding: 12px;
        }
        
        /* Force single column for Streamlit columns */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Adjust font sizes for mobile readability */
        h1 {
            font-size: 1.75rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.25rem;
        }
        
        /* Ensure no horizontal scrolling */
        .main {
            overflow-x: hidden;
        }
        
        /* Make images responsive */
        img {
            max-width: 100%;
            height: auto;
        }
        
        /* Adjust sidebar for mobile */
        [data-testid="stSidebar"] {
            width: 100%;
        }
    }
    
    /* Tablet breakpoint: 769px to 1024px */
    @media (min-width: 769px) and (max-width: 1024px) {
        /* Two-column layout for tablet */
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        
        /* Two-column grid for tablet */
        [data-testid="column"] {
            width: 48% !important;
            flex: 1 1 48% !important;
            min-width: 48% !important;
        }
        
        /* Stack components in two columns */
        .mobile-stack {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        /* Compact header for tablet */
        .mobile-header {
            display: flex;
            flex-direction: row;
            gap: 16px;
            padding: 12px;
            background-color: #f0f2f6;
            border-radius: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        
        /* Collapsible sections for tablet */
        .collapsible-section {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        .collapsible-section summary {
            padding: 12px;
            background-color: #f8f9fa;
            cursor: pointer;
            font-weight: 600;
            min-height: 44px;
            display: flex;
            align-items: center;
        }
    }
    
    /* Desktop breakpoint: 1025px and above */
    @media (min-width: 1025px) {
        /* Preserve existing multi-column layout for desktop */
        .main .block-container {
            max-width: 1200px;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        
        /* Desktop uses default Streamlit column behavior */
        [data-testid="column"] {
            /* Let Streamlit handle column widths naturally */
        }
        
        /* Hide mobile-specific elements on desktop */
        .mobile-header {
            display: none;
        }
        
        /* Desktop layout for stacked components */
        .mobile-stack {
            display: flex;
            flex-direction: row;
            gap: 24px;
            flex-wrap: wrap;
        }
        
        /* Collapsible sections always open on desktop */
        .collapsible-section {
            border: none;
        }
        
        .collapsible-section summary {
            display: none;
        }
        
        .collapsible-section .content {
            display: block;
        }
    }
    
    /* Touch feedback for all interactive elements */
    button:active, .stButton > button:active, .touch-target:active {
        transform: scale(0.98);
        opacity: 0.8;
        transition: all 0.1s ease;
    }
    
    /* Ensure adequate spacing between interactive elements */
    .stButton, .stTextInput, .stSelectbox, .stCheckbox, .stRadio {
        margin: 8px 0;
    }
    </style>
    """
    return css


def inject_responsive_styles() -> None:
    """
    Injects responsive CSS into the current Streamlit page.
    
    This function should be called at the start of the Streamlit app to apply
    responsive styles. Includes error handling with fallback to default styles.
    """
    try:
        css = get_responsive_css()
        st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.warning("⚠️ Responsive styles could not be loaded. Some features may not work on mobile.")
        logging.error(f"CSS injection failed: {e}")
