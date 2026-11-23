function run_cisp_sweep(sweep, ensembles, output_file)
% Sun--Ho--Wan 2019 Example.m design with DeviceIoT and Cartesian Chan--Ho.
% sweep is 'noise' or 'range'. Set ensembles explicitly (1000/2000 in the
% original). Save the paired range differences in m and raw method outputs.
arguments
    sweep (1,:) char {mustBeMember(sweep, {'noise','range'})}
    ensembles (1,1) double {mustBeInteger,mustBeGreaterThan(ensembles,1)}
    output_file (1,:) char
end
if isfile(output_file)
    error('Sweep:Exists', 'Result already exists: %s', output_file);
end
root = fileparts(fileparts(mfilename('fullpath')));
old_path = path;
restore_path = onCleanup(@() path(old_path));
addpath(fullfile(root,'baselines','matlab','sun2019'), ...
        fullfile(root,'baselines','matlab','device_iot'), ...
        fullfile(root,'baselines','matlab','chan_ho1994'));
design = jsondecode(fileread(fullfile(root,'src','tdoa_mpr','sun2019_design.json')));
stations = design.stations_km.' * 1e3;   % absolute positions, m; reference in column 1
angles = design.angles_deg(:) * pi/180;
[direction_x,direction_y,direction_z] = sph2cart(angles(1), angles(2), 1);
direction = [direction_x; direction_y; direction_z];
range_m = design.(sweep).range_km(:).' * 1e3;
variance_db = design.(sweep).tdoa_variance_db(:).';
points = max(numel(range_m),numel(variance_db));
range_m = range_m + zeros(1,points);
variance_db = variance_db + zeros(1,points);
M = size(stations,2);
Qs = zeros(3*M);
method_names = {'SCO','SUM','GTRS','Chan-Ho'};

% Example.m resets the same stream at every grid point and subtracts the
% ensemble's mean differenced noise. Generate those same columns once.
old_rng = rng;
restore_rng = onCleanup(@() rng(old_rng));
rng('default');
rng_start = rng;
arrivals = zeros(M,ensembles);
arrival_sum = zeros(M,1);
for frame = 1:ensembles
    arrivals(:,frame) = randn(M,1);
    arrival_sum = arrival_sum + arrivals(:,frame);
end
mean_arrival = arrival_sum/ensembles/sqrt(2);
noise = (arrivals(2:end,:) - arrivals(1,:))/sqrt(2) - (mean_arrival(2:end) - mean_arrival(1));
Qr = zeros(M-1,M-1,points);
y = zeros(M-1,ensembles,points);
mpr = nan(3,numel(method_names),ensembles,points); % [az,el,g] x method x frame x point
position = nan(size(mpr));             % native Cartesian output in m
errors = cell(numel(method_names),ensembles,points);
warnings = cell(size(errors));
crlb = zeros(4,points);                % angle-coordinate trace, g, position, range
bias_2019 = zeros(3,2,points);         % angle magnitude, |g bias|, position magnitude

for k = 1:points
    p = direction * range_m(k);
    distances = sqrt(sum((p-stations).^2,1)).';
    variance = 10^(variance_db(k)/10);
    Q = variance * (ones(M-1)+eye(M-1))/2;
    Qr(:,:,k) = Q;
    y(:,:,k) = (distances(2:end)-distances(1)) + sqrt(variance)*noise;
    C = TDOALocCRLB_MPR(stations,p,Q);
    % d p / d [azimuth,elevation,g] in the reference-at-origin example.
    J = [-p(2), -cos(angles(1))*p(3), -distances(1)*p(1);
          p(1), -sin(angles(1))*p(3), -distances(1)*p(2);
             0,  distances(1)*cos(angles(2)), -distances(1)*p(3)];
    Cp = J*C*J.';
    crlb(:,k) = [C(1,1)+C(2,2); C(3,3); trace(Cp); direction.'*Cp*direction];
    b = [Bias_SUM_MPR(stations,p,Q), Bias_GTRS_MPR(stations,p,Q)];
    bias_2019(:,:,k) = [vecnorm(b(1:2,:)); abs(b(3,:)); vecnorm(J*b)];
    for frame = 1:ensembles
        [mpr(:,1:3,frame,k),position(:,1:3,frame,k),err,warn] = ...
            device_iot_estimates(stations,y(:,frame,k),Q,Qs);
        [mpr(:,4,frame,k),position(:,4,frame,k),err{4},warn{4}] = ...
            chan_ho_estimate(stations,y(:,frame,k),Q);
        errors(:,frame,k) = err.';
        warnings(:,frame,k) = warn.';
    end
end
folder = fileparts(output_file);
if ~isempty(folder) && ~isfolder(folder), mkdir(folder); end
matlab_release = version('-release');
official_ensembles = design.(sweep).ensembles;
device_iot_zip_sha256 = '070aeeafbe248fd1f61207929718f1670d7469b4664882e4dfb42b9a04d6f975';
chan_ho_zip_sha256 = '0f04fd45e5c0f844b45b577f738340e662a1278467f8936c8d596274d1fd4de8';
save(output_file,'sweep','ensembles','official_ensembles','method_names','rng_start', ...
    'matlab_release','device_iot_zip_sha256','chan_ho_zip_sha256','stations','angles','range_m','variance_db', ...
    'Qr','Qs','y','mpr','position','errors','warnings','crlb','bias_2019','-v7');
end
