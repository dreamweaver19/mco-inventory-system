allowed_transitions = {

"Receipt": ["Awaiting FFFT"],

"Awaiting FFFT": ["Under FFFT"],

"Under FFFT": ["Serviceable", "Unserviceable"],

"Serviceable": ["Issued"],

"Unserviceable": ["Disposal"]

}


def transition(current_state, new_state):

    if new_state in allowed_transitions.get(current_state, []):

        return True

    return False