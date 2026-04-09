clc
clear all
close all
modbus = readmatrix("torque_log_doppelsinus.csv");
measurement_current = readmatrix("modbus_referenzfahrten/2026-02-14_13-53-10/current.csv");
measurement_position = readmatrix("modbus_referenzfahrten/2026-02-14_13-53-10/position.csv");

%% truncate measurment from position time

plot(measurement_position(:, 1), measurement_position(:, 2));

% -13.742 - 0.1045

ts_current_meas = timeseries(measurement_current(:, 2), measurement_current(:, 1));
ts_position_meas = timeseries(measurement_position(:, 2), measurement_position(:, 1));

start_time = -13.742;
end_time = 0.1045;
ts_current_meas = getsamples(ts_current_meas, ts_current_meas.Time >= start_time & ts_current_meas.Time <= end_time);
ts_position_meas = getsamples(ts_position_meas, ts_position_meas.Time >= start_time & ts_position_meas.Time <= end_time);

subplot(3,1,1);
plot(ts_position_meas.Data);

subplot(3, 1, 2);
plot(ts_current_meas.Data);

subplot(3, 1, 3);
plot(modbus(:, 1), modbus(:, 3));

%% 10.1525 + (-13.742 - 0.1045)

ts_current_modbus = timeseries(modbus(:, 3), modbus(:, 1));
start_time = 10.726;
ts_current_modbus = getsamples(ts_current_modbus, ts_current_modbus.Time >= start_time & ...
    ts_current_modbus.Time <= (start_time + (abs(-13.742 - 0.1045))));

offset = ts_current_modbus.Time(1);
ts_current_modbus.Time = ts_current_modbus.Time - offset;
offset = ts_current_meas.Time(1);
ts_current_meas.Time = ts_current_meas.Time - offset;
offset = ts_position_meas.Time(1);
ts_position_meas.Time = ts_position_meas.Time - offset;

%%

close all;
subplot(3,1,1);
plot(ts_position_meas.Time, ts_position_meas.Data);

subplot(3, 1, 2);
plot(ts_current_meas.Time, ts_current_meas.Data);

subplot(3, 1, 3);
plot(ts_current_modbus.Time, ts_current_modbus.Data);
linkaxes(findall(gcf, 'Type', 'axes'), 'x');





