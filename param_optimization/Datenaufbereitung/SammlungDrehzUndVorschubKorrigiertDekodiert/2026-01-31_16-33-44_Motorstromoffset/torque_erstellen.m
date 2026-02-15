
%% Daten laden

clear all;
clc;

current = readmatrix("currentAnfangAbgeschnitten.csv");
position = readmatrix("positionAnfangAbgeschnitten.csv");

% Zeit bei 0 starten lassen
current(:,1) = current(:,1) + abs(current(1,1));
position(:,1) = position(:,1) + abs(position(1,1));

%% Daten vorverarbeiten

current_offset = -52.38; % mA
current(:,2) = current(:,2) + current_offset;

%% To do shape-matching, also Positionswerte downsampeln auf shape von current
% Dann das ganze auf eine Frequenz interpolieren (Ich glaube der solver braucht
% feste Schritte
%
% Dann jeweils an den Hochpunkten der Position (oder Wendepunkten also
% 2. Ableitung?) Vorzeichen des Stroms ändern
% Zuletzt noch mit Motorkonstante multiplizieren und dann in Datenstruktur
% bringen. 
%
% https://de.mathworks.com/matlabcentral/answers/450562-what-is-the-best-way-to-smooth-and-compute-the-derivatives-of-noisy-data


duration_measurement = current(end, 1) - current(1, 1);
sampling_rate = 1 / (duration_measurement / length(current));
target_sampling_rate = sampling_rate * 0.9; %% arbiträrer puffer
% convert to timeseries

ts_current = timeseries(current(:, 2), current(:, 1));
ts_position = timeseries(position(:, 2), position(:, 1));
ts_position = getsamples(ts_position, ts_position.Time <= ts_current.Time(end) & ...
        ts_position.Time >= ts_current.Time(1));

new_time = 0:(1 / target_sampling_rate):min(ts_current.Time(end), ts_position.Time(end));
ts_current = resample(ts_current, new_time, 'linear');
ts_position = resample(ts_position, new_time, 'linear');


%%

order = 3;
framelen = ceil(sampling_rate * 0.05);

if mod(framelen, 2) == 0
    framelen = framelen +1;
end

 position_filtered = sgolayfilt(ts_position.Data, order, framelen);
% hold on;
% plot(ts_position.Data, DisplayName="POSITION");
% plot(position_filtered, DisplayName="gefiltert");
% hold off;

%%

velocity = gradient(position_filtered);
velocity_filtered = sgolayfilt(velocity, order, framelen);
acceleration = gradient(velocity_filtered);


% figure;
% 
% subplot(3,1,1);
% plot(ts_position.Data, 'Color', 'b');
% title('Position');
% 
% subplot(3,1,2);
% plot(velocity_filtered, 'Color', 'r');
% title('Velocity');
% 
% subplot(3,1,3);
% plot(acceleration, 'Color', 'g');
% title('Acceleration');
% 
% linkaxes(findall(gcf, 'Type', 'axes'), 'x');

%%

threshold_velocity = 1.8e-4;
vorzeichen = ones(size(velocity_filtered));
vorzeichen(velocity_filtered > threshold_velocity) = 1;
vorzeichen(velocity_filtered < -threshold_velocity) = -1;
% close all;
% figure;
% 
% subplot(3,1,1);
% plot(ts_position.Data, 'Color', 'b');
% title('Position');
% 
% subplot(3,1,2);
% plot(velocity_filtered, 'Color', 'r');
% title('Velocity');
% 
% subplot(3,1,3);
% plot(vorzeichen, 'Color', 'cyan', LineWidth=2);
% title('vz');
% 
% linkaxes(findall(gcf, 'Type', 'axes'), 'x');

%% Drehmoment 


MOTORKONSTANTE = 0.08 * 10^-3; %% Auf Nm / mA gebracht
torque = ts_current.Data .* vorzeichen .* MOTORKONSTANTE;
close all;
hold on;
subplot(3,1,1);
plot(ts_position.Data, color='g');
title("position");

subplot(3,1,2);
plot(ts_current.Data, color='r', LineStyle='-')
title("current")
subplot(3,1,3);
plot(torque, Color='b', LineStyle='-')
title("Torque")
linkaxes(findall(gcf, 'Type', 'axes'), 'x');

hold off;

%% Torque und Positions csv erstellen

% Save torque and position data to CSV files
writematrix([ts_position.Time, ts_position.Data], 'position_sim.csv');
writematrix([ts_current.Time, torque], 'torque_sim.csv');

fprintf("Abtastpunkte: %d\n", length(ts_current.Data));
fprintf("Zeitschritt: %f\n", ts_current.Time(2) - ts_current.Time(1));
