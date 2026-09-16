function result = measurement_model(proximal,joint,distal,coordinateDomain,imageSize)
%MEASUREMENT_MODEL Evaluate the deterministic MotionLab angle model.
%   Pixel inputs are used directly. Normalized inputs are converted with
%   [width_px,height_px] before Euclidean geometry.
    if nargin<4 || isempty(coordinateDomain), coordinateDomain='pixel'; end
    if nargin<5, imageSize=[]; end
    domain=lower(string(coordinateDomain));
    inputPoints=[reshape(double(proximal),1,[]);reshape(double(joint),1,[]);reshape(double(distal),1,[])];
    if size(inputPoints,2)~=2, error('MotionLab:InvalidPoint','Each landmark must contain exactly two coordinates.'); end
    switch domain
        case "pixel", pixelPoints=inputPoints;
        case "normalized"
            if isempty(imageSize), error('MotionLab:MissingImageSize','Normalized coordinates require [width_px,height_px].'); end
            pixelPoints=normalized_to_pixel(inputPoints,imageSize);
        otherwise, error('MotionLab:InvalidCoordinateDomain','coordinateDomain must be pixel or normalized.');
    end
    includedAngle=compute_angle_2d(pixelPoints(1,:),pixelPoints(2,:),pixelPoints(3,:));
    result=struct('coordinate_domain',char(domain),'pixel_points',pixelPoints,'included_angle_deg',includedAngle,'projected_flexion_angle_deg',180-includedAngle);
end
