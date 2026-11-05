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

output "cloudfront_auth_key_group_id" {
  description = "CloudFront key group for authenticated website access"
  value       = aws_cloudfront_key_group.auth.id
}

output "cloudfront_auth_public_key_id" {
  description = "CloudFront public key ID used to sign authentication cookies"
  value       = aws_cloudfront_public_key.auth.id
}

output "auth_api_url" {
  description = "HTTP API endpoint for the authentication session exchange"
  value       = aws_apigatewayv2_api.auth.api_endpoint
}
