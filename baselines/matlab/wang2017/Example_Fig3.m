% This program generates the results for TDOA MLE_MPR.
% The figure generated from this code corresponds to Fig. 3 in the reference paper.  
%
% NOTE: the CVX results at low noise level are about 15 dB better than what being shown
% in Fig. 3 of the paper.
%
% NOTE: slow processing time is mainly caused by running CVX to obtain the SDR solution
%
% Reference: Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range," IEEE 
%  Trans. Signal Process., vol. 65, no. 6, pp. 1447-1460, Mar. 2017.
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

addpath('..\cvx')
cvx_setup

L = 1000;                               % Number of ensemble runs.     

randn('seed',0);                        % Initialize random number generator.
rand('seed',5050); 

uo=[-1 5 3]';                           % source position
[thetao phio ro]=cart2sph(uo(1),uo(2),uo(3));

x=[0   -4.6400   -4.9400   -5.0500   -0.2800   -5.4400   -5.4000   -5.9700   -8.1100   -3.4600];
y=[0    6.6000   -2.1300    3.8400    5.0700    7.0400    6.6300    5.8200   -0.2800    0.4100];
z=[0    1.5500    2.1500    1.8500   -4.3100    3.1000   -5.4900   -5.9700   -4.0800   -4.0800];
s=[x; y; z];                            % sensor positions

M = size(s,2);                          % Number of sensors.
N = size(s,1);                          % Dimension of localization.

R = (eye(M-1)+ones(M-1))/2;             % covariance structure of TDOA
NsePwrVecdB=-70:10:20; 
dbr=80;                                 % soruce range
fprintf('Simulation in progress');
randn('state',0);
r_rd=randn(M-1,L);
m_rd=mean(r_rd,2);
n_rd=r_rd-m_rd*ones(1,L);               % ensure zero-mean noise
r=dbr;
uo_p=[thetao phio 1/r]';                % true source location in MPR
%uo=[0 0 0]';
[uo(1,1) uo(2,1) uo(3,1)]=sph2cart(thetao,phio,r);
ro = sqrt(sum((uo*ones(1,M)-s).^2))';   % true source-sensor ranges
rdo = ro(2:end)-ro(1);                  % true range difference

for nseIdx=1:length(NsePwrVecdB),       % vary measurement noise level
    fprintf('.');
    nsePwr = 10^(NsePwrVecdB(nseIdx)/10);
    Q = nsePwr * R;                     % Covariance matrix of TDOA (range difference) noise

    [CRLB] = TDOALocCRLB_MPR(s,uo,Q);
    cb_theta3(nseIdx)=CRLB(1,1);
    cb_phi3(nseIdx)=CRLB(2,2);
    cb_invr(nseIdx)=CRLB(3,3);
    cb_angles3(nseIdx)=CRLB(1,1)+CRLB(2,2);
    
    SimulationMSET_invr = 0;
    SimulationMSEMPMTS_angles=0;
    SimulationMSESDR_invr=0;
    SimulationMSESDR_angles=0;
    SimulationMSECC_invr = 0;
    SimulationMSECC_angles = 0;
    for k = 1 : L,                          % Monte Carlo Simulation.
        rdNse = sqrtm(Q) * randn(M-1,1);
        rd = rdo + sqrtm(Q)*n_rd(:,k);      % Noisy source TDOAs (range differences).
        upSDR=TDOA_SDRMPR_3D(s,rd,Q);           % SDR-MPR solution
        [upT] = TDOA_MLEMPR(s,rd,Q,upSDR);   % MLE-MPR solution
        SimulationMSEMPMTS_angles = SimulationMSEMPMTS_angles+norm([upT(1:2)]-[uo_p(1:2)])^2;
        SimulationMSET_invr = SimulationMSET_invr + (upT(3)-uo_p(3))^2;
        SimulationMSESDR_angles = SimulationMSESDR_angles+norm([upSDR(1:2)]-[uo_p(1:2)])^2;     
        SimulationMSESDR_invr = SimulationMSESDR_invr+(upSDR(3)-uo_p(3))^2;
    end;
    mseT_invr(nseIdx) = SimulationMSET_invr/L;
    mseMPMTS_angles(nseIdx) = SimulationMSEMPMTS_angles/L;
    mseSDR_invr(nseIdx) = SimulationMSESDR_invr/L;
    mseSDR_angles(nseIdx) = SimulationMSESDR_angles/L;
end;

fprintf('\n');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure; 
subplot(2,1,1);
plot(NsePwrVecdB,10*log10(cb_invr),'k--'); grid on; hold on;
plot(NsePwrVecdB,10*log10(mseSDR_invr),'^k','MarkerSize',8); hold on;
plot(NsePwrVecdB,10*log10(mseT_invr),'xk','MarkerSize',8); hold on;
hold off; grid on;
ylim([-100 0]);
xlabel('10 log(\sigma_n^2)'); 
ylabel('10 log(MSE(1/r))');
legend('CRLB','SDR-MPR','MLE-MPR','Location','southeast')
subplot(2,1,2)
plot(NsePwrVecdB,10*log10(cb_angles3),'k--'); grid on; hold on;
plot(NsePwrVecdB,10*log10(mseSDR_angles),'^k','MarkerSize',8); hold on;
plot(NsePwrVecdB,10*log10(mseMPMTS_angles),'xk','MarkerSize',8); hold on;
hold off; grid on;
ylim([-100 20]);
xlabel('10 log(\sigma_n^2)'); 
ylabel('10 log(MSE([\theta,\phi](rad)))');
% legend('CRLB','MLE-Cartesian','SDR-MPR','MLE-MPR','Location','southeast')
legend('CRLB','SDR-MPR','MLE-MPR','Location','southeast')


