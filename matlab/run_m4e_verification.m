function outputs = run_m4e_verification(m4dDataDir)
%RUN_M4E_VERIFICATION Execute analytical, sensitivity, and crosscheck workflows.
    matlabRoot=fileparts(mfilename('fullpath')); addpath(fullfile(matlabRoot,'geometry')); addpath(fullfile(matlabRoot,'modeling')); addpath(fullfile(matlabRoot,'analysis')); addpath(fullfile(matlabRoot,'verification')); outputDir=fullfile(matlabRoot,'results'); if ~isfolder(outputDir), mkdir(outputDir); end
    outputs=struct(); outputs.analytical=verify_known_angles(outputDir); outputs.sensitivity=sensitivity_analysis(outputDir);
    casesPath=fullfile(matlabRoot,'verification','crosscheck_cases.csv'); pythonPath=fullfile(matlabRoot,'results','python_crosscheck_results.csv'); if ~isfile(pythonPath), error('MotionLab:PythonCrosscheckMissing','Run scripts/export_matlab_crosscheck.py first.'); end
    outputs.crosscheck=compare_python_matlab(casesPath,pythonPath,outputDir,1e-10);
    if nargin>=1 && strlength(string(m4dDataDir))>0, outputs.m4d=analyze_m4d_digitization(m4dDataDir,outputDir); end
    fprintf('M4-E workflow completed. Generated outputs: %s\n',outputDir);
end
