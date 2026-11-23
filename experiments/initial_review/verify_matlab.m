function verify_matlab
% Small deterministic author-code audit. No original Monte Carlo script runs.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
data = load(fullfile(root,'runs','initial_review','matlab_inputs.mat'));
sun = fullfile(root,'baselines','matlab','sun2019');
wang = fullfile(root,'baselines','matlab','wang2017');
addpath(sun);
result.role = 'development_diagnostics_not_paper_reproduction';
result.matlab = version;
result.records = {};
for k=1:numel(data.g)
    s = squeeze(data.stations(k,:,:))';
    rd = data.y(k,:)'; u = data.u(k,:)'; g = data.g(k);
    for method = {'SUM','GTRS'}
        result.records{end+1} = call2019(method{1},s,rd,data.qr,u,g,data.names{k},false);
        if norm(s(:,1)) > 0
            result.records{end+1} = call2019(method{1},s,rd,data.qr,u,g,data.names{k},true);
        end
    end
end
% 32 Gaussian draws per fixed scene, same saved noise for both algorithms.
% Common draws across scenes; no sample recentering or failure deletion.
result.noisy_records = {};
for k = [1 2 5]
    s = squeeze(data.stations(k,:,:))';
    for n=1:size(data.noise,1)
        rd = data.y(k,:)'+data.noise(n,:)';
        for method = {'SUM','GTRS'}
            rec = call2019(method{1},s,rd,data.qr,data.u(k,:)',data.g(k),data.names{k},false);
            rec.draw = n;
            result.noisy_records{end+1} = rec;
        end
    end
end
s = squeeze(data.stations(1,:,:))';
u = data.u(1,:)'; g = data.g(1);
p = u/g;
cb = TDOALocCRLB_MPR(s,p,data.qr);
phi = atan2(u(3),norm(u(1:2)));
result.crlb2019.angle_covariance = cb;
result.crlb2019.spherical_direction_bound = cos(phi)^2*cb(1,1)+cb(2,2);
result.crlb2019.unweighted_angle_trace = cb(1,1)+cb(2,2);
result.crlb2019.inverse_range_variance = cb(3,3);
result.crlb2019.python_direction_relative_error = abs(result.crlb2019.spherical_direction_bound/data.expected_direction_bound-1);
result.crlb2019.python_g_relative_error = abs(cb(3,3)/data.expected_g_bound-1);
cs = Cov_SUM_MPR(s,p,data.qr);
cg = Cov_GTRS_MPR(s,p,data.qr);
result.theory_covariance.sum = cs;
result.theory_covariance.sum_symmetry_relative = norm(cs-cs','fro')/norm(cs,'fro');
result.theory_covariance.gtrs = cg;
result.theory_covariance.gtrs_symmetry_relative = norm(cg-cg','fro')/norm(cg,'fro');
result.theory_bias.sum = Bias_SUM_MPR(s,p,data.qr);
result.theory_bias.gtrs = Bias_GTRS_MPR(s,p,data.qr);

% One noiseless case with the author's seven-station geometry and angles.
sx = [0 0 0; .4664 -.8712 .6294; 1.2402 -.0798 .8116; ...
      .4437 .6323 -.7460; .5798 -.2362 .8268; 1.0502 -.5172 .2647; -.8156 1.0448 -.8049]'*1000;
az = 22.13*pi/180; el = 14.41*pi/180;
ux = [cos(az)*cos(el);sin(az)*cos(el);sin(el)]; gx = 1/15000;
dx = vecnorm(ux/gx-sx); yx = dx(2:end)'-dx(1);
qx = (eye(6)+ones(6))/2;
result.author2019_geometry = {call2019('SUM',sx,yx,qx,ux,gx,'author_example_noiseless',false), ...
                            call2019('GTRS',sx,yx,qx,ux,gx,'author_example_noiseless',false)};

% Keep the two identically named CRLB functions isolated by search path.
rmpath(sun); clear TDOALocCRLB_MPR;
addpath(wang);
result.cvx_path = which('cvx_begin');
result.cvx_solver = cvx_solver;
result.wang2017 = {};
for k = [1 2 5 8]
    s = squeeze(data.stations(k,:,:))';
    rd = data.y(k,:)'; u = data.u(k,:)'; g = data.g(k);
    rec.name = data.names{k};
    rec.initialization = 'original SDR at centered reported coordinates';
    lastwarn('');
    try
        ss = s-s(:,1);
        init = TDOA_SDRMPR_3D(ss,rd,data.qr);
        est = TDOA_MLEMPR(ss,rd,data.qr,init);
        rec.initial_mpr = init;
        rec.estimated_mpr = est;
        uu = [cos(est(1))*cos(est(2));sin(est(1))*cos(est(2));sin(est(2))];
        v = uu+est(3)*s(:,1); nn = norm(v);
        uu = v/nn; gg = est(3)/nn;
        rec.direction_chord = norm(uu-u);
        rec.g_error = gg-g;
        rec.forward_residual_norm_m = norm(forward(uu,gg,s)-rd);
        rec.finite_real = isreal(est)&&all(isfinite(est));
        rec.error = '';
    catch err
        rec.error = err.message; rec.finite_real = false;
    end
    [rec.last_warning,rec.last_warning_id] = lastwarn;
    result.wang2017{end+1} = rec;
    clear rec;
end
% Reproduce the original 2017 Fig. 3 geometry only, with one noiseless input.
sx = [0 -4.64 -4.94 -5.05 -.28 -5.44 -5.4 -5.97 -8.11 -3.46; ...
      0 6.60 -2.13 3.84 5.07 7.04 6.63 5.82 -.28 .41; ...
      0 1.55 2.15 1.85 -4.31 3.10 -5.49 -5.97 -4.08 -4.08];
ux = [-1;5;3]/norm([-1;5;3]); gx = 1/80;
dx = vecnorm(ux/gx-sx); yx = dx(2:end)'-dx(1);
qx = (eye(9)+ones(9))/2;
try
    init = TDOA_SDRMPR_3D(sx,yx,qx);
    est = TDOA_MLEMPR(sx,yx,qx,init);
    uu = [cos(est(1))*cos(est(2));sin(est(1))*cos(est(2));sin(est(2))];
    result.author2017_geometry.initial_mpr = init;
    result.author2017_geometry.estimated_mpr = est;
    result.author2017_geometry.direction_chord = norm(uu-ux);
    result.author2017_geometry.g_error = est(3)-gx;
    result.author2017_geometry.forward_residual_norm_m = norm(forward(uu,est(3),sx)-yx);
catch err
    result.author2017_geometry.error = err.message;
end
rmpath(wang);
file = fullfile(root,'experiments','initial_review','evidence','matlab_checks.json');
fid = fopen(file,'w'); fprintf(fid,'%s\n',jsonencode(result,'PrettyPrint',true)); fclose(fid);
disp(['Saved ',file]);
end

function rec = call2019(method,s,rd,Q,u,g,name,center)
rec.name=name; rec.method=method; rec.center_and_map_back=center;
lastwarn('');
try
    input_s=s;
    if center, input_s=s-s(:,1); end
    if strcmp(method,'SUM')
        [az,el,gg,pos] = TDOA_SUM_MPR(input_s,rd,Q);
    else
        [az,el,gg,pos] = TDOA_GTRS_MPR(input_s,rd,Q);
    end
    rec.native_mpr_real=real([az;el;gg]); rec.native_mpr_imag=imag([az;el;gg]);
    rec.native_cartesian_finite=all(isfinite(pos));
    rec.finite_real=isreal([az;el;gg])&&all(isfinite([az;el;gg]));
    rec.error='';
    if rec.finite_real
        uu=[cos(az)*cos(el);sin(az)*cos(el);sin(el)];
        if center
            v=uu+gg*s(:,1); nn=norm(v); uu=v/nn; gg=gg/nn;
        end
        rec.u=uu; rec.g=gg; rec.direction_chord=norm(uu-u);
        rec.angle_error_deg=acos(max(-1,min(1,uu'*u)))*180/pi;
        rec.g_error=gg-g;
        rec.forward_residual_norm_m=norm(forward(uu,gg,s)-rd);
    end
catch err
    rec.error=err.message; rec.finite_real=false;
end
[rec.last_warning,rec.last_warning_id]=lastwarn;
end

function y=forward(u,g,s)
% Rationalized identity, used only to audit returned source states.
v=u-g*s; a=vecnorm(v);
num=-2*(s(:,2:end)-s(:,1))'*u+g*(sum(s(:,2:end).^2,1)-sum(s(:,1).^2))';
y=num./(a(2:end)'+a(1));
end
