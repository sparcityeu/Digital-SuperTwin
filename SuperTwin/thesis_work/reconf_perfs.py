import supertwin




if __name__ == "__main__":

    dolap_supertwin = supertwin.SuperTwin("10.36.54.195")
    deren_supertwin = supertwin.SuperTwin("10.92.53.74")
    poseidon_supertwin = supertwin.SuperTwin("10.92.55.4")
    luna_supertwin = supertwin.SuperTwin("10.36.52.109")
    
    dolap_supertwin.reconfigure_observation_events_parameterized("general_perfevent.txt")
    deren_supertwin.reconfigure_observation_events_parameterized("general_perfevent.txt")
    poseidon_supertwin.reconfigure_observation_events_parameterized("general_perfevent.txt")
    luna_supertwin.reconfigure_observation_events_parameterized("luna_perfevent.txt")
