import sys
sys.path.append('../')
import gtpyhop

# Import from separate modules
from icsia_poc_state import create_initial_state
from icsia_poc_actions import (
    move_element_to, hold_oocyte, release_oocyte, capture_sperm, release_sperm,
    locate_oocyte_in_droplet, focus_on_oocyte, inject_sperm_into_oocyte,
    c_move_element_to, c_hold_oocyte, c_release_oocyte, c_capture_sperm,
    c_release_sperm, c_locate_oocyte_in_droplet, c_focus_on_oocyte, c_inject_sperm_into_oocyte
)
from icsia_poc_tasks import (
    m_perform_icsi_injection_in_droplet, m_perform_icsi_injection_to_oocyte,
    m_prepare_for_injection, m_complete_injection, m_locate_and_focus
)
from icsia_poc_goals import (
    achieve_oocyte_status_goal, achieve_oocyte_position_goal, achieve_held_oocyte_goal,
    achieve_icsi_has_sperm, m_move_element_to
)


#~ Domain Setup Functions ----------------------------------------------------------------------->

def register_domain_knowledge(domain):
    """Register all actions, tasks, and goals with the domain"""
    gtpyhop.current_domain = domain
    
    #~ Register Actions -----------------------------------------------------
    gtpyhop.declare_actions(move_element_to,
                            hold_oocyte,
                            release_oocyte,
                            capture_sperm,
                            release_sperm,
                            inject_sperm_into_oocyte,
                            locate_oocyte_in_droplet,
                            focus_on_oocyte)
    
    #~ Register Commands -----------------------------------------------------
    gtpyhop.declare_commands(c_move_element_to,
                             c_hold_oocyte,
                             c_release_oocyte,
                             c_capture_sperm,
                             c_release_sperm,
                             c_inject_sperm_into_oocyte,
                             c_locate_oocyte_in_droplet,
                             c_focus_on_oocyte)
    
    #~ Register Tasks -----------------------------------------------------------------------------
    gtpyhop.declare_task_methods('perform_icsi_injection', m_perform_icsi_injection_in_droplet, m_perform_icsi_injection_to_oocyte)
    gtpyhop.declare_task_methods('prepare_for_injection', m_prepare_for_injection)
    gtpyhop.declare_task_methods('complete_injection', m_complete_injection)
    gtpyhop.declare_task_methods('locate_and_focus', m_locate_and_focus)

    #~ Register Goals -----------------------------------------------------------------------------
    gtpyhop.declare_unigoal_methods('current_location', m_move_element_to)
    gtpyhop.declare_unigoal_methods('oocyte_status', achieve_oocyte_status_goal)
    gtpyhop.declare_unigoal_methods('oocyte_position', achieve_oocyte_position_goal)
    gtpyhop.declare_unigoal_methods('held_oocyte', achieve_held_oocyte_goal)
    gtpyhop.declare_unigoal_methods('icsi_p_has_sperm', achieve_icsi_has_sperm)

    #~ Register Multigoals ------------------------------------------------------------------------
    # Multigoal methods will be added here


#~ Test Presentation Functions --------------------------------------------------------------->

def print_welcome_header():
    """Print welcome header for ICSIA application"""
    print("="*100)
    print("       WELCOME TO ICSIA PROOF OF CONCEPT USING GTPYHOP")
    print("="*100)
    print()

def print_section_separator(section_name, is_header=True):
    """Print section header or footer with visual distinction"""
    if is_header:
        # Header uses # symbols and ">>> STARTING" format
        print("\n" + "#"*100)
        print(f">>> STARTING: {section_name}")
        print("#"*100)
        print()
    else:
        # Footer uses = symbols and "<<< COMPLETED" format  
        print("\n" + "="*100)
        print(f"<<< COMPLETED: {section_name}")
        print("="*100)
        print()

def print_test_result(test_num, test_name, goal_description, goal_tuple, plan):
    """
    Print formatted test result with goal and plan
    
    Args:
        test_num (int): Test number
        test_name (str): Name of the test
        goal_description (str): Human-readable goal description
        goal_tuple (tuple): The actual goal tuple
        plan (list): Generated plan or None if failed
    """
    print("-"*100)
    print(f"        TEST {test_num}: {test_name.upper()}")
    print("-"*100)
    print(f"Goal: {goal_description}")
    print(f"Target: {goal_tuple}\n")
    
    if plan:
        print("SUCCESS: Plan Found!")
        step_count = len(plan)
        print(f"\nGenerated Plan ({step_count} step{'s' if step_count != 1 else ''}):")
        for i, action in enumerate(plan, 1):
            print(f"  {i:2d}. {action}")
    else:
        print("FAILURE: No plan found")
    
    print()  # Extra line for spacing

#~ Main ------------------------------------------------------------------------------------------>
def main():
    import sys

    print_welcome_header()
    
    # Parse command line arguments for verbosity
    verbosity = 1  # Default verbosity
    if len(sys.argv) > 1:
        try:
            verbosity = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid verbosity level '{sys.argv[1]}'. Using default (1).")
    
    # Create domain and register all knowledge
    the_domain = gtpyhop.Domain("icsia_poc")
    register_domain_knowledge(the_domain)
    
    # Create initial state
    state = create_initial_state(show_state=True)

    gtpyhop.print_methods()
    
    print_section_separator("PLANNER TESTS", is_header=True)

    # Request a plan for a certain state
    gtpyhop.verbose = verbosity  # Set verbosity from CLI parameter


    # Test 1: Inject oocyte
    my_goal_01 = [('oocyte_status', 'oocyte_001', 'injected')]
    plan_for_goal1 = gtpyhop.find_plan(state, my_goal_01)
    
    print_test_result(
        test_num=1,
        test_name="Inject Oocyte by ID",
        goal_description="Change oocyte_001 status to 'injected'",
        goal_tuple=my_goal_01[0],
        plan=plan_for_goal1
    )
    
    # Test 2: Locate oocyte position
    my_goal_02 = [('oocyte_position', 'oocyte_001', 'known')]
    plan_for_goal2 = gtpyhop.find_plan(state, my_goal_02)
    
    print_test_result(
        test_num=2,
        test_name="Locate Oocyte Position",
        goal_description="Make oocyte_001 position known via computer vision",
        goal_tuple=my_goal_02[0],
        plan=plan_for_goal2
    )

    # Test 3: Same as Goal 1 but we already have sperm in the ICSI pipette. 
    state.icsi_p_has_sperm = True
    plan_for_goal3 = gtpyhop.find_plan(state, my_goal_01)

    print_test_result(
        test_num=3,
        test_name="Inject Oocyte with Sperm already in the pipette",
        goal_description="Change oocyte_001 status to 'injected' with sperm present",
        goal_tuple=my_goal_01[0],
        plan=plan_for_goal3
    )

    # Test 4: Inject oocyte but we're already holding a different oocyte
    state.held_oocyte = 'oocyte_002'
    plan_for_goal4 = gtpyhop.find_plan(state, my_goal_01)

    print_test_result(
        test_num=4,
        test_name="Inject Oocyte with Different Oocyte Held, and sperm already in the pipette.",
        goal_description="Change oocyte_001 status to 'injected' while holding oocyte_002",
        goal_tuple=my_goal_01[0],
        plan=plan_for_goal4
    )

    print_section_separator("PLANNER TESTS", is_header=False)

    print_section_separator("PLAN AND EXECUTION", is_header=True)

    final_state = gtpyhop.run_lazy_lookahead(state, [('oocyte_status', 'oocyte_001', 'injected')])

    final_state.display()

    print_section_separator("PLAN AND EXECUTION", is_header=False)


if __name__ == '__main__':

    main()