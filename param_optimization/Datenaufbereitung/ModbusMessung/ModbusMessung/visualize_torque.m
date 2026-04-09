
clear all;
%%
data_ihsv = readmatrix("2026-02-21_14-46-32_doppelsinus_A1_40_T_10/current_modbus.csv");
data_meas = readmatrix("2026-02-21_14-46-32_doppelsinus_A1_40_T_10/current.csv");

%%

% hold on;
% 
% subplot(2,1,1);
% plot(data_ihsv(:,1), abs(data_ihsv(:,2)));
% 
% subplot(2,1,2);
% plot(data_meas(:,1), data_meas(:,2));
% hold off;

%%

sampling_rate = data_ihsv(end, 1) / length(data_ihsv(:,1));
%sampling_rate = 1/sampling_rate


%%

modbus_ts = timeseries(data_ihsv(:,3), data_ihsv(:,1));
meas_ts = timeseries(data_meas(:,2), data_meas(:,1));

modbus_ts = getsamples(modbus_ts, modbus_ts.Time >= 1.69 & modbus_ts.Time <= 11.1587);
meas_ts = getsamples(meas_ts, meas_ts.Time >= -9.66 & meas_ts.Time <= -0.188);
%%
start_time = modbus_ts.Time(1);
modbus_ts.Time = modbus_ts.Time - start_time;

start_time = meas_ts.Time(1);
meas_ts.Time = meas_ts.Time - start_time;

%%

close all;
hold on;
plot(modbus_ts.Time, modbus_ts.Data, color="red");
plot(meas_ts.Time, meas_ts.Data, color="blue");
hold off;