"""Core module for testing the helper functions."""

import json
from pathlib import Path
from typing import Generator
from unittest import mock

import pytest

from vantage_agent.helpers import (
    cache_dict,
    load_cached_dict,
    parse_slurm_config,
    parse_slurm_nodes,
    parse_slurm_partitions,
    parse_slurm_queue,
)


@pytest.fixture
def raw_scontrol_show_config() -> Generator[str, None, None]:
    """Yield an example of the `scontrol show config` command."""
    yield """
    Configuration data as of 2024-08-19T19:08:02
    AccountingStorageBackupHost = (null)
    AccountingStorageEnforce = none
    AccountingStorageHost   = 10.59.51.10
    AccountingStorageExternalHost = (null)
    AccountingStorageParameters = (null)
    AccountingStoragePort   = 6839
    AccountingStorageTRES   = cpu,mem,energy,node,billing,fs/disk,vmem,pages
    AccountingStorageType   = accounting_storage/slurmdbd
    AccountingStorageUser   = N/A
    AccountingStoreFlags    = (null)
    AcctGatherEnergyType    = acct_gather_energy/none
    AcctGatherFilesystemType = acct_gather_filesystem/none
    AcctGatherInterconnectType = acct_gather_interconnect/none
    AcctGatherNodeFreq      = 0 sec
    AcctGatherProfileType   = acct_gather_profile/none
    AllowSpecResourcesUsage = No
    AuthAltTypes            = auth/jwt
    AuthAltParameters       = jwt_key=/var/lib/slurm/slurmctld/jwt_hs256.key
    AuthInfo                = socket=/var/run/munge/munge.socket.2
    AuthType                = auth/munge
    BatchStartTimeout       = 10 sec
    BcastExclude            = /lib,/usr/lib,/lib64,/usr/lib64
    BcastParameters         = (null)
    BOOT_TIME               = 2024-08-07T19:57:56
    BurstBufferType         = (null)
    CliFilterPlugins        = (null)
    ClusterName             = demo-cluster
    CommunicationParameters = (null)
    CompleteWait            = 0 sec
    CoreSpecPlugin          = core_spec/none
    CpuFreqDef              = Unknown
    CpuFreqGovernors        = OnDemand,Performance,UserSpace
    CredType                = cred/munge
    DebugFlags              = NO_CONF_HASH
    DefMemPerNode           = UNLIMITED
    DependencyParameters    = (null)
    DisableRootJobs         = No
    EioTimeout              = 60
    EnforcePartLimits       = NO
    Epilog                  = (null)
    EpilogMsgTime           = 2000 usec
    EpilogSlurmctld         = (null)
    ExtSensorsType          = ext_sensors/none
    ExtSensorsFreq          = 0 sec
    FederationParameters    = (null)
    FirstJobId              = 1
    GetEnvTimeout           = 2 sec
    GresTypes               = (null)
    GpuFreqDef              = (null)
    GroupUpdateForce        = 1
    GroupUpdateTime         = 600 sec
    HASH_VAL                = Match
    HealthCheckInterval     = 0 sec
    HealthCheckNodeState    = ANY
    HealthCheckProgram      = (null)
    InactiveLimit           = 0 sec
    InteractiveStepOptions  = --interactive --preserve-env --pty $SHELL
    JobAcctGatherFrequency  = 30
    JobAcctGatherType       = jobacct_gather/linux
    JobAcctGatherParams     = (null)
    JobCompHost             = localhost
    JobCompLoc              = (null)
    JobCompParams           = (null)
    JobCompPort             = 0
    JobCompType             = jobcomp/none
    JobCompUser             = root
    JobContainerType        = job_container/none
    JobCredentialPrivateKey = (null)
    JobCredentialPublicCertificate = (null)
    JobDefaults             = (null)
    JobFileAppend           = 0
    JobRequeue              = 1
    JobSubmitPlugins        = (null)
    KillOnBadExit           = 0
    KillWait                = 30 sec
    LaunchParameters        = (null)
    Licenses                = (null)
    LogTimeFormat           = iso8601_ms
    MailDomain              = (null)
    MailProg                = /bin/mail
    MaxArraySize            = 1001
    MaxBatchRequeue         = 5
    MaxDBDMsgs              = 20004
    MaxJobCount             = 10000
    MaxJobId                = 67043328
    MaxMemPerNode           = UNLIMITED
    MaxNodeCount            = 1
    MaxStepCount            = 40000
    MaxTasksPerNode         = 512
    MCSPlugin               = mcs/none
    MCSParameters           = (null)
    MessageTimeout          = 10 sec
    MinJobAge               = 300 sec
    MpiDefault              = none
    MpiParams               = (null)
    MULTIPLE_SLURMD         = Yes
    NEXT_JOB_ID             = 1
    NodeFeaturesPlugins     = (null)
    OverTimeLimit           = 0 min
    PluginDir               = /usr/lib/x86_64-linux-gnu/slurm-wlm/
    PlugStackConfig         = /etc/slurm/plugstack.conf
    PowerParameters         = (null)
    PowerPlugin             =
    PreemptMode             = OFF
    PreemptParameters       = (null)
    PreemptType             = preempt/none
    PreemptExemptTime       = 00:00:00
    PrEpParameters          = (null)
    PrEpPlugins             = prep/script
    PriorityParameters      = (null)
    PrioritySiteFactorParameters = (null)
    PrioritySiteFactorPlugin = (null)
    PriorityType            = priority/basic
    PrivateData             = none
    ProctrackType           = proctrack/linuxproc
    Prolog                  = (null)
    PrologEpilogTimeout     = 65534
    PrologSlurmctld         = (null)
    PrologFlags             = (null)
    PropagatePrioProcess    = 0
    PropagateResourceLimits = ALL
    PropagateResourceLimitsExcept = (null)
    RebootProgram           = (null)
    ReconfigFlags           = (null)
    RequeueExit             = (null)
    RequeueExitHold         = (null)
    ResumeFailProgram       = (null)
    ResumeProgram           = (null)
    ResumeRate              = 300 nodes/min
    ResumeTimeout           = 60 sec
    ResvEpilog              = (null)
    ResvOverRun             = 0 min
    ResvProlog              = (null)
    ReturnToService         = 2
    RoutePlugin             = route/default
    SchedulerParameters     = (null)
    SchedulerTimeSlice      = 30 sec
    SchedulerType           = sched/backfill
    ScronParameters         = (null)
    SelectType              = select/cons_res
    SelectTypeParameters    = CR_CORE
    SlurmUser               = slurm(64030)
    SlurmctldAddr           = 10.59.51.10
    SlurmctldDebug          = info
    SlurmctldHost[0]        = democluster-example
    SlurmctldLogFile        = /var/log/slurm/slurmctld.log
    SlurmctldPort           = 6817
    SlurmctldSyslogDebug    = (null)
    SlurmctldPrimaryOffProg = (null)
    SlurmctldPrimaryOnProg  = (null)
    SlurmctldTimeout        = 300 sec
    SlurmctldParameters     = (null)
    SlurmdDebug             = info
    SlurmdLogFile           = /var/log/slurm/slurmd.log
    SlurmdParameters        = (null)
    SlurmdPidFile           = /var/run/slurmd.pid
    SlurmdPort              = 6818
    SlurmdSpoolDir          = /var/lib/slurm/slurmd
    SlurmdSyslogDebug       = (null)
    SlurmdTimeout           = 60 sec
    SlurmdUser              = root(0)
    SlurmSchedLogFile       = (null)
    SlurmSchedLogLevel      = 0
    SlurmctldPidFile        = /var/run/slurmctld.pid
    SLURM_CONF              = /etc/slurm/slurm.conf
    SLURM_VERSION           = 23.02.7
    SrunEpilog              = (null)
    SrunPortRange           = 0-0
    SrunProlog              = (null)
    StateSaveLocation       = /var/lib/slurm/checkpoint
    SuspendExcNodes         = (null)
    SuspendExcParts         = (null)
    SuspendExcStates        = (null)
    SuspendProgram          = (null)
    SuspendRate             = 60 nodes/min
    SuspendTime             = INFINITE
    SuspendTimeout          = 30 sec
    SwitchParameters        = (null)
    SwitchType              = switch/none
    TaskEpilog              = (null)
    TaskPlugin              = task/none
    TaskPluginParam         = (null type)
    TaskProlog              = (null)
    TCPTimeout              = 2 sec
    TmpFS                   = /tmp
    TopologyParam           = (null)
    TopologyPlugin          = topology/none
    TrackWCKey              = No
    TreeWidth               = 50
    UsePam                  = No
    UnkillableStepProgram   = (null)
    UnkillableStepTimeout   = 60 sec
    VSizeFactor             = 0 percent
    WaitTime                = 0 sec
    X11Parameters           = (null)

    Slurmctld(primary) at democluster-example is UP
    """


@pytest.fixture
def parsed_scontrol_show_config() -> Generator[dict[str, str], None, None]:
    """Yield a parsed example of the `scontrol show config` command."""
    yield {
        "AccountingStorageBackupHost": "(null)",
        "AccountingStorageEnforce": "none",
        "AccountingStorageHost": "10.59.51.10",
        "AccountingStorageExternalHost": "(null)",
        "AccountingStorageParameters": "(null)",
        "AccountingStoragePort": "6839",
        "AccountingStorageTRES": "cpu,mem,energy,node,billing,fs/disk,vmem,pages",
        "AccountingStorageType": "accounting_storage/slurmdbd",
        "AccountingStorageUser": "N/A",
        "AccountingStoreFlags": "(null)",
        "AcctGatherEnergyType": "acct_gather_energy/none",
        "AcctGatherFilesystemType": "acct_gather_filesystem/none",
        "AcctGatherInterconnectType": "acct_gather_interconnect/none",
        "AcctGatherNodeFreq": "0 sec",
        "AcctGatherProfileType": "acct_gather_profile/none",
        "AllowSpecResourcesUsage": "No",
        "AuthAltTypes": "auth/jwt",
        "AuthAltParameters": "jwt_key=/var/lib/slurm/slurmctld/jwt_hs256.key",
        "AuthInfo": "socket=/var/run/munge/munge.socket.2",
        "AuthType": "auth/munge",
        "BatchStartTimeout": "10 sec",
        "BcastExclude": "/lib,/usr/lib,/lib64,/usr/lib64",
        "BcastParameters": "(null)",
        "BOOT_TIME": "2024-08-07T19:57:56",
        "BurstBufferType": "(null)",
        "CliFilterPlugins": "(null)",
        "ClusterName": "demo-cluster",
        "CommunicationParameters": "(null)",
        "CompleteWait": "0 sec",
        "CoreSpecPlugin": "core_spec/none",
        "CpuFreqDef": "Unknown",
        "CpuFreqGovernors": "OnDemand,Performance,UserSpace",
        "CredType": "cred/munge",
        "DebugFlags": "NO_CONF_HASH",
        "DefMemPerNode": "UNLIMITED",
        "DependencyParameters": "(null)",
        "DisableRootJobs": "No",
        "EioTimeout": "60",
        "EnforcePartLimits": "NO",
        "Epilog": "(null)",
        "EpilogMsgTime": "2000 usec",
        "EpilogSlurmctld": "(null)",
        "ExtSensorsType": "ext_sensors/none",
        "ExtSensorsFreq": "0 sec",
        "FederationParameters": "(null)",
        "FirstJobId": "1",
        "GetEnvTimeout": "2 sec",
        "GresTypes": "(null)",
        "GpuFreqDef": "(null)",
        "GroupUpdateForce": "1",
        "GroupUpdateTime": "600 sec",
        "HASH_VAL": "Match",
        "HealthCheckInterval": "0 sec",
        "HealthCheckNodeState": "ANY",
        "HealthCheckProgram": "(null)",
        "InactiveLimit": "0 sec",
        "InteractiveStepOptions": "--interactive --preserve-env --pty $SHELL",
        "JobAcctGatherFrequency": "30",
        "JobAcctGatherType": "jobacct_gather/linux",
        "JobAcctGatherParams": "(null)",
        "JobCompHost": "localhost",
        "JobCompLoc": "(null)",
        "JobCompParams": "(null)",
        "JobCompPort": "0",
        "JobCompType": "jobcomp/none",
        "JobCompUser": "root",
        "JobContainerType": "job_container/none",
        "JobCredentialPrivateKey": "(null)",
        "JobCredentialPublicCertificate": "(null)",
        "JobDefaults": "(null)",
        "JobFileAppend": "0",
        "JobRequeue": "1",
        "JobSubmitPlugins": "(null)",
        "KillOnBadExit": "0",
        "KillWait": "30 sec",
        "LaunchParameters": "(null)",
        "Licenses": "(null)",
        "LogTimeFormat": "iso8601_ms",
        "MailDomain": "(null)",
        "MailProg": "/bin/mail",
        "MaxArraySize": "1001",
        "MaxBatchRequeue": "5",
        "MaxDBDMsgs": "20004",
        "MaxJobCount": "10000",
        "MaxJobId": "67043328",
        "MaxMemPerNode": "UNLIMITED",
        "MaxNodeCount": "1",
        "MaxStepCount": "40000",
        "MaxTasksPerNode": "512",
        "MCSPlugin": "mcs/none",
        "MCSParameters": "(null)",
        "MessageTimeout": "10 sec",
        "MinJobAge": "300 sec",
        "MpiDefault": "none",
        "MpiParams": "(null)",
        "MULTIPLE_SLURMD": "Yes",
        "NEXT_JOB_ID": "1",
        "NodeFeaturesPlugins": "(null)",
        "OverTimeLimit": "0 min",
        "PluginDir": "/usr/lib/x86_64-linux-gnu/slurm-wlm/",
        "PlugStackConfig": "/etc/slurm/plugstack.conf",
        "PowerParameters": "(null)",
        "PowerPlugin": "",
        "PreemptMode": "OFF",
        "PreemptParameters": "(null)",
        "PreemptType": "preempt/none",
        "PreemptExemptTime": "00:00:00",
        "PrEpParameters": "(null)",
        "PrEpPlugins": "prep/script",
        "PriorityParameters": "(null)",
        "PrioritySiteFactorParameters": "(null)",
        "PrioritySiteFactorPlugin": "(null)",
        "PriorityType": "priority/basic",
        "PrivateData": "none",
        "ProctrackType": "proctrack/linuxproc",
        "Prolog": "(null)",
        "PrologEpilogTimeout": "65534",
        "PrologSlurmctld": "(null)",
        "PrologFlags": "(null)",
        "PropagatePrioProcess": "0",
        "PropagateResourceLimits": "ALL",
        "PropagateResourceLimitsExcept": "(null)",
        "RebootProgram": "(null)",
        "ReconfigFlags": "(null)",
        "RequeueExit": "(null)",
        "RequeueExitHold": "(null)",
        "ResumeFailProgram": "(null)",
        "ResumeProgram": "(null)",
        "ResumeRate": "300 nodes/min",
        "ResumeTimeout": "60 sec",
        "ResvEpilog": "(null)",
        "ResvOverRun": "0 min",
        "ResvProlog": "(null)",
        "ReturnToService": "2",
        "RoutePlugin": "route/default",
        "SchedulerParameters": "(null)",
        "SchedulerTimeSlice": "30 sec",
        "SchedulerType": "sched/backfill",
        "ScronParameters": "(null)",
        "SelectType": "select/cons_res",
        "SelectTypeParameters": "CR_CORE",
        "SlurmUser": "slurm(64030)",
        "SlurmctldAddr": "10.59.51.10",
        "SlurmctldDebug": "info",
        "SlurmctldHost[0]": "democluster-example",
        "SlurmctldLogFile": "/var/log/slurm/slurmctld.log",
        "SlurmctldPort": "6817",
        "SlurmctldSyslogDebug": "(null)",
        "SlurmctldPrimaryOffProg": "(null)",
        "SlurmctldPrimaryOnProg": "(null)",
        "SlurmctldTimeout": "300 sec",
        "SlurmctldParameters": "(null)",
        "SlurmdDebug": "info",
        "SlurmdLogFile": "/var/log/slurm/slurmd.log",
        "SlurmdParameters": "(null)",
        "SlurmdPidFile": "/var/run/slurmd.pid",
        "SlurmdPort": "6818",
        "SlurmdSpoolDir": "/var/lib/slurm/slurmd",
        "SlurmdSyslogDebug": "(null)",
        "SlurmdTimeout": "60 sec",
        "SlurmdUser": "root(0)",
        "SlurmSchedLogFile": "(null)",
        "SlurmSchedLogLevel": "0",
        "SlurmctldPidFile": "/var/run/slurmctld.pid",
        "SLURM_CONF": "/etc/slurm/slurm.conf",
        "SLURM_VERSION": "23.02.7",
        "SrunEpilog": "(null)",
        "SrunPortRange": "0-0",
        "SrunProlog": "(null)",
        "StateSaveLocation": "/var/lib/slurm/checkpoint",
        "SuspendExcNodes": "(null)",
        "SuspendExcParts": "(null)",
        "SuspendExcStates": "(null)",
        "SuspendProgram": "(null)",
        "SuspendRate": "60 nodes/min",
        "SuspendTime": "INFINITE",
        "SuspendTimeout": "30 sec",
        "SwitchParameters": "(null)",
        "SwitchType": "switch/none",
        "TaskEpilog": "(null)",
        "TaskPlugin": "task/none",
        "TaskPluginParam": "(null type)",
        "TaskProlog": "(null)",
        "TCPTimeout": "2 sec",
        "TmpFS": "/tmp",
        "TopologyParam": "(null)",
        "TopologyPlugin": "topology/none",
        "TrackWCKey": "No",
        "TreeWidth": "50",
        "UsePam": "No",
        "UnkillableStepProgram": "(null)",
        "UnkillableStepTimeout": "60 sec",
        "VSizeFactor": "0 percent",
        "WaitTime": "0 sec",
        "X11Parameters": "(null)",
    }


@pytest.fixture
def raw_scontrol_show_partition() -> Generator[str, None, None]:
    """Yield a raw example of the `scontrol show partition` command."""
    yield """
    PartitionName=debug
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=YES QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=3 MaxTime=60 MinNodes=0 LLN=NO MaxCPUsPerNode=32 MaxCPUsPerSocket=UNLIMITED
        Nodes=node[01-03]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=UP TotalCPUs=96 TotalNodes=3 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED
        TRES=cpu=96,mem=UNLIMITED,node=3,billing=96

    PartitionName=normal
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=NO QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=7 MaxTime=INFINITE MinNodes=0 LLN=NO MaxCPUsPerNode=64 MaxCPUsPerSocket=UNLIMITED
        Nodes=node[04-10]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=DOWN TotalCPUs=448 TotalNodes=7 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED
        TRES=cpu=448,mem=UNLIMITED,node=7,billing=448

    PartitionName=longrun
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=NO QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=5 MaxTime=INFINITE MinNodes=0 LLN=NO MaxCPUsPerNode=48 MaxCPUsPerSocket=UNLIMITED
        Nodes=node[11-15]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=MAINT TotalCPUs=240 TotalNodes=5 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED
        TRES=cpu=240,mem=UNLIMITED,node=5,billing=240
    """


@pytest.fixture
def parsed_scontrol_show_partition() -> Generator[dict[str, dict[str, str]], None, None]:
    """Yield a parsed example of the `scontrol show partition` command."""
    yield {
        "debug": {
            "AllowGroups": "ALL",
            "AllowAccounts": "ALL",
            "AllowQos": "ALL",
            "AllocNodes": "ALL",
            "Default": "YES",
            "QoS": "N/A",
            "DefaultTime": "NONE",
            "DisableRootJobs": "NO",
            "ExclusiveUser": "NO",
            "GraceTime": "0",
            "Hidden": "NO",
            "MaxNodes": "3",
            "MaxTime": "60",
            "MinNodes": "0",
            "LLN": "NO",
            "MaxCPUsPerNode": "32",
            "MaxCPUsPerSocket": "UNLIMITED",
            "Nodes": "node[01-03]",
            "PriorityJobFactor": "1",
            "PriorityTier": "1",
            "RootOnly": "NO",
            "ReqResv": "NO",
            "OverSubscribe": "NO",
            "OverTimeLimit": "NONE",
            "PreemptMode": "OFF",
            "State": "UP",
            "TotalCPUs": "96",
            "TotalNodes": "3",
            "SelectTypeParameters": "NONE",
            "JobDefaults": "(null)",
            "DefMemPerNode": "UNLIMITED",
            "MaxMemPerNode": "UNLIMITED",
            "TRES": "cpu=96,mem=UNLIMITED,node=3,billing=96",
        },
        "normal": {
            "AllowGroups": "ALL",
            "AllowAccounts": "ALL",
            "AllowQos": "ALL",
            "AllocNodes": "ALL",
            "Default": "NO",
            "QoS": "N/A",
            "DefaultTime": "NONE",
            "DisableRootJobs": "NO",
            "ExclusiveUser": "NO",
            "GraceTime": "0",
            "Hidden": "NO",
            "MaxNodes": "7",
            "MaxTime": "INFINITE",
            "MinNodes": "0",
            "LLN": "NO",
            "MaxCPUsPerNode": "64",
            "MaxCPUsPerSocket": "UNLIMITED",
            "Nodes": "node[04-10]",
            "PriorityJobFactor": "1",
            "PriorityTier": "1",
            "RootOnly": "NO",
            "ReqResv": "NO",
            "OverSubscribe": "NO",
            "OverTimeLimit": "NONE",
            "PreemptMode": "OFF",
            "State": "DOWN",
            "TotalCPUs": "448",
            "TotalNodes": "7",
            "SelectTypeParameters": "NONE",
            "JobDefaults": "(null)",
            "DefMemPerNode": "UNLIMITED",
            "MaxMemPerNode": "UNLIMITED",
            "TRES": "cpu=448,mem=UNLIMITED,node=7,billing=448",
        },
        "longrun": {
            "AllowGroups": "ALL",
            "AllowAccounts": "ALL",
            "AllowQos": "ALL",
            "AllocNodes": "ALL",
            "Default": "NO",
            "QoS": "N/A",
            "DefaultTime": "NONE",
            "DisableRootJobs": "NO",
            "ExclusiveUser": "NO",
            "GraceTime": "0",
            "Hidden": "NO",
            "MaxNodes": "5",
            "MaxTime": "INFINITE",
            "MinNodes": "0",
            "LLN": "NO",
            "MaxCPUsPerNode": "48",
            "MaxCPUsPerSocket": "UNLIMITED",
            "Nodes": "node[11-15]",
            "PriorityJobFactor": "1",
            "PriorityTier": "1",
            "RootOnly": "NO",
            "ReqResv": "NO",
            "OverSubscribe": "NO",
            "OverTimeLimit": "NONE",
            "PreemptMode": "OFF",
            "State": "MAINT",
            "TotalCPUs": "240",
            "TotalNodes": "5",
            "SelectTypeParameters": "NONE",
            "JobDefaults": "(null)",
            "DefMemPerNode": "UNLIMITED",
            "MaxMemPerNode": "UNLIMITED",
            "TRES": "cpu=240,mem=UNLIMITED,node=5,billing=240",
        },
    }


@pytest.fixture
def raw_scontrol_show_node() -> Generator[str, None, None]:
    """Yield a raw example of the `scontrol show node` command."""
    yield """
    NodeName=node01 Arch=x86_64 CoresPerSocket=8
        CPUAlloc=2 CPUErr=0 CPUTot=16 CPULoad=0.05
        AvailableFeatures=(null) ActiveFeatures=(null)
        Gres=gpu:2 NodeAddr=node01 NodeHostName=node01 Version=20.11
        OS=Linux 3.10.0-1160.el7.x86_64 #1 SMP Tue Sep 22 17:24:55 UTC 2020
        RealMemory=64000 AllocMem=20000 FreeMem=40000 Sockets=2 Boards=1
        State=IDLE ThreadsPerCore=2 TmpDisk=0 Weight=1 Owner=N/A MCS_label=N/A
        BootTime=2021-04-15T10:05:55 SlurmdStartTime=2021-04-15T10:10:30
        CfgTRES=cpu=16,mem=64000M,billing=16
        AllocTRES=cpu=2,mem=20000M
        CapWatts=n/a
        CurrentWatts=0 LowestJoules=0 ConsumedJoules=0
        ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s
        Reason=NHC: check_ps_service:  Service sshd (process sshd) owned by root not running [root@2024-08-20T16:32:47]

    NodeName=node02 Arch=x86_64 CoresPerSocket=8
        CPUAlloc=0 CPUErr=0 CPUTot=16 CPULoad=0.00
        AvailableFeatures=(null) ActiveFeatures=(null)
        Gres=gpu:2 NodeAddr=node02 NodeHostName=node02 Version=20.11
        OS=Linux 3.10.0-1160.el7.x86_64 #1 SMP Tue Sep 22 17:24:55 UTC 2020
        RealMemory=64000 AllocMem=0 FreeMem=64000 Sockets=2 Boards=1
        State=ALLOCATED ThreadsPerCore=2 TmpDisk=0 Weight=1 Owner=N/A MCS_label=N/A
        BootTime=2021-04-15T10:05:55 SlurmdStartTime=2021-04-15T10:10:30
        CfgTRES=cpu=16,mem=64000M,billing=16
        AllocTRES=cpu=0,mem=0M
        CapWatts=n/a
        CurrentWatts=0 LowestJoules=0 ConsumedJoules=0
        ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s
        Reason=NHC: check_ps_service:  Service sshd (process sshd) owned by root not running [root@2024-08-20T16:32:47]
    """


@pytest.fixture
def raw_squeue_all() -> Generator[str, None, None]:
    """Yield a raw example of the `squeue -o %all` command."""
    yield """
    ACCOUNT|TRES_PER_NODE|MIN_CPUS|MIN_TMP_DISK|END_TIME|FEATURES|GROUP|OVER_SUBSCRIBE|JOBID|NAME|COMMENT|TIME_LIMIT|MIN_MEMORY|REQ_NODES|COMMAND|PRIORITY|QOS|REASON|ST|USER|RESERVATION|WCKEY|EXC_NODES|NICE|S:C:T|JOBID|EXEC_HOST|CPUS|NODES|DEPENDENCY|ARRAY_JOB_ID|GROUP|SOCKETS_PER_NODE|CORES_PER_SOCKET|THREADS_PER_CORE|ARRAY_TASK_ID|TIME_LEFT|TIME|NODELIST|CONTIGUOUS|PARTITION|PRIORITY|NODELIST(REASON)|START_TIME|STATE|UID|SUBMIT_TIME|LICENSES|CORE_SPEC|SCHEDNODES|WORK_DIR
(null)|N/A|1|0|NONE|(null)|ubuntu|OK|1|spawner-jupyterhub|(null)|UNLIMITED|0||(null)|0.99998474121093|normal|None|R|ubuntu|(null)|(null)||0|*:*:*|1|compute-compute-4|1|1|(null)|1|1000|*|*|*|N/A|UNLIMITED|15:56:32|compute-compute-4|0|compute|4294901759|compute-compute-4|2025-06-17T00:55:01|RUNNING|1000|2025-06-17T00:51:03|(null)|N/A|(null)|/home/ubuntu
(null)|N/A|1|0|NONE|(null)|ubuntu|OK|2|spawner-jupyterhub|(null)|UNLIMITED|0||(null)|0.99998474097810|normal|None|R|ubuntu|(null)|(null)||0|*:*:*|2|compute-compute-4|1|1|(null)|2|1000|*|*|*|N/A|UNLIMITED|15:56:32|compute-compute-4|0|compute|4294901758|compute-compute-4|2025-06-17T00:55:01|RUNNING|1000|2025-06-17T00:51:04|(null)|N/A|(null)|/home/ubuntu
    """  # noqa


@pytest.fixture
def parsed_squeue_all() -> Generator[list[dict[str, str]], None, None]:
    """Yield a parsed example of the `squeue -o %all` command."""
    yield {
        "1-spawner-jupyterhub": {
            "account": "(null)",
            "tres_per_node": "N/A",
            "min_cpus": "1",
            "min_tmp_disk": "0",
            "end_time": "NONE",
            "features": "(null)",
            "group": "1000",
            "over_subscribe": "OK",
            "jobid": "1",
            "name": "spawner-jupyterhub",
            "comment": "(null)",
            "time_limit": "UNLIMITED",
            "min_memory": "0",
            "req_nodes": "",
            "command": "(null)",
            "priority": "4294901759",
            "qos": "normal",
            "reason": "None",
            "st": "R",
            "user": "ubuntu",
            "reservation": "(null)",
            "wckey": "(null)",
            "exc_nodes": "",
            "nice": "0",
            "s:c:t": "*:*:*",
            "exec_host": "compute-compute-4",
            "cpus": "1",
            "nodes": "1",
            "dependency": "(null)",
            "array_job_id": "1",
            "sockets_per_node": "*",
            "cores_per_socket": "*",
            "threads_per_core": "*",
            "array_task_id": "N/A",
            "time_left": "UNLIMITED",
            "time": "15:56:32",
            "nodelist": "compute-compute-4",
            "contiguous": "0",
            "partition": "compute",
            "nodelist(reason)": "compute-compute-4",
            "start_time": "2025-06-17T00:55:01",
            "state": "RUNNING",
            "uid": "1000",
            "submit_time": "2025-06-17T00:51:03",
            "licenses": "(null)",
            "core_spec": "N/A",
            "schednodes": "(null)",
            "work_dir": "/home/ubuntu",
        },
        "2-spawner-jupyterhub": {
            "account": "(null)",
            "tres_per_node": "N/A",
            "min_cpus": "1",
            "min_tmp_disk": "0",
            "end_time": "NONE",
            "features": "(null)",
            "group": "1000",
            "over_subscribe": "OK",
            "jobid": "2",
            "name": "spawner-jupyterhub",
            "comment": "(null)",
            "time_limit": "UNLIMITED",
            "min_memory": "0",
            "req_nodes": "",
            "command": "(null)",
            "priority": "4294901758",
            "qos": "normal",
            "reason": "None",
            "st": "R",
            "user": "ubuntu",
            "reservation": "(null)",
            "wckey": "(null)",
            "exc_nodes": "",
            "nice": "0",
            "s:c:t": "*:*:*",
            "exec_host": "compute-compute-4",
            "cpus": "1",
            "nodes": "1",
            "dependency": "(null)",
            "array_job_id": "2",
            "sockets_per_node": "*",
            "cores_per_socket": "*",
            "threads_per_core": "*",
            "array_task_id": "N/A",
            "time_left": "UNLIMITED",
            "time": "15:56:32",
            "nodelist": "compute-compute-4",
            "contiguous": "0",
            "partition": "compute",
            "nodelist(reason)": "compute-compute-4",
            "start_time": "2025-06-17T00:55:01",
            "state": "RUNNING",
            "uid": "1000",
            "submit_time": "2025-06-17T00:51:04",
            "licenses": "(null)",
            "core_spec": "N/A",
            "schednodes": "(null)",
            "work_dir": "/home/ubuntu",
        },
    }


@pytest.fixture
def parsed_scontrol_show_node() -> Generator[dict[str, dict[str, str]], None, None]:
    """Yield a parsed example of the `scontrol show node` command."""
    yield {
        "node01": {
            "Arch": "x86_64",
            "CoresPerSocket": "8",
            "CPUAlloc": "2",
            "CPUErr": "0",
            "CPUTot": "16",
            "CPULoad": "0.05",
            "AvailableFeatures": "(null)",
            "ActiveFeatures": "(null)",
            "Gres": "gpu:2",
            "NodeAddr": "node01",
            "NodeHostName": "node01",
            "Version": "20.11",
            "OS": "Linux 3.10.0-1160.el7.x86_64 #1 SMP Tue Sep 22 17:24:55 UTC 2020",
            "RealMemory": "64000",
            "AllocMem": "20000",
            "FreeMem": "40000",
            "Sockets": "2",
            "Boards": "1",
            "State": "IDLE",
            "ThreadsPerCore": "2",
            "TmpDisk": "0",
            "Weight": "1",
            "Owner": "N/A",
            "MCS_label": "N/A",
            "BootTime": "2021-04-15T10:05:55",
            "SlurmdStartTime": "2021-04-15T10:10:30",
            "CfgTRES": "cpu=16,mem=64000M,billing=16",
            "AllocTRES": "cpu=2,mem=20000M",
            "CapWatts": "n/a",
            "CurrentWatts": "0",
            "LowestJoules": "0",
            "ConsumedJoules": "0",
            "ExtSensorsJoules": "n/s",
            "ExtSensorsWatts": "0",
            "ExtSensorsTemp": "n/s",
            "Reason": "NHC: check_ps_service:  Service sshd (process sshd) owned by root not running [root@2024-08-20T16:32:47]",
        },
        "node02": {
            "Arch": "x86_64",
            "CoresPerSocket": "8",
            "CPUAlloc": "0",
            "CPUErr": "0",
            "CPUTot": "16",
            "CPULoad": "0.00",
            "AvailableFeatures": "(null)",
            "ActiveFeatures": "(null)",
            "Gres": "gpu:2",
            "NodeAddr": "node02",
            "NodeHostName": "node02",
            "Version": "20.11",
            "OS": "Linux 3.10.0-1160.el7.x86_64 #1 SMP Tue Sep 22 17:24:55 UTC 2020",
            "RealMemory": "64000",
            "AllocMem": "0",
            "FreeMem": "64000",
            "Sockets": "2",
            "Boards": "1",
            "State": "ALLOCATED",
            "ThreadsPerCore": "2",
            "TmpDisk": "0",
            "Weight": "1",
            "Owner": "N/A",
            "MCS_label": "N/A",
            "BootTime": "2021-04-15T10:05:55",
            "SlurmdStartTime": "2021-04-15T10:10:30",
            "CfgTRES": "cpu=16,mem=64000M,billing=16",
            "AllocTRES": "cpu=0,mem=0M",
            "CapWatts": "n/a",
            "CurrentWatts": "0",
            "LowestJoules": "0",
            "ConsumedJoules": "0",
            "ExtSensorsJoules": "n/s",
            "ExtSensorsWatts": "0",
            "ExtSensorsTemp": "n/s",
            "Reason": "NHC: check_ps_service:  Service sshd (process sshd) owned by root not running [root@2024-08-20T16:32:47]",
        },
    }


class TestParseCorrectSlurmOutput:
    """Test the slurm output parsing functions when the output is pretty."""

    def test_parse_slurm_config(self, raw_scontrol_show_config, parsed_scontrol_show_config):
        """Test the `parse_slurm_config` function."""
        assert parse_slurm_config(raw_scontrol_show_config) == parsed_scontrol_show_config

    def test_parse_scontrol_show_partition(self, raw_scontrol_show_partition, parsed_scontrol_show_partition):
        """Test the `parse_scontrol_show_partition` function."""
        assert parse_slurm_partitions(raw_scontrol_show_partition) == parsed_scontrol_show_partition

    def test_parse_squeue_all(self, raw_squeue_all, parsed_squeue_all):
        """Test the `parse_squeue_all` function."""
        assert parse_slurm_queue(raw_squeue_all) == parsed_squeue_all

    def test_parse_scontrol_show_node(self, raw_scontrol_show_node, parsed_scontrol_show_node):
        """Test the `parse_scontrol_show_node` function."""
        assert parse_slurm_nodes(raw_scontrol_show_node) == parsed_scontrol_show_node


class TestParseBuggySlurmOutput:
    """Test the slurm output parsing functions when the output is buggy."""

    def test_parse_buggy_slurm_config(self):
        """Test parsing the `scontrol show config` command when the output is buggy."""
        raw_output = """
        AccountingStorageBackupHost=(null)
        AccountingStorageEnforce=none
        AccountingStorageHost-buggy
        """

        expected_output = {
            "AccountingStorageBackupHost": "(null)",
            "AccountingStorageEnforce": "none",
        }

        assert parse_slurm_config(raw_output) == expected_output

    def test_parse_buggy_scontrol_show_partition(self):
        """Test parsing the `scontrol show partition` command when the output is buggy."""
        raw_output = """
        PartitionName=debug
            AllocNodes$$$$ALL Default(#&)YES MaxNodes=3 OverSubscribe!!--NO
            QoS=buggy
        """

        expected_output = {
            "debug": {
                "MaxNodes": "3",
                "QoS": "buggy",
            }
        }

        assert parse_slurm_partitions(raw_output) == expected_output

    def test_parse_empty_squeue_all(self):
        """Test parsing the `squeue -o %all` command when the output is empty."""
        raw_output = """
        ACCOUNT|TRES_PER_NODE|MIN_CPUS|MIN_TMP_DISK|END_TIME|FEATURES|GROUP|OVER_SUBSCRIBE|JOBID|NAME|COMMENT|TIME_LIMIT|MIN_MEMORY|REQ_NODES|COMMAND|PRIORITY|QOS|REASON|ST|USER|RESERVATION|WCKEY|EXC_NODES|NICE|S:C:T|JOBID|EXEC_HOST|CPUS|NODES|DEPENDENCY|ARRAY_JOB_ID|GROUP|SOCKETS_PER_NODE|CORES_PER_SOCKET|THREADS_PER_CORE|ARRAY_TASK_ID|TIME_LEFT|TIME|NODELIST|CONTIGUOUS|PARTITION|PRIORITY|NODELIST(REASON)|START_TIME|STATE|UID|SUBMIT_TIME|LICENSES|CORE_SPEC|SCHEDNODES|WORK_DIR
        """

        expected_output = {}

        assert parse_slurm_queue(raw_output) == expected_output

    def test_parse_buggy_squeue_all(self):
        """Test parsing the `squeue -o %all` command when the output is empty."""
        raw_output = """
        ACCOUNT|TRES_PER_NODE|MIN_CPUS|MIN_TMP_DISK|END_TIME|FEATURES|GROUP|OVER_SUBSCRIBE|JOBID|NAME
        (null)|N/A|1|0|NONE|(null)|ubuntu|OK|1|spawner-jupyterhub|(null)|UNLIMITED|0||(null)
        """

        expected_output = {
            "1-spawner-jupyterhub": {
                "account": "(null)",
                "tres_per_node": "N/A",
                "min_cpus": "1",
                "min_tmp_disk": "0",
                "end_time": "NONE",
                "features": "(null)",
                "group": "ubuntu",
                "over_subscribe": "OK",
                "jobid": "1",
                "name": "spawner-jupyterhub",
            }
        }

        assert parse_slurm_queue(raw_output) == expected_output

        raw_output = """
        ACCOUNT|TRES_PER_NODE|MIN_CPUS|MIN_TMP_DISK|END_TIME|FEATURES|GROUP|OVER_SUBSCRIBE|JOBID|NAME|
        (null)|N/A|1|0|(null)|ubuntu|OK|1|spawner-jupyterhub
        """

        expected_output = {
            "spawner-jupyterhub-": {
                "account": "(null)",
                "tres_per_node": "N/A",
                "min_cpus": "1",
                "min_tmp_disk": "0",
                "end_time": "(null)",
                "features": "ubuntu",
                "group": "OK",
                "over_subscribe": "1",
                "jobid": "spawner-jupyterhub",
                "name": "",
                "": "",
            }
        }

        assert parse_slurm_queue(raw_output) == expected_output

    def test_parse_buggy_scontrol_show_node(self):
        """Test parsing the `scontrol show node` command when the output is buggy."""
        raw_output = """
        NodeName=buggy Arch=x86_64 CoresPerSocket*$&#8
            CPUAlloc=0 CPUErr!!--$%0 CPUTot=16 CPULoad###0.00
        """

        expected_output = {
            "buggy": {
                "Arch": "x86_64",
                "CPUAlloc": "0",
                "CPUTot": "16",
            }
        }

        assert parse_slurm_nodes(raw_output) == expected_output


class TestLoadCachedDict:
    """Test the `load_cached_dict` function."""

    @pytest.mark.parametrize(
        "file_name, expected_data",
        [
            ("foo.json", {"alpha": "beta", "gamma": "delta"}),
            ("boo.json", {"epsilon": "zeta", "eta": "theta"}),
        ],
    )
    def test_load_existing_json(
        self, file_name: str, expected_data: dict[str, str], tmp_path_factory: pytest.TempPathFactory
    ):
        """Test loading an existing JSON file."""
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with open(cache_dir / f"{file_name}", "w") as f:
            json.dump(expected_data, f)

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            result: dict[str, str] = load_cached_dict(file_name)

        assert result == expected_data

    @pytest.mark.parametrize("file_name", ["baz", "qux"])
    def test_load_nonexistent_file(self, file_name: str, tmp_path_factory: pytest.TempPathFactory):
        """Test loading a non-existent file."""
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        # Patch SETTINGS.CACHE_DIR and call the function
        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            result = load_cached_dict(file_name)

        assert result == {}

    def test_load_invalid_json(self, tmp_path_factory: pytest.TempPathFactory):
        """Test loading an invalid JSON file."""
        file_name = "invalid_data"
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with open(f"{cache_dir}/{file_name}.json", "w") as f:
            f.write("invalid json")

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            result = load_cached_dict(file_name)

        assert result == {}

    @pytest.mark.parametrize(
        "file_name, expected_data",
        [
            ("baz", {"iota": "kappa", "lambda": "mu"}),
            ("qux", {"nu": "xi", "omicron": "pi"}),
        ],
    )
    def test_file_name_without_extension(
        self, file_name: str, expected_data: dict[str, str], tmp_path_factory: pytest.TempPathFactory
    ):
        """Test providing a file name without the .json extension."""
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with open(f"{cache_dir}/{file_name}.json", "w") as f:
            json.dump(expected_data, f)

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            result = load_cached_dict(file_name)

        assert result == expected_data


class TestCacheDict:
    """Test the `cache_dict` function."""

    @pytest.mark.parametrize(
        "file_name, content",
        [
            ("baz", {"lakers": "seahawks", "steelers": "falcons"}),
            ("qux", {"saints": "bulls", "raptors": "packers"}),
        ],
    )
    def test_cache_valid_dict(
        self, file_name: str, content: dict[str, str], tmp_path_factory: pytest.TempPathFactory
    ):
        """Test caching a valid dictionary."""
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            cache_dict(content, file_name)

        cached_file_path = cache_dir / f"{file_name}.json"
        assert cached_file_path.exists()

        with open(cached_file_path, "r") as f:
            cached_data = json.load(f)

        assert cached_data == content

    @pytest.mark.parametrize(
        "file_name, content",
        [
            ("zoo", {"eagles": "bengals", "patriots": "london"}),
            ("bar", {"broncos": "raiders", "chargers": "seattle"}),
        ],
    )
    def test_file_name_without_extension(
        self, file_name: str, content: dict[str, str], tmp_path_factory: pytest.TempPathFactory
    ):
        """Test providing a file name without the .json extension."""
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            cache_dict(content, file_name)

        cached_file_path = cache_dir / f"{file_name}.json"
        assert cached_file_path.exists()

    def test_override_existing_cache(self, tmp_path_factory: pytest.TempPathFactory):
        """Test overriding an existing cached dictionary."""
        initial_dict = {"key1": "value1"}
        new_dict = {"key2": "value2"}
        file_name = "test_override"
        cache_dir: Path = tmp_path_factory.mktemp("cache")

        with open(cache_dir / f"{file_name}.json", "w") as f:
            json.dump(initial_dict, f)

        with mock.patch("vantage_agent.helpers.SETTINGS.CACHE_DIR", str(cache_dir)):
            cache_dict(new_dict, file_name)

        cached_file_path = cache_dir / f"{file_name}.json"
        assert cached_file_path.exists()

        with open(cached_file_path, "r") as f:
            cached_data = json.load(f)

        assert cached_data == new_dict
