
%% Signale für das Simulinkmodell aus der Torque.csv erstellen

dataset = Simulink.SimulationData.Dataset;

%% 2026-01-31_16-44-26_MyPilger5_1_F6000
input_data = readmatrix("2026-01-31_16-44-26_MyPilger5_1_F6000/torque_sim.csv");
ts_torque = timeseries(input_data(:,2), input_data(:,1));
ts_torque.Name = "2026-01-31_16-44-26_MyPilger5_1_F6000";

dataset = dataset.addElement(ts_torque, ts_torque.Name);

%% 2026-01-31_17-03-16doppelsinusF_5126_A1_5_f1_5_A2_2_f2_5_1
% Abtastpunkte: 5013 #
% Zeitschritt: 0.001594 s
% last timestep = 7.991560477871520 s
% start pos = 0.004777600000000 mm

input_data_1 = readmatrix("2026-01-31_17-03-16doppelsinusF_5126_A1_5_f1_5_A2_2_f2_5_1/torque_sim.csv");

ts_torque_1 = timeseries(input_data_1(:,2), input_data_1(:,1));
ts_torque_1.Name = "doppelsinus";
dataset = dataset.addElement(ts_torque_1, ts_torque_1.Name);

save("newtest.mat", 'dataset');

%%

plot(dataset{1}.Data)
%%
plot(dataset{2}.Data)