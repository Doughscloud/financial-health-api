variable "region" {
  description = "The AWS region to deploy the infrastructure"
  default     = "us-east-1"  # You can override this by passing a different region
}

variable "instance_type" {
  description = "Type of instance"
  default     = "t2.micro"  # Default is small instance size for testing
}

variable "ami" {
  description = "AMI ID for the instance"
  default     = "ami-0c55b159cbfafe1f0"  # Update with correct AMI
}
