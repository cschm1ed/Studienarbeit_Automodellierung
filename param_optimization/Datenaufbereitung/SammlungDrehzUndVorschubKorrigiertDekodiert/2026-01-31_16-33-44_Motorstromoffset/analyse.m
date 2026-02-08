%% Messwerte
current = readmatrix("current.csv");
position = readmatrix("position.csv");
time_pos = position(:, 1);
time_current = current(:, 1);

%% Sortieren und 4er-Muster extrahieren
[~, sort_order] = sort([cursor_info_pos.DataIndex]);
cursor_info_pos_sorted = cursor_info_pos(sort_order);

before_rise_indices_pos = [cursor_info_pos_sorted(1:4:end).DataIndex];
after_rise_indices_pos  = [cursor_info_pos_sorted(2:4:end).DataIndex];
before_fall_indices_pos = [cursor_info_pos_sorted(3:4:end).DataIndex];
after_fall_indices_pos  = [cursor_info_pos_sorted(4:4:end).DataIndex];

%% Current-Indizes: Finde nächsten Zeitpunkt
pos2current = @(pos_idx) arrayfun(@(i) find(abs(time_current - time_pos(i)) == min(abs(time_current - time_pos(i))), 1), pos_idx);

before_rise_indices_current = pos2current(before_rise_indices_pos);
after_rise_indices_current  = pos2current(after_rise_indices_pos);
before_fall_indices_current = pos2current(before_fall_indices_pos);
after_fall_indices_current  = pos2current(after_fall_indices_pos);

%% Segmente extrahieren (mit plateau_low)
n_cycles = length(after_fall_indices_pos);

rising_pos = [];
rising_current = [];
plateau_high_pos = [];
plateau_high_current = [];
falling_pos = [];
falling_current = [];
plateau_low_pos = [];
plateau_low_current = [];

nan_row_pos = [NaN, NaN];
nan_row_current = [NaN, NaN];

for k = 1:n_cycles
    % Rising: before_rise -> after_rise
    rising_pos = [rising_pos; position(before_rise_indices_pos(k):after_rise_indices_pos(k), :); nan_row_pos];
    rising_current = [rising_current; current(before_rise_indices_current(k):after_rise_indices_current(k), :); nan_row_current];
    
    % Plateau High: after_rise -> before_fall
    plateau_high_pos = [plateau_high_pos; position(after_rise_indices_pos(k):before_fall_indices_pos(k), :); nan_row_pos];
    plateau_high_current = [plateau_high_current; current(after_rise_indices_current(k):before_fall_indices_current(k), :); nan_row_current];
    
    % Falling: before_fall -> after_fall
    falling_pos = [falling_pos; position(before_fall_indices_pos(k):after_fall_indices_pos(k), :); nan_row_pos];
    falling_current = [falling_current; current(before_fall_indices_current(k):after_fall_indices_current(k), :); nan_row_current];
    
    % Plateau Low: after_fall -> before_rise (nächster Zyklus)
    if k < n_cycles
        plateau_low_pos = [plateau_low_pos; position(after_fall_indices_pos(k):before_rise_indices_pos(k+1), :); nan_row_pos];
        plateau_low_current = [plateau_low_current; current(after_fall_indices_current(k):before_rise_indices_current(k+1), :); nan_row_current];
    end
end

%% Plot 1: Rising
figure('Position', [100, 100, 1000, 400]);
yyaxis left
plot(rising_pos(:,1), rising_pos(:,2), 'b-');
ylabel('Position');
yyaxis right
plot(rising_current(:,1), rising_current(:,2), 'r-');
ylabel('Current');
title('Rising');
legend({'Position', 'Current'});
grid on;

%% Plot 2: Plateau (High und Low)
figure('Position', [100, 550, 1000, 400]);
yyaxis left
plot(plateau_high_pos(:,1), plateau_high_pos(:,2), 'b-');
hold on;
plot(plateau_low_pos(:,1), plateau_low_pos(:,2), 'b--');
ylabel('Position');
yyaxis right
plot(plateau_high_current(:,1), plateau_high_current(:,2), 'r-');
hold on;
plot(plateau_low_current(:,1), plateau_low_current(:,2), 'r--');
ylabel('Current');
title('Plateau (solid=high, dashed=low)');
legend({'Pos High', 'Pos Low', 'Curr High', 'Curr Low'});
grid on;

%% Plot 3: Falling
figure('Position', [100, 1000, 1000, 400]);
yyaxis left
plot(falling_pos(:,1), falling_pos(:,2), 'b-');
ylabel('Position');
yyaxis right
plot(falling_current(:,1), falling_current(:,2), 'r-');
ylabel('Current');
title('Falling');
legend({'Position', 'Current'});
grid on;

%% Plot gesammt
hold on;
yyaxis left;
plot(current(:,1), current(:,2), DisplayName="Strom", color="r");
yyaxis right;
plot(position(:,1), position(:,2), DisplayName="Position", color="b");
grid on;
legend();
hold off;

%% Strom bevor fahrt
% x = x_1...-118.632

sum = 0;
i = 1;
while current(i, 1) <= -118.632
    sum = sum + current(i, 2);
    i = i + 1;
end

average = sum / i;
display(average);
