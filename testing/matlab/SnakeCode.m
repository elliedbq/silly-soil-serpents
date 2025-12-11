%% SERPENTINE MOTION %%

%Assumptions: 
%The snake follows a serpentine/serpenoid curve

% Definitions:
v_s = 0.5; %The snake's constant velocity along the curve (input, m/s)
n = 3; %number of links (3 links that can move horizontally)
L = 0.5; %total length, m
r = .06; %radius of curve, m
K_n = 0.5; % degree of curve
beta = (2*K_n*pi)/n; %phase lag
% alpha_0 = %curvature amplitude - don't know how to calculate??
joints = (1:n+1);
t_run = 5; % run length (seconds)

% Parameters that we control:
alpha = 0.4; % winding angle parameter, change this to change the shape of the motion
omega = 0.5; % speed parameter, change this to change speed
gamma = -0.05; % heading parameter, changes direction (0=straight forward)

%% Parameters in context:
% alpha = -2*alpha_0*sin(K*n*pi/n)
% omega = ((2*K*n*pi)/L)*v_s

%% MOTOR ANGLE EQUATION %%

% theta_i(t) = alpha*sin(omega*t + beta_i) + gamma, i = 1,...,n-1

% create a matrix, (joint #, time) inside has corresponding joint angles
%
%    t1  t2  t3  t4  t5  t6
% j Γ .   .   .   .   .   . ᄀ
% o | .   .   .   .   .   .  |
% i | .   .   .   .   .   .  |
% n | .   .   .   .   .   .  |
% t | .   .   .   .   .   .  |
%   | .   .   .   .   .   .  |
% # L .   .   .   .   .   .  」

time = (1:t_run*1000); % milliseconds
theta = zeros(n-1, length(time)); % columns are for each joint, rows are for each time step

for t = time
	for j = joints(1:end-1)
		theta(j, t) = alpha*sin(omega*t + beta.*j) + gamma;
	end
end

% theta is in RAD
%% Get x and y position of joints
% to get x and y position of the joints, we need angle relative to the
% y-axis (phi)

% for each link, phi_x(i+1) = theta(i+1) + phi_x(i)
% in matrix form, phi_x = E*theta + e*theta_0, where E = tril(ones(n, n-1), -1)
% i am going to go with the link by link way so that I don't have to find
% theta_0, which requires the initial curve amplitude

% initializing matrix phi_x
phi_x = zeros(size(theta));
phi_x(1, 1) = theta(1, 1); % the first angle is not offset

for t = time
    for j = joints(1:end-1)
        phi_x(j+1, t) = theta(j+1) + phi_x(j);
    end
end

% getting y-axis angle from x-axis angle
phi_y = pi/2 - phi_x;

% get joint location from phi_y
% initialize x and y position matrices
x_pos = zeros(size(theta));
y_pos = zeros(size(theta));

% we are starting from the origin
x_pos(1, 1) = 0;
y_pos(1, 1) = 0;

for i = 1:(numel(x_pos)-1)
    x_pos(i+1) = r*sin(phi_y(i+1)) + x_pos(i);
    y_pos(i+1) = r*cos(phi_y(i+1)) + y_pos(i);
end

%% PLOT joint position

% start by plotting the snake position at t = 1 (1 millisecond)

% figure(); hold on;
plot(x_pos(:, 1), y_pos(:, 1), 'r-'); hold on;

% and now at other times

for i = 1:10
    plot(x_pos(:, i), y_pos(:, i), 'r-')
end

title('Snake Position Sequence')
xlabel('X Position (m)')
ylabel('Y Position(m)')

% need to figure out gamma parameter, why it moves at an angle, timing and
% why links don't overlap