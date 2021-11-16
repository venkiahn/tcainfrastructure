"""
Application Stack consisting of Aurora Postgresql DB cluster and ECS cluster on Fargate
"""

from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_rds as rds,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

class AppStackProperties:

    def __init__(
            self,
            vpc: ec2.Vpc,
            load_balancer: elbv2.ApplicationLoadBalancer,
    ) -> None:

        self.vpc = vpc
        self.load_balancer = load_balancer


class AppStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str,
                 properties: AppStackProperties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = rds.ServerlessCluster(
            self, "AppServerless",
            engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "ParameterGroup",
                "default.aurora-postgresql10"
            ),
            default_database_name="app",
            vpc=properties.vpc,
            scaling=rds.ServerlessScalingOptions(
                auto_pause=core.Duration.seconds(0)
            ),
            deletion_protection=False,
            backup_retention=core.Duration.days(7),
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        repository = ecr.Repository.from_repository_name(
            self,id="ecr-repo",
            repository_name="techchallengeapp")

        cluster = ecs.Cluster(
            self, 'ComputeResourceProvider',
            vpc=properties.vpc
        )

        event_task = ecs.FargateTaskDefinition(
            self, "AppTask"
        )

        # application server

        app_container = event_task.add_container(
            "App",
            environment={
                'VTT_DBHOST': database.cluster_endpoint.hostname,
                'VTT_DBNAME': 'app',
                'VTT_LISTENHOST': 'localhost',
                'VTT_LISTENPORT': '3000'
            },
            secrets={
                'VTT_DBUSER':
                    ecs.Secret.from_secrets_manager(database.secret, field="username"),
                'VTT_DBPASSWORD':
                    ecs.Secret.from_secrets_manager(database.secret, field="password"),
                'APP_DB_NAME':
                    ecs.Secret.from_secrets_manager(database.secret, field="dbname"),
            },
            image=ecs.ContainerImage.from_registry("servian/techchallengeapp"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ECSEvents"),
            command=["CMD-SHELL", "./TechChallengeApp updatedb -s\n./TechChallengeApp serve"]
        )

        app_container.add_port_mappings(
            ecs.PortMapping(container_port=3000)
        )

        # create service

        app_service = ecs.FargateService(
            self, "InternalService",
            task_definition=event_task,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            cluster=cluster,
        )

        # scaling

        scaling = app_service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=50
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=85,
            scale_in_cooldown=core.Duration.seconds(120),
            scale_out_cooldown=core.Duration.seconds(30),
        )

        # network acl

        database.connections.allow_default_port_from(app_service, "app access to db")

        # external access

        app_service.connections.allow_from(
            other=properties.load_balancer,
            port_range=ec2.Port.tcp(80)
        )

        http_listener = properties.load_balancer.add_listener(
            "HttpListener",
            port=80,
        )

        http_listener.add_targets(
            "HttpServiceTarget",
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[app_service]
        )
