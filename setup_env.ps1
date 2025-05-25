# setup_env.ps1
$venvPath = "Z:\Projects\Phil-Earthquake-Monitoring\DataProcessing\dataproc_env"
$scriptPath = "Z:\Projects\Phil-Earthquake-Monitoring\DataProcessing\main.py"

# Set CD Folder
cd "Z:\Projects\Phil-Earthquake-Monitoring\DataProcessing"

# Activate venv
& "$venvPath\Scripts\Activate.ps1"

# Set environment variables
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-11.0.27.6-hotspot"
$env:HADOOP_HOME = "C:\hadoop"
$env:Path = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;" + $env:Path

