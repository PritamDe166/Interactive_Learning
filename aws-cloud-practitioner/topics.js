/* =========================================================================
   topics.js: the AWS course map, one entry per topic page (same order as
   the Notion notes). index.html draws the roadmap from it, and every topic
   page shows a "Section · topic n of m" strip with previous / next links:
       <div class="aws-trail"></div>  <script src="topics.js"></script>
   A topic is live when it has  live: true.  Old one-page-per-section files
   are listed in OLD so they can point readers to the new pages.
   ========================================================================= */
(function () {
  const S = [
    { id: 'overview', t: 'Cloud & AWS overview', tags: ['d1', 'd2'], topics: [
      { file: 'traditional-it.html', t: 'Traditional IT: how a website is served', k: 'server CPU RAM storage database network router switch DNS IP data centre', live: true },
      { file: 'what-is-cloud.html', t: 'What is cloud computing', k: 'on-demand pay as you go private public hybrid five characteristics six advantages capex opex', live: true },
      { file: 'cloud-service-models.html', t: 'IaaS, PaaS, SaaS & pricing', k: 'infrastructure platform software as a service who manages what pricing compute storage data transfer', live: true },
      { file: 'regions-azs-edge.html', t: 'Regions, AZs & edge locations', k: 'AWS global infrastructure region availability zone data centre edge location point of presence global regional services choose a region', live: true },
      { file: 'shared-responsibility.html', t: 'Shared responsibility model', k: 'security of the cloud security in the cloud customer AWS shared controls', live: true },
      { file: 'overview-review.html', t: 'Section review', k: 'exam summary quiz cheat sheet', review: true, live: true }
    ] },
    { id: 'iam', t: 'IAM', tags: ['d2'], topics: [
      { file: 'iam-users-groups.html', t: 'IAM users & groups', k: 'IAM user group root least privilege global policy', live: true },
      { file: 'iam-root-vs-user.html', t: 'Root account vs IAM user', k: 'AWS account root user MFA root-only tasks account ID', live: true },
      { file: 'iam-policies.html', t: 'IAM policies', k: 'policy JSON effect action resource principal condition explicit deny implicit deny managed inline', live: true },
      { file: 'iam-access-methods.html', t: 'Console, CLI, SDK & access keys', k: 'access key secret CLI SDK console temporary credentials aws configure', live: true },
      { file: 'iam-cloudshell.html', t: 'AWS CloudShell', k: 'cloudshell browser terminal region home storage', live: true },
      { file: 'iam-roles.html', t: 'IAM roles for services', k: 'role assume temporary credentials STS trust policy EC2 Lambda cross-account federation', live: true },
      { file: 'iam-security-tools.html', t: 'IAM security tools', k: 'credential report access advisor last accessed audit', live: true },
      { file: 'iam-best-practices.html', t: 'IAM best practices & shared responsibility', k: 'MFA password policy rotate keys secrets manager shared responsibility', live: true },
      { file: 'iam-review.html', t: 'Section review', k: 'summary exam questions quiz cheat sheet', review: true, live: true }
    ] },
    { id: 'ec2', t: 'EC2', tags: ['d3', 'd4'], topics: [
      { file: 'aws-budgets.html', t: 'AWS Budgets & billing alerts', k: 'budget alert free tier billing', live: true },
      { file: 'ec2-basics.html', t: 'EC2 basics', k: 'instance AMI EBS ENI', live: true },
      { file: 'ec2-user-data.html', t: 'Launching a web server with user data', k: 'user data bootstrap script', live: true },
      { file: 'ec2-instance-types.html', t: 'EC2 instance types', k: 'general purpose compute memory storage optimized', live: true },
      { file: 'security-groups.html', t: 'Security groups & classic ports', k: 'security group inbound outbound port 22 80 443 3389', live: true },
      { file: 'ssh.html', t: 'SSH into EC2', k: 'ssh key pair pem chmod', live: true },
      { file: 'ec2-instance-connect.html', t: 'EC2 Instance Connect', k: 'instance connect browser ssh', live: true },
      { file: 'ec2-iam-roles.html', t: 'IAM roles for EC2', k: 'instance profile role credentials', live: true },
      { file: 'purchasing-options.html', t: 'EC2 purchasing options', k: 'on-demand reserved savings plans spot dedicated', live: true },
      { file: 'ec2-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'storage', t: 'EC2 instance storage', tags: ['d3'], topics: [
      { file: 'ebs.html', t: 'EBS volumes', k: 'EBS volume AZ network drive', live: true },
      { file: 'ebs-snapshots.html', t: 'EBS snapshots', k: 'snapshot archive recycle bin', live: true },
      { file: 'ami.html', t: 'AMIs', k: 'AMI image launch', live: true },
      { file: 'ec2-image-builder.html', t: 'EC2 Image Builder', k: 'image builder pipeline', live: true },
      { file: 'instance-store.html', t: 'EC2 instance store', k: 'instance store ephemeral', live: true },
      { file: 'efs.html', t: 'EFS & EFS-IA', k: 'EFS NFS shared file system infrequent access', live: true },
      { file: 'fsx.html', t: 'Amazon FSx', k: 'FSx windows lustre', live: true },
      { file: 'ec2-storage-choices.html', t: 'Choosing EC2 storage', k: 'EBS vs EFS vs instance store', live: true },
      { file: 'storage-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'elb', t: 'ELB & Auto Scaling', old: ['elb-asg.html'], tags: ['d1', 'd3'], topics: [
      { file: 'ha-scalability.html', t: 'High availability, scalability & elasticity', k: 'vertical horizontal scale availability elasticity agility', live: true },
      { file: 'load-balancers.html', t: 'Elastic Load Balancing', k: 'ALB NLB GWLB health check', live: true },
      { file: 'auto-scaling.html', t: 'Auto Scaling groups', k: 'ASG min max desired', live: true },
      { file: 'scaling-strategies.html', t: 'Scaling strategies', k: 'target tracking step scheduled predictive', live: true },
      { file: 'elb-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 's3', t: 'Amazon S3', old: ['s3.html'], tags: ['d2', 'd3'], topics: [
      { file: 's3-basics.html', t: 'S3 buckets & objects', k: 'bucket object key', live: true },
      { file: 's3-security.html', t: 'S3 security & bucket policies', k: 'bucket policy block public access', live: true },
      { file: 's3-static-website.html', t: 'S3 static website hosting', k: 'static website endpoint 403', live: true },
      { file: 's3-versioning.html', t: 'S3 versioning', k: 'version delete marker', live: true },
      { file: 's3-replication.html', t: 'S3 replication', k: 'CRR SRR', live: true },
      { file: 's3-storage-classes.html', t: 'S3 storage classes', k: 'standard IA glacier intelligent tiering', live: true },
      { file: 's3-encryption.html', t: 'S3 encryption', k: 'SSE-S3 SSE-KMS client side', live: true },
      { file: 'iam-access-analyzer.html', t: 'IAM Access Analyzer for S3', k: 'access analyzer public', live: true },
      { file: 'storage-gateway.html', t: 'AWS Storage Gateway', k: 'hybrid storage gateway', live: true },
      { file: 's3-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'db', t: 'Databases & analytics', old: ['databases-analytics.html'], tags: ['d3'], topics: [
      { file: 'databases-intro.html', t: 'Databases on AWS', k: 'relational NoSQL managed', live: true },
      { file: 'rds-aurora.html', t: 'RDS & Aurora', k: 'RDS Aurora managed relational', live: true },
      { file: 'rds-deployments.html', t: 'Read replicas, Multi-AZ & Multi-Region', k: 'read replica multi-AZ failover', live: true },
      { file: 'elasticache.html', t: 'ElastiCache', k: 'redis memcached cache', live: true },
      { file: 'dynamodb.html', t: 'DynamoDB & DAX', k: 'dynamodb key value DAX', live: true },
      { file: 'dynamodb-global-tables.html', t: 'DynamoDB global tables', k: 'global tables active active', live: true },
      { file: 'redshift.html', t: 'Redshift', k: 'data warehouse OLAP', live: true },
      { file: 'emr.html', t: 'EMR', k: 'hadoop spark big data', live: true },
      { file: 'athena.html', t: 'Athena', k: 'serverless SQL on S3', live: true },
      { file: 'quicksight.html', t: 'QuickSight', k: 'BI dashboards', live: true },
      { file: 'documentdb.html', t: 'DocumentDB', k: 'mongodb document', live: true },
      { file: 'neptune.html', t: 'Neptune', k: 'graph database', live: true },
      { file: 'timestream.html', t: 'Timestream', k: 'time series', live: true },
      { file: 'managed-blockchain.html', t: 'Managed Blockchain', k: 'blockchain', live: true },
      { file: 'glue.html', t: 'AWS Glue', k: 'ETL data catalog', live: true },
      { file: 'dms.html', t: 'Database Migration Service', k: 'DMS migration', live: true },
      { file: 'db-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'compute', t: 'Other compute services', old: ['containers-serverless.html'], tags: ['d3', 'd4'], topics: [
      { file: 'docker.html', t: 'Docker basics', k: 'container image', live: true },
      { file: 'ecs-fargate-ecr.html', t: 'ECS, Fargate & ECR', k: 'ECS Fargate ECR', live: true },
      { file: 'eks.html', t: 'EKS', k: 'kubernetes', live: true },
      { file: 'serverless.html', t: 'What is serverless', k: 'serverless', live: true },
      { file: 'lambda.html', t: 'AWS Lambda', k: 'lambda function event', live: true },
      { file: 'api-gateway.html', t: 'API Gateway', k: 'API gateway REST', live: true },
      { file: 'aws-batch.html', t: 'AWS Batch', k: 'batch jobs', live: true },
      { file: 'lightsail.html', t: 'Lightsail', k: 'lightsail simple', live: true },
      { file: 'compute-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'deploy', t: 'Deployment & infrastructure at scale', old: ['deployment-iac.html'], tags: ['d3'], topics: [
      { file: 'cloudformation.html', t: 'CloudFormation', k: 'IaC template stack', live: true },
      { file: 'cdk.html', t: 'AWS CDK', k: 'CDK code', live: true },
      { file: 'cdk-vs-terraform.html', t: 'CDK vs Terraform', k: 'terraform IaC', live: true },
      { file: 'elastic-beanstalk.html', t: 'Elastic Beanstalk', k: 'PaaS beanstalk', live: true },
      { file: 'iac-choices.html', t: 'CloudFormation vs CDK vs Beanstalk', k: 'compare', live: true },
      { file: 'codecommit.html', t: 'CodeCommit', k: 'git repository', live: true },
      { file: 'codebuild.html', t: 'CodeBuild', k: 'build', live: true },
      { file: 'codedeploy.html', t: 'CodeDeploy', k: 'deploy', live: true },
      { file: 'codepipeline.html', t: 'CodePipeline', k: 'pipeline CI CD', live: true },
      { file: 'codeartifact.html', t: 'CodeArtifact', k: 'packages', live: true },
      { file: 'systems-manager.html', t: 'Systems Manager', k: 'SSM fleet', live: true },
      { file: 'session-manager.html', t: 'Session Manager', k: 'shell without ssh', live: true },
      { file: 'parameter-store.html', t: 'Parameter Store', k: 'config secrets', live: true },
      { file: 'deploy-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'global', t: 'Global infrastructure', old: ['global-infrastructure.html'], tags: ['d3'], topics: [
      { file: 'why-global.html', t: 'Why go global', k: 'latency disaster recovery', live: true },
      { file: 'route53.html', t: 'Route 53', k: 'DNS routing policies', live: true },
      { file: 'cloudfront.html', t: 'CloudFront', k: 'CDN cache edge', live: true },
      { file: 's3-transfer-acceleration.html', t: 'S3 Transfer Acceleration', k: 'upload edge', live: true },
      { file: 'global-accelerator.html', t: 'Global Accelerator', k: 'anycast static IP', live: true },
      { file: 'outposts.html', t: 'AWS Outposts', k: 'outposts on-premises racks hybrid', live: true },
      { file: 'wavelength.html', t: 'AWS Wavelength', k: 'wavelength 5G edge', live: true },
      { file: 'local-zones.html', t: 'AWS Local Zones', k: 'local zones metro latency', live: true },
      { file: 'global-architectures.html', t: 'Global application architectures', k: 'active-passive active-active multi-region', live: true },
      { file: 'global-review.html', t: 'Section review', review: true, live: true }
    ] },
    { id: 'integration', t: 'Cloud integrations', tags: ['d3'], topics: [
      { file: 'sync-vs-async.html', t: 'Synchronous vs asynchronous communication', k: 'decouple queue SQS SNS Kinesis', live: true }
    ] }
  ];
  const ALL = S.flatMap(s => s.topics.map(t => Object.assign({ sec: s }, t)));
  const esc = v => String(v).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function trail(el) {
    const here = location.pathname.split('/').pop() || 'index.html';
    const me = ALL.find(t => t.file === (el.dataset.file || here));
    if (!me) return;
    const list = me.sec.topics, i = list.findIndex(t => t.file === me.file);
    const live = ALL.filter(t => t.live), li = live.indexOf(me);
    const prev = live[li - 1], next = live[li + 1];
    const dots = list.map((t, j) => t.live
      ? `<a href="${t.file}" class="${j < i ? 'done' : j === i ? 'now' : ''}" title="${esc(t.t)}" aria-label="${esc(t.t)}"></a>`
      : `<span title="${esc(t.t)} (not built yet)"></span>`).join('');
    el.innerHTML = `<div class="at-top"><span class="at-sec">Section ${S.indexOf(me.sec) + 1} · ${esc(me.sec.t)}</span><span class="at-step">${me.review ? 'review' : `topic ${i + 1} of ${list.filter(t => !t.review).length}`}</span></div>
      <div class="at-dots">${dots}</div>
      <div class="at-nav">${prev ? `<a href="${prev.file}">← ${esc(prev.t)}</a>` : '<span></span>'}${next ? `<a href="${next.file}">${esc(next.t)} →</a>` : ''}</div>`;
  }
  window.AWSTopics = { SECTIONS: S, ALL, trail };
  document.querySelectorAll('.aws-trail').forEach(trail);
})();
