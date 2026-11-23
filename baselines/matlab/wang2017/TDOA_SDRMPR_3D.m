function [up] = TDOA_CVXMPR_3D(s,rd,Q)
%
% up = TDOA_CVXMPR_3D(s,rd,Q)
%
% s:  (Dim x M) matrix, each column is a sensor position and 
%     first column is for the reference sensor,
%     M is the number of sensors and should be at least Dim+2,
%     the sensors should not lie in a plane or a line
% rd: (M-1)x1, range difference measurement (TDOA x SignalPropagationSpeed)
% Q:  (M-1)x(M-1) covariance matrix of the TDOA (range difference) vector
% up: CVX solution in MPR
%
% Reference: Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range," IEEE 
%  Trans. Signal Process., vol. 65, no. 6, pp. 1447-1460, Mar. 2017.
%
% Note: additional constraints other than (37) in the reference paper are imposed 
% when the number of sensors is less to ensble a reasonable solution from CVX.
%
% Yue Wang, K. C. Ho    05-18-2017
%
%       Copyright (C) 2017
%       Computational Intelligence Signal Processing Laboratory
%       University of Missouri
%       Columbia, MO 65211, USA.
%       hod@missouri.edu
%

M = length(rd) + 1;     % number of sensors
W1 = inv(Q/Q(1,1));
n1=9;                   % number of parameters in the solution

h1 = rd;
for i=2:M
    sd(:,i-1)=s(:,i)-s(:,1);
    [alpha(i-1), beta(i-1) R(i-1)]=cart2sph(sd(1,i-1),sd(2,i-1),sd(3,i-1));
end
for i=1:M-1
    G1(i,:) = [-R(i)*cos(alpha(i))*cos(beta(i)) -R(i)*sin(alpha(i))*cos(beta(i)) -R(i)*sin(beta(i)) 0.5*R(i)^2*(1-cos(alpha(i))^2*cos(beta(i))^2)...
        0.5*R(i)^2*(1-sin(alpha(i))^2*cos(beta(i))^2) 0.5*R(i)^2*cos(beta(i))^2 -R(i)^2*sin(alpha(i))*cos(alpha(i))*cos(beta(i))*cos(beta(i))...
        -R(i)^2*cos(alpha(i))*sin(beta(i))*cos(beta(i)) -R(i)^2*sin(alpha(i))*sin(beta(i))*cos(beta(i))];
end

M1=zeros(9,9); M1(1,1)=1; M1(2,2)=1; M1(3,3)=1;
M2=zeros(9,9); M2(1,9)=1; M2(9,1)=1; M2(2,8)=-1; M2(8,2)=-1;
M3=zeros(9,9); M3(1,9)=1; M3(9,1)=1; M3(3,7)=-1; M3(7,3)=-1;
M5=zeros(9,9); M5(1,6)=1; M5(6,1)=1; M5(3,8)=-1; M5(8,3)=-1;
M6=zeros(9,9); M6(2,6)=1; M6(6,2)=1; M6(3,9)=-1; M6(9,3)=-1;
M4=zeros(9,9); M4(4,5)=0.5; M4(5,4)=0.5; M4(7,7)=-1;

% -- additional constraints are needed if we have less sensors --
if (M<10)
%%%%%% additional new constraints %%%%%
M7=zeros(9,9); M7(1,7)=1; M7(7,1)=1; M7(2,4)=-1; M7(4,2)=-1;
M8=zeros(9,9); M8(1,8)=1; M8(8,1)=1; M8(3,4)=-1; M8(4,3)=-1;
M9=zeros(9,9); M9(2,7)=1; M9(7,2)=1; M9(1,5)=-1; M9(5,1)=-1;
M10=zeros(9,9); M10(2,9)=1; M10(9,2)=1; M10(3,5)=-1; M10(5,3)=-1;
M11=zeros(9,9); M11(7,8)=1; M11(8,7)=1; M11(4,9)=-1; M11(9,4)=-1;
M12=zeros(9,9); M12(7,9)=1; M12(9,7)=1; M12(5,8)=-1; M12(8,5)=-1;
M13=zeros(9,9); M13(8,9)=1; M13(9,8)=1; M13(6,7)=-1; M13(7,6)=-1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
end;

if (M<10)
    % -- additional constraints are needed if we have less sensors --
    cvx_begin quiet;
    variables s1 s2 s3
    variable V1(9,9) symmetric
    minimize(trace(G1'*W1*G1*V1)-2*pow_p(trace(G1'*W1*h1*h1'*W1*G1*V1),0.5))
    subject to
    
    1-trace(M1*V1)==0
    -trace(M2*V1)==0
    -trace(M3*V1)==0
    -trace(M4*V1)==0
    -trace(M5*V1)==0
    -trace(M6*V1)==0
    -trace(M7*V1)==0
    -trace(M8*V1)==0
    -trace(M9*V1)==0
    -trace(M10*V1)==0
    -trace(M11*V1)==0
    -trace(M12*V1)==0
    -trace(M13*V1)==0
    
    V1==semidefinite(n1);
    cvx_end;
else
    cvx_begin quiet;
    variables s1 s2 s3
    variable V1(9,9) symmetric
    minimize(trace(G1'*W1*G1*V1)-2*pow_p(trace(G1'*W1*h1*h1'*W1*G1*V1),0.5))
    subject to
    
    1-trace(M1*V1)==0
    -trace(M2*V1)==0
    -trace(M3*V1)==0
    -trace(M4*V1)==0
    -trace(M5*V1)==0
    -trace(M6*V1)==0
    
    V1==semidefinite(n1);
    cvx_end;
end;

[V,D]=eig(V1);
[d,IX]=sort(sum(D));
u1=V(:,IX(end))/sqrt(d(end));

% -- take care of sign ambiguity --
up1=[atan2(u1(2),u1(1)); atan2(u1(3),norm(u1(1:2))); sum(u1(4:6))];
u2=-u1;
up2=[atan2(u2(2),u2(1)); atan2(u2(3),norm(u2(1:2))); sum(u1(4:6))];

rd1=G1*u1;
rd2=G1*u2;
e1=norm(rd1-rd,2);
e2=norm(rd2-rd,2);
if e1<e2
    up=up1;
else
    up=up2;
end

up(end)=abs(up(end));   % inverse range must be positive
