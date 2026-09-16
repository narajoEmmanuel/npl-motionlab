function plot_m4d_results(result,outputDir)
%PLOT_M4D_RESULTS Plot descriptive M4-D recording-level results.
    if nargin<2 || strlength(string(outputDir))==0, outputDir=fullfile(fileparts(fileparts(mfilename('fullpath'))),'results'); end
    if ~isfolder(outputDir), mkdir(outputDir); end
    perCapture=result.per_capture; ids=string(perCapture.CaptureId); centerMask=startsWith(ids,"m4d01_C_") & ~contains(ids,"return"); rightMask=startsWith(ids,"m4d01_R_"); returnMask=contains(ids,"return");
    figure('Visible','off'); hold on; scatter(ones(sum(centerMask),1),perCapture.MeanAngleDeg(centerMask),55,'filled','DisplayName','Center recording means'); scatter(2*ones(sum(rightMask),1),perCapture.MeanAngleDeg(rightMask),55,'filled','DisplayName','Right recording means'); scatter(3,perCapture.MeanAngleDeg(returnMask),70,'filled','DisplayName','Return diagnostic'); yline(90,'--','Nominal 90 deg'); xlim([.5,3.5]); xticks([1,2,3]); xticklabels({'Center','Right','Return'}); ylabel('Recording mean included angle (deg)'); title('M4-D descriptive recording-level results'); grid on; legend('Location','best'); exportgraphics(gcf,fullfile(outputDir,'m4d_recording_means.png'),'Resolution',200); close(gcf);
    figure('Visible','off'); bar(1:height(perCapture),perCapture.WithinFrameSampleSDDeg); xticks(1:height(perCapture)); xticklabels(ids); xtickangle(35); ylabel('Within-frame sample SD (deg)'); title('M4-D manual digitization variability'); grid on; exportgraphics(gcf,fullfile(outputDir,'m4d_digitization_variability.png'),'Resolution',200); close(gcf);
end
