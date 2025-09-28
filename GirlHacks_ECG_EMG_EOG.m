clear all
close all
clc

for ii=1:3;

d = daq("ni");

addinput(d,"Dev2","ai0","Voltage");

addinput(d,"Dev2","ai1","Voltage");

addinput(d,"Dev2","ai2","Voltage");

%#ok<*AGROW>
Dev2_1 = [];
n = ceil(d.Rate/10);

t = tic;

start(d,"continuous")


while toc(t) < 20 % Increase or decrease the pause duration to fit your needs.
    data = read(d,n);
    Dev2_1 = [Dev2_1; data];
    time=seconds(Dev2_1.Time);
    signal1=Dev2_1.Dev2_ai0; % ECG
    signal2=Dev2_1.Dev2_ai1; % EOG
    signal3=Dev2_1.Dev2_ai2; % EMG

    % Uncomment the following lines to enable live plotting.
    % plot(data.Time, data.Variables)
    subplot(3,1,1)
    plot(seconds(Dev2_1.Time),Dev2_1.Dev2_ai0)
    xlabel("Time (s)")
    ylabel("ECG Signal (V)")
    subplot(3,1,2)
    plot(seconds(Dev2_1.Time),Dev2_1.Dev2_ai1)
    xlabel("Time (s)")
    ylabel("EOG Signal (V)")
    subplot(3,1,3)
    plot(seconds(Dev2_1.Time),Dev2_1.Dev2_ai2)
    xlabel("Time (s)")
    ylabel("EMG Signal (V)")
    %legend(data.Properties.VariableNames)
end
stop(d)


save()

% Display the read data
% Dev2_1

time=seconds(Dev2_1.Time);
signal1=Dev2_1.Dev2_ai0;
signal2=Dev2_1.Dev2_ai1;
signal3=Dev2_1.Dev2_ai2;

% plot(Dev2_1.Time, Dev2_1.Variables)
% xlabel("Time (s)")
% ylabel("Amplitude")
% legend(Dev2_1.Properties.VariableNames, "Interpreter", "none")


%csv save
% 
% writematrix([time,signal1,signal2,signal3], strcat("Trible_EXG_Signal",num2str(ii),".csv"));

[xxx,yyy]=findpeaks(signal1,1000, "MinPeakDistance",0.7,'MinPeakHeight', mean(signal1) + 0.5 * std(signal1));
ECGbpm=size(yyy,1);

EMG_envelope=envelope(signal2,150,'rms');
High_EMG=max(EMG_envelope);
Mean_EMG=min(EMG_envelope);
Low_EMG=mean(EMG_envelope);

[eogxxx,eogyyy]=findpeaks(signal2,1000, "MinPeakDistance",0.7,'MinPeakHeight', mean(signal2) + 0.9 * std(signal2));
ECGbpm=size(yyy,1);
Eyeblinks=size(eogxxx,1);

outputsentences=strcat("The bpm is ", num2str(ECGbpm*3), ...
            ";the eye blink # is ", num2str(Eyeblinks), ...
            "; and the EMG Max, Min & average levels are ", ...
            num2str(High_EMG), ", ", num2str(Low_EMG), ", ", num2str(Mean_EMG));
disp(outputsentences);

%json save

% 整理成结构体
    dataStruct = struct( ...
        "Segment", ii, ...
        "Message", outputsentences, ...
        "Time", time, ...
        "Signal1", signal1, ...
        "Signal2", signal2, ...
        "Signal3", signal3);
        

    % 转换成JSON
    jsonStr = jsonencode(dataStruct);

    % 保存到文件
    % fileName = strcat("Trible_EXG_Signal",num2str(ii),".json");
        
    fileName = strcat("Trible_EXG_Signal.json");

    fid = fopen(fileName, "w");
    fprintf(fid, "%s", jsonStr);
    fclose(fid);


end