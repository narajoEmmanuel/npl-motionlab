function pixelPoints = normalized_to_pixel(normalizedPoints, imageSize)
%NORMALIZED_TO_PIXEL Convert normalized [x,y] image coordinates to pixels.
%   Values outside [0,1] are retained. No clipping or rounding is performed.
    if ~isnumeric(normalizedPoints) || ~isreal(normalizedPoints) || ndims(normalizedPoints) ~= 2 || size(normalizedPoints,2) ~= 2
        error('MotionLab:InvalidNormalizedCoordinates','normalizedPoints must be a real numeric N-by-2 array.');
    end
    if any(~isfinite(normalizedPoints),'all')
        error('MotionLab:NonFiniteNormalizedCoordinates','normalizedPoints must contain only finite values.');
    end
    if ~isnumeric(imageSize) || ~isreal(imageSize) || ~isvector(imageSize) || numel(imageSize) ~= 2
        error('MotionLab:InvalidImageSize','imageSize must be [width_px, height_px].');
    end
    imageSize = double(reshape(imageSize,1,2));
    if any(~isfinite(imageSize)) || any(imageSize <= 0)
        error('MotionLab:InvalidImageSize','Image width and height must be positive finite values.');
    end
    pixelPoints = double(normalizedPoints) .* imageSize;
end
