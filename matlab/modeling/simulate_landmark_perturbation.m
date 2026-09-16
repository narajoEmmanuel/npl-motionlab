function results = simulate_landmark_perturbation(proximal,joint,distal,magnitudesPx)
%SIMULATE_LANDMARK_PERTURBATION Deterministic one-landmark perturbations.
    if nargin<4 || isempty(magnitudesPx), magnitudesPx=[1,2,3,5]; end
    magnitudesPx=double(magnitudesPx(:));
    if any(~isfinite(magnitudesPx)) || any(magnitudesPx<=0), error('MotionLab:InvalidPerturbationMagnitude','Magnitudes must be positive finite values.'); end
    points=[reshape(double(proximal),1,2);reshape(double(joint),1,2);reshape(double(distal),1,2)]; baseline=compute_angle_2d(points(1,:),points(2,:),points(3,:));
    landmarks=["proximal","joint","distal"]; modes=["x_only","y_only","xy_equal"];
    caseId=strings(0,1); landmark=strings(0,1); mode=strings(0,1); magnitude=zeros(0,1); dx=zeros(0,1); dy=zeros(0,1); displacement=zeros(0,1); angle=zeros(0,1); signedDifference=zeros(0,1); absoluteDifference=zeros(0,1); counter=0;
    for li=1:3
        for mi=1:numel(magnitudesPx)
            m=magnitudesPx(mi);
            for oi=1:numel(modes)
                currentMode=modes(oi);
                if currentMode=="x_only", deltas=[m,0;-m,0]; elseif currentMode=="y_only", deltas=[0,m;0,-m]; else, deltas=[m,m;m,-m;-m,m;-m,-m]; end
                for di=1:size(deltas,1)
                    counter=counter+1; perturbed=points; perturbed(li,:)=perturbed(li,:)+deltas(di,:); perturbedAngle=compute_angle_2d(perturbed(1,:),perturbed(2,:),perturbed(3,:)); difference=perturbedAngle-baseline;
                    caseId(counter,1)=sprintf('%s_%s_%gpx_%d',char(landmarks(li)),char(currentMode),m,di); landmark(counter,1)=landmarks(li); mode(counter,1)=currentMode; magnitude(counter,1)=m; dx(counter,1)=deltas(di,1); dy(counter,1)=deltas(di,2); displacement(counter,1)=hypot(dx(counter,1),dy(counter,1)); angle(counter,1)=perturbedAngle; signedDifference(counter,1)=difference; absoluteDifference(counter,1)=abs(difference);
                end
            end
        end
    end
    baselineColumn=repmat(baseline,counter,1);
    results=table(caseId,landmark,mode,magnitude,dx,dy,displacement,baselineColumn,angle,signedDifference,absoluteDifference,'VariableNames',{'CaseId','Landmark','Mode','MagnitudePx','DeltaXPx','DeltaYPx','DisplacementPx','BaselineAngleDeg','PerturbedAngleDeg','SignedAngularDifferenceDeg','AbsoluteAngularDifferenceDeg'});
end
