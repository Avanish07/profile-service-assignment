1. Tool choice — why Terraform
I would choose Terraform because it is cloud-agnostic, declarative, and has a vast provider ecosystem, making it the industry standard for Infrastructure as Code. In my experience, I have used Terraform extensively to provision and manage AWS infrastructure, including networking, compute, Kubernetes (EKS), IAM, and monitoring resources. Its modular approach, state management, and strong community support make it highly scalable and maintainable for production environments.
Compared to alternatives, Pulumi offers the flexibility of using programming languages such as Python or TypeScript, but it can introduce additional complexity and require stronger software development practices. Bicep is a good option for Azure environments, but it is limited to the Azure ecosystem, whereas Terraform provides a consistent experience across multiple cloud providers and platforms.


2. Folder structure
terraform/
├── modules/namespace/    # reusable module
└── environments/
    ├── dev/
    ├── staging/
    └── prod/

Modules hold reusable logic, environments call them with different inputs. Each env is isolated.


3. Remote state strategy (explain, since you're using local now)
For this assignment, I am using a local Terraform state file (terraform.tfstate) stored on disk. In a team or production environment, I would use a remote backend such as AWS S3 to store the state centrally. This ensures that all team members work with the same source of truth and prevents state files from being lost or duplicated. To avoid concurrent modifications, I would enable state locking using DynamoDB (or S3 native locking where applicable), ensuring that only one Terraform operation can run against a state file at a time. Additionally, I would maintain separate state files for different environments (e.g., development, staging, and production) to provide proper isolation and reduce the risk of unintended changes across environments.


4. Placeholder cloud resources
Since the assignment cannot rely on paid cloud services, I implemented a real Kubernetes namespace module that can be deployed and tested locally using Minikube. This demonstrates the Terraform workflow, module structure, and Infrastructure as Code practices without requiring access to a cloud account.

In a production environment, I would extend the solution by adding modules for cloud resources such as an Amazon ECR repository for container images, IAM roles and IRSA (IAM Roles for Service Accounts) for secure workload authentication, and AWS Secrets Manager integration for managing application secrets. These components are documented as placeholders rather than fully implemented because they require valid AWS credentials and cloud resources that reviewers may not have access to. This approach keeps the assignment reproducible while clearly showing how the infrastructure would be expanded for a real-world deployment.


5. How to run it
cd environments/dev
terraform init
terraform validate
terraform plan
terraform apply      # would create the namespace on the current kube-context