#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Platform detection utilities for Featrix Sphere.

Provides functions to detect the execution environment (firmware vs development).
"""
import os
import platform
import logging

logger = logging.getLogger(__name__)


def os_is_featrix_firmware() -> bool:
    """
    Check if we're running on a Featrix firmware box (not development).
    
    Firmware boxes have:
    - /sphere directory exists
    - Running Linux (not Mac/Windows)
    
    Returns:
        True if running on Featrix firmware box, False otherwise
    """
    sphere_exists = os.path.exists('/sphere')
    is_linux = platform.system() == 'Linux'
    
    return sphere_exists and is_linux


def featrix_get_root() -> str:
    """
    Get the Featrix root directory.
    
    On firmware (production): /sphere
    On development (Mac/Linux): ~/sphere-workspace
    
    Creates the directory if it doesn't exist on development machines.
    
    Returns:
        Path to Featrix root directory
    """
    if os_is_featrix_firmware():
        return '/sphere'
    else:
        # Development machine - use ~/sphere-workspace
        home = os.path.expanduser('~')
        dev_root = os.path.join(home, 'sphere-workspace')
        
        # Create if doesn't exist
        os.makedirs(dev_root, exist_ok=True)
        
        return dev_root


def featrix_get_qa_root() -> str:
    """
    Get the QA test output directory.
    
    Prefers /scratch if mounted (large temp space on servers).
    Falls back to featrix_get_root()/qa-test.
    
    Creates the directory if it doesn't exist.
    
    Returns:
        Path to QA test output directory
    """
    # Check if /scratch is mounted and writable
    if os.path.exists('/scratch') and os.access('/scratch', os.W_OK):
        qa_root = '/scratch/qa-test'
    else:
        # Fall back to featrix_get_root()/qa-test
        qa_root = os.path.join(featrix_get_root(), 'qa-test')
    
    # Create if doesn't exist
    os.makedirs(qa_root, exist_ok=True)
    
    return qa_root

