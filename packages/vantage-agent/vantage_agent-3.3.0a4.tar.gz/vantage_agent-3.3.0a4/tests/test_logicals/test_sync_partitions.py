"""Core module for partitions test related operations."""

import json
import os
import random
import uuid
from pathlib import Path
from subprocess import CalledProcessError
from textwrap import dedent
from typing import Any
from unittest import mock

import pytest
from respx.router import MockRouter

from vantage_agent.logicals.sync_partitions import (
    create_backup,
    get_cluster_partitions,
    get_node_type_info,
    reconfigure_slurm,
    sync_cluster_partitions,
    update_partition_config,
    update_slurm_config,
)
from vantage_agent.vantage_api_client import backend_client


def _build_partition_node_group_blob(
    node_group_name: str,
    max_nodes: int,
    region: str,
    cpu_count: int,
    launch_template_id: str,
    subnet_id: str,
    instance_type: str,
    gpu_count: int | None = None,
) -> list[dict[str, Any]]:
    slurm_specifications = {"Weight": 1, "Feature": "cloud", "CPUs": cpu_count}
    if gpu_count:
        slurm_specifications["Gres"] = f"gpu:{gpu_count}"
    return [
        {
            "NodeGroupName": node_group_name,
            "MaxNodes": max_nodes,
            "Region": region,
            "SlurmSpecifications": slurm_specifications,
            "PurchasingOption": "on-demand",
            "OnDemandOptions": {"AllocationStrategy": "lowest-price"},
            "LaunchTemplateSpecification": {
                "LaunchTemplateId": launch_template_id,
                "Version": "$Latest",
            },
            "LaunchTemplateOverrides": [{"InstanceType": instance_type}],
            "SubnetIds": [subnet_id],
        }
    ]


def _build_partition_blob(
    partition_name: str,
    max_nodes: int,
    region: str,
    cpu_count: int,
    launch_template_id: str,
    subnet_id: str,
    instance_type: str,
    gpu_count: int | None = None,
    is_default: bool = False,
) -> dict[str, Any]:
    return {
        "PartitionName": partition_name,
        "NodeGroups": _build_partition_node_group_blob(
            partition_name,
            max_nodes,
            region,
            cpu_count,
            launch_template_id,
            subnet_id,
            instance_type,
            gpu_count,
        ),
        "PartitionOptions": {"Default": "Yes" if is_default else "No"},
    }


@pytest.mark.respx(base_url=str(backend_client.base_url))
@pytest.mark.usefixtures("mock_access_token")
async def test_get_partitions(respx_mock: MockRouter):
    """Test get the partitions through the API client."""
    cluster_name = "vantage-agent"

    query = dedent(
        """
        query($filters: JSONScalar!, $first: Int, $after: Int) {
            partitions(filters: $filters, after: $after, first: $first) {
                edges {
                    node {
                        clusterName
                        id
                        isDefault
                        maxNodeCount
                        name
                        nodeType
                        cluster {
                            creationParameters
                        }
                    }
                }
            }
        }
        """
    )

    body = {
        "query": query,
        "variables": {
            "filters": {
                "clusterName": {"eq": cluster_name},
            },
            "after": 1,
            "first": 100,
        },
    }

    partitions = [
        {
            "id": 1,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": str(uuid.uuid4())}},
        }
    ]
    response_body = {"data": {"partitions": {"edges": [{"node": partition} for partition in partitions]}}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, content=json.dumps(response_body))
    response = await get_cluster_partitions()
    assert response == partitions


@mock.patch("vantage_agent.logicals.sync_partitions.copyfile")
async def test_create_backup(copyfile_mock: mock.Mock):
    """Test create a backup of slurm.conf."""
    file_path = "/etc/slurm/slurm.conf"
    from vantage_agent.settings import SETTINGS

    create_backup(file_path)
    copyfile_mock.assert_called_once_with(file_path, f"{SETTINGS.CACHE_DIR}/slurm.conf.bkp")


@mock.patch("vantage_agent.logicals.sync_partitions.copyfile")
@mock.patch("vantage_agent.logicals.sync_partitions.SETTINGS")
@mock.patch("vantage_agent.logicals.sync_partitions.get_node_type_info", new_callable=mock.AsyncMock)
async def test_update_slurm_config(
    get_node_type_info_mock: mock.AsyncMock,
    settings_mock: mock.Mock,
    copyfile_mock: mock.Mock,
):
    """Test create a backup of slurm.conf."""
    file_path = "./slurm.conf"
    settings_mock.SLURM_CONF_PATH = file_path
    settings_mock.CACHE_DIR = "./"

    t3_small_cpus = random.randint(1, 100)
    t3_small_memory = random.randint(1, 100)
    t3_xlarge_cpus = random.randint(1, 100)
    t3_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_cpus = random.randint(1, 100)
    g4dn_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_gpus = random.randint(1, 100)

    def node_info(node_type: str, region: str):
        if node_type == "t3.small":
            return {"numCpus": t3_small_cpus, "numGpus": 0, "memory": t3_small_memory}
        elif node_type == "t3.xlarge":
            return {"numCpus": t3_xlarge_cpus, "numGpus": 0, "memory": t3_xlarge_memory}
        else:
            return {"numCpus": g4dn_xlarge_cpus, "numGpus": g4dn_xlarge_gpus, "memory": g4dn_xlarge_memory}

    get_node_type_info_mock.side_effect = node_info

    with open(file_path, "w") as f:
        dummy_file = [
            "SuspendRate=100\n",
            "ResumeTimeout=600\n",
            "SuspendTime=350\n",
            "TreeWidth=60000\n",
            "NodeName=computeA-computeA-[0-9] State=CLOUD Weight=1 Feature=cloud CPUs=2 RealMemory=1024\n",
            "PartitionName=computeA Nodes=computeA-computeA-[0-9] MaxTime=INFINITE State=UP Default=Yes\n",
            "NodeName=computeB-computeB-[0-9] State=CLOUD Weight=1 Feature=cloud CPUs=2 RealMemory=1024\n",
            "PartitionName=computeB Nodes=computeB-computeB-[0-9] MaxTime=INFINITE State=UP Default=No\n",
            "NodeName=computeC-computeC-[0-9] State=CLOUD Weight=1 Feature=cloud CPUs=2 RealMemory=2048\n",
            "PartitionName=computeC Nodes=computeC-computeC-[0-9] MaxTime=INFINITE State=UP Default=No\n",
        ]
        f.writelines(dummy_file)

    partitions = [
        {
            "id": 1,
            "name": "partitionD",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": True,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
        {
            "id": 2,
            "name": "partitionE",
            "nodeType": "t3.xlarge",
            "maxNodeCount": 4,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
        {
            "id": 3,
            "name": "partitionF",
            "nodeType": "g4dn.xlarge",
            "maxNodeCount": 1,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
    ]

    expected_lines = [
        f"NodeName=partitionD-partitionD-[0-2] State=CLOUD Weight=1 Feature=cloud CPUs={t3_small_cpus} RealMemory={t3_small_memory * 1024}\n",  # noqa
        "PartitionName=partitionD Nodes=partitionD-partitionD-[0-2] MaxNodes=3 MaxTime=INFINITE State=UP Default=Yes\n",  # noqa
        f"NodeName=partitionE-partitionE-[0-3] State=CLOUD Weight=1 Feature=cloud CPUs={t3_xlarge_cpus} RealMemory={t3_xlarge_memory * 1024}\n",  # noqa
        "PartitionName=partitionE Nodes=partitionE-partitionE-[0-3] MaxNodes=4 MaxTime=INFINITE State=UP Default=No\n",  # noqa
        f"NodeName=partitionF-partitionF-0 State=CLOUD Weight=1 Feature=cloud CPUs={g4dn_xlarge_cpus} RealMemory={g4dn_xlarge_memory * 1024} Gres=gpu:{g4dn_xlarge_gpus}(File=/dev/nvidia)\n",  # noqa
        "PartitionName=partitionF Nodes=partitionF-partitionF-0 MaxNodes=1 MaxTime=INFINITE State=UP Default=No\n",  # noqa
    ]

    with open(file_path, "r") as f:
        result = await update_slurm_config(partitions)

        copyfile_mock.assert_has_calls(
            calls=[
                mock.call(settings_mock.SLURM_CONF_PATH, f"{settings_mock.CACHE_DIR}/slurm.conf.bkp"),
                mock.call(settings_mock.SLURM_CONF_PATH, "/nfs/slurm/etc/slurm/slurm.conf"),
            ]
        )
        lines = f.readlines()
        intersection = set(lines).intersection(expected_lines)

        assert len(dummy_file) == len(lines)
        assert len(intersection) == 6

    os.remove(file_path)

    get_node_type_info_mock.assert_has_calls(
        [
            mock.call(partition["nodeType"], partition["cluster"]["creationParameters"]["region_name"])
            for partition in partitions
        ]
    )
    assert result is True


@mock.patch("vantage_agent.logicals.sync_partitions.copyfile")
@mock.patch("vantage_agent.logicals.sync_partitions.SETTINGS")
@mock.patch("vantage_agent.logicals.sync_partitions.get_node_type_info", new_callable=mock.AsyncMock)
async def test_update_slurm_config__no_diff_between_old_and_new_config(
    get_node_type_info_mock: mock.AsyncMock,
    settings_mock: mock.Mock,
    copyfile_mock: mock.Mock,
):
    """Test create a backup of slurm.conf."""
    import uuid

    file_path = f"./slurm-{uuid.uuid4()}.conf"
    settings_mock.SLURM_CONF_PATH = file_path
    settings_mock.CACHE_DIR = "./"

    t3_small_cpus = random.randint(1, 100)
    t3_small_memory = random.randint(1, 100)
    t3_xlarge_cpus = random.randint(1, 100)
    t3_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_cpus = random.randint(1, 100)
    g4dn_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_gpus = random.randint(1, 100)

    def node_info(node_type: str, region: str):
        if node_type == "t3.small":
            return {"numCpus": t3_small_cpus, "numGpus": 0, "memory": t3_small_memory}
        elif node_type == "t3.xlarge":
            return {"numCpus": t3_xlarge_cpus, "numGpus": 0, "memory": t3_xlarge_memory}
        else:
            return {"numCpus": g4dn_xlarge_cpus, "numGpus": g4dn_xlarge_gpus, "memory": g4dn_xlarge_memory}

    get_node_type_info_mock.side_effect = node_info

    with open(file_path, "w") as f:
        dummy_file = [
            "SuspendRate=100\n",
            "ResumeTimeout=600\n",
            "SuspendTime=350\n",
            "TreeWidth=60000\n",
            f"NodeName=partitionA-partitionA-[0-2] State=CLOUD Weight=1 Feature=cloud CPUs={t3_small_cpus} RealMemory={t3_small_memory * 1024}\n",  # noqa
            "PartitionName=partitionA Nodes=partitionA-partitionA-[0-2] MaxNodes=3 MaxTime=INFINITE State=UP Default=Yes\n",  # noqa
            f"NodeName=partitionC-partitionC-0 State=CLOUD Weight=1 Feature=cloud CPUs={g4dn_xlarge_cpus} RealMemory={g4dn_xlarge_memory * 1024} Gres=gpu:{g4dn_xlarge_gpus}(File=/dev/nvidia)\n",  # noqa
            "PartitionName=partitionC Nodes=partitionC-partitionC-0 MaxNodes=1 MaxTime=INFINITE State=UP Default=No\n",  # noqa
            f"NodeName=partitionB-partitionB-[0-3] State=CLOUD Weight=1 Feature=cloud CPUs={t3_xlarge_cpus} RealMemory={t3_xlarge_memory * 1024}\n",  # noqa
            "PartitionName=partitionB Nodes=partitionB-partitionB-[0-3] MaxNodes=4 MaxTime=INFINITE State=UP Default=No\n",  # noqa
        ]
        f.writelines(dummy_file)

    partitions = [
        {
            "id": 1,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": True,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
        {
            "id": 2,
            "name": "partitionB",
            "nodeType": "t3.xlarge",
            "maxNodeCount": 4,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
        {
            "id": 3,
            "name": "partitionC",
            "nodeType": "g4dn.xlarge",
            "maxNodeCount": 1,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "us-east-1"}},
        },
    ]

    expected_lines = [
        f"NodeName=partitionA-partitionA-[0-2] State=CLOUD Weight=1 Feature=cloud CPUs={t3_small_cpus} RealMemory={t3_small_memory * 1024}\n",  # noqa
        "PartitionName=partitionA Nodes=partitionA-partitionA-[0-2] MaxNodes=3 MaxTime=INFINITE State=UP Default=Yes\n",  # noqa
        f"NodeName=partitionC-partitionC-0 State=CLOUD Weight=1 Feature=cloud CPUs={g4dn_xlarge_cpus} RealMemory={g4dn_xlarge_memory * 1024} Gres=gpu:{g4dn_xlarge_gpus}(File=/dev/nvidia)\n",  # noqa
        "PartitionName=partitionC Nodes=partitionC-partitionC-0 MaxNodes=1 MaxTime=INFINITE State=UP Default=No\n",  # noqa
        f"NodeName=partitionB-partitionB-[0-3] State=CLOUD Weight=1 Feature=cloud CPUs={t3_xlarge_cpus} RealMemory={t3_xlarge_memory * 1024}\n",  # noqa
        "PartitionName=partitionB Nodes=partitionB-partitionB-[0-3] MaxNodes=4 MaxTime=INFINITE State=UP Default=No\n",  # noqa
    ]

    result = await update_slurm_config(partitions)

    # Backup file name is based on the input file path
    expected_backup_name = file_path.split("/").pop()
    copyfile_mock.assert_called_once_with(
        settings_mock.SLURM_CONF_PATH, f"{settings_mock.CACHE_DIR}/{expected_backup_name}.bkp"
    )

    with open(file_path, "r") as f:
        lines = f.readlines()
        intersection = set(lines).intersection(expected_lines)

        assert len(dummy_file) == len(lines)
        assert len(intersection) == 6

    os.remove(file_path)

    get_node_type_info_mock.assert_has_calls(
        [
            mock.call(partition["nodeType"], partition["cluster"]["creationParameters"]["region_name"])
            for partition in partitions
        ]
    )
    assert result is False


@mock.patch("vantage_agent.logicals.sync_partitions.SETTINGS")
@mock.patch("vantage_agent.logicals.sync_partitions.get_node_type_info", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.sync_partitions.create_backup")
async def test_update_partitions_config(
    create_backup_mock: mock.Mock,
    get_node_type_info_mock: mock.AsyncMock,
    settings_mock: mock.Mock,
    tmp_path: Path,
):
    """Test update of partitions.json."""
    tmp_partitions_file_path = tmp_path / "partitions.json"
    settings_mock.PARTITIONS_JSON_PATH = tmp_partitions_file_path

    tmp_gres_conf_file_path = tmp_path / "gres.conf"
    settings_mock.GRES_CONF_PATH = tmp_gres_conf_file_path

    t3_small_cpus = random.randint(1, 100)
    t3_small_memory = random.randint(1, 100)
    t3_xlarge_cpus = random.randint(1, 100)
    t3_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_cpus = random.randint(1, 100)
    g4dn_xlarge_memory = random.randint(1, 100)
    g4dn_xlarge_gpus = random.randint(1, 100)
    g3_8xlarge_cpus = random.randint(1, 100)
    g3_8xlarge_memory = random.randint(1, 100)
    g3_8xlarge_gpus = random.randint(1, 100)
    launch_template_id = str(uuid.uuid4())
    subnet_id = str(uuid.uuid4())

    def node_info(node_type: str, region: str):
        if node_type == "t3.small":
            return {"numCpus": t3_small_cpus, "numGpus": 0, "memory": t3_small_memory}
        elif node_type == "t3.xlarge":
            return {"numCpus": t3_xlarge_cpus, "numGpus": 0, "memory": t3_xlarge_memory}
        elif node_type == "g4dn.xlarge":
            return {"numCpus": g4dn_xlarge_cpus, "numGpus": g4dn_xlarge_gpus, "memory": g4dn_xlarge_memory}
        elif node_type == "g3.8xlarge":
            return {"numCpus": g3_8xlarge_cpus, "numGpus": g3_8xlarge_gpus, "memory": g3_8xlarge_memory}

    get_node_type_info_mock.side_effect = node_info

    with open(tmp_partitions_file_path, "w") as f:
        dummy_file = {
            "Partitions": [
                _build_partition_blob(
                    "compute", 10, "eu-north-1", 2, launch_template_id, subnet_id, "t3.small", is_default=True
                ),
            ]
        }
        json.dump(dummy_file, f, indent=4, ensure_ascii=False)

    with open(tmp_gres_conf_file_path, "w") as f:
        pass

    partitions = [
        {
            "id": 1,
            "name": "partitionC",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": True,
            "cluster": {"creationParameters": {"region_name": "eu-north-1"}},
        },
        {
            "id": 2,
            "name": "partitionD",
            "nodeType": "t3.xlarge",
            "maxNodeCount": 4,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "eu-north-1"}},
        },
        {
            "id": 3,
            "name": "partitionE",
            "nodeType": "g4dn.xlarge",
            "maxNodeCount": 1,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "eu-north-1"}},
        },
        {
            "id": 4,
            "name": "partitionF",
            "nodeType": "g3.8xlarge",
            "maxNodeCount": 15,
            "isDefault": False,
            "cluster": {"creationParameters": {"region_name": "eu-north-1"}},
        },
    ]

    await update_partition_config(partitions)
    get_node_type_info_mock.assert_has_calls(
        calls=[
            mock.call("t3.small", "eu-north-1"),
            mock.call("t3.xlarge", "eu-north-1"),
            mock.call("g4dn.xlarge", "eu-north-1"),
            mock.call("g3.8xlarge", "eu-north-1"),
        ]
    )
    create_backup_mock.assert_has_calls(
        [
            mock.call(tmp_partitions_file_path),
            mock.call(tmp_gres_conf_file_path),
        ]
    )

    with open(tmp_partitions_file_path, "r") as f:
        data = json.load(f)
        assert data == {
            "Partitions": [
                _build_partition_blob(
                    "partitionC",
                    3,
                    "eu-north-1",
                    t3_small_cpus,
                    launch_template_id,
                    subnet_id,
                    "t3.small",
                    is_default=True,
                ),
                _build_partition_blob(
                    "partitionD",
                    4,
                    "eu-north-1",
                    t3_xlarge_cpus,
                    launch_template_id,
                    subnet_id,
                    "t3.xlarge",
                    is_default=False,
                ),
                _build_partition_blob(
                    "partitionE",
                    1,
                    "eu-north-1",
                    g4dn_xlarge_cpus,
                    launch_template_id,
                    subnet_id,
                    "g4dn.xlarge",
                    g4dn_xlarge_gpus,
                    is_default=False,
                ),
                _build_partition_blob(
                    "partitionF",
                    15,
                    "eu-north-1",
                    g3_8xlarge_cpus,
                    launch_template_id,
                    subnet_id,
                    "g3.8xlarge",
                    g3_8xlarge_gpus,
                    is_default=False,
                ),
            ]
        }

    with open(tmp_gres_conf_file_path, "r") as f:
        lines = f.readlines()
        assert lines == [
            "NodeName=partitionE-partitionE-0 Name=gpu File=/dev/nvidia{gpu_range}\n".format(
                gpu_range=f"[0-{g4dn_xlarge_gpus - 1}]" if g4dn_xlarge_gpus > 1 else "0",
            ),
            "NodeName=partitionF-partitionF-[0-14] Name=gpu File=/dev/nvidia{gpu_range}\n".format(
                gpu_range=f"[0-{g3_8xlarge_gpus - 1}]" if g3_8xlarge_gpus > 1 else "0",
            ),
        ]


@mock.patch("vantage_agent.logicals.sync_partitions.subprocess.run")
def test_reconfigure_slurm__test_the_success_execution(subprocess_run_mock: mock.Mock):
    """Reload the slurm.conf to get the new changes in the slurm.conf."""
    reconfigure_slurm()
    subprocess_run_mock.assert_called_once_with(
        ["systemctl", "restart", "slurmctld"], check=True, capture_output=True, text=True
    )


@mock.patch("vantage_agent.logicals.sync_partitions.subprocess.run")
def test_reconfigure_slurm__test_the_filed_execution(subprocess_run_mock: mock.Mock):
    """Reload the slurm.conf to get the new changes in the slurm.conf."""
    subprocess_run_mock.side_effect = CalledProcessError(
        stderr="Dummy Error", output="Log......", returncode=1, cmd=""
    )

    try:
        reconfigure_slurm()
        assert False
    except Exception as e:
        subprocess_run_mock.assert_called_once_with(
            ["systemctl", "restart", "slurmctld"], check=True, capture_output=True, text=True
        )
        assert isinstance(e, CalledProcessError)


@pytest.mark.respx(base_url=str(backend_client.base_url))
@pytest.mark.usefixtures("mock_access_token")
async def test_get_node_type_info__test_when_it_gets_the_node_info_with_success(respx_mock: MockRouter):
    """Test get the nodeInfo based on nodeType."""
    instance_type = str(uuid.uuid4())
    region = str(uuid.uuid4())

    query = dedent(
        """
        query($filters: JSONScalar!, $first: Int, $after: Int) {
            awsNodePicker(filters: $filters, after: $after, first: $first) {
                edges {
                    node {
                        awsRegion
                        cpuName
                        cpuManufacturer
                        cpuArch
                        gpuName
                        gpuManufacturer
                        id
                        instanceType
                        memory
                        numCpus
                        numGpus
                        pricePerHour
                    }
                }
            }
        }
        """
    )

    body = {
        "query": query,
        "variables": {
            "filters": {
                "instanceType": {"eq": instance_type},
                "awsRegion": {"eq": region},
            },
            "after": 1,
            "first": 100,
        },
    }

    node_infos = [
        {
            "awsRegion": region,
            "cpuName": str(uuid.uuid4()),
            "cpuManufacturer": str(uuid.uuid4()),
            "cpuArch": str(uuid.uuid4()),
            "gpuName": str(uuid.uuid4()),
            "gpuManufacturer": str(uuid.uuid4()),
            "id": random.randint(1, 100),
            "instanceType": instance_type,
            "memory": random.randint(1, 100),
            "numCpus": random.randint(1, 100),
            "numGpus": random.randint(1, 100),
            "pricePerHour": random.random(),
        }
    ]
    response_body = {"data": {"awsNodePicker": {"edges": [{"node": node_info} for node_info in node_infos]}}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, content=json.dumps(response_body))

    response = await get_node_type_info(instance_type, region)
    assert response == node_infos[0]


@mock.patch("vantage_agent.logicals.sync_partitions.reconfigure_slurm")
@mock.patch("vantage_agent.logicals.sync_partitions.get_cluster_partitions")
@mock.patch("vantage_agent.logicals.sync_partitions.update_slurm_config")
@mock.patch("vantage_agent.logicals.sync_partitions.update_partition_config")
async def test_sync_cluster_partitions__test_when_it_syncs_with_success(
    update_partition_mock: mock.Mock,
    update_config_mock: mock.Mock,
    get_partitions_mock: mock.Mock,
    reconfigure_slurm_mock: mock.Mock,
):
    """Sync the slurm partitions with the current partitions in the API."""
    partitions = [
        {
            "id": 1,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
        {
            "id": 2,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
    ]
    get_partitions_mock.return_value = partitions

    update_config_mock.return_value = True

    await sync_cluster_partitions()

    get_partitions_mock.assert_called_once_with()
    update_config_mock.assert_called_once_with(partitions=partitions)
    update_partition_mock.assert_called_once_with(partitions=partitions)
    reconfigure_slurm_mock.assert_called_once_with()


@mock.patch("vantage_agent.logicals.sync_partitions.reconfigure_slurm")
@mock.patch("vantage_agent.logicals.sync_partitions.get_cluster_partitions")
@mock.patch("vantage_agent.logicals.sync_partitions.update_slurm_config", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.sync_partitions.update_partition_config", new_callable=mock.AsyncMock)
async def test_sync_cluster_partitions__test_when_there_is_no_diff(
    update_partition_mock: mock.AsyncMock,
    update_config_mock: mock.AsyncMock,
    get_partitions_mock: mock.AsyncMock,
    reconfigure_slurm_mock: mock.AsyncMock,
):
    """Sync the slurm partitions with the current partitions in the API."""
    partitions = [
        {
            "id": 1,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
        {
            "id": 2,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
    ]
    get_partitions_mock.return_value = partitions

    update_config_mock.return_value = False

    await sync_cluster_partitions()

    get_partitions_mock.assert_called_once_with()
    update_config_mock.assert_called_once_with(partitions=partitions)
    update_partition_mock.assert_called_once_with(partitions=partitions)
    reconfigure_slurm_mock.assert_not_called()


@mock.patch("vantage_agent.logicals.sync_partitions.reconfigure_slurm", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.sync_partitions.get_cluster_partitions", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.sync_partitions.update_slurm_config", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.sync_partitions.update_partition_config", new_callable=mock.AsyncMock)
async def test_sync_cluster_partitions__test_when_it_fails(
    update_partition_mock: mock.AsyncMock,
    update_config_mock: mock.AsyncMock,
    get_partitions_mock: mock.AsyncMock,
    reconfigure_slurm_mock: mock.AsyncMock,
):
    """Sync the slurm partitions with the current partitions in the API."""
    partitions = [
        {
            "id": 1,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
        {
            "id": 2,
            "name": "partitionA",
            "nodeType": "t3.small",
            "maxNodeCount": 3,
            "isDefault": False,
        },
    ]
    get_partitions_mock.return_value = partitions

    update_config_mock.side_effect = Exception("Dummy Error")

    await sync_cluster_partitions()

    get_partitions_mock.assert_called_once_with()
    update_config_mock.assert_called_once_with(partitions=partitions)
    update_partition_mock.assert_not_called()
    reconfigure_slurm_mock.assert_not_called()
