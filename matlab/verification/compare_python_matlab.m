function results = compare_python_matlab(casesPath,pythonResultsPath,outputDir,toleranceDeg)
%COMPARE_PYTHON_MATLAB Compare independent implementations on identical inputs.
    if nargin<1 || strlength(string(casesPath))==0, root=fileparts(fileparts(mfilename('fullpath'))); casesPath=fullfile(root,'verification','crosscheck_cases.csv'); end
    if nargin<2 || strlength(string(pythonResultsPath))==0, root=fileparts(fileparts(mfilename('fullpath'))); pythonResultsPath=fullfile(root,'results','python_crosscheck_results.csv'); end
    if nargin<3 || strlength(string(outputDir))==0, root=fileparts(fileparts(mfilename('fullpath'))); outputDir=fullfile(root,'results'); end
    if nargin<4 || isempty(toleranceDeg), toleranceDeg=1e-10; end
    if ~isfolder(outputDir), mkdir(outputDir); end
    cases=readtable(casesPath,'TextType','string'); python=readtable(pythonResultsPath,'TextType','string');
    if height(cases)~=height(python) || any(cases.case_id~=python.case_id), error('MotionLab:CrosscheckInputMismatch','Python results do not match neutral case IDs/order.'); end
    matlabAngle=zeros(height(cases),1);
    for idx=1:height(cases), matlabAngle(idx)=compute_angle_2d([cases.proximal_x(idx),cases.proximal_y(idx)],[cases.joint_x(idx),cases.joint_y(idx)],[cases.distal_x(idx),cases.distal_y(idx)]); end
    pythonAngle=double(python.python_angle_deg); absoluteDifference=abs(matlabAngle-pythonAngle); pass=absoluteDifference<=toleranceDeg; status=repmat("FAIL",height(cases),1); status(pass)="PASS";
    results=table(cases.case_id,pythonAngle,matlabAngle,absoluteDifference,status,'VariableNames',{'CaseId','PythonAngleDeg','MatlabAngleDeg','AbsoluteDifferenceDeg','Status'}); writetable(results,fullfile(outputDir,'python_matlab_crosscheck.csv'));
    fid=fopen(fullfile(outputDir,'python_matlab_crosscheck_report.txt'),'w'); cleaner=onCleanup(@() fclose(fid)); %#ok<NASGU>
    fprintf(fid,'Python-MATLAB numerical cross-verification\nTolerance: %.3g deg\nCases: %d\nPassing: %d\nMaximum absolute difference: %.17g deg\nClaim boundary: implementation consistency only.\n',toleranceDeg,height(results),sum(pass),max(absoluteDifference));
    figure('Visible','off'); scatter(pythonAngle,matlabAngle,48,'filled'); hold on; limits=[min([pythonAngle;matlabAngle]),max([pythonAngle;matlabAngle])]; plot(limits,limits,'--'); xlabel('Python angle (deg)'); ylabel('MATLAB angle (deg)'); title('Python vs MATLAB angle implementation'); grid on; exportgraphics(gcf,fullfile(outputDir,'python_vs_matlab.png'),'Resolution',200); close(gcf);
    figure('Visible','off'); stem(1:height(results),absoluteDifference,'filled'); yline(toleranceDeg,'--','Tolerance'); xticks(1:height(results)); xticklabels(cases.case_id); xtickangle(35); ylabel('Absolute difference (deg)'); title('Cross-implementation absolute difference'); grid on; exportgraphics(gcf,fullfile(outputDir,'python_matlab_absolute_difference.png'),'Resolution',200); close(gcf);
    if ~all(pass), error('MotionLab:CrossVerificationFailed','At least one Python-MATLAB case exceeded tolerance.'); end
end
