import supertwin
import utils




if __name__ == "__main__":

    my_superTwin = supertwin.SuperTwin("10.36.52.138")
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    my_superTwin.reconfigure_observation_events_parameterized("dolap_ai_perfevent.txt")
    
    my_superTwin.execute_observation_batch_parameters("", "likwid-pin -q -c N:0",
                                                      ["copy1|likwid-bench -t copy -w S0:100MB:1-0:S0,1:S1 -s 3",
                                                       "copy2|likwid-bench -t copy -w S0:50MB:1-0:S0,1:S1 -s 3",
                                                       "daxpy1|likwid-bench -t daxpy -w S0:100MB:1-0:S0,1:S1 -s 3",
                                                       "daxpy2|likwid-bench -t daxpy -w S0:50MB:1-0:S0,1:S1 -s 3"])
