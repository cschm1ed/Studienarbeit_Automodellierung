%{
Autor: Yann Rutschke
Date: 05.06.2023
Store x_Sim place which is callable from python.

------Input---------
    out : simulink.SimulationOutput 
    i: int

------Output--------
    gxSim: double array comprising x_Sim
%}

function gxSim = getxSim(out, i)

    gxSim = out(1,i).x_Sim;

end

