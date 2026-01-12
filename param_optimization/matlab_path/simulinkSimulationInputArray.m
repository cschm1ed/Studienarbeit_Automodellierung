%{
Autor: Yann Rutschke
Date: 05.06.2023
Create an array of Simulink.SimulationInput object in Simulink.

------Input---------
    m : matrix
    n_pop: int
    simu: string

------Output--------
    in: Array of Simulink.SimulationInput object
%}

function in = simulinkSimulationInputArray(m, n_pop, simu)

    for i = n_pop:-1:1

        in(i) = Simulink.SimulationInput(simu);
        in(i) = in(i).setVariable('c', m(i,:));
    
    end

end