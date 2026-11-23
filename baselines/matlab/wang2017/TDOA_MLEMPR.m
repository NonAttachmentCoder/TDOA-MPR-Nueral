function [uTilde] = TDOA_MLEMPR(s,rd,Q,uTildeInit)
%
% uTilde = TDOA_MLEMPR(s,rd,Q,uTildeInit)
%
% s:   (Dim x M) matrix, each column is a sensor position and
%      first column is for the reference sensor,
%      M is the number of sensors and should be at least Dim+2
%      the sensors should not lie in a plane or a line
% rd:  (M-1)x1, range difference measurement (TDOA x SignalPropagationSpeed)
% Q:   (M-1)x(M-1) covariance matrix of the TDOA (range difference) vector
% uTildeInit:   initial solution guest to start the iteration
% uTilde:       solution in MPR
%
% The routine uses the Gauss-Newton iteration to obtain the solution in MPR, 2-D or 3-D
%
% Reference: Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range," IEEE
%  Trans. Signal Process., vol. 65, no. 6, pp. 1447-1460, Mar. 2017.
%
% Yue Wang, K. C. Ho    11-28-2018
%       Modifed to work for 2-D and 3-D 
% Yue Wang, K. C. Ho    05-18-2017
%
%       Copyright (C) 2017
%       Computational Intelligence Signal Processing Laboratory
%       University of Missouri
%       Columbia, MO 65211, USA.
%       hod@missouri.edu
%

[Dim,M]=size(s);	% Dim=dimension, M=NumSensors
iterN=20;       % maximum number of iterations

W=inv(Q/Q(1,1));
uTilde=uTildeInit;
du=ones(size(uTilde));
SmallValue=1e-10;   % small value to stop iteration

l=0;
while (norm(du)>SmallValue & l<iterN)
    l=l+1;
    switch Dim,
        case 2,
            invrg=uTildeInit(1);
            thetag=uTildeInit(2);
            for i=1:M
                a0(i,:)=[cos(thetag)-s(1,i)*invrg sin(thetag)-s(2,i)*invrg];
                a(i,:)=a0(i,:)/norm(a0(i,:),2);
            end
            P=-[cos(thetag)*invrg sin(thetag)*invrg;sin(thetag) -cos(thetag)];
        case 3,
            thetag=uTilde(1);
            phig=uTilde(2);
            invrg=uTilde(3);
            
            for i=1:M,
                a0(i,:)=[cos(thetag)*cos(phig)-s(1,i)*invrg   sin(thetag)*cos(phig)-s(2,i)*invrg   sin(phig)-s(3,i)*invrg];
                a(i,:)=a0(i,:)/norm(a0(i,:),2);
            end
            P=-(1/cos(phig))*[ ...
                sin(thetag) -cos(thetag) 0;
                cos(thetag)*sin(phig)*cos(phig) sin(thetag)*sin(phig)*cos(phig) -cos(phig)^2;
                invrg*cos(thetag)*cos(phig)^2 invrg*sin(thetag)*cos(phig)^2 invrg*sin(phig)*cos(phig) ...
                ];
            
    end;
    
    
    for i=2:M,
        G(i-1,:)=a(i,:)-a(1,:);
    end
    
    n_a0=sqrt(sum(a0(2:end,:).^2,2));
    h=rd*(invrg)-(n_a0-1);
    
    du=P*inv(G'*W*G)*G'*W*h;
    uTilde=uTilde+du;
end


