%% Load Messwerte
current = readmatrix("current.csv");
position = readmatrix("position.csv");

% Extract time and data columns
time_current = current(:, 1);
data_current = current(:, 2);
time_pos = position(:, 1);
data_pos = position(:, 2);

%% Manuell extrahierte Punkte (indices into position data)
before_rise_indices_pos = [1, 5, 9, 13, 17, 21, 25, 29, 31, 35];
after_rise_indices_pos = [2, 6, 10, 14, 18, 22, 26, 30, 34];
before_fall_indices_pos = [3, 7, 11, 15, 19, 23, 27, 31, 35];
after_fall_indices_pos = [4, 8, 12, 16, 20, 24, 28, 32, 36];

%% Create figure with dual y-axis
figure('Position', [100, 100, 1200, 600]);

% Plot with two y-axes
yyaxis left
plot(time_pos, data_pos, 'b-', 'LineWidth', 1.5, 'DisplayName', 'Position');
ylabel('Position');
set(gca, 'YColor', 'b');

yyaxis right
plot(time_current, data_current, 'r-', 'LineWidth', 1.5, 'DisplayName', 'Current');
ylabel('Current');
set(gca, 'YColor', 'r');

xlabel('Time');
title('Position and Current vs Time');
grid on;
hold on;

%% Add vertical lines at marked indices
% Get y-axis limits for vertical lines
yyaxis right
ylim_vals = ylim;

% Collect all unique time values for vertical lines
all_indices = unique([before_rise_indices_pos, after_rise_indices_pos, ...
                      before_fall_indices_pos, after_fall_indices_pos]);

% Filter out indices that exceed array bounds
valid_indices = all_indices(all_indices <= length(time_pos));

% Define colors for different marker types
colors = struct();
colors.before_rise = [0, 0.6, 0];      % Green
colors.after_rise = [0, 0.8, 0.8];     % Cyan
colors.before_fall = [0.8, 0, 0.8];    % Magenta
colors.after_fall = [1, 0.5, 0];       % Orange

% Plot vertical lines for before_rise (green, solid)
for i = 1:length(before_rise_indices_pos)
    idx = before_rise_indices_pos(i);
    if idx <= length(time_pos)
        xline(time_pos(idx), '-', 'Color', colors.before_rise, 'LineWidth', 1, ...
              'Alpha', 0.7, 'HandleVisibility', 'off');
    end
end

% Plot vertical lines for after_rise (cyan, dashed)
for i = 1:length(after_rise_indices_pos)
    idx = after_rise_indices_pos(i);
    if idx <= length(time_pos)
        xline(time_pos(idx), '--', 'Color', colors.after_rise, 'LineWidth', 1, ...
              'Alpha', 0.7, 'HandleVisibility', 'off');
    end
end

% Plot vertical lines for before_fall (magenta, solid)
for i = 1:length(before_fall_indices_pos)
    idx = before_fall_indices_pos(i);
    if idx <= length(time_pos)
        xline(time_pos(idx), '-', 'Color', colors.before_fall, 'LineWidth', 1, ...
              'Alpha', 0.7, 'HandleVisibility', 'off');
    end
end

% Plot vertical lines for after_fall (orange, dashed)
for i = 1:length(after_fall_indices_pos)
    idx = after_fall_indices_pos(i);
    if idx <= length(time_pos)
        xline(time_pos(idx), '--', 'Color', colors.after_fall, 'LineWidth', 1, ...
              'Alpha', 0.7, 'HandleVisibility', 'off');
    end
end

%% Add legend with dummy lines for marker types
hold on;
h1 = plot(NaN, NaN, '-', 'Color', colors.before_rise, 'LineWidth', 2);
h2 = plot(NaN, NaN, '--', 'Color', colors.after_rise, 'LineWidth', 2);
h3 = plot(NaN, NaN, '-', 'Color', colors.before_fall, 'LineWidth', 2);
h4 = plot(NaN, NaN, '--', 'Color', colors.after_fall, 'LineWidth', 2);

yyaxis left
h_pos = plot(NaN, NaN, 'b-', 'LineWidth', 1.5);
yyaxis right
h_cur = plot(NaN, NaN, 'r-', 'LineWidth', 1.5);

legend([h_pos, h_cur, h1, h2, h3, h4], ...
       {'Position', 'Current', 'Before Rise', 'After Rise', 'Before Fall', 'After Fall'}, ...
       'Location', 'best');

hold off;

%% 
clc;
A = [1,2,3,4,5, ; 
     6,7,8,9,10];

display(length(A))
