import sys
sys.path.append('../')
import gtpyhop


#~ Goal Methods for State-Based Planning ----------------------------------------------------------#

def achieve_oocyte_status_goal(state, oocyte_id, desired_status):
    """
    Goal: Make oocyte with specific ID have the desired status
    """
    # Check if oocyte exists and needs status change
    if (oocyte_id in state.oocyte_status and 
        state.oocyte_status[oocyte_id] == 'fresh' and 
        desired_status == 'injected'):
        return [('perform_icsi_injection', oocyte_id)]
    
    return []  # Goal already achieved or not applicable

def achieve_oocyte_position_goal(state, oocyte_id, desired_position):
    """
    Goal: Make oocyte with specific ID have the desired position knowledge
    """
    # Check if oocyte exists and needs position change
    if (oocyte_id in state.oocyte_position and 
        state.oocyte_position[oocyte_id] == 'unknown' and 
        desired_position == 'known'):
        return [('locate_and_focus', oocyte_id)]
    
    return []  # Goal already achieved or not applicable

def achieve_held_oocyte_goal(state, target_oocyte_id):
    """
    Goal: Hold a specific oocyte by ID (None means release any held oocyte)
    """
    if target_oocyte_id is None:
        # Goal: Release any held oocyte
        if state.held_oocyte is not None:
            return [('release_oocyte',)]
    else:
        # Goal: Hold a specific oocyte
        if (state.held_oocyte != target_oocyte_id and 
            target_oocyte_id in state.oocyte_status and
            state.oocyte_status[target_oocyte_id] == 'fresh'):
            tasks = []
            
            # If holding a different oocyte, release it first
            if state.held_oocyte is not None:
                tasks.append(('release_oocyte',))
            
            # Move to target oocyte and hold it
            location = state.oocyte_location[target_oocyte_id]
            tasks.extend([('move_element_to', 'holding_p', location), ('hold_oocyte',)])
            return tasks
    
    return []  # Goal already achieved

def achieve_icsi_has_sperm(state, should_have):
    """
    Goal: Control whether ICSI pipette has sperm
    """
    if should_have and not state.icsi_p_has_sperm:
        return [('move_element_to', 'icsi_p', 'l_sperm_droplet'), ('capture_sperm',)]
    elif not should_have and state.icsi_p_has_sperm:
        return [('release_sperm',)]

#~ Simple Goal Methods to call Actions ------------------------------------------------------------#
def m_move_element_to(state, element, loc):
    """Goal method: Move an element to a location"""
    return [('move_element_to', element, loc)]