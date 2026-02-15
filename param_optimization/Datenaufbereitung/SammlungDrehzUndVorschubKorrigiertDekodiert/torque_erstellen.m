
%% Daten laden

clear all;
clc;

plots = true;

addpath("2026-01-31_17-03-16doppelsinusF_5126_A1_5_f1_5_A2_2_f2_5_1/");

current = readmatrix("currentAnfangAbgeschnitten.csv");
position = readmatrix("positionAnfangAbgeschnitten.csv");

% Zeit bei 0 starten lassen
current(:,1) = current(:,1) + abs(current(1,1));
position(:,1) = position(:,1) + abs(position(1,1));

%% Daten vorverarbeiten

current_offset = -38.0533; % mA
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

    hold on;
    plot(ts_position.Data, DisplayName="POSITION");
    plot(position_filtered, DisplayName="gefiltert");
    hold off;


%%

velocity = gradient(position_filtered);
velocity_filtered = sgolayfilt(velocity, order, framelen);
acceleration = gradient(velocity_filtered);


    figure;
    
    subplot(4,1,1);
    plot(ts_position.Data, 'Color', 'b');
    title('Position');
    
    subplot(4,1,2);
    plot(velocity_filtered, 'Color', 'r');
    title('Velocity');
    
    subplot(4,1,3);
    plot(acceleration, 'Color', 'g');
    title('Acceleration');
 
    subplot(4,1,4);
    plot(current(:,2), 'Color', 'magenta');
    title('current');
    

    linkaxes(findall(gcf, 'Type', 'axes'), 'x');

%%

% threshold_velocity = 5e-4;
% vorzeichen = ones(size(velocity_filtered));
% vorzeichen(velocity_filtered > threshold_velocity) = 1;
% vorzeichen(velocity_filtered < -threshold_velocity) = -1;

thresohold_acceleration = 1e-4;
vorzeichen = ones(size(acceleration));
vorzeichen(acceleration > thresohold_acceleration) = 1;
vorzeichen(acceleration < -thresohold_acceleration) = -1;

% close all;
if plots
    figure;
    
    subplot(3,1,1);
    plot(ts_position.Data, 'Color', 'b');
    title('Position');
    
    subplot(3,1,2);
    plot(velocity_filtered, 'Color', 'r');
    title('Velocity');
    
    subplot(3,1,3);
    plot(vorzeichen, 'Color', 'cyan', LineWidth=2);
    title('vz');
    
    linkaxes(findall(gcf, 'Type', 'axes'), 'x');
end
%% Drehmoment 


MOTORKONSTANTE = 0.08 * 10^-3;
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


%%

offset_total = sum(vorzeichen .* ts_current.Data);

offset_global = offset_total / length(ts_current.Data);

%% 38.0533 mA bei doppelsinus17-03-16

