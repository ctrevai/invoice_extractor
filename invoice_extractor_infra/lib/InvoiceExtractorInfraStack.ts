import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as path from 'path';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';




export class InvoiceExtractorInfraStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const bucket = new s3.Bucket(this, 'InvoiceS3Bucket', {
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            encryption: s3.BucketEncryption.S3_MANAGED,
            accessControl: s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            enforceSSL: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });

        const vpc = ec2.Vpc.fromLookup(this, 'Vpc', {
            isDefault: true,
        });

        const cluster = new ecs.Cluster(this, 'InvoiceExtractorCluster', {
            vpc,
        });

        const taskDefinition = new ecs.FargateTaskDefinition(this, 'InvoiceExtractorTaskDefinition', {
            memoryLimitMiB: 2048,
            cpu: 1024,
            runtimePlatform: {
                cpuArchitecture: ecs.CpuArchitecture.ARM64,
            },
        });

        taskDefinition.addContainer('InvoiceExtractorContainer', {
            image: ecs.ContainerImage.fromAsset(path.join(__dirname, '../../frontend')),
            portMappings: [{ containerPort: 8501 }],
            environment: {
                'S3_BUCKET_NAME': bucket.bucketName,
            }
        });

        new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'InvoiceExtractorService', {
            cluster,
            taskDefinition,
            desiredCount: 1,
            assignPublicIp: true,
            publicLoadBalancer: true,
            listenerPort: 80
        });

        //Permission
        //Grant ECS read/write access to S3
        bucket.grantReadWrite(taskDefinition.taskRole);
        //Grant ECS to invoke Bedrock
        taskDefinition.addToTaskRolePolicy(new iam.PolicyStatement({
            actions: ['bedrock:*'],
            resources: ['*']
        }))

    }
}
