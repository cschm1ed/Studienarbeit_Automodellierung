%% Create simulation signals

clear all;
%%
current = readmatrix("jonas_fahrten/2026-02-28_11-30-31_doppelsinus_75s/current_modbus.csv");
position = readmatrix("2026-02-28_11-30-31_doppelsinus_75s/position.csv");

ts_current = timeseries(current(:,3), current(:,1));
ts_position = timeseries(position(:,2), position(:,1));

sample_duration = ts_current.Time(end) / numel(ts_current.Time());
disp(1 / sample_duration);

start_time = -58.5088;
end_time =  -0.317575;
duration = end_time - start_time;
ts_position = getsamples(ts_position, ts_position.Time >= start_time & ts_position.Time <= end_time);

start_time = 35.306612540428738;
end_time = start_time + duration;
ts_current = getsamples(ts_current, ts_current.Time >= start_time & ts_current.Time <= end_time);

start_time = ts_position.Time(1);
ts_position.Time = ts_position.Time - start_time;

start_time = ts_current.Time(1);
ts_current.Time = ts_current.Time - start_time;

%%
sample_duration = seconds(0.02);

TT_current = timeseries2timetable(ts_current);
TT_position = timeseries2timetable(ts_position);

TT_current = retime(TT_current, 'regular', 'linear', 'TimeStep', sample_duration);
TT_position = retime(TT_position, 'regular', 'linear', 'TimeStep', sample_duration);
TT_position(end, :) = [];
%%

subplot(3,1,1);
plot(TT_position.Time, TT_position.Variables, DisplayName="Position");
subplot(3,1,2);
plot(TT_current.Time, TT_current.Variables, DisplayName="Strom Modbus");
writetimetable(TT_position, "position_sim.csv");
writetimetable(TT_current, "current_modbus_sim.csv");

%%



%%
Motorkonstante = -0.08 / 1000; % Nm / A
torque_data = (TT_current.Variables) .* Motorkonstante;
time_sec = seconds(TT_current.Time);  % convert duration to double
ts_torque = timeseries(torque_data, time_sec);
%%

close all;
t1 = 7.36;
t2 = 53.84;
t3 = 44.54;
t4 = 47.64;
t5 = 25.94;
t6 = 29.04;

% theoretisch könnte man das auch im gleitenden durchschnitt über die
% Dauer einer halben Periode machen.

mask = (ts_torque.Time >= t1 & ts_torque.Time <= t2); %%...
     % | (ts_torque.Time >= t3 & ts_torque.Time <= t4) ...
     % | (ts_torque.Time >= t5 & ts_torque.Time <= t6);
offset_total = sum(ts_torque.Data(mask));
len = numel(ts_torque.Data(mask));
offset = offset_total / len;
%%
ts_torque.Data = ts_torque.Data - offset;
ts_torque.Name = "2026-02-28_11-30-31_doppelsinus_75s_1_autocorell_timefit";
dataset = Simulink.SimulationData.Dataset;
dataset = dataset.addElement(ts_torque, ts_torque.Name);
save("doppelsinus_75s_1_autocorell_timefit.mat", "dataset");

%%

c = [01.12E-02	8.84E+07	1.97E+00	8.10E-01	1.00E+08	9.51E-01	5.02E-02	9.35E-04	5.73E+07	9.43E-07	1.55E-03	1.16E-04	4.49E+07	6.83E-01	1.23E+00	5.89E-03	6.82E-06	1.26E+03];

start_position = 20.000000000000000;

%%
% drift_total = sum(ts_torque.Data);
% offset = drift_total / numel(ts_torque.Data);
% 
% ts_torque_drift_corrected = ts_torque;
% ts_torque_drift_corrected.Data = ts_torque.Data - offset;
% 
% ts_torque_drift_corrected.Name = "drift_corrected_2026-02-21_14-46-32_doppelsinus_A1_40_T_10";
% dataset = Simulink.SimulationData.Dataset;
% dataset = dataset.addElement(ts_torque_drift_corrected, ts_torque_drift_corrected.Name);
% save("drift_corrected_doppelsinus.mat", "dataset");


ax1 = subplot(2, 1, 1);
hold on;
plot(TT_position.Time, x_Sim, 'Color', 'r');
plot(TT_position.Time, TT_position.Data, 'Color', 'b');
hold off;

ax2 = subplot(2, 1, 2);
plot(TT_current.Time, TT_current.Data);

linkaxes([ax1, ax2], 'x');

%%

