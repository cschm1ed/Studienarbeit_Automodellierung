c  = [1.685082264734805,1.6814466953741207e-06,0.009999993257493107,0.9000145671384575,0.10000133609148719,0.0020000187958843815,8.47842304562683e-05]
start_position = 0.0047776


%%

plot(dataset{1}.Data)


%%

load('testdataset.mat');
m = rand(2, 7);  % 2 particles, 7 parameters
in = simulinkSimulationInputArray(m, 2, 'doppelsinusF_5126_A1_5_f1_5_A2_2_f2_5_1_7V');
out = parsim(in, 'TransferBaseWorkspaceVariables', 'on');