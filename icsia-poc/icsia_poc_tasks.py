import sys
sys.path.append('../')
import gtpyhop
from icsia_poc_state import get_oocyte_at_location


#~ Task Methods -----------------------------------------------------------------------------------#

def m_perform_icsi_injection_in_droplet(state, oocyte_droplet):
    """
    Complete ICSI procedure: Position microscope → Position pipettes → 
    Capture sperm → Hold oocyte → Inject → Release oocyte
    """
    oocyte_id = get_oocyte_at_location(state, oocyte_droplet)
    if oocyte_id and state.oocyte_status.get(oocyte_id) == 'fresh':
        return [
            ('move_element_to', 'microscope', oocyte_droplet),
            ('prepare_for_injection', oocyte_droplet),
            ('complete_injection', oocyte_droplet)
        ]
    
def m_perform_icsi_injection_to_oocyte(state, oocyte_id):
    """
    Complete ICSI procedure by oocyte ID: Locate & focus → Position pipettes → 
    Capture sperm → Hold oocyte → Inject → Release oocyte
    """
    # Check if oocyte exists and is fresh
    if (oocyte_id in state.oocyte_status and 
        state.oocyte_status[oocyte_id] == 'fresh'):
        
        oocyte_droplet = state.oocyte_location[oocyte_id]
        return [
            ('locate_and_focus', oocyte_id),
            ('prepare_for_injection', oocyte_droplet),
            ('complete_injection', oocyte_droplet)
        ]    

def m_prepare_for_injection(state, oocyte_droplet):
    """
    Setup phase: Handle oocyte switching → Capture sperm (if needed) → Hold target oocyte
    """
    tasks = []
    
    # Get the target oocyte ID at the specified droplet
    target_oocyte_id = get_oocyte_at_location(state, oocyte_droplet)
    
    # If we're holding a different oocyte, release it in a safe droplet location
    if (state.held_oocyte is not None and 
        state.held_oocyte != target_oocyte_id):
        
        # Get current held oocyte's location to determine where to release it
        held_oocyte_location = state.oocyte_location[state.held_oocyte]
        
        # Only release if we can move to a valid droplet (not parking)
        if held_oocyte_location.startswith('l_droplet_'):
            tasks.extend([
                ('move_element_to', 'holding_p', held_oocyte_location),
                ('release_oocyte',)
            ])
    
    # Only capture sperm if we don't already have it
    if not state.icsi_p_has_sperm:
        tasks.extend([
            ('move_element_to', 'icsi_p', 'l_sperm_droplet'),
            ('capture_sperm',)
        ])
    
    # Move to target oocyte and hold it (only if not already holding it)
    if state.held_oocyte != target_oocyte_id:
        tasks.extend([
            ('move_element_to', 'holding_p', oocyte_droplet),
            ('hold_oocyte',)
        ])
    
    return tasks

def m_complete_injection(state, oocyte_droplet):
    """
    Injection phase: Move ICSI pipette to oocyte droplet → Inject → Release oocyte
    """
    if (state.held_oocyte is not None and 
        state.current_location['holding_p'] == oocyte_droplet and
        state.icsi_p_has_sperm):
        return [
            ('move_element_to', 'icsi_p', oocyte_droplet),
            ('inject_sperm_into_oocyte',),
            ('release_oocyte',)
        ]

def m_locate_and_focus(state, oocyte_id):
    """
    Task: Complete locate-and-focus workflow for a specific oocyte
    Returns sequence: move microscope → locate → focus
    """
    # Check if oocyte exists and is fresh
    if (oocyte_id in state.oocyte_status and 
        state.oocyte_status[oocyte_id] == 'fresh'):
        droplet = state.oocyte_location[oocyte_id]
        return [
            ('move_element_to', 'microscope', droplet),
            ('locate_oocyte_in_droplet', droplet),
            ('focus_on_oocyte', oocyte_id)
        ]