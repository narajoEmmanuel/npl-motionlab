function angleDeg = compute_angle_2d(proximal, joint, distal)
%COMPUTE_ANGLE_2D Unsigned included 2D angle at JOINT in degrees [0,180].
    p = validatePoint(proximal,'proximal'); j = validatePoint(joint,'joint'); d = validatePoint(distal,'distal');
    u = p-j; v = d-j; uNorm = hypot(u(1),u(2)); vNorm = hypot(v(1),v(2));
    if uNorm==0 || vNorm==0, error('MotionLab:ZeroLengthVector','Angle is undefined for a zero-length segment.'); end
    uHat=u./uNorm; vHat=v./vNorm; detuv=uHat(1)*vHat(2)-uHat(2)*vHat(1); dotuv=dot(uHat,vHat);
    angleDeg = atan2d(abs(detuv),dotuv);
end
function point = validatePoint(value,name)
    if ~isnumeric(value)||~isreal(value)||~isvector(value)||numel(value)~=2, error('MotionLab:InvalidPoint','%s must contain exactly two real numeric coordinates.',name); end
    point=double(reshape(value,1,2)); if any(~isfinite(point)), error('MotionLab:NonFinitePoint','%s must contain only finite coordinates.',name); end
end
