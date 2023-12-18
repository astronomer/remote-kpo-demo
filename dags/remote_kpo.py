from airflow.configuration import conf
from airflow.decorators import dag
from airflow.providers.amazon.aws.operators.eks import EksPodOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from airflow.utils.dates import days_ago

namespace = conf.get("kubernetes", "NAMESPACE")

default_args = {
    "owner": "Astronomer",
    "depends_on_past": False,
}

doc_md = """
# Remote KPO
This Airflow DAG showcases how to trigger a Kubernetes pod. We have added two tasks to trigger a pod both inside 
the default Astro Kubernetes (K8s) cluster and to a remote Amazon EKS (Elastic Kubernetes Service) cluster. 

### Let's break down the key tasks in this DAG:

The `in-cluster-kpo` task uses the KubernetesPodOperator to trigger a pod inside the Astro K8s cluster.
The namespace is set to the value of the NAMESPACE configuration variable, which is set to your deployment namespace.

The `ekspo` task uses the EksPodOperator to trigger a pod inside the remote EKS cluster.
We use the EksPodOperator instead of the standard KubernetesPodOperator because the EksPodOperator generates the 
Kubeconfig file for us automatically at run time. EksPodOperator also allows us to perform assume-role authentication 
before connecting to the remote EKS cluster. The assume-role is done by setting the extra.role_arn parameter in the aws_conn_id.

### Configuring the AWS Connection
We create an AWS connection in the Airflow UI with the following parameters:
* Conn Id: aws_eks
* Conn Type: Amazon Web Services
* Extra: {"region_name": "role_arn": "arn:aws:iam::111122223333:role/AstroRemoteKPO"}

All the other fields are left empty. The Workload Identity of your Deployment will be used to assume the role.
"""


@dag(
    dag_id="remote_kpo",
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=["KPO"],
    doc_md=doc_md,
)
def remote_kpo():
    """
    Test triggering a pod both inside the Astro K8s cluster and remote EKS cluster.
    """
    in_cluster_kpo = KubernetesPodOperator(
        task_id="in-cluster-kpo",
        namespace=namespace,
        image="debian",
        cmds=["bash", "-cx"],
        arguments=["echo", "hello world!"],
        name="hello-world",
        get_logs=True,
    )

    ekspo = EksPodOperator(
        task_id="ekspo",
        cluster_name="remote-kpo-demo",
        namespace="astro-remote-kpo",
        pod_name="hello-world",
        region="us-east-1",
        aws_conn_id="aws_eks",
        image="debian",
        cmds=["bash", "-cx"],
        arguments=["echo", "hello world!"],
        get_logs=True,
    )

    in_cluster_kpo
    ekspo
