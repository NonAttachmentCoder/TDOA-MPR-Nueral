function [state, position, err, warn] = chan_ho_estimate(stations, y, Qr)
% Absolute station columns in m, y = r(2:end)-r(1) in m, dense Qr in m^2.
% Keep the native global Cartesian position. Score angles (rad) and inverse
% range (1/m) relative to station 1, as for the DeviceIoT output columns.
state = nan(3,1);
position = nan(3,1);
err = '';
warn = '';
lastwarn('', '');
try
    p = TDOALoc(stations, y, Qr);
    if ~isequal(size(p), [3,1])
        error('ChanHo:OutputShape', 'The estimator returned a %s position.', mat2str(size(p)));
    end
    position = p;
    if ~isreal(p) || any(~isfinite(p))
        error('ChanHo:InvalidPosition', 'The native position is complex or nonfinite.');
    end
    d = p - stations(:,1);
    r = norm(d);
    if r == 0
        error('ChanHo:AtReference', 'The estimated direction and inverse range are undefined.');
    end
    state = [atan2(d(2),d(1)); atan2(d(3),hypot(d(1),d(2))); 1/r];
catch exception
    err = [exception.identifier ' ' exception.message];
end
[message, id] = lastwarn;
if ~isempty(message), warn = [id ' ' message]; end
end
