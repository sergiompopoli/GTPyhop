import sys
sys.path.append('../')
import gtpyhop


# Helper functions -------------------------------------------------------------------------------#
def is_element_ready(element):
    """
    Placeholder: Check if hardware component is operational
    TODO: Implement hardware status checking
    """
    return True  # For now, assume all elements are ready

def get_oocyte_at_location(state, location):
    """
    Get the oocyte ID at a specific location, or None if no oocyte there
    """
    for oocyte_id, oocyte_location in state.oocyte_location.items():
        if oocyte_location == location:
            return oocyte_id
    return None

def has_known_position(state, oocyte_id):
    """
    Check if an oocyte has a known position within its droplet
    """
    return state.oocyte_position.get(oocyte_id) == 'known'

def set_oocyte_position_known(state, location):
    """
    Mark an oocyte's position as known (after computer vision locates it)
    """
    oocyte_id = get_oocyte_at_location(state, location)
    if oocyte_id:
        state.oocyte_position[oocyte_id] = 'known'
        return True
    return False

def set_oocyte_position_unknown(state, location):
    """
    Mark an oocyte's position as unknown (after releasing, oocyte moves in fluid)
    """
    oocyte_id = get_oocyte_at_location(state, location)
    if oocyte_id:
        state.oocyte_position[oocyte_id] = 'unknown'
        return True
    return False

def perform_autofocus():
    """
    Mock autofocus helper function
    In reality, this would interact with microscope hardware to optimize focus
    For planning purposes, we just need to know the operation was performed
    """
    import random
    import time
    time.sleep(0.1)  # Mock processing time
    return random.choice([True])  # Always succeeds for mock

def update_oocyte_status(state, location, new_status):
    """
    Update the status of an oocyte at a specific location
    """
    oocyte_id = get_oocyte_at_location(state, location)
    if oocyte_id:
        state.oocyte_status[oocyte_id] = new_status
        return True
    return False


def create_initial_state(show_state=False):
    """Create and return the initial world state for ICSIA"""
    state = gtpyhop.State('icsia_world')

    state.locations = {'l_droplet_01', 'l_droplet_02', 'l_droplet_03', 'l_sperm_droplet',
                       'l_pvp_droplet', 'l_holding_p_parking', 'l_icsi_pipette_parking', 'l_plate_center'}
    
    state.elements = {'holding_p', 'icsi_p', 'microscope'}
    #state.magnifications = {'4x', '10x', '20x'}

    # High level element positions
    state.current_location = {'holding_p': 'l_holding_p_parking',
                              'icsi_p': 'l_icsi_pipette_parking',
                              'microscope': 'l_plate_center'}

    state.held_oocyte = None  # None or oocyte_id (e.g., 'oocyte_001') 
    state.icsi_p_has_sperm = False
    #state.microscope_magnification = '4x'

    # Oocyte tracking: three separate state variables with oocyte_id as key
    state.oocyte_location = {
        'oocyte_001': 'l_droplet_01',
        'oocyte_002': 'l_droplet_02', 
        'oocyte_003': 'l_droplet_03'
    }

    # Possible values: fresh, injected or damaged.
    state.oocyte_status = {
        'oocyte_001': 'fresh',
        'oocyte_002': 'damaged',
        'oocyte_003': 'fresh'
    }
    
    # If the real XYZ position is known, probably by the CV
    state.oocyte_position = {
        'oocyte_001': 'unknown',  # 'unknown' or 'known'
        'oocyte_002': 'unknown',
        'oocyte_003': 'unknown'
    }

    if show_state:
        state.display()

    return state