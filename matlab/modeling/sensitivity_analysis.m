function outputs = sensitivity_analysis(outputDir)
%SENSITIVITY_ANALYSIS Quantify deterministic pixel-perturbation sensitivity.
    if nargin<1 || strlength(string(outputDir))==0, outputDir=fullfile(fileparts(fileparts(mfilename('fullpath'))),'results'); end
    if ~isfolder(outputDir), mkdir(outputDir); end
    baselineAngles=[30,60,90,120,150]; magnitudesPx=[1,2,3,5]; segmentLengthPx=100; joint=[500,500]; proximal=joint+[segmentLengthPx,0]; allRows=table();
    for theta=baselineAngles
        distal=joint+segmentLengthPx.*[cosd(theta),sind(theta)]; current=simulate_landmark_perturbation(proximal,joint,distal,magnitudesPx); current.BaselineGeometryDeg=repmat(theta,height(current),1);
        if isempty(allRows), allRows=current; else, allRows=[allRows;current]; end %#ok<AGROW>
    end
    landmarks=["proximal","joint","distal"]; modes=["x_only","y_only","xy_equal"]; summaryRows=table();
    for theta=baselineAngles
        for landmark=landmarks
            for mode=modes
                for magnitude=magnitudesPx
                    mask=allRows.BaselineGeometryDeg==theta & allRows.Landmark==landmark & allRows.Mode==mode & allRows.MagnitudePx==magnitude; values=allRows.AbsoluteAngularDifferenceDeg(mask);
                    row=table(theta,landmark,mode,magnitude,mean(values),max(values),'VariableNames',{'BaselineGeometryDeg','Landmark','Mode','MagnitudePx','MeanAbsoluteAngularDifferenceDeg','MaxAbsoluteAngularDifferenceDeg'});
                    if isempty(summaryRows), summaryRows=row; else, summaryRows=[summaryRows;row]; end %#ok<AGROW>
                end
            end
        end
    end
    linearityRows=table();
    for theta=baselineAngles
        for landmark=landmarks
            for mode=modes
                mask=summaryRows.BaselineGeometryDeg==theta & summaryRows.Landmark==landmark & summaryRows.Mode==mode & summaryRows.MagnitudePx<=3; x=summaryRows.MagnitudePx(mask); y=summaryRows.MeanAbsoluteAngularDifferenceDeg(mask); coefficients=polyfit(x,y,1); fitted=polyval(coefficients,x); sse=sum((y-fitted).^2); sst=sum((y-mean(y)).^2); if sst==0, rSquared=1; else, rSquared=1-sse/sst; end
                row=table(theta,landmark,mode,coefficients(1),coefficients(2),rSquared,'VariableNames',{'BaselineGeometryDeg','Landmark','Mode','SlopeDegPerPx','InterceptDeg','RSquaredSmallPerturbations'}); if isempty(linearityRows), linearityRows=row; else, linearityRows=[linearityRows;row]; end %#ok<AGROW>
            end
        end
    end
    writetable(allRows,fullfile(outputDir,'landmark_perturbation_cases.csv')); writetable(summaryRows,fullfile(outputDir,'sensitivity_summary.csv')); writetable(linearityRows,fullfile(outputDir,'small_perturbation_linearity.csv'));
    plotCurves(summaryRows,90,'x_only',outputDir,'sensitivity_90deg_x_only.png'); plotCurves(summaryRows,90,'y_only',outputDir,'sensitivity_90deg_y_only.png'); plotGeometry(summaryRows,outputDir);
    outputs=struct('cases',allRows,'summary',summaryRows,'linearity',linearityRows);
end
function plotCurves(summaryRows,baselineDeg,modeName,outputDir,fileName)
    figure('Visible','off'); hold on; landmarks=["proximal","joint","distal"];
    for landmark=landmarks, mask=summaryRows.BaselineGeometryDeg==baselineDeg & summaryRows.Mode==modeName & summaryRows.Landmark==landmark; subset=sortrows(summaryRows(mask,:),'MagnitudePx'); plot(subset.MagnitudePx,subset.MeanAbsoluteAngularDifferenceDeg,'-o','DisplayName',char(landmark),'LineWidth',1.2); end
    xlabel('Perturbation magnitude per axis (px)'); ylabel('Mean absolute angular difference (deg)'); title(sprintf('Deterministic sensitivity, %g deg baseline, %s',baselineDeg,strrep(modeName,'_',' '))); grid on; legend('Location','best'); exportgraphics(gcf,fullfile(outputDir,fileName),'Resolution',200); close(gcf);
end
function plotGeometry(summaryRows,outputDir)
    figure('Visible','off'); hold on; landmarks=["proximal","joint","distal"];
    for landmark=landmarks, x=unique(summaryRows.BaselineGeometryDeg); y=zeros(size(x)); for idx=1:numel(x), mask=summaryRows.BaselineGeometryDeg==x(idx) & summaryRows.Landmark==landmark & summaryRows.MagnitudePx==3; y(idx)=max(summaryRows.MaxAbsoluteAngularDifferenceDeg(mask)); end; plot(x,y,'-o','DisplayName',char(landmark),'LineWidth',1.2); end
    xlabel('Baseline included angle (deg)'); ylabel('Worst-case absolute angular difference at 3 px (deg)'); title('Sensitivity dependence on initial geometry'); grid on; legend('Location','best'); exportgraphics(gcf,fullfile(outputDir,'sensitivity_by_geometry.png'),'Resolution',200); close(gcf);
end
