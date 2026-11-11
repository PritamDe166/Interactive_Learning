output "website_bucket_name" {
  description = "S3 bucket that stores the static website"
  value       = aws_s3_bucket.website.bucket
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID used for cache invalidation"
  value       = aws_cloudfront_distribution.website.id
}

output "cloudfront_domain_name" {
  description = "Default CloudFront hostname"
  value       = aws_cloudfront_distribution.website.domain_name
}

output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions"
  value       = aws_iam_role.github_actions_deploy.arn
}

output "route53_name_servers" {
  description = "Enter these 4 nameservers at Hostinger for seehowitworks.dev"
  value       = aws_route53_zone.site.name_servers
}

output "site_url" {
  description = "Public address of the website"
  value       = "https://${local.domain_name}"
}
