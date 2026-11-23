function [CRLB] = TDOALocCRLB_MPR(SensorPositions,SourceLocation,Q)
%
% CRLB = TDOALocCRLB_MPR(SensorPositions,SourceLocation,Q)
%
% SensorPositons: (Dim x M) matrix, each column is a sensor position and 
%                 first column is the reference sensor
%                 M is the number of sensors and should be at least Dim+2
%                 the sensors should not lie in one plane or line
% SourceLocation: (Dim x 1) vector of the estimated source location
% Q:              the covariance matrix of the TDOA (range difference) vector
% CRLB:           (Dim x Dim) CRLB matrix of the estimated source localization
%
% The program can be used for 2D(Dim=2) or 3D(Dim=3) localization
%
%   
% Reference: Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range," IEEE 
%  Trans. Signal Process., vol. 65, no. 6, pp. 1447-1460, Mar. 2017.
%
% The generated figure from this code corresponds to Fig. 3 in the reference.  
%
% Yue Wang, K. C. Ho    05-18-2017
%
%       Copyright (C) 2017
%       Computational Intelligence Signal Processing Laboratory
%       University of Missouri
%       Columbia, MO 65211, USA.
%       hod@missouri.edu
%

M = length(Q) + 1;

if (M<size(SensorPositions,1)+2)
    fprintf('Number of sensors must be at least %d\n',size(SensorPositions,1)+2);
    return;
end;

if (rank(SensorPositions) < size(SensorPositions,1))
    disp('The sensors should not lie in one plane or line!');
    return;
end

S = SensorPositions;
uo = SourceLocation;

M = size(SensorPositions,2);
ro = sqrt(sum((uo*ones(1,M)-S).^2));

d_u = (S(:,2:end)-uo*ones(1,M-1))'./(ro(2:end)'*ones(1,size(S,1))) ...
    -ones(M-1,1)*((S(:,1)-uo)'/ro(1));

J = d_u'*inv(Q)*d_u;    % FIM
CRLB_cart = inv(J);

% -- CRLB of angles and (1/r) --
if (length(SourceLocation)==2)  % 2-D case
    ro=norm(uo);
    thetao=angle(uo(1)+sqrt(-1)*uo(2));
    cThetao=cos(thetao); sThetao=sin(thetao);
    X=[ ro*sThetao, -ro*cThetao;
        cThetao, sThetao]/(-ro^2);
else          % 3-D case
    ro=norm(uo);
    thetao=angle(uo(1)+sqrt(-1)*uo(2));
    phio=angle(norm(uo(1:2))+sqrt(-1)*uo(3));
    cThetao=cos(thetao); sThetao=sin(thetao); cPhio=cos(phio); sPhio=sin(phio);
    X=[ ro*sThetao, -ro*cThetao, 0;
        ro*cThetao*sPhio*cPhio, ro*sThetao*sPhio*cPhio, -ro*cPhio*cPhio;
        cThetao*cPhio*cPhio, sThetao*cPhio*cPhio, sPhio*cPhio]/(-ro*ro*cPhio);
end;

CRLB=X*CRLB_cart*X';
