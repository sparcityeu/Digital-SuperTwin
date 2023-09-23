import supertwin_cross_save as supertwin
import influx_help
import utils


if __name__ == "__main__":

    dolap_SuperTwin = supertwin.SuperTwin("10.36.52.138")
    fedora_SuperTwin = supertwin.SuperTwin("localhost")

    
    dolap_SuperTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    dolap_id = dolap_SuperTwin.execute_observation_parameters("/common_data/SparseBaseOrderExample", 1, "compact", "dolap_rcm|./rcm 1138_bus.mtx")
    dolap_id_2 = dolap_SuperTwin.execute_observation_parameters("/common_data/SparseBaseOrderExample", 1, "compact", "dolap_random|./random 1138_bus.mtx")

    fedora_SuperTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    fedora_id = fedora_SuperTwin.execute_observation_parameters("/home/fatih/SparseBaseOrderExample", 1, "compact", "fedora_rcm|./rcm 1138_bus.mtx")
    fedora_id_2 = fedora_SuperTwin.execute_observation_parameters("/home/fatih/SparseBaseOrderExample", 1, "compact", "fedora_random|./random 1138_bus.mtx")

    
    print("Dolap rcm id: ", dolap_id)
    print("Dolap random id: ", dolap_id_2)

    print("Fedora rcm id: ", fedora_id)
    print("Fedora random id: ", fedora_id_2)
    

    influx_help.normalize_twin_tags([dolap_SuperTwin, dolap_id],
                                    [dolap_SuperTwin, dolap_id_2],
                                    [fedora_SuperTwin, fedora_id],
                                    [fedora_SuperTwin, fedora_id_2])

    
    utils.multinode_comparison([dolap_SuperTwin, dolap_id],                                     
                               [dolap_SuperTwin, dolap_id_2],
                               [fedora_SuperTwin, fedora_id],
                               [fedora_SuperTwin, fedora_id_2])
    

    
