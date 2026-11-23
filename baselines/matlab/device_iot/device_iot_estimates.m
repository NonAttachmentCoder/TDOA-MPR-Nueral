function [mpr, position, errors, warnings] = device_iot_estimates(stations, y, Qr, Qs)
% Columns of stations are absolute 3-D positions in m. Column 1 is the
% reference for y = r(2:end)-r(1) in m. Qr and station-major Qs are in m^2.
% Each output column is one unchanged DeviceIoT estimator, in SCO/SUM/GTRS
% order. Native MPR is [azimuth; elevation; signed inverse reference range]
% in rad, rad, 1/m. Native Cartesian position is relative to the global origin.
mpr = nan(3,3);
position = nan(3,3);
errors = cell(1,3);
warnings = cell(1,3);
for method = 1:3
    lastwarn('', '');
    try
        switch method
            case 1
                [state, p] = TDOA_SCO_MPR(stations, y, Qr, Qs);
            case 2
                [az, el, g, p] = TDOA_SUM_MPR(stations, y, Qr, Qs);
                state = [az; el; g];
            case 3
                [az, el, g, p] = TDOA_GTRS_MPR(stations, y, Qr, Qs);
                state = [az; el; g];
        end
        mpr(:,method) = state;
        position(:,method) = p;
    catch exception
        errors{method} = [exception.identifier ' ' exception.message];
    end
    [message, id] = lastwarn;
    if ~isempty(message)
        warnings{method} = [id ' ' message];
    end
end
end
