function result = analyze_m4d_digitization(dataDir,outputDir)
%ANALYZE_M4D_DIGITIZATION Reproduce the existing nested M4-D analysis read-only.
    if nargin<2 || strlength(string(outputDir))==0, outputDir=fullfile(fileparts(fileparts(mfilename('fullpath'))),'results'); end
    if ~isfolder(outputDir), mkdir(outputDir); end
    dataDir=char(dataDir); manifestPath=fullfile(dataDir,'m4d01_manifest.json'); if ~isfile(manifestPath), error('MotionLab:M4DManifestMissing','Missing M4-D manifest.'); end
    manifest=jsondecode(fileread(manifestPath)); captures=manifest.captures; if numel(captures)~=7, error('MotionLab:M4DUnexpectedRecordingCount','Expected exactly seven retained recordings.'); end
    captureId=strings(7,1); meanAngle=zeros(7,1); signedDifference=zeros(7,1); withinSd=zeros(7,1); rangeDeg=zeros(7,1); meanAbsDifference=zeros(7,1); meanBx=zeros(7,1); meanBy=zeros(7,1); nDigitizations=zeros(7,1); imageWidthPx=zeros(7,1); imageHeightPx=zeros(7,1); allResiduals=[]; operatorIds=strings(0,1); procedures=strings(0,1); displaySettings=strings(0,1);
    for ci=1:7
        id=string(captures(ci).capture_id); captureId(ci)=id; expectedChecksum=string(captures(ci).frame_sha256); files=dir(fullfile(dataDir,char(id+"_digitization_*.json"))); [~,order]=sort({files.name}); files=files(order); if numel(files)~=4, error('MotionLab:M4DUnexpectedDigitizationCount','Expected four digitizations for %s.',id); end
        angles=zeros(4,1); bx=zeros(4,1); by=zeros(4,1); imageWidth=NaN; imageHeight=NaN;
        for ri=1:4
            record=jsondecode(fileread(fullfile(files(ri).folder,files(ri).name))); if string(record.capture_id)~=id, error('MotionLab:M4DCaptureIdMismatch','Capture ID mismatch.'); end; if string(record.frame_sha256)~=expectedChecksum, error('MotionLab:M4DChecksumReferenceMismatch','Checksum reference mismatch.'); end
            clickOrder=string(record.click_order(:)); if numel(clickOrder)~=3 || any(clickOrder~=["A";"B";"C"]), error('MotionLab:M4DClickOrderMismatch','Unexpected click order.'); end; if double(record.nominal_reference_deg)~=90, error('MotionLab:M4DNominalAngleMismatch','Unexpected nominal angle.'); end
            p=[double(record.points_px.A.x),double(record.points_px.A.y)]; j=[double(record.points_px.B.x),double(record.points_px.B.y)]; d=[double(record.points_px.C.x),double(record.points_px.C.y)]; angles(ri)=compute_angle_2d(p,j,d); bx(ri)=j(1); by(ri)=j(2);
            if isfield(record,'angle_ABC_deg') && ~isempty(record.angle_ABC_deg) && abs(angles(ri)-double(record.angle_ABC_deg))>1e-12, error('MotionLab:M4DSavedAngleMismatch','Saved angle mismatch.'); end
            imageWidth=double(record.image_width_px); imageHeight=double(record.image_height_px); operatorIds(end+1,1)=string(record.operator_id); procedures(end+1,1)=string(record.procedure); displaySettings(end+1,1)=string(record.display_width_px)+"@"+string(record.scale); %#ok<AGROW>
        end
        currentMean=mean(angles); nDigitizations(ci)=4; meanAngle(ci)=currentMean; signedDifference(ci)=currentMean-90; withinSd(ci)=std(angles,0); rangeDeg(ci)=max(angles)-min(angles); meanAbsDifference(ci)=mean(abs(angles-90)); meanBx(ci)=mean(bx); meanBy(ci)=mean(by); imageWidthPx(ci)=imageWidth; imageHeightPx(ci)=imageHeight; allResiduals=[allResiduals;angles-currentMean]; %#ok<AGROW>
        if ~isfinite(imageWidth)||~isfinite(imageHeight)||imageWidth<=0||imageHeight<=0, error('MotionLab:M4DInvalidImageDimensions','Invalid image dimensions.'); end
    end
    if numel(unique(operatorIds))~=1 || numel(unique(procedures))~=1 || numel(unique(displaySettings))~=1, error('MotionLab:M4DProcedureChanged','Operator, procedure, or display setting changed.'); end
    meanBNormalizedX=meanBx./imageWidthPx; meanBNormalizedY=meanBy./imageHeightPx;
    perCapture=table(captureId,nDigitizations,meanAngle,signedDifference,withinSd,rangeDeg,meanAbsDifference,meanBx,meanBy,meanBNormalizedX,meanBNormalizedY,'VariableNames',{'CaptureId','NDigitizations','MeanAngleDeg','MeanSignedDifferenceDeg','WithinFrameSampleSDDeg','RangeDeg','MeanAbsoluteDifferenceDeg','MeanBPxX','MeanBPxY','MeanBNormalizedX','MeanBNormalizedY'});
    centerMask=startsWith(captureId,"m4d01_C_") & ~contains(captureId,"return"); rightMask=startsWith(captureId,"m4d01_R_"); returnMask=captureId=="m4d01_C_return_01"; if sum(centerMask)~=3 || sum(rightMask)~=3 || sum(returnMask)~=1, error('MotionLab:M4DConditionStructureMismatch','Expected 3 Center, 3 Right, 1 return.'); end
    centerMeans=meanAngle(centerMask); rightMeans=meanAngle(rightMask); condition=["Center";"Right"]; nRecordings=[3;3]; meanOfRecordingMeansDeg=[mean(centerMeans);mean(rightMeans)]; meanSignedDifferenceDeg=meanOfRecordingMeansDeg-90; betweenRecordingSampleSDDeg=[std(centerMeans,0);std(rightMeans,0)]; rangeOfRecordingMeansDeg=[max(centerMeans)-min(centerMeans);max(rightMeans)-min(rightMeans)]; meanWithinFrameSampleSDDeg=[mean(withinSd(centerMask));mean(withinSd(rightMask))]; achievedMeanBPxX=[mean(meanBx(centerMask));mean(meanBx(rightMask))]; achievedMeanBPxY=[mean(meanBy(centerMask));mean(meanBy(rightMask))]; achievedMeanBNormalizedX=[mean(meanBNormalizedX(centerMask));mean(meanBNormalizedX(rightMask))]; achievedMeanBNormalizedY=[mean(meanBNormalizedY(centerMask));mean(meanBNormalizedY(rightMask))];
    conditionSummary=table(condition,nRecordings,meanOfRecordingMeansDeg,meanSignedDifferenceDeg,betweenRecordingSampleSDDeg,rangeOfRecordingMeansDeg,meanWithinFrameSampleSDDeg,achievedMeanBPxX,achievedMeanBPxY,achievedMeanBNormalizedX,achievedMeanBNormalizedY);
    pooledWithinFrameSampleSDDeg=sqrt(sum(allResiduals.^2)/(numel(allResiduals)-7)); rightMinusCenterMeanDeg=mean(rightMeans)-mean(centerMeans); returnMinusInitialCenterMeanDeg=meanAngle(returnMask)-mean(centerMeans);
    result=struct('per_capture',perCapture,'condition_summary',conditionSummary,'right_minus_center_mean_deg',rightMinusCenterMeanDeg,'return_minus_initial_center_mean_deg',returnMinusInitialCenterMeanDeg,'pooled_within_frame_sample_sd_deg',pooledWithinFrameSampleSDDeg,'return_capture',perCapture(returnMask,:));
    writetable(perCapture,fullfile(outputDir,'m4d_per_capture.csv'));
    writetable(conditionSummary,fullfile(outputDir,'m4d_condition_summary.csv'));
    fid=fopen(fullfile(outputDir,'m4d_summary.txt'),'w');
    cleaner=onCleanup(@() fclose(fid)); %#ok<NASGU>
    fprintf(fid,'M4-D MATLAB descriptive analysis\nRight minus Center mean: %.12f deg\nReturn minus initial Center mean: %.12f deg\nPooled within-frame sample SD: %.12f deg\n',rightMinusCenterMeanDeg,returnMinusInitialCenterMeanDeg,pooledWithinFrameSampleSDDeg);
    plot_m4d_results(result,outputDir);
end
