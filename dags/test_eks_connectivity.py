import logging

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.eks import EksHook
from airflow.utils.dates import days_ago

doc_md = """
# EKS Connectivity Test

This DAG is designed to test connectivity to an Amazon Elastic Kubernetes Service (EKS) cluster.
The DAG uses the EksHook and the aws_eks connection to describe the EKS cluster and print its config in the logs.
"""


@dag(default_args={}, schedule=None, start_date=days_ago(1), doc_md=doc_md)
def connectivity_test():
    """
    Test connectivity to EKS cluster.
    """

    @task()
    def describe_eks_cluster():
        hook = EksHook(aws_conn_id="aws_eks")
        describe = hook.describe_cluster(name="remote-kpo-demo", verbose=True)
        logging.info(describe)

    describe_eks_cluster()


connectivity_test()
