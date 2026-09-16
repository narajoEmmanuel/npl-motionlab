function results = verify_known_angles(outputDir)
%VERIFY_KNOWN_ANGLES Independently verify analytically known 2D geometries.
    if nargin < 1, outputDir = ''; end
    knownAngles = [0;30;45;60;90;120;150;180]; toleranceDeg = 1e-10;
    proximal=[100,0]; joint=[0,0]; calculated=zeros(size(knownAngles)); absoluteError=zeros(size(knownAngles)); pass=false(size(knownAngles));
    for idx=1:numel(knownAngles)
        theta=knownAngles(idx); distal=100.*[cosd(theta),sind(theta)];
        calculated(idx)=compute_angle_2d(proximal,joint,distal); absoluteError(idx)=abs(calculated(idx)-theta); pass(idx)=absoluteError(idx)<=toleranceDeg;
    end
    status=repmat("FAIL",size(knownAngles)); status(pass)="PASS";
    results=table(knownAngles,calculated,absoluteError,status,'VariableNames',{'KnownAngleDeg','MatlabAngleDeg','AbsoluteErrorDeg','Status'}); disp(results);
    if ~all(pass), error('MotionLab:AnalyticalVerificationFailed','At least one known-angle MATLAB verification case failed.'); end
    if strlength(string(outputDir))>0
        if ~isfolder(outputDir), mkdir(outputDir); end
        writetable(results,fullfile(outputDir,'known_angle_verification.csv'));
    end
end
