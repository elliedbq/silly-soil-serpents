%% SIDEWINDING SIMULATION V2
L = 0.11; % link length estimate meters
% angles are in reference to the y axis
pt1 = [0,0];
pt2 = [2*L*sin(-5*pi/4), 2*L*cos(-5*pi/4)];
pt3 = [pt2(1) + 2*L*sin(-7*pi/4), pt2(2) + 2*L*cos(-7*pi/4)];
pt4 = [pt3(1) + 2*L*sin(-5*pi/4), pt3(2) + 2*L*cos(-5*pi/4)];
pts = [pt1; pt2; pt3; pt4];

% plot the points
figure(); hold on;
plot(pts(:,1), pts(:,2), 'b-', LineWidth = 2, DisplayName = 'Stage 1')

%% Second Position
pt4_2 = pt4;
pt3_2 = pt3;
pt2_2 = [pt3_2(1)-2*L, pt3_2(2)];
pt1_2 = [0, pt2_2(2) + 2*L*cos(pi/4)];
pts_2 = [pt1_2; pt2_2; pt3_2; pt4_2];

plot(pts_2(:,1), pts_2(:,2), 'm-', LineWidth=2, DisplayName='Stage 2')

%% Back to Original Shape
pts_3 = [pts(:,1), pts(:,2)+(pt3_2(2) - pt4_2(2))];

plot(pts_3(:,1), pts_3(:,2), 'r-', LineWidth=2, DisplayName='Stage 3');
title('Shape Change During Sidewinding (from Above)')
xlabel('X-Position(m)')
ylabel('Y-Position(m)')
legend();
axis square
%% Vertical links positioning
