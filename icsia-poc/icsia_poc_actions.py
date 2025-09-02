import sys
sys.path.append('../')
import gtpyhop
from icsia_poc_state import is_element_ready, get_oocyte_at_location, has_known_position, set_oocyte_position_known, set_oocyte_position_unknown, perform_autofocus, update_oocyte_status


# Action definitions -----------------------------------------------------------------------------#
def move_element_to(state, element, loc):
    if element in state.elements and loc in state.locations and is_element_ready(element):
        state.current_location[element] = loc
        return state
    return None

def hold_oocyte(state):
    # Find the location of the holding pipette
    holding_p_loc = state.current_location['holding_p']
    # Check if there's a fresh oocyte at that location with known position
    oocyte_id = get_oocyte_at_location(state, holding_p_loc)
    if (oocyte_id and 
        state.oocyte_status.get(oocyte_id) == 'fresh' and
        has_known_position(state, oocyte_id) and
        state.held_oocyte is None and  # Not already holding an oocyte
        is_element_ready('holding_p')):
        state.held_oocyte = oocyte_id  # Track which specific oocyte is held
        return state
    return None

def release_oocyte(state):
    if state.held_oocyte is not None and is_element_ready('holding_p'):
        # Get the oocyte currently being held
        held_oocyte_id = state.held_oocyte
        holding_p_loc = state.current_location['holding_p']
        
        # Mark position as unknown (oocyte will move in fluid after release)
        set_oocyte_position_unknown(state, holding_p_loc)
        
        # Update oocyte location to current pipette location (in case it moved)
        state.oocyte_location[held_oocyte_id] = holding_p_loc
        
        # Release the oocyte
        state.held_oocyte = None
        return state
    return None

def capture_sperm(state):
    # Check if ICSI pipette is at sperm droplet
    icsi_p_location = state.current_location['icsi_p']
    if (icsi_p_location == 'l_sperm_droplet' and not state.icsi_p_has_sperm and is_element_ready('icsi_p')):
        state.icsi_p_has_sperm = True
        return state
    return None

def release_sperm(state):
    # Check if ICSI pipette is holding sperm and the pipette is operational. If so, release sperm.
    if state.icsi_p_has_sperm and is_element_ready('icsi_p'):
        state.icsi_p_has_sperm = False
        return state
    return None

def locate_oocyte_in_droplet(state, droplet):
    """
    Computer Vision Action: Locate an oocyte within a droplet
    Mock implementation - in reality this would use image analysis
    """
    oocyte_id = get_oocyte_at_location(state, droplet)
    if (oocyte_id and 
        state.oocyte_status.get(oocyte_id) == 'fresh' and 
        state.current_location['microscope'] == droplet and
        is_element_ready('microscope')):
        
        # Mock CV: In reality, this would analyze the image and determine x,y,z coordinates
        # For planning purposes, we just mark the position as 'known'
        set_oocyte_position_known(state, droplet)
        return state
    return None

def focus_on_oocyte(state, oocyte_id):
    """
    Pure focus action - assumes microscope is already at oocyte location
    Checks focus and performs autofocus if needed
    """
    # Check if oocyte exists and has known position
    if (oocyte_id in state.oocyte_location and 
        has_known_position(state, oocyte_id) and 
        is_element_ready('microscope')):
        
        # Verify microscope is at the oocyte's location
        droplet = state.oocyte_location[oocyte_id]
        if state.current_location['microscope'] != droplet:
            return None  # Microscope not at correct location
        
        # Mock focus check: assume oocyte needs refocusing
        import random
        is_in_focus = random.choice([True, False])  # Mock focus check
        
        if not is_in_focus:
            # Use autofocus helper - in reality this adjusts microscope focus
            # For planning purposes, position remains 'known'
            perform_autofocus() # TODO: Could it fail? What if it does?
        
        return state
    return None

def inject_sperm_into_oocyte(state):
    # Check if the holding pipette has an oocyte and the ICSI pipette has sperm
    # Both pipettes must be at the same location with a fresh oocyte
    if (state.held_oocyte is not None and state.icsi_p_has_sperm and
        is_element_ready('holding_p') and is_element_ready('icsi_p')):
        
        # Get current locations of both pipettes
        holding_p_loc = state.current_location['holding_p']
        icsi_p_loc = state.current_location['icsi_p']
        
        # Get the oocyte being held
        held_oocyte_id = state.held_oocyte
        
        # Check if both pipettes are at same location and held oocyte is fresh
        if (holding_p_loc == icsi_p_loc and 
            state.oocyte_status.get(held_oocyte_id) == 'fresh'):
            # Inject sperm into the held oocyte
            state.icsi_p_has_sperm = False
            state.oocyte_status[held_oocyte_id] = 'injected'
            return state
    return None


#~ Command Implementations (Hardware Execution) --------------------------------------------------#
# These are the functions that should actually interface with the different modules, UI, motors, CV, etc.

def c_move_element_to(state, element, loc):
    """Command: Execute actual hardware movement"""
    import random
    print(f"> [EXECUTING]: Moving {element} to {loc}")
    
    # Simulate hardware failures
    if random.random() < 0.1:  # 10% chance of movement failure
        print(f">>> [ERROR]: Hardware failure - {element} movement blocked!")
        return False
    
    # Simulate positioning errors (treat as complete failures)
    if element == 'microscope' and random.random() < 0.15:  # 15% chance for microscope
        print(f">>> [ERROR]: Microscope positioning error - movement failed!")
        print(f">>> [ERROR]: Precise positioning required for {element} - replanning needed!")
        return False
    
    # Normal successful execution
    return move_element_to(state, element, loc)

def c_hold_oocyte(state):
    """Command: Execute actual oocyte holding via hardware"""
    import random
    print("> [EXECUTING]: Holding oocyte with pipette")
    
    # Simulate pipette suction failure
    if random.random() < 0.2:  # 20% chance of suction failure
        print(">>>>> [ERROR]: Pipette suction failure - cannot hold oocyte!")
        return False
    
    # Simulate oocyte movement out of view
    if random.random() < 0.15:  # 15% chance oocyte moves away
        print(">>> [ERROR]: Oocyte moved out of image field during approach!")
        # Mark oocyte position as unknown since it moved - but still fail the command
        holding_p_loc = state.current_location['holding_p']
        oocyte_id = get_oocyte_at_location(state, holding_p_loc)
        if oocyte_id:
            state.oocyte_position[oocyte_id] = 'unknown'
        return False
    
    return hold_oocyte(state)

def c_release_oocyte(state):
    """Command: Execute actual oocyte release via hardware"""
    import random
    print("> [EXECUTING]: Releasing oocyte from pipette")
    
    # Simulate rare release failures
    if random.random() < 0.05:  # 5% chance of release mechanism failure
        print(">>>>> [ERROR]: Release mechanism failure - oocyte stuck to pipette!")
        return False
    
    return release_oocyte(state)

def c_capture_sperm(state):
    """Command: Execute actual sperm capture via hardware"""
    import random
    print("> [EXECUTING]: Capturing sperm with ICSI pipette")
    
    # Simulate sperm capture failures
    if random.random() < 0.25:  # 25% chance of no sperm found
        print(">>> [ERROR]: No viable sperm found in droplet!")
        return False
    
    if random.random() < 0.1:  # 10% chance of pipette blockage
        print(">>> [ERROR]: ICSI pipette blocked - cannot capture sperm!")
        return False
    
    return capture_sperm(state)

def c_release_sperm(state):
    """Command: Execute actual sperm release via hardware"""
    import random
    print("> [EXECUTING]: Releasing sperm from ICSI pipette")
    
    # Simulate rare sperm release failures
    if random.random() < 0.08:  # 8% chance of sperm sticking to pipette
        print(">>> [ERROR]: Sperm adhered to pipette tip - cannot release!")
        return False
    
    return release_sperm(state)

def c_inject_sperm_into_oocyte(state):
    """Command: Execute actual sperm injection via hardware"""
    import random
    print("> [EXECUTING]: Injecting sperm into oocyte")
    
    # Simulate injection failures
    if random.random() < 0.18:  # 18% chance of injection failure
        print(">>> [ERROR]: Injection failed - oocyte membrane too tough or sperm lost!")
        return False
    
    if random.random() < 0.12:  # 12% chance of oocyte damage
        print("> [FATAL ERROR]: Oocyte damaged during injection!")
        print("> [FATAL ERROR]: This oocyte cannot be recovered - injection goal is impossible!")
        # Terminal failure - no plan can fix a damaged oocyte
        return False
    
    return inject_sperm_into_oocyte(state)

def c_locate_oocyte_in_droplet(state, droplet):
    """Command: Execute actual computer vision oocyte location"""
    import random
    print(f"> [EXECUTING]: Computer vision locating oocyte in {droplet}")
    
    # Simulate computer vision failure
    if random.random() < 0.15:  # 15% chance oocyte cannot be found
        print(f">>> [ERROR]: Computer vision failed - no oocyte detected in {droplet}!")
        # Explicitly mark oocyte position as unknown after CV failure - but still fail
        oocyte_id = get_oocyte_at_location(state, droplet)
        if oocyte_id:
            state.oocyte_position[oocyte_id] = 'unknown'
            print(f">>> [ERROR]: {oocyte_id} position marked as unknown - cannot focus!")
        return False
    
    return locate_oocyte_in_droplet(state, droplet)

def c_focus_on_oocyte(state, oocyte_id):
    """Command: Execute actual microscope focus adjustment"""
    import random
    print(f"> [EXECUTING]: Focusing microscope on {oocyte_id}")
    
    # Check preconditions explicitly in command
    if not has_known_position(state, oocyte_id):
        print(f">>> [ERROR]: Cannot focus on {oocyte_id} - position is unknown!")
        print(f">>> [ERROR]: Computer vision localization must succeed first!")
        return False
    
    # Check if microscope is at correct location
    droplet = state.oocyte_location[oocyte_id]
    if state.current_location['microscope'] != droplet:
        print(f">>> [ERROR]: Microscope not at {droplet} - cannot focus on {oocyte_id}!")
        return False
    
    # Simulate autofocus failures
    if random.random() < 0.12:  # 12% chance of autofocus failure
        print(">>> [ERROR]: Autofocus failed - cannot achieve sharp focus!")
        return False
    
    return focus_on_oocyte(state, oocyte_id)