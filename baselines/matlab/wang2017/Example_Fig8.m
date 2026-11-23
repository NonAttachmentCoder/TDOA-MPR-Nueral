% This program generates the results for TDOA MLE_MPR.
%
% Reference: Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range," IEEE 
%  Trans. Signal Process., vol. 65, no. 6, pp. 1447-1460, Mar. 2017.
%
% The figure generated from this code corresponds to Fig. 8 in the reference.  
%
% NOTE: slow processing time is mainly caused by running CVX to obtain the SDR solution
%
% Yue Wang, K. C. Ho    11-28-2018, updated
% Yue Wang, K. C. Ho    05-18-2017
%
%       Copyright (C) 2017
%       Computational Intelligence Signal Processing Laboratory
%       University of Missouri
%       Columbia, MO 65211, USA.
%       hod@missouri.edu
%

clc; 
clear all;
warning off;  % Program initialization.

addpath('.\cvx')
cvx_setup

L = 1000;                               % Number of ensemble runs.     

randn('seed',0);                        % Initialize random number generator.
rand('seed',5050); 

uo=[-1 5 3]';
[thetao phio ro]=cart2sph(uo(1),uo(2),uo(3));

x=[0   -4.6400   -4.9400   -5.0500   -0.2800   -5.4400   -5.4000   -5.9700   -8.1100   -3.4600];
y=[0    6.6000   -2.1300    3.8400    5.0700    7.0400    6.6300    5.8200   -0.2800    0.4100];
z=[0    1.5500    2.1500    1.8500   -4.3100    3.1000   -5.4900   -5.9700   -4.0800   -4.0800];
s=[x; y; z];
s=s(:,1:6);                             % use six sensors

M = size(s,2);                          % Number of sensors
N = size(s,1);                          % Dimension of localization

R = (eye(M-1)+ones(M-1))/2;             % covariance structure of TDOA
NsePwrVecdB=-20; 

dbr=10:5:160;
fprintf('Simulation in progress');

for dbrIdx=1:length(dbr)
    randn('state',0);
    r_rd=randn(M-1,L);
    m_rd=mean(r_rd,2);
    n_rd=r_rd-m_rd*ones(1,L);
    
    r=dbr(dbrIdx);
    uo_p=[thetao phio 1/r]';
    uo=[0 0 0]';
    [uo(1) uo(2) uo(3)]=sph2cart(thetao,phio,r);
    
    ro = sqrt(sum((uo*ones(1,M)-s).^2))';   % True source-sensor ranges
    rdo = ro(2:end)-ro(1);
    
% for nseIdx=1:length(NsePwrVedB),       % vary measurement noise level
for nseIdx=1:1,       % vary measurement noise level
    fprintf('.');
    nsePwr = 10^(NsePwrVecdB(nseIdx)/10);
    Q = nsePwr * R;                     % Covariance matrix of TDOA (range difference) noise
    
    [CRLB] = TDOALocCRLB_MPR(s,uo,Q);
    cb_theta3(dbrIdx)=CRLB(1,1);
    cb_phi3(dbrIdx)=CRLB(2,2);
    cb_invr(dbrIdx)=CRLB(3,3);
    cb_angles3(dbrIdx)=CRLB(1,1)+CRLB(2,2);

    SimulationMSE_u=0;
    SimulationMSE_r=0;
    SimulationMSE_angles2=0;
    SimulationMSET_invr = 0;
    SimulationMSET_theta = 0;
    SimulationMSET_phi = 0;
    SimulationMSEFFTS_angles=0;
    SimulationMSEMPMTS_angles=0;
    for k = 1 : L,                      % Monte Carlo Simulation.
        rdNse = sqrtm(Q) * randn(M-1,1);
        rd = rdo + sqrtm(Q)*n_rd(:,k);  % Noisy source TDOAs (range differences)
        upSDR=TDOA_SDRMPR_3D(s,rd,Q);   % SDR-MPR solution for initialization     
        [upT] = TDOA_MLEMPR(s,rd,Q,upSDR);   % MLE-MPR solution
        theta_upT(k)=upT(1);
        phi_upT(k)=upT(2);
        SimulationMSET_invr = SimulationMSET_invr + (upT(3)-uo_p(3))^2;
        SimulationMSET_theta = SimulationMSET_theta + (upT(1)-uo_p(1))^2;
        SimulationMSET_phi = SimulationMSET_phi + (upT(2)-uo_p(2))^2;
        SimulationMSEMPMTS_angles = SimulationMSEMPMTS_angles+sum(([upT(1:2)]-[uo_p(1:2)]).^2);
    end;
    mseT_invr(dbrIdx) = SimulationMSET_invr/L;
    mseMPMTS_angles(dbrIdx) = SimulationMSEMPMTS_angles/L;
end;
end;

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure; 
subplot(2,1,1);
plot(dbr,10*log10(cb_invr),'k'); grid on; hold on;
plot(dbr,10*log10(mseT_invr),'xk','MarkerSize',8); hold on;
hold off; grid on;
xlabel('Source Range'); 
ylabel('10 log(MSE(1/r))');
legend('CRLB','MLE-MPR','Location','southeast');
ylim([-55,-40]);
xlim([dbr(1),dbr(end)]);
subplot(2,1,2);
plot(dbr,10*log10(cb_angles3),'k'); grid on; hold on;
plot(dbr,10*log10(mseMPMTS_angles),'xk','MarkerSize',8); hold on;
hold off; grid on;
xlabel('Source Range'); 
ylabel('10 log(MSE(\theta))');
legend('HBB Bound','MLE-MPR','Location','southeast');
ylim([-40,-25]);
xlim([dbr(1),dbr(end)]);


