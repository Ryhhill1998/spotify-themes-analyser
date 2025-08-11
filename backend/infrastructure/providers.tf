terraform {
  cloud {
    organization = "ryans-personal-development"

    workspaces {
      name = "spotify-themes-analyser"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
